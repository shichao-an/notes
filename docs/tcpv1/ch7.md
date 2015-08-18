### **Chapter 7. Firewalls and Network Address Translation (NAT)**

> Perhaps ironically, the development and eventual widespread use of NAT has contributed to significantly slow the adoption of IPv6.
> <small>*TCPv1*</small>

Many security problems (attacks) were caused by bugs or unplanned protocol operations in the software implementations of Internet hosts. Fixing the problem would have required a way to control the Internet traffic to which the end hosts were exposed. Today, this is provided by a **firewall**, a type of router that restricts the types of traffic it forwards. [p299]

As firewalls are being deployed, another problem was becoming important: the number of available IPv4 addresses was diminishing,
with a threat of exhaustion. One of the most important mechanisms developed to deal with this, aside from IPv6, is called **Network Address Translation** (NAT). With NAT, Internet addresses need not be globally unique, but can be reused in different parts of the Internet, called *address realms*. This greatly eased the problem of address exhaustion.

### Firewalls

Given the enormous management problems associated with trying to keep end system software up-to-date and bug-free, the focus of resisting attacks expanded

* From: securing end systems,
* To: restricting the Internet traffic allowed to flow to end systems by filtering out some traffic using firewalls.

Today, several different types of firewalls have evolved.

The two major types of firewalls commonly used include **proxy firewalls** and **packet-filtering firewalls**. The main difference between them is the layer in the protocol stack at which they operate, and consequently the way IP addresses and port numbers are used. The packet-filtering firewall is an Internet router that drops datagrams that (fail to) meet specific criteria. The proxy firewall operates as a multihomed server host from the viewpoint of an Internet client. That is, it is the endpoint of TCP and UDP transport associations; it does not typically route IP datagrams at the IP protocol layer.

#### Packet-Filtering Firewalls

Packet-filtering firewalls act as Internet routers and filter (drop) some traffic. They can generally be configured to discard or forward packets whose headers meet (or fail to meet) certain criteria, called *filters*.

Popular filters involve:

* Undesired IP addresses or options,
* Types of ICMP messages,
* Various UDP or TCP services, based on the port numbers contained in each packet.

Stateless and stateful:

* *Stateless* firewalls treat each datagram individually.
* *Stateful* firewalls are able associate packets with either previous or future packets to make inferences about datagrams or streams.

[p300]

A typical packet-filtering firewall is shown below.

In this figure

* The firewall is an Internet router with three network interfaces:
    * "inside"
    * "outside"
    * "DMZ"
* The DMZ subnet provides access to an extranet or DMZ where servers are deployed for Internet users to access.
* Network administrators install filters or **access control lists** (ACLs, basically policy lists indicating what types of packets to discard or forward) in the firewall.
* Typically, these filters conservatively block traffic from the outside that may be harmful and liberally allow traffic to travel from inside to outside.

[![A typical packet-filtering firewall configuration. The firewall acts as an IP router between an “inside” and an “outside” network, and sometimes a third “DMZ” or extranet network, allowing only certain traffic to pass through it. A common configuration allows all traffic to pass from inside to outside but only a small subset of traffic to pass in the reverse direction. When a DMZ is used, only certain services are permitted to be accessed from the Internet.](figure_7-1.png)](figure_7-1.png "A typical packet-filtering firewall configuration. The firewall acts as an IP router between an “inside” and an “outside” network, and sometimes a third “DMZ” or extranet network, allowing only certain traffic to pass through it. A common configuration allows all traffic to pass from inside to outside but only a small subset of traffic to pass in the reverse direction. When a DMZ is used, only certain services are permitted to be accessed from the Internet.")

#### Proxy Firewalls

Proxy firewalls are not really Internet routers. They are essentially hosts running one or more [**application-layer gateways**](https://en.wikipedia.org/wiki/Application-level_gateway) (ALGs), hosts with more than one network interface that relay traffic of certain types between one connection/association and another at the application layer.

The figure below illustrates a proxy firewall:

* Clients on the inside of the firewall are usually configured in a special way to associate (or connect) with the proxy instead of the actual end host providing the desired service.
* The firewalls act as multihomed hosts with their IP forwarding capability typically disabled.
* As with packet-filtering firewalls, a common configuration is to have an "outside" interface assigned a globally routable IP address and for its "inner" interface to be configured with a private IP address. Thus, proxy firewalls support the use of private address realms.

[![The proxy firewall acts as a multihomed Internet host, terminating TCP connections and UDP associations at the application layer. It does not act as a conventional IP router but rather as an ALG. Individual applications or proxies for each service supported must be enabled for communication to take place through the proxy firewall.](figure_7-2_600.png)](figure_7-2.png "The proxy firewall acts as a multihomed Internet host, terminating TCP connections and UDP associations at the application layer. It does not act as a conventional IP router but rather as an ALG. Individual applications or proxies for each service supported must be enabled for communication to take place through the proxy firewall.")

This type of firewall can be quite secure at the cost of brittleness and lack of flexibility:

* Since this style of firewall must contain a proxy for each transport-layer service, any new services to be used must have a corresponding proxy installed and operated for connectivity to take place through the proxy.
* Each client must be configured to find the proxy, for example using the [Web Proxy Auto-Discovery Protocol](https://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol) (WPAD), although there are some alternatives: capturing proxies that catch all traffic of a certain type regardless of destination address).
* Significant intervention is required from network operators to support additional services.

The two most common forms of proxy firewalls are HTTP proxy firewalls and SOCKS firewalls.

* **HTTP proxy firewalls**, also called **Web proxies**, work only for the HTTP and HTTPS (Web) protocols.
    * These proxies act as Web servers for internal clients and as Web clients when accessing external Web sites.
    * Such proxies often also operate as **Web caches**. These caches save copies of Web pages so that subsequent accesses can be served directly from the cache instead of from the originating Internet Web server. Doing so can reduce latency to display Web pages and improve the experience of users accessing the Web.
    * Some Web proxies are also used as **content filters**, which attempt to block access to certain Web sites based on a “blacklist” of prohibited sites. Conversely, **tunneling proxy servers** are available on the Internet. These servers (e.g., [psiphon](https://en.wikipedia.org/wiki/Psiphon), [CGIProxy](https://en.wikipedia.org/wiki/CGIProxy)) essentially perform the opposite function: to allow users to avoid being blocked by content filters.
* **SOCKS firewalls** uses the [SOCKS protocol](https://en.wikipedia.org/wiki/SOCKS), which is more generic than HTTP for proxy access and is applicable to more services than just the Web. Two versions of SOCKS are currently in use: version 4 (SOCKS5) and version 5 (SOCKS5). Version 4 provides the basic support for proxy traversal, and version 5 adds strong authentication, UDP traversal, and IPv6 addressing.
    * To use a SOCKS proxy, an application must be written to use SOCKS (it must be "socksified") and configured to know the location and version of the SOCKS proxy. Then the client uses the SOCKS protocol to request the proxy to perform network connections and, optionally, DNS lookups.

### Network Address Translation (NAT)

NAT is a mechanism that allows the same sets of IP addresses to be reused in different parts of the Internet. With NAT as a common use, all incoming and outgoing traffic passes through a single NAT device that partitions the inside (private) address realm from the global Internet address realm, all the internal systems can be provided Internet connectivity as clients using locally assigned, private IP addresses. [p303]

NAT was introduced to solve two problems: address depletion and concerns regarding the scalability of routing. NAT was initially suggested as a stopgap, temporary measure to be used until the deployment of some protocol with a larger number of addresses (IPv6) became widespread. Routing scalability was being tackled with the development of Classless Inter-Domain Routing (CIDR, [Chapter 2](ch2.md))

NAT is popular because:

1. It reduces the need for globally routable Internet addresses
2. It offers some degree of natural firewall capability and requires little configuration.

Perhaps ironically, the development and eventual widespread use of NAT has contributed to significantly slow the adoption of IPv6. Among its other benefits, IPv6 was intended to make NAT unnecessary.

NAT has several drawbacks:

* Offering Internet-accessible services from the private side requires special configuration because privately addressed systems are not directly reachable from the Internet.
* Every packet in both directions of a connection or association must pass through the same NAT, because the NAT must actively rewrite the addressing information in each packet.
    * NATs require connection state on a *per-association* (or *per-connection*) basis and must operate across multiple protocol layers, unlike conventional routers. Modifying an address at the IP layer also requires modifying checksums at the transport layer (see [Chapters 10](ch10.md) and [Chatper 13](ch13.md) regarding the pseudoheader checksum)
* Some applications protocols, especially those that send IP addressing information inside the application-layer payload, such as [File Transfer Protocol](https://en.wikipedia.org/wiki/File_Transfer_Protocol) (FTP) and [Session Initiation Protocol](https://en.wikipedia.org/wiki/Session_Initiation_Protocol) (SIP), require a special application-layer gateway function that rewrites the application content in order to work unmodified with NAT or other NAT traversal methods that allow the applications to determine how to work with the specific NAT they are using.

Despite its shortcomings, NATs are very widely used, and most network routers support it; NAT supports the basic protocols (e.g., e-mail, Web browsing) that are needed by millions of client systems accessing the Internet every day.

A NAT works by rewriting the identifying information in packets transiting through a router. Most commonly NAT involves rewriting the source IP address of packets as they are forwarded in one direction and the destination IP addresses of packets traveling in the reverse direction. This allows the source IP address in outgoing packets to become one of the NAT router’s Internet-facing interfaces instead of the originating host’s. Thus, <u>to a host on the Internet, packets coming from any of the hosts on the privately addressed side of the NAT appear to be coming from a globally routable IP address of the NAT router.</u>

Most NATs perform both *translation* and *packet filtering*, and the packet-filtering criteria depend on the dynamics of the NAT state. The choice of packet-filtering policy may have a different granularity. For example, the treatment of unsolicited packets (those not associated with packets originating from behind the NAT) received by the NAT may depend on source and destination IP address and/or source and destination port number. [p305]

#### Traditional NAT: Basic NAT and NAPT
