### **Chapter 3. Link Layer**

### Introduction

This chapter discusses the details involved in using the Ethernet and Wi-Fi link layers, how the Point-to-Point Protocol (PPP) is used, and how link-layer protocols can be carried inside other (link- or higher-layer) protocols, a technique known as tunneling.

When referring to link-layer protocol data units (PDUs), we usually use the term **frame**, so as to distinguish the PDU format from those at higher layers such as packets or segments, terms used to describe network- and transport-layer PDUs, respectively.

Frame formats usually support a variable-length frame size, the upper bound of which is called the [**maximum transmission unit**](https://en.wikipedia.org/wiki/Maximum_transmission_unit) (MTU). Some network technologies, such as modems and serial lines, do not impose their own maximum frame size, so they can be configured by the user.


### Ethernet and the IEEE 802 LAN/MAN Standards

### Full Duplex, Power Save, Autonegotiation, and 802.1X Flow Control

### Bridges and Switches

### Wireless LANs—IEEE 802.11(Wi-Fi)

### Point-to-Point Protocol (PPP)

### Loopback

In many cases clients want to communicate with servers on the same computer using Internet protocols such as TCP/IP. To enable this, most implementations support a network-layer [**loopback**](https://en.wikipedia.org/wiki/Loopback) capability that typically takes the form of a [virtual loopback network interface](https://en.wikipedia.org/wiki/Localhost). <u>It acts like a real network interface but is really a special piece of software provided by the operating system to enable TCP/IP and other communications on the same host computer.</u>

IPv4 addresses starting with 127 are reserved for this, as is the IPv6 address ::1 ([Chapter 2](ch2.md)). Traditionally, UNIX-like systems including Linux assign the IPv4 address of 127.0.0.1 (::1 for IPv6) to the loopback interface and assign it the name localhost.
