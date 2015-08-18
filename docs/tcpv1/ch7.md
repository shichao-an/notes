### **Chapter 7. Firewalls and Network Address Translation (NAT)**

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


The two most common forms of proxy firewalls are **HTTP proxy firewalls** and **SOCKS firewalls**.

### Network Address Translation (NAT)
