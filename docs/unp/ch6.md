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

In the figure above, the process calls `recvfrom` and the system call does not return until the datagram arrives and is copied into our application buffer, or an error occurs. The most common error is the system call being interrupted by a signal, as we described in [Section 5.9](ch5.md#handling-sigchld-signals). We say that the process is blocked the entire time from when it calls `recvfrom` until it returns. When `recvfrom` returns successfully, our application processes the datagram.

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
* Advantage: we can wait for more than one descriptor to be ready (see [the `select` function](#select-function) later in this chapter)

##### **Multithreading with blocking I/O** *

Another closely related I/O model is to use multithreading with blocking I/O. That model very closely resembles the model described above, except that instead of using `select` to block on multiple file descriptors, the program uses multiple threads (one per file descriptor), and each thread is then free to call blocking system calls like `recvfrom`.

#### Signal-Driven I/O Model

The **signal-driven I/O model** uses signals, telling the kernel to notify us with the `SIGIO` signal when the descriptor is ready. The figure is below:

[![Figure 6.4. Signal-Driven I/O model.](figure_6.4.png)](figure_6.4.png "Figure 6.4. Signal-Driven I/O model.")

* We first enable the socket for signal-driven I/O ([Section 25.2](ch25.md)) and install a signal handler using the `sigaction` system call. The return from this system call is immediate and our process continues; it is not blocked.
* When the datagram is ready to be read, the `SIGIO` signal is generated for our process. We can either:
    * read the datagram from the signal handler by calling `recvfrom` and then notify the main loop that the data is ready to be processed ([Section 25.3](ch25.md))
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

### `select` Function

The `select` function allows the process to instruct the kernel to either:

* Wait for any one of multiple events to occur and to wake up the process only when one or more of these events occurs, or
* When a specified amount of time has passed.

This means that we tell the kernel what descriptors we are interested in (for reading, writing, or an exception condition) and how long to wait. The descriptors in which we are interested are not restricted to sockets; any descriptor can be tested using `select`.

```c
#include <sys/select.h>
#include <sys/time.h>

int select(int maxfdp1, fd_set *readset, fd_set *writeset, fd_set *exceptset,
           const struct timeval *timeout);

/* Returns: positive count of ready descriptors, 0 on timeout, –1 on error */
```

##### **The *timeout* argument** *

The *timeout* argument tells the kernel how long to wait for one of the specified descriptors to become ready. A `timeval` structure specifies the number of seconds and microseconds.

```c
struct timeval  {
  long   tv_sec;          /* seconds */
  long   tv_usec;         /* microseconds */
};
```
There are three possibilities for the *timeout*:

1. **Wait forever** (*timeout* is specified as a null pointer). Return only when one of the specified descriptors is ready for I/O.
2. **Wait up to a fixed amount of time** (*timeout* points to a `timeval` structure). Return when one of the specified descriptors is ready for I/O, but do not wait beyond the number of seconds and microseconds specified in the `timeval` structure.
3. **Do not wait at all** (*timeout* points to a `timeval` structure and the timer value is 0, i.e. the number of seconds and microseconds specified by the structure are 0). Return immediately after checking the descriptors. This is called **polling**.

Note:

* The wait in the first two scenarios is normally interrupted if the process catches a signal and returns from the signal handler. For portability, we must be prepared for `select` to return an error of `EINTR` if we are catching signals. Berkeley-derived kernels never automatically restart `select`.
* Although the `timeval` structure has a microsecond field `tv_usec`, the actual resolution supported by the kernel is often more coarse. Many Unix kernels round the timeout value up to a multiple of 10 ms. There is also a scheduling latency involved, meaning it takes some time after the timer expires before the kernel schedules this process to run.
* On some systems, the `timeval` structure can represent values that are not supported by `select`; it will fail with `EINVAL` if the `tv_sec` field in the timeout is over 100 million seconds.
* The `const` qualifier on the *timeout* argument means it is not modified by `select` on return.

##### **The descriptor sets arguments** *

The three middle arguments, *readset*, *writeset*, and *exceptset*, specify the descriptors that we want the kernel to test for reading, writing, and exception conditions. There are only two exception conditions currently supported:

* The arrival of [out-of-band data](https://en.wikipedia.org/wiki/Out-of-band_data) for a socket.
* The presence of control status information to be read from the master side of a pseudo-terminal that has been put into packet mode. (Not covered in UNP)

`select` uses **descriptor sets**, typically an array of integers, with each bit in each integer corresponding to a descriptor. For example, using 32-bit integers, the first element of the array corresponds to descriptors 0 through 31, the second element of the array corresponds to descriptors 32 through 63, and so on. All the implementation details are irrelevant to the application and are hidden in the `fd_set` datatype and the following four macros:

```c
void FD_ZERO(fd_set *fdset);         /* clear all bits in fdset */
void FD_SET(int fd, fd_set *fdset);  /* turn on the bit for fd in fdset */
void FD_CLR(int fd, fd_set *fdset);  /* turn off the bit for fd in fdset */
int FD_ISSET(int fd, fd_set *fdset); /* is the bit for fd on in fdset ? */
```

We allocate a descriptor set of the `fd_set` datatype, we set and test the bits in the set using these macros, and we can also assign it to another descriptor set across an equals sign (=) in C.

An array of integers using one bit per descriptor, is just one possible way to implement select. Nevertheless, it is common to refer to the individual descriptors within a descriptor set as bits, as in "turn on the bit for the listening descriptor in the read set."

The following example defines a variable of type `fd_set` and then turn on the bits for descriptors 1, 4, and 5:

```c
fd_set rset;

FD_ZERO(&rset);          /* initialize the set: all bits off */
FD_SET(1, &rset);        /* turn on bit for fd 1 */
FD_SET(4, &rset);        /* turn on bit for fd 4 */
FD_SET(5, &rset);        /* turn on bit for fd 5 */
```

It is important to initialize the set, since unpredictable results can occur if the set is allocated as an automatic variable and not initialized.

Any of the middle three arguments to `select`, *readset*, *writeset*, or *exceptset*, can be specified as a null pointer if we are not interested in that condition. Indeed, if all three pointers are null, then we have a higher precision timer than the normal Unix `sleep` function. The `poll` function provides similar functionality.

##### **The *maxfdp1* argument** *

The *maxfdp1* argument specifies the number of descriptors to be tested. Its value is the maximum descriptor to be tested plus one. The descriptors 0, 1, 2, up through and including *maxfdp1*–1 are tested.

The constant `FD_SETSIZE`, defined by including `<sys/select.h>`, is the number of descriptors in the `fd_set` datatype. Its value is often 1024, but few programs use that many descriptors.

The reason the *maxfdp1* argument exists, along with the burden of calculating its value, is for efficiency. Although each `fd_set` has room for many descriptors, typically 1,024, this is much more than the number used by a typical process. The kernel gains efficiency by not copying unneeded portions of the descriptor set between the process and the kernel, and by not testing bits that are always 0.

##### ***readset*, *writeset*, and *exceptset* as value-result arguments** *

`select` modifies the descriptor sets pointed to by the *readset*, *writeset*, and *exceptset* pointers. These three arguments are value-result arguments. When we call the function, we specify the values of the descriptors that we are interested in, and on return, the result indicates which descriptors are ready. We use the `FD_ISSET` macro on return to test a specific descriptor in an `fd_set` structure. Any descriptor that is not ready on return will have its corresponding bit cleared in the descriptor set. To handle this, we turn on all the bits in which we are interested in all the descriptor sets each time we call select.

##### **Return value of `select`** *

The return value from this function indicates the total number of bits that are ready across all the descriptor sets. If the timer value expires before any of the descriptors are ready, a value of 0 is returned. A return value of –1 indicates an error (which can happen, for example, if the function is interrupted by a caught signal).


#### Conditions for a Ready Descriptor

Previous sections discusses waiting for a descriptor to become ready for I/O (reading or writing) or to have an exception condition pending on it (out-of-band data). The following discussion are specific about the conditions that cause select to return "ready" for sockets

1. **A socket is ready for reading** if any of the following four conditions is true:
    * The number of bytes of data in the socket receive buffer is greater than or equal to the current size of the low-water mark for the socket receive buffer. A read operation on the socket will not block and will return a value greater than 0 (i.e., the data that is ready to be read). We can set this low-water mark using the `SO_RCVLOWAT` socket option. It defaults to 1 for TCP and UDP sockets.
    * The read half of the connection is closed (i.e., a TCP connection that has received a FIN). A read operation on the socket will not block and will return 0 (i.e., EOF).
    * The socket is a listening socket and the number of completed connections is nonzero.
    * A socket error is pending. A read operation on the socket will not block and will return an error (–1) with `errno` set to the specific error condition. These pending errors can also be fetched and cleared by calling `getsockopt` and specifying the `SO_ERROR` socket option.
2. **A socket is ready for writing** if any of the following four conditions is true:
    * The number of bytes of available space in the socket send buffer is greater than or equal to the current size of the low-water mark for the socket send buffer and either: (i) the socket is connected, or (ii) the socket does not require a connection (e.g., UDP). This means that if we set the socket to nonblocking ([Chapter 16](ch16.md)), a write operation will not block and will return a positive value (e.g., the number of bytes accepted by the transport layer). We can set this low-water mark using the `SO_SNDLOWAT` socket option. This low-water mark normally defaults to 2048 for TCP and UDP sockets.
    * The write half of the connection is closed. A write operation on the socket will generate `SIGPIPE` ([Section 5.12](ch5.md#sigpipe-signal)).
    * A socket using a non-blocking connect has completed the connection, or the connect has failed.
    * A socket error is pending. A write operation on the socket will not block and will return an error (–1) with `errno` set to the specific error condition. These pending errors can also be fetched and cleared by calling getsockopt with the `SO_ERROR` socket option.
3. **A socket has an exception condition pending if there is out-of-band data for the socket or the socket is still at the out-of-band mark** ([Chapter 24](ch24.md)).

<u>When an error occurs on a socket, it is marked as both readable and writable by select.</u>

The purpose of the receive and send low-water marks is to give the application control over how much data must be available for reading or how much space must be available for writing before select returns a readable or writable status. For example, if we know that our application has nothing productive to do unless at least 64 bytes of data are present, we can set the receive low-water mark to 64 to prevent select from waking us up if less than 64 bytes are ready for reading.

As long as the send low-water mark for a UDP socket is less than the send buffer size (which should always be the default relationship), the UDP socket is always writable, since a connection is not required.

The following table is the summary of conditions that cause a socket to be ready for select.

Condition | Readable? | Writable? | Exception
--------- | --------- | --------- | ---------
Data to read | x | |
Read half of the connection closed | x | |
New connection ready for listening socket | x | |
Space available for writing | | x |
Write half of the connection closed | | x |
Pending error | x | x |
TCP out-of-band data | | | x

#### Maximum Number of Descriptors for `select`

Most applications do not use lots of descriptors. It is rare to find an application that uses hundreds of descriptors, but such applications do exist, and they often use `select` to multiplex the descriptors.

When `select` was originally designed, the OS normally had an upper limit on the maximum number of descriptors per process (the 4.2BSD limit was 31), and select just used this same limit. But, current versions of Unix allow for a virtually unlimited number of descriptors per process (often limited only by the amount of memory and any administrative limits), which affects `select`.

Many implementations have declarations similar to the following, which are taken from the 4.4BSD `<sys/types.h>` header:

```c
/*
 * Select uses bitmasks of file descriptors in longs. These macros
 * manipulate such bit fields (the filesystem macros use chars).
 * FD_SETSIZE may be defined by the user, but the default here should
 * be enough for most uses.
 */
#ifndef FD_SETSIZE
#define FD_SETSIZE      256
#endif
```

This makes us think that we can just `#define FD_SETSIZE` to some larger value before including this header to increase the size of the descriptor sets used by `select`. Unfortunately, this normally does not work. The three descriptor sets are declared within the kernel and also uses the kernel's definition of `FD_SETSIZE` as the upper limit. The only way to increase the size of the descriptor sets is to increase the value of `FD_SETSIZE` and then recompile the kernel. Changing the value without recompiling the kernel is inadequate.

Some vendors are changing their implementation of select to allow the process to define `FD_SETSIZE` to a larger value than the default. BSD/OS has changed the kernel implementation to allow larger descriptor sets, and it also provides four new `FD_`*xxx* macros to dynamically allocate and manipulate these larger sets. From a portability standpoint, however, beware of using large descriptor sets.

### `str_cli` Function (Revisited)

The problem with earlier version of the `str_cli` ([Section 5.5](ch5.md#tcp-echo-client-str_cli-function)) was that we could be blocked in the call to `fgets` when something happened on the socket. We can now rewrite our `str_cli` function using `select` so that:

* The client process is notified as soon as the server process terminates.
* The client process blocks in a call to `select` waiting for either standard input or the socket to be readable.

The figure below shows the various conditions that are handled by our call to `select`:

[![Figure 6.8. Conditions handled by select in str_cli.](figure_6.8.png)](figure_6.8.png "Figure 6.8. Conditions handled by select in str_cli.")

Three conditions are handled with the socket:

1. If the peer TCP sends data, the socket becomes readable and read `returns` greater than 0 (the number of bytes of data).
2. If the peer TCP sends a FIN (the peer process terminates), the socket becomes readable and read returns 0 (EOF).
3. If the peer TCP sends an RST (the peer host has crashed and rebooted), the socket becomes readable, read returns –1, and `errno` contains the specific error code.

Below is the source code for this new version.

<small>[select/strcliselect01.c](https://github.com/shichao-an/unpv13e/blob/master/select/strcliselect01.c)</small>

```c
#include	"unp.h"

void
str_cli(FILE *fp, int sockfd)
{
	int			maxfdp1;
	fd_set		rset;
	char		sendline[MAXLINE], recvline[MAXLINE];

	FD_ZERO(&rset);
	for ( ; ; ) {
		FD_SET(fileno(fp), &rset);
		FD_SET(sockfd, &rset);
		maxfdp1 = max(fileno(fp), sockfd) + 1;
		Select(maxfdp1, &rset, NULL, NULL, NULL);

		if (FD_ISSET(sockfd, &rset)) {	/* socket is readable */
			if (Readline(sockfd, recvline, MAXLINE) == 0)
				err_quit("str_cli: server terminated prematurely");
			Fputs(recvline, stdout);
		}

		if (FD_ISSET(fileno(fp), &rset)) {  /* input is readable */
			if (Fgets(sendline, MAXLINE, fp) == NULL)
				return;		/* all done */
			Writen(sockfd, sendline, strlen(sendline));
		}
	}
}
```

This code does the following:

* **Call `select`**.
    * We only need one descriptor set (`rset`) to check for readability. This set is initialized by `FD_ZERO` and then two bits are turned on using `FD_SET`: the bit corresponding to the standard I/O file pointer, `fp`, and the bit corresponding to the socket, `sockfd`. The function `fileno` converts a standard I/O file pointer into its corresponding descriptor, since `select` (and `poll`) work only with descriptors.
    * `select` is called after calculating the maximum of the two descriptors. In the call, the write-set pointer and the exception-set pointer are both null pointers. The final argument (the time limit) is also a null pointer since we want the call to block until something is ready.
* **Handle readable socket**. On return from select, if the socket is readable, the echoed line is read with `readline` and output by `fputs`.
* **Handle readable input**. If the standard input is readable, a line is read by `fgets` and written to the socket using `writen`.

Instead of the function flow being driven by the call to `fgets`, it is now driven by the call to `select`.
