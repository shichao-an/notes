### **Chapter 1. Tutorial**

This chapter is a tour of the basic components of Go. We hope to provide enough information and examples to get you off the ground and doing useful things as quickly as possible.

When you’re learning a new language, there’s a natural tendency to write code as you would have written it in a language you already know. Be aware of this bias as you learn Go and try to avoid it. We’ve tried to illustrate and explain how to write good Go, so use the code here as a guide when you’re writing your own.

### Hello, World

We'll start with the now-traditional "hello, world" example, which appears at the beginning of [*The C Programming Language*](https://en.wikipedia.org/wiki/The_C_Programming_Language), published in 1987.

<small>[gopl.io/ch1/helloworld/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/helloworld/main.go)</small>

```go
package main

import "fmt"

func main() {
	fmt.Println("Hello, 世界")
}
```

Go is a compiled language:

* The Go toolchain converts a source program and the things it depends on into instructions in the native machine language of a computer.
* These tools are accessed through a single command called `go` that has a number of subcommands. The simplest of these subcommands is `run`, which compiles the source code from one or more source files whose names end in `.go`, links it with libraries, then runs the resulting executable file.

```shell-session
$ go run helloworld.go
```

Go natively handles Unicode, so it can process text in all the world’s languages.

If the program is more than a one-shot experiment, you can compile it once and save the compiled result for later use, which is done with `go build`:

```shell-session
$ go build helloworld.go
```

This creates an executable binary file called `helloworld` that can be run any time without further processing:

```shell-session
$ ./helloworld
Hello, 世界
```

If you run `go get gopl.io/ch1/helloworld`, it will fetch the source code and place it in the corresponding directory. There’s more about this topic in [Section 2.6](ch2.md#packages-and-files) and [Section 10.7](ch10.md#the-go-tool).

Go code is organized into packages (similar to libraries or modules in other languages). A package consists of `.go` source files in a single directory that define what the package does. Each source file begins with the following things in order:

1. A package declaration (e.g. `package main`) that states which package the file belongs to,
2. A list of other packages that it imports,
3. The declarations of the program that are stored in that file.

Package `main` is special. It defines a standalone executable program, not a library. Within package `main` the function `main` is also special: it’s where execution of the program begins. `main` will normally call upon functions in other packages to do much of the work, such as the function `fmt.Println`.

The `import` declaration tells the compiler what packages are needed by this source file. The "hello, world" program uses only one function from one other package, but most programs will import more packages.  You must import exactly the packages you need. <u>A program will not compile if there are missing imports or if there are unnecessary ones.</u> This strict requirement prevents references to unused packages from accumulating as programs evolve.

The `import` declarations must follow the package declaration. After that, a program consists of the declarations of functions, variables, constants, and types (keywords `func`, `var`, `const`, and `type`); for the most part, the order of declarations does not matter. This program is about as short as possible since it declares only one function, which in turn calls only one other function.

A function declaration consists of the keyword `func`, the name of the function, a parameter
list (empty for `main`), a result list (also empty here), and the body of the function enclosed in braces. This is detailed in [Chapter 5](ch5.md).

Go does not require semicolons at the ends of statements or declarations, except where two or more appear on the same line. In effect, newlines following certain tokens are converted into semicolons, so where newlines are placed matters to proper parsing of Go code. For instance, the opening brace `{` of the function must be on the same line as the end of the `func` declaration, not on a line by itself, and in the expression `x + y`, a newline is permitted after but not before the `+` operator.

Go takes a strong stance on code formatting. The `gofmt` tool rewrites code into the standard format, and the go tool’s `fmt` subcommand applies `gofmt` to all the files in the specified package, or the ones in the current directory by default. All Go source files in the book have been run through `gofmt`. <u>Declaring a standard format by fiat eliminates a lot of pointless debate about trivia and, more importantly, enables a variety of automated source code transformations that would be infeasible if arbitrary formatting were allowed.</u>

Many text editors can be configured to run `gofmt` each time you save a file, so that your source code is always properly formatted. A related tool, `goimports`, additionally manages the insertion and removal of import declarations as needed. It is not part of the standard distribution but you can obtain it with this command:

```shell-session
$ go get golang.org/x/tools/cmd/goimports
```

For most users, the usual way to download and build packages, run their tests, show their documentation, and so on, is with the go tool.

### Command-Line Arguments

The `os` package provides functions and other values for dealing with the operating system in a platform-independent fashion. Command-line arguments are available to a program as the variable `os.Args`.

#### Slice `os.Args` *

The variable `os.Args` is a slice of strings. Slices are a fundamental notion in Go. For now, think of a slice as a dynamically sized sequence `s` of array elements where:

* Individual elements can be accessed as `s[i]`;
* A contiguous subsequence can be accessed as `s[m:n]`.
* The number of elements is given by `len(s)`.
* As in most other programming languages, all indexing in Go uses half-open intervals that include the first index but exclude the last, because it simplifies logic. For example, the slice `s[m:n]`, where `0` ≤ `m` ≤ `n` ≤ `len(s)`, contains `n-m` elements.

The first element of `os.Args`, `os.Args[0]`, is the name of the command itself; the other elements are the arguments that were presented to the program when it started execution. A slice expression of the form `s[m:n]` yields a slice that refers to elements `m` through `n-1`, so the elements we need for our next example are those in the slice `os.Args[1:len(os.Args)]`. If `m` or `n` is omitted, it defaults to 0 or `len(s)` respectively, so we can abbreviate the desired slice as `os.Args[1:]`.

#### Example implementation of Unix `echo` command *

The following is an implementation of the Unix `echo` command, which prints its command-line arguments on a single line. <u>It imports two packages, which are given as a parenthesized list rather than as individual import declarations. Either form is legal, but conventionally the list form is used. The order of imports doesn’t matter; the `gofmt` tool sorts the package names into alphabetical order.</u>

<small>[gopl.io/ch1/echo1/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/echo1/main.go)</small>

```go
// Echo1 prints its command-line arguments.
package main

import (
	"fmt"
	"os"
)

func main() {
	var s, sep string
	for i := 1; i < len(os.Args); i++ {
		s += sep + os.Args[i]
		sep = " "
	}
	fmt.Println(s)
}
```
#### Comments that describe the program *

Comments begin with `//`. By convention, we describe each package in a comment immediately preceding its package declaration; for a `main` package, this comment is one or more complete sentences that describe the program as a whole.

#### Variables, declarations and assignment *

The `var` declaration declares two variables `s` and `sep`, of type `string`. A variable can be initialized as part of its declaration. If it is not explicitly initialized, it is implicitly initialized to the [zero value](https://golang.org/ref/spec#The_zero_value) for its type, which is 0 for numeric types and the empty string "" for strings. In this example, the declaration implicitly initializes `s` and `sep` to empty strings. Variables and declarations are detailed in [Chapter 2](ch2.md).

The statement:

```go
s += sep + os.Args[i]
```

is an **assignment statement** that concatenates the old value of `s` with `sep` and `os.Args[i]` and assigns it back to `s`; it is equivalent to:

```go
s = s + sep + os.Args[i]
```

The operator `+=` is an **assignment operator**. Each arithmetic and logical operator like + or * has a corresponding assignment operator.

A number of improved versions of `echo` will be shown in this chapter and the next that will deal with any real inefficiency.

#### `for` loop

The loop index variable `i` is declared in the first part of the `for` loop. The `:=` symbol is part of a **short variable declaration**, a statement that declares one or more variables and gives them appropriate types based on the initializer values (detailed in the next chapter). The increment statement `i++` adds 1 to `i`; it’s equivalent to `i += 1` which is in turn equivalent to `i = i + 1`. There’s a corresponding decrement statement `i--` that subtracts 1. These are statements, not expressions as they are in most languages in the C family, so `j = i++` is illegal, and they are postfix only, so `--i` is not legal either.

The `for` loop is the only loop statement in Go. It has a number of forms, one of which is illustrated here:

```text
for initialization; condition; post {
	// zero or more statements
}
```

