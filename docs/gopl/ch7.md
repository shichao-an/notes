### **Chapter 7. Interfaces**

Interface types express generalizations or abstractions about the behaviors of other types. By generalizing, interfaces facilitate more flexible and adaptable functions because they are not tied to the details of one particular implementation.

Different from the notion of interfaces in other object-oriented languages, Go's interfaces is distinctive in that they are satisfied implicitly. In other words, there's no need to declare all the interfaces that a given concrete type satisfies; simply possessing the necessary methods is enough. With this design, you are able to create new interfaces that are satisfied by existing concrete types without changing the existing types, which is particularly useful for types defined in packages that you don't control.

This chapter discusses:

* Basic mechanics of interface types and their values
* Several important interfaces from the standard library
* Type assertions and type switches

### Interfaces as Contracts

#### Concrete type and interface type *

All the types discussed so far are [**concrete types**](https://en.wikipedia.org/wiki/Class_(computer_programming)#Abstract_and_Concrete). A concrete type specifies the exact representation of its values and exposes the intrinsic operations of that representation, such as arithmetic for numbers, or indexing, `append`, and `range` for slices. A concrete type may also provide additional behaviors through its methods. When you have a value of a concrete type, you know exactly what it is and what you can do with it.

There is another kind of type in Go called an **interface type**. An interface is an [**abstract type**](https://en.wikipedia.org/wiki/Abstract_type). It doesn't expose the representation or internal structure of its values, or the set of basic operations they support; it reveals only some of their methods. When you have a value of an interface type, you know nothing about what it is; you know only what it can do, or more precisely, what behaviors are provided by its methods.

#### The `io.Writer` interface *

This book has used two similar functions for string formatting:

* `fmt.Printf`, which writes the result to the standard output (a file)
* `fmt.Sprintf`, which returns the result as a string

Thanks to interfaces, both of these functions are in effect wrappers around a third function, `fmt.Fprintf`, which is agnostic about what happens to the result it computes:

```go
package fmt

func Fprintf(w io.Writer, format string, args ...interface{}) (int, error)

func Printf(format string, args ...interface{}) (int, error) {
	return Fprintf(os.Stdout, format, args...)
}

func Sprintf(format string, args ...interface{}) string {
	var buf bytes.Buffer
	Fprintf(&buf, format, args...)
	return buf.String()
}
```

The `F` prefix of `Fprintf` stands for *file* and indicates that the formatted output should be written to the file provided as the first argument.

* In the `Printf` case, the argument, `os.Stdout`, is an [`*os.File`](https://golang.org/pkg/os/#File).
* In the `Sprintf` case, the argument is not a file but superficially resembles one: `&buf` is a pointer to a memory buffer to which bytes can be written.

The first parameter of `Fprintf` is not a file either. It's an [`io.Writer`](https://golang.org/pkg/io/#Writer), which is an interface type with the following declaration:

<small>[go/src/io/io.go](https://github.com/golang/go/blob/master/src/io/io.go)</small>

```go
package io

// Writer is the interface that wraps the basic Write method.
//
// Write writes len(p) bytes from p to the underlying data stream.
// It returns the number of bytes written from p (0 <= n <= len(p))
// and any error encountered that caused the write to stop early.
// Write must return a non-nil error if it returns n < len(p).
// Write must not modify the slice data, even temporarily.
//
// Implementations must not retain p.
type Writer interface {
	Write(p []byte) (n int, err error)
}
```

The `io.Writer` interface defines the contract between `Fprintf` and its callers.

* The contract requires that the caller provide a value of a concrete type like `*os.File` or `*bytes.Buffer` that has a method called `Write` with the appropriate signature and behavior.
* The contract guarantees that `Fprintf` will do its job given any value that satisfies the `io.Writer` interface.
* `Fprintf` may not assume that it is writing to a file or to memory, only that it can call `Write`.

Because `fmt.Fprintf` assumes nothing about the representation of the value and relies only on the behaviors guaranteed by the `io.Writer` contract, we can safely pass a value of any concrete type that satisfies `io.Writer` as the first argument to `fmt.Fprintf`. This freedom to substitute one type for another that satisfies the same interface is called *substitutability*, and is a hallmark of object-oriented programming.

The following example uses a new type. The `Write` method of the `*ByteCounter` type below merely counts the bytes written to it before discarding them. (The conversion is required to make the types of `len(p)` and `*c` match in the `+=` assignment statement.)

<small>[gopl.io/ch7/bytecounter/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/bytecounter/main.go)</small>

```go
type ByteCounter int

func (c *ByteCounter) Write(p []byte) (int, error) {
	*c += ByteCounter(len(p)) // convert int to ByteCounter
	return len(p), nil
}
```

Since `*ByteCounter` satisfies the `io.Writer` contract, we can pass it to `Fprintf`; the `ByteCounter` correctly accumulates the length of the result.

```go
var c ByteCounter
c.Write([]byte("hello"))
fmt.Println(c) // "5", = len("hello")

c = 0 // reset the counter
var name = "Dolly"
fmt.Fprintf(&c, "hello, %s", name)
fmt.Println(c) // "12", = len("hello, Dolly")
```

#### The `fmt.Stringer` interface *

Besides `io.Writer`, `fmt.Stringer` is another interface of great importance to the `fmt` package. `Fprintf` and `Fprintln` provide a way for types to control how their values are printed. For example:

* In [Section 2.5](ch2.md#type-declarations), we defined a `String` method for the `Celsius` type so that temperatures would print as "`100°C`.
* In [Section 6.5](ch6.md#example-bit-vector-type), we equipped `*IntSet` with a `String` method so that sets would be rendered using traditional set notation like "`{1 2 3}`".

Declaring a `String` method makes a type satisfy `fmt.Stringer`, which is one of the most widely used interfaces of all:

<small>[go/src/fmt/print.go](https://github.com/golang/go/blob/master/src/fmt/print.go)</small>

```go
package fmt

// The String method is used to print values passed
// as an operand to any format that accepts a string
// or to an unformatted printer such as Print.
type Stringer interface {
	String() string
}
```

[Section 7.10](#type-assertions) will explain how the `fmt` package discovers which values satisfy this interface.

### Interface Types

An interface type specifies a set of methods that a concrete type must possess to be considered an instance of that interface.

The `io.Writer` type is one of the most widely used interfaces because it provides an abstraction of all the types to which bytes can be written, such as files, memory buffers, network connections, HTTP clients, archivers and hashers. The `io` package defines many other useful interfaces. A `Reader` represents any type from which you can read bytes, and a `Closer` is any value that you can close, such as a file or a network connection. (Notice the naming convention for many of Go's single-method interfaces.)

```go
package io

type Reader interface {
	Read(p []byte) (n int, err error)
}

type Closer interface {
	Close() error
}
```

The following are examples of new interface types as combinations of existing ones:

```go
type ReadWriter interface {
	Reader
	Writer
}

type ReadWriteCloser interface {
	Reader
	Writer
	Closer
}
```

The syntax used above, which resembles [struct embedding](ch4#struct-embedding-and-anonymous-fields), enables us to name another interface as a shorthand for writing out all of its methods. This is called *embedding* an interface. We could have written `io.ReadWriter` without embedding like this:

```go
type ReadWriter interface {
	Read(p []byte) (n int, err error)
	Write(p []byte) (n int, err error)
}
```

We can even use a mixture of the two styles:

```go
type ReadWriter interface {
	Read(p []byte) (n int, err error)
	Writer
}
```

All three declarations have the same effect. The order in which the methods appear is immaterial. All that matters is the set of methods.

### Interface Satisfaction

A type *satisfies* an interface if it possesses all the methods the interface requires. For example:

* An `*os.File` satisfies `io.Reader`, `Writer`, `Closer`, and `ReadWriter`.
* A `*bytes.Buffer` satisfies `Reader`, `Writer`, and `ReadWriter`, but does not satisfy `Closer` because it does not have a `Close` method.

As a shorthand, Go programmers often say that a concrete type "is a" particular interface type, meaning that it satisfies the interface. For example:

* A `*bytes.Buffer` is an `io.Writer`.
* An `*os.File` is an `io.ReadWriter`.

The assignability rule ([Section 2.4.2](ch2.md##assignability)) for interfaces is very simple: an expression may be assigned to an interface only if its type satisfies the interface. For example:

```go
var w io.Writer
w = os.Stdout           // OK: *os.File has Write method
w = new(bytes.Buffer)   // OK: *bytes.Buffer has Write method
w = time.Second         // compile error: time.Duration lacks Write method

var rwc io.ReadWriteCloser
rwc = os.Stdout         // OK: *os.File has Read, Write, Close methods
rwc = new(bytes.Buffer) // compile error: *bytes.Buffer lacks Close method
```

This rule applies even when the right-hand side is itself an interface:

```go
w = rwc     // OK: io.ReadWriteCloser has Write method
rwc = w     // compile error: io.Writer lacks Close method
```

We should explain one subtlety in what it means for a type to have a method. Recall from [Section 6.2](ch6.md#methods-with-a-pointer-receiver) that for each named concrete type `T`, some of its methods have a receiver of type `T` itself whereas others require a `*T` pointer. Recall also that it is legal to call a `*T` method on an argument of type `T` as long as the argument is a variable; the compiler implicitly takes its address. However, this is mere syntactic sugar: a value of type `T` does not possess all the methods that a `*T` pointer does; as a result, `T` might satisfy fewer interfaces.

For example, the `String` method of the `IntSet` type from [Section 6.5](ch6.md#example-bit-vector-type) requires a pointer receiver, so we cannot call that method on a non-addressable `IntSet` value:

```go
type IntSet struct { /* ... */ }
func (*IntSet) String() string
var _ = IntSet{}.String() // compile error: String requires *IntSet receiver
```

But we can call it on an `IntSet` variable:

```go
var s IntSet
var _ = s.String() // OK: s is a variable and &s has a String method
```

However, since only `*IntSet` has a `String` method, only `*IntSet` satisfies the `fmt.Stringer` interface:

```go
var _ fmt.Stringer = &s // OK
var _ fmt.Stringer = s  // compile error: IntSet lacks String method
```

[Section 12.8](ch12.md#displaying-the-methods-of-a-type) includes a program that prints the methods of an arbitrary value, and the `godoc -analysis=type` tool ([Section 10.7.4](ch10.md#documenting-packages)) displays the methods of each type and the relationship between interfaces and concrete types.

An interface wraps and conceals the concrete type and value that it holds. <u>Only the methods revealed by the interface type may be called, even if the concrete type has others</u>:

```go
os.Stdout.Write([]byte("hello")) // OK: *os.File has Write method
os.Stdout.Close()                // OK: *os.File has Close method

var w io.Writer
w = os.Stdout
w.Write([]byte("hello")) // OK: io.Writer has Write method
w.Close()                // compile error: io.Writer lacks Close method
```

#### Empty interface: `interface{}` *

An interface with more methods, such as `io.ReadWriter`, tells us more about the values it contains, and places greater demands on the types that implement it, than does an interface with fewer methods such as `io.Reader`. Similarly, the type `interface{}`, which has no methods at all, tell us about nothing about the concrete types that satisfy it. This may seem useless, but in fact the type `interface{}`, which is called the **empty interface** type, is indispensable. Because the empty interface type places no demands on the types that satisfy it, we can assign any value to the empty interface.

```go
var any interface{}
any = true
any = 12.34
any = "hello"
any = map[string]int{"one": 1}
any = new(bytes.Buffer)
```

The empty interface type has been used in the very first example in this book, because it is what allows functions like `fmt.Println`, or `errorf` in [Section 5.7](ch5.md#anonymous-functions), to accept arguments of any type.

Having created an `interface{}` value containing a boolean, float, string, map, pointer, or any other type, we can do nothing directly to the value it holds since the interface has no methods. We need a way to get the value back out again, which can be done using a type assertion, discussed in [Section 7.10](#type-assertions).

Since interface satisfaction depends only on the methods of the two types involved, there is no need to declare the relationship between a concrete type and the interfaces it satisfies. However, it is occasionally useful to document and assert the relationship when it is intended but not otherwise enforced by the program. The declaration below asserts at compile time that a value of type `*bytes.Buffer` satisfies `io.Writer`:

```go
// *bytes.Buffer must satisfy io.Writer
var w io.Writer = new(bytes.Buffer)
```

We needn't allocate a new variable since any value of type `*bytes.Buffer` will do, even `nil`, which we write as `(*bytes.Buffer)(nil)` using an explicit conversion. Since we never intend to refer to `w`, we can replace it with the blank identifier, which makes more frugal variant:

```go
// *bytes.Buffer must satisfy io.Writer
var _ io.Writer = (*bytes.Buffer)(nil)
```

Non-empty interface types such as `io.Writer` are most often satisfied by a pointer type, particularly when one or more of the interface methods implies some kind of mutation to the receiver, as the `Write` method does. A pointer to a struct is an especially common method-bearing type.

Pointer types are not the only types that satisfy interfaces, and even interfaces with mutator methods may be satisfied by other reference types. For example:

* Slice types with methods (`geometry.Path`, [Section 6.1](ch6.md#method-declarations))
* Map types with methods (`url.Values`, [Section 6.2.1](ch6.md#nil-is-a-valid-receiver-value)),
* Function type with methods (`http.HandlerFunc`, [Section 7.7](#the-httphandler-interface)).
* Even basic types may satisfy interfaces: in [Section 7.4](#parsing-flags-with-flagvalue), `time.Duration` satisfies `fmt.Stringer`.

A concrete type may satisfy many unrelated interfaces. For example, a program that organizes or sells digitized cultural artifacts might define the following set of concrete types:

```text
Album
Book
Movie
Magazine
Podcast
TVEpisode
Track
```

Each abstraction of interest can be expressed as an interface. Some properties are common to all artifacts, such as a title, a creation date, and a list of creators (authors or artists).

```go
type Artifact interface {
	Title() string
	Creators() []string
	Created() time.Time
}
```

Other properties are restricted to certain types of artifacts. Properties of the printed word are relevant only to books and magazines, whereas only movies and TV episodes have a screen resolution.

```go
type Text interface {
	Pages() int
	Words() int
	PageSize() int
}

type Audio interface {
	Stream() (io.ReadCloser, error)
	RunningTime() time.Duration
	Format() string // e.g., "MP3", "WAV"
}

type Video interface {
  Stream() (io.ReadCloser, error)
  RunningTime() time.Duration
  Format() string // e.g., "MP4", "WMV"
  Resolution() (x, y int)
}
```

These interfaces are not the only useful way to group related concrete types together and express the facets they share in common. We may discover other groupings later. For example, if we find we need to handle `Audio` and `Video` items in the same way, we can define a `Streamer` interface to represent their common aspects without changing any existing type declarations.

```go
type Streamer interface {
	Stream() (io.ReadCloser, error)
	RunningTime() time.Duration
	Format() string
}
```

Each grouping of concrete types based on their shared behaviors can be expressed as an interface type. Unlike class-based languages, in which the set of interfaces satisfied by a class is explicit, in Go we can define new abstractions or groupings of interest when we need them, without modifying the declaration of the concrete type. This is particularly useful when the concrete type comes from a package written by a different author. Of course, there do need to be underlying commonalities in the concrete types.

### Parsing Flags with `flag.Value`

This section discusses another standard interface, `flag.Value`, which enables us to define new notations for command-line flags. For example, the following program sleeps for a specified period of time:

<small>[gopl.io/ch7/sleep/sleep.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/sleep/sleep.go)</small>

```go
var period = flag.Duration("period", 1*time.Second, "sleep period")

func main() {
	flag.Parse()
	fmt.Printf("Sleeping for %v...", *period)
	time.Sleep(*period)
	fmt.Println()
}
```

Before it goes to sleep it prints the time period. The `fmt` package calls the `time.Duration`'s `String` method to print the period in a user-friendly notation instead of [a number of nanoseconds](ch6.md#other-aspects-of-encapsulation):

```shell-session
$ go build gopl.io/ch7/sleep
$ ./sleep
Sleeping for 1s...
```

* By default, the sleep period is one second, but it can be controlled through the `-period` command-line flag.
* The `flag.Duratio` function creates a flag variable of type `time.Duration` and allows the user to specify the duration in a variety of user-friendly formats, including the same notation printed by the `String` method. This symmetry of design leads to a nice user interface.

```shell-session
$ ./sleep -period 50ms
Sleeping for 50ms...
$ ./sleep -period 2m30s
Sleeping for 2m30s...
$ ./sleep -period 1.5h
Sleeping for 1h30m0s...
$ ./sleep -period "1 day"
invalid value "1 day" for flag -period: time: invalid duration 1 day
```

It's easy to define new flag notations for our own data types. We need only define a type that satisfies the `flag.Value` interface, whose declaration is:

```go
package flag

// Value is the interface to the value stored in a flag.
type Value interface {
	String() string
	Set(string) error
}
```

* The `String` method formats the flags' value for use in command-line help messages; thus every `flag.Value` is also a `fmt.Stringer`.
* The `Set` method parses its string argument and updates the flag value. In effect, the `Set` method is the inverse of the `String` method, and it is good practice for them to use the same notation.

The following example defines a `celsiusFlag` type that allows a temperature to be specified in Celsius, or in Fahrenheit with an appropriate conversion. Notice that `celsiusFlag` embeds a `Celsius` ([Section 2.5](ch2.md#type-declarations)), thereby getting a `String` method for free. To satisfy `flag.Value`, we need only declare the Set method:

<small>[gopl.io/ch7/tempconv/tempconv.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/tempconv/tempconv.go)</small>

```go
type celsiusFlag struct{ Celsius }

func (f *celsiusFlag) Set(s string) error {
	var unit string
	var value float64
	fmt.Sscanf(s, "%f%s", &value, &unit) // no error check needed
	switch unit {
	case "C", "°C":
		f.Celsius = Celsius(value)
		return nil
	case "F", "°F":
		f.Celsius = FToC(Fahrenheit(value))
		return nil
	}
	return fmt.Errorf("invalid temperature %q", s)
}
```

The call to [`fmt.Sscanf`](https://golang.org/pkg/fmt/#Sscanf) parses a floating-point number (`value`) and a string (`unit`) from the input `s`. Although one must usually check `Sscanf`'s error result, in this case we don't need to because if there was a problem, no switch case will match.

The `CelsiusFlag` function below wraps it all up.

```go
// CelsiusFlag defines a Celsius flag with the specified name,
// default value, and usage, and returns the address of the flag variable.
// The flag argument must have a quantity and a unit, e.g., "100C".
func CelsiusFlag(name string, value Celsius, usage string) *Celsius {
	f := celsiusFlag{value}
	flag.CommandLine.Var(&f, name, usage)
	return &f.Celsius
}
```

* To the caller, it returns a pointer to the `Celsius` field embedded within the `celsiusFlag` variable `f`. The `Celsius` field is the variable that will be updated by the `Set` method during flags processing.
* The call to `Var` adds the flag to the application's set of command-line flags, the global variable `flag.CommandLine`. Programs with complex command-line interfaces may have several variables of this type.
* <u>The call to `Var` assigns a `*celsiusFlag` argument to a `flag.Value` parameter, causing the compiler to check that `*celsiusFlag` has the necessary methods.</u> (See [Section 7.3](#interface-satisfaction))

The following program uses `CelsiusFlag`:

<small>[gopl.io/ch7/tempflag/tempflag.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/tempflag/tempflag.go)</small>

```
var temp = tempconv.CelsiusFlag("temp", 20.0, "the temperature")

func main() {
	flag.Parse()
	fmt.Println(*temp)
}
```

Run this program:

```shell-session
$ go build gopl.io/ch7/tempflag
$ ./tempflag
20°C
$ ./tempflag -temp -18C
-18°C
$ ./tempflag -temp 212°F
100°C
$ ./tempflag -temp 273.15K
invalid value "273.15K" for flag -temp: invalid temperature "273.15K"
Usage of ./tempflag:
-temp value
the temperature (default 20°C)
$ ./tempflag -help
Usage of ./tempflag:
-temp value
the temperature (default 20°C)
```

### Interface Values

Conceptually, an **interface value** (a value of an interface type) has two components:

* A concrete type, called the interface's *dynamic type*
* A value of that type, called the interface's *dynamic value*

For a statically typed language like Go, types are a compile-time concept, so a type is not a value. In our conceptual model, a set of values called *type descriptors* provide information about each type, such as its name and methods. In an interface value, the type component is represented by the appropriate type descriptor.

In the four statements below, the variable `w` takes on three different values. (The initial and final values are the same.)

```go
var w io.Writer
w = os.Stdout
w = new(bytes.Buffer)
w = nil
```

The first statement declares `w`:

```go
var w io.Writer
```

In Go, variables are always initialized to a well-defined value, and interfaces are no exception.  The zero value for an interface has both its type and value components set to `nil` (see the figure below).

[![Figure 7.1. A nil interface value.](figure_7.1.png)](figure_7.1.png "Figure 7.1. A nil interface value.")

An interface value is described as nil or non-nil based on its dynamic type, so this is a nil interface value. You can test whether an interface value is nil using `w == nil` or `w != nil`. Calling any method of a nil interface value causes a panic:

```go
w.Write([]byte("hello")) // panic: nil pointer dereference
```

The second statement assigns a value of type `*os.File` to `w`:

```go
w = os.Stdout
```

This assignment involves an implicit conversion from a concrete type to an interface type, and is equivalent to the explicit conversion `io.Writer(os.Stdout)`. Such conversion, whether explicit or implicit, captures the type and the value of its operand. The interface value's dynamic type is set to the type descriptor for the pointer type `*os.File`, and its dynamic value holds a copy of `os.Stdout`, which is a pointer to the `os.File` variable representing the standard output of the process (see the figure below).

[![Figure 7.2. An interface value containing an *os.File pointer.](figure_7.2.png)](figure_7.2.png "Figure 7.2. An interface value containing an *os.File pointer.")

Calling the `Write` method on an interface value containing an `*os.File` pointer causes the `(*os.File).Write` method to be called, which prints "hello".

```go
w.Write([]byte("hello")) // "hello"
```

In general, we cannot know at compile time what the dynamic type of an interface value will be, so a call through an interface must use [*dynamic dispatch*](https://en.wikipedia.org/wiki/Dynamic_dispatch). Instead of a direct call, the compiler must generate code to obtain the address of the method named `Write` from the type descriptor, then make an indirect call to that address. The receiver argument for the call is a copy of the interface's dynamic value,` os.Stdout`. The effect is as if we had made this call directly:

```go
os.Stdout.Write([]byte("hello")) // "hello"
```

The third statement assigns a value of type `*bytes.Buffer` to the interface value:

```go
w = new(bytes.Buffer)
```

The dynamic type is now `*bytes.Buffer` and the dynamic value is a pointer to the newly allocated buffer (see figure below).

[![Figure 7.3. An interface value containing a *bytes.Buffer pointer.](figure_7.3.png)](figure_7.3.png "Figure 7.3. An interface value containing a *bytes.Buffer pointer.")

A call to the `Write` method uses the same mechanism as before:

```go
w.Write([]byte("hello")) // writes "hello" to the bytes.Buffer
```

This time, the type descriptor is `*bytes.Buffer`, so the `(*bytes.Buffer).Write` method is called, with the address of the buffer as the value of the receiver parameter. The call appends "`hello`" to the buffer.

Finally, the fourth statement assigns `nil` to the interface value:

```go
w = nil
```

This resets both its components to `nil`, restoring `w` to the same state as when it was declared, as shown in [Figure 7.1](figure_7.1.png).

An interface value can hold arbitrarily large dynamic values. For example, the `time.Time`
type is a struct type with several unexported fields.

```go
var x interface{} = time.Now()
```

This interface value is like the following figure:

[![Figure 7.4. An interface value holding a time.Time struct.](figure_7.4.png)](figure_7.4.png "Figure 7.4. An interface value holding a time.Time struct.")

Conceptually, the dynamic value always fits inside the interface value, no matter how large its type. Note that this is only a conceptual model; a realistic implementation is quite different.

Interface values may be compared using `==` and `!=`. Two interface values are equal if either of the following occurs:

* Both of them are nil.
* Their dynamic types are identical and their dynamic values are equal according to the usual behavior of `==` for that type.

Because interface values are comparable, they may be used as the keys of a map or as the operand of a switch statement. However, if two interface values are compared and have the same dynamic type, but that type is not comparable (e.g. slice), then the comparison fails with a panic:

```go
var x interface{} = []int{1, 2, 3}
fmt.Println(x == x) // panic: comparing uncomparable type []int
```

Therefore, interface types are unusual: interface values are comparable, but may panic, while other types are either safely comparable or not comparable at all:

* Safely comparable, such as basic types and pointers
* Not comparable, such as slices, maps, and functions

When comparing interface values or aggregate types that contain interface values, we must be aware of the potential for a panic. A similar risk exists when using interfaces as map keys or switch operands. <u>Only compare interface values if you are certain that they contain dynamic values of comparable types.</u>

When handling errors, or during debugging, it is often helpful to report the dynamic type of an interface value, using the `fmt` package's `%T` verb:

```go
var w io.Writer
fmt.Printf("%T\n", w) // "<nil>"

w = os.Stdout
fmt.Printf("%T\n", w) // "*os.File"

w = new(bytes.Buffer)
fmt.Printf("%T\n", w) // "*bytes.Buffer"
```

Internally, `fmt` uses reflection ([Chapter 12](ch12.md)) to obtain the name of the interface's dynamic type.

#### Caveat: An Interface Containing a Nil Pointer Is Non-Nil

A nil interface value, which contains no value at all, is not the same as an interface value containing a pointer that happens to be nil.

In the program below, when `debug` is set to `true`, the function collects the output of the function `f` in a `bytes.Buffer`.

```go
const debug = true

func main() {
	var buf *bytes.Buffer
	if debug {
		buf = new(bytes.Buffer) // enable collection of output
	}
	f(buf) // NOTE: subtly incorrect!
	if debug {
		// ...use buf...
	}
}

// If out is non-nil, output will be written to it.
func f(out io.Writer) {
	// ...do something...
	if out != nil {
		out.Write([]byte("done!\n"))
	}
}
```

We might expect that changing `debug` to `false` would disable the collection of the output, but in fact it causes the program to panic during the `out.Write` call:

```go
if out != nil {
	out.Write([]byte("done!\n")) // panic: nil pointer dereference
}
```

When `main` calls `f`, it assigns a nil pointer of type `*bytes.Buffer` to the `out` parameter, so the dynamic value of `out` is `nil`. However, its dynamic type is `*bytes.Buffer`, meaning that `out` is a non-nil interface containing a nil pointer value (see figure below), so the defensive check `out != nil` is still true.

[![Figure 7.5. A non-nil interface containing a nil pointer.](figure_7.5.png)](figure_7.5.png "Figure 7.5. A non-nil interface containing a nil pointer.")

The dynamic dispatch mechanism determines that `(*bytes.Buffer).Write` must be called but this time with a receiver value that is nil. For some types, such as `*os.File`, nil is a valid receiver ([Section 6.2.1](ch6.md#nil-is-a-valid-receiver-value)), but `*bytes.Buffer` is not among them. The method is called, but it panics as it tries to access the buffer.

The problem is that although a nil `*bytes.Buffer` pointer has the methods needed to satisfy the interface, it doesn't satisfy the *behavioral* requirements of the interface. In particular, the call violates the implicit precondition of `(*bytes.Buffer).Write` that its receiver is not nil, so assigning the nil pointer to the interface was a mistake. The solution is to change the type of `buf` in `main` to `io.Writer`, thereby avoiding the assignment of the dysfunctional value to the interface in the first place:

```go
var buf io.Writer
if debug {
	buf = new(bytes.Buffer) // enable collection of output
}
f(buf) // OK
```

### Sorting with `sort.Interface`

Sorting is a frequently used operation in many programs. [p186]

In many languages, the sorting algorithm is associated with the sequence data type, while the ordering function is associated with the type of the elements.

In Go, the [`sort`](https://golang.org/pkg/sort/) package provides in-place sorting of any sequence according to any ordering function. However, its design is rather unusual:

* `sort.Sort` function assumes nothing about the representation of either the sequence or its elements. Instead, it uses an interface, `sort.Interface`, to specify the contract between the generic sort algorithm and each sequence type that may be sorted.
* An implementation of this interface determines both the concrete representation of the sequence, which is often a slice, and the desired ordering of its elements.

An in-place sort algorithm needs three things:

* The length of the sequence
* A means of comparing two elements
* A way to swap two elements

They are the three methods of `sort.Interface`:

```go
package sort

type Interface interface {
	Len() int
	Less(i, j int) bool // i, j are indices of sequence elements
	Swap(i, j int)
}
```

To sort any sequence, we need to define a type that implements these three methods, then apply `sort.Sort` to an instance of that type. For example, consider sorting a slice of strings. The new type `StringSlice` and its `Len`, `Less`, and `Swap` methods are shown below:

```go
type StringSlice []string
func (p StringSlice) Len() int           { return len(p) }
func (p StringSlice) Less(i, j int) bool { return p[i] < p[j] }
func (p StringSlice) Swap(i, j int)      { p[i], p[j] = p[j], p[i] }
```

Now we can sort a slice of strings, `names`, by converting the slice to a `StringSlice` like this:

```go
sort.Sort(StringSlice(names))
```

The conversion yields a slice value with the same length, capacity, and underlying array as `names` but with a type that has the three methods required for sorting.

Sorting a slice of strings is so common that the sort package provides the `StringSlice` type and a function called `Strings`. The call above can be simplified as:

```go
sort.Strings(names)
```

This technique can be easily adapted to other sort orders, for instance, to ignore capitalization or special characters. For more complicated sorting, we use the same idea, but with more complicated data structures or more complicated implementations of the `sort.Interface` methods.

#### Example: sorting a playlist *

The following example is a music playlist, displayed as a table. Each track is a single row, and each column is an attribute of that track. The playlist can be sorted by any attribute in the columns.

The variable `tracks` below contains a playlist. Each element is indirect, a pointer to a `Track`. Although the code below would work if we stored the `Track`s directly, the `sort` function will swap many pairs of elements, so it will run faster if each element is a pointer, which is a single machine word, instead of an entire `Track`.

<small>[gopl.io/ch7/sorting/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/sorting/main.go)</small>

```go
type Track struct {
	Title  string
	Artist string
	Album  string
	Year   int
	Length time.Duration
}

var tracks = []*Track{
	{"Go", "Delilah", "From the Roots Up", 2012, length("3m38s")},
	{"Go", "Moby", "Moby", 1992, length("3m37s")},
	{"Go Ahead", "Alicia Keys", "As I Am", 2007, length("4m36s")},
	{"Ready 2 Go", "Martin Solveig", "Smash", 2011, length("4m24s")},
}

func length(s string) time.Duration {
	d, err := time.ParseDuration(s)
	if err != nil {
		panic(s)
	}
	return d
}
```

The `printTracks` function prints the playlist as a table. It uses the [`text/tabwriter`](https://golang.org/pkg/text/tabwriter/) package to produce a table whose columns are neatly aligned and padded.

* `*tabwriter.Writer` satisfies `io.Writer`.
* It collects each piece of data written to it.
* Its `Flush` method formats the entire table and writes it to `os.Stdout`.

```go
func printTracks(tracks []*Track) {
	const format = "%v\t%v\t%v\t%v\t%v\t\n"
	tw := new(tabwriter.Writer).Init(os.Stdout, 0, 8, 2, ' ', 0)
	fmt.Fprintf(tw, format, "Title", "Artist", "Album", "Year", "Length")
	fmt.Fprintf(tw, format, "-----", "------", "-----", "----", "------")
	for _, t := range tracks {
		fmt.Fprintf(tw, format, t.Title, t.Artist, t.Album, t.Year, t.Length)
	}
	tw.Flush() // calculate column widths and print table
}
```

To sort the playlist by the `Artist` field, we define a new slice type with the necessary `Len`, `Less`, and `Swap` methods, similar to the `StringSlice` example.

```go
type byArtist []*Track

func (x byArtist) Len() int           { return len(x) }
func (x byArtist) Less(i, j int) bool { return x[i].Artist < x[j].Artist }
func (x byArtist) Swap(i, j int)      { x[i], x[j] = x[j], x[i] }
```

To call the generic `sort` routine, we must first convert tracks to the new type, `byArtist`, that defines the order:

```go
sort.Sort(byArtist(tracks))
```

After sorting the slice by artist, the output from `printTracks` is:

```text
Title       Artist          Album              Year  Length
-----       ------          -----              ----  ------
Go Ahead    Alicia Keys     As I Am            2007  4m36s
Go          Delilah         From the Roots Up  2012  3m38s
Ready 2 Go  Martin Solveig  Smash              2011  4m24s
Go          Moby            Moby               1992  3m37s
```

To sort by artist in reverse order, we needn't define a new type `byReverseArtist` with an inverted `Less` method. The `sort` package provides a [`Reverse`](https://golang.org/pkg/sort/#Reverse) function that transforms any sort order to its inverse.

```go
sort.Sort(sort.Reverse(byArtist(tracks)))
```

The `sort.Reverse` function uses composition ([Section 6.3](ch6.md#composing-types-by-struct-embedding)), which is an important idea. The `sort` package defines an unexported type `reverse`, which is a struct that embeds a `sort.Interface`. The `Less` method for `reverse` calls the `Less` method of the embedded `sort.Interface` value, but with the indices flipped, reversing the order of the sort results.

```go
package sort
type reverse struct{ Interface } // that is, sort.Interface
func (r reverse) Less(i, j int) bool { return r.Interface.Less(j, i) }
func Reverse(data Interface) Interface { return reverse{data} }
```

`Len` and `Swap`, the other two methods of `reverse`, are implicitly provided by the original `sort.Interface` value because it is an embedded field. The exported function `Reverse` returns an instance of the reverse type that contains the original `sort.Interface` value.

To sort by a different column, we must define a new type, such as `byYear`:

```go
type byYear []*Track

func (x byYear) Len() int           { return len(x) }
func (x byYear) Less(i, j int) bool { return x[i].Year < x[j].Year }
func (x byYear) Swap(i, j int)      { x[i], x[j] = x[j], x[i] }
```

Similarly, sort `tracks` by year using `sort.Sort(byYear(tracks))`.

For every slice element type and every ordering function we need, we declare a new implementation of `sort.Interface`; the `Len` and `Swap` methods have identical definitions for all slice types.

In the following example, the concrete type `customSort` combines a slice with a function, so we can define a new sort order by writing only the comparison function. Incidentally, the concrete types that implement `sort.Interface` are not always slices; `customSort` is a struct type.

```go
type customSort struct {
	t    []*Track
	less func(x, y *Track) bool
}

func (x customSort) Len() int           { return len(x.t) }
func (x customSort) Less(i, j int) bool { return x.less(x.t[i], x.t[j]) }
func (x customSort) Swap(i, j int)      { x.t[i], x.t[j] = x.t[j], x.t[i] }
```

The following code defines a multi-tier ordering function whose primary sort key is the `Title`, secondary key is the `Year`, and tertiary key is the running time, `Length`. This is the call to `Sort` using an anonymous ordering function:

```go
sort.Sort(customSort{tracks, func(x, y *Track) bool {
	if x.Title != y.Title {
		return x.Title < y.Title
	}
	if x.Year != y.Year {
		return x.Year < y.Year
	}
	if x.Length != y.Length {
		return x.Length < y.Length
	}
	return false
}})
```

[p190]

Although sorting a sequence of length *n* requires O(*n* log *n*) comparison operations, testing whether a sequence is already sorted requires at most *n*−1 comparisons. The [`IsSorted`](https://golang.org/pkg/sort/#IsSorted) function from the `sort` package checks this for us. Like `sort.Sort`, it abstracts both the sequence and its ordering function using `sort.Interface`, but it never calls the `Swap` method.

The following code demonstrates the [`IntsAreSorted`](https://golang.org/pkg/sort/#IntsAreSorted) and [`Ints`](https://golang.org/pkg/sort/#Ints) functions and the [`IntSlice`](https://golang.org/pkg/sort/#IntSlice) type from the `sort` package:

```go
values := []int{3, 1, 4, 1}
fmt.Println(sort.IntsAreSorted(values)) // "false"
sort.Ints(values)
fmt.Println(values)                     // "[1 1 3 4]"
fmt.Println(sort.IntsAreSorted(values)) // "true"
sort.Sort(sort.Reverse(sort.IntSlice(values)))
fmt.Println(values)                     // "[4 3 1 1]"
fmt.Println(sort.IntsAreSorted(values)) // "false"
```

For convenience, the `sort` package provides versions of its functions and types specialized for `[]int`, `[]string`, and `[]float64` using their natural orderings. For other types, such as `[]int64` or `[]uint`, we need to write types on our own, though the path is short.

### The `http.Handler` Interface

Chapter 1 discusses how to use the [`net/http`](https://golang.org/pkg/net/http/) package to implement web clients ([Section 1.5](ch1.md#fetching-a-url)) and servers ([Section 1.7](ch1.md#a-web-server)). This section focuses on server API, whose foundation is the `http.Handler` interface:

```go
package http

type Handler interface {
	ServeHTTP(w ResponseWriter, r *Request)
}

func ListenAndServe(address string, h Handler) error
```

The `ListenAndServe` function requires two arguments:

* A server address, such as "localhost:8000"
* An instance of the `Handler` interface, to which all requests should be dispatched.

This function runs forever, or until the server fails or fails to start; when it fails, it always returns an non-nil error.

The program of the following example shows the simplest implementation of an e-commerce site with a database mapping the items for sale to their prices in dollars. It models the inventory as a map type, `database`, to which we've attached a `ServeHTTP` method so that it satisfies the `http.Handler` interface. The handler ranges over the map and prints the items.

<small>[gopl.io/ch7/http1/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/http1/main.go)</small>

```go
func main() {
	db := database{"shoes": 50, "socks": 5}
	log.Fatal(http.ListenAndServe("localhost:8000", db))
}

type dollars float32

func (d dollars) String() string { return fmt.Sprintf("$%.2f", d) }

type database map[string]dollars

func (db database) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	for item, price := range db {
		fmt.Fprintf(w, "%s: %s\n", item, price)
	}
}
```

If we start the server:

```shell-session
$ go build gopl.io/ch7/http1
$ ./http1 &
```

Then connect to it with the `fetch` program from [Section 1.5](ch1.md#fetching-a-url) (or a web browser if you prefer), we get the following output:

```text
$ go build gopl.io/ch1/fetch
$ ./fetch http://localhost:8000
shoes: $50.00
socks: $5.00
```

The following program shows a more realistic server that defines multiple different URLs, each triggering a different behavior. It names the existing one `/list` and adds another one called `/price` that reports the price of a single item, specified as a request parameter like `/price?item=socks`.

<small>[gopl.io/ch7/http2/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/http2/main.go)</small>

```go
func (db database) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	switch req.URL.Path {
	case "/list":
		for item, price := range db {
			fmt.Fprintf(w, "%s: %s\n", item, price)
		}
	case "/price":
		item := req.URL.Query().Get("item")
		price, ok := db[item]
		if !ok {
			w.WriteHeader(http.StatusNotFound) // 404
			fmt.Fprintf(w, "no such item: %q\n", item)
			return
		}
		fmt.Fprintf(w, "%s\n", price)
	default:
		w.WriteHeader(http.StatusNotFound) // 404
		fmt.Fprintf(w, "no such page: %s\n", req.URL)
	}
}
```

The handler above decides what logic to execute based on the path component of the URL, `req.URL.Path`. If the handler doesn't recognize the path, it reports an HTTP error to the client by calling `w.WriteHeader(http.StatusNotFound)`; this must be done before writing any text to `w`. `http.ResponseWriter` is another interface, which augments `io.Writer` with methods for sending HTTP response headers. Equivalently, we could use the `http.Error` utility function:

```go
msg := fmt.Sprintf("no such page: %s\n", req.URL)
http.Error(w, msg, http.StatusNotFound) // 404
```

The case for `/price` calls the URL's `Query` method to parse the HTTP request parameters as a map, or more precisely, a multimap of type `url.Values` ([Section 6.2.1](ch6.md#nil-is-a-valid-receiver-value)) from the `net/url` package. It then finds the first item parameter and looks up its price. If the item wasn't found, it reports an error.

The following is an example session with the new server:

```text
$ go build gopl.io/ch7/http2
$ go build gopl.io/ch1/fetch
$ ./http2 &
$ ./fetch http://localhost:8000/list
shoes: $50.00
socks: $5.00
$ ./fetch http://localhost:8000/price?item=socks
$5.00
$ ./fetch http://localhost:8000/price?item=shoes
$50.00
$ ./fetch http://localhost:8000/price?item=hat
no such item: "hat"
$ ./fetch http://localhost:8000/help
no such page: /help
```

In a realistic application:

1. It's convenient to define the logic for each case in a separate function or method.
2. Related URLs may need similar logic. For instance, several image files may have URLs of the form `/images/*.png`.

For these reasons, `net/http` provides [`ServeMux`](https://golang.org/pkg/net/http/#ServeMux), a *request multiplexer*, to simplify the association between URLs and handlers. A `ServeMux` aggregates a collection of `http.Handler`s into a single `http.Handler`. We see that different types satisfying the same interface are *substitutable*: the web server can dispatch requests to any `http.Handler`, regardless of which concrete type is behind it.

For a more complex application, several `ServeMux`es may be composed to handle more intricate dispatching requirements. [p193]

The program below does the following:

1. It creates a `ServeMux` and use it to associate the URLs with the corresponding handlers for the `/list` and `/price` operations, which have been split into separate methods.
2. It then uses the `ServeMux` as the main handler in the call to `ListenAndServe`.

<small>[gopl.io/ch7/http3/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/http3/main.go)</small>

```go
func main() {
	db := database{"shoes": 50, "socks": 5}
	mux := http.NewServeMux()
	mux.Handle("/list", http.HandlerFunc(db.list))
	mux.Handle("/price", http.HandlerFunc(db.price))
	log.Fatal(http.ListenAndServe("localhost:8000", mux))
}

type database map[string]dollars

func (db database) list(w http.ResponseWriter, req *http.Request) {
	for item, price := range db {
		fmt.Fprintf(w, "%s: %s\n", item, price)
	}
}

func (db database) price(w http.ResponseWriter, req *http.Request) {
	item := req.URL.Query().Get("item")
	price, ok := db[item]
	if !ok {
		w.WriteHeader(http.StatusNotFound) // 404
		fmt.Fprintf(w, "no such item: %q\n", item)
		return
	}
	fmt.Fprintf(w, "%s\n", price)
}
```

The two calls to `mux.Handle` register the handlers. In the first one, `db.list` is a method value ([Section 6.4](ch6.md#method-values-and-expressions)), which is a value of the following type:

```go
func(w http.ResponseWriter, req *http.Request)
```

When `db.list` is called, it invokes the `database.list` method with the receiver value `db`. So `db.list` is a function that implements handler-like behavior, but since it has no methods, it doesn't satisfy the `http.Handler` interface and can't be passed directly to `mux.Handle`. The expression `http.HandlerFunc(db.list)` is a conversion, not a function call, since [`http.HandlerFunc`](https://golang.org/pkg/net/http/#HandlerFunc) is a type. It has the following definition:

```go
package http

type HandlerFunc func(w ResponseWriter, r *Request)
func (f HandlerFunc) ServeHTTP(w ResponseWriter, r *Request) {
	f(w, r)
}
```

As a demonstration of some unusual features of Go's interface mechanism, <u>`HandlerFunc` is a function type that has methods and satisfies an interface, `http.Handler`. The behavior of its `ServeHTTP` method is to call the underlying function. `HandlerFunc` is thus an adapter that lets a function value satisfy an interface, where the function and the interface's sole method have the same signature.</u> In effect, this trick enables a single type such as `database` to satisfy the `http.Handler` interface in several different ways: once through its `list` method, once through its `price` method, and so on.

Because registering a handler this way is so common, `ServeMux` has a convenience method `HandleFunc` simplify the handler registration code:

<small>[gopl.io/ch7/http3a/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/http3a/main.go)</small>

```
mux.HandleFunc("/list", db.list)
mux.HandleFunc("/price", db.price)
```

We could also construct a program in which there are two different web servers, listening on different ports, defining different URLs, and dispatching to different handlers. This can be done by constructing another `ServeMux` and make another call to `ListenAndServe` perhaps concurrently. [p195]

For convenience, `net/http` provides a global `ServeMux` instance called `DefaultServeMux` and package-level functions called `http.Handle` and `http.HandleFunc`. To use `DefaultServeMux` as the server's main handler, we needn't pass it to `ListenAndServe`; `nil` will do.

The server's main function can then be simplified to:

<small>[gopl.io/ch7/http4/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/http4/main.go)</small>

```go
func main() {
	db := database{"shoes": 50, "socks": 5}
	http.HandleFunc("/list", db.list)
	http.HandleFunc("/price", db.price)
	log.Fatal(http.ListenAndServe("localhost:8000", nil))
}
```

As we mentioned in [Section 1.7](ch1.md#a-web-server), the web server invokes each handler in a new goroutine, so handlers must take precautions such as *locking* when accessing variables that other goroutines, including other requests to the same handler, may be accessing. Concurrency is discussed in the next two chapters.

### The `error` Interface

The predeclared `error` type is just an interface type with a single method that returns an error message:

```go
type error interface {
	Error() string
}
```

The simplest way to create an `error` is by calling `errors.New`, which returns a new `error` for a given error message. The entire `errors` package is only four lines long:

```go
package errors

func New(text string) error { return &errorString{text} }

type errorString struct { text string }

func (e *errorString) Error() string { return e.text }
```

The underlying type of `errorString` is a struct, not a string, to protect its representation from inadvertent (or premeditated) updates. The pointer type `*errorString` is used to satisfy the `error` interface rather than `errorString` alone so that every call to `New` allocates a distinct error instance that is not equal to each other. We would not want a distinguished error such as `io.EOF` to compare equal to one that may happen to have the same message.

```go
fmt.Println(errors.New("EOF") == errors.New("EOF")) // "false"
```

Calls to `errors.New` are infrequent because there's a convenient wrapper function, [`fmt.Errorf`](https://golang.org/pkg/fmt/#Errorf) that does string formatting. It is used in [Chapter 5](ch5.md).

```go
package fmt

import "errors"

func Errorf(format string, args ...interface{}) error {
	return errors.New(Sprintf(format, args...))
}
```

Although `*errorString` may be the simplest type of `error` but not the only one. For example, the `syscall` package provides Go's low-level system call API. On many platforms, it defines a numeric type `Errno` that satisfies `error`, and on Unix platforms, `Errno`'s `Error` method does a lookup in a table of strings, as shown below:

```go
package syscall

type Errno uintptr // operating system error code

var errors = [...]string{
	1: "operation not permitted", // EPERM
	2: "no such file or directory", // ENOENT
	3: "no such process", // ESRCH
	// ...
}

func (e Errno) Error() string {
	if 0 <= int(e) && int(e) < len(errors) {
		return errors[e]
	}
	return fmt.Sprintf("errno %d", e)
}
```

The following statement creates an interface value holding the `Errno` value 2, signifying the POSIX `ENOENT` condition:

```go
var err error = syscall.Errno(2)
fmt.Println(err.Error()) // "no such file or directory"
fmt.Println(err)         // "no such file or directory"
```

The value of `err` is shown graphically the following figure:

[![Figure 7.6. An interface value holding a syscall.Errno integer.](figure_7.6.png)](figure_7.6.png "Figure 7.6. An interface value holding a syscall.Errno integer.")

`Errno` is an efficient representation of system call errors drawn from a finite set, and it satisfies the standard `error` interface. Other types that satisfy this interface will be discussed in [Section 7.11](#discriminating-errors-with-type-assertions).

### Example: Expression Evaluator

[skipped]

### Type Assertions

A [**type assertion**](https://golang.org/ref/spec#Type_assertions) is an operation applied to an interface value. Syntactically, it looks like `x.(T)`, where `x` is an expression of an interface type and `T` is a type, called the "asserted" type. A type assertion checks that the dynamic type of its operand matches the asserted type, which has two possibilities as discussed below.

If the asserted type `T` is a concrete type, then the type assertion checks whether `x`'s dynamic type is identical to `T`. If this check succeeds, the result of the type assertion is `x`'s dynamic value, whose type is of course `T`. <u>In other words, a type assertion to a concrete type extracts the concrete value from its operand.</u> If the check fails, then the operation panics. For example:

```go
var w io.Writer
w = os.Stdout
f := w.(*os.File)      // success: f == os.Stdout
c := w.(*bytes.Buffer) // panic: interface holds *os.File, not *bytes.Buffer
```

If the asserted type `T` is an interface type, then the type assertion checks whether `x`'s dynamic type *satisfies* `T`. If this check succeeds, the dynamic value is not extracted; the result is still an interface value with the same type and value components, but the result has the interface type `T`. In other words, a type assertion to an interface type changes the type of the expression, making a different (and usually larger) set of methods accessible, but it preserves the dynamic type and value components inside the interface value.

After the first type assertion below, both `w` and `rw` hold `os.Stdout` so each has a dynamic type of `*os.File`, but `w`, an `io.Writer`, exposes only the file's `Write` method, whereas `rw` also exposes its `Read` method.

```go
var w io.Writer
w = os.Stdout
rw := w.(io.ReadWriter) // success: *os.File has both Read and Write

w = new(ByteCounter)
rw = w.(io.ReadWriter)  // panic: *ByteCounter has no Read method
```

If the operand is a nil interface value, the type assertion always fails. A type assertion to a less restrictive interface type (one with fewer methods) is rarely needed, as it behaves just like an assignment, except in the nil case.

```go
w = rw // io.ReadWriter is assignable to io.Writer
w = rw.(io.Writer) // fails only if rw == nil
```

When we're not sure of the dynamic type of an interface value, we can test whether it is some particular type. If the type assertion appears in an assignment in which two results are expected, such as the following declarations, the operation does not panic on failure but instead returns an additional second result, a boolean indicating success:

```go
var w io.Writer = os.Stdout
f, ok := w.(*os.File)      // success: ok, f == os.Stdout
b, ok := w.(*bytes.Buffer) // failure: !ok, b == nil
```

The second result is conventionally assigned to a variable named `ok`. If the operation failed, `ok` is false, and the first result is equal to the zero value of the asserted type, which in this example is a nil `*bytes.Buffer`.

The `ok` result is often immediately used to decide what to do next, as written in an `if` statement of the following form:

```go
if f, ok := w.(*os.File); ok {
	// ...use f...
}
```

When the operand of a type assertion is a variable, rather than invent another name for the new local variable, you'll sometimes see the original name reused, shadowing the original, like this:

```go
if w, ok := w.(*os.File); ok {
	// ...use w...
}
```

### Discriminating Errors with Type Assertions

Consider the set of errors returned by file operations in the `os` package. I/O can fail for any number of reasons, but three kinds of failure often must be handled differently:

* file already exists (for create operations)
* file not found (for read operations)
* permission denied

The `os` package provides three helper functions to classify the failure indicated by a given `error` value:

```go
package os

func IsExist(err error) bool
func IsNotExist(err error) bool
func IsPermission(err error) bool
```

A naïve implementation might check that the error message contains a certain substring:

```go
func IsNotExist(err error) bool {
	// NOTE: not robust!
	return strings.Contains(err.Error(), "file does not exist")
}
```

Because the logic for handling I/O errors can vary from one platform to another, this approach is not robust and the same failure may be reported with a variety of different error messages.

A more reliable approach is to represent structured error values using a dedicated type. The `os` package defines these types:

* `PathError`, which describes failures involving an operation on a file path, like `Open` or `Delete`
* A variant `LinkError`, which describes failures of operations involving two file paths, like `Symlink` and `Rename`

The following is `os.PathError`:

```go
package os

// PathError records an error and the operation and file path that caused it.
type PathError struct {
	Op string
	Path string
	Err error
}

func (e *PathError) Error() string {
	return e.Op + " " + e.Path + ": " + e.Err.Error()
}
```

Although `PathError`'s `Error` method forms a message by simply concatenating the fields, `PathError`'s structure preserves the underlying components of the error. Clients can use a [type assertion](#type-assertions) to detect the specific type of the error; the specific type provides more detail than a simple string.

```go
_, err := os.Open("/no/such/file")
fmt.Println(err) // "open /no/such/file: No such file or directory"
fmt.Printf("%#v\n", err)
// Output:
// &os.PathError{Op:"open", Path:"/no/such/file", Err:0x2}
```

That is how the three helper functions work. For example, `IsNotExist`, shown below, reports whether an error is equal to `syscall.ENOENT` ([Section 7.8](#the-error-interface)) or to the distinguished error `os.ErrNotExist` (see `io.EOF` in [Section 5.4.2](ch5.md#end-of-file-eof)), or is a `*PathError` whose underlying error is one of those two.

```go
import (
	"errors"
	"syscall"
)

var ErrNotExist = errors.New("file does not exist")

// IsNotExist returns a boolean indicating whether the error is known to
// report that a file or directory does not exist. It is satisfied by
// ErrNotExist as well as some syscall errors.
func IsNotExist(err error) bool {
	if pe, ok := err.(*PathError); ok {
		err = pe.Err
	}
	return err == syscall.ENOENT || err == ErrNotExist
}
```

This is how it is used:

```go
_, err := os.Open("/no/such/file")
fmt.Println(os.IsNotExist(err)) // "true"
```

`PathError`'s structure is lost if the error message is combined into a larger string, for instance by a call to `fmt.Errorf`. Error discrimination must usually be done immediately after the failing operation, before an error is propagated to the caller.

### Querying Behaviors with Interface Type Assertions

The code below is similar to the part of the [`net/http`](https://golang.org/pkg/net/http/) web server responsible for writing HTTP header fields. The `io.Writer w` represents the HTTP response; the bytes written to it are sent to the web browser.

```go
func writeHeader(w io.Writer, contentType string) error {
if _, err := w.Write([]byte("Content-Type: ")); err != nil {
		return err
	}
	if _, err := w.Write([]byte(contentType)); err != nil {
		return err
	}
	// ...
}
```

Because the `Write` method requires a byte slice, a `[]byte(...)` conversion from a string is required. This conversion allocates memory and makes a copy, but the copy is discarded almost immediately after. Can we avoid allocating memory here?

The [`io.Writer`](https://golang.org/pkg/io/#Writer) interface tells us only one fact about the concrete type that `w` holds: that bytes may be written to it. If we look behind the curtains of the `net/http` package, we see that the dynamic type that `w` holds in this program also has a `WriteString` method that allows strings to be efficiently written to it, avoiding the need to allocate a temporary copy. A number of important types that satisfy `io.Writer` also have a `WriteString` method, including `*bytes.Buffer`, `*os.File` and `*bufio.Writer`.

We cannot assume that an arbitrary `io.Writer w` also has the `WriteString` method. But we can define a new interface that has just this method and use a type assertion to test whether the dynamic type of `w` satisfies this new interface.

```go
// writeString writes s to w.
// If w has a WriteString method, it is invoked instead of w.Write.
func writeString(w io.Writer, s string) (n int, err error) {
	type stringWriter interface {
		WriteString(string) (n int, err error)
	}
	if sw, ok := w.(stringWriter); ok {
		return sw.WriteString(s) // avoid a copy
	}
	return w.Write([]byte(s)) // allocate temporary copy
}

func writeHeader(w io.Writer, contentType string) error {
	if _, err := writeString(w, "Content-Type: "); err != nil {
		return err
	}
	if _, err := writeString(w, contentType); err != nil {
		return err
	}
	// ...
}
```

The standard library provides it as [`io.WriteString`](https://golang.org/pkg/io/#WriteString); it is the recommended way to write a string to an `io.Writer`.

From this example, we realize that:

* There is no standard interface that defines the `WriteString` method and specifies its required behavior.
* Whether or not a concrete type satisfies the `stringWriter` interface is determined only by its methods, not by any declared relationship between it and the interface type.

What this means is that the technique above relies on the assumption that if a type satisfies the interface below, then `WriteString(s)` must have the same effect as `Write([]byte(s))`.

```go
interface {
	io.Writer
	WriteString(s string) (n int, err error)
}
```

Although `io.WriteString` documents its assumption, few functions that call it are likely to document that they make the same assumption. Defining a method of a particular type is taken as an implicit assent for a certain behavioral contract. This lack of explicit intention seems unsettling, but it is rarely a problem in practice. With the exception of the empty interface `interface{}`, interface types are seldom satisfied by unintended coincidence.

The `writeString` function above uses a type assertion to see whether a value of a general interface type also satisfies a more specific interface type, and if so, it uses the behaviors of the specific interface. This technique can be put to good use whether or not the queried interface is standard like `io.ReadWriter` or user-defined like `stringWriter`.

It's also how `fmt.Fprintf` distinguishes values that satisfy `error` or `fmt.Stringer` from all other values. Within `fmt.Fprintf`, there is a step that converts a single operand to a string, something like this:

```go
package fmt

func formatOneValue(x interface{}) string {
	if err, ok := x.(error); ok {
		return err.Error()
	}
	if str, ok := x.(Stringer); ok {
		return str.String()
	}
	// ...all other types...
}
```

If `x` satisfies either of the two interfaces, that determines the formatting of the value. If not, the default case handles all other types more or less uniformly using [reflection](https://blog.golang.org/laws-of-reflection), which is discussed in [Chapter 12](ch12.md).

Again, this makes the assumption that any type with a `String` method satisfies the behavioral contract of `fmt.Stringer`, which is to return a string suitable for printing.

### Type Switches

Interfaces are used in two distinct styles.

1. The first style is exemplified by interfaces such as `io.Reader`, `io.Writer`, `fmt.Stringer`, `sort.Interface`, `http.Handler`, and `error`.
    * In this style, an interface's methods express the similarities of the concrete types that satisfy the interface but hide the representation details and intrinsic operations of those concrete types.
    * The emphasis is on the methods, not on the concrete types.
2. The second style exploits the ability of an interface value to hold values of a variety of concrete types and considers the interface to be the *union* of those types.
    * Type assertions are used to discriminate among these types dynamically and treat each case differently.
    * The emphasis is on the concrete types that satisfy the interface, not on the interface's methods, and there is no hiding of information.
    * The interfaces used this way are described as [discriminated unions](https://en.wikipedia.org/wiki/Tagged_union).

In object-oriented programming, these two styles may be recognized as [subtype polymorphism](https://en.wikipedia.org/wiki/Subtyping) and [ad hoc polymorphism](https://en.wikipedia.org/wiki/Ad_hoc_polymorphism).

Go's API for querying an SQL database separates the fixed part of a query from the variable parts. In the following example:

```go
import "database/sql"
func listTracks(db sql.DB, artist string, minYear, maxYear int) {
	result, err := db.Exec(
		"SELECT * FROM tracks WHERE artist = ? AND ? <= year AND year <= ?",
		artist, minYear, maxYear)
	// ...
}
```

The `Exec` method replaces each '`?`' in the query string with an SQL literal denoting the corresponding argument value. Constructing queries this way helps avoid SQL injection attacks, in which an adversary takes control of the query by exploiting improper quotation of input data.

Within `Exec`, we might find a function like the one below, which converts each argument value to its literal SQL notation.

```go
func sqlQuote(x interface{}) string {
	if x == nil {
		return "NULL"
	} else if _, ok := x.(int); ok {
		return fmt.Sprintf("%d", x)
	} else if _, ok := x.(uint); ok {
		return fmt.Sprintf("%d", x)
	} else if b, ok := x.(bool); ok {
		if b {
			return "TRUE"
		}
		return "FALSE"
	} else if s, ok := x.(string); ok {
		return sqlQuoteString(s) // (not shown)
	} else {
		panic(fmt.Sprintf("unexpected type %T: %v", x, x))
	}
}
```

A `switch` statement simplifies an `if`-`else` chain that performs a series of value equality tests. An analogous [type switch](https://golang.org/doc/effective_go.html#type_switch) statement simplifies an `if`-`else` chain of type assertions.

In its simplest form:

* A type switch looks like an ordinary `switch` statement in which the operand is `x.(type)` (that's literally the keyword `type`) and each case has one or more types.
* A type switch enables a multi-way branch based on the interface value's dynamic type. The `nil` case matches if `x == nil`, and the `default` case matches if no other case does.

A type switch for `sqlQuote` would have these cases:

```go
switch x.(type) {
case nil:       // ...
case int, uint: // ...
case bool:      // ...
case string:    // ...
default:        // ...
}
```

As with an ordinary `switch` statement ([Section 1.8](ch1.md#loose-ends)):

* Cases are considered in order. When a match is found, the case's body is executed.
* Case order becomes significant when one or more case types are interfaces, since then there is a possibility of two cases matching.
* The position of the `default` case relative to the others is immaterial.
* No `fallthrough` is allowed.

In the original function, the logic for the `bool` and `string` cases needs access to the value extracted by the type assertion. The type switch statement has an extended form that binds the extracted value to a new variable within each case:

```go
switch x := x.(type) { /* ... */ }
```

The new variables is called `x`, since reuse of variable names is common, as with type assertions. Like a `switch` statement, a type switch implicitly creates a lexical block, so the declaration of the new variable called `x` does not conflict with a variable `x` in an outer block. Each case also implicitly creates a separate lexical block.

`sqlQuote` can be rewritten to use the extended form of type switch:

```go
func sqlQuote(x interface{}) string {
	switch x := x.(type) {
	case nil:
		return "NULL"
	case int, uint:
		return fmt.Sprintf("%d", x) // x has type interface{} here.
	case bool:
		if x {
			return "TRUE"
		}
		return "FALSE"
	case string:
		return sqlQuoteString(x) // (not shown)
	default:
		panic(fmt.Sprintf("unexpected type %T: %v", x, x))
	}
}
```

In the above code:

* Within the block of each single-type case, the variable `x` has the same type as the case.
    * For instance, `x` has type `bool` within the `bool` case and `string` within the `string` case.
* In all other cases, `x` has the (interface) type of the `switch` operand, which is `interface{}`.
* When the same action is required for multiple cases, like `int` and `uint`, the type switch makes it easy to combine them.

Although `sqlQuote` accepts an argument of any type, the function runs to completion only if the argument's type matches one of the cases in the type switch; otherwise it panics with an "unexpected type" message. Although the type of `x` is `interface{}`, we consider it a discriminated union of `int`, `uint`, `bool`, `string`, and `nil`.

### Example: Token-Based XML Decoding

[Section 4.5](ch4.md#json) showed how to decode JSON documents into Go data structures with the `Marshal` and `Unmarshal` functions from the `encoding/json` package. The `encoding/xml` package provides a similar API.

This approach is convenient when we want to construct a representation of the document tree, but that's unnecessary for many programs. The `encoding/xml` package also provides a lower-level token-based API for decoding XML. In the token-based style, the parser consumes the input and produces a stream of tokens, primarily of four kinds:

* `StartElement`
* `EndElement`
* `CharData`
* `Comment`

Each of them is a concrete type in the `encoding/xml` package. Each call to `(*xml.Decoder).Token` returns a token. The relevant parts of the API are shown here:

```go
package xml

type Name struct {
	Local string // e.g., "Title" or "id"
}

type Attr struct { // e.g., name="value"
	Name Name
	Value string
}

// A Token includes StartElement, EndElement, CharData,
// and Comment, plus a few esoteric types (not shown).
type Token interface{}
type StartElement struct { // e.g., <name>
	Name Name
	Attr []Attr
}
type EndElement struct { Name Name } // e.g., </name>
type CharData []byte                 // e.g., <p>CharData</p>
type Comment []byte                  // e.g., <!-- Comment -->

type Decoder struct{ /* ... */ }
func NewDecoder(io.Reader) *Decoder
func (*Decoder) Token() (Token, error) // returns next Token in sequence
```

The `Token` interface, which has no methods, is also an example of a discriminated union.

* The purpose of a traditional interface like `io.Reader` is to hide details of the concrete types that satisfy it so that new implementations can be created; each concrete type is treated uniformly.
* By contrast, the set of concrete types that satisfy a discriminated union is fixed by the design and exposed, not hidden. Discriminated union types have few methods; functions that operate on them are expressed as a set of cases using a type switch, with different logic in each case.

The `xmlselect` program below extracts and prints the text found beneath certain elements in an XML document tree. Using the API above, it can do its job in a single pass over the input without ever materializing the tree.

<small>[gopl.io/ch7/xmlselect/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch7/xmlselect/main.go)</small>

```go
// Xmlselect prints the text of selected elements of an XML document.
package main

import (
	"encoding/xml"
	"fmt"
	"io"
	"os"
	"strings"
)

func main() {
	dec := xml.NewDecoder(os.Stdin)
	var stack []string // stack of element names
	for {
		tok, err := dec.Token()
		if err == io.EOF {
			break
		} else if err != nil {
			fmt.Fprintf(os.Stderr, "xmlselect: %v\n", err)
			os.Exit(1)
		}
		switch tok := tok.(type) {
		case xml.StartElement:
			stack = append(stack, tok.Name.Local) // push
		case xml.EndElement:
			stack = stack[:len(stack)-1] // pop
		case xml.CharData:
			if containsAll(stack, os.Args[1:]) {
				fmt.Printf("%s: %s\n", strings.Join(stack, " "), tok)
			}
		}
	}
}

// containsAll reports whether x contains the elements of y, in order.
func containsAll(x, y []string) bool {
	for len(y) <= len(x) {
		if len(y) == 0 {
			return true
		}
		if x[0] == y[0] {
			y = y[1:]
		}
		x = x[1:]
	}
	return false
}
```

* Each time the loop in main encounters a `StartElement`, it pushes the elements' name onto a stack, and for each `EndElement` it pops the name from the stack.
* The API guarantees that the sequence of `StartElement` and `EndElement` tokens will be properly matched, even in illformed documents.
* `Comments` are ignored.
* When `xmlselect` encounters a `CharData`, it prints the text only if the stack contains all the elements named by the command-line arguments, in order.

The command below prints the text of any `h2` elements appearing beneath two levels of `div` elements.

```text
$ go build gopl.io/ch1/fetch
$ ./fetch http://www.w3.org/TR/2006/REC-xml11-20060816 |
    ./xmlselect div div h2
html body div div h2: 1 Introduction
html body div div h2: 2 Documents
html body div div h2: 3 Logical Structures
html body div div h2: 4 Physical Structures
html body div div h2: 5 Conformance
html body div div h2: 6 Notation
html body div div h2: A References
html body div div h2: B Definitions for Character Normalization
...
```

### A Few Words of Advice

When designing a new package, novice Go programmers often start by creating a set of interfaces and only later define the concrete types that satisfy them. This approach is not recommended, because:

* It results in many interfaces, each of which has only a single implementation. These interfaces are unnecessary abstractions.
* These interfaces also have a run-time cost.

You can restrict which methods of a type or fields of a struct are visible outside a package using the export mechanism ([Section 6.6](ch6.md#encapsulation)). Interfaces are only needed when there are two or more concrete types that must be dealt with in a uniform way.

An exception to this rule is: when an interface is satisfied by a single concrete type but that type cannot live in the same package as the interface because of its dependencies. In that case, an interface is a good way to decouple two packages.

Because interfaces are used only when they are satisfied by two or more types, they necessarily abstract away from the details of any particular implementation. The result is smaller interfaces with fewer, simpler methods, often just one as with `io.Writer` or `fmt.Stringer.` Small interfaces are easier to satisfy when new types come along. A good rule of thumb for interface design is *ask only for what you need*.

With methods and interfaces, Go has great support for the object-oriented style of programming, but this does not mean you need to use it exclusively. Not everything need be an object; standalone functions have their place, as do unencapsulated data types.


### Doubts and Solution

#### Verbatim

##### **p210 on assumption of `WriteString`**

> Although `io.WriteString` documents its assumption, few functions that call it are likely to document that they make the same assumption. Defining a method of a particular type is taken as an implicit assent for a certain behavioral contract.

<span class="text-danger">Question</span>: What does it mean?
