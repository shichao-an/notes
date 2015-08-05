### **Chapter 2. The Internet Address Architecture**

### Introduction

This chapter deals with the structure of network-layer addresses used in the Internet, the IP addresses. [p31-32]

* Every device connected to the Internet has at least one IP address.
* When devices are attached to the global Internet, they are assigned addresses that must be coordinated so as to not duplicate other addresses in use on the network.

### Expressing IP Addresses

In IPv4, the dotted-quad notation for IPv4 addresses consists of four decimal numbers separated by periods. For example, 165.195.130.107. Each such number is a nonnegative integer in the range [0, 255] and represents one-quarter of the entire IP address. It is simply a way of writing the whole IPv4 address ( a 32-bit nonnegative integer used throughout the Internet system) using convenient decimal numbers. [p32]

In IPv6, addresses are 128 bits in length, four times larger than IPv4 addresses. The conventional notation for IPv6 addresses is a series of four hexadecimal ("hex" or base-16) numbers called *blocks* or *fields* separated by colons. For example, an IPv6 address containing eight blocks would be written as 5f05:2000:80ad:5800:0058:0800:2023:1d71. In addition, a number of agreed-upon simplifications have been standardized for expressing IPv6 addresses:

1. Leading zeros of a block need not be written. In the preceding example, the address could have been written as 5f05:2000:80ad:5800:58:800:2023:1d71.
2. Blocks of all zeros can be omitted and replaced by the notation ::.
    * For example, the IPv6 address 0:0:0:0:0:0:0:1 can be written more compactly as ::1.
    * Similarly, the address 2001:0db8:0:0:0:0:0:2 can be written more compactly as 2001:db8::2.
    * To avoid ambiguities, the :: notation may be used only once in an IPv6 address
3. **IPv4-mapped IPv6 address**. The block immediately preceding the IPv4 portion of the address has the value ffff and the remaining part of the address is formatted using dotted-quad. For example, the IPv6 address ::ffff:10.0.0.1 represents the IPv4 address 10.0.0.1. This is called an **IPv4-mapped IPv6 address**.
4. **IPv4-compatible IPv6 address**. The low-order 32 bits of the IPv6 address can be written using dotted-quad notation. The IPv6 address ::0102:f001 is therefore equivalent to the address ::1.2.240.1.

The colon delimiter in an IPv6 address may be confused with another separator such as the colon used between an IP address and a port number. In such circumstances, bracket characters, [ and ], are used to surround the IPv6 address. The following URL is an example:

```text
http://[2001:0db8:85a3:08d3:1319:8a2e:0370:7344]:443/
```

The flexibility provided by [RFC4291] resulted in unnecessary confusion due to the ability to represent the same IPv6 address in multiple ways. To remedy this situation, [RFC5952] imposes some rules to narrow the range of options while remaining compatible with [RFC4291]. They are as follows:

1. Leading zeros must be suppressed (e.g., 2001:0db8::0022 becomes 2001:db8::22).
2. The :: construct must be used to its maximum possible effect (most zeros suppressed) but not for only 16-bit blocks. If multiple blocks contain equallength runs of zeros, the first is replaced with ::.
3. The hexadecimal digits a through f should be represented in lowercase.

### Basic IP Address Structure

IPv4 has 2<sup>32</sup> possible addresses and IPv6 has 2<sup>128</sup>.

* Most of the IPv4 address space is **unicast** address space, which is IPv4 addresses chunks subdivided down to a single address and used to identify a single network interface of a computer attached to the Internet or to some private intranet.
* Most of the IPv6 address space is not currently being used.

#### Classful Addressing
