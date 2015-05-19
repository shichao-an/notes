# Part I: Networking Fundamentals

## Chapter 1. Introduction to Computer Networking

## Chapter 2. The TCP/IP and OSI Networking Models

### TCP/IP Networking Model

A **networking model** (**networking architecture** or **networking blueprint**), refers to a comprehensive set of documents that define everything that should happen for a computer network to work.

The TCP/IP model both defines and references a large collection of protocols that allow computers to communicate. TCP/IP uses documents called **Requests for Comments** (RFC).

#### Data Encapsulation Terminology

[![Figure 2-11 Five Steps of Data Encapsulation: TCP/IP](figure_2-11.png)](figure_2-11.png "Figure 2-11 Five Steps of Data Encapsulation: TCP/IP")

1. Create and encapsulate the application data with any required application layer headers.
2. Encapsulate the data supplied by the application layer inside a transport layer header. 
3. Encapsulate the data supplied by the transport layer inside an Internet layer (IP) header.
4. Encapsulate the data supplied by the Internet layer inside a data link layer header and trailer. This is the only layer that uses both a **header** and a **trailer**.
5. Transmit the bits.

### OSI Networking Model

[![Figure 2-13 OSI Model Compared to the Two TCP/IP Models](figure_2-13.png)](figure_2-13.png "Figure 2-13 OSI Model Compared to the Two TCP/IP Models")

#### Describing Protocols by Referencing the OSI Layers

Networking documents often describe TCP/IP protocols and standards by referencing OSI layers, both by layer number and layer name. For instance, a common description of a LAN switch is “layer 2 switch,” with “layer 2” referring to OSI layer 2.

Layer Name | Protocols and Specifications | Devices
---------- | ---------------------------- | -------
Application, presentation, session (Layers 5–7) | Telnet, HTTP, FTP, SMTP, POP3, VoIP, SNMP | Firewall, intrusion detection systems, hosts
Transport (Layer 4) | TCP, UDP | Hosts, firewalls
Network (Layer 3) | IP | Router
Data link (Layer 2) | Ethernet (IEEE 802.3), HDLC, Frame Relay, PPP | LAN switch, wireless access point, cable modem, DSL modem
Physical (Layer 1) | RJ-45, EIA/TIA-232, V.35, Ethernet (IEEE 802.3) | LAN hub, LAN repeater, cables

#### OSI Layering Concepts and Benefits

[p41]

* Less complex
* Standard interfaces
* Easier to learn
* Easier to develop
* Multivendor interoperability
* Modular engineering

#### OSI Encapsulation Terminology

[![Figure 2-14 OSI Encapsulation and Protocol Data Units](figure_2-14.png)](figure_2-14.png "Figure 2-14 OSI Encapsulation and Protocol Data Units")

The TCP/IP model uses terms such as **segment**, **packet**, and **frame** to refer to various layers and their respective encapsulated data. OSI uses a more generic term: **protocol data unit** (PDU).


## Chapter 3. Fundamentals of LANs
### An Overview of Modern Ethernet LANs

Types of cabling:

* **Unshielded Twisted-Pair** (UTP)
* **Fiber-optic**

Most IEEE standards define a different variation of Ethernet at the physical layer. 
For the data link layer:

* 802.3 Media Access Control (MAC) sublayer
* 802.2 Logical Link Control (LLC) sublayer

[p52]

Common Name | Speed | Alternative Name | Name of IEEE Standard | Cable Type, Maximum Length
----------- | ----- | ---------------- | --------------------- | --------------------------
Ethernet | 10 Mbps | 10BASE-T | IEEE 802.3 | Copper, 100 m
Fast Ethernet | 100 Mbps | 100BASE-TX | IEEE 802.3u | Copper, 100 m
Gigabit Ethernet | 1000 Mbps | 1000BASE-LX, 1000BASE-SX | IEEE 802.3z | Fiber, 550 m (SX) 5 km (LX)
Gigabit Ethernet | 1000 Mbps | 1000BASE-T | IEEE 802.3ab | 100 m

The term Ethernet is often used to mean "all types of Ethernet", but in some cases it is used to mean "10BASE-T Ethernet"

### A Brief History of Ethernet
* Carrier sense multiple access with collision detection (CSMA/CD) algorithm

#### Repeaters

**Repeaters** extended the length of LANs by cleaning up the electrical signal and repeating it (a Layer 1 function) but without interpreting the meaning of the electrical signal. [p56]

#### Building 10BASE-T Networks with Hubs

**Hubs** are essentially repeaters with multiple physical ports. It simply regenerates the electrical signal that comes in one port and sends the same signal out every other port.

### Ethernet UTP Cabling
#### UTP Cables and RJ-45 Connectors


### Improving Performance by Using Switches Instead of Hubs

CSMA/CD logic helps prevent collisions and also defines how to act when a collision does occur:

1. A device with a frame to send listens until the Ethernet is not busy.
2. When the Ethernet is not busy, the sender(s) begin(s) sending the frame.
3. The sender(s) listen(s) to make sure that no collision occurred.
4. If a collision occurs, the devices that had been sending a frame each send a jamming signal to ensure that all stations recognize the collision.
5. After the jamming is complete, each sender randomizes a timer and waits that long before trying to resend the collided frame. When each random timer expires, the process starts over with Step 1.

#### Increasing Available Bandwidth Using Switches

#### Doubling Performance by Using Full-Duplex Ethernet

#### Ethernet Data-Link Protocols
