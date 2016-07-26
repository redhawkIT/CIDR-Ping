# CIDR Ping - an alternative to bping / fping
---

##### Requires:
 - Python 2.7
 - Netaddr (pip install netaddr)

This project was designed to serve as a method of scanning and reporting information on a subnet - it provides information about a subnet, it's available information e.g. the Mask, Broadcast, and range of available IP's, and most importantly - it can ping every single address (up to 255!) in less than a second.

I do not have access to the source file of bping, but I was informed that it works off of PUMA data, which explains why I've seen unreported devices in a bping query. This makes sense to some extent - we don't want to flood the screen with the results of 255 pings. Instead, what I did in this program, is I added a function that groups together pings by "online" and "offline", and then groups ranges of IP's together, followed by creating a table, minimizing screen flood. Example output:

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

##### Technical notes:
 - This is not meant to replace bping/fping. In fact, we should keep the two so we can cross-reference queries and then discover potential PUMA record conflicts.
 - This was not developed by the tools group, but I am working on refactoring the code so that this could potentially be run on port.washington.edu
 - The pinger class needs to be refactored for better encapsulation, but time has imposed a restraint on that for now.