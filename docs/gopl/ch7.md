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
