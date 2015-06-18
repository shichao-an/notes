### **Chapter 3. Sockets Introduction**

### Introduction

This chapter begins the description of the sockets API.


### Socket Address Structures

The name of socket address structures begin with `sockaddr_` and end with a unique suffix for each protocol suite.

#### IPv4 Socket Address Structure

An IPv4 socket address structure, commonly called an "Internet socket address structure", is named `sockaddr_in` and is defined by including the `<netinet/in.h>` header.

```c
struct in_addr {
  in_addr_t   s_addr;           /* 32-bit IPv4 address */
                                /* network byte ordered */
};

struct sockaddr_in {
  uint8_t         sin_len;      /* length of structure (16) */
  sa_family_t     sin_family;   /* AF_INET */
  in_port_t       sin_port;     /* 16-bit TCP or UDP port number */
                                /* network byte ordered */
  struct in_addr  sin_addr;     /* 32-bit IPv4 address */
                                /* network byte ordered */
  char            sin_zero[8];  /* unused */
};
```

* `sin_len`: the length field. We need never set it and need never examine it.
    * The four socket functions that pass a socket address structure from the process to the kernel, `bind`, `connect`, `sendto`, and `sendmsg`, all go through the `sockargs` function in a Berkeley-derived implementation. This function copies the socket address structure from the process and explicitly sets its `sin_len` member to the size of the structure that was passed as an argument to these four functions. The five socket functions that pass a socket address structure from the kernel to the process, `accept`, `recvfrom`, `recvmsg`, `getpeername`, and `getsockname`, all set the `sin_len` member before returning to the process.
* POSIX requires only three members in the structure: `sin_family`, `sin_addr`, and `sin_port`. Almost all implementations add the `sin_zero` member so that all socket address structures are at least 16 bytes in size.
*  The `in_addr_t` datatype must be an unsigned integer type of at least 32 bits, `in_port_t` must be an unsigned integer type of at least 16 bits, and `sa_family_t` can be any unsigned integer type. The latter is normally an 8-bit unsigned integer if the implementation supports the length field, or an unsigned 16-bit integer if the length field is not supported.
* Both the IPv4 address and the TCP or UDP port number are always stored in the structure in **network byte order**.
* The `sin_zero` member is unused. By convention, we always set the entire structure to 0 before filling it in.
* Socket address structures are used only on a given host: The structure itself is not communicated between different hosts

#### Generic Socket Address Structure

A socket address structures is always passed by reference when passed as an argument to any socket functions. But any socket function that takes one of these pointers as an argument must deal with socket address structures from any of the supported protocol families.

A generic socket address structure in the `<sys/socket.h>` header:

```c
struct sockaddr {
  uint8_t      sa_len;
  sa_family_t  sa_family;    /* address family: AF_xxx value */
  char         sa_data[14];  /* protocol-specific address */
};
```

The socket functions are then defined as taking a pointer to the generic socket address structure, as shown here in the ANSI C function prototype for the `bind` function:

```c
int bind(int, struct sockaddr *, socklen_t);
```

This requires that any calls to these functions must cast the <u>pointer to the *protocol-specific socket address structure*</u> to be a <u>pointer to a *generic socket address structure*.</u>

For example:

```c
struct sockaddr_in  serv;      /* IPv4 socket address structure */

/* fill in serv{} */

bind(sockfd, (struct sockaddr *) &serv, sizeof(serv));
```

[In Chapter 1 in our unp.h header](/unp/ch1/#a-simple-daytime-client), we define `SA` to be the string `struct sockaddr`, just to shorten the code that we must write to cast these pointers.

* From an application programmer ’s point of view, <u>the only use of these generic socket address structures is to cast pointers to protocol-specific structures.</u>
* From the kernel’s perspective, another reason for using pointers to generic socket address structures as arguments is that the kernel must take the caller’s pointer, cast it to a `struct sockaddr *`, and then look at the value of `sa_family` to determine the type of the structure.

#### IPv6 Socket Address Structure

The IPv6 socket address is defined by including the `<netinet/in.h>` header:

```c
struct in6_addr {
  uint8_t  s6_addr[16];          /* 128-bit IPv6 address */
                                 /* network byte ordered */
};

#define SIN6_LEN      /* required for compile-time tests */

struct sockaddr_in6 {
  uint8_t         sin6_len;      /* length of this struct (28) */
  sa_family_t     sin6_family;   /* AF_INET6 */
  in_port_t       sin6_port;     /* transport layer port# */
                                 /* network byte ordered */
  uint32_t        sin6_flowinfo; /* flow information, undefined */
  struct in6_addr sin6_addr;     /* IPv6 address */
                                 /* network byte ordered */
  uint32_t        sin6_scope_id; /* set of interfaces for a scope */
};
```

* The `SIN6_LEN` constant must be defined if the system supports the length member for socket address structures.
* The IPv6 family is `AF_INET6`, whereas the IPv4 family is `AF_INET`
* The members in this structure are ordered so that if the `sockaddr_in6` structure is 64-bit aligned, so is the 128-bit `sin6_addr` member.
* The `sin6_flowinfo` member is divided into two fields:
    * The low-order 20 bits are the flow label
    * The high-order 12 bits are reserved
* The `sin6_scope_id` identifies the scope zone in which a scoped address is meaningful, most commonly an interface index for a link-local address

#### New Generic Socket Address Structure

A new generic socket address structure was defined as part of the IPv6 sockets API, to overcome some of the shortcomings of the existing `struct sockaddr`. Unlike the `struct sockaddr`, the new `struct sockaddr_storage` is large enough to hold any socket address type supported by the system. The `sockaddr_storage` structure is defined by including the `<netinet/in.h>` header:

```c
struct sockaddr_storage {
  uint8_t      ss_len;       /* length of this struct (implementation dependent) */
  sa_family_t  ss_family;    /* address family: AF_xxx value */
  /* implementation-dependent elements to provide:
   * a) alignment sufficient to fulfill the alignment requirements of
   *    all socket address types that the system supports.
   * b) enough storage to hold any type of socket address that the
   *    system supports.
   */
};
```

The `sockaddr_storage` type provides a generic socket address structure that is different from `struct sockaddr` in two ways:

1. If any socket address structures that the system supports have alignment requirements, the `sockaddr_storage` provides the strictest alignment requirement.
2. The `sockaddr_storage` is large enough to contain any socket address structure that the system supports.

The fields of the `sockaddr_storage` structure are opaque to the user, except for `ss_family` and `ss_len` (if present). The `sockaddr_storage` must be cast or copied to the appropriate socket address structure for the address given in `ss_family` to access any other fields.

#### Comparison of Socket Address Structures

In this figure, we assume that:

* Socket address structures all contain a one-byte length field 
* The family field also occupies one byte
* Any field that must be at least some number of bits is exactly that number of bits

[![Figure 3.6 Comparison of various socket address structures.](figure_3.6_600.png)](figure_3.6.png "Figure 3.6 Comparison of various socket address structures.")

To handle variable-length structures, whenever we pass a pointer to a socket address structure as an argument to one of the socket functions, we pass its length as another argument. 


### Value-Result Arguments

When a socket address structure is passed to any socket function, it is always passed by reference (a pointer to the structure is passed). The length of the structure is also passed as an argument. 

The way in which the length is passed depends on which direction the structure is being passed:

1. From the process to the kernel
2. From the kernel to the process
