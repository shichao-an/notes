### **Chapter 5. TCP Client/Server Example**

### Introduction

We will now use the elementary functions from the previous chapter to write a complete TCP client/server example. Our simple example is an echo server that performs the following steps:


1. The client reads a line of text from its standard input and writes the line to the server.
2. The server reads the line from its network input and echoes the line back to the client.
3. The client reads the echoed line and prints it on its standard output.

The figure below depcits this simple client/server:

[![Figure 5.1. Simple echo client and server.](figure_5.1.png)](figure_5.1.png "Figure 5.1. Simple echo client and server.")

Despite two arrows between the client and server in the above figure, it is really a [full-duplex](/unp/ch2/#transmission-control-protocol-tcp) TCP connection. `fgets` and `fputs` functions are from the standard I/O library. `writen` and `readline` functions were shown in [Section 3.9](/unp/ch3/#readn-writen-and-readline-functions).

The echo client/server is a valid, simple example of a network application. To expand this example into your own application, all you need to do is change what the server does with the input it receives from its clients.

Besides running the client/server in normal mode (type in a line and watch it echo), we examine lots of boundary conditions:

* What happens when the client and server are started?
* What happens when the client terminates normally?
* What happens to the client if the server process terminates before the client is done?
* What happens to the client if the server host crashes?

In all these examples, we have "hard-coded" protocol-specific constants such as addresses and ports. There are two reasons for this:

* We must understand exactly what needs to be stored in the protocol-specific address structures
* We have not yet covered the library functions that can make this more portable

### TCP Echo Server: `main` Function

Our TCP client and server follow the flow of functions that we diagrammed in [Figure 4.1](figure_4.1.png). The below code is the concurrent server program:

<small>[tcpcliserv/tcpserv01.c](https://github.com/shichao-an/unpv13e/blob/master/tcpcliserv/tcpserv01.c)</small>

```c
#include	"unp.h"

int
main(int argc, char **argv)
{
	int					listenfd, connfd;
	pid_t				childpid;
	socklen_t			clilen;
	struct sockaddr_in	cliaddr, servaddr;

	listenfd = Socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family      = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port        = htons(SERV_PORT);

	Bind(listenfd, (SA *) &servaddr, sizeof(servaddr));

	Listen(listenfd, LISTENQ);

	for ( ; ; ) {
		clilen = sizeof(cliaddr);
		connfd = Accept(listenfd, (SA *) &cliaddr, &clilen);

		if ( (childpid = Fork()) == 0) {	/* child process */
			Close(listenfd);	/* close listening socket */
			str_echo(connfd);	/* process the request */
			exit(0);
		}
		Close(connfd);			/* parent closes connected socket */
	}
}
```

The above code does the following:

* **Create socket, bind server's well-known port**
    * A TCP socket is created.
    * An Internet socket address structure is filled in with the wildcard address (`INADDR_ANY`) and the server's well-known port (`SERV_PORT`, which is defined as 9877 in our [unp.h](https://github.com/shichao-an/unpv13e/blob/master/lib/unp.h#L200) header). Binding the wildcard address tells the system that we will accept a connection destined for any local interface, in case the system is multihomed. Our choice of the TCP port number is based on [Figure 2.10](figure_2.10.png) in [Section 2.9](/unp/ch2/#port-numbers). It should be greater than 1023 (we do not need a reserved port), greater than 5000 (to avoid conflict with the ephemeral ports allocated by many Berkeley-derived implementations), less than 49152 (to avoid conflict with the "correct" range of ephemeral ports), and it should not conflict with any registered port.  [p122]
    * The socket is converted into a listening socket by `listen`.
* **Wait for client connection to complete**
    * The server blocks in the call to `accept`, waiting for a client connection to complete.
* **Concurrent server**
    * For each client, `fork` spawns a child, and the child handles the new client. The child closes the listening socket and the parent closes the connected socket. ([Section 4.8](/unp/ch4/#concurrent-servers))

### TCP Echo Server: `str_echo` Function

The function `str_echo` performs the server processing for each client: It reads data from the client and echoes it back to the client.

<small>[lib/str_echo.c](https://github.com/shichao-an/unpv13e/blob/master/lib/str_echo.c)</small>

```c
#include	"unp.h"

void
str_echo(int sockfd)
{
	ssize_t		n;
	char		buf[MAXLINE];

again:
	while ( (n = read(sockfd, buf, MAXLINE)) > 0)
		Writen(sockfd, buf, n);

	if (n < 0 && errno == EINTR)
		goto again;
	else if (n < 0)
		err_sys("str_echo: read error");
}
```

The above code does the following:

* **Read a buffer and echo the buffer**
    * `read` reads data from the socket and the line is echoed back to the client by `writen`. If the client closes the connection (the normal scenario), <u>the receipt of the client's FIN causes the child's read to return 0.</u> This causes the `str_echo` function to return, which terminates the child.

### TCP Echo Client: `main` Function

</small>[tcpcliserv/tcpcli01.c](https://github.com/shichao-an/unpv13e/blob/master/tcpcliserv/tcpcli01.c)</small>

```c
#include	"unp.h"

int
main(int argc, char **argv)
{
	int					sockfd;
	struct sockaddr_in	servaddr;

	if (argc != 2)
		err_quit("usage: tcpcli <IPaddress>");

	sockfd = Socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(SERV_PORT);
	Inet_pton(AF_INET, argv[1], &servaddr.sin_addr);

	Connect(sockfd, (SA *) &servaddr, sizeof(servaddr));

	str_cli(stdin, sockfd);		/* do it all */

	exit(0);
}
```

The above code does the following:

* **Create socket, fill in Internet socket address structure**
    * A TCP socket is created and an Internet socket address structure is filled in with the server's IP address and port number. The server's IP address is taken from the command-line argument and the server's well-known port (`SERV_PORT`) is from our `unp.h` header.
* **Connect to server**
    * `connect` establishes the connection with the server. The function `str_cli` handles the rest of the client processing.

### TCP Echo Client: `str_cli` Function

The `str_cli` function handles the client processing loop: It reads a line of text from standard input, writes it to the server, reads back the server's echo of the line, and outputs the echoed line to standard output.

</small>[lib/str_cli.c](https://github.com/shichao-an/unpv13e/blob/master/lib/str_cli.c)</small>

```c
#include	"unp.h"

void
str_cli(FILE *fp, int sockfd)
{
	char	sendline[MAXLINE], recvline[MAXLINE];

	while (Fgets(sendline, MAXLINE, fp) != NULL) {

		Writen(sockfd, sendline, strlen(sendline));

		if (Readline(sockfd, recvline, MAXLINE) == 0)
			err_quit("str_cli: server terminated prematurely");

		Fputs(recvline, stdout);
	}
}
```

The above code does the following:

* **Read a line, write to server**
    * `fgets` reads a line of text and `writen` sends the line to the server.
* **Read echoed line from server, write to standard output**
    * `readline` reads the line echoed back from the server and `fputs` writes it to standard output.
* **Return to main**
  * The loop terminates when `fgets` returns a null pointer, which occurs when it encounters either an end-of-file (EOF) or an error. Our `Fgets` wrapper function checks for an error and aborts if one occurs, so `Fgets` returns a null pointer only when an end-of-file is encountered.

### Normal Startup

Although the TCP example is small, it is essential that we understand:

* How the client and server start and end,
* What happens when something goes wrong:
    * the client host crashes,
    * the client process crashes,
    * network connectivity is lost

Only by understanding these boundary conditions, and their interaction with the TCP/IP protocols, can we write robust clients and servers that can handle these conditions.

#### Start the server in the background

First, we start the server in the background:

```text
linux % tcpserv01 &
[1] 17870
```

When the server starts, it calls `socket`, `bind`, `listen`, and `accept`, blocking in the call to accept.

#### Run `netstat`

Before starting the client, we run the `netstat` program to verify the state of the server's listening socket.

```text
linux % netstat -a
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address       Foreign Address      State
tcp        0      0 *:9877              *:*                  LISTEN
```

This command shows the status of all sockets on the system. We must specify the `-a` flag to see listening sockets.

In the output, a socket is in the LISTEN state with a wildcard for the local IP address and a local port of 9877. `netstat` prints an asterisk for an IP address of 0 (`INADDR_ANY`, the wildcard) or for a port of 0.

#### Start the client on the same host

We then start the client on the same host, specifying the server's IP address of 127.0.0.1 (the loopback address). We could have also specified the server's normal (nonloopback) IP address.

```text
linux % tcpcli01 127.0.0.1
```

The client calls `socket`, and `connect` which causes TCP's three-way handshake. When the three-way handshake completes, `connect` returns in the client and `accept` returns in the server. The connection is established. The following steps then take place:

1. The client calls `str_cli`, which will block in the call to `fgets`.
2. When `accept` returns in the server, it calls `fork` and the child calls `str_echo`. This function calls `readline`, which calls `read`, which blocks while waiting for a line to be sent from the client.
3. The server parent, on the other hand, calls `accept` again, and blocks while waiting for the next client connection.

Notes from the previous three steps:

* All three processes are asleep (blocked): client, server parent, and server child.
* We purposely list the client step first, and then the server steps when the three-way handshake completes. This is because `accept` returns one-half of the RTT after `connect` returns (see [Figure 2.5](figure_2.5.png)):
    * On the client side, `connect` returns when the second segment of the handshake is received
    * On the server side, `accept` does not return until the third segment of the handshake is received

#### Run `netstat` after connection completes

Since we are running the client and server on the same host, `netstat` now shows two additional lines of output, corresponding to the TCP connection:

```text
linux % netstat -a
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address          State
tcp        0      0 local host:9877         localhost:42758          ESTABLISHED
tcp        0      0 local host:42758        localhost:9877           ESTABLISHED
tcp        0      0 *:9877                  *:*                      LISTEN
```

* The first ESTABLISHED line corresponds to the server child's socket, since the local port is 9877.
* The second ESTABLISHED lines is the client's socket, since the local port is 42758

If we were running the client and server on different hosts, the client host would display only the client's socket, and the server host would display only the two server sockets.

#### Run `ps` to check process status and relationship

```text
linux % ps -t pts/6 -o pid,ppid,tty,stat,args,wchan
  PID  PPID TT       STAT COMMAND          WCHAN
22038 22036 pts/6    S    -bash            wait4
17870 22038 pts/6    S    ./tcpserv01      wait_for_connect
19315 17870 pts/6    S    ./tcpserv01      tcp_data_wait
19314 22038 pts/6    S    ./tcpcli01 127.0 read_chan
```

Very specific arguments to `ps` are used:

* The TT column (`pts/6`): client and server are run from the same window, pseudo-terminal number 6.
* The PID and PPID columns show the parent and child relationships.
    * The first `tcpserv01` line is the parent and the second tcpserv01 line is the child since the PPID of the child is the parent's PID.
    * The PPID of the parent is the shell (bash).
* The STAT column for all three of our network processes is "S", meaning the process is sleeping (waiting for something).
* The WCHAN column specifies the condition when a process is asleep.
    * Linux prints `wait_for_connect` when a process is blocked in either `accept` or `connect`, `tcp_data_wait` when a process is blocked on socket input or output, or `read_chan` when a process is blocked on terminal I/O.
    * In [`ps(1)`](http://man7.org/linux/man-pages/man1/ps.1.html), WCHAN column indicates the name of the kernel function in which the process is sleeping, a "-" if the process is running, or a "*" if the process is multi-threaded and ps is not displaying threads.

### Normal Termination

At this point, the connection is established and whatever we type to the client is echoed back.

```shell-session
linux % tcpcli01 127.0.0.1   # we showed this line earlier
hello, world                 # we now type this
hello, world                 # and the line is echoed
good bye
good bye
^D                           # Control-D is our terminal EOF character
```

If we immediately execute netstat, we have:

```shell-session
linux % netstat -a | grep 9877
tcp        0      0 *:9877               *:*               LISTEN
tcp        0      0 localhost:42758      localhost:9877    TIME_WAIT
```
This time we pipe the output of netstat into `grep`, printing only the lines with our server's well-known port:

* The client's side of the connection (since the local port is 42758) enters the TIME_WAIT state
* The listening server is still waiting for another client connection.

The following steps are involved in the normal termination of client and server:

1. When we type our EOF character, `fgets` returns a null pointer and the function `str_cli` ([Section 5.5](#tcp-echo-client-str_cli-function)) returns.
2. `str_cli` returns to the client `main` function ([Section 5.5](#tcp-echo-client-main-function)), which terminates by calling `exit`.
3. Part of process termination is the closing of all open descriptors, so the client socket is closed by the kernel. This sends a FIN to the server, to which the server TCP responds with an ACK. This is the first half of the TCP connection termination sequence. At this point, the server socket is in the CLOSE_WAIT state and the client socket is in the FIN_WAIT_2 state ([Figure 2.4](figure_2.4.png) and [Figure 2.5](figure_2.5.png))
4. When the server TCP receives the FIN, the server child is blocked in a call to `read` ([Section 3.8](#tcp-echo-server-str_echo-function)), and `read` then returns 0. This causes the `str_echo` function to return to the server child main. [Errata] [p128]
5. The server child terminates by calling exit. ([Section 5.2](#tcp-echo-server-main-function))
6. All open descriptors in the server child are closed.
    * The closing of the connected socket by the child causes the final two segments of the TCP connection termination to take place: a FIN from the server to the client, and an ACK from the client.
7. Finally, the `SIGCHLD` signal is sent to the parent when the server child terminates.
    * This occurs in this example, but we do not catch the signal in our code, and the default action of the signal is to be ignored. Thus, the child enters the zombie state. We can verify this with the `ps` command.

```shell-session
linux % ps -t pts/6 -o pid,ppid,tty,stat,args,wchan
  PID  PPID TT       STAT COMMAND          WCHAN
22038 22036 pts/6    S    -bash            read_chan
17870 22038 pts/6    S    ./tcpserv01      wait_for_connect
19315 17870 pts/6    Z    [tcpserv01 <defu do_exit
```

The STAT of the child is now `Z` (for zombie).

We need to clean up our zombie processes and doing this requires dealing with Unix signals. The next section will give an overview of signal handling.

### POSIX Signal Handling

A **signal** is a notification to a process that an event has occurred. Signals are sometimes called **software interrupts**. Signals usually occur asynchronously, which means that a process doesn't know ahead of time exactly when a signal will occur.

Signals can be sent:

* By one process to another process (or to itself)
* By the kernel to a process.
    * For example, whenever a process terminates, the kernel send a `SIGCHLD` signal to the parent of the terminating process.

Every signal has a **disposition**, which is also called the **action** associated with the signal. We set the disposition of a signal by calling the `sigaction` function and we have three choices for the disposition:

1. **Catching a signal**. We can provide a function called a **signal handler** that is called whenever a specific signal occurs. The two signals `SIGKILL` and `SIGSTOP` cannot be caught. Our function is called with a single integer argument that is the signal number and the function returns nothing. Its function prototype is therefore:

        void handler (int signo);

    For most signals, we can call `sigaction` and specify the signal handler to catch it. A few signals, `SIGIO`, `SIGPOLL`, and `SIGURG`, all require additional actions on the part of the process to catch the signal.

2. **Ignoring a signal**. We can ignore a signal by setting its disposition to `SIG_IGN`. The two signals SIGKILL and SIGSTOP cannot be ignored.
3. **Setting the default disposition for a signal**. This can be done by setting its disposition to `SIG_DFL`. The default is normally to terminate a process on receipt of a signal, with certain signals also generating a core image of the process in its current working directory. There are a few signals whose default disposition is to be ignored: `SIGCHLD` and `SIGURG` (sent on the arrival of out-of-band data) are two that we will encounter in this text.


### `signal` Function

The POSIX way to establish the disposition of a signal is to call the `sigaction` function, which is complicated in that one argument to the function is a structure (`struct sigaction`) that we must allocate and fill in.

An easier way to set the disposition of a signal is to call the `signal` function. The first argument is the signal name and the second argument is either a pointer to a function or one of the constants `SIG_IGN` or `SIG_DFL`.

However, `signal` is an historical function that predates POSIX. Different implementations provide different signal semantics when it is called, providing backward compatibility, whereas POSIX explicitly spells out the semantics when `sigaction` is called.

The solution is to define our own function named `signal` that just calls the POSIX `sigaction` function. This provides a simple interface with the desired POSIX semantics. We include this function in our own library, along with our `err`_XXX functions and our wrapper functions. [p130]

<small>[lib/signal.c](https://github.com/shichao-an/unpv13e/blob/master/lib/signal.c)</small>

```c
#include	"unp.h"

Sigfunc *
signal(int signo, Sigfunc *func)
{
	struct sigaction	act, oact;

	act.sa_handler = func;
	sigemptyset(&act.sa_mask);
	act.sa_flags = 0;
	if (signo == SIGALRM) {
#ifdef	SA_INTERRUPT
		act.sa_flags |= SA_INTERRUPT;	/* SunOS 4.x */
#endif
	} else {
#ifdef	SA_RESTART
		act.sa_flags |= SA_RESTART;		/* SVR4, 44BSD */
#endif
	}
	if (sigaction(signo, &act, &oact) < 0)
		return(SIG_ERR);
	return(oact.sa_handler);
}
/* end signal */

Sigfunc *
Signal(int signo, Sigfunc *func)	/* for our signal() function */
{
	Sigfunc	*sigfunc;

	if ( (sigfunc = signal(signo, func)) == SIG_ERR)
		err_sys("signal error");
	return(sigfunc);
}
```

#### Simplify function prototype using `typedef`

The normal function prototype for `signal` is complicated by the level of nested parentheses.

```c
void (*signal (int signo, void (*func) (int))) (int);
```

To simplify this, we define the `Sigfunc` type in our [unp.h](https://github.com/shichao-an/unpv13e/blob/master/lib/unp.h#L243) header as

```c
typedef    void    Sigfunc(int);
```

stating that signal handlers are functions with an integer argument and the function returns nothing (`void`). The function prototype then becomes

```c
Sigfunc *signal (int signo, Sigfunc *func);
```

A pointer to a signal handling function is the second argument to the function, as well as the return value from the function.

#### Set handler

The `sa_handler` member of the `sigaction` structure is set to the *func* argument.

#### Set signal mask for handler

POSIX allows us to specify a set of signals that will be blocked when our signal handler is called. Any signal that is blocked cannot be delivered to a process. We set the `sa_mask` member to the empty set, which means that no additional signals will be blocked while our signal handler is running. <u>POSIX guarantees that the signal being caught is always blocked while its handler is executing.</u>

#### Set `SA_RESTART` flag

`SA_RESTART` is an optional flag. When the flag is set, a system call interrupted by this signal will be automatically restarted by the kernel.

If the signal being caught is not `SIGALRM`, we specify the `SA_RESTART` flag, if defined. This is because the purpose of generating the `SIGALRM` signal is normally to place a timeout on an I/O operation, in which case, we want the blocked system call to be interrupted by the signal. [p131]

#### Call `sigaction`

We call `sigaction` and then <u>return the old action for the signal as the return value of the signal function.</u>

Throughout this text, we will use the `signal` function from the above definition.

### Handling `SIGCHLD` Signals

The zombie state is to maintain information about the child for the parent to fetch later, which includes:

* process ID of the child,
* termination status,
* information on the resource utilization of the child.
