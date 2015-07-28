### **Chapter 6. I/O Multiplexing: The `select` and `poll` Functions**

### Introduction

When the TCP client is handling two inputs at the same time: standard input and a TCP socket, we encountered a problem when the client was blocked in a call to `fgets` (on standard input) and the server process was killed. The server TCP correctly sent a FIN to the client TCP, but since the client process was blocked reading from standard input, it never saw the EOF until it read from the socket (possibly much later).

We want to be notified if one or more I/O conditions are ready (i.e., input is ready to be read, or the descriptor is capable of taking more output). This capability is called **I/O multiplexing** and is provided by the `select` and `poll` functions, as well as a newer POSIX variation of the former, called `pselect`.

I/O multiplexing is typically used in networking applications in the following scenarios:

* When a client is handling multiple descriptors (normally interactive input and a network socket)
* When a client to handle multiple sockets at the same time (this is possible, but rare)
* If a TCP server handles both a listening socket and its connected sockets
* If a server handles both TCP and UDP
* If a server handles multiple services and perhaps multiple protocols

I/O multiplexing is not limited to network programming. Many nontrivial applications find a need for these techniques.

### I/O Models

We first examine the basic differences in the five I/O models that are available to us under Unix:

* blocking I/O
* nonblocking I/O
* I/O multiplexing (`select` and `poll`)
* signal driven I/O (`SIGIO`)
* asynchronous I/O (the POSIX `aio_` functions)

There are normally two distinct phases for an input operation:

1. Waiting for the data to be ready. This involves waiting for data to arrive on the network. When the packet arrives, it is copied into a buffer within the kernel.
2. Copying the data from the kernel to the process. This means copying the (ready) data from the kernel's buffer into our application buffer

#### Blocking I/O Model

The most prevalent model for I/O is the blocking I/O model (which we have used for all our examples in the previous sections). By default, all sockets are blocking. The scenario is shown in the figure below:

[![Figure 6.1. Blocking I/O model.](figure_6.1.png)](figure_6.1.png "Figure 6.1. Blocking I/O model.")

We use UDP for this example instead of TCP because with UDP, the concept of data being "ready" to read is simple: either an entire datagram has been received or it has not. With TCP it gets more complicated, as additional variables such as the socket's low-water mark come into play.

We also refer to `recvfrom` as a system call to differentiate between our application and the kernel, regardless of how `recvfrom` is implemented (system call on BSD and function that invokes `getmsg` system call on System V). There is normally a switch from running in the application to running in the kernel, followed at some time later by a return to the application.

In the figure above, the process calls `recvfrom` and the system call does not return until the datagram arrives and is copied into our application buffer, or an error occurs. The most common error is the system call being interrupted by a signal, as we described in [Section 5.9](/unp/ch5/#handling-sigchld-signals). We say that the process is blocked the entire time from when it calls `recvfrom` until it returns. When `recvfrom` returns successfully, our application processes the datagram.

#### Nonblocking I/O Model

When a socket is set to be nonblocking, we are telling the kernel "when an I/O operation that I request cannot be completed without putting the process to sleep, do not put the process to sleep, but return an error instead". The figure is below:

[![Figure 6.2. Nonblocking I/O model.](figure_6.2.png)](figure_6.2.png "Figure 6.2. Nonblocking I/O model.")

* For the first three `recvfrom`, there is no data to return and the kernel immediately returns an error of `EWOULDBLOCK`.
* For the fourth time we call recvfrom, a datagram is ready, it is copied into our application buffer, and `recvfrom` returns successfully. We then process the data.

When an application sits in a loop calling `recvfrom` on a nonblocking descriptor like this, it is called **polling**. The application is continually polling the kernel to see if some operation is ready. This is often a waste of CPU time, but this model is occasionally encountered, normally on systems dedicated to one function.

#### I/O Multiplexing Model

With **I/O multiplexing**, we call `select` or `poll` and block in one of these two system calls, instead of blocking in the actual I/O system call. The figure is a summary of the I/O multiplexing model:

[![Figure 6.3. I/O multiplexing model.](figure_6.3.png)](figure_6.3.png "Figure 6.3. I/O multiplexing model.")

We block in a call to `select`, waiting for the datagram socket to be readable. When `select` returns that the socket is readable, we then call `recvfrom` to copy the datagram into our application buffer.

##### **Comparing to the blocking I/O model** *

Comparing [Figure 6.3](figure_6.3.png) to [Figure 6.1](figure_6.1.png):

* Disadvantage: using `select` requires two system calls (`select` and `recvfrom`) instead of one
* Advantage: we can wait for more than one descriptor to be ready (see [select-function]() later in this chapter)

##### **Multithreading with blocking I/O** *

Another closely related I/O model is to use multithreading with blocking I/O. That model very closely resembles the model described above, except that instead of using `select` to block on multiple file descriptors, the program uses multiple threads (one per file descriptor), and each thread is then free to call blocking system calls like `recvfrom`.

#### Signal-Driven I/O Model

The **signal-driven I/O model** uses signals, telling the kernel to notify us with the `SIGIO` signal when the descriptor is ready. The figure is below:

[![Figure 6.4. Signal-Driven I/O model.](figure_6.4.png)](figure_6.4.png "Figure 6.4. Signal-Driven I/O model.")

* We first enable the socket for signal-driven I/O ([Section 25.2](/unp/ch25/)) and install a signal handler using the `sigaction` system call. The return from this system call is immediate and our process continues; it is not blocked.
* When the datagram is ready to be read, the `SIGIO` signal is generated for our process. We can either:
    * read the datagram from the signal handler by calling `recvfrom` and then notify the main loop that the data is ready to be processed ([Section 25.3](/unp/ch25/))
    * notify the main loop and let it read the datagram.

The advantage to this model is that we are not blocked while waiting for the datagram to arrive. The main loop can continue executing and just wait to be notified by the signal handler that either the data is ready to process or the datagram is ready to be read.

#### Asynchronous I/O Model

**Asynchronous I/O** is defined by the POSIX specification, and various differences in the *real-time* functions that appeared in the various standards which came together to form the current POSIX specification have been reconciled.

These functions work by telling the kernel to start the operation and to notify us when the entire operation (including the copy of the data from the kernel to our buffer) is complete. <u>The main difference between this model and the signal-driven I/O model is that with signal-driven I/O, the kernel tells us when an I/O operation can be initiated, but with asynchronous I/O, the kernel tells us when an I/O operation is complete.</u> See the figure below for example:

[![Figure 6.5. Asynchronous I/O model.](figure_6.5.png)](figure_6.5.png "Figure 6.5. Asynchronous I/O model.")

* We call `aio_read` (the POSIX asynchronous I/O functions begin with `aio_` or `lio_`) and pass the kernel the following:
    * descriptor, buffer pointer, buffer size (the same three arguments for `read`),
    * file offset (similar to `lseek`),
    * and how to notify us when the entire operation is complete.

    This system call returns immediately and our process is not blocked while waiting for the I/O to complete.

* We assume in this example that we ask the kernel to generate some signal when the operation is complete. This signal is not generated until the data has been copied into our application buffer, which is different from the signal-driven I/O model.

#### Comparison of the I/O Models

The figure below is a comparison of the five different I/O models.

[![Figure 6.6. Comparison of the five I/O models.](figure_6.6.png)](figure_6.6.png "Figure 6.6. Comparison of the five I/O models.")

The main difference between the first four models is the first phase, as the second phase in the first four models is the same: the process is blocked in a call to `recvfrom` while the data is copied from the kernel to the caller's buffer. Asynchronous I/O, however, handles both phases and is different from the first four.

#### Synchronous I/O versus Asynchronous I/O

POSIX defines these two terms as follows:

* A synchronous I/O operation causes the requesting process to be blocked until that I/O operation completes.
* An asynchronous I/O operation does not cause the requesting process to be blocked.

Using these definitions, the first four I/O models (blocking, nonblocking, I/O multiplexing, and signal-driven I/O) are all synchronous because the actual I/O operation (`recvfrom`) blocks the process. Only the asynchronous I/O model matches the asynchronous I/O definition.

#### `select` Function
