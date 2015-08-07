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

[![The IPv6 header is of fixed size (40 bytes) and contains 128-bit source and destination addresses. The Next Header field is used to indicate the presence and types of additional extension headers that follow the IPv6 header, forming a daisy chain of headers that may include special extensions or processing directives. Application data follows the header chain, usually immediately following a transport-layer header.](figure_5-2_600.png)](figure_5-2.png "The IPv6 header is of fixed size (40 bytes) and contains 128-bit source and destination addresses. The Next Header field is used to indicate the presence and types of additional extension headers that follow the IPv6 header, forming a daisy chain of headers that may include special extensions or processing directives. Application data follows the header chain, usually immediately following a transport-layer header.")

##### **Size and network byte order** *

* The normal size of the IPv4 header is 20 bytes, unless options are present (which is rare).
* <u>The IPv6 header is twice as large as the IPv4 Header but never has any options.</u> It may have *extension headers*.

In our pictures of headers and datagrams, for a 32-bit value, <u>the most significant bit is numbered 0 at the left, and the least significant bit of a 32-bit value is numbered 31 on the right.</u> The 4 bytes in a 32-bit value are transmitted in the following order: bits 0–7 first, then bits 8–15, then 16–23, and bits 24–31 last. This is called **big endian** byte ordering, which is the byte ordering required for all binary integers in the TCP/IP headers as they traverse a network. It is also called **network byte order**. Computer CPUs that store binary integers in little endian format must convert the header values into network byte order for transmission and back again for reception.

#### IP Header Fields

* The **Version** field is the first field (only 4 bits or one nibble wide). It contains the version number of the IP datagram: 4 for IPv4 and 6 for IPv6.
    * This is the only field that IPv4 and IPv6 of which share the location. The two protocols are not directly interoperable, which means a host or router must handle either IPv4 or IPv6 (or both, called **dual stack**) separately.
* The **Internet Header Length (IHL)** field is the number of 32-bit words in the IPv4 header, including any options.
    * Because this is also a 4-bit field, the IPv4 header is limited to a maximum of fifteen 32-bit words or 60 bytes.
    * The normal value of this field (when no options are present) is 5. There is no such field in IPv6 because the header length is fixed at 40 bytes.
* The 8 bits following the header length (IPv4) are two fields used for special processing of the datagram when it is forwarded, in both IPv4 and IPv6:
    * The first 6 bits are the **Differentiated Services Field (DS)** field.
    * The last 2 bits are the **Explicit Congestion Notification (ECN)** field or indicator bits.
* The **Total Length** field is the total length of the IPv4 datagram in bytes.
    * Using this field and the IHL field can indicate where the data portion of the datagram starts, and its length.
    * Because this is a 16-bit field, the maximum size of an IPv4 datagram (including header) is 65,535 bytes.
    * This field is required in the header because some lower-layer protocols that carry IPv4 datagrams do not (accurately) convey the size of encapsulated datagrams on their own. For example, Ethernet pads small frames to be a minimum length (64 bytes) and an IPv4 datagram (minimum 20 bytes) can be smaller than the minimum Ethernet payload size (46 bytes). Without the Total Length field, the IPv4 implementation would not know how much of a 46-byte Ethernet frame was really an IP datagram, as opposed to padding.
    * Although it is possible to send a 65,535-byte IP datagram, most link layers (such as Ethernet) are not able to carry one this large without fragmenting it into smaller pieces.
        * <u>In IPv4, a host is not required to be able to receive an IPv4 datagram larger than 576 bytes.</u>
        * <u>In IPv6 a host must be able to process a datagram at least as large as the MTU of the link to which it is attached, and the minimum link MTU is 1280 bytes.</u>

        Many applications that use the UDP protocol ([Chapter 10](ch10.md)) for data transport (e.g., DNS, DHCP, etc.) use a limited data size of 512 bytes to avoid the 576-byte IPv4 limit. TCP chooses its own datagram size based on additional information ([Chapter 15](ch15.md)).

    * When an IPv4 datagram is fragmented into multiple smaller fragments, each of which itself is an independent IP datagram, the Total Length field reflects the length of the particular fragment.

* The **Payload Length** field is the length of the IPv6 datagram not including the length of the header; extension headers, however, are included in the Payload Length field. In IPv6, fragmentation is not supported by the header.
    * The 16-bit size of this field limits its maximum value to 65,535 (64KB), which applies to the payload length, not the entire datagram.
    * In addition, IPv6 supports a **jumbogram** option that provides for the possibility (at least theoretically) of single packets with payloads as large as 4GB (4,294,967,295 bytes).
* The **Identification** field (IPv4) indentifies each datagram sent by an IPv4 host. To prevent confusion among fragments of a datagrams, the sending host normally increments an internal counter by 1 each time a datagram is sent (from one of its IP addresses) and copies the value of the counter into the IPv4 Identification field.
    * This field is most important for implementing fragmentation, along with the Flags and Fragment Offset fields.
    * In IPv6, this field shows up in the Fragmentation extension header,
* The **Time-to-Live** field, or **TTL**, sets an upper limit on the number of routers through which a datagram can pass.
    * This field initialized by the sender to some value (64 is recommended, although 128 or 255 is not uncommon) and decremented by 1 by every router that forwards the datagram. <u>When this field reaches 0, the datagram is thrown away, and the sender is notified with an ICMP message ([Chapter 8](ch8.md)).</u> This prevents packets from getting caught in the network forever should an unwanted routing loop occur.
* The **Protocol** field in the IPv4 header contains a number indicating the type of data found in the payload portion of the datagram. The most common values are 17 (for UDP) and 6 (for TCP).
    * This field provides a demultiplexing feature so that the IP protocol can be used to carry payloads of more than one protocol type. Although this field originally specified the transport-layer protocol the datagram is encapsulating, it now can identify the encapsulated protocol, which may or not be a transport protocol. Other encapsulations are possible, such as IPv4-in-IPv4 (value 4). The official list of the possible values of the Protocol field
is given in the [assigned numbers page](http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml).
* The **Next Header** field in the IPv6 header generalizes the Protocol field from IPv4. It is used to indicate the type of header following the IPv6 header. This field may contain any values defined for the IPv4 Protocol field, or any of the values associated with the IPv6 extension headers.
* The **Header Checksum** field is calculated *over the IPv4 header only*, which means that <u>the payload of the IPv4 datagram (e.g., TCP or UDP data) is not checked for correctness by the IP protocol.</u> To ensure that payload portion of an IP datagram has been correctly delivered, other protocols must cover any important data that follows the header with their own data-integrity-checking mechanisms.
