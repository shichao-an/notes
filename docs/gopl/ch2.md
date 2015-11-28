### **Chapter 2. Program Structure**

This chapter provides details about the basic structural elements of a Go program.

### Names

In Go, the names of functions, variables, constants, types, statement labels, and packages follow a simple rule: a name begins with a letter (anything that Unicode deems a letter) or an underscore and may have any number of additional letters, digits, and underscores. The names are case-sensitive: `heapSort` and `Heapsort` are different names.

Go has 25 keywords like `if` and `switch` that may be used only where the syntax permits; they can’t be used as names.

 | | |
-|-|-|-
`break`|`default`|`func`|`interface`|`select`
`case`|`defer`|`go`|`map`|`struct`
`chan`|`else`|`goto`|`package`|`switch`
`const`|`fallthrough`|`if`|`range`|`type`
`continue`|`for`|`import`|`return`|`var`

In addition, there are about three dozen *predeclared* names like `int` and `true` for built-in constants, types, and functions:

 |
-|-
Constants: | `true` `false` `iota` `nil`
Types: | `int` `int8` `int16` `int32` `int64` `uint` `uint8` `uint16` `uint32` `uint64` `uintptr` `float32` `float64` `complex128` `complex64` `bool` `byte` `rune` `string` `error`
Functions: | `make` `len` `cap` `new` `append` `copy` `close` `delete` `complex` `real` `imag` `panic` `recover`

These names are not reserved, so you may use them in declarations. Beware of the potential for confusion.

#### Local and exported names *

If an entity is:

* Declared within a function: it is *local* to that function.
* Declared outside of a function: it is visible in all files of the package to which it belongs.

The case of the first letter of a name determines its visibility across package boundaries:

* If the name begins with an upper-case letter, it is *exported* (visible and accessible outside of its own package and may be referred to by other parts of the program), as with `Printf` in the `fmt` package.
* Package names themselves are always in lower case.

#### Naming convention and style *

* There is no limit on name length;
* Short names are preferred, especially for local variables with small scopes (`i` is better than `theLoopIndex`);
* The larger the scope of a name, the longer and more meaningful it should be.
* [Camel case](https://en.wikipedia.org/wiki/CamelCase) are used when forming names by combining words, e.g. `QuoteRuneToASCII` and `parseRequestLine` (instead of `quote_rune_to_ASCII` or `parse_request_line`).
* The letters of acronyms and initialisms like `ASCII` and `HTML` are always rendered in the same case, so a function might be called `htmlEscape`, `HTMLEscape`, or `escapeHTML`, but not `escapeHtml`.


### Declarations

A **declaration** names a program entity and specifies its properties. There are four major kinds of declarations:

1. `var` (variables)
2. `const` (constants)
3. `type` (types)
4. `func` (functions)

This chapter discusses variables and types. Constants are disucssed in [Chapter 3](ch3.md), and functions in [Chapter 5](ch5.md).

Each `.go` file has declarations in the following order:

1. A `package` declaration that says what package the file is part of.
2. Any `import` declarations
3. A sequence of package-level declarations of types, variables, constants, and functions, in any order.

For example, the following program declares a constant, a function, and a couple of variables:

<small>[gopl.io/ch2/boiling/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch2/boiling/main.go)</small>

```go
// Boiling prints the boiling point of water.
package main

import "fmt"

const boilingF = 212.0

func main() {
	var f = boilingF
	var c = (f - 32) * 5 / 9
	fmt.Printf("boiling point = %g°F or %g°C\n", f, c)
	// Output:
	// boiling point = 212°F or 100°C
}
```

* Each package-level name is visible in all the files of the package.
* Local declarations are visible only within the function in which they are declared.

A function declaration has a name, a list of parameters an optional list of results (omitted if the function does not return anything), and the function body.

### Variables

A `var` declaration creates a variable of a particular type, attaches a name to it, and sets its initial value, with the general form:

```go
var name type = expression
```

<u>Either the type or the `= expression` part may be omitted, but not both:</u>

* If the type is omitted, it is determined by the initializer expression.
* If the expression is omitted, the initial value is the **zero value** for the type, which is:
    * 0 for numbers
    * `false` for booleans
    * `""` for strings
    * `nil` for interfaces and reference types (slice, pointer, map, channel, function).

The zero value of an aggregate type like an array or a struct has the zero value of all of its elements or fields.

The zero-value mechanism ensures that a variable always holds a well-defined value of its type; in Go there is no such thing as an uninitialized variable. This simplifies code and often ensures sensible behavior of boundary conditions without extra work. For example,

```go
var s string
fmt.Println(s) // ""
```

Go programmers often go to some effort to make the zero value of a more complicated type meaningful, so that variables begin life in a useful state.

It is possible to declare and optionally initialize a set of variables in a single declaration, with a matching list of expressions. Omitting the type allows declaration of multiple variables of different types:

```go
var i, j, k int // int, int, int
var b, f, s = true, 2.3, "four" // bool, float64, string
```

* Initializers may be literal values or arbitrary expressions.
* Package-level variables are initialized before `main` begins ([Section 2.6.2](#package-initialization)).
* Local variables are initialized as their declarations are encountered during function execution.

A set of variables can also be initialized by calling a function that returns multiple values:

```go
var f, err = os.Open(name) // os.Open returns a file and an error
```

#### Short Variable Declarations

Within a function, an alternate form called a short variable declaration may be used to declare and initialize local variables. It takes the form `name := expression`, and the type of name is determined by the type of expression. For exmaple ([Animated GIFs](ch1.md#animated-gifs)),

##### **When to use short variable declaration and `var` declaration** *

* Short variable declarations are used to declare and initialize the majority of local variables, for brevity and flexibility.
* A `var` declaration tends to be reserved for:
    * Local variables that need an explicit type that differs from that of the initializer expression;
    * Local variables when they will be assigned a value later and its initial value is unimportant.

```go
i := 100 // an int
var boiling float64 = 100 // a float64
var names []string
var err error
var p Point
```

As with `var` declarations, multiple variables may be declared and initialized in the same short variable declaration:

```go
i, j := 0, 1
```

However, declarations with multiple initializer expressions should be used only when they help readability, such as for short and natural groupings like the initialization part of a for loop.

Keep in mind that `:=` is a declaration, whereas `=` is an assignment. A multi-variable declaration should not be confused with a [tuple assignment](#tuple-assignment), in which each variable on the left-hand side is assigned the corresponding value from the right-hand side:

```go
i, j = j, i // swap values of i and j
```

Like `var` declarations, short variable declarations may be used for calls to functions like `os.Open` that return two or more values:

```go
f, err := os.Open(name)
	if err != nil {
		return err
}
// ...use f...
f.Close()
```

##### **One subtle but important point** *

A short variable declaration does not necessarily declare all the variables on its left-hand side. If some of them were already declared in the same lexical block , then the short variable declaration acts like an assignment to those variables. For example,

```go
in, err := os.Open(infile)
// ...
out, err := os.Create(outfile)
```

In the above code:

* The first statement declares both `in` and `err`.
* The second declares `out` but only assigns a value to the existing `err` variable.

A short variable declaration must declare at least one new variable. Therefore, the following code will not compile:

```go
f, err := os.Open(infile)
// ...
f, err := os.Create(outfile) // compile error: no new variables
```

The fix is to use an ordinary assignment for the second statement.

A short variable declaration acts like an assignment only to variables that were already declared in the same lexical block; declarations in an outer block are ignored.

#### Pointers

A **variable** is a piece of storage containing a value.

* Variables created by declarations are identified by a name, such as `x`
* Many other variables are identified only by expressions like `x[i]` or `x.f`.

All these expressions read the value of a variable, except when they appear on the lefthand side of an assignment, in which case a new value is assigned to the variable.

A **pointer** value is the address of a variable. A pointer is thus the location at which a value is stored. Not every value has an address, but every variable does. With a pointer, we can read or update the value of a variable indirectly, without using or even knowing the name of the variable, if indeed it has a name.

##### **Pointer type (`*type`) and address-of (`&`) operators** *

If a variable is declared `var x int`, the expression `&x` ("address of `x`") yields a pointer to an integer variable (a value of type `*int`, which is pronounced "pointer to `int`"). If this value is called `p`, we say "`p` points to `x`", or equivalently "`p` contains the address of `x`". The variable to which `p` points is written `*p`. The expression `*p` yields the value of that variable, an `int`, but since `*p` denotes a variable, it may also appear on the left-hand side of an assignment, in which case the assignment updates the variable.

```go
x := 1
p := &x          // p, of type *int, points to x
fmt.Println(*p)  // "1"
*p = 2           // equivalent to x = 2
fmt.Println(x)   // "2"
```

Each component of a variable of aggregate type: a field of a struct or an element of an array, is also a variable and thus has an address too.

Variables are sometimes described as *addressable* values. Expressions that denote variables are the only expressions to which the *address-of* operator `&` may be applied.

##### **Comparing pointers** *

The zero value for a pointer of any type is `nil`. The test `p != nil` is true if `p` points to a variable. Pointers are comparable; two pointers are equal if and only if they point to the same variable or both are `nil`.

```go
var x, y int
fmt.Println(&x == &x, &x == &y, &x == nil) // "true false false"
```

<u>It is perfectly safe for a function to return the address of a local variable.</u> For example:

```go
var p = f()

func f() *int {
	v := 1
	return &v
}
```

<u>The local variable `v` created by this particular call to `f` will remain in existence even after the call has returned, and the pointer `p` will still refer to it.</u> Each call of `f` returns a distinct value:

```go
fmt.Println(f() == f()) // "false"
```




### Doubts and Solutions

#### Verbatim

p32 on short variable declaration.

> A short variable declaration acts like an assignment only to variables that were already declared in the same lexical block; declarations in an outer block are ignored.

What does "declarations in an outer block are ignored" mean?
