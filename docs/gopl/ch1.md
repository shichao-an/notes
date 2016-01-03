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

The next program demonstrates usage of Go’s standard image packages to create a sequence of bit-mapped images and then encode the sequence as a GIF animation, called [Lissajous figures](https://en.wikipedia.org/wiki/Lissajous_curve).

There are several new constructs in this code, including `const` declarations, struct types, and composite literals, and also involves floating-point computations.

<small>[gopl.io/ch1/lissajous/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/lissajous/main.go)</small>

```go
// Lissajous generates GIF animations of random Lissajous figures.
package main

import (
	"image"
	"image/color"
	"image/gif"
	"io"
	"math"
	"math/rand"
	"os"
)

//!-main
// Packages not needed by version in book.
import (
	"log"
	"net/http"
	"time"
)

//!+main

var palette = []color.Color{color.White, color.Black}

const (
	whiteIndex = 0 // first color in palette
	blackIndex = 1 // next color in palette
)

func main() {
	lissajous(os.Stdout)
}

func lissajous(out io.Writer) {
	const (
		cycles  = 5     // number of complete x oscillator revolutions
		res     = 0.001 // angular resolution
		size    = 100   // image canvas covers [-size..+size]
		nframes = 64    // number of animation frames
		delay   = 8     // delay between frames in 10ms units
	)
	freq := rand.Float64() * 3.0 // relative frequency of y oscillator
	anim := gif.GIF{LoopCount: nframes}
	phase := 0.0 // phase difference
	for i := 0; i < nframes; i++ {
		rect := image.Rect(0, 0, 2*size+1, 2*size+1)
		img := image.NewPaletted(rect, palette)
		for t := 0.0; t < cycles*2*math.Pi; t += res {
			x := math.Sin(t)
			y := math.Sin(t*freq + phase)
			img.SetColorIndex(size+int(x*size+0.5), size+int(y*size+0.5),
				blackIndex)
		}
		phase += 0.1
		anim.Delay = append(anim.Delay, delay)
		anim.Image = append(anim.Image, img)
	}
	gif.EncodeAll(out, &anim) // NOTE: ignoring encoding errors
}
```

#### Package names with multiple components *

After importing a package whose path has multiple components, we refer to the package with a name that comes from the last component. Therefore:

* The variable `color.White` belongs to the `image/color` package
* The [`gif.GIF`](https://golang.org/pkg/image/gif/#GIF) belongs to the `image/gif` package

#### `constant` declarations *

A `const` declaration ([Section 3.6](ch3.md#constants)) gives names to constants (values that are fixed at compile time) such as the numerical parameters for cycles, frames, and delay. Like `var` declarations, const declarations may appear at package level (so the names are visible throughout the package) or within a function (so the names are visible only within that function). <u>The value of a constant must be a number, string, or boolean.</u>

#### Composite literals *

The expressions `[]color.Color{...}` (a slice) and `gif.GIF{...}` (a struct) are [**composite literals**](https://golang.org/ref/spec#Composite_literals) ([Section 4.2](ch4.md#slices), [Section 4.4.1](ch4.md#struct-literals)), a compact notation for instantiating any of Go’s composite types from a sequence of element values.

#### Structs *

The type `gif.GIF` is a struct type ([Section 4.4](ch4.md#structs)). A struct is a group of values called *fields*, often of different types, that are collected together in a single object that can be treated as a unit. The variable `anim` is a struct of type `gif.GIF`. The struct literal creates a struct value whose `LoopCount` field is set to `nframes`; all other fields have the zero value for their type. The individual fields of a struct can be accessed using dot notation, as in the final two assignments which explicitly update the `Delay` and `Image` fields of `anim`.

#### The `lissajous` function *

[p15]

(skipped)

Used concepts:

* Built-in `append` function
* `io.Writer`

The `main` function calls the `lissajous` function, directing it to write to the standard output, so this command produces an animated GIF:

```shell-session
$ go build gopl.io/ch1/lissajous
$ ./lissajous >out.gif
```

### Fetching a URL

Go provides a collection of packages, grouped under `net`, that make it easy to send and receive information through the Internet, make low-level network connections, and set up servers, for which Go’s concurrency features ([Chapter 8](ch8.md)) are particularly useful.

The following program fetches the content of each specified URL and prints it as uninterpreted text, which is inspired the `curl` utility:

<small>[gopl.io/ch1/fetch/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/fetch/main.go)</small>

```go
// Fetch prints the content found at a URL.
package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

func main() {
	for _, url := range os.Args[1:] {
		resp, err := http.Get(url)
		if err != nil {
			fmt.Fprintf(os.Stderr, "fetch: %v\n", err)
			os.Exit(1)
		}
		b, err := ioutil.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			fmt.Fprintf(os.Stderr, "fetch: reading %s: %v\n", url, err)
			os.Exit(1)
		}
		fmt.Printf("%s", b)
	}
}
```

This program introduces functions from two packages, `net/http` and `io/ioutil`.

1. The `http.Get` function makes an HTTP request and, if there is no error, returns the result in the response struct `resp`.
2. The `Body` field of `resp` contains the server response as a readable stream.
3. `ioutil.ReadAll` reads the entire response; the result is stored in `b`.
4. The `Body` stream is closed to avoid leaking resources, and `Printf` writes the response to the standard output.

```shell-session
$ go build gopl.io/ch1/fetch
$ ./fetch http://gopl.io
<html>
<head>
<title>The Go Programming Language</title>
...
```

If the HTTP request fails, `fetch` reports the failure instead:

```shell-session
$ ./fetch http://bad.gopl.io
fetch: Get http://bad.gopl.io: dial tcp: lookup bad.gopl.io: no such host
```

### Fetching URLs Concurrently

Support for concurrent programming is one of the most interesting and novel aspects of Go. This is a large topic (concurrency mechanisms, goroutines and channels) to which Chapter 8 and Chapter 9 are devoted.

The following program, `fetchall`, does the same fetch of a URL’s contents as the previous example, but it fetches many URLs concurrently, so that the process will take no longer than the longest fetch rather than the sum of all the fetch times. This version of `fetchall` discards the responses but reports the size and elapsed time for each one:

<small>[gopl.io/ch1/fetchall/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/fetchall/main.go)</small>

```go
// Fetchall fetches URLs in parallel and reports their times and sizes.
package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"time"
)

func main() {
	start := time.Now()
	ch := make(chan string)
	for _, url := range os.Args[1:] {
		go fetch(url, ch) // start a goroutine
	}
	for range os.Args[1:] {
		fmt.Println(<-ch) // receive from channel ch
	}
	fmt.Printf("%.2fs elapsed\n", time.Since(start).Seconds())
}

func fetch(url string, ch chan<- string) {
	start := time.Now()
	resp, err := http.Get(url)
	if err != nil {
		ch <- fmt.Sprint(err) // send to channel ch
		return
	}

	nbytes, err := io.Copy(ioutil.Discard, resp.Body)
	resp.Body.Close() // don't leak resources
	if err != nil {
		ch <- fmt.Sprintf("while reading %s: %v", url, err)
		return
	}
	secs := time.Since(start).Seconds()
	ch <- fmt.Sprintf("%.2fs  %7d  %s", secs, nbytes, url)
}
```

Result:

```shell-session
$ go build gopl.io/ch1/fetchall
$ ./fetchall https://golang.org http://gopl.io https://godoc.org
0.14s
6852 https://godoc.org
0.16s
7261 https://golang.org
0.48s
2475 http://gopl.io
0.48s elapsed
```

* A **goroutine** is a concurrent function execution.
* A **channel** is a communication mechanism that allows one goroutine to pass values of a specified type to another goroutine.
    * The function `main` runs in a goroutine and the `go` statement creates additional goroutines.

This program does the following:

1. The `main` function creates a channel of strings using `make`.
2. For each command-line argument, the `go` statement in the first range loop starts a new goroutine that calls `fetch` asynchronously to fetch the URL using `http.Get`.
3. The [`io.Copy`](https://golang.org/pkg/io/#Copy) function reads the body of the response and discards it by writing to the [`ioutil.Discard`](https://golang.org/pkg/io/ioutil/#Discard) output stream.
4. `Copy` returns the byte count, along with any error that occurred. As each result arrives, `fetch` sends a summary line on the channel `ch`.
5. The second range loop in main receives and prints those lines.

When one goroutine attempts a send or receive on a channel, it blocks until another goroutine attempts the corresponding receive or send operation, at which point the value is transferred and both goroutines proceed. In this example, each `fetch` sends a value (`ch <-` *expression*) on the channel `ch`, and `main` receives all of them (`<-ch`). <u>Having `main` do all the printing ensures that output from each goroutine is processed as a unit, with no danger of interleaving if two goroutines finish at the same time.</u>

### A Web Server

Go’s libraries makes it easy to write a web server.

#### Echoing URL path *

The following example shows a minimal server that returns the path component of the URL used to access the server. That is, if the request is for `http://localhost:8000/hello`, the response will be `URL.Path = "/hello"`.

<small>[gopl.io/ch1/server1/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/server1/main.go)</small>

```go
// Server1 is a minimal "echo" server.
package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/", handler) // each request calls handler
	log.Fatal(http.ListenAndServe("localhost:8000", nil))
}

// handler echoes the Path component of the request URL r.
func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "URL.Path = %q\n", r.URL.Path)
}
```
This program does the following:

1. The `main` function connects a handler function to incoming URLs that begin with `/` (which is all URLs) using [`http.HandleFunc`](https://golang.org/pkg/net/http/#HandleFunc), and starts a server listening for incoming requests on port 8000 using [`http.ListenAndServe`](https://golang.org/pkg/net/http/#ListenAndServe).
2. A request is represented as a struct of type `http.Request`, which contains a number of related fields, one of which is the URL of the incoming request.
3. When a request arrives, it is given to the `handler` function, which extracts the path component (`/hello`) from the request URL and sends it back as the response, using `fmt.Fprintf`. Web servers will be explained in detail in [Section 7.7](ch7.md#the-httphandler-interface).

#### Request counter *

This version does the same echo but also counts the number of requests; a request to the URL `/count` returns the count so far, excluding `/count` requests themselves:

<small>[gopl.io/ch1/server2/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/server2/main.go)</small>

```go
// Server2 is a minimal "echo" and counter server.
package main

import (
	"fmt"
	"log"
	"net/http"
	"sync"
)

var mu sync.Mutex
var count int

func main() {
	http.HandleFunc("/", handler)
	http.HandleFunc("/count", counter)
	log.Fatal(http.ListenAndServe("localhost:8000", nil))
}

// handler echoes the Path component of the requested URL.
func handler(w http.ResponseWriter, r *http.Request) {
	mu.Lock()
	count++
	mu.Unlock()
	fmt.Fprintf(w, "URL.Path = %q\n", r.URL.Path)
}

// counter echoes the number of calls so far.
func counter(w http.ResponseWriter, r *http.Request) {
	mu.Lock()
	fmt.Fprintf(w, "Count %d\n", count)
	mu.Unlock()
}
```

The server has two handlers, and the request URL determines which one is called: a request for `/count` invokes `counter` and all others invoke `handler`. A handler pattern that ends with a slash matches any URL that has the pattern as a prefix.

Behind the scenes, the server runs the handler for each incoming request in a separate goroutine so that it can serve multiple requests simultaneously. We must ensure that at most one goroutine accesses the `count` variable at a time, which is the purpose of the `mu.Lock()` and `mu.Unlock()` calls that bracket each access of `count`. Otherwise, if two concurrent requests try to update count at the same time, it might not be incremented consistently; the program would have a serious bug called a race condition. Concurrency and shared variables are detailed in [Chapter 9](ch9.md).

#### Inspecting requests *

In the following example, the `handler` function can report on the headers and form data that it receives, making the server useful for inspecting and debugging requests:

<small>[gopl.io/ch1/server3/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/server3/main.go)</small>

```go
// handler echoes the HTTP request.
func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "%s %s %s\n", r.Method, r.URL, r.Proto)
	for k, v := range r.Header {
		fmt.Fprintf(w, "Header[%q] = %q\n", k, v)
	}
	fmt.Fprintf(w, "Host = %q\n", r.Host)
	fmt.Fprintf(w, "RemoteAddr = %q\n", r.RemoteAddr)
	if err := r.ParseForm(); err != nil {
		log.Print(err)
	}
	for k, v := range r.Form {
		fmt.Fprintf(w, "Form[%q] = %q\n", k, v)
	}
}
```

[p21]

The call to `ParseForm` is nested within an `if` statement. Go allows a simple statement such as a local variable declaration to precede the `if` condition, which is particularly useful for error handling as in this example. It could have been written it as:

```go
err := r.ParseForm()
if err != nil {
	log.Print(err)
}
```

but combining the statements is shorter and reduces the scope of the variable `err`, which is good practice. Scope is defined in [Section 2.7](ch2.md#section).

In these programs, three very different types are used as output streams:

* The `fetch` program copied HTTP response data to `os.Stdout`,
* The `fetchall` program threw the response away by copying it to the trivial sink `ioutil.Discard`.
* The web server above used `fmt.Fprintf `to write to an `http.ResponseWriter` representing the web browser.

Although these three types differ in the details of what they do, they all satisfy a common
interface, allowing any of them to be used wherever an output stream is needed. That interface, called `io.Writer`, is discussed in [Section 7.1](ch7.md#interfaces-as-contracts).

Go’s interface mechanism is the topic of [Chapter 7](ch7.md). It's easy to combine the web server with the `lissajous` function so that animated GIFs are written not to the standard output, but to the HTTP client. Add the following code:

```go
handler := func(w http.ResponseWriter, r *http.Request) {
	lissajous(w)
}
http.HandleFunc("/", handler)
```

or equivalently:

```go
http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
	lissajous(w)
})
```

The second argument to the `HandleFunc` function call immediately above is a [**function literal**](https://golang.org/ref/spec#Function_literals), which is an anonymous function defined at its point of use. This is detailed in [Section 5.6](#anonymous-functions).

### Loose Ends

The following are some topics that have been barely touched upon or omitted entirely.

#### Control flow

##### **The `switch` statement** *

Besides `if` and `for`, there is the `switch` statement, which is a multi-way branch. For example:

```go
switch coinflip() {
case "heads":
	heads++
case "tails":
	tails++
default:
	fmt.Println("landed on edge!")
}
```

The result of calling `coinflip` is compared to the value of each case. Cases are evaluated from
top to bottom, so the first matching one is executed. <u>The optional default case matches if none
of the other cases does; it may be placed anywhere. Cases do not fall through from one to the
next as in C-like languages,</u> though there is a rarely used [`fallthrough`](https://github.com/golang/go/wiki/Switch#fall-through) statement that overrides this behavior.

A `switch` does not need an operand; it can just list the cases, each of which is a boolean expression:

```go
func Signum(x int) int {
	switch {
	case x > 0:
		return +1
	default:
		return 0
	case x < 0:
		return -1
	}
}
```

This form is called a *tagless switch*; it’s equivalent to `switch true`.

Like the `for` and `if` statements, a `switch` may include an optional simple statement: a short variable declaration, an increment or assignment statement, or a function call, that can be used to set a value before it is tested.

##### **`break` and `continue`** *

The `break` and continue `statements` modify the flow of control.

* A `break` causes control to resume at the next statement after the innermost `for`, `switch`, or [`select`](https://golang.org/ref/spec#Select_statements) statement
* A `continue` causes the innermost for loop to start its next iteration.

Statements [may be labeled](https://golang.org/ref/spec#Continue_statements) so that `break` and `continue` can refer to them, for instance to break out of several nested loops at once or to start the next iteration of the outermost loop.

There is even a `goto` statement, though it’s intended for machine-generated code, not regular use by programmers.

#### Named types

A `type` declaration gives a name to an existing type. <u>Since struct types are often long, they are nearly always named.</u> For example:

```go
type Point struct {
	X, Y int
}
var p Point
```

Type declarations and named types are covered in [Chapter 2](ch2.md).

#### Pointers

Pointers are values that contain the address of a variable.

* In some languages, notably C, pointers are relatively unconstrained.
* In other languages, pointers are disguised as "references", and there’s not much that can be done with them except pass them around.
* Go takes a position somewhere in the middle.
    * Pointers are explicitly visible.
    * The `&` operator yields the address of a variable.
    * The `*` operator retrieves the variable that the pointer refers to, but there is no pointer arithmetic.

Pointers are detailed in [Section 2.3.2](ch2.md#pointers).

#### Methods and interfaces

A method is a function associated with a named type. In Go, methods may be attached to almost any named type. Methods are covered in [Chapter 6](ch6.md).

Interfaces are abstract types that let us treat different concrete types in the same way based on what methods they have, not how they are represented or implemented. Interfaces are the subject of [Chapter 7](ch7.md).

#### Packages

Go has an extensive standard library of useful packages, and the Go community has created and shared many more. This book disucsses a couple of the most important standard packages.

Before you embark on any new program, it’s a good idea to see if packages already exist that might help you get your job done more easily. You can find an index of the standard library packages at [https://golang.org/pkg](https://golang.org/pkg) and the packages contributed by the community at [https://godoc.org](https://godoc.org). The `go doc` tool makes these documents easily accessible from the command line:

```shell-session
$ go doc http.ListenAndServe
package http // import "net/http"

func ListenAndServe(addr string, handler Handler) error

  ListenAndServe listens on the TCP network address addr and then
  calls Serve with handler to handle requests on incoming connections.
...
```

#### Comments

Besides documentation comments at the beginning of a program or package, it’s also good style to write a comment before the declaration of each function to specify its behavior. These conventions are important, because they are used by tools like `go doc` and `godoc` to locate and display documentation.

For comments that span multiple lines or appear within an expression or statement, there is also the `/* ... */` notation familiar from other languages. Such comments are sometimes used at the beginning of a file for a large block of explanatory text to avoid a `//` on every line.  Within a comment, // and `/*` have no special meaning, so comments do not nest.
