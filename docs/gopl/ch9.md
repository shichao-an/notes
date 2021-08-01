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

This chapter focuses on the most important one, the [**race condition**](https://en.wikipedia.org/wiki/Race_condition).

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

### Lazy Initialization: `sync.Once`

Initializing a variable up front increases the start-up latency of a program and is unnecessary if execution doesn't always reach the part of the program that uses that variable. Therefore, it is good practice to defer an expensive initialization step until it is needed. Consider the `icons` variable discussed [earlier in the chapter](#avoiding-a-data-race):

```go
var icons map[string]image.Image
```

The following version of `Icon` uses [*lazy initialization*](https://en.wikipedia.org/wiki/Lazy_initialization):

```go
func loadIcons() {
	icons = map[string]image.Image{
		"spades.png": loadIcon("spades.png"),
		"hearts.png": loadIcon("hearts.png"),
		"diamonds.png": loadIcon("diamonds.png"),
		"clubs.png": loadIcon("clubs.png"),
	}
}

// NOTE: not concurrency-safe!
func Icon(name string) image.Image {
	if icons == nil {
		loadIcons() // one-time initialization
	}
	return icons[name]
}
```

For a variable accessed by only a single goroutine, we can use the pattern above, but this pattern is not safe if `Icon` is called concurrently. Like the bank's original `Deposit` function, `Icon` consists of multiple steps: it tests whether `icons` is nil, then it loads the icons, then it updates icons to a non-nil value.

Intuition might suggest that the worst possible outcome of the race condition above is that the `loadIcons` function is called several times. While the first goroutine is busy loading the icons, another goroutine entering `Icon` would find the variable still equal to nil, and would also call `loadIcons`. However, this intuition is also wrong. As discussed in [Section 9.4](#memory-synchronization), in the absence of explicit synchronization, the compiler and CPU are free to reorder accesses to memory in any number of ways, so long as the behavior of each goroutine is sequentially consistent. One possible reordering of the statements of `loadIcons` is shown below. It stores the empty map in the `icons` variable before populating it:

```go
func loadIcons() {
	icons = make(map[string]image.Image)
	icons["spades.png"] = loadIcon("spades.png")
	icons["hearts.png"] = loadIcon("hearts.png")
	icons["diamonds.png"] = loadIcon("diamonds.png")
	icons["clubs.png"] = loadIcon("clubs.png")
}
```

Consequently, a goroutine finding `icons` to be non-nil may not assume that the initialization of the variable is complete.

The simplest correct way to ensure that all goroutines observe the effects of `loadIcons` is to synchronize them using a mutex:

```go
var mu sync.Mutex // guards icons
var icons map[string]image.Image

// Concurrency-safe.
func Icon(name string) image.Image {
	mu.Lock()
	defer mu.Unlock()
	if icons == nil {
		loadIcons()
	}
	return icons[name]
}
```

However, the cost of enforcing mutually exclusive access to icons is that two goroutines cannot access the variable concurrently, even once the variable has been safely initialized and will never be modified again. This suggests a multiple-readers lock:

```go
var mu sync.RWMutex // guards icons
var icons map[string]image.Image

// Concurrency-safe.
func Icon(name string) image.Image {
	mu.RLock()
	if icons != nil {
		icon := icons[name]
		mu.RUnlock()
		return icon
	}
	mu.RUnlock()

	// acquire an exclusive lock
	mu.Lock()
	if icons == nil { // NOTE: must recheck for nil
		loadIcons()
	}
	icon := icons[name]
	mu.Unlock()
	return icon
}
```

There are now two critical sections:

1. The goroutine first acquires a reader lock, consults the map, then releases the lock.
2. If an entry was found, it is returned. If no entry was found, the goroutine acquires a writer lock. There is no way to upgrade a shared lock to an exclusive one without first releasing the shared lock, so we must recheck the `icons` variable in case another goroutine already initialized it in the interim.

The pattern above has greater concurrency but is complex and thus error-prone. Fortunately, the `sync` package provides a specialized solution to the problem of one-time initialization: [`sync.Once`](https://golang.org/pkg/sync/#Once). Conceptually, a `Once` consists of a mutex and a boolean variable that records whether initialization has taken place; the mutex guards both the boolean and the client's data structures. The sole method, `Do`, accepts the initialization function as its argument. The following `Icon` function uses `Once`:

```go
var loadIconsOnce sync.Once
var icons map[string]image.Image

// Concurrency-safe.
func Icon(name string) image.Image {
	loadIconsOnce.Do(loadIcons)
	return icons[name]
}
```

Each call to `Do(loadIcons)` locks the mutex and checks the boolean variable. In the first call, in which the variable is false, `Do` calls `loadIcons` and sets the variable to true. Subsequent calls do nothing, but the mutex synchronization ensures that the effects of `loadIcons` on memory (specifically, `icons`) become visible to all goroutines. Using `sync.Once` in this way, we can avoid sharing variables with other goroutines until they have been properly constructed.

### The Race Detector

The Go runtime and toolchain are equipped with a sophisticated and easy-to-use dynamic analysis tool, the [**race detector**](https://golang.org/doc/articles/race_detector.html). Add the `-race` flag to your `go build`, `go run`, or `go test` command. This causes the compiler to build a modified version of your application or test with additional instrumentation that effectively records all accesses to shared variables that occurred during execution, along with the identity of the goroutine that read or wrote the variable. In addition, the modified program records all synchronization events, such as `go` statements, channel operations, and calls to `(*sync.Mutex).Lock`, `(*sync.WaitGroup).Wait`, and so on. The complete set of synchronization events is specified by the [*The Go Memory Model*](https://golang.org/ref/mem) document that accompanies the language specification.

The race detector studies this stream of events, looking for cases in which <u>one goroutine reads or writes a shared variable that was most recently written by a different goroutine without an intervening synchronization operation.</u> This indicates a concurrent access to the shared variable, and thus a data race. The tool prints a report that includes the identity of the variable, and the stacks of active function calls in the reading goroutine and the writing goroutine. This is usually sufficient to pinpoint the problem. [Section 9.7](#example-concurrent-non-blocking-cache) contains an example of race detector.

The race detector reports all data races that were actually executed. However, it can only detect race conditions that occur during a run; it cannot prove that none will ever occur. For best results, make sure that your tests exercise your packages using concurrency. Due to extra bookkeeping, a program built with race detection needs more time and memory to run, but the overhead is tolerable even for many production jobs. For infrequently occurring race conditions, making the race detector do its job can save time of debugging.

### Example: Concurrent Non-Blocking Cache

This section talks about building a *concurrent non-blocking cache*, an abstraction that solves a problem in real-world concurrent programs but is not well addressed by existing libraries. This is the problem of [*memoizing*](https://en.wikipedia.org/wiki/Memoization) a function, which means caching the result of a function so that it need be computed only once.

The solution will be concurrency-safe and will avoid the contention associated with designs based on a single lock for the whole cache. It'll use the `httpGetBody` function below as an example of the function to memoize. It makes an HTTP GET request and reads the request body. Calls to this function are relatively expensive, so we want to avoid repeating them unnecessarily.

```go
func httpGetBody(url string) (interface{}, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return ioutil.ReadAll(resp.Body)
}
```

Notice the final line. `ReadAll` returns two results, a `[]byte` and an `error`, but since these are assignable to the declared result types of `httpGetBody`, `interface{}` and `error` respectively, we can return the result of the call without further ado. We chose this return type for `httpGetBody` so that it conforms to the type of functions that our cache is designed to memoize.

<small>[gopl.io/ch9/memo1/memo.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/memo1/memo.go)</small>

```go
// Package memo provides a concurrency-unsafe
// memoization of a function of type Func.
package memo

// A Memo caches the results of calling a Func.
type Memo struct {
	f     Func
	cache map[string]result
}

// Func is the type of the function to memoize.
type Func func(key string) (interface{}, error)

type result struct {
	value interface{}
	err   error
}

func New(f Func) *Memo {
	return &Memo{f: f, cache: make(map[string]result)}
}

// NOTE: not concurrency-safe!
func (memo *Memo) Get(key string) (interface{}, error) {
	res, ok := memo.cache[key]
	if !ok {
		res.value, res.err = memo.f(key)
		memo.cache[key] = res
	}
	return res.value, res.err
}
```

A `Memo` instance holds the function `f` to memoize, of type `Func`, and the `cache`, which is a mapping from strings to results. Each result is simply the pair of results returned by a call to `f`, a value and an error.

Below is an example of how to use `Memo`. For each element in a stream of incoming URLs, we call `Get`, logging the latency of the call and the amount of data it returns:

```go
m := memo.New(httpGetBody)
for url := range incomingURLs() {
	start := time.Now()
	value, err := m.Get(url)
	if err != nil {
	log.Print(err)
	}
	fmt.Printf("%s, %s, %d bytes\n",
		url, time.Since(start), len(value.([]byte)))
}
```

We can use the [`testing`](https://golang.org/pkg/testing/) package (the topic of [Chapter 11](ch11.md)) to systematically investigate the effect of memoization. In the test output below,the URL stream contains duplicates; that although the first call to `(*Memo).Get` for each URL takes hundreds of milliseconds, the second request returns the same amount of data in under a millisecond.

```text
$ go test -v gopl.io/ch9/memo1
=== RUN Test
https://golang.org, 175.026418ms, 7537 bytes
https://godoc.org, 172.686825ms, 6878 bytes
https://play.golang.org, 115.762377ms, 5767 bytes
http://gopl.io, 749.887242ms, 2856 bytes
https://golang.org, 721ns, 7537 bytes
https://godoc.org, 152ns, 6878 bytes
https://play.golang.org, 205ns, 5767 bytes
http://gopl.io, 326ns, 2856 bytes
--- PASS: Test (1.21s)
PASS
ok gopl.io/ch9/memo1 1.257s
```

This test executes all calls to `Get` sequentially.

Since HTTP requests are a great opportunity for parallelism, the following test makes all requests concurrently. <u>The test uses a `sync.WaitGroup` to wait until the last request is complete before returning.</u>

<small>[gopl.io/ch9/memotest/memotest.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/memotest/memotest.go#L84)</small>

```go
m := memo.New(httpGetBody)
var n sync.WaitGroup
for url := range incomingURLs() {
	n.Add(1)
	go func(url string) {
		start := time.Now()
		value, err := m.Get(url)
		if err != nil {
			log.Print(err)
		}
		fmt.Printf("%s, %s, %d bytes\n",
			url, time.Since(start), len(value.([]byte)))
		n.Done()
	}(url)
}
n.Wait()
```

The test runs much faster, but unfortunately it is unlikely to work correctly all the time. We may notice unexpected cache misses, or cache hits that return incorrect values, or even crashes.

The worse thing is that it is likely to work correctly some of the time, so we may not even notice that it has a problem. But if we run it with the `-race` flag, the race detector ([Section 9.6](#the-race-detector)) often prints a report such as this one:

```text
$ go test -run=TestConcurrent -race -v gopl.io/ch9/memo1
=== RUN TestConcurrent
...
WARNING: DATA RACE
Write by goroutine 36:
runtime.mapassign1()
~/go/src/runtime/hashmap.go:411 +0x0
gopl.io/ch9/memo1.(*Memo).Get()
~/gobook2/src/gopl.io/ch9/memo1/memo.go:32 +0x205
...
Previous write by goroutine 35:
runtime.mapassign1()
~/go/src/runtime/hashmap.go:411 +0x0
gopl.io/ch9/memo1.(*Memo).Get()
~/gobook2/src/gopl.io/ch9/memo1/memo.go:32 +0x205
...
Found 1 data race(s)
FAIL gopl.io/ch9/memo1 2.393s
```

The reference to `memo.go:32` tells us that two goroutines have updated the `cache` map without any intervening synchronization. `Get` is not concurrency-safe: it has a data race.

```text
28 func (memo *Memo) Get(key string) (interface{}, error) {
29     res, ok := memo.cache[key]
30     if !ok {
31         res.value, res.err = memo.f(key)
32         memo.cache[key] = res
33     }
34     return res.value, res.err
35 }
```

The simplest way to make the cache concurrency-safe is to use monitor-based synchronization, by adding a mutex to the `Memo`, which acquires the mutex lock at the start of `Get`, and releases it before `Get` returns, so that the two cache operations occur within the critical section:

<small>[gopl.io/ch9/memo2/memo.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/memo2/memo.go)</small>

```go
type Memo struct {
	f     Func
	mu    sync.Mutex // guards cache
	cache map[string]result
}

// Get is concurrency-safe.
func (memo *Memo) Get(key string) (value interface{}, err error) {
	memo.mu.Lock()
	res, ok := memo.cache[key]
	if !ok {
		res.value, res.err = memo.f(key)
		memo.cache[key] = res
	}
	memo.mu.Unlock()
	return res.value, res.err
}
```

Now the race detector is silent, even when running the tests concurrently. Unfortunately this change to `Memo` reverses our earlier performance gains. By holding the lock for the duration of each call to `f`, `Get` serializes all the I/O operations we intended to parallelize. What we need is a *non-blocking* cache, one that does not serialize calls to the function it memoizes.

In the following implementation of `Get`, the calling goroutine acquires the lock twice: once for the lookup, and then a second time for the update if the lookup returned nothing. In between, other goroutines are free to use the cache.

<small>[gopl.io/ch9/memo3/memo.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/memo3/memo.go)</small>

```go
func (memo *Memo) Get(key string) (value interface{}, err error) {
	memo.mu.Lock()
	res, ok := memo.cache[key]
	memo.mu.Unlock()
	if !ok {
		res.value, res.err = memo.f(key)

		// Between the two critical sections, several goroutines
		// may race to compute f(key) and update the map.
		memo.mu.Lock()
		memo.cache[key] = res
		memo.mu.Unlock()
	}
	return res.value, res.err
}
```

The performance improves again, but now we notice that some URLs are being fetched twice.  This happens when two or more goroutines call `Get` for the same URL at about the same time. Both consult the cache, find no value there, and then call the slow function `f`. Then both of them update the map with the result they obtained. One of the results is overwritten by the other.

We need to avoid this redundant work. This feature is sometimes called *duplicate suppression*. In the version of `Memo` below, each map element is a pointer to an entry struct. Each entry contains the memoized result of a call to the function `f`, but it additionally contains a channel called `ready`. Right after the entry's result has been set, this channel will be closed, to *broadcast* ([Section 8.9](ch8.md#cancellation)) to any other goroutines that it is now safe for them to read the result from the `entry`.

<small>[gopl.io/ch9/memo4/memo.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/memo4/memo.go)</small>

```go
type entry struct {
	res   result
	ready chan struct{} // closed when res is ready
}

func New(f Func) *Memo {
	return &Memo{f: f, cache: make(map[string]*entry)}
}

type Memo struct {
	f     Func
	mu    sync.Mutex // guards cache
	cache map[string]*entry
}

func (memo *Memo) Get(key string) (value interface{}, err error) {
	memo.mu.Lock()
	e := memo.cache[key]
	if e == nil {
		// This is the first request for this key.
		// This goroutine becomes responsible for computing
		// the value and broadcasting the ready condition.
		e = &entry{ready: make(chan struct{})}
		memo.cache[key] = e
		memo.mu.Unlock()

		e.res.value, e.res.err = memo.f(key)

		close(e.ready) // broadcast ready condition
	} else {
		// This is a repeat request for this key.
		memo.mu.Unlock()

		<-e.ready // wait for ready condition
	}
	return e.res.value, e.res.err
}
```

A call to `Get` now involves:

* Acquiring the mutex lock that guards the `cache` map
* Looking in the map for a pointer to an existing `entry`
* Allocating and inserting a new `entry` if none was found, then releasing the lock

But there are two cases this time:

* If there was an existing `entry` (in the `else` block), its value is not necessarily ready yet: another goroutine could still be calling the slow function `f`. Thus the calling goroutine must wait for the entry's "ready" condition before it reads the `entry`'s result. <u>It does this by reading a value from the `ready` channel, since this operation blocks until the channel is closed.</u>
* If there was no existing entry (in the `if e == nil` block), then by inserting a new "not ready" entry into the map, the current goroutine becomes responsible for invoking the slow function, updating the entry, and broadcasting the readiness of the new entry to any other goroutines that might (by then) be waiting for it.

Notice that the variables `e.res.value` and `e.res.err` in the `entry` are shared among multiple goroutines. The goroutine that creates the `entry` sets their values, and other goroutines read their values once the "ready" condition has been broadcast. Despite being accessed by multiple goroutines, no mutex lock is necessary. The closing of the `ready` channel happens before any other goroutine receives the broadcast event, so the write to those variables in the first goroutine happens before they are read by subsequent goroutines. There is no data race.

Our concurrent, duplicate-suppressing, non-blocking cache is complete.

The implementation of `Memo` above uses a mutex to guard a map variable that is shared by each goroutine that calls `Get`. It's interesting to contrast this design with an alternative one in which the map variable is confined to a *monitor goroutine* to which callers of `Get` must send a message.

The declarations of `Func`, `result`, and `entry` remain as before. However, the `Memo` type now consists of a channel, `requests`, through which the caller of `Get` communicates with the monitor goroutine. The element type of the channel is a `request`. Using this structure, the caller of `Get` sends the monitor goroutine both the key (the argument to the memoized function), and another channel, `response`, over which the result should be sent back when it becomes available. This channel will carry only a single value.

<small>[gopl.io/ch9/memo5/memo.go](https://github.com/shichao-an/gopl.io/blob/master/ch9/memo5/memo.go)</small>

```go
// A request is a message requesting that the Func be applied to key.
type request struct {
	key      string
	response chan<- result // the client wants a single result
}

type Memo struct{ requests chan request }

// New returns a memoization of f.  Clients must subsequently call Close.
func New(f Func) *Memo {
	memo := &Memo{requests: make(chan request)}
	go memo.server(f)
	return memo
}

func (memo *Memo) Get(key string) (interface{}, error) {
	response := make(chan result)
	memo.requests <- request{key, response}
	res := <-response
	return res.value, res.err
}

func (memo *Memo) Close() { close(memo.requests) }
```

The `Get` method above creates a `response` channel, puts it in the `request`, sends it to the monitor goroutine, then immediately receives from it.

The cache variable is confined to the monitor goroutine `(*Memo).server` shown below. The monitor reads requests in a loop until the `request` channel is closed by the `Close` method. For each request, it consults the cache, creating and inserting a new `entry` if none was found.

```go
func (memo *Memo) server(f Func) {
	cache := make(map[string]*entry)
	for req := range memo.requests {
		e := cache[req.key]
		if e == nil {
			// This is the first request for this key.
			e = &entry{ready: make(chan struct{})}
			cache[req.key] = e
			go e.call(f, req.key) // call f(key)
		}
		go e.deliver(req.response)
	}
}

func (e *entry) call(f Func, key string) {
	// Evaluate the function.
	e.res.value, e.res.err = f(key)
	// Broadcast the ready condition.
	close(e.ready)
}

func (e *entry) deliver(response chan<- result) {
	// Wait for the ready condition.
	<-e.ready
	// Send the result to the client.
	response <- e.res
}
```

Similar to the mutex-based version, the first request for a given key becomes responsible for calling the function `f` on that key, storing the result in the `entry`, and broadcasting the readiness of the `entry` by closing the `ready` channel. This is done by `(*entry).call`.

A subsequent request for the same key finds the existing `entry` in the map, waits for the result to become ready, and sends the result through the `response` channel to the client goroutine that called `Get`. This is done by `(*entry).deliver`.

<u>The `call` and `deliver` methods must be called in their own goroutines to ensure that the monitor goroutine does not stop processing new requests.</u>

This example shows that it's possible to build many concurrent structures using either of the
two approaches without excessive complexity:

* Shared variables and locks
* Communicating sequential processes

It's not always obvious which approach is preferable in a given situation, but it's worth knowing how they correspond. Sometimes switching from one approach to the other can make your code simpler.

### Goroutines and Threads

The [previous chapter](ch8.md) mentioned that the difference between goroutines and operating system (OS) threads could be ignored until later. Although the differences between them are essentially quantitative, a big enough quantitative difference becomes a qualitative one, and so it is with goroutines and threads.

#### Growable Stacks

Each OS thread has a fixed-size block of memory (often as large as 2MB) for its [*stack*](https://en.wikipedia.org/wiki/Call_stack), the work area where it saves the local variables of function calls that are in progress or temporarily suspended while another function is called.

This fixed-size stack is simultaneously too much and too little:

* A 2MB stack would be a huge waste of memory for a little goroutine, such as one that merely waits for a `WaitGroup` then closes a channel.
* It's too small for a Go program that creates hundreds of thousands of goroutines at one time. Yet despite their size, fixed-size stacks are not always big enough for the most complex and deeply recursive of functions.

Changing the fixed size can improve space efficiency and allow more threads to be created, or it can enable more deeply recursive functions, but it cannot do both.

In contrast, a goroutine starts life with a small stack, typically 2KB. A goroutine's stack, like the stack of an OS thread, holds the local variables of active and suspended function calls, but unlike an OS thread, a goroutine’s stack is not fixed; it grows and shrinks as needed. The size limit for a goroutine stack may be as much as 1GB, orders of magnitude larger than a typical fixed-size thread stack, though few goroutines use that much.

#### Goroutine Scheduling

OS threads are scheduled by the OS kernel. Every few milliseconds, a hardware timer interrupts the processor, which causes a kernel function called the *scheduler* to be invoked. This function does the following things:

1. Suspends the currently executing thread and saves its registers in memory.
2. Looks over the list of threads and decides which one should run next
3. Restores that thread's registers from memory, then resumes the execution of that thread.

Because OS threads are scheduled by the kernel, passing control from one thread to another requires a full [context switch](https://en.wikipedia.org/wiki/Context_switch), which does the following things:

* Saving the state of one user thread to memory
* Restoring the state of another thread
* Updating the scheduler's data structures.

This operation is slow, due to its poor locality and the number of memory accesses required, and has historically only gotten worse as the number of CPU cycles required to access memory has increased.

The Go runtime contains its own scheduler that uses a technique known as *m:n scheduling*, because it multiplexes (or schedules) *m* goroutines on *n* OS threads. The job of the Go scheduler is analogous to that of the kernel scheduler, but it is concerned only with the goroutines of a single Go program.

Unlike the operating system's thread scheduler, the Go scheduler is not invoked periodically by a hardware timer, but implicitly by certain Go language constructs. For example, when a goroutine calls `time.Sleep` or blocks in a channel or mutex operation, the scheduler puts it to sleep and runs another goroutine until it is time to wake the first one up. Because it doesn't need a switch to kernel context, rescheduling a goroutine is much cheaper than rescheduling a thread.

#### GOMAXPROCS

The Go scheduler uses a parameter called `GOMAXPROCS` to determine how many OS threads may be actively executing Go code simultaneously. Its default value is the number of CPUs on the machine, so on a machine with 8 CPUs, the scheduler will schedule Go code on up to 8 OS threads at once. `GOMAXPROCS` is the *n* in *m*:*n* scheduling.

* <u>Goroutines that are sleeping or blocked in a communication do not need a thread at all.</u>
* Goroutines that are blocked in I/O or other system calls or are calling non-Go functions, do need an OS thread, but `GOMAXPROCS` need not account for them.

You can explicitly control this parameter using the `GOMAXPROCS` environment variable or the [`runtime.GOMAXPROCS`](https://golang.org/pkg/runtime/#GOMAXPROCS) function.

We can see the effect of `GOMAXPROCS` on the following program, which prints an endless stream of zeros and ones:

```go
for {
	go fmt.Print(0)
	fmt.Print(1)
}
```

```text
$ GOMAXPROCS=1 go run hacker-cliché.go
111111111111111111110000000000000000000011111...
$ GOMAXPROCS=2 go run hacker-cliché.go
010101010101010101011001100101011010010100110...
```

1. In the first run, at most one goroutine was executed at a time. Initially, it was the main goroutine, which prints ones. After a period of time, the Go scheduler put it to sleep and woke up the goroutine that prints zeros, giving it a turn to run on the OS thread.
2. In the second run, there were two OS threads available, so both goroutines ran simultaneously, printing digits at about the same rate.

Note that many factors are involved in goroutine scheduling, and the runtime is constantly evolving, so your results may differ from the ones above.

#### Goroutines Have No Identity

In most operating systems and programming languages that support multithreading, the current thread has a distinct identity that can be easily obtained as an ordinary value, typically an integer or pointer. This makes it easy to build an abstraction called [**thread-local storage**](https://en.wikipedia.org/wiki/Thread-local_storage), which is essentially a global map keyed by thread identity, so that each thread can store and retrieve values independent of other threads.

Goroutines have no notion of identity that is accessible to the programmer. This is by design, since thread-local storage tends to be abused. For example, in a web server implemented in a language with thread-local storage, it's common for many functions to find information about the HTTP request on whose behalf they are currently working by looking in that storage. However, this can lead to an unhealthy "[action at a distance](https://en.wikipedia.org/wiki/Action_at_a_distance_(computer_programming))" in which the behavior of a function is not determined by its arguments alone, but by the identity of the thread in which it runs. Consequently, if the identity of the thread changes (e.g. some worker threads are enlisted to help) the function misbehaves mysteriously.

Go encourages a simpler style of programming in which parameters that affect the behavior of a function are explicit. Not only does this make programs easier to read, but it facilitates us to freely assign subtasks of a given function to many different goroutines without worrying about their identity.

At this point, all the language features needed for writing Go programs have been discussed. The next two chapters will step back to some of the practices and tools that support programming in the large: how to structure a project as a set of packages, and how to obtain, build, test, benchmark, profile, document, and share those packages.

### Doubts and Solution

#### Verbatim

##### **p265 on mutexes**

> Although a re-entrant mutex would ensure that no other goroutines are accessing the shared variables, it cannot protect the additional invariants of those variables.

<span class="text-danger">Question</span>: What does it mean?

##### **p271 in `sync.Once`**

> ... the mutex synchronization ensures that the effects of `loadIcons` on memory (specifically, `icons`) become visible to all goroutines. Using `sync.Once` in this way, we can avoid sharing variables with other goroutines until they have been properly constructed.

<span class="text-danger">Question</span>: What does it mean?
