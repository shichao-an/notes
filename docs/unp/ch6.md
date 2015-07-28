### **Chapter 6. I/O Multiplexing: The `select` and `poll` Functions**

### Introduction

When the TCP client is handling two inputs at the same time: standard input and a TCP socket, we encountered a problem when the client was blocked in a call to `fgets` (on standard input) and the server process was killed. The server TCP correctly sent a FIN to the client TCP, but since the client process was blocked reading from standard input, it never saw the EOF until it read from the socket (possibly much later).

We want to be notified if one or more I/O conditions are ready (i.e., input is ready to be read, or the descriptor is capable of taking more output). This capability is called **I/O multiplexing** and is provided by the `select` and `poll` functions, as well as a newer POSIX variation of the former, called `pselect`..

I/O multiplexing is typically used in networking applications in the following scenarios:

* When a client is handling multiple descriptors (normally interactive input and a network socket)
* When a client to handle multiple sockets at the same time (this is possible, but rare)
* If a TCP server handles both a listening socket and its connected sockets
* If a server handles both TCP and UDP
* If a server handles multiple services and perhaps multiple protocols

I/O multiplexing is not limited to network programming. Many nontrivial applications find a need for these techniques.
