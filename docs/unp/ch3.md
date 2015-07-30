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

[In Chapter 1 in our unp.h header](ch1.md#a-simple-daytime-client), we define `SA` to be the string `struct sockaddr`, just to shorten the code that we must write to cast these pointers.

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

1. From the **process to the kernel**
2. From the **kernel to the process**

#### From process to kernel

`bind`, `connect`, and `sendto` functions pass a socket address structure from the process to the kernel.

Arumgents to these functions:

* The pointer to the socket address structure
* The integer size of the structure

```c
struct sockaddr_in serv;

/* fill in serv{} */
connect (sockfd, (SA *) &serv, sizeof(serv));
```

[![Figure 3.7 Socket address structure passed from process to kernel.](figure_3.7.png)](figure_3.7.png "Figure 3.7 Socket address structure passed from process to kernel.")

The datatype for the size of a socket address structure is actually `socklen_t` and not `int`, but the POSIX specification recommends that `socklen_t` be defined as `uint32_t`.


#### From kernel to process

`accept`, `recvfrom`, `getsockname`, and `getpeername` functions pass a socket address structure from the kernel to the process.

Arguments to these functions:

* The pointer to the socket address structure
* The pointer to an integer containing the size of the structure.

```c
struct sockaddr_un  cli;   /* Unix domain */
socklen_t  len;

len = sizeof(cli);         /* len is a value */
getpeername(unixfd, (SA *) &cli, &len);
/* len may have changed */
```

[![Figure 3.8 Socket address structure passed from kernel to process.](figure_3.8.png)](figure_3.8.png "Figure 3.8 Socket address structure passed from kernel to process.")

**Value-result argument** (Figure 3.8): the size changes from an integer to be a pointer to an integer because the size is both <u>a value when the function is called and a result when the function returns.</u>

* As a **value**: it tells the kernel the size of the structure so that the kernel does not write past the end of the structure when filling it in
* As a **result**: it tells the process how much information the kernel actually stored in the structure

For two other functions that pass socket address structures, `recvmsg` and `sendmsg`, the length field is not a function argument but a structure member.

If the socket address structure is fixed-length, the value returned by the kernel will always be that fixed size: 16 for an IPv4 `sockaddr_in` and 28 for an IPv6 `sockaddr_in6`. But with a variable-length socket address structure (e.g., a Unix domain `sockaddr_un`), the value returned can be less than the maximum size of the structure.

Though the most common example of a value-result argument is the length of a returned socket address structure, we will encounter other value-result arguments in this text:

* The middle three arguments for the `select` function (Section 6.3)
* The length argument for the `getsockopt` function (Section 7.2)
* The `msg_namelen` and `msg_controllen` members of the `msghdr` structure, when used with `recvmsg` (Section 14.5)
* The `ifc_len` member of the `ifconf` structure (Figure 17.2)
* The first of the two length arguments for the `sysctl` function (Section 18.4)

### Byte Ordering Functions

For a 16-bit integer that is made up of 2 bytes, there are two ways to store the two bytes in memory:

* **Little-endian** order: low-order byte is at the starting address.
* **Big-endian** order: high-order byte is at the starting address.

[![Figure 3.9 Little-endian byte order and big-endian byte order for a 16-bit integer.](figure_3.9_600.png)](figure_3.9.png "Figure 3.9 Little-endian byte order and big-endian byte order for a 16-bit integer.")

The figure shows the most significant bit (MSB) as the leftmost bit of the 16-bit value and the least significant bit (LSB) as the rightmost bit.

The terms "little-endian" and "big-endian" indicate which end of the multibyte value, the little end or the big end, is stored at the starting address of the value.

**Host byte order** refer to the byte ordering used by a given system. The program below prints the host byte order:

<small>[byteorder.c](https://github.com/shichao-an/unpv13e/blob/master/intro/byteorder.c)</small>

<script src="https://gist.github.com/shichao-an/ee430bf440011d96f76a.js"></script>

We store the two-byte value `0x0102` in the short integer and then look at the two consecutive bytes, `c[0]` (the address *A*) and `c[1]` (the address *A+1*) to determine the byte order.

The string `CPU_VENDOR_OS` is determined by the GNU `autoconf` program.

```text
freebsd4 % byteorder
i386-unknown-freebsd4.8: little-endian

macosx % byteorder
powerpc-apple-darwin6.6: big-endian

freebsd5 % byteorder
sparc64-unknown-freebsd5.1: big-endian

aix % byteorder
powerpc-ibm-aix5.1.0.0: big-endian

hpux % byteorder
hppa1.1-hp-hpux11.11: big-endian

linux % byteorder
i586-pc-linux-gnu: little-endian

solaris % byteorder
sparc-sun-solaris2.9: big-endian
```

Networking protocols must specify a **network byte order**. The sending protocol stack and the receiving protocol stack must agree on the order in which the bytes of these multibyte fields will be transmitted. <u>The Internet protocols use big-endian byte ordering for these multibyte integers.</u>

But, both history and the POSIX specification say that certain fields in the socket address structures must be maintained in network byte order. We use the following four functions to convert between these two byte orders:

<small>[unp_htons.h](https://gist.github.com/shichao-an/27bb5bebddf78e36198e)</small>

```c
#include <netinet/in.h>

uint16_t htons(uint16_t host16bitvalue);
uint32_t htonl(uint32_t host32bitvalue);

/* Both return: value in network byte order */

uint16_t ntohs(uint16_t net16bitvalue);
uint32_t ntohl(uint32_t net32bitvalue);

/* Both return: value in host byte order */
```

* `h` stands for *host*
* `n` stands for *network*
* `s` stands for *short* (16-bit value, e.g. TCP or UDP port number)
* `l` stands for *long* (32-bit value, e.g. IPv4 address)

When using these functions, we do not care about the actual values (big-endian or little-endian) for the host byte order and the network byte order. What we must do is call the appropriate function to convert a given value between the host and network byte order. On those systems that have the same byte ordering as the Internet protocols (big-endian), these four functions are usually defined as null macros.

We use the term "byte" to mean an 8-bit quantity since almost all current computer systems use 8-bit bytes. Most Internet standards use the term **octet** instead of byte to mean an 8-bit quantity.

Bit ordering is an important convention in Internet standards, such as the the first 32 bits of the IPv4 header from RFC 791:

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL |Type of Service|           Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

This represents four bytes in the order in which they appear on the wire; the leftmost bit is the most significant. However, the numbering starts with zero assigned to the most significant bit.


### Byte Manipulation Functions

Two types functions differ in whether they deal with null-terminated C strings:

* The functions that operate on multibyte fields, without interpreting the data, and without assuming that the data is a null-terminated C string. These types of functions deal with socket address structures to manipulate fields such as IP addresses, which can contain bytes of 0, but are not C character strings.
    * The functions whose names begin with `b` (for byte) (from 4.2BSD)
    * The functions whose names begin with `mem` (for memory) (from ANSI C)
* The functions that deal with null-terminated C character strings (beginning with `str` (for string), defined by including the `<string.h>` header)



<small>[unp_bzero.h](https://gist.github.com/shichao-an/4871b3026c68dc6c4140)</small>

```c
#include <strings.h>

void bzero(void *dest, size_t nbytes);
void bcopy(const void *src, void *dest, size_t nbytes);
int bcmp(const void *ptr1, const void *ptr2, size_t nbytes);

/* Returns: 0 if equal, nonzero if unequal */
```

The memory pointed to by the `const` pointer is read but not modified by the function.

* `bzero` sets the specified number of bytes to 0 in the destination. We often use this function to initialize a socket address structure to 0.
* `bcopy` moves the specified number of bytes from the source to the destination.
* `bcmp` compares two arbitrary byte strings. The return value is zero if the two byte strings are identical; otherwise, it is nonzero

<small>[unp_memset.h](https://gist.github.com/shichao-an/c229d6cc4ac8d310567b)</small>

```c
#include <string.h>

void *memset(void *dest, int c, size_t len);
void *memcpy(void *dest, const void *src, size_t nbytes);
int memcmp(const void *ptr1, const void *ptr2, size_t nbytes);

/* Returns: 0 if equal, <0 or >0 if unequal (see text) */
```

* `memset` sets the specified number of bytes to the value `c` in the destination
* `memcpy` is similar to `bcopy`, but the order of the two pointer arguments is swapped
* `memcmp` compares two arbitrary byte strings

Note:

* One way to remember the order of the two pointers for `memcpy` is to remember that they are written in the same left-to-right order as an assignment statement in C:

        dest = src;

* One way to remember the order of the final two arguments to `memset` is to realize that all of the ANSI C `memXXX` functions require a length argument, and it is always the final argument. The comparison is done assuming the two unequal bytes are `unsigned chars`.

### `inet_aton`, `inet_addr`, and `inet_ntoa` Functions

These functions convert Internet addresses between ASCII strings (what humans prefer to use) and network byte ordered binary values (values that are stored in socket address structures).

<small>[unp_inet_aton.h](https://gist.github.com/shichao-an/af1102b95566ee43cde7)</small>

```c
#include <arpa/inet.h>

int inet_aton(const char *strptr, struct in_addr *addrptr);
/* Returns: 1 if string was valid, 0 on error */

in_addr_t inet_addr(const char *strptr);
/* Returns: 32-bit binary network byte ordered IPv4 address; INADDR_NONE if error */

char *inet_ntoa(struct in_addr inaddr);
/* Returns: pointer to dotted-decimal string */
```

* `inet_aton`: converts the C character string pointed to by *strptr* into its 32-bit binary network byte ordered value, which is stored through the pointer *addrptr*
* `inet_addr`: does the same conversion, returning the 32-bit binary network byte ordered value as the return value. It is deprecated and any new code should use `inet_aton` instead
* `inet_ntoa`: converts a 32-bit binary network byte ordered IPv4 address into its corresponding dotted-decimal string.
    * <u>The string pointed to by the return value of the function resides in static memory.</u> This means the function is not reentrant, which we will discuss in Section 11.18.
    * This function takes a structure as its argument, not a pointer to a structure. (Functions that take actual structures as arguments are rare. It is more common to pass a pointer to the structure.)

### `inet_pton` and `inet_ntop` Functions

These two functions are new with IPv6 and work with both IPv4 and IPv6 addresses. We use these two functions throughout the text. The letters "p" and "n" stand for *presentation* and *numeric*. The presentation format for an address is often an ASCII string and the numeric format is the binary value that goes into a socket address structure.

<small>[unp_inet_pton.h](https://gist.github.com/shichao-an/a4f313716c78362d0b49)</small>

```c
#include <arpa/inet.h>

int inet_pton(int family, const char *strptr, void *addrptr);
/* Returns: 1 if OK, 0 if input not a valid presentation format, -1 on error */

const char *inet_ntop(int family, const void *addrptr, char *strptr, size_t len);
/* Returns: pointer to result if OK, NULL on error */
```

Arguments:

* *family*: is either `AF_INET` or `AF_INET6`. If *family* is not supported, both functions return an error with `errno` set to `EAFNOSUPPORT`.

Functions:

* `inet_pton`: converts the string pointed to by *strptr*, storing the binary result through the pointer *addrptr*. If successful, the return value is 1. If the input string is not a valid presentation format for the specified *family*, 0 is returned.
* `inet_ntop` does the reverse conversion, from numeric (*addrptr*) to presentation (*strptr*).
    * *len* argument is the size of the destination. To help specify this size, the following two definitions are defined by including the `<netinet/in.h>` header.
    * If *len* is too small to hold the resulting presentation format, including the terminating null, a null pointer is returned and `errno` is set to `ENOSPC`.
    * The *strptr* argument to `inet_ntop` cannot be a null pointer. The caller must allocate memory for the destination and specify its size. On success, this pointer is the return value of the function.

Size definitions in `<netinet/in.h>` header for the *len* argument:

```c
#define INET_ADDRSTRLEN       16       /* for IPv4 dotted-decimal */
#define INET6_ADDRSTRLEN      46       /* for IPv6 hex string */
```

The following figure summarizes the five functions on address conversion functions:

[![Figure 3.11 Summary of address conversion functions.](figure_3.11_600.png)](figure_3.11.png "Figure 3.11 Summary of address conversion functions.")

Even if your system does not yet include support for IPv6, you can start using these newer functions by replacing calls of the form.

#### Replacing `inet_addr` to `inet_pton`

Replace:

```c
foo.sin_addr.s_addr = inet_addr(cp);
```

with

```c
inet_pton(AF_INET, cp, &foo.sin_addr);
```

#### Replacing `inet_ntoa` to `inet_ntop`

Replace:

```
ptr = inet_ntoa(foo.sin_addr);
```

with

```c
char str[INET_ADDRSTRLEN];
ptr = inet_ntop(AF_INET, &foo.sin_addr, str, sizeof(str));
```

#### Simple definitions of `inet_pton` and `inet_ntop` that support IPv4

<small>[libfree/inet_pton_ipv4.c](https://github.com/shichao-an/unpv13e/blob/master/libfree/inet_pton_ipv4.c)</small>

```c
int
inet_pton(int family, const char *strptr, void *addrptr)
{
    if (family == AF_INET) {
    	struct in_addr  in_val;

        if (inet_aton(strptr, &in_val)) {
            memcpy(addrptr, &in_val, sizeof(struct in_addr));
            return (1);
        }
		return(0);
    }
	errno = EAFNOSUPPORT;
    return (-1);
}
```

<small>[inet_ntop_ipv4.c](https://github.com/shichao-an/unpv13e/blob/master/libfree/inet_ntop_ipv4.c)</small>

```c
const char *
inet_ntop(int family, const void *addrptr, char *strptr, size_t len)
{
	const u_char *p = (const u_char *) addrptr;

	if (family == AF_INET) {
		char	temp[INET_ADDRSTRLEN];

		snprintf(temp, sizeof(temp), "%d.%d.%d.%d",
				 p[0], p[1], p[2], p[3]);
		if (strlen(temp) >= len) {
			errno = ENOSPC;
			return (NULL);
		}
		strcpy(strptr, temp);
		return (strptr);
	}
	errno = EAFNOSUPPORT;
	return (NULL);
}
```

### `sock_ntop` and Related Functions

A basic problem with `inet_ntop` is that it requires the caller to pass a pointer to a binary address. This address is normally contained in a socket address structure, requiring the caller to know the format of the structure and the address family.

For IPv4:

```c
struct sockaddr_in   addr;
inet_ntop(AF_INET, &addr.sin_addr, str, sizeof(str));
```

For IPv6:

```c
struct sockaddr_in6   addr6;
inet_ntop(AF_INET6, &addr6.sin6_addr, str, sizeof(str));
```

This (above) makes our code protocol-dependent.

To solve this, we will write our own function named `sock_ntop` that takes a pointer to a socket address structure, looks inside the structure, and calls the appropriate function to return the presentation format of the address.

<small>[unp_sock_ntop.h](https://gist.github.com/shichao-an/b0f21ce69e2b8024022e)</small>

```c
#include "unp.h"

char *sock_ntop(const struct sockaddr *sockaddr, socklen_t addrlen);

/* Returns: non-null pointer if OK, NULL on error */
```

*sockaddr* points to a socket address structure whose length is *addrlen*. The function uses its own static buffer to hold the result and a pointer to this buffer is the return value. Notice that <u>using static storage for the result prevents the function from being **re-entrant** or **thread-safe**.</u>

#### Presentation format of `sock_ntop`

* IPv4: dotted-decimal form, followed by a terminator (colon), followed by the decimal port number, followed by a null character
    * The buffer size must be at least `INET_ADDRSTRLEN` plus 6 bytes for IPv4 (16 + 6 = 22)
* IPv6: hex string form of an IPv6 address surrounded by brackets, followed by a terminator (colon), followed by the decimal port number, followed by a
null character. Hence, the buffer size must be at least INET_ADDRSTRLEN plus 6 bytes
    * The buffer size must be at least `INET6_ADDRSTRLEN` plus 8 bytes for IPv6 (46 + 8 = 54)

#### `sock_ntop` definition

* [lib/sock_ntop.c](https://github.com/shichao-an/unpv13e/blob/master/lib/sock_ntop.c)

The source code for only the `AF_INET` case:

```c
char *
sock_ntop(const struct sockaddr *sa, socklen_t salen)
{
    char		portstr[8];
    static char str[128];		/* Unix domain is largest */

	switch (sa->sa_family) {
	case AF_INET: {
		struct sockaddr_in	*sin = (struct sockaddr_in *) sa;

		if (inet_ntop(AF_INET, &sin->sin_addr, str, sizeof(str)) == NULL)
			return(NULL);
		if (ntohs(sin->sin_port) != 0) {
			snprintf(portstr, sizeof(portstr), ":%d", ntohs(sin->sin_port));
			strcat(str, portstr);
		}
		return(str);
	}
  /* ... */
```

#### Related functions
There are a few other functions that we define to operate on socket address structures,
and these will simplify the portability of our code between IPv4 and IPv6.

<small>[apue_sock_bind_wild.h](https://gist.github.com/shichao-an/f63ebf361581af641397)</small>

```c
#include "unp.h"

int sock_bind_wild(int sockfd, int family);
/* Returns: 0 if OK, -1 on error */

int sock_cmp_addr(const struct sockaddr *sockaddr1,
                  const struct sockaddr *sockaddr2, socklen_t addrlen);
/* Returns: 0 if addresses are of the same family and ports are equal,
   else nonzero
*/

int sock_cmp_port(const struct sockaddr *sockaddr1,
                  const struct sockaddr *sockaddr2, socklen_t addrlen);
/* Returns: 0 if addresses are of the same family and ports are equal,
   else nonzero
*/

int sock_get_port(const struct sockaddr *sockaddr, socklen_t addrlen);
/* Returns: non-negative port number for IPv4 or IPv6 address, else -1 */

char *sock_ntop_host(const struct sockaddr *sockaddr, socklen_t addrlen);
/* Returns: non-null pointer if OK, NULL on error */

void sock_set_addr(const struct sockaddr *sockaddr, socklen_t addrlen,
                   void *ptr);
void sock_set_port(const struct sockaddr *sockaddr, socklen_t addrlen,
                   int port);
void sock_set_wild(struct sockaddr *sockaddr, socklen_t addrlen);
```

* `sock_bind_wild`: binds the wildcard address and an ephemeral port to a socket.
* `sock_cmp_addr`: compares the address portion of two socket address structures.
* `sock_cmp_port`: compares the port number of two socket address structures.
* `sock_get_port`: returns just the port number.
* `sock_ntop_host`: converts just the host portion of a socket address structure to presentation format (not the port number)
* `sock_set_addr`: sets just the address portion of a socket address structure to the value pointed to by *ptr*.
* `sock_set_port`: sets just the port number of a socket address structure.
* `sock_set_wild`: sets the address portion of a socket address structure to the wildcard

### `readn`, `writen`, and `readline` Functions

Stream sockets (e.g., TCP sockets) exhibit a behavior with the `read` and `write` functions that differs from normal file I/O. A `read` or `write` on a stream socket might input or output fewer bytes than requested, but this is not an error condition. <u>The reason is that buffer limits might be reached for the socket in the kernel. All that is required to input or output the remaining bytes is for the caller to invoke the `read` or `write` function again.</u> This scenario is always a possibility on a stream socket with `read`, but is normally seen with `write` only if the socket is nonblocking.

<small>[unp_readn.h](https://gist.github.com/shichao-an/26f53ad6de8d2e1a10b2)</small>

```c
#include "unp.h"

ssize_t readn(int filedes, void *buff, size_t nbytes);
ssize_t writen(int filedes, const void *buff, size_t nbytes);
ssize_t readline(int filedes, void *buff, size_t maxlen);

/* All return: number of bytes read or written, –1 on error */
```

* [lib/readn.c](https://github.com/shichao-an/unpv13e/blob/master/lib/readn.c)
* [lib/writen.c](https://github.com/shichao-an/unpv13e/blob/master/lib/writen.c)
* [test/readline1.c](https://github.com/shichao-an/unpv13e/blob/master/test/readline1.c)
* [lib/readline.c](https://github.com/shichao-an/unpv13e/blob/master/lib/readline.c)

```c
#include	"unp.h"

ssize_t						/* Read "n" bytes from a descriptor. */
readn(int fd, void *vptr, size_t n)
{
	size_t	nleft;
	ssize_t	nread;
	char	*ptr;

	ptr = vptr;
	nleft = n;
	while (nleft > 0) {
		if ( (nread = read(fd, ptr, nleft)) < 0) {
			if (errno == EINTR)
				nread = 0;		/* and call read() again */
			else
				return(-1);
		} else if (nread == 0)
			break;				/* EOF */

		nleft -= nread;
		ptr   += nread;
	}
	return(n - nleft);		/* return >= 0 */
}
```

Our three functions look for the error `EINTR` (the system call was interrupted by a caught signal) and continue reading or writing if the error occurs. We handle the error here, instead of forcing the caller to call `readn` or `writen` again, since the purpose of these three functions is to prevent the caller from having to handle a short count.

In Section 14.3, we will mention that the `MSG_WAITALL` flag can be used with the `recv` function to replace the need for a separate `readn` function.

In *test/readline1.c*, our `readline` function calls the system’s `read` function once for every byte of data. This is very inefficient, and why we’ve commented the code to state it is "PAINFULLY SLOW".

Our advice is to think in terms of buffers and not lines. Write your code to read buffers of data, and if a line is expected, check the buffer to see if it contains that line.

*lib/readline.c* shows a faster version of the readline function, which uses its own buffering rather than stdio buffering. Most importantly, the state of readline’s internal buffer is exposed, so callers have visibility into exactly what has been received.

In *lib/readline.c*, the internal function `my_read` reads up to `MAXLINE` characters at a time and then returns them, one at a time. The only change to the `readline` function itself is to call `my_read` instead of `read`. A new function, `readlinebuf`, exposes the internal buffer state so that callers can check and see if more data was received beyond a single line.

Unfortunately, by using `static` variables in `readline.c` to maintain the state information across successive calls, the functions are not **re-entrant** or **thread-safe**.
