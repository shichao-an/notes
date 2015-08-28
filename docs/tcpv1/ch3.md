### **Chapter 3. Link Layer**

### Introduction

This chapter discusses the details involved in using the Ethernet and Wi-Fi link layers, how the Point-to-Point Protocol (PPP) is used, and how link-layer protocols can be carried inside other (link- or higher-layer) protocols, a technique known as tunneling.

When referring to link-layer protocol data units (PDUs), we usually use the term **frame**, so as to distinguish the PDU format from those at higher layers such as packets or segments, terms used to describe network- and transport-layer PDUs, respectively.

Frame formats usually support a variable-length frame size, the upper bound of which is called the [**maximum transmission unit**](https://en.wikipedia.org/wiki/Maximum_transmission_unit) (MTU). Some network technologies, such as modems and serial lines, do not impose their own maximum frame size, so they can be configured by the user.


### Ethernet and the IEEE 802 LAN/MAN Standards

[p80]

#### The IEEE 802 LAN/MAN Standards

[p82]

#### The Ethernet Frame Format

The figure below shows the current layout of an Ethernet frame and how it relates to a relatively new term introduced by IEEE, the **IEEE packet**.

[![The Ethernet (IEEE 802.3) frame format contains source and destination addresses, an overloaded Length/Type field, a field for data, and a frame check sequence (a CRC32). Additions to the basic frame format provide for a tag containing a VLAN ID and priority information (802.1p/q) and more recently for an extensible number of tags. The preamble and SFD are used for synchronizing receivers. When half-duplex operation is used with Ethernet running at 100Mb/s or more, additional bits may be appended to short frames as a carrier extension to ensure that the collision detection circuitry operates properly. ](figure_3-3_600.png)](figure_3-3.png "The Ethernet (IEEE 802.3) frame format contains source and destination addresses, an overloaded Length/Type field, a field for data, and a frame check sequence (a CRC32). Additions to the basic frame format provide for a tag containing a VLAN ID and priority information (802.1p/q) and more recently for an extensible number of tags. The preamble and SFD are used for synchronizing receivers. When half-duplex operation is used with Ethernet running at 100Mb/s or more, additional bits may be appended to short frames as a carrier extension to ensure that the collision detection circuitry operates properly. ")

* The Ethernet frame begins with a **Preamble** area used by the receiving interface’s circuitry to determine when a frame is arriving and to determine the amount of time between encoded bits (called **clock recovery**). Because Ethernet is an asynchronous LAN, the space between encoded bits may differ from one interface card from another.
* This basic frame format includes 48-bit (6-byte) **Destination** (DST) and **Source** (SRC) Address fields. These addresses are sometimes known by other names such as:
    * MAC address
    * Link-layer address
    * 802 address
    * Hardware address
    * Physical address

    The destination address in an Ethernet frame is also allowed to address more than one station ("broadcast" or "multicast"; see [Chapter 9](ch9.md)). The broadcast capability is used by the ARP protocol ([Chapter 4](ch4.md)) and multicast capability is used by the ICMPv6 protocol ([Chapter 8](ch8.md)) to convert between network-layer and link-layer addresses.

* **Type** field that doubles as a **Length** field. It identifies the type of data that follows the header. Popular values used with TCP/IP networks include:
    * IPv4 (0x0800)
    * IPv6 (0x86DD)
    * ARP (0x0806).

    The value 0x8100 indicates a Q-tagged frame (i.e., one that can carry a "virtual LAN" or VLAN ID according to the 802.1q standard).

    <u>The size of a basic Ethernet frame is 1518 bytes</u>, but the more recent standard extended this size to 2000 bytes.


### Full Duplex, Power Save, Autonegotiation, and 802.1X Flow Control

### Bridges and Switches

### Wireless LANs—IEEE 802.11(Wi-Fi)

### Point-to-Point Protocol (PPP)

### Loopback

In many cases clients want to communicate with servers on the same computer using Internet protocols such as TCP/IP. To enable this, most implementations support a network-layer [**loopback**](https://en.wikipedia.org/wiki/Loopback) capability that typically takes the form of a [virtual loopback network interface](https://en.wikipedia.org/wiki/Localhost). <u>It acts like a real network interface but is really a special piece of software provided by the operating system to enable TCP/IP and other communications on the same host computer.</u>

IPv4 addresses starting with 127 are reserved for this, as is the IPv6 address ::1 ([Chapter 2](ch2.md)). Traditionally, UNIX-like systems including Linux assign the IPv4 address of 127.0.0.1 (::1 for IPv6) to the loopback interface and assign it the name localhost.

<u>An IP datagram sent to the loopback interface must not appear on any network.</u> Although we could imagine the transport layer detecting that the other end is a loopback address and shortcircuiting some of the transport-layer logic and all of the network-layer logic, most implementations perform complete processing of the data in the transport layer and network layer and loop the IP datagram back up in the network stack only when the datagram leaves the bottom of the network layer. This can be useful for performance measurement, for example, because the amount of time required to execute the stack software can be measured without any hardware overheads. In Linux, the loopback interface is called `lo`.

```text
Linux% ifconfig lo
lo Link encap:Local Loopback
 inet addr:127.0.0.1 Mask:255.0.0.0
 inet6 addr: ::1/128 Scope:Host
 UP LOOPBACK RUNNING MTU:16436 Metric:1
 RX packets:458511 errors:0 dropped:0 overruns:0 frame:0
 TX packets:458511 errors:0 dropped:0 overruns:0 carrier:0
 collisions:0 txqueuelen:0
 RX bytes:266049199 (253.7 MiB)
 TX bytes:266049199 (253.7 MiB)
```

This local loopback interface:

* The IPv4 address is 127.0.0.1 and has a subnet mask of 255.0.0.0 (corresponding to class A network number 127 in classful addressing).
* The IPv6 address ::1 has a 128-bit-long prefix, so it represents only a single address. The interface has an MTU of 16KB (this can be configured to a much larger size, up to 2GB).

We would not expect to see errors on the local loopback device, given that it never really sends packets on any network

### MTU and Path MTU

From [Figure 3-3](figure_3-3.png), there is a limit on the frame's size available for carrying the PDUs of higher-layer protocols in link-layer networks. This usually limits the number of payload bytes to about 1500 for Ethernet and often the same amount for PPP in order to maintain compatibility with Ethernet.

This characteristic (the limit of frame's size to carry higher-layer PDUs) of the link layer is called the **maximum transmission unit** (MTU). Most packet networks (like Ethernet) have a fixed upper limit:

* Most stream-type networks (serial links) have a configurable limit that is then used by framing protocols such as PPP.
* If IP has a datagram to send, and the datagram is larger than the link layer’s MTU, IP performs *fragmentation*, breaking the datagram up into smaller pieces (fragments), so that each fragment is smaller than the MTU.

MTU on networks:

* When two hosts on the same network are communicating with each other, it is the MTU of the local link interconnecting them that has a direct effect on the size of datagrams.
* When two hosts communicate across multiple networks, each link can have a different MTU. The minimum MTU across the network path comprising all of the links is called the **path MTU**.

The path MTU between any two hosts need not be constant over time:

* It depends on the path being used at any time, which can change if the routers or links in the network fail;
* Paths are often not *symmetric* (the path from host A to B may not be the reverse of the path from B to A); hence the path MTU need not be the same in the two directions.

[**Path MTU discovery**](https://en.wikipedia.org/wiki/Path_MTU_Discovery) (PMTUD) is used to determine the path MTU at a point in time (and is required of IPv6 implementations).

### Doubts and Solutions

#### Verbatim

p146 on loopback

> An IP datagram sent to the loopback interface must not appear on any network. Although we could imagine the transport layer detecting that the other end is a loopback address and shortcircuiting some of the transport-layer logic and all of the network-layer logic, most implementations perform complete processing of the data in the transport layer and network layer and loop the IP datagram back up in the network stack only when the datagram leaves the bottom of the network layer.
