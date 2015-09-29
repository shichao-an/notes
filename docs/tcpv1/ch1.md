### **Chapter 1. Introduction**

Some terms [p1]:

* [Gateways](http://en.wikipedia.org/wiki/Gateway_(telecommunications)): later called routers
* [Catenet](http://en.wikipedia.org/wiki/Catenet) ("concatenated" network): obsolete term, later called internetwork

This chapter provides an overview of the Internet architecture and TCP/IP protocol suite.

### Architectural Principles

The TCP/IP protocol suite is an open system which forms the basis for the Internet. We refer to World Wide Web (WWW) as an application that uses the Internet for communication (which is perhaps the most important Internet application) [p2-3]

#### Packets, Connections, and Datagrams

In 1960s one of the most important concepts was **packet switching**, where "chunks" (packets) of digital information comprising some number of bytes are carried through the network somewhat independently. Chunks coming from different sources or senders can be mixed together and pulled apart later, which is called **multiplexing**. The chunks can be moved around from one switch to another on their way to a destination, and the path might be subject to change. This has two potential advantages:

* The network can be more resilient (against being physically attacked).
* There can be better utilization of the network links and switches because of statistical multiplexing.

[p4]

##### **Connection-oriented networks**

**Virtual circuits** (VCs) that behave like circuits but do not depend on physical circuit switches can be implemented atop connection-oriented packets. This is the basis for a protocol known as [X.25](https://en.wikipedia.org/wiki/X.25) that was popular until about the early 1990s when it was largely replaced with [Frame Relay](https://en.wikipedia.org/wiki/Frame_Relay) and ultimately [digital subscriber line](https://en.wikipedia.org/wiki/Digital_subscriber_line) (DSL) technology.

The VC abstraction and connection-oriented packet networks such as X.25 required *state* to be stored in each switch for each connection. The reason is that each packet carries only a small bit of overhead information that provides an index into a state table. [p5] Such networks are consequently called **connection-oriented**.

##### **Connectionless networks**

In the late 1960s, another option was developed known as the datagram. A datagram is a special type of packet in which all the identifying information of the source and final destination resides inside the packet itself. Thus, a **connectionless network** could be built.

##### **Message boundaries**

**Message boundaries** (or **record markers**) are related concepts. As shown in the figure below, when an application sends more than one chunk into the network, the fact that more than one chunk was written may or may not be preserved by the communication protocol. Most datagram protocols preserve message boundaries. This is natural because the datagram itself has a beginning and an end.  However, in a circuit or VC network, it is possible that an application may write several chunks of data, all of which are read together as one or more different-size chunks by a receiving application. These types of protocols do not preserve message boundaries. In cases where an underlying protocol fails to preserve message boundaries but they are needed by an application, the application must provide its own.

[![Applications write messages that are carried in protocols. A message boundary is the position or byte offset between one write and another. Protocols that preserve message boundaries indicate the position of the sender’s message boundaries at the receiver. Protocols that do not preserve message boundaries (e.g., streaming protocols like TCP) ignore this information and do not make it available to a receiver. As a result, applications may need to implement their own methods to indicate a sender’s message boundaries if this capability is required.](figure_1-1_600.png)](figure_1-1.png "Applications write messages that are carried in protocols. A message boundary is the position or byte offset between one write and another. Protocols that preserve message boundaries indicate the position of the sender’s message boundaries at the receiver. Protocols that do not preserve message boundaries (e.g., streaming protocols like TCP) ignore this information and do not make it available to a receiver. As a result, applications may need to implement their own methods to indicate a sender’s message boundaries if this capability is required.")

In this figure, applications write messages that are carried in protocols. A message boundary is the position or byte offset between one write and another.

* **Protocols that preserve message boundaries** (e.g., UDP) indicate the position of the sender’s message boundaries at the receiver.
* **Protocols that do not preserve message boundaries** (e.g., streaming protocols like TCP) ignore this information and do not make it available to a receiver. As a result, applications may need to implement their own methods to indicate a sender’s message boundaries if this capability is required.

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

### Doubts and Solutions

#### Verbatim

p5-6 on message boundaries:

> Protocols that preserve message boundaries (e.g., UDP) indicate the position of the sender’s message boundaries at the receiver. Protocols that do not preserve message boundaries (e.g., streaming protocols like TCP) ignore this information and do not make it available to a receiver.

Some explanations:

* [The TCP Service Model](ch12.md#the-tcp-service-model) in Chapter 12.
* [TCP stream vs UDP message](http://stackoverflow.com/questions/17446491/tcp-stream-vs-udp-message)
* [What is a message boundary?](http://stackoverflow.com/questions/9563563/what-is-a-message-boundary)
