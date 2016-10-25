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

### Mutual Exclusion: [`sync.Mutex`](https://golang.org/pkg/sync/#Mutex)

[Section 8.6](#example-concurrent-web-crawler) uses a buffered channel as a *counting semaphore* to ensure that no more than 20 goroutines made simultaneous HTTP requests. With the same idea, we can use a channel of capacity 1 to ensure that at most one goroutine accesses a shared variable at a time. A semaphore that counts only to 1 is called a [*binary semaphore*](https://en.wikipedia.org/wiki/Semaphore_(programming)).

<small>[gopl.io/ch9/bank2/bank.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/bank2/bank.go)</small>

```go
var (
	sema    = make(chan struct{}, 1) // a binary semaphore guarding balance
	balance int
)

func Deposit(amount int) {
	sema <- struct{}{} // acquire token
	balance = balance + amount
	<-sema // release token
}

func Balance() int {
	sema <- struct{}{} // acquire token
	b := balance
	<-sema // release token
	return b
}
```

This pattern of [mutual exclusion](https://en.wikipedia.org/wiki/Mutual_exclusion) is so useful that it is supported directly by the [`Mutex`](https://golang.org/pkg/sync/#Mutex) type from the [`sync`](https://golang.org/pkg/sync/) package. Its `Lock` method acquires the token (called a *lock*) and its `Unlock` method releases it:

<small>[gopl.io/ch9/bank3/bank.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/bank3/bank.go)</small>

```go
import "sync"

var (
	mu      sync.Mutex // guards balance
	balance int
)

func Deposit(amount int) {
	mu.Lock()
	balance = balance + amount
	mu.Unlock()
}

func Balance() int {
	mu.Lock()
	b := balance
	mu.Unlock()
	return b
}
```

Each time a goroutine accesses `balance`, it must call the mutex's `Lock` method to acquire an exclusive lock. If some other goroutine has acquired the lock, this operation will block until the other goroutine calls `Unlock` and the lock becomes available again. The mutex *guards* the shared variables. <u>By convention, the variables guarded by a mutex are declared immediately after the declaration of the mutex itself.</u> If you deviate from this, be sure to document it.

The region of code between `Lock` and `Unlock` in which a goroutine is free to read and modify the shared variables is called a [*critical section*](https://en.wikipedia.org/wiki/Critical_section). The lock holder's call to `Unlock` happens before any other goroutine can acquire the lock for itself. It is essential that the goroutine release the lock once it is finished, on all paths through the function, including error paths.

The bank program above exemplifies a common concurrency pattern:

* A set of exported functions encapsulates one or more variables so that the only way to access the variables is through these functions (or methods, for the variables of an object).
* Each function acquires a mutex lock at the beginning and releases it at the end, thereby ensuring that the shared variables are not accessed concurrently.

This arrangement of functions, mutex lock, and variables is called a [*monitor*](https://en.wikipedia.org/wiki/Monitor_(synchronization)). This older use of the word "monitor" inspired the term "monitor goroutine". Both uses share the meaning of a broker that ensures variables are accessed sequentially.

In more complex critical sections, especially those in which errors must be dealt with by returning early, it can be hard to tell that calls to `Lock` and `Unlock` are strictly paired on all paths. Go's `defer` statement is useful by deferring a call to `Unlock`, and the critical section implicitly extends to the end of the current function.

```go
func Balance() int {
	mu.Lock()
	defer mu.Unlock()
	return balance
}
```

In the example above:

* The `Unlock` executes after the `return` statement has read the value of `balance`, so the `Balance` function is concurrency-safe. Also, the local variable `b` is no longer needed.
* Furthermore, a deferred `Unlock` will run even if the critical section panics, which may be important in programs that make use of `recover` ([Section 5.10](ch5.md#recover)). A `defer` is marginally more expensive than an explicit call to `Unlock`, but not enough to justify less clear code. Concurrent programs always favor clarity and resist premature optimization. Where possible, use `defer` and extend critical sections to the end of a function.

In the `Withdraw` function below:

* On success, it reduces the balance by the specified amount and returns `true`.
* If the account holds insufficient funds for the transaction, `Withdraw` restores the balance and returns `false`.

```go
// NOTE: not atomic!
func Withdraw(amount int) bool {
	Deposit(-amount)
	if Balance() < 0 {
		Deposit(amount)
		return false // insufficient funds
	}
	return true
}
```

This function eventually gives the correct result, but it has a side effect. When an excessive withdrawal is attempted, the balance transiently dips below zero. This may cause a concurrent withdrawal for a modest sum to be spuriously rejected. So if Bob tries to buy a sports car, Alice can't pay for her morning coffee.

The problem is that `Withdraw` is not [*atomic*](https://en.wikipedia.org/wiki/Linearizability): it consists of a sequence of three separate operations, each of which acquires and then releases the mutex lock, but nothing locks the whole sequence.

Ideally, `Withdraw` should acquire the mutex lock once around the whole operation. However, this attempt won't work:

```go
// NOTE: incorrect!
func Withdraw(amount int) bool {
	mu.Lock()
	defer mu.Unlock()
	Deposit(-amount)
	if Balance() < 0 {
		Deposit(amount)
		return false // insufficient funds
	}
	return true
}
```

`Deposit` tries to acquire the mutex lock a second time by calling `mu.Lock()`, but because mutex locks are not [*re-entrant*](https://en.wikipedia.org/wiki/Reentrancy_(computing)), it's not possible to lock a mutex that's already locked. This leads to a deadlock where nothing can proceed, and `Withdraw` blocks forever.

There is a good reason Go's mutexes are not re-entrant. The purpose of a mutex is to ensure that certain invariants of the shared variables are maintained at critical points during program execution. One of the invariants is "no goroutine is accessing the shared variables", but there may be additional invariants specific to the data structures that the mutex guards. When a goroutine acquires a mutex lock, it may assume that the invariants hold. While it holds the lock, it may update the shared variables so that the invariants are temporarily violated. However, when it releases the lock, it must guarantee that order has been restored and the invariants hold once again. Although a re-entrant mutex would ensure that no other goroutines are accessing the shared variables, it cannot protect the additional invariants of those variables.

A common solution is to divide a function such as `Deposit` into two:

* An unexported function, `deposit`, which assumes the lock is already held and does the real work
* An exported function `Deposit` that acquires the lock before calling `deposit`

The rewritten `Withdraw` in terms of `deposit` is like this:

```go
func Withdraw(amount int) bool {
	mu.Lock()
	defer mu.Unlock()
	deposit(-amount)
	if balance < 0 {
		deposit(amount)
		return false // insufficient funds
	}
	return true
}

func Deposit(amount int) {
	mu.Lock()
	defer mu.Unlock()
	deposit(amount)
}

func Balance() int {
	mu.Lock()
	defer mu.Unlock()
	return balance
}

// This function requires that the lock be held.
func deposit(amount int) { balance += amount }
```

Encapsulation ([Section 6.6](ch6.md#encapsulation)), by reducing unexpected interactions in a program, helps us maintain data structure invariants. For the same reason, encapsulation also helps us maintain concurrency invariants. <u>When you use a mutex, make sure that both it and the variables it guards are not exported, whether they are package-level variables or the fields of a struct.</u>

### Read/Write Mutexes: [`sync.RWMutex`](https://golang.org/pkg/sync/#RWMutex)

Since the `Balance` function only needs to read the state of the variable, it would actually be safe for multiple `Balance` calls to run concurrently, as long as no `Deposit` or `Withdraw` call is running. In this scenario we need a special kind of lock that allows read-only operations to proceed in parallel with each other, but write operations to have fully exclusive access. This lock is called a [*multiple readers, single writer*](https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock) lock, which is provided by `sync.RWMutex` in Go:

```go
var mu sync.RWMutex
var balance int

func Balance() int {
	mu.RLock() // readers lock
	defer mu.RUnlock()
	return balance
}
```

* The `Balance` function now calls the `RLock` and `RUnlock` methods to acquire and release a *reader* or *shared* lock.
* The `Deposit` function, which is unchanged, calls the `mu.Lock` and `mu.Unlock` methods to acquire and release a *writer* or *exclusive* lock.

`RLock` can be used only if there are no writes to shared variables in the critical section. In general, we should not assume that logically read-only functions or methods don't also update some variables. For example, a method that appears to be a simple accessor might also increment an internal usage counter, or update a cache so that repeat calls are faster. If in doubt, use an exclusive `Lock`.

It's only profitable to use an `RWMutex` when most of the goroutines that acquire the lock are readers, and the lock is under contention, that is, goroutines routinely have to wait to acquire it. An `RWMutex` requires more complex internal bookkeeping, making it slower than a regular mutex for uncontended locks.

### Memory Synchronization

From previous examples, it is seen that the `Balance` method needs mutual exclusion, either channel-based or mutex-based, even if it consists only of a single operation (unlike `Deposit` where there is no danger of another goroutine executing "in the middle" of it). There are two reasons we need a mutex:

1. It's equally important that `Balance` not execute in the middle of some other operation like `Withdraw`.
2. Synchronization is about more than just the order of execution of multiple goroutines; synchronization also affects memory.

In a modern computer there may be dozens of processors, each with its own local cache of the main memory. For efficiency, writes to memory are buffered within each processor and flushed out to main memory only when necessary. They may even be committed to main memory in a different order than they were written by the writing goroutine. <u>Synchronization primitives like channel communications and mutex operations cause the processor to flush out and commit all its accumulated writes so that the effects of goroutine execution up to that point are guaranteed to be visible to goroutines running on other processors.</u>

Consider the possible outputs of the following code:

```go
var x, y int
go func() {
	x = 1                   // A1
	fmt.Print("y:", y, " ") // A2
}()

go func() {
	y = 1                   // B1
	fmt.Print("x:", x, " ") // B2
}()
```

Since these two goroutines are concurrent and access shared variables without mutual exclusion, there is a data race, so the program is not deterministic. We might expect it to print any one of these four results, which correspond to intuitive interleavings of the labeled statements of the program:

```text
y:0 x:1
x:0 y:1
x:1 y:1
y:1 x:1
```

The fourth line above could be explained by the sequence `A1,B1,A2,B2` or by `B1,A1,A2,B2`. However, the following two outcomes might also happen, depending on the compiler, CPU, and many other factors:

```text
x:0 y:0
y:0 x:0
```

Within a single goroutine, the effects of each statement are guaranteed to occur in the order of execution; goroutines are [*sequentially consistent*](https://en.wikipedia.org/wiki/Sequential_consistency). But in the absence of explicit synchronization using a channel or mutex, there is no guarantee that events are seen in the same order by all goroutines. Although goroutine *A* must observe the effect of the write `x = 1` before it reads the value of `y`, it does not necessarily observe the write to `y` done by goroutine *B*, so A may print a *stale* value of `y`.

It is tempting to try to understand concurrency as if it corresponds to some interleaving of the statements of each goroutine, but as the example above shows, this is not how a modern compiler or CPU works:

* <u>Because the assignment and the `Print` refer to different variables, a compiler may conclude that the order of the two statements cannot affect the result, and swap them.</u>
* If the two goroutines execute on different CPUs, each with its own cache, writes by one goroutine are not visible to the other goroutine's `Print` until the caches are synchronized with main memory.

All these concurrency problems can be avoided by the consistent use of simple, established patterns. Where possible, confine variables to a single goroutine; for all other variables, use mutual exclusion.

### Doubts and Solution

#### Verbatim

##### **p265 on mutexes**

> Although a re-entrant mutex would ensure that no other goroutines are accessing the shared variables, it cannot protect the additional invariants of those variables.

<span class="text-danger">Question</span>: What does it mean?
