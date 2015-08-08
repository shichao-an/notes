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
    * The first 6 bits are the **Differentiated Services (DS)** field.
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
    * This field initialized by the sender to some value (64 is recommended, although 128 or 255 is not uncommon) and decremented by 1 by every router that forwards the datagram. <u>When this field reaches 0, the datagram is thrown away, and the sender is notified with an ICMP message</u> ([Chapter 8](ch8.md)). This prevents packets from getting caught in the network forever should an unwanted routing loop occur.
    * In IPv6, the field has been renamed to its de facto use: **Hop Limit**.
* The **Protocol** field in the IPv4 header contains a number indicating the type of data found in the payload portion of the datagram. The most common values are 17 (for UDP) and 6 (for TCP).
    * This field provides a demultiplexing feature so that the IP protocol can be used to carry payloads of more than one protocol type. Although this field originally specified the transport-layer protocol the datagram is encapsulating, it now can identify the encapsulated protocol, which may or not be a transport protocol. Other encapsulations are possible, such as IPv4-in-IPv4 (value 4). The official list of the possible values of the Protocol field
is given in the [assigned numbers page](http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml).
* The **Next Header** field in the IPv6 header generalizes the Protocol field from IPv4. It is used to indicate the type of header following the IPv6 header. This field may contain any values defined for the IPv4 Protocol field, or any of the values associated with the IPv6 extension headers.
* The **Header Checksum** field is calculated *over the IPv4 header only*, which means that <u>the payload of the IPv4 datagram (e.g., TCP or UDP data) is not checked for correctness by the IP protocol.</u> To ensure the payload has been correctly delivered, other protocols must cover any important data that follows the header with their own data-integrity-checking mechanisms.
    * Almost all protocols encapsulated in IP (ICMP, IGMP, UDP, and TCP) have a checksum in their own headers to cover their header and data and also to cover certain parts of the IP header they deem important (a form of "layering violation").
    * The IPv6 header does not have any checksum field.
    * The algorithm used in computing a checksum (also used by most of the other Internet-related protocols) is sometimes known as the **Internet checksum**.
    * When an IPv4 datagram passes through a router, its header checksum must change as a result of decrementing the TTL field.
* The **Source IP Address** is the IP address of the datagram's sender and the **Destination IP Address** of where the datagram is destined. These are 32-bit values for IPv4 and 128-bit values for IPv6, and they usually identify a single interface on a computer, although multicast and broadcast addresses ([Chapter 2](ch2.md)) violate this rule.

#### The Internet Checksum

The **Internet checksum** is a 16-bit mathematical sum used to determine, with reasonably high probability, whether a received message or portion of a message matches the one sent. the Internet checksum algorithm is not the same as the common **cyclic redundancy check** (CRC), which offers stronger protection.

To compute the IPv4 header checksum for an outgoing datagram, the value of the datagram’s Checksum field is first set to 0. Then, the 16-bit one’s complement sum of the header is calculated (the entire header is considered a sequence of 16-bit words). The 16-bit one’s complement of this sum is then stored in the Checksum field to make the datagram ready for transmission.

When an IPv4 datagram is received, a checksum is computed across the whole header, including the value of the Checksum field itself. Assuming there are no errors, the computed checksum value is always 0 (a one’s complement of the value FFFF). <u>The value of the Checksum field in the packet can never be FFFF.</u> If it were, the sum (prior to the final one’s complement operation at the sender) would have to have been 0. No sum can ever be 0 using one’s complement addition unless all the bytes are 0. ([end-round carry](https://en.wikipedia.org/wiki/Signed_number_representations#Ones.27_complement))

When the header is found to be bad (the computed checksum is nonzero), the IPv4 implementation discards the received datagram. No error message is generated. It is up to the higher layers to somehow detect the missing datagram and retransmit if necessary.

##### **Mathematics of the Internet Checksum**

For the mathematically inclined, the set of 16-bit hexadecimal values V = {0001, . . . , FFFF} and the one’s complement sum operation + together form an [Abelian group](https://en.wikipedia.org/wiki/Abelian_group). The following properties are obeyed:

* For any X,Y in V, (X + Y) is in V [closure]
* For any X,Y,Z in V, X + (Y + Z) = (X + Y) + Z [associativity]
* For any X in V, e + X = X + e = X where e = FFFF [identity]
* For any X in V, there is an X′ in V such that X + X′ = e [inverse]
* For any X,Y in V, (X + Y) = (Y + X) [commutativity]

Note that in the set V and the group &lt;V,+&gt;, number 0000 deleted the from consideration. If we put the number 0000 in the set V, then &lt;V,+&gt; is not a group any longer. [p187-188]

#### DS Field and ECN

The third and fourth fields of the IPv4 header (second and third fields of the IPv6 header) are the **Differentiated Services** (called DS Field) and **ECN** fields, formerly called the **ToS Byte** or IPv6 **Traffic Class**.

Differentiated Services (called *DiffServ*) is a framework and set of standards aimed at supporting differentiated classes of service (beyond just best-effort) on the Internet. IP datagrams that are marked in certain ways may be forwarded differently (e.g., with higher priority) and can lead to increased or decreased queuing delay in the network and other special effects (possibly with associated special fees imposed by an ISP). [p188]

The Differentiated Services Code Point (DSCP) is a number (in the DS Field) that refers to a particular predefined arrangement of bits with agreed-upon meaning. Datagrams have a DSCP assigned to them when they are given to the network infrastructure that remains unmodified during delivery ,but policies (such as how many high-priority packets are allowed to be sent in a period of time) may cause a change in DSCP during delivery. [p188]

The pair of ECN bits marks a datagram with a *congestion indicator* when passing through a router that has a significant amount of internally queued traffic. Both bits are set by persistently congested ECN-aware routers when forwarding packets. When a marked packet is received at the destination, some protocol (such as TCP) will notice that the packet is marked and indicate this fact back to the sender, which would then slow down, thereby easing congestion before a router is forced to drop traffic because of overload. This mechanism is one of several aimed at avoiding or dealing with network congestion.

(Original uses for the ToS and Traffic Class skipped) [p188-189]

The 6-bit DS Field holds the DSCP, providing support for 64 distinct code points. The particular value of the DSCP, expressed as **per-hop behavior** (PHB), tells a router the forwarding treatment or special handling the datagram should receive. The default value for the DSCP is generally 0, which corresponds to routine, best-effort Internet traffic.

[![The DS Field contains the DSCP in 6 bits (5 bits are currently standardized to indicate the forwarding treatment the datagram should receive when forwarded by a compliant router). The following 2 bits are used for ECN and may be turned on in the datagram when it passes through a persistently congested router. When such datagrams arrive at their destinations, the congestion indication is sent back to the source in a later datagram to inform the source that its datagrams are passing through one or more congested routers.](figure_5-5_600.png)](figure_5-5.png "The DS Field contains the DSCP in 6 bits (5 bits are currently standardized to indicate the forwarding treatment the datagram should receive when forwarded by a compliant router). The following 2 bits are used for ECN and may be turned on in the datagram when it passes through a persistently congested router. When such datagrams arrive at their destinations, the congestion indication is sent back to the source in a later datagram to inform the source that its datagrams are passing through one or more congested routers.")

As indicated in the table below, the DSCP values are divided into three pools: standardized, experimental/local use (EXP/LU), and experimental/local use.

Pool | Code Point Prefix | Policy
---- | ----------------- | ------
1 | xxxxx0 | Standards
2 | xxxx11 | EXP/LU
3 | xxxx01 | EXP/LU(*)

A router is to first segregate traffic into different classes. Traffic within a common class may have different drop probabilities, allowing the router to decide what traffic to drop first if it is forced to discard traffic. The 3-bit class selector provides for eight defined code points (called the **class selector code points**) that correspond to PHBs with a specified minimum set of features providing similar functionality to the earlier IP precedence capability. These are called **class selector compliant PHBs**. Code points of the form xxx000 always map to such PHBs.

The **Assured Forwarding** (AF) group provides forwarding of IP packets in a fixed number of independent AF classes. Traffic from one class is forwarded separately from other classes. Within a traffic class, a datagram is assigned a **drop precedence**. Datagrams of higher drop precedence in a class areare discarded with higher priority over those with lower drop precedence in the same class. Combining the traffic class and drop precedence, the name *AFij* corresponds to assured forwarding class *i* with drop precedence *j*.

The **Expedited Forwarding** (EF) service provides the appearance of an uncongested network (EF traffic should receive relatively low delay, jitter, and loss). This requires the rate of EF traffic going out of a router to be at least as large as the rate coming in. Consequently, EF traffic will only ever have to wait in a router queue behind other EF traffic.

The following table indicates the class selector DSCP values:

<small>

Name | Value | Reference | Description
---- | ----- | --------- | -----------
CS0 | 000000 | [RFC2474] | Class selector (best-effort/routine)
CS1 | 001000 | [RFC2474] | Class selector (priority)
CS2 | 010000 | [RFC2474] | Class selector (immediate)
CS3 | 011000 | [RFC2474] | Class selector (flash)
CS4 | 100000 | [RFC2474] | Class selector (flash override)
CS5 | 101000 | [RFC2474] | Class selector (CRITIC/ECP)
CS6 | 110000 | [RFC2474] | Class selector (internetwork control)
CS7 | 111000 | [RFC2474] | Class selector (control)
AF11 | 001010 | [RFC2597] | Assured Forwarding (class 1,dp 1)
AF12 | 001100 | [RFC2597] | Assured Forwarding (1,2)
AF13 | 001110 | [RFC2597] | Assured Forwarding (1,3)
AF21 | 010010 | [RFC2597] | Assured Forwarding (2,1)
AF22 | 010100 | [RFC2597] | Assured Forwarding (2,2)
AF23 | 010110 | [RFC2597] | Assured Forwarding (2,3)
AF31 | 011010 | [RFC2597] | Assured Forwarding (3,1)
AF32 | 011100 | [RFC2597] | Assured Forwarding (3,2)
AF33 | 011110 | [RFC2597] | Assured Forwarding (3,3)
AF41 | 100010 | [RFC2597] | Assured Forwarding (4,1)
AF42 | 100100 | [RFC2597] | Assured Forwarding (4,2)
AF43 | 100110 | [RFC2597] | Assured Forwarding (4,3)
EF PHB | 101110 | [RFC3246] | Expedited Forwarding
VOICE-ADMIT | 101100 | [RFC5865] | Capacity-Admitted Traffic

</small>

#### IP Options
