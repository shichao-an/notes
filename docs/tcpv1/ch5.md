### **Chapter 5. The Internet Protocol (IP)**

> IP is the workhorse protocol of the TCP/IP protocol suite.
> <small>*TCPv1*</small>

### Introduction

IP provides a best-effort, connectionless datagram delivery service. When something goes wrong, such as a router temporarily running out of buffers, IP simly throws away some data. Any required reliability must be provided by the upper layers (e.g. TCP). IPv4 and IPv6 both use this basic best-effort delivery model.

The term *connectionless* means that IP does not maintain any connection state information about related datagrams within the network elements (within the routers):

* Each IP datagram is handled independently from all other others.
* Datagrams can be delivered out of order.

This chapter is on IPv4 and IPv6 header fields, and describes how IP forwarding works.

### IPv4 and IPv6 Headers

##### **IPv4 Header** *

[![The IPv4 datagram. The header is of variable size, limited to fifteen 32-bit words (60 bytes) by the 4-bit IHL field. A typical IPv4 header contains 20 bytes (no options). The source and destination addresses are 32 bits long. Most of the second 32-bit word is used for the IPv4 fragmentation function. A header checksum helps ensure that the fields in the header are delivered correctly to the proper destination but does not protect the data.](figure_5-1_600.png)](figure_5-1.png "The IPv4 datagram. The header is of variable size, limited to fifteen 32-bit words (60 bytes) by the 4-bit IHL field. A typical IPv4 header contains 20 bytes (no options). The source and destination addresses are 32 bits long. Most of the second 32-bit word is used for the IPv4 fragmentation function. A header checksum helps ensure that the fields in the header are delivered correctly to the proper destination but does not protect the data.")

##### **IPv6 Header** *

[![The IPv6 header is of fixed size (40 bytes) and contains 128-bit source and destination addresses. The Next Header field is used to indicate the presence and types of additional extension headers that follow the IPv6 header, forming a daisy chain of headers that may include special extensions or processing directives. Application data follows the header chain, usually immediately following a transport-layer header.](figure_5-1_600.png)](figure_5-1.png "The IPv6 header is of fixed size (40 bytes) and contains 128-bit source and destination addresses. The Next Header field is used to indicate the presence and types of additional extension headers that follow the IPv6 header, forming a daisy chain of headers that may include special extensions or processing directives. Application data follows the header chain, usually immediately following a transport-layer header.")

##### **Size and network byte order** *

* The normal size of the IPv4 header is 20 bytes, unless options are present (which is rare).
* <u>The IPv6 header is twice as large as the IPv4 Header but never has any options.</u> It may have *extension headers*.

In our pictures of headers and datagrams, for a 32-bit value, <u>the most significant bit is numbered 0 at the left, and the least significant bit of a 32-bit value is numbered 31 on the right.</u> The 4 bytes in a 32-bit value are transmitted in the following order: bits 0–7 first, then bits 8–15, then 16–23, and bits 24–31 last. This is called **big endian** byte ordering, which is the byte ordering required for all binary integers in the TCP/IP headers as they traverse a network. It is also called **network byte order**. Computer CPUs that store binary integers in little endian format must convert the header values into network byte order for transmission and back again for reception.
