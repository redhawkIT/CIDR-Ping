#!/usr/bin/env python

'''
CIDR Ping - an alternative to bping / fping
    by Ryan Keller, UW-IT NIM
---

##### Requires:
 - Python 2.X
 - Netaddr (any version)

This project was designed to serve as a method of scanning and reporting information on a subnet - it provides information about a subnet, it's available information e.g. the Mask, Broadcast, and range of available IP's, and most importantly - it can ping every single address (up to 255!) in less than a second.

    ========================================
    CIDR:   172.31.219.80/28        Range: 80-95
    ----------------------------------------
    Mask:   255.255.255.240
    Gate:   172.31.219.81
    Broad:  172.31.219.95
    ========================================
    ONLINE:
    81     |84     |91     |93-94  |
    ----------------------------------------
    OFFLINE:
    80     |82-83  |85-90  |92     |95     |
    ========================================
'''

################################################################################
#                                      Import Segment
################################################################################

import sys, platform
import threading
import subprocess
'''
Subprocess is used because it is compatible with multithreading.
It is *possible* to utilize os.system, but it will spam your terminal
and piping stout/err to dev/null can cause errors. SP remains as the most
effective way to do this, and PIP documentation reflects this as an intended
use case as well.
'''

import netaddr as net
'''
Used to calculate IP's in a CIDR. Keep in mind that an IP address
is treated as an object, that's why I cast them as strings so much.
'''



################################################################################
#                                      Operation Settings
################################################################################

### Ping Configuration
TIMEOUT = '500'     #Miliseconds
    #I find 500, or half a second, to be the best
UNIX_TIMEOUT = '1'
    #Some UNIX systems appear to throw exceptions upon receiving floats
    
PACKET_NUMBER = '2' #Attempts to reach a device
PACKET_SIZE = '2'   #Size of packets, Windows default is 32



################################################################################
#                                      Main Function
################################################################################

def main():

    try:
        #Gather the CIDR or IP. A good CIDR to test is 172.31.219.94/24
        if len(sys.argv) > 1:
            CIDR = sys.argv[1]
        else:
            CIDR = raw_input('CIDR Net:\t').rstrip('\r\n')
        network = net.IPNetwork(CIDR)
        print('='*40)
        
        #Print essential/useful data
        print('CIDR:\t' + str(network.cidr) + '\t' + \
        'Range: ' + str(network[0]).split('.')[3] + \
        '-' + str(network[-1]).split('.')[3])
        print('-'*40)
        try:
            print('Mask:\t' + str(network.netmask))
            print('Gate:\t' + str(network[1]))
            print('Broad:\t' + str(network.broadcast))
        except:
            pass
        print('='*40)
        
        
        try:
            online = []
            offline = []
            
            #Create an array of threads for ping processes, start them
            ipCheckList = []
            for ip in network:
                ping = Pinger(str(ip))
                ipCheckList.append(ping)
                ping.start()
            
            #Merge all of the pings, check and record results
            for ping in ipCheckList:
                ping.join()
                if ping.status == True:
                    online.append(ping.lastOctet)
                else:
                    offline.append(ping.lastOctet)
            
            #Print formatted tables for online/offline status
            print('Online:')
            if (len(online) > 0):
                print(createTable(sortFeedback(online)))
            else:
                print('(none)')
            print('-'*40)
            
            print('Offline:')
            if (len(offline) > 0):
                print(createTable(sortFeedback(offline)))
            else:
                print('(none)')
        
        except:
            pass
        print('='*40)
        print('Utility developed by Ryan Keller (RcKeller.Github.IO)')

        
    except Exception as reason:
        print('='*40)
        print('An error occured, the network may have been invalid:')
        print(reason)
        print('='*40)
    
    return

    
    
################################################################################
#                                      Sortation Functions
################################################################################
    
def sortFeedback(ipList):
    '''
    This creates an array that contains formatted string for ranges of final IP octets.
    E.g. if .10, .11 and .12 are online, it is recorded in an array as '10-12'
    '''
    def sortedIPList(ipList):
        first = last = ipList[0]
        grouping = [str(first), str(last)]
        for n in ipList[1:]:
            if n - 1 == last: # Part of the group, bump the end
                last = n
            else: # Not part of the group, yield current group and start a new
                yield first, last
                first = last = n
        yield first, last # Yield the last group

    #Create an array with these formatted strings
    feedback = []
    for pair in sortedIPList(ipList):
        pair = list(pair)   #Function yields tuples, must cast
        if (pair[0] != pair[1]):
            feedback.append(str(pair[0]) + '-' + str(pair[1]))
        else:
            feedback.append(str(pair[0]))            
    return feedback
    
    
def createTable(data):
    '''
    Takes an array and creates a primitive table out of it,
    useful for consolidating data & avoiding terminal spam.
    '''
    table = ''
    fieldsInLine = 0
    for field in data:
        fieldsInLine += 1
        if (fieldsInLine == 6):
            table += ('\n')
            fieldsInLine = 1
        table += ('{0: <7}|').format(field)
    return table



################################################################################
#                                      Networking Functions
################################################################################

class Pinger(threading.Thread):
    '''
    Pinger is a class designed to use subprocesses to rapidly ping networks for reachability.
    self.status is false by default, and if a ping is successful, that changes.
    Notice that a class paramater is actually a thread. These Pingers can be initialized
    by .start() and merged with .join(). Each ping command has their own way of terminating
    and returning the flow of control at the end of the thread.
    '''
    def __init__ (self, address):
        threading.Thread.__init__(self)
        self.ip = str(address)
        self.lastOctet = int(self.ip.split('.')[3])
        self.system = platform.system().lower()
        self.status = False
        
        if self.system == 'windows':
            self.command =  ['ping', self.ip,
                            '-n', PACKET_NUMBER,
                            '-w', TIMEOUT,
                            '-l', PACKET_SIZE]
            #Windows prefers a string instead of list, unlike unix.
            self.command = ' '.join(map(str, self.command))
        else:
            '''
            UNIX based systems will require a timeout, failed pings will perpetuate
            otherwise, requiring us to prefix the command with a timout that is SEPARATE
            from the actual ping command.
            '''
            self.command =  ['timeout', UNIX_TIMEOUT,
                            'ping', '-b',
                            self.ip,
                            '-c', PACKET_NUMBER,
                            '-l', PACKET_SIZE]
                            
    def run(self):
        try:
            self.response = subprocess.check_call(self.command, stdout=subprocess.PIPE)
            if self.response == 0:
                self.status = True
        except Exception:
            self.status = False #Redundant but in case this is expanded later


            
################################################################################
#                                      Function Calls
################################################################################

if __name__ == '__main__':
    main()
