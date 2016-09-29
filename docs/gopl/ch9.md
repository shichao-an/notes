### **Chapter 9. Concurrency with Shared Variables**

The previous chapter presented several programs that use goroutines and channels to
express concurrency in a direct and natural way.

This chapter looks at the mechanics of concurrency, and in particular discusses:

* Some of the problems associated with sharing variables among multiple goroutines.
* The analytical techniques for recognizing those problems.
* The patterns for solving them.
* Some of the technical differences between goroutines and operating system threads.

### Race Conditions

In a sequential program, that is, a program with only one goroutine, the steps of the program happen in the familiar execution order determined by the program logic. For instance, in a sequence of statements, the first one happens before the second one, and so on.

In a program with two or more goroutines, the steps within each goroutine happen in the familiar order, but in general we don't know whether an event *x* in one goroutine happens before an event *y* in another goroutine, or happens after it, or is simultaneous with it. When we cannot confidently say that one event *happens before* the other, then the events *x* and *y* are *concurrent*.

Consider a function that works correctly in a sequential program. That function is *concurrency-safe* if it continues to work correctly even when called concurrently (called from two or more goroutines with no additional synchronization).

This notion can be generalized to a set of collaborating functions, such as the methods and operations of a particular type. A type is concurrency-safe if all its accessible methods and operations are concurrency-safe.

We can make a program concurrency-safe without making every concrete type in that program concurrency-safe. Indeed, concurrency-safe types are the exception rather than the rule, so you should access a variable concurrently only if the documentation for its type says that this is safe. We avoid concurrent access to most variables by either of the following:

* Confining them to a single goroutine
* Maintaining a higher-level invariant of mutual exclusion

In contrast, exported package-level functions are generally expected to be concurrency-safe. Since package-level variables cannot be confined to a single goroutine, functions that modify them must enforce mutual exclusion.

There are many reasons a function might not work when called concurrently, including:

* Deadlock
* Livelock
* Resource starvation.

This chapter focuse on the most important one, the [**race condition**](https://en.wikipedia.org/wiki/Race_condition).

A race condition is a situation in which the program does not give the correct result for some interleavings of the operations of multiple goroutines. Race conditions are pernicious because they may remain latent in a program and appear infrequently, perhaps only under heavy load or when using certain compilers, platforms, or architectures. This makes them hard to reproduce and diagnose.

The following example explains the seriousness of race conditions through the metaphor of financial loss:

```go
// Package bank implements a bank with only one account.
package bank

var balance int

func Deposit(amount int) { balance = balance + amount }

func Balance() int { return balance }
```

As a sequential program, any sequence of calls to `Deposit` and `Balance` will give the right answer, that is, `Balance` will report the sum of all amounts previously deposited. However, if we call these functions not in a sequence but concurrently, `Balance` is no longer guaranteed to give the right answer. Consider the following two goroutines, which represent two transactions on a joint bank account:

```go
// Alice:
go func() {
	bank.Deposit(200) // A1
	fmt.Println("=", bank.Balance()) // A2
}()

// Bob:
go bank.Deposit(100) // B
```

Alice deposits $200, then checks her balance, while Bob deposits $100. Since the steps `A1` and `A2` occur concurrently with `B`, we cannot predict the order in which they happen.

Intuitively, it might seem that there are only three possible orderings:

1. "Alice first"
2. "Bob first"
3. "Alice/Bob/Alice"

[p259]

In all cases the final balance is $300. The only variation is whether Alice's balance slip includes Bob's transaction or not, but the customers are satisfied either way.

However, this intuition is wrong. There is a fourth possible outcome, in which Bob's deposit occurs in the middle of Alice's deposit, after the balance has been read (`balance + amount`) but before it has been updated (`balance = ...`), causing Bob's transaction to disappear. This is because Alice's deposit operation `A1` is really a sequence of two operations, a read and a write; call them `A1r` and `A1w`. The following is the problematic interleaving:

After `A1r`, the expression `balance + amount` evaluates to 200, so this is the value written during `A1w`, despite the intervening deposit.

This program contains a particular kind of race condition called a [*data race*](https://en.wikipedia.org/wiki/Race_condition#Software). The definition of it is:

<u>A data race occurs whenever two goroutines access the same variable concurrently and at least one of the accesses is a write.</u>

Things get even messier if the data race involves a variable of a type that is larger than a single machine word, such as an interface, a string, or a slice. The following code updates `x` concurrently to two slices of different lengths:

```go
var x []int
go func() { x = make([]int, 10) }()
go func() { x = make([]int, 1000000) }()
x[999999] = 1 // NOTE: undefined behavior; memory corruption possible!
```

The value of `x` in the final statement is not defined. It could be any of the following:

* nil
* A slice of length 10
* A slice of length 1,000,000.

Recall that there are three parts to a slice: the pointer, the length, and the capacity. If the pointer comes from the first call to `make` and the length comes from the second, `x` would be a slice whose nominal length is 1,000,000 but whose underlying array has only 10 elements. In this case, storing to element 999,999 would clobber an arbitrary faraway memory location, with consequences that are impossible to predict and hard to debug and localize. This semantic minefield is called [*undefined behavior*](https://en.wikipedia.org/wiki/Undefined_behavior) and is well known to C programmers; fortunately it is rarely as troublesome in Go as in C.

Even the notion that a concurrent program is an interleaving of several sequential programs is a false intuition. [Section 9.4](#memory-synchronization) will show that data races may have even stranger outcomes. Many programmers will occasionally offer justifications for known data races in their programs. The absence of problems on a given compiler and platform may give them false confidence. A good rule of thumb is that there is no such thing as a *benign data race*. So how do we avoid data races in our programs?

#### Avoiding a data race *

There are three ways to avoid a data race.

##### **Avoid writing the variable** *

The first way is not to write the variable. Consider the map below, which is lazily populated as each key is requested for the first time. If `Icon` is called sequentially, the program works fine, but if `Icon` is called concurrently, there is a data race accessing the map.

```go
var icons = make(map[string]image.Image)

func loadIcon(name string) image.Image

// NOTE: not concurrency-safe!
func Icon(name string) image.Image {
	icon, ok := icons[name]
	if !ok {
	icon = loadIcon(name)
	icons[name] = icon
	}
	return icon
}
```

If instead we initialize the map with all necessary entries before creating additional goroutines and never modify it again, then any number of goroutines may safely call `Icon` concurrently since each only reads the map.

```go
var icons = map[string]image.Image{
	"spades.png": loadIcon("spades.png"),
	"hearts.png": loadIcon("hearts.png"),
	"diamonds.png": loadIcon("diamonds.png"),
	"clubs.png": loadIcon("clubs.png"),
}

// Concurrency-safe.
func Icon(name string) image.Image { return icons[name] }
```

In the example above, the `icons` variable is assigned during package initialization, which happens before the program's `main` function starts running. Once initialized, `icons` is never modified. Data structures that are never modified or are immutable are inherently concurrency-safe and need no synchronization. This approach can be used if updates are essential.

##### **Avoid accessing the variable from multiple goroutines** *

The second way to avoid a data race is to avoid accessing the variable from multiple goroutines. This is the approach taken by many of the programs in the previous chapter, for example:

* The main goroutine in the concurrent web crawler ([Section 8.6](ch8.md#example-concurrent-web-crawler)) is the sole goroutine that accesses the `seen` map.
* The `broadcaster` goroutine in the chat server ([Section 8.10](ch8.md#example-chat-server)) is the only goroutine that accesses the `clients` map.

These variables are *confined* to a single goroutine.

Since other goroutines cannot access the variable directly, they must use a channel to send the confining goroutine a request to query or update the variable. This is what is meant by the Go mantra:

"Do not communicate by sharing memory; instead, share memory by communicating."

A goroutine that brokers access to a confined variable using channel requests is called a *monitor goroutine* for that variable. For example, the `broadcaster` goroutine monitors access to the `clients` map.

The following is the `bank` example rewritten with the `balance` variable confined to a monitor goroutine called `teller`:

<small>[gopl.io/ch9/bank1/bank.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/bank1/bank.go)</small>

```go
// Package bank provides a concurrency-safe bank with one account.
package bank

var deposits = make(chan int) // send amount to deposit
var balances = make(chan int) // receive balance

func Deposit(amount int) { deposits <- amount }
func Balance() int       { return <-balances }

func teller() {
	var balance int // balance is confined to teller goroutine
	for {
		select {
		case amount := <-deposits:
			balance += amount
		case balances <- balance:
		}
	}
}

func init() {
	go teller() // start the monitor goroutine
}
```

Even when a variable cannot be confined to a single goroutine for its entire lifetime, confinement may still be a solution to the problem of concurrent access. For example, it's common to share a variable between goroutines in a pipeline by passing its address from one stage to the next over a channel. If each stage of the pipeline refrains from accessing the variable after sending it to the next stage, then all accesses to the variable are sequential. In effect, the variable is confined to one stage of the pipeline, then confined to the next, and so on. This discipline is sometimes called *serial confinement*.

In the example below, `Cakes` are serially confined, first to the `baker` goroutine, then to the `icer` goroutine:

```go
type Cake struct{ state string }

func baker(cooked chan<- *Cake) {
	for {
		cake := new(Cake)
		cake.state = "cooked"
		cooked <- cake // baker never touches this cake again
	}
}

func icer(iced chan<- *Cake, cooked <-chan *Cake) {
	for cake := range cooked {
		cake.state = "iced"
		iced <- cake // icer never touches this cake again
	}
}
```

##### **Allow only one goroutine to access the variable at a time** *

The third way to avoid a data race is to allow many goroutines to access the variable, but only one at a time. This approach is known as [*mutual exclusion*](https://en.wikipedia.org/wiki/Mutual_exclusion) and is the subject of the next section.
