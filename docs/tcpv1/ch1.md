### **Chapter 1. Introduction**

Some terms [p1]:

* [Gateways](http://en.wikipedia.org/wiki/Gateway_(telecommunications)): later called routers
* [Catenet](http://en.wikipedia.org/wiki/Catenet) ("concatenated" network): obsolete term, later called internetwork

This chapter provides an overview of the Internet architecture and TCP/IP protocol suite.

### Architectural Principles

The TCP/IP protocol suite is an open system which forms the basis for the Internet. We refer to World Wide Web (WWW) as an application that uses the Internet for communication (which is perhaps the most important Internet application) [p2-3]

#### Packets, Connections, and Datagrams



### Design and Implementation

### The Architecture and Protocols of the TCP/IP Suite

#### The ARPANET Reference Model
#### Multiplexing, Demultiplexing, and Encapsulation in TCP/IP
#### Port Numbers

Port numbers are 16-bit nonnegative integers (0–65535).


#### Names, Addresses, and the DNS

### Internets, Intranets, and Extranets

### Designing Applications

#### Client/Server
#### Peer-to-Peer
#### Application Programming Interfaces (APIs)

### Standardization Process

The group with which we will most often be concerned is the [Internet Engineering Task Force](https://en.wikipedia.org/wiki/Internet_Engineering_Task_Force) (IETF). [p22]

#### Request for Comments (RFC)

Every official standard in the Internet community is published as a [Request for Comments](https://en.wikipedia.org/wiki/Request_for_Comments) (RFC).

### Implementations and Software Distributions

The historical de facto standard TCP/IP implementations were from the Computer Systems Research Group (CSRG) at the University of California, Berkeley. They were distributed with the 4.x BSD (Berkeley Software Distribution) system and with the BSD Networking Releases until the mid-1990s. This source code has been the starting point for many other implementations. [p24]

In this text, we tend to draw examples from the TCP/IP implementations in Linux, Windows, and sometimes FreeBSD and Mac OS (both of which are derived from historical BSD releases).

[![Figure 1-7 The history of software releases supporting TCP/IP up to 1995. The various BSD releases pioneered the availability of TCP/IP. In part because of legal uncertainties regarding the BSD releases in the early 1990s, Linux was developed as an alternative that was initially tailored for PC users. Microsoft began supporting TCP/IP in Windows a couple of years later.](figure_1-7_600.png)](figure_1-7.png "Figure 1-7 The history of software releases supporting TCP/IP up to 1995. The various BSD releases pioneered the availability of TCP/IP. In part because of legal uncertainties regarding the BSD releases in the early 1990s, Linux was developed as an alternative that was initially tailored for PC users. Microsoft began supporting TCP/IP in Windows a couple of years later.")

### Attacks Involving the Internet Architecture

#### Spoofing *

The Internet architecture delivers IP datagrams based on destination IP addresses. As a result, malicious users are able to insert whatever IP address they choose into the source IP address field of each IP datagram they send, an activity called [**spoofing**](https://en.wikipedia.org/wiki/IP_address_spoofing). The resulting datagrams are delivered to their destinations, but it is difficult to perform **attribution**. That is, it may be difficult or impossible to determine the origin of a datagram received from the Internet. [p25-26]

#### Denial-of-service (DoS) *

* Denial-of-service (DoS)
* Distributed DoS (DDS)

#### Unauthorized access

* **Black hats** are programmers who intentionally develop malware and exploit systems for (illegal) profit or other malicious purposes are generally called .
* **White Hats** do the same sorts of technical things but notify vulnerable parties instead of exploit them.

#### Encryption concerns
