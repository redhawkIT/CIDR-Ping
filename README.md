# CIDR Ping - an alternative to bping / fping
---

##### Requires:
 - Python 2.7
 - Netaddr (any version)

This project was designed to serve as a method of scanning and reporting information on a subnet - it provides information about a subnet, it's available information e.g. the Mask, Broadcast, and range of available IP's, and most importantly - it can ping every single address (up to 255!) in less than a second.
This was created due to the poor data formatting and speed of nMap and fping - they do the same logical work, but a /24 network can easily flood your screen several times over.

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