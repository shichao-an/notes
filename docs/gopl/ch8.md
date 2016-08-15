### **Chapter 8. Goroutines and Channels**

Concurrent programming, the expression of a program as a composition of several autonomous activities, has never been more important than it is today.

Go enables two styles of concurrent programming.

* This chapter presents goroutines and channels, which support [communicating sequential processes](https://en.wikipedia.org/wiki/Communicating_sequential_processes) (CSP), a model of concurrency in which values are passed between independent activities (goroutines) but variables are for the most part confined to a single activity.
* [Chapter 9](ch9.md) covers some aspects of the more traditional model of **shared memory multithreading**, which will be familiar to those who used threads in other mainstream languages.

### Goroutines

In Go, each concurrently executing activity is called a *goroutine*. If you have used operating system threads or threads in other languages, then you can assume for now that a goroutine is similar to a thread.  The differences between threads and goroutines are essentially quantitative, not qualitative, and will be described in [Section 9.8](ch9.md#goroutines-and-threads).

When a program starts, its only goroutine is the one that calls the `main` function, so we call it the *main goroutine*. New goroutines are created by the `go` statement:

* Syntactically, a `go` statement is an ordinary function or method call prefixed by the keyword `go`.
* A `go` statement causes the function to be called in a newly created goroutine. The go statement itself completes immediately.

```go
f()    // call f(); wait for it to return
go f() // create a new goroutine that calls f(); don't wait
```

In the example below, the main goroutine computes the 45th Fibonacci number using an inefficient recursive algorithm, which runs for an appreciable time, during which we provide the user with a visual indication that the program is still running, by displaying an animated textual "spinner".

<small>[gopl.io/ch8/spinner/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/spinner/main.go)</small>

```go

func main() {
	go spinner(100 * time.Millisecond)
	const n = 45
	fibN := fib(n) // slow
	fmt.Printf("\rFibonacci(%d) = %d\n", n, fibN)
}

func spinner(delay time.Duration) {
	for {
		for _, r := range `-\|/` {
			fmt.Printf("\r%c", r)
			time.Sleep(delay)
		}
	}
}

func fib(x int) int {
	if x < 2 {
		return x
	}
	return fib(x-1) + fib(x-2)
}
```

After several seconds of animation, the `fib(45)` call returns and the main function prints its result:

```text
Fibonacci(45) = 1134903170
```

The `main` function then returns. When this happens, all goroutines are abruptly terminated and the program exits. Other than by returning from `main` or exiting the program, there is no programmatic way for one goroutine to stop another, but as we will see later, there are ways to communicate with a goroutine to request that it stop itself.

Notice how the program is expressed as the composition of two autonomous activities, spinning and Fibonacci computation. Each is written as a separate function but both make progress concurrently.

### Example: Concurrent Clock Server

Networking is a natural domain to use concurrency since servers typically handle many connections from their clients at once, each client being essentially independent of the others. This section introduces the [`net`](https://golang.org/pkg/net/) package, which provides the components for building networked client and server programs that communicate over TCP, UDP, or Unix domain sockets. The [`net/http`](https://golang.org/pkg/net/http/) package introduced since [Chapter 1](ch1.md) is built on top of functions from the `net` package.

The first example is a sequential clock server that writes the current time to the client once per second:

<small>[gopl.io/ch8/clock1/clock.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/clock1/clock.go)</small>

```go
// Clock1 is a TCP server that periodically writes the time.
package main

import (
	"io"
	"log"
	"net"
	"time"
)

func main() {
	listener, err := net.Listen("tcp", "localhost:8000")
	if err != nil {
		log.Fatal(err)
	}
	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Print(err) // e.g., connection aborted
			continue
		}
		handleConn(conn) // handle one connection at a time
	}
}

func handleConn(c net.Conn) {
	defer c.Close()
	for {
		_, err := io.WriteString(c, time.Now().Format("15:04:05\n"))
		if err != nil {
			return // e.g., client disconnected
		}
		time.Sleep(1 * time.Second)
	}
}
```

* The `Listen` function creates a [`net.Listener`](https://golang.org/pkg/net/#Listener), an object that listens for incoming connections on a network port, in this case TCP port `localhost:8000`. The listener's `Accept` method blocks until an incoming connection request is made, then returns a [`net.Conn`](https://golang.org/pkg/net/#Conn) object representing the connection.
* The `handleConn` function handles one complete client connection.
    * In a loop, it writes the current time, `time.Now()`, to the client.
    * Since `net.Conn` satisfies the `io.Writer` interface, we can write directly to it.
    * The loop ends when the write fails, most likely because the client has disconnected, at which point `handleConn` closes its side of the connection using a deferred call to `Close` and goes back to waiting for another connection request.
* The `time.Time.Format` method provides a way to format date and time information by example. Its argument is a template indicating how to format a reference time, specifically `Mon Jan 2 03:04:05PM 2006 UTC-0700`.
    * The reference time has eight components. Any collection of them can appear in the `Format` string in any order and in a number of formats; the selected components of the date and time will be displayed in the selected formats. This example uses the hour, minute, and second of the time.
    * The `time` package defines templates for many standard time formats, such as [`time.RFC1123`](https://golang.org/pkg/time/#pkg-constants). The same mechanism is used in reverse when parsing a time using `time.Parse`.

To connect to the server, we need a client program such as `nc` ("netcat"), a standard utility program for manipulating network connections:

```shell-session
$ go build gopl.io/ch8/clock1
$ ./clock1 &
$ nc localhost 8000
13:58:54
13:58:55
13:58:56
13:58:57
^C
```

The client displays the time sent by the server each second until we interrupt the client with Control-C, which on Unix systems is echoed as `^C` by the shell. We can also use `telnet`, or the following simple Go version of `netcat` that uses `net.Dial` to connect to a TCP server:

```go
// Netcat1 is a read-only TCP client.
package main

import (
	"io"
	"log"
	"net"
	"os"
)

func main() {
	conn, err := net.Dial("tcp", "localhost:8000")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()
	mustCopy(os.Stdout, conn)
}

func mustCopy(dst io.Writer, src io.Reader) {
	if _, err := io.Copy(dst, src); err != nil {
		log.Fatal(err)
	}
}
```

This program reads data from the connection and writes it to the standard output until an
end-of-file condition or an error occurs. The `mustCopy` function is a utility used in several
examples in this section.

We run two clients at the same time on different terminals, one shown to the left and one to the right:

```text
$ go build gopl.io/ch8/netcat1
$ ./netcat1
13:58:54                        $ ./netcat1
13:58:55
13:58:56
^C
                                13:58:57
                                13:58:58
                                13:58:59
                                ^C
$ killall clock1
```

The second client must wait until the first client is finished because the server is sequential; it deals with only one client at a time.  Only one small change is needed to make the server concurrent: adding the `go` keyword to the call to `handleConn` causes each call to run in its own goroutine.

<small>[gopl.io/ch8/clock2/clock.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/clock2/clock.go)</small>

```go
for {
	conn, err := listener.Accept()
	if err != nil {
		log.Print(err) // e.g., connection aborted
		continue
	}
	go handleConn(conn) // handle connections concurrently
}
```

Now, multiple clients can receive the time at once.

```text
$ go build gopl.io/ch8/clock2
$ ./clock2 &
$ go build gopl.io/ch8/netcat1
$ ./netcat1
14:02:54                     $ ./netcat1
14:02:55                     14:02:55
14:02:56                     14:02:56
14:02:57                     ^C
14:02:58
14:02:59                     $ ./netcat1
14:03:00                     14:03:00
14:03:01                     14:03:01
^C                           14:03:02
                             ^C
```
