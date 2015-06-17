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
