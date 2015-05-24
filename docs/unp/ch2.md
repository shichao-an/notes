## Chapter 2. The Transport Layer: TCP, UDP, and SCTP

### Introduction

This chapter focuses on the transport layer: TCP, UDP, and Stream Control Transmission Protocol (SCTP). UDP is a simple, unreliable datagram protocol, while TCP is a sophisticated, reliable byte-stream protocol. SCTP is similar to TCP as a reliable transport protocol, but it also provides message boundaries, transport-level support for multihoming, and a way to minimize head-of-line blocking.


### The Big Picture 

Overview of TCP/IP protocols:

Protocol | Description
-------- | -----------
IPv4 | Internet Protocol version 4. IPv4 uses 32-bit addresses and provides packet delivery service for TCP, UDP, SCTP, ICMP, and IGMP.
IPv6 | Internet Protocol version 6. IPv6 uses 128-bit addresses.
TCP | Transmission Control Protocol. TCP is a connection-oriented protocol that provides a reliable, full-duplex byte stream to its users
UDP | User Datagram Protocol. UDP is a connectionless protocol, and UDP sockets are an example of datagram sockets.
SCTP | Stream Control Transmission Protocol. SCTP is a connection-oriented protocol that provides a reliable full-duplex association
ICMP | Internet Control Message Protocol. ICMP handles error and control information between routers and hosts.
IGMP | Internet Group Management Protocol. IGMP is used with multicasting.
ARP | Address Resolution Protocol. ARP maps an IPv4 address into a hardware address (such as an Ethernet address). ARP is normally used on broadcast networks such as Ethernet, [token ring](http://en.wikipedia.org/wiki/Token_ring), and [FDDI](http://en.wikipedia.org/wiki/Fiber_Distributed_Data_Interface), and is not needed on point-to-point networks.
RARP | Reverse Address Resolution Protocol. RARP maps a hardware address into an IPv4 address. It is sometimes used when a diskless node is booting.
ICMPv6 | Internet Control Message Protocol version 6. ICMPv6 combines the functionality of ICMPv4, IGMP, and ARP.
BPF | [BSD packet filter](http://en.wikipedia.org/wiki/PF_(firewall)). This interface provides access to the datalink layer. It is normally found on Berkeley-derived kernels.
DLPI | [Datalink provider interface](http://en.wikipedia.org/wiki/Data_Link_Provider_Interface). 

### User Datagram Protocol (UDP)

* Lack of reliability
* Each UDP datagram has a length
* **Connectionless** service

### Transmission Control Protocol (TCP)

* **Connection**: TCP provides connections between clients and servers. A TCP client establishes a connection with a server, exchanges data across the connection, and then terminates the connection.
* **Reliability**: TCP requires acknowledgment when sending data. If an acknowledgment is not received, TCP automatically retransmits the data and waits a longer amount of time.
* **Round-trip time** (RTT): TCP estimates RTT between a client and server dynamically so that it knows how long to wait for an acknowledgment.
* **Sequencing**: TCP associates a sequence number with every byte (**segment**, unit of data that TCP passes to IP.) it sends. TCP reorders out-of-order segments and discards duplicate segments.
* **Flow control**
* **Full-duplex**: an application can send and receive data in both directions on a given connection at any time.

### Stream Control Transmission Protocol (SCTP)

Like TCP, SCTP provides reliability, sequencing, flow control, and full-duplex data transfer.

Unlike TCP, SCTP provides:

* **Association** instead of "connection": An association refers to a communication between two systems, which may involve more than two addresses due to multihoming.
* **Message-oriented**: provides sequenced delivery of individual records. Like UDP, the length of a record written by the sender is passed to the receiving application.
* **Multihoming**: allows a single SCTP endpoint to support multiple IP addresses. This feature can provide increased robustness against network failure.
