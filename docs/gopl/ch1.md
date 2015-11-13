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
