### **Chapter 8. ICMPv4 and ICMPv6: Internet Control Message Protocol**

### Introduction

The IP protocol alone provides no direct way to do the following:

* For an end system to learn the fate of IP packets that fail to make it to their destinations.
* For obtaining diagnostic information (e.g., which routers are used along a path or a method to estimate the round-trip time).

To address these deficiencies, a special protocol called the [**Internet Control Message Protocol**](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol) (ICMP) is used in conjunction with IP to provide diagnostics and control information related to the configuration of the IP protocol layer and the disposition of IP packets.
