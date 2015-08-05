### **Chapter 4. Elementary TCP Sockets**

### Introduction

This chapter describes the elementary socket functions required to write a complete TCP client and server, along with concurrent servers, a common Unix technique for providing concurrency when numerous clients are connected to the same server at the same time. Each client connection causes the server to fork a new process just for that client. In this chapter, we consider only the one-process-per-client model using `fork`.

The figure below shows a timeline of the typical scenario that takes place between a TCP client and server. First, the server is started, then sometime later, a client is started that connects to the server. We assume that the client sends a request to the server, the server processes the request, and the server sends a reply back to the client. This continues until the client closes its end of the connection, which sends an end-of-file notification to the server. The server then closes its end of the connection and either terminates or waits for a new client connection.

[![Figure 4.1. Socket functions for elementary TCP client/server.](figure_4.1.png)](figure_4.1.png "Figure 4.1. Socket functions for elementary TCP client/server.")

### `socket` Function

To perform network I/O, the first thing a process must do is call the `socket` function, specifying the type of communication protocol desired (TCP using IPv4, UDP using IPv6, Unix domain stream protocol, etc.).

```c
#include <sys/socket.h>

int socket (int family, int type, int protocol);

/* Returns: non-negative descriptor if OK, -1 on error */
```

Arguments:

* *family* specifies the protocol family and is one of the constants in the table below. This argument is often referred to as *domain* instead of *family*.

    *family* | Description
    -------- | -----------
    `AF_INET` | IPv4 protocols
    `AF_INET6` | IPv6 protocols
    `AF_LOCAL` | Unix domain protocols ([Chapter 15](ch15.md))
    `AF_ROUTE` | Routing sockets ([Chapter 18](ch18.md))
    `AF_KEY` | Key socket ([Chapter 19](ch19.md))

* The socket *type* is one of the constants shown in table below:

    *type* | Description
    ------ | -----------
    `SOCK_STREAM` | stream socket
    `SOCK_DGRAM` | datagram socket
    `SOCK_SEQPACKET` | sequenced packet socket
    `SOCK_RAW` | raw socket

* The *protocol* argument to the `socket` function should be set to the specific protocol type found in the table below, or 0 to select the system's default for the given combination of *family* and *type*.

    *protocol* | Description
    ---------- | -----------
    `IPPROTO_TCP` | TCP transport protocol
    `IPPROTO_UDP` | UDP transport protocol
    `IPPROTO_SCTP` | SCTP transport protocol

Not all combinations of socket *family* and *type* are valid. The table below shows the valid combinations, along with the actual protocols that are valid for each pair. The boxes marked "Yes" are valid but do not have handy acronyms. The blank boxes are not supported.

| | | | | |
|-|-|-|-|-|-
| | `AF_INET` | `AF_INET6` | `AF_LOCAL` | `AF_ROUTE` | `AF_KEY`
|`SOCK_STREAM` | TCP/SCTP | TCP/SCTP | Yes | |
|`SOCK_DGRAM` | UDP | UDP | Yes | |
|`SOCK_SEQPACKET` | SCTP | SCTP | Yes | |
|`SOCK_RAW` | IPv4 | IPv6 | | Yes | Yes

Notes:

* You may also encounter the corresponding `PF_`*xxx* constant as the first argument to socket. This is discussed in the next section in this Chapter.
* You may encounter `AF_UNIX` (the historical Unix name) instead of `AF_LOCAL` (the POSIX name). This is discussed in [Chapter 15](ch15.md).
* Linux supports a new socket type, `SOCK_PACKET`, that provides access to the datalink, similar to BPF and DLPI ([Section 2.2](ch2.md#the-big-picture)). This is discussed in [Chapter 29](ch29.md)
* The key socket, `AF_KEY`, is newer than the others. It provides support for cryptographic security. Similar to the way that a routing socket (`AF_ROUTE`) is an interface to the kernel's routing table, the key socket is an interface into the kernel's key table. This is discussed in [Chapter 19](ch19.md).

On success, the socket function returns a small non-negative integer value, similar to a file descriptor. We call this a **socket descriptor**, or a *sockfd*. To obtain this socket descriptor, all we have specified is a protocol family (IPv4, IPv6, or Unix) and the socket type (stream, datagram, or raw). We have not yet specified either the local protocol address or the foreign protocol address.

#### `AF_`*xxx* Versus `PF_`*xxx*

The "`AF_`" prefix stands for "address family" and the "`PF_`" prefix stands for "protocol family." Historically, the intent was that a single protocol family might support multiple address families and that the `PF_` value was used to create the socket and the `AF_` value was used in socket address structures. But in actuality, a protocol family supporting multiple address families has never been supported and the `<sys/socket.h>` header defines the `PF_` value for a given protocol to be equal to the `AF_` value for that protocol. While there is no guarantee that this equality between the two will always be true, should anyone change this for existing protocols, lots of existing code would break.

To conform to existing coding practice, we use only the `AF_` constants in this text, although you may encounter the `PF_` value, mainly in calls to `socket`.

[p98-99]

### `connect` Function

The `connect` function is used by a TCP client to establish a connection with a TCP server.

```c
#include <sys/socket.h>

int connect(int sockfd, const struct sockaddr *servaddr, socklen_t addrlen);

/* Returns: 0 if OK, -1 on error */
```

* *sockfd* is a socket descriptor returned by the `socket` function.
* The *servaddr* and *addrlen* arguments are a pointer to a socket address structure (which contains the IP address and port number of the server) and its size. ([Section 3.3](ch3.md#value-result-arguments))

<u>The client does not have to call `bind` before calling `connect`: the kernel will choose both an ephemeral port and the source IP address if necessary.</u>

In the case of a TCP socket, the connect function initiates TCP's three-way handshake ([Section 2.6](ch2.md#tcp-connection-establishment-and-termination)). The function returns only when the connection is established or an error occurs. There are several different error returns possible:

1. If the client TCP receives no response to its SYN segment, `ETIMEDOUT` is returned.
    * For example, in 4.4BSD, the client sends one SYN when `connect` is called, sends another SYN 6 seconds later, and sends another SYN 24 seconds later. If no response is received after a total of 75 seconds, the error is returned.
    * Some systems provide administrative control over this timeout.
2. If the server's response to the client's SYN is a reset (RST), this indicates that no process is waiting for connections on the server host at the port specified (the server process is probably not running). This is a **hard error** and the error `ECONNREFUSED` is returned to the client as soon as the RST is received. An RST is a type of TCP segment that is sent by TCP when something is wrong. Three conditions that generate an RST are:
    * When a SYN arrives for a port that has no listening server.
    * When TCP wants to abort an existing connection.
    * When TCP receives a segment for a connection that does not exist.
3. If the client's SYN elicits an ICMP "destination unreachable" from some intermediate router, this is considered a **soft error**. The client kernel saves the message but keeps sending SYNs with the same time between each SYN as in the first scenario. If no response is received after some fixed amount of time (75 seconds for 4.4BSD), the saved ICMP error is returned to the process as either `EHOSTUNREACH` or `ENETUNREACH`. It is also possible that the remote system is not reachable by any route in the local system's forwarding table, or that the connect call returns without waiting at all. Note that Network unreachables are considered obsolete, and applications should just treat `ENETUNREACH` and `EHOSTUNREACH` as the same error.

#### Example: nonexistent host on the local subnet *

We run the client `daytimetcpcli` ([Figure 1.5](ch1.md#a-simple-daytime-client)) and specify an IP address that is on the local subnet (192.168.1/24) but the host ID (100) is nonexistent. When the client host sends out ARP requests (asking for that host to respond with its hardware address), it will never receive an ARP reply.

```shell-session
solaris % daytimetcpcli 192.168.1.100
connect error: Connection timed out
```

We only get the error after the connect times out. Notice that our `err_sys` function prints the human-readable string associated with the `ETIMEDOUT` error.

#### Example: no server process running *

We specify a host (a local router) that is not running a daytime server:

```shell-session
solaris % daytimetcpcli 192.168.1.5
connect error: Connection refused
```

The server responds immediately with an RST.

#### Example: destination not reachable on the Internet *

Our final example specifies an IP address that is not reachable on the Internet. If we watch the packets with `tcpdump`, we see that a router six hops away returns an ICMP host unreachable error.

```shell-session
solaris % daytimetcpcli 192.3.4.5
connect error: No route to host
```

As with the `ETIMEDOUT` error, `connect` returns the `EHOSTUNREACH` error only after waiting its specified amount of time.


In terms of the TCP state transition diagram ([Figure 2.4](figure_2.4.png)):

* `connect` moves from the CLOSED state (the state in which a socket begins when it is created by the `socket` function) to the SYN_SENT state, and then, on success, to the ESTABLISHED state.
* If `connect` fails, the socket is no longer usable and must be closed. We cannot call `connect` again on the socket.

In [Figure 11.10](ch4.md#tcp_connect-function), we will see that when we call `connect` in a loop, trying each IP address for a given host until one works, each time `connect` fails, we must close the socket descriptor and call `socket` again.
