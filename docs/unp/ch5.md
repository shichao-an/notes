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

* [tcpcliserv/tcpserv01.c](https://github.com/shichao-an/unpv13e/blob/master/tcpcliserv/tcpserv01.c)

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

* [lib/str_echo.c](https://github.com/shichao-an/unpv13e/blob/master/lib/str_echo.c)

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

* [tcpcliserv/tcpcli01.c](https://github.com/shichao-an/unpv13e/blob/master/tcpcliserv/tcpcli01.c)

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

* [lib/str_cli.c](https://github.com/shichao-an/unpv13e/blob/master/lib/str_cli.c)

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
