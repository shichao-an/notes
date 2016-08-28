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

<small>[gopl.io/ch8/netcat1/netcat.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/netcat2/netcat.go)</small>

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

This program reads data from the connection and writes it to the standard output until an end-of-file condition or an error occurs. The `mustCopy` function is a utility used in several examples in this section.

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

### Example: Concurrent Echo Server

The clock server used one goroutine per connection. In this section, we'll build an echo server that uses multiple goroutines per connection. Most echo servers merely write whatever they read, which can be done with this trivial version of `handleConn`:

```go
func handleConn(c net.Conn) {
	io.Copy(c, c) // NOTE: ignoring errors
	c.Close()
}
```

This version of echo server simulates the reverberations of a real echo, with the response loud at first ("HELLO!"), then moderate ("Hello!") after a delay, then quiet ("hello!") before fading to nothing:

<small>[gopl.io/ch8/reverb1/reverb.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/reverb1/reverb.go)</small>

```go
func echo(c net.Conn, shout string, delay time.Duration) {
	fmt.Fprintln(c, "\t", strings.ToUpper(shout))
	time.Sleep(delay)
	fmt.Fprintln(c, "\t", shout)
	time.Sleep(delay)
	fmt.Fprintln(c, "\t", strings.ToLower(shout))
}

func handleConn(c net.Conn) {
	input := bufio.NewScanner(c)
	for input.Scan() {
		echo(c, input.Text(), 1*time.Second)
	}
	// NOTE: ignoring potential errors from input.Err()
	c.Close()
}
```

The following client program sends terminal input to the server while also copying the server response to the output:

<small>[gopl.io/ch8/netcat2/netcat.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/netcat2/netcat.go)</small>

```go
func main() {
	conn, err := net.Dial("tcp", "localhost:8000")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()
	go mustCopy(os.Stdout, conn)
	mustCopy(conn, os.Stdin)
}
```

While the main goroutine reads the standard input and sends it to the server, a second goroutine reads and prints the server's response. When the main goroutine encounters the end of the input (for example, after the user types Control-D (`^D`)) at the terminal, the program stops, even if the other goroutine still has work to do. ([Section 8.4.1](#unbuffered-channels) discusses how to make the program wait for both sides to finish)

```text
$ go build gopl.io/ch8/reverb1
$ ./reverb1 &
$ go build gopl.io/ch8/netcat2
$ ./netcat2
Hello?
    HELLO?
    Hello?
    hello?
Is there anybody there?
    IS THERE ANYBODY THERE?
Yooo-hooo!
    Is there anybody there?
    is there anybody there?
    YOOO-HOOO!
    Yooo-hooo!
    yooo-hooo!
^D
$ killall reverb1
```

Notice that the third shout from the client is not dealt with until the second shout has petered out, which is not very realistic. A real echo would consist of the *composition* of the three independent shouts. To simulate it, more goroutines are needed; all we need to do is add the `go` keyword, this time to the call to `echo`:

<small>[gopl.io/ch8/reverb2/reverb.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/reverb2/reverb.go)</small>

```go
func handleConn(c net.Conn) {
	input := bufio.NewScanner(c)
	for input.Scan() {
		go echo(c, input.Text(), 1*time.Second)
	}
	// NOTE: ignoring potential errors from input.Err()
	c.Close()
}
```

The arguments to the function started by `go` are evaluated when the `go` statement itself is executed; thus `input.Text()` is evaluated in the main goroutine.

Now the echoes are concurrent and overlap in time:

```text
$ go build gopl.io/ch8/reverb2
$ ./reverb2 &
$ ./netcat2
Is there anybody there?
    IS THERE ANYBODY THERE?
Yooo-hooo!
    Is there anybody there?
    YOOO-HOOO!
    is there anybody there?
    Yooo-hooo!
    yooo-hooo!
^D
$ killall reverb2
```

<u>All that was required to make the server use concurrency, not just to handle connections from multiple clients but even within a single connection, was the insertion of two `go` keywords.</u>

However in adding these keywords, we had to consider carefully that it is safe to call methods of `net.Conn` concurrently, which is not true for most types. The next chapter discusses the crucial concept of concurrency safety in the.

### Channels

If goroutines are the activities of a concurrent Go program, channels are the connections between them.

* A channel is a communication mechanism that enables one goroutine to send values to another goroutine.
* Each channel is a conduit for values of a particular type, called the channel's *element type*. The type of a channel whose elements have type int is written `chan int`.

To create a channel, use the built-in `make` function:

```go
ch := make(chan int) // ch has type 'chan int'
```

A channel is a reference to the data structure created by `make`.

* When we copy a channel or pass one as an argument to a function, we are copying a reference, so caller and callee refer to the same data structure.
* As with other reference types, the zero value of a channel is `nil`.
* Two channels of the same type may be compared using `==`. The comparison is `true` if both are references to the same channel data structure. A channel may also be compared to `nil`.

A channel has two principal operations, *send* and *receive*, collectively known as *communications*. A send statement transmits a value from one goroutine, through the channel, to another goroutine executing a corresponding receive expression.

Both operations are written using the `<-` operator.

* In a send statement, the `<-` separates the channel and value operands.
* In a receive expression, `<-` precedes the channel operand. A receive expression whose result is not used is a valid statement.

```go
ch <- x // a send statement

x=<-ch  // a receive expression in an assignment statement
<-ch    // a receive statement; result is discarded
```

Channels support a third operation, *close*, which sets a flag indicating that no more values will ever be sent on this channel.

* Send operations on a closed channel will panic.
* Receive operations on a closed channel yield the values that have been sent until no more values are left; any receive operations thereafter complete immediately and yield the zero value of the channel's element type.

To close a channel, call the built-in `close` function:

```go
close(ch)
```

A channel created with a simple call to `make` is called an *unbuffered* channel. `make` accepts an optional second argument, an integer called the channel's *capacity*. If the capacity is nonzero, `make` creates a `buffered` channel.

```go
ch = make(chan int)    // unbuffered channel
ch = make(chan int, 0) // unbuffered channel
ch = make(chan int, 3) // buffered channel with capacity 3
```

Unbuffered channels are discussed in [Section 8.4.1](#unbuffered-channels) and buffered channels in [Section 8.4.4](#buffered-channels).

#### Unbuffered Channels

* A send operation on an unbuffered channel blocks the sending goroutine until another goroutine executes a corresponding receive on the same channel, at which point the value is transmitted and both goroutines may continue.
* Conversely, if the receive operation was attempted first, the receiving goroutine is blocked until another goroutine performs a send on the same channel.

Communication over an unbuffered channel causes the sending and receiving goroutines to *synchronize*. Because of this, unbuffered channels are sometimes called *synchronous* channels. When a value is sent on an unbuffered channel, the receipt of the value happens *before* the reawakening of the sending goroutine.

In discussions of concurrency:

* When we say *x happens before y*, we don't mean merely that *x* occurs earlier in time than *y*. We mean that it is guaranteed to do so and that all its prior effects (e.g. updates to variables) are complete and that you may rely on them.
* When we say *x is concurrent with y*, we mean *x* neither happens before *y* nor after *y*.
    * This doesn't mean that *x* and *y* are necessarily simultaneous; it merely means that we cannot assume anything about their ordering.
    * As discussed in the next chapter, it's necessary to order certain events during the program's execution to avoid the problems that arise when two goroutines access the same variable concurrently.

The client program in [Section 8.3](#example-concurrent-echo-server) copies input to the server in its main goroutine, so the client program terminates as soon as the input stream closes, even if the background goroutine is still working. To make the program wait for the background goroutine to complete before exiting, we use a channel to synchronize the two goroutines:

<small>[gopl.io/ch8/netcat3/netcat.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/netcat3/netcat.go)</small>

```go
func main() {
	conn, err := net.Dial("tcp", "localhost:8000")
	if err != nil {
		log.Fatal(err)
	}
	done := make(chan struct{})
	go func() {
		io.Copy(os.Stdout, conn) // NOTE: ignoring errors
		log.Println("done")
		done <- struct{}{} // signal the main goroutine
	}()
	mustCopy(conn, os.Stdin)
	conn.Close()
	<-done // wait for background goroutine to finish
}
```

When the user closes the standard input stream, `mustCopy` returns and the main goroutine calls `conn.Close()`, closing both halves of the network connection:

* Closing the write half of the connection causes the server to see an end-of-file condition.
* Closing the read half causes the background goroutine's call to `io.Copy` to return a "read from closed connection" error, which is why we've removed the error logging. Notice that the go statement calls a literal function, a common construction.

Before it returns, the background goroutine logs a message, then sends a value on the done channel. The main goroutine waits until it has received this value before returning. As a result, the program always logs the "`done`" message before exiting.

Messages sent over channels have two important aspects. Each message has a value, but sometimes the fact of communication and the moment at which it occurs are important. We call messages *events* when we wish to stress this aspect. When the event carries no additional information, that is, its sole purpose is synchronization, we'll emphasize this by using a channel whose element type is `struct{}`, though it's common to use a channel of `bool` or `int` for the same purpose since `done <- 1` is shorter than `done <- struct{}{}`.

#### Pipelines

Channels can be used to connect goroutines together so that the output of one is the input to another. This is called a *pipeline*. The program below consists of three goroutines connected by two channels, as shown the following figure.

[![Figure 8.1. A three-stage pipeline.](figure_8.1_600.png)](figure_8.1.png "Figure 8.1. A three-stage pipeline.")

<small>[gopl.io/ch8/pipeline1/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/pipeline1/main.go)</small>

```go
func main() {
	naturals := make(chan int)
	squares := make(chan int)

	// Counter
	go func() {
		for x := 0; ; x++ {
			naturals <- x
		}
	}()

	// Squarer
	go func() {
		for {
			x := <-naturals
			squares <- x * x
		}
	}()

	// Printer (in main goroutine)
	for {
		fmt.Println(<-squares)
	}
}
```

The first goroutine, `counter`, generates the integers 0, 1, 2, ..., and sends them over a channel to the second goroutine, `squarer`, which receives each value, squares it, and sends the result over another channel to the third goroutine, `printer`, which receives the squared values and prints them.

This program prints the infinite series of squares 0, 1, 4, 9, and so on. Pipelines like this may be found in long-running server programs where channels are used for lifelong communication between goroutines containing infinite loops.  If the sender knows that no further values will ever be sent on a channel, it is useful to communicate this fact to the receiver goroutines so that they can stop waiting. This is accomplished by closing the channel using the built-in `close` function:

```go
close(naturals)
```

After a channel has been closed, any further send operations on it will panic. After the closed channel has been *drained* (that is, after the last sent element has been received), all subsequent receive operations will proceed without blocking but will yield a zero value. Closing the `naturals` channel above would cause the `squarer`'s loop to spin as it receives a never-ending stream of zero values, and to send these zeros to the `printer`.

There is no way to test directly whether a channel has been closed, but there is a variant of the receive operation that produces two results: the received channel element, plus a boolean value, conventionally called `ok`, which is `true` for a successful receive and `false` for a receive on a closed and drained channel. Using this feature, we can modify the `squarer`'s loop to stop when the `naturals` channel is drained and close the `squares` channel in turn.

```go
// Squarer
go func() {
	for {
		x, ok := <-naturals
		if !ok {
			break // channel was closed and drained
		}
		squares <- x * x
	}
	close(squares)
}()
```

Since this pattern is common, the language enables us to use a `range` loop to iterate over channels. This is a more convenient syntax for receiving all the values sent on a channel and terminating the loop after the last one. In the pipeline below, when the `counter` goroutine finishes its loop after 100 elements, it closes the `naturals` channel, causing the `squarer` to finish its loop and close the `squares` channel. Finally, the main goroutine finishes its loop and the program exits. In a more complex program, it might make sense for the `counter` and `squarer` functions to defer the calls to `close` at the outset.

<small>[gopl.io/ch8/pipeline2/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/pipeline2/main.go)</small>

```go
func main() {
	naturals := make(chan int)
	squares := make(chan int)

	// Counter
	go func() {
		for x := 0; x < 100; x++ {
			naturals <- x
		}
		close(naturals)
	}()

	// Squarer
	go func() {
		for x := range naturals {
			squares <- x * x
		}
		close(squares)
	}()

	// Printer (in main goroutine)
	for x := range squares {
		fmt.Println(x)
	}
}
```

Not every channel needs closing. It's only necessary to close a channel when it is important to tell the receiving goroutines that all data have been sent. A channel that the garbage collector determines to be unreachable will have its resources reclaimed whether or not it is closed. (Don't confuse this with the `close` operation for open files. It is important to call the `Close` method on every file when you've finished with it.) Attempting to close an already-closed channel causes a panic, as does closing a `nil` channel. Closing channels has another use as a broadcast mechanism ([Section 8.9](#cancellation)).

#### Unidirectional Channel Types

As programs grow, it is natural to break up large functions into smaller pieces. The previous example program naturally divides into three functions:

```go
func counter(out chan int)
func squarer(out, in chan int)
func printer(in chan int)
```

The `squarer` function takes two parameters, the input channel and the output channel: `in` is only to be received from, and `out` is only to be sent to. The names `in` and `out` convey this intention, but nothing prevents squarer from sending to in or receiving from out.

This arrangement is typical. When a channel is supplied as a function parameter, it is nearly always with the intent that it be used exclusively for sending or exclusively for receiving.

To document this intent and prevent misuse, the Go type system provides *unidirectional* channel types that expose only one of the send and receive operations:

* The type `chan<- int`, a send-only channel of `int`, allows sends but not receives.
* The type `<-chan int`, a receive-only channel of `int`, allows receives but not sends.

Violations of this discipline are detected at compile time.

Since the `close` operation asserts that no more sends will occur on a channel, only the sending goroutine is in a position to call it, and for this reason it is a compile-time error to attempt to close a receive-only channel.

The following program is the squaring pipeline with unidirectional channel types:

<small>[gopl.io/ch8/pipeline3/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/pipeline3/main.go)</small>

```go
func counter(out chan<- int) {
	for x := 0; x < 100; x++ {
		out <- x
	}
	close(out)
}

func squarer(out chan<- int, in <-chan int) {
	for v := range in {
		out <- v * v
	}
	close(out)
}

func printer(in <-chan int) {
	for v := range in {
		fmt.Println(v)
	}
}

func main() {
	naturals := make(chan int)
	squares := make(chan int)

	go counter(naturals)
	go squarer(squares, naturals)
	printer(squares)
}
```

* The call `counter(naturals)` implicitly converts naturals, a value of type `chan int`, to the type of the parameter, `chan<- int`.
* The `printer(squares)` call does a similar implicit conversion to `<-chan int`.

Conversions from bidirectional to unidirectional channel types are permitted in any assignment, but not backward. Once you have a value of a unidirectional type such as `chan<- int`, there is no way to obtain from it a value of type `chan int` that refers to the same channel data structure.

#### Buffered Channels

A buffered channel has a queue of elements. The queue's maximum size is determined  by the capacity argument to `make` when it is created. The statement below creates a buffered channel capable of holding three string values.

```go
ch = make(chan string, 3)
```

The following figure a graphical representation of `ch` and the channel to which it refers.

[![Figure 8.2. An empty buffered channel.](figure_8.2.png)](figure_8.2.png "Figure 8.2. An empty buffered channel.")

A send operation on a buffered channel inserts an element at the back of the queue, and a receive operation removes an element from the front.

* If the channel is full, the send operation blocks its goroutine until space is made available by another goroutine's receive.
* If the channel is empty, a receive operation blocks until a value is sent by another goroutine.

We can send up to three values on this channel without the goroutine blocking:

```go
ch <- "A"
ch <- "B"
ch <- "C"
```

At this point, the channel is full, as shown below; a fourth send statement would block.

[![Figure 8.3. A full buffered channel.](figure_8.3.png)](figure_8.3.png "Figure 8.3. A full buffered channel.")

If we receive one value like this:

```go
fmt.Println(<-ch) // "A"
```

The channel is neither full nor empty (as shown in the figure below), so either a send operation or a receive operation could proceed without blocking. In this way, <u>the channel's buffer decouples the sending and receiving goroutines.</u>

[![Figure 8.4. A partially full buffered channel.](figure_8.4.png)](figure_8.4.png "Figure 8.4. A partially full buffered channel.")

The built-in `cap` function obtains the channel's buffer capacity:

```go
fmt.Println(cap(ch)) // "3"
```

The built-in `len` function returns the number of elements currently buffered

```go
fmt.Println(len(ch)) // "2"
```

Since in a concurrent program this information is likely to be stale as soon as it is retrieved, its value is limited, but it could conceivably be useful during fault diagnosis or performance optimization.

After two more receive operations the channel is empty again, and a fourth would block:

```go
fmt.Println(<-ch) // "B"
fmt.Println(<-ch) // "C"
```

In real programs, the send and receive operations are usually performed by different goroutines. It is a mistake to use buffered channels within a single goroutine as a queue. Channels are deeply connected to goroutine scheduling, and without another goroutine receiving from the channel, a sender (and perhaps the whole program) risks becoming blocked forever.

The example below shows an application of a buffered channel. It makes parallel requests to three mirror sites. It sends their responses over a buffered channel, then receives and returns only the first response, which is the quickest one to arrive. Thus `mirroredQuery` returns a result even before the two slower servers have responded. (It's quite normal for several goroutines to send values to the same channel concurrently, as in this example, or to receive from the same channel.)

```go
func mirroredQuery() string {
	responses := make(chan string, 3)
	go func() { responses <- request("asia.gopl.io") }()
	go func() { responses <- request("europe.gopl.io") }()
	go func() { responses <- request("americas.gopl.io") }()
	return <-responses // return the quickest response
}

func request(hostname string) (response string) { /* ... */ }
```

If we had used an unbuffered channel in the above example, the two slower goroutines would have gotten stuck trying to send their responses on a channel from which no goroutine will ever receive. This situation, called a *goroutine leak*, would be a bug. <u>Unlike garbage variables, leaked goroutines are not automatically collected, so it is important to make sure that goroutines terminate themselves when no longer needed.</u>

The choice between unbuffered and buffered channels, and the choice of a buffered channel's capacity, may both affect the correctness of a program.

* Unbuffered channels give stronger synchronization guarantees because every send operation is synchronized with its corresponding receive
* With buffered channels, the send and receive operations are decoupled.

When we know an upper bound on the number of values that will be sent on a channel, it's not unusual to create a buffered channel of that size and perform all the sends before the first value is received. Failure to allocate sufficient buffer capacity would cause the program to deadlock.

##### **Packaging cake example** *

Channel buffering may also affect program performance. Imagine three cooks in a cake shop, one baking, one icing, and one inscribing each cake before passing it on to the next cook in the assembly line:

* In a kitchen with little space, each cook that has finished a cake must wait for the next cook to become ready to accept it. This is analogous to communication over an unbuffered channel.
* If there is space for one cake between each cook, a cook may place a finished cake there and immediately start work on the next. This is analogous to a buffered channel with capacity 1.
    * As long as the cooks work at about the same rate on average, most of these handovers proceed quickly, smoothing out transient differences in their respective rates.
    * More space between cooks (larger buffers) can smooth out bigger transient variations in their rates without stalling the assembly line, such as happens when one cook takes a short break, then later rushes to catch up.

On the other hand, a buffer provides no benefit in either of the following case:

* When an earlier stage of the assembly line is consistently faster than the following stage, the buffer between them will spend most of its time full.
* When a later stage is faster, the buffer will usually be empty.

If the second stage is more elaborate, a single cook may not be able to keep up with the supply from the first cook or meet the demand from the third. To solve the problem, we could hire another cook to help the second, performing the same task but working independently. This is analogous to creating another goroutine communicating over the same channels.

The [gopl.io/ch8/cake](https://github.com/shichao-an/gopl.io/blob/master/ch8/cake/cake.go) package simulates this cake shop, with several parameters.

### Looping in Parallel

This section explores some common concurrency patterns for executing all the iterations of a loop in parallel. The following examples consider the problem of producing thumbnail-size images from a set of full-size ones. The [gopl.io/ch8/thumbnail](https://github.com/shichao-an/gopl.io/blob/master/ch8/thumbnail/thumbnail.go) package provides an `ImageFile` function that can scale a single image.

The program below loops over a list of image file names and produces a thumbnail for each one:

<small>[gopl.io/ch8/thumbnail/thumbnail_test.go](https://github.com/shichao-an/gopl.io/blob/master/ch8/thumbnail/thumbnail_test.go)</small>

```go
// makeThumbnails makes thumbnails of the specified files.
func makeThumbnails(filenames []string) {
	for _, f := range filenames {
		if _, err := thumbnail.ImageFile(f); err != nil {
			log.Println(err)
		}
	}
}
```

The order in which we process the files doesn't matter, since each scaling operation is independent of all the others. Problems like this that consist entirely of subproblems that are completely independent of each other are described as [*embarrassingly parallel*](https://en.wikipedia.org/wiki/Embarrassingly_parallel). Embarrassingly parallel problems are the easiest kind to implement concurrently and enjoy performance that scales linearly with the amount of parallelism.

The following first attempt at a concurrent version just adds a `go` keyword. Let's ignore errors for now and address them later.

```go
// NOTE: incorrect!
func makeThumbnails2(filenames []string) {
	for _, f := range filenames {
		go thumbnail.ImageFile(f) // NOTE: ignoring errors
	}
}
```

This version runs too fast, since it takes less time than the original, even when the slice of file names contains only a single element. This is because `makeThumbnails` returns before it has finished doing what it was supposed to do. It starts all the goroutines, one per file name, but doesn't wait for them to finish.

There is no direct way to wait until a goroutine has finished, but we can change the inner goroutine to report its completion to the outer goroutine by sending an event on a shared channel. Since we know that there are exactly `len(filenames)` inner goroutines, the outer goroutine need only count that many events before it returns:

```go
// makeThumbnails3 makes thumbnails of the specified files in parallel.
func makeThumbnails3(filenames []string) {
	ch := make(chan struct{})
	for _, f := range filenames {
		go func(f string) {
			thumbnail.ImageFile(f) // NOTE: ignoring errors
			ch <- struct{}{}
		}(f)
	}

	// Wait for goroutines to complete.
	for range filenames {
		<-ch
	}
}
```

Notice that we passed the value of `f` as an explicit argument to the literal function instead of using the declaration of `f` from the enclosing for loop (as shown below):

```go
for _, f := range filenames {
	go func() {
		thumbnail.ImageFile(f) // NOTE: incorrect!
		// ...
	}()
}
```

Recall the problem of loop variable capture inside an anonymous function, described in [Section 5.6.1](ch5.md#caveat-capturing-iteration-variables). In the above code, the single variable `f` is shared by all the anonymous function values and updated by successive loop iterations. By the time the new goroutines start executing the literal function, the `for` loop may have updated `f` and started another iteration or finished entirely, so when these goroutines read the value of `f`, they all observe it to have the value of the final element of the slice. By adding an explicit parameter, we ensure that we use the value of `f` that is current when the go statement is executed.

