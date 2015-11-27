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

#### `for` loop *

The loop index variable `i` is declared in the first part of the `for` loop. The `:=` symbol is part of a **short variable declaration**, a statement that declares one or more variables and gives them appropriate types based on the initializer values (detailed in the next chapter). The increment statement `i++` adds 1 to `i`; it’s equivalent to `i += 1` which is in turn equivalent to `i = i + 1`. There’s a corresponding decrement statement `i--` that subtracts 1. These are statements, not expressions as they are in most languages in the C family, so `j = i++` is illegal, and they are postfix only, so `--i` is not legal either.

The `for` loop is the only loop statement in Go. It has a number of forms, one of which is illustrated here:

```text
for initialization; condition; post {
	// zero or more statements
}
```

In the above form, parentheses are never used around the three components of a `for` loop. The braces are mandatory, and the opening brace must be on the same line as the *post* statement. The three statements are:

* The optional *initialization* statement is executed before the loop starts. If it is present, it must be a **simple statement**, which is one of the following:
    * A short variable declaration,
    * An increment or assignment statement,
    * A function call.
* The *condition* is a boolean expression evaluated at the beginning of each iteration of the loop; if it evaluates to true, the statements controlled by the loop are executed.
* The *post* statement is executed after the body of the loop, then the condition is evaluated again. The loop ends when the condition becomes false.  Any of these parts may be omitted. If there is no initialization and no post, the semicolons may also be omitted:

If there is no *initialization* and no *post*, the semicolons may also be omitted:

##### **`for` as a "while" loop** *

```go
// a traditional "while" loop
for condition {
	// ...
}
```

If the *condition* is omitted entirely in any of these forms, for example in

```go
// a traditional infinite loop
for {
// ...
}
```

This loop is infinite, though it may be terminated in some other way, like a `break` or `return` statement.

##### **`for` as iteration** *

Another form of the for loop iterates over a range of values from a data type like a string or a slice:

<small>[gopl.io/ch1/echo2/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/echo2/main.go)</small>

```go
// Echo2 prints its command-line arguments.
package main

import (
	"fmt"
	"os"
)

func main() {
	s, sep := "", ""
	for _, arg := range os.Args[1:] {
		s += sep + arg
		sep = " "
	}
	fmt.Println(s)
}
```

In each iteration, `range` produces a pair of values: the index and the value of the element at that index. Here, we don’t need the index, but the `range` loop requires that we deal with both the element and the index. Since Go does not permit unused local variables (which would result in a compilation error), the solution is to use the **blank identifier**, whose name is `_` (an underscore). The blank identifier may be used whenever syntax requires a variable name but program logic does not, for instance to discard an unwanted loop index when we require only the element value.

##### **Equivalent ways of declaring string variables** *

There are several ways to declare a string variable; these are all equivalent:

```go
s := ""
var s string
var s = ""
var s string = ""
```

1. The first form is a short variable declaration and is the most compact, but it may be used only within a function, not for package-level variables.
2. The second form relies on default initialization to the zero value for strings, which is "".
3. The third form is rarely used except when declaring multiple variables.
4. The fourth form is explicit about the variable’s type, which is redundant when it is the same as that of the initial value but necessary in other cases where they are not of the same type.

In practice, you should generally use one of the first two forms, with explicit initialization to say that the initial value is important and implicit initialization to say that the initial value doesn’t matter.

Each time around the loop, the string s gets completely new contents. The `+=` statement makes a new string by concatenating the old string, a space character, and the next argument, then assigns the new string to `s`. <u>The old contents of `s` are no longer in use, so they will be garbage-collected in due course.</u>

##### **`strings.Join` function**

If the amount of data involved is large, this could be costly. A simpler and more efficient solution would be to use the `Join` function from the `strings` package:

<small>[gopl.io/ch1/echo3/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/echo3/main.go)</small>

```go
func main() {
	fmt.Println(strings.Join(os.Args[1:], " "))
}
```
If we don’t care about format but just want to see the values, perhaps for debugging, we can let `Println` format the results for us:

```go
fmt.Println(os.Args[1:])
```

### Finding Duplicate Lines

This section shows three variants of a program called `dup`; it is partly inspired by the Unix `uniq` command, which looks for adjacent duplicate lines.

The first version of `dup` prints each line that appears more than once in the standard input, preceded by its count. This program introduces the following:

* `if` statement
* `map` data type
* `bufio` package

<small>[gopl.io/ch1/dup1/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/dup1/main.go)</small>

```go
// Dup1 prints the text of each line that appears more than
// once in the standard input, preceded by its count.
package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	counts := make(map[string]int)
	input := bufio.NewScanner(os.Stdin)
	for input.Scan() {
		counts[input.Text()]++
	}
	// NOTE: ignoring potential errors from input.Err()
	for line, n := range counts {
		if n > 1 {
			fmt.Printf("%d\t%s\n", n, line)
		}
	}
}
```

#### `if` statement *

As with `for`, parentheses are never used around the condition in an `if` statement, but braces are required for the body. There can be an optional `else` part that is executed if the condition is false.

#### `map` that holds `counts` *

A **map** holds a set of key/value pairs and provides constant-time operations to store, retrieve, or test for an item in the set.

* The key may be of any type whose values can compared with `==`, strings being the most common example;
* The value may be of any type at all.

In this example, the keys are `string`s and the values are `int`s. The built-in function `make` creates a new empty map. Maps are detailed in [Section 4.3](ch4.md#maps).

The statement `counts[input.Text()]++` is equivalent to these two statements:

```go
line := input.Text()
counts[line] = counts[line] + 1
```

It’s not a problem if the map doesn’t yet contain that key. The first time a new line is seen, the expression `counts[line]` on the right-hand side evaluates to the zero value for its type, which is 0 for `int`.

To print the results, we use another `range`-based `for` loop, this time over the `counts` map. Each iteration produces two results, a key and the value of the map element for that key. <u>The order of map iteration is not specified, but in practice it is random, varying from one run to another. This design is intentional, since it prevents programs from relying on any particular ordering where none is guaranteed.</u>

#### `bufio.Scanner` function

The `bufio` package helps make input and output efficient and convenient. One of its most useful features is a type called `Scanner` that reads input and breaks it into lines or words; it’s often the easiest way to process input that comes naturally in lines.

The program uses a short variable declaration to create a new variable `input` that refers to a `bufio.Scanner`:

```go
input := bufio.NewScanner(os.Stdin)
```

The scanner reads from the program’s standard input. Each call to `input.Scan()` reads the next line and removes the newline character from the end; the result can be retrieved by calling `input.Text()`. The `Scan` function returns `true` if there is a line and `false` when there is no more input.

#### `fmt.Printf` function

The function `fmt.Printf` produces formatted output from a list of expressions. Its first argument is a format string that specifies how subsequent arguments should be formatted. The format of each argument is determined by a conversion character, a letter following a percent sign.

 |
-|-
`%d` | decimal integer
`%x`, `%o`, `%b` | integer in hexadecimal, octal, binary
`%f`, `%g`, `%e` | floating-point number: `3.141593` `3.141592653589793` `3.141593e+00`
`%t` | boolean: `true` or `false`
`%c` | rune (Unicode code point)
`%s` | string
`%q` | quoted string `"abc"` or rune `'c'`
`%v` | any value in a natural format
`%T` | type of any value
`%%` | literal percent sign (no operand)

`\t` (tab) and `\n` (newline) are **escape sequences** for representing otherwise invisible characters. `Printf` does not write a newline by default. By convention:

* Formatting functions whose names end in `f`, such as `log.Printf` and `fmt.Errorf`, use the formatting rules of `fmt.Printf`;
* Formatting functions whose names end in `ln` use the formatting rules of `fmt.Println`, formatting their arguments as if by `%v`, followed by a newline.

#### `os.Open` function

The next version of `dup` can read from the standard input or handle a list of file names, using `os.Open` to open each one:

<small>[gopl.io/ch1/dup2/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/dup2/main.go)</small>

```go
// Dup2 prints the count and text of lines that appear more than once
// in the input.  It reads from stdin or from a list of named files.
package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	counts := make(map[string]int)
	files := os.Args[1:]
	if len(files) == 0 {
		countLines(os.Stdin, counts)
	} else {
		for _, arg := range files {
			f, err := os.Open(arg)
			if err != nil {
				fmt.Fprintf(os.Stderr, "dup2: %v\n", err)
				continue
			}
			countLines(f, counts)
			f.Close()
		}
	}
	for line, n := range counts {
		if n > 1 {
			fmt.Printf("%d\t%s\n", n, line)
		}
	}
}

func countLines(f *os.File, counts map[string]int) {
	input := bufio.NewScanner(f)
	for input.Scan() {
		counts[input.Text()]++
	}
	// NOTE: ignoring potential errors from input.Err()
}
```

The function `os.Open` returns two values:

1. The first is an open file (`*os.File`) used in subsequent reads by the `Scanner`.
2. The second result of `os.Open` is a value of the built-in error type:
    * If `err` equals the special built-in value `nil`, the file was opened successfully. The file is read, and when the end of the input is reached, `Close` closes the file and releases any resources.
    * If `err` is not `nil`, something went wrong; the error value describes the problem.

In this program, the error handling prints a message on the standard error stream using `Fprintf` and
the verb `%v`, which displays a value of any type in a default format. The details of error handling are in [Section 5.4](ch5.md#errors).

<u>Notice that the call to `countLines` precedes its declaration. Functions and other package-level entities may be declared in any order.</u>

### Animated GIFs

### Fetching a URL

### Fetching URLs Concurrently

### A Web Server

### Loose Ends
