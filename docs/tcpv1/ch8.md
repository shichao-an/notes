### **Chapter 8. ICMPv4 and ICMPv6: Internet Control Message Protocol**

### Introduction

The IP protocol alone provides no direct way to do the following:

* For an end system to learn the fate of IP packets that fail to make it to their destinations.
* For obtaining diagnostic information (e.g., which routers are used along a path or a method to estimate the round-trip time).

To address these deficiencies, a special protocol called the [**Internet Control Message Protocol**](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol) (ICMP) is used in conjunction with IP to provide diagnostics and control information related to the configuration of the IP protocol layer and the disposition of IP packets.

ICMP provides for the delivery of error and control messages that may require attention. ICMP messages are usually acted on by:

* The IP layer itself,
* Higher-layer transport protocols (TCP or UDP),
* User applications.

ICMP does not provide reliability for IP; it indicates certain classes of failures and configuration information. The most common cause of packet drops (buffer overrun at a router) does not elicit any ICMP information. Other protocols, such as TCP, handle such situations.

Because of the ability of ICMP to affect the operation of important system functions and obtain configuration information, hackers have used ICMP messages in a large number of attacks. As a result of concerns about such attacks, network administrators often arrange to block ICMP messages with firewalls, especially at border routers. If ICMP is blocked, however, a number of common diagnostic utilities (e.g., ping, traceroute) do not work properly.

The term ICMP refers to ICMP in general, and the terms ICMPv4 and ICMPv6 to refer specifically to the versions of ICMP used with IPv4 and IPv6, respectively. ICMPv6 plays a far more important role in the operation of IPv6 than ICMPv4 does for IPv4.

In IPv6, ICMPv6 is used for several purposes beyond simple error reporting and signaling. It is used for:

* **Neighbor Discovery** (ND), which plays the same role as ARP does for IPv4 ([Chapter 4](ch4.md)).
* **Router Discovery** function used for configuring hosts ([Chapter 6](ch6.md)) and multicast address management ([Chapter 9](ch9.md)).
* Manageing hand-offs in Mobile IPv6.

#### Encapsulation in IPv4 and IPv6

[![Encapsulation of ICMP messages in IPv4 and IPv6. The ICMP header contains a checksum covering the ICMP data area. In ICMPv6, the checksum also covers the Source and Destination IPv6 Address, Length, and Next Header fields in the IPv6 header.](figure_8-1.png)](figure_8-1.png " Encapsulation of ICMP messages in IPv4 and IPv6. The ICMP header contains a checksum covering the ICMP data area. In ICMPv6, the checksum also covers the Source and Destination IPv6 Address, Length, and Next Header fields in the IPv6 header.")

* In IPv4, a Protocol field value of 1 indicates that the datagram caries ICMPv4.
* In IPv6, the ICMPv6 message may begin after zero or more extension headers. The last extension header before the ICMPv6 header includes a Next Header field with value 58.

ICMP messages may be fragmented like other IP datagrams ([Chapter 10](ch10.md)), although this is not common.

The following figure shows the format of both ICMPv4 and ICMPv6 messages. The first 4 bytes have the same format for all messages, but the remainder differ from one message to the next.

[![Figure 8-2 All ICMP messages begin with 8-bit Type and Code fields, followed by a 16-bit Checksum that covers the entire message. The type and code values are different for ICMPv4 and ICMPv6. ](figure_8-2.png)](figure_8-2.png "Figure 8-2 All ICMP messages begin with 8-bit Type and Code fields, followed by a 16-bit Checksum that covers the entire message. The type and code values are different for ICMPv4 and ICMPv6. ")

In ICMPv4:

* 42 different values are reserved for the **Type** field [[ICMPTYPES](http://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml)], which identify the particular message. Only about 8 of these are in regular use.
* Many types of ICMP messages also use different values of the **Code** field to further specify the meaning of the message.
* The **Checksum** field covers the entire ICMPv4 message; in ICMPv6 it also covers a pseudo-header derived from portions of the IPv6 header.  The algorithm used for computing the checksum is the same as that used for the IP header checksum defined in [Chapter 5](ch5.md).
    * This is our first example of an *end-to-end* checksum. It is carried all the way from the sender of the ICMP message to the final recipient. In contrast, the IPv4 header checksum discussed in [Chapter 5](ch5.md) is changed at every router hop. If an ICMP implementation receives an ICMP message with a bad checksum, the message is discarded; there is no ICMP message to indicate a bad checksum in a received ICMP message. Recall that the IP layer has no protection on the payload portion of the datagram. If ICMP did not include a checksum, the contents of the ICMP message might not be correct, leading to incorrect system behavior.

### ICMP Messages

ICMP messages are grouped into two major categories:

* **Error messages**: related to problems with delivering IP datagrams.
* **Query or information messages**: related to information gathering and configuration.

#### ICMPv4 Messages

For ICMPv4, the informational messages include:

* Echo Request (type 8)
* Echo Reply (type 0)
* Router Advertisement (type 9)
* Router Solicitation (type 10)

Router Advertisement and Router Solicitation are together called Router Discovery.

The most common error message types are:

* Destination Unreachable (type 3)
* Redirect (type 5)
* Time Exceeded (type 11)
* Parameter Problem (type 12)

The table below lists the message types defined for standard ICMPv4 messages. Types marked with asterisks (*) are the most common. Those marked with a plus (+) may contain [RFC4884] extension objects. In the fourth column, E is for error messages and I indicates query/informational messages.

Type | Official Name | Reference | E/I | Use/Comment
---- | ------------- | --------- | --- | -----------
0 (*) | Echo Reply | [RFC0792] | I | Echo (`ping`) reply; returns data
3 (*)(+) | Destination Unreachable | [RFC0792] | E | Unreachable host/protocol
4 | Source Quench | [RFC0792] | E | Indicates congestion (deprecated)
5 (*) | Redirect | [RFC0792] | E | Indicates alternate router should be used
8 (*) | Echo | [RFC0792] | I | Echo (`ping`) request (data optional)
9 | Router Advertisement | [RFC1256] | I | Indicates router addresses/preferences
10 | Router Solicitation | [RFC1256] | I | Requests Router Advertisement
11 (*)(+) | Time Exceeded | [RFC0792] | E | Resource exhausted (e.g., IPv4 TTL)
12 (*)(+) | Parameter Problem | [RFC0792] | E | Malformed packet or header

For the commonly used messages, the code numbers shown in the table below are used. Some messages are capable of carrying extended information

Type | Code | Official Name | Use/Comment
---- | ---- | ------------- | -----------
3 | 0 | Net Unreachable | No route (at all) to destination
3 (*) | 1 | Host Unreachable | Known but unreachable host
3 | 2 | Protocol Unreachable | Unknown (transport) protocol
3 (*) | 3 | Port Unreachable | Unknown/unused (transport) port
3 (*) | 4 | Fragmentation Needed and Don’t Fragment Was Set (PTB message) | Needed fragmentation prohibited by DF bit; used by PMTUD [RFC1191]
3 | 5 | Source Route Failed | Intermediary hop not reachable
3 | 6 | Destination Network Unknown | Deprecated [RFC1812]
3 | 7 | Destination Host Unknown | Destination does not exist
3 | 8 | Source Host Isolated | Deprecated [RFC1812]
3 | 9 | Communication with Destination Network Administratively | Prohibited Deprecated [RFC1812]
3 | 10 | Communication with Destination Host Administratively | Prohibited Deprecated [RFC1812]
3 | 11 | Destination Network Unreachable for Type of Service | Type of service not available (net)
3 | 12 | Destination Host Unreachable for Type of Service | Type of service not available (host)
3 | 13 | Communication Administratively Prohibited | Communication prohibited by filtering policy
3 | 14 | Host Precedence Violation | Precedence disallowed for src/dest/port
3 | 15 | Precedence Cutoff in Effect | Below minimum ToS [RFC1812]
5 | 0 | Redirect Datagram for the Network (or Subnet) | Indicates alternate router
5 (*) | 1 | Redirect Datagram for the Host | Indicates alternate router (host)
5 | 2 | Redirect Datagram for the Type of Service and Network | Indicates alternate router (ToS/net)
5 | 3 | Redirect Datagram for the Type of Service and Host | Indicates alternate router (ToS/host)
9 | 0 | Normal Router Advertisement | Router’s address and configuration information
9 | 16 | Does Not Route Common Traffic | With Mobile IP [RFC5944], router does not route ordinary packets
11 (*) | 0 | Time to Live Exceeded in Transit | Hop limit/TTL exceeded
11 | 1 | Fragment Reassembly Time Exceeded | Not all fragments of datagram arrived before reassembly timer expired
12 (*) | 0 | Pointer Indicates the Error | Byte offset (pointer) indicates first problem field
12 | 1 | Missing a Required Option | Deprecated/historic
12 | 2 | Bad Length Packet had invalid | Total Length field

#### ICMPv6 Messages

ICMPv6 is responsible not only for error and informational messages but also for a great deal of IPv6 router and host configuration.

[p358-359]

In ICMPv6, as in ICMPv4, messages are grouped into the informational and error classes. In ICMPv6, however, all the error messages have a 0 in the high-order bit of the **Type** field. Thus, ICMPv6 types 0 through 127 are all errors, and types 128 through 255 are all informational. Many of the informational messages are request/reply pairs.

In comparing the common ICMPv4 messages with the ICMPv6 standard messages, we conclude that some of the effort in designing ICMPv6 was to eliminate the unused messages from the original specification while retaining the useful ones. Following this approach, ICMPv6 also makes use of the **Code** field, primarily to refine the meanings of certain error messages.

[p360]

In addition to the Type and Code fields that define basic functions in ICMPv6, a large number of standard options are also supported, some of which are required.  This distinguishes ICMPv6 from ICMPv4 (ICMPv4 does not have options).

#### Processing of ICMP Messages

In ICMP, the processing of incoming messages varies from system to system. Generally:

* Incoming informational requests are handled automatically by the operating system.
* Error messages are delivered to user processes or to a transport protocol such as TCP.

The processes may choose to act on them or ignore them. Exceptions to this general rule include:

* The Redirect message. This results in an automatic update to the host’s routing table.
* The Destination Unreachable—Fragmentation Required messages. This is used in the path MTU discovery (PMTUD) mechanism, which is generally implemented by the transport-layer protocols such as TCP.

In ICMPv6, the following rules are applied when processing incoming ICMPv6 messages:

1. Unknown ICMPv6 error messages must be passed to the upper-layer process that produced the datagram causing the error (if possible).
2. Unknown ICMPv6 informational messages are dropped.
3. ICMPv6 error messages include as much of the original ("offending") IPv6 datagram that caused the error as will fit without making the error message datagram exceed the minimum IPv6 MTU (1280 bytes).
4. When processing ICMPv6 error messages, the upper-layer protocol type is extracted from the original or "offending" packet (contained in the body of the ICMPv6 error message) and used to select the appropriate upper-layer process. If this is not possible, the error message is silently dropped after any IPv6-layer processing.
5. There are special rules for handling errors (see Section 8.3).
6. An IPv6 node must limit the rate of ICMPv6 error messages it sends. There are a variety of ways of implementing the rate-limiting

### ICMP Error Messages

The distinction between the error and informational classes of ICMP messages is important. An ICMP error message is not to be sent in response to any of the following messages:

* Another ICMP error message,
* Datagrams with bad headers (e.g., bad checksum),
* IP-layer broadcast/multicast datagrams,
* Datagrams encapsulated in link-layer broadcast or multicast frames,
* Datagrams with an invalid or network zero source address,
* Any fragment other than the first.

The reason for imposing these restrictions on the generation of ICMP errors is to limit the creation of so-called [broadcast storms](https://en.wikipedia.org/wiki/Broadcast_radiation), a scenario in which the generation of a small number of messages creates an unwanted traffic cascade (e.g., by generating error responses in response to error responses, indefinitely). These rules can be summarized as follows:

#### ICMPv4 error messages *

An ICMPv4 error message is never generated in response to:

* An ICMPv4 error message. (An ICMPv4 error message may, however, be generated in response to an ICMPv4 query message.)
* A datagram destined for an IPv4 broadcast address or an IPv4 multicast address (formerly known as a class D address).
* A datagram sent as a link-layer broadcast.
* A fragment other than the first.
* A datagram whose source address does not define a single host. This means that the source address cannot be any of the following:
    * Zero address,
    * Loopback address,
    * Broadcast address,
    * Multicast address.

#### ICMPv4 error messages *

An ICMPv6 error message is never generated in response to

* An ICMPv6 error message
* An ICMPv6 Redirect message
* A packet destined for an IPv6 multicast address, with two exceptions:
    * The Packet Too Big (PTB) message
    * The Parameter Problem message (code 2)
* A packet sent as a link-layer multicast (with the exceptions noted previously)
* A packet sent as a link-layer broadcast (with the exceptions noted previously)
* A packet whose source address does not uniquely identify a single node. This means that the source address cannot be any of the following:
    * Unspecified address,
    * IPv6 multicast address,
    * Any address known by the sender to be an anycast address.

#### Rate-limiting ICMP messages with token buckets *

In addition to the rules governing the conditions under which ICMP messages are generated, there is also a rule that limits the overall ICMP traffic level from a single sender. In [RFC4443], a recommendation for rate-limiting ICMP messages is to use a **[token bucket](https://en.wikipedia.org/wiki/Token_bucket)**.

With a token bucket, a "bucket" holds a maximum number (*B*) of "tokens", each of which allows a certain number of messages to be sent. The bucket is periodically filled with new tokens (at rate *N*) and drained by 1 for each message sent. Thus, a token bucket (or **token bucket filter**, as it is often called) is characterized by the parameters (*B*, *N*). For small or midsize devices, [RFC4443] provides an example token bucket using the parameters (10, 10). Token buckets are a common mechanism used in protocol implementations to limit bandwidth utilization, and in many cases *B* and *N* are in byte units rather than message units.

#### Copy of offending datagram headers in ICMP error message

When an ICMP error message is sent, it contains a copy of the full IP header from the "offending" or "original" datagram (i.e., the IP header of the datagram that caused the error to be generated, including any IP options), plus any other data from the original datagram’s IP payload area such that the generated IP/ ICMP datagram’s size does not exceed a specific value. For IPv4 this value is 576 bytes, and for IPv6 it is the IPv6 minimum MTU, which is at least 1280 bytes.

Including a portion of the payload from the original IP datagram lets the receiving ICMP module associate the message with one particular protocol (e.g., TCP or UDP) from the Protocol or Next Header field in the IP header and one particular user process (from the TCP or UDP port numbers that are in the TCP or UDP header contained in the first 8 bytes of the IP datagram payload area).

[p362-363]

#### Extended ICMP and Multipart Messages

[p363-364]

#### Destination Unreachable (ICMPv4 Type 3, ICMPv6 Type 1) and Packet Too Big (ICMPv6 Type 2)

Messages of this type are used to indicate that <u>a datagram could not be delivered all the way to its destination because of either a problem in transit or the lack of a receiver interested in receiving it.</u> Although 16 different codes are defined for this message in ICMPv4, only 4 are commonly used. These include:

* Host Unreachable (code 1)
* Port Unreachable (code 3)
* Fragmentation Required/ Don’t-Fragment Specified (code 4),
* Communication Administratively Prohibited (code 13).

In ICMPv6, the Destination Unreachable message is type 1 with seven possible code values. In ICMPv6, as compared with IPv4, the Fragmentation Required message has been replaced by an entirely different type (type 2), but the usage is very similar to the corresponding ICMP Destination Unreachable message. In ICMPv6 this is called the Packet Too Big (PTB) message. We will use the simpler ICMPv6 PTB terminology from here onward to refer to either the ICMPv4 (type 3, code 4) message or the ICMPv6 (type 2, code 0) message.

##### **ICMPv4 Host Unreachable (Code 1) and ICMPv6 Address Unreachable (Code 3)**

This form of the Destination Unreachable message is <u>generated by a router or host when it is required to send an IP datagram to a host using direct delivery ([Chapter 5](ch5.md#direct-delivery)) but for some reason cannot reach the destination</u>. This situation may arise, for example, because <u>the last-hop router is attempting to send an ARP request to a host that is either missing or down.</u> (This situation is explored in [Chapter 4](ch4.md), which describes ARP.) For ICMPv6, which uses a somewhat different mechanism for detecting unresponsive hosts, this message can be the result of a failure in the ND process (see Section 8.5).

##### **ICMPv6 No Route to Destination (Code 0)**

[p365]

##### **ICMPv4 Communication Administratively Prohibited (Code 13) and ICMPv6 Communication with Destination Administratively Prohibited (Code 1)**

[p365]

##### **ICMPv4 Port Unreachable (Code 3) and ICMPv6 Port Unreachable (Code 4)**

The Port Unreachable message is generated when an incoming datagram is destined for an application that is not ready to receive it. This occurs most commonly in conjunction with UDP, when a message is sent to a port number that is not in use by any server process. If UDP receives a datagram and the destination port does not correspond to a port that some process has in use, UDP responds with an ICMP Port Unreachable message.

[p366-370]

##### **ICMPv4 PTB (Code 4)**

##### **ICMPv6 PTB (Type 2, Code 0)**

##### **ICMPv6 Beyond Scope of Source Address (Code 2)**

##### **ICMPv6 Source Address Failed Ingress/Egress Policy (Code 5)**

##### **ICMPv6 Reject Route to Destination (Code 6)**

#### Redirect (ICMPv4 Type 5, ICMPv6 Type 137)

#### ICMP Time Exceeded (ICMPv4 Type 11, ICMPv6 Type 3)

Every IPv4 datagram has a **Time-to-Live** (TTL) field in its IPv4 header, and every IPv6 datagram has a **Hop Limit** field in its header ([Chapter 5](ch5.md)).

As originally conceived, the 8-bit TTL field was to hold the number of seconds a datagram was allowed to remain active in the network before being forcibly discarded (a good thing if forwarding loops are present). Because of an additional rule that said that any router must decrement the TTL field by at least 1, combined with the fact that datagram forwarding times grew to be small fractions of a second, the <u>TTL field has been used in practice as a limitation on the number of hops an IPv4 datagram is allowed to take before it is discarded by a router.</u> This usage was formalized and
ultimately adopted in IPv6.

ICMP Time Exceeded (code 0) messages are generated when a router discards a datagram because the TTL or Hop Limit field is too low (i.e., arrives with value 0 or 1 and must be forwarded). This message is important for the proper operation of the `traceroute` tool (called `tracert` on Windows). Its format, for both ICMPv4 and ICMPv6, is given in the figure below.

[![Figure 8-10 The ICMP Time Exceeded message format for ICMPv4 and ICMPv6. The message is standardized for both the TTL or hop count being exceeded (code 0) or the time for reassembling fragments exceeding some preconfigured threshold (code 1).](figure_8-10.png)](figure_8-10.png "Figure 8-10 The ICMP Time Exceeded message format for ICMPv4 and ICMPv6. The message is standardized for both the TTL or hop count being exceeded (code 0) or the time for reassembling fragments exceeding some preconfigured threshold (code 1).")

Another less common variant of this message is when a fragmented IP datagram only partially arrives at its destination (all its fragments do not arrive after a period of time). In such cases, a variant of the ICMP Time Exceeded message (code 1) is used to inform the sender that its overall datagram has been discarded. Recall that if any fragment of a datagram is dropped, the entire datagram is lost.

##### **Example: The `traceroute` Tool**

The `traceroute` tool is used to determine the routers used along a path from a sender to a destination. This section discusses the operation of the IPv4 version. The approach involves sending datagrams first with an IPv4 TTL field set to 1 and allowing the expiring datagrams to induce routers along the path to send ICMPv4 Time Exceeded (code 0) messages. Each round, the sending TTL value is increased by 1, causing the routers that are one hop farther to expire the datagrams and generate ICMP messages. These messages are sent from the router’s primary IPv4 address "facing" the sender.

In this example, `traceroute` is used to send UDP datagrams from the laptop to the host `www.eecs.berkeley.edu`. (an Internet host with IPv4 address 128.32.244.172). This is accomplished using the following command:

```text
Linux% traceroute –m 2 www.cs.berkeley.edu
traceroute to web2.eecs.berkeley.edu (128.32.244.172), 2 hops max,
52 byte packets
 1 gw (192.168.0.1) 3.213 ms 0.839 ms 0.920 ms
 2 10.0.0.1 (10.0.0.1) 1.524 ms 1.221 ms 9.176 ms
```

The `–m` option instructs `traceroute` to perform only two rounds: one using TTL = 1 and one using TTL = 2. Each line gives the information found at the corresponding TTL. For example, line 1 indicates that one hop away a router with IPv4 address 192.168.0.1 was found and that three independent round-trip-time (RTT) measurements (3.213, 0.839, and 0.920ms) were taken. The difference between the first and subsequent times relates to additional work that is involved in the first measurement (i.e., an ARP transaction).

[p377-379]

#### Parameter Problem (ICMPv4 Type 12, ICMPv6 Type 4)
