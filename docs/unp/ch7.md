### **Chapter 7. Socket Options**

### Introduction

There are various ways to get and set the options that affect a socket:

* The `getsockopt` and `setsockopt` functions.
* The `fcntl` function, which is the POSIX way to set a socket for nonblocking I/O, signal-driven I/O, and to set the owner of a socket.
* The `ioctl` function.

### `getsockopt` and `setsockopt` Functions

These two functions apply only to sockets:

```c
#include <sys/socket.h>

int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
int setsockopt(int sockfd, int level, int optname, const void *optval socklen_t optlen);

/* Both return: 0 if OK,–1 on error */
```

Arguments:

* *sockfd* must refer to an open socket descriptor.
* *level* specifies the code in the system that interprets the option: the general socket code or some protocol-specific code (e.g., IPv4, IPv6, TCP, or SCTP).
* *optval* is a pointer to a variable from which the new value of the option is fetched by `setsockopt`, or into which the current value of the option is stored by `getsockopt`. The size of this variable is specified by the final argument *optlen*, as a value for `setsockopt` and as a value-result for `getsockopt`.

The following table lists socket and IP-layer socket options for `getsockopt` and `setsockopt`.

[![Figure 7.1. Summary of socket and IP-layer socket options for getsockopt and setsockopt.](figure_7.1.png)](figure_7.1.png "Figure 7.1. Summary of socket and IP-layer socket options for getsockopt and setsockopt.")

The following table lists transport-layer socket options.

[![Figure 7.2. Summary of transport-layer socket options.](figure_7.2.png)](figure_7.2.png "Figure 7.2. Summary of transport-layer socket options.")

There are two basic types of options:

* **Flags**: binary options that enable or disable a certain feature (flags)
* **Values**: options that fetch and return specific values that we can either set or examine.

The column labeled "Flag" specifies a flag option:

* `getsockopt`: `*optval` is an integer. The value returned in `*optval` is zero if the option is disabled, or nonzero if the option is enabled.
* `setsockopt`: it requires a nonzero `*optval` to turn the option on, and a zero value to turn the option off.

If the "Flag" column does not contain a block dot, then the option is used to pass a value of the specified datatype between the user process and the system.

### Checking if an Option Is Supported and Obtaining the Default

[sockopt/checkopts.c](https://github.com/shichao-an/unpv13e/blob/master/sockopt/checkopts.c)

### Socket States

The following socket options are inherited by a connected TCP socket from the listening socket:

* `SO_DEBUG`
* `SO_DONTROUTE`
* `SO_KEEPALIVE`
* `SO_LINGER`
* `SO_OOBINLINE`
* `SO_RCVBUF`
* `SO_RCVLOWAT`
* `SO_SNDBUF`
* `SO_SNDLOWAT`
* `TCP_MAXSEG`
* `TCP_NODELAY`

This is important with TCP because the connected socket is not returned to a server by `accept` until the three-way handshake is completed by the TCP layer. <u>To ensure that one of these socket options is set for the connected socket when the three-way handshake completes, we must set that option for the listening socket.</u>

### Generic Socket Options

Generic socket options are protocol-independent (they are handled by the protocol-independent code within the kernel, not by one particular protocol module such as IPv4), but some of the options apply to only certain types of sockets. For example, even though the `SO_BROADCAST` socket option is called "generic," it applies only to datagram sockets.

### IPv4 Socket Options

#### `SO_BROADCAST` Socket Option

This option enables or disables the ability of the process to send broadcast messages. Broadcasting is supported for only datagram sockets and only on networks that support the concept of a broadcast message (e.g., Ethernet, token ring, etc.). You cannot broadcast on a point-to-point link or any connection-based transport protocol such as SCTP or TCP.

Since an application must set this socket option before sending a broadcast datagram, it prevents a process from sending a broadcast when the application was never designed to broadcast. For example, a UDP application might take the destination IP address as a command-line argument, but the application never intended for a user to type in a broadcast address. Rather than forcing the application to try to determine if a given address is a broadcast address or not, the test is in the kernel: If the destination address is a broadcast address and this socket option is not set, `EACCES` is returned.

#### `SO_DEBUG` Socket Option

This option is supported only by TCP. When enabled for a TCP socket, the kernel keeps track of detailed information about all the packets sent or received by TCP for the socket. These are kept in a [circular buffer](https://en.wikipedia.org/wiki/Circular_buffer) within the kernel that can be examined with the `trpt` program.

#### `SO_DONTROUTE` Socket Option

This option specifies that outgoing packets are to bypass the normal routing mechanisms of the underlying protocol. The destination must be on a directly-connected network, and messages are directed to the appropriate network interface according to the destination address [[Use of Options](http://pubs.opengroup.org/onlinepubs/9699919799/functions/V2_chap02.html#tag_15_10_16)]. For example, with IPv4, the packet is directed to the appropriate local interface, as specified by the network and subnet portions of the destination address. If the local interface cannot be determined from the destination address (e.g., the destination is not on the other end of a point-to-point link, or is not on a shared network), `ENETUNREACH` is returned.

The equivalent of this option can also be applied to individual datagrams using the `MSG_DONTROUTE` flag with the `send`, `sendto`, or `sendmsg` functions.

This option is often used by routing daemons (e.g., `routed` and `gated`) to bypass the routing table and force a packet to be sent out a particular interface.

#### `SO_ERROR` Socket Option

This option is one that can be fetched but cannot be set.

When an error occurs on a socket, the protocol module in a Berkeley-derived kernel sets a variable named `so_error` for that socket to one of the standard Unix `E`xxx values. This is called the *pending error* for the socket. The process can be immediately notified of the error in one of two ways:

1. If the process is blocked in a call to `select` on the socket ([Section 6.3](ch6.md#select-function)), for either readability or writability, `select` returns with either or both conditions set.
2. If the process is using signal-driven I/O, the `SIGIO` signal is generated for either the process or the process group.

The process can then obtain the value of `so_error` by fetching the `SO_ERROR` socket option. The integer value returned by `getsockopt` is the pending error for the socket. The value of `so_error` is then reset to 0 by the kernel.

* If `so_error` is nonzero when the process calls `read` and there is no data to return, `read` returns –1 with `errno` set to the value of `so_error`. The value of `so_error` is then reset to 0. If there is data queued for the socket, that data is returned by `read` instead of the error condition.
* If `so_error` is nonzero when the process calls `write`, –1 is returned with `errno` set to the value of `so_error` and `so_error` is reset to 0.

#### `SO_KEEPALIVE` Socket Option

When the keep-alive option is set for a TCP socket and no data has been exchanged across the socket in either direction for two hours, TCP automatically sends a **keep-alive probe** to the peer. This probe is a TCP segment to which the peer must respond. One of three scenarios results:

1. The peer responds with the expected ACK. The application is not notified (since everything is okay). TCP will send another probe following another two hours of inactivity.
2. The peer responds with an RST, which tells the local TCP that the peer host has crashed and rebooted. The socket's pending error is set to `ECONNRESET` and the socket is closed.
3. There is no response from the peer to the keep-alive probe. Berkeley-derived TCPs send 8 additional probes, 75 seconds apart, trying to elicit a response. TCP will give up if there is no response within 11 minutes and 15 seconds after sending the first probe.

##### **No response and errors** *

* If there is no response at all to TCP's keep-alive probes, the socket's pending error is set to `ETIMEDOUT` and the socket is closed.
* If the socket receives an ICMP error in response to one of the keep-alive probes, the corresponding error ([Figures A.15](figure_a.15.png) and [Figure A.16](figure_a.16.png)) is returned instead, and the socket is still closed.
    * A common ICMP error in this scenario is "host unreachable", where the pending error is set to `EHOSTUNREACH`. This can occur because of either of the following:
        * Network failure.
        * <u>The remote host has crashed and the last-hop router has detected the crash.</u>

##### **Changing the inactivity time** *

A common question regarding this option is about modifying the timing parameters (usually to reduce the two-hour period of inactivity to some shorter value). Appendix E of TCPv1 discusses how to change these timing parameters for various kernels, but be aware that most kernels maintain these parameters on a per-kernel basis, not on a per-socket basis. For example, changing the inactivity period from 2 hours to 15 minutes will affect all sockets on the host that enables this option. However, such questions usually result from a misunderstanding of the purpose of this option, as discussed below.

##### **Misunderstanding of the purpose** *

<u>The purpose of this option is to detect if the peer *host* crashes or becomes unreachable</u> (e.g., dial-up modem connection drops, power fails, etc.). If the *peer* process crashes, its TCP will send a FIN across the connection, which we can easily detect with `select`, which was why we used `select` in [Section 6.4](ch6.md#str_cli-function-revisited). If there is no response to any of the keep-alive probes (scenario 3), we are not guaranteed that the peer host has crashed, and TCP may well terminate a valid connection. It could be that some intermediate router has crashed for 15 minutes, and that period of time just happens to completely overlap our host's 11-minute and 15-second keep-alive probe period. In fact, this function might more properly be called "make-dead" rather than "keep-alive" since it can terminate live connections.


#### `SO_LINGER` Socket Option

### ICMPv6 Socket Option

### IPv6 Socket Options

### TCP Socket Options


### Doubts and Solutions

#### Verbatim

Section 7.5 on `SO_KEEPALIVE` Socket Option.

> Appendix E of TCPv1 discusses how to change these timing parameters for various kernels, ...

I did not find Appendix E (actually no appendix at all) in TCPv1 (3rd Edition).
