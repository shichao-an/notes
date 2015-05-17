## Introduction

### Introduction

The **client** and **server** organization is used by most network-awared applications. Some complex applications also require **asynchronous callback** communication, where the server initiates a message to the client.

### A Simple Daytime Client

* [daytimetcpcli.c](https://github.com/shichao-an/unpv13e/blob/master/intro/daytimetcpcli.c)

<script src="https://gist.github.com/shichao-an/d4b1bae51c0a10a29fe3.js"></script>

#### Create TCP socket

The `socket` function creates an Internet (`AF_INET`) stream (`SOCK_STREAM`) socket, which is a fancy name for a TCP socket. The function returns a small integer descriptor to identify the socket.

#### Specify server's IP address and port

The IP address (`sin_addr`) and port number (`sin_port`) fields in the Internet socket address structure (`sockaddr_in`) must be in specific formats:

* `htons` (host to network short): converts the binary port number
* `inet_pton` (presentation to numeric): convert the ASCII command-line argument (such as `206.62.226.35` when we ran this example) into the proper format.

`bzero` is not an ANSI C function, but is used in this book instead of the ANSI C `memset` function, because `bzero` is easier to remember (with only two arguments) than `memset` (with three arguments).

#### Establish connection with server

* `connect`

In the `unp.h` header, `SA` is defined to be `struct sockaddr`, a generic socket address structure.


#### Read and display server's reply

We must be careful when using TCP because it is a **byte-stream** protocol with no record boundaries. Since we cannot assume that the server's reply will be returned by a single `read`, we always need to code the `read` in a loop when reading from a TCP socket.


#### Terminate program

`exit` terminates the program. Unix always closes all open descriptors when a process terminates.


### Protocol Independence

The above program is protocol-depdent on IPv4.

It is better to make a program protocol-independent by using the `getaddrinfo` function.

### Error Handling: Wrapper Functions

We can shorten our programs by defining a **wrapper function** that performs the actual function call, tests the return value, and terminates on an error.

```c
sockfd = Socket(AF_INET, SOCK_STREAM, 0);
```

With careful C coding, we could use macros instead of functions, providing a little run-time efficiency, but these wrapper functions are rarely the performance bottleneck of a program. This book uses these wrapper functions unless otherwise explicit error needs handling.

### Unix `errno` Value

The value of `errno` is set by a function only if an error occurs. All of the positive error values are constants with all-uppercase names beginning with "E," and are normally defined in the `<sys/errno.h>` header. No error has a value of 0.

Storing errno in a global variable does not work with multiple threads that share all global variables.

### A Simple Daytime Server

* [daytimetcpsrv.c](https://github.com/shichao-an/unpv13e/blob/master/intro/daytimetcpsrv.c)

<script src="https://gist.github.com/shichao-an/bf927f23914b9c20f04c.js"></script>

#### Create a TCP socket

Identical to the client code.

#### Bind server's well-known port to socket

* `bind`: the server's well-known port (13) is bound to the socket by calling `bind`
* `INADDR_ANY` allows the server to accept a client connection on any interface

#### Convert socket to listening socket

* `listen`: converts the socket into a listening socket, on which incoming connections from clients will be accepted by the kernel
* `listenfd` in the code is called a **listening descriptor**


#### Accept client connection, send reply

* `accept`
* `connfd` in the code is called a **connected descriptor** for communication with the client. A new descriptor is returned by accept for each client that connects to our server.

This book uses this code style for infinite loop:

```c
for ( ; ; ) {
    // . . .
}
```

#### `snprintf` function

* `snprintf` instead of `sprintf`

Similarly:

* `fgets` instead of `gets`
* `strncat` or `strlcat` instead of `strcat`
* `strncpy` or `strlcpy` instead of a `strcpy`

#### Terminate connection

`close` initiates the normal TCP connection termination sequence: a FIN is sent in each direction and each FIN is acknowledged by the other end.

The server implemented in the above server code is:

* Protocol-dependent on IPv4
* Handles only one client at a time. If multiple client connections arrive at about the same time, the kernel queues them, up to some limit, and returns them to `accept` one at a time.
* Called an **iterative server**. A **concurrent server** handles multiple clients at the same time.
