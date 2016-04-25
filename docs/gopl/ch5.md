### **Chapter 5. Functions**

Functions are a critical part of any programming language. [p119]

### Function Declarations

A function declaration has a name, a list of parameters, an optional list of results, and a body:

<pre>
func <i>name</i>(<i>parameter-list</i>) (<i>result-list</i>) {
	<i>body</i>
}
</pre>

* The parameter list specifies the names and types of the function's [*parameters*](https://en.wikipedia.org/wiki/Parameter_(computer_programming)), which are local variables whose values (*arguments*) are supplied by the caller.
* The result list specifies the types of the values that the function returns.
    * <u>If the function returns one unnamed result or no results, parentheses are optional and usually omitted.</u>
    * Leaving off the result list entirely declares a function that does not return any value.

For example, in the `hypot` function below:

```go
func hypot(x, y float64) float64 {
	return math.Sqrt(x*x + y*y)
}

fmt.Println(hypot(3, 4)) // "5"
```

* `x` and `y` are parameters in the declaration.
* `3` and `4` are arguments of the call.
* The function returns a `float64` value.

Results may be named, in which case each name declares a local variable initialized to the zero value for its type.

A function that has a result list must end with a `return` statement unless execution clearly cannot reach the end of the function, the possible cases being:

* The function ends with a call to [`panic`](https://golang.org/pkg/builtin/#panic)
* Infinite `for` loop with no `break`

A sequence of parameters or results of the same type can be factored so that the type itself is written only once. These two declarations are equivalent:

```go
func f(i, j, k int, s, t string)                { /* ... */ }
func f(i int, j int, k int, s string, t string) { /* ... */ }
```

Below are four ways to declare a function with two parameters and one result, all of type `int`.  The blank identifier can be used to emphasize that a parameter is unused.

```go
func add(x int, y int) int   { return x + y }
func sub(x, y int) (z int)   { z = x - y; return }
func first(x int, _ int) int { return x }
func zero(int, int) int      { return 0 }

fmt.Printf("%T\n", add)   // "func(int, int) int"
fmt.Printf("%T\n", sub)   // "func(int, int) int"
fmt.Printf("%T\n", first) // "func(int, int) int"
fmt.Printf("%T\n", zero)  // "func(int, int) int"
```

The type of a function is sometimes called its [*signature*](https://en.wikipedia.org/wiki/Type_signature). Two functions have the same type or signature if they have the same sequence of parameter types and the same sequence of result types. The following don't affect the type:

* The names of parameters and results
* Whether or not they were declared using the factored form

Every function call must provide an argument for each parameter, in the order in which the parameters were declared.

Go does not have the concept of the following:

* Default parameter values
* Any way to specify arguments by name

The names of parameters and results don't matter to the caller except as documentation.

Parameters are local variables within the body of the function, with their initial values set to the arguments supplied by the caller. Function parameters and named results are variables in the same lexical block as the functions' outermost local variables.

Arguments are passed [*by value*](https://en.wikipedia.org/wiki/Evaluation_strategy#Call_by_value): the function receives a copy of each argument; modifications to the copy do not affect the caller. However, if the argument contains some kind of reference, like a pointer, slice, map, function, or channel, then the caller may be affected by any modifications the function makes to variables *indirectly* referred to by the argument.

You may occasionally encounter a function declaration without a body, indicating that the function is implemented in a language other than Go. Such a declaration defines the function signature.

```go
package math

func Sin(x float64) float64 // implemented in assembly language
```

### Recursion

Functions may be recursive, which means they may call themselves, either directly or indirectly.

The example program below uses a non-standard package, [`golang.org/x/net/html`](https://godoc.org/golang.org/x/net/html), which provides an HTML parser. The `golang.org/x/...` repositories hold packages designed and maintained by the Go team for applications such as networking, internationalized text processing, mobile platforms, image manipulation, cryptography, and developer tools. These packages are not in the standard library because they're still under development or rarely needed by the majority of Go programmers.

The parts of the `golang.org/x/net/html` API are shown below.

* The function [`html.Parse`](https://godoc.org/golang.org/x/net/html#Parse) reads a sequence of bytes, parses them, and returns the root of the HTML document tree, which is an [`html.Node`](https://godoc.org/golang.org/x/net/html#Node).
* HTML has several kinds of nodes. We are concerned only with *element* nodes of the form `<name key='value'>`.

```go
package html

type Node struct {
	Type NodeType
	Data string
	Attr []Attribute
	FirstChild, NextSibling *Node
}

type NodeType int32

const (
	ErrorNode NodeType = iota
	TextNode
	DocumentNode
	ElementNode
	CommentNode
	DoctypeNode
)

type Attribute struct {
	Key, Val string
}

func Parse(r io.Reader) (*Node, error)
```

The `main` function parses the standard input as HTML, extracts the links using a recursive `visit` function, and prints each discovered link:

<small>[gopl.io/ch5/findlinks1/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/findlinks1/main.go)</small>

```go
// Findlinks1 prints the links in an HTML document read from standard input.
package main

import (
	"fmt"
	"os"
	"golang.org/x/net/html"
)

func main() {
	doc, err := html.Parse(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "findlinks1: %v\n", err)
		os.Exit(1)
	}
	for _, link := range visit(nil, doc) {
		fmt.Println(link)
	}
}
```

The `visit` function traverses an HTML node tree, extracts the link from the `href` attribute of each *anchor* element `<a href='...'>`, appends the links to a slice of strings, and returns the resulting slice:

```go
// visit appends to links each link found in n and returns the result.
func visit(links []string, n *html.Node) []string {
	if n.Type == html.ElementNode && n.Data == "a" {
		for _, a := range n.Attr {
			if a.Key == "href" {
				links = append(links, a.Val)
			}
		}
	}
	for c := n.FirstChild; c != nil; c = c.NextSibling {
		links = visit(links, c)
	}
	return links
}
```

[p123]

The next program uses recursion over the HTML node tree to print the structure of the tree in outline. As it encounters each element, it pushes the element's tag onto a stack, then prints the stack.

<small>[gopl.io/ch5/outline/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/outline/main.go)</small>

```go
func main() {
	doc, err := html.Parse(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "outline: %v\n", err)
		os.Exit(1)
	}
	outline(nil, doc)
}

func outline(stack []string, n *html.Node) {
	if n.Type == html.ElementNode {
		stack = append(stack, n.Data) // push tag
		fmt.Println(stack)
	}
	for c := n.FirstChild; c != nil; c = c.NextSibling {
		outline(stack, c)
	}
}
```

Note that `outline` "pushes" an element on stack, but there is no corresponding pop. <u>When `outline` calls itself recursively, the callee receives a copy of stack.</u> Although the callee may append elements to this slice, modifying its underlying array and perhaps even allocating a new array, it doesn't modify the initial elements that are visible to the caller, so when the function returns, the caller's stack is as it was before the call.

The following is the outline of `https://golang.org`:

```text
$ go build gopl.io/ch5/outline
$ ./fetch https://golang.org | ./outline
[html]
[html head]
[html head meta]
[html head title]
[html head link]
[html body]
[html body div]
[html body div]
[html body div div]
[html body div div form]
[html body div div form div]
[html body div div form div a]
...
```

#### Variable-size stacks in Go *

Many programming language implementations use a fixed-size function call stack; sizes from 64KB to 2MB are typical. Fixed-size stacks impose a limit on the depth of recursion, so one must be careful to avoid a [stack overflow](https://en.wikipedia.org/wiki/Stack_overflow) when traversing large data structures recursively; fixed-size stacks may even pose a security risk.

In contrast, <u>typical Go implementations use variable-size stacks that start small and grow as needed up to a limit on the order of a gigabyte, which lets us use recursion safely and without worrying about overflow.</u>

### Multiple Return Values

A function can return more than one result. Many examples of functions from standard packages return two values, the desired computational result and an error value or boolean that indicates whether the computation worked.

The program below is a variation of `findlinks` that makes the HTTP request itself. Because the HTTP and parsing operations can fail, `findLinks` declares two results: the list of discovered links and an error. The HTML parser can usually recover from bad input and construct a document containing error nodes, so `Parse` rarely fails; when it does, it’s typically due to underlying I/O errors.

<small>[gopl.io/ch5/findlinks2/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/findlinks2/main.go)</small>

```go
func main() {
	for _, url := range os.Args[1:] {
		links, err := findLinks(url)
		if err != nil {
			fmt.Fprintf(os.Stderr, "findlinks2: %v\n", err)
			continue
		}
		for _, link := range links {
			fmt.Println(link)
		}
	}
}

// findLinks performs an HTTP GET request for url, parses the
// response as HTML, and extracts and returns the links.
func findLinks(url string) ([]string, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		return nil, fmt.Errorf("getting %s: %s", url, resp.Status)
	}
	doc, err := html.Parse(resp.Body)
	resp.Body.Close()
	if err != nil {
		return nil, fmt.Errorf("parsing %s as HTML: %v", url, err)
	}
	return visit(nil, doc), nil
}
```

There are four return statements in `findLinks`, each of which returns a pair of values. The first three returns cause the function to pass the underlying errors from the `http` and `html` packages on to the caller.

* In the first case, the error is returned unchanged.
* In the second and third, it is augmented with additional context information by `fmt.Errorf` ([Section 7.8](ch7.md#the-error-interface)).
* If `findLinks` is successful, the final return statement returns the slice of links, with no error.

We must ensure that `resp.Body` is closed so that network resources are properly released even in case of error. <u>Go's garbage collector recycles unused memory, but you cannot assume it will release unused operating system resources like open files and network connections.</u> They should be closed explicitly.

The result of calling a multi-valued function is a tuple of values. The caller of such a function must explicitly assign the values to variables if any of them are to be used:

```go
links, err := findLinks(url)
```

To ignore one of the values, assign it to the blank identifier:

```go
links, _ := findLinks(url) // errors ignored
```

The result of a multi-valued call may itself be returned from a (multi-valued) calling function. For example, the following function behaves like `findLinks` but logs its argument:

```go
func findLinksLog(url string) ([]string, error) {
	log.Printf("findLinks %s", url)
	return findLinks(url)
}
```

<u>A multi-valued call may appear as the sole argument when calling a function of multiple parameters.</u> Although rarely used in production code, this feature is sometimes convenient during debugging since it prints all the results of a call using a single statement. The two print statements below have the same effect.

```go
log.Println(findLinks(url))

links, err := findLinks(url)
log.Println(links, err)
```

Well-chosen names can document the significance of a function's results. Names are particularly valuable when a function returns multiple results of the same type. For example:

```go
func Size(rect image.Rectangle) (width, height int)
func Split(path string) (dir, file string)
func HourMinSec(t time.Time) (hour, minute, second int)
```

However, it's not always necessary to name multiple results solely for documentation. For instance, <u>convention dictates that a final `bool` result indicates success;</u> an [`error`](https://golang.org/pkg/builtin/#error) result often needs no explanation.

#### Bare return *

In a function with named results, the operands of a return statement may be omitted. This is called a *bare return*.

```go
// CountWordsAndImages does an HTTP GET request for the HTML
// document url and returns the number of words and images in it.
func CountWordsAndImages(url string) (words, images int, err error) {
	resp, err := http.Get(url)
	if err != nil {
		return
}
	doc, err := html.Parse(resp.Body)
	resp.Body.Close()
	if err != nil {
		err = fmt.Errorf("parsing HTML: %s", err)
		return
	}
	words, images = countWordsAndImages(doc)
	return
}

func countWordsAndImages(n *html.Node) (words, images int) { /* ... */ }
```

A bare return is a shorthand way to return each of the named result variables in order: in the function above, each return statement is equivalent to.

```go
return words, images, err
```

In such functions with many return statements and several results, bare returns can reduce code duplication, but they rarely make code easier to understand. For instance, it's not obvious that the two early returns are equivalent to return `0, 0, err` (because the result variables words and images are initialized to their zero values) and that the final return is equivalent to return `words, images, nil`. For this reason, bare returns should be sparingly used.

### Errors

Some functions always succeed. For example, `strings.Contains` and `strconv.FormatBool` have well-defined results for all possible argument values and cannot fail, except catastrophic and unpredictable scenarios like running out of memory. [p127]

Other functions always succeed so long as their preconditions are met. For example, the [`time.Date`](https://golang.org/pkg/time/#Date) function always constructs a `time.Time` from its components (year, month, etc.), unless the last argument (the time zone) is `nil`, in which case it panics. This panic is a sure sign of a bug in the calling code and should never happen in a well-written program.

<u>For many other functions, even in a well-written program, success is not assured because it depends on factors beyond the programmers' control.</u> Any function that does I/O, for example, must confront the possibility of error, and only a naive programmer believes a simple read or write cannot fail. We most need to know why when the most reliable operations fail unexpectedly

Errors are thus an important part of a package's API or an applications' user interface, and failure is just one of several expected behaviors. This is the approach Go takes to [error handling](http://blog.golang.org/error-handling-and-go).

A function for which failure is an expected behavior returns an additional result, conventionally the last one. <u>If the failure has only one possible cause, the result is a boolean, usually called `ok`</u>, as in the following example of a cache lookup that always succeeds unless there was no entry for that key:

```go
value, ok := cache.Lookup(key)
	if !ok {
	// ...cache[key] does not exist...
}
```

More often, and especially for I/O, the failure may have a variety of causes for which the caller will need an explanation. In such cases, the type of the additional result is `error`.

The built-in type [`error`](https://golang.org/pkg/builtin/#error) is an interface type (detailed in [Chapter 7](ch7.md). An error may be `nil` or non-`nil`; `nil` implies success and non-`nil` implies failure, and non-`nil` error has an error message string which can be obtained by calling its `Error` method or print by calling `fmt.Println(err)` or `fmt.Printf("%v", err)`.

Usually when a function returns a non-nil error, its other results are undefined and should be ignored. However, a few functions may return partial results in error cases. For example, if an error occurs while reading from a file, a call to `Read` returns the number of bytes it was able to read and an `error` value describing the problem. For correct behavior, some callers may need to process the incomplete data before handling the error, so it is important that such functions clearly document their results.

#### Why Go uses control-flow mechanisms for error handling *

Go's approach differs from many other languages in which failures are reported using *exceptions*, not ordinary values. Although Go does have an exception mechanism of sorts, which is discussed discussed in [Section 5.9](#panic), it is used only for reporting truly unexpected errors that indicate a bug, not the routine errors that a robust program should be built to expect.

The problem is that exceptions tend to entangle the description of an error with the control flow required to handle it, often leading to an undesirable outcome: routine errors are reported to the end user in the form of an incomprehensible stack trace, full of information about the structure of the program but lacking intelligible context about what went wrong.

By contrast, Go programs use ordinary control-flow mechanisms like `if` and `return` to respond to errors. This style undeniably demands that more attention be paid to error-handling logic, but that is precisely the point.

#### Error-Handling Strategies

When a function call returns an error, it's the caller's responsibility to check it and take appropriate action. Depending on the situation, there may be a number of possibilities. This section discusses five of them.

##### **Propagating the error** *

The first and most common strategy is to propagate the error, so that a failure in a subroutine becomes a failure of the calling routine. In the `findLinks` function of [Section 5.3](#multiple-return-values), if the call to `http.Get` fails, `findLinks` returns the HTTP error to the caller immediately:

```go
resp, err := http.Get(url)
if err != nil {
	return nil, err
}
```

In contrast, if the call to `html.Parse` fails, `findLinks` does not return the HTML parser's error directly because it lacks two crucial pieces of information:

1. The error occurred in the parser
2. The URL of the document that was being parsed.

In this case, `findLinks` constructs a new error message that includes both pieces of information as well as the underlying parse error:

```go
doc, err := html.Parse(resp.Body)
resp.Body.Close()
if err != nil {
	return nil, fmt.Errorf("parsing %s as HTML: %v", url, err)
}
```

The `fmt.Errorf` function formats an error message using `fmt.Sprintf` and returns a new `error` value. It is used to build descriptive errors by successively prefixing additional context information to the original error message. When the error is ultimately handled by the program's main function, it should provide a clear causal chain from the root problem to the overall failure, reminiscent of a NASA accident investigation:

```go
genesis: crashed: no parachute: G-switch failed: bad relay orientation
```

<u>Because error messages are frequently chained together, message strings should not be capitalized and newlines should be avoided.</u> The resulting errors may be long, but they will be self-contained when found by tools like `grep`.

When designing error messages, remember the following:

* Be deliberate, so that each one is a meaningful description of the problem with sufficient and relevant detail.
* Be consistent, so that errors returned by the same function or by a group of functions in the same package are similar in form and can be dealt with in the same way.

For example, the [`os`](https://golang.org/pkg/os/) package guarantees that every error returned by a file operation, such as `os.Open` or the `Read`, `Write`, or `Close` methods of an open file, describes not just the nature of the failure (permission denied, no such directory, and so on) but also the name of the file, so the caller needn't include this information in the error message it constructs.

In general, the call `f(x)` is responsible for reporting the attempted operation `f` and the argument value `x` as they relate to the context of the error. The caller is responsible for adding further information that it has but the call `f(x)` does not, such as the URL in the call to `html.Parse` above.

##### **Retrying the failed operation** *

The second strategy is for errors that represent transient or unpredictable problems; in such cases, it may make sense to retry the failed operation, possibly with a delay between tries and with a limit on the number of attempts or the time spent trying before giving up entirely.

<small>[gopl.io/ch5/wait/wait.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/wait/wait.go)</small>

```go
// WaitForServer attempts to contact the server of a URL.
// It tries for one minute using exponential back-off.
// It reports an error if all attempts fail.
func WaitForServer(url string) error {
	const timeout = 1 * time.Minute
	deadline := time.Now().Add(timeout)
	for tries := 0; time.Now().Before(deadline); tries++ {
		_, err := http.Head(url)
		if err == nil {
			return nil // success
		}
		log.Printf("server not responding (%s); retrying...", err)
		time.Sleep(time.Second << uint(tries)) // exponential back-off
	}
	return fmt.Errorf("server %s failed to respond after %s", url, timeout)
}
```

##### **Printing the error and stopping the program** *

Third, if progress is impossible, the caller can print the error and stop the program gracefully,
but <u>this action should generally be reserved for the main package of a program.</u>

Library functions should usually propagate errors to the caller, unless the error is a sign of an internal inconsistency, that is, a bug.

```go
// (In function main.)
if err := WaitForServer(url); err != nil {
	fmt.Fprintf(os.Stderr, "Site is down: %v\n", err)
	os.Exit(1)
}
```

A more convenient, equivalent way is to call [`log.Fatalf`](https://golang.org/pkg/log/#Fatalf). As with all the [`log`](https://golang.org/pkg/log/) functions, by default it prefixes the time and date to the error message.

```go
if err := WaitForServer(url); err != nil {
	log.Fatalf("Site is down: %v\n", err)
}
```

The default format is helpful in a long-running server, but not useful for an interactive tool:

```text
2006/01/02 15:04:05 Site is down: no such domain: bad.gopl.io
```

We can set the prefix used by the `log` package to the name of the command, and suppress the display of the date and time:

```go
log.SetPrefix("wait: ")
log.SetFlags(0)
```

##### **Logging the error and continuing** *

Fourth, in some cases, it's sufficient just to log the error and then continue, perhaps with
reduced functionality. Using the `log` package adds the usual prefix:

```go
if err := Ping(); err != nil {
	log.Printf("ping failed: %v; networking disabled", err)
}
```

To print directly to the standard error stream:

```go
if err := Ping(); err != nil {
	fmt.Fprintf(os.Stderr, "ping failed: %v; networking disabled\n", err)
}
```

Note that all `log` functions append a newline if one is not already present.

##### **Ignoring the error** *


Fifth and finally, in rare cases we can safely ignore an error entirely:

```go
dir, err := ioutil.TempDir("", "scratch")
if err != nil {
	return fmt.Errorf("failed to create temp dir: %v", err)
}

// ...use temp dir...
os.RemoveAll(dir) // ignore errors; $TMPDIR is cleaned periodically
```

The call to `os.RemoveAll` may fail, but the program ignores it because the operating system periodically cleans out the temporary directory. In this case, discarding the error was intentional, but the program logic would be the same had we forgotten to deal with it. When you deliberately ignore one, document your intention clearly.


##### **Summary of error handling** *

Error handling in Go has a particular rhythm.

1. After checking an error, failure is usually dealt with before success.
2. If failure causes the function to return, the logic for success is not indented within an else block but follows at the outer level.
3. Functions tend to exhibit a common structure, with a series of initial checks to reject errors, followed by the substance of the function at the end, minimally indented.

#### End of File (EOF)

Occasionally, program must take different
actions depending on the kind of error that has occurred. Consider an attempt to read *n* bytes
of data from a file:

* If *n* is chosen to be the length of the file, any error represents a failure.
* If the caller repeatedly tries to read fixed-size chunks until the file is exhausted, the caller must respond differently to an [end-of-file](https://en.wikipedia.org/wiki/End-of-file) condition than it does to all other errors.

For this reason, the [`io`](https://golang.org/pkg/io/) package guarantees that any read failure caused by an end-of-file condition is always reported by a distinguished error, [`io.EOF`](https://golang.org/pkg/io/#EOF), which is defined as follows:

```go
package io

import "errors"

// EOF is the error returned by Read when no more input is available.
var EOF = errors.New("EOF")
```

The caller can detect this condition using a simple comparison, as in the loop below, which reads runes from the standard input. (The [`charcount`](https://github.com/shichao-an/gopl.io/blob/master/ch4/charcount/main.go) program in Section 4.3 provides a more complete example.)

```go
in := bufio.NewReader(os.Stdin)
for {
	r, _, err := in.ReadRune()
	if err == io.EOF {
		break // finished reading
	}
	if err != nil {
		return fmt.Errorf("read failed: %v", err)
	}
	// ...use r...
}
```

Since in an end-of-file condition there is no information to report besides the fact of it, `io.EOF` has a fixed error message, `"EOF"`. For other errors, we may need to report both the quality and quantity of the error, so a fixed error value will not do. [Section 7.11](ch7.md#discriminating-errors-with-type-assertions) will present a more systematic way to distinguish certain error values from others.

### Function Values

Functions are [*first-class values*](https://en.wikipedia.org/wiki/First-class_citizen) in Go: like other values, function values have types, and they may be assigned to variables or passed to or returned from functions. A function value may be called like any other function. For example:

```go
func square(n int) int { return n * n }
func negative(n int) int { return -n }
func product(m, n int) int { return m * n }

f := square
fmt.Println(f(3)) // "9"

f = negative
fmt.Println(f(3))     // "-3"
fmt.Printf("%T\n", f) // "func(int) int"

f = product // compile error: can't assign f(int, int) int to f(int) int
```

The zero value of a function type is `nil`. Calling a `nil` function value causes a panic:

```go
var f func(int) int
f(3) // panic: call of nil function
```

Function values may be compared with `nil`:

```go
var f func(int) int
	if f != nil {
	f(3)
}
```

But they are not comparable, so they may not be compared against each other or used as keys in a map.

With function values, we can parameterize our functions over not only data, but also behavior. The standard libraries contain many examples. For instance, `strings.Map` applies a function to each character of a string, joining the results to make another string.

```go
func add1(r rune) rune { return r + 1 }
fmt.Println(strings.Map(add1, "HAL-9000")) // "IBM.:111"
fmt.Println(strings.Map(add1, "VMS")) // "WNT"
fmt.Println(strings.Map(add1, "Admix")) // "Benjy"
```

The `findLinks` function from [Section 5.2](#recursion) uses a helper function, `visit`, to visit all the nodes in an HTML document and apply an action to each one. Using a function value, we can separate the logic for tree traversal from the logic for the action to be applied to each node, so that we can reuse the traversal with different actions.

<small>[gopl.io/ch5/outline2/outline.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/outline2/outline.go)</small>

```go
// forEachNode calls the functions pre(x) and post(x) for each node
// x in the tree rooted at n. Both functions are optional.
// pre is called before the children are visited (preorder) and
// post is called after (postorder).
func forEachNode(n *html.Node, pre, post func(n *html.Node)) {
	if pre != nil {
		pre(n)
	}

	for c := n.FirstChild; c != nil; c = c.NextSibling {
		forEachNode(c, pre, post)
	}

	if post != nil {
		post(n)
	}
}
```

The `forEachNode` function accepts two function arguments, one to call before a node's children are visited and one to call after. This arrangement gives the caller a great deal of flexibility. For example, the functions `startElement` and `endElement` print the start and end tags of an HTML element like `<b>...</b>`:

```go
var depth int

func startElement(n *html.Node) {
	if n.Type == html.ElementNode {
		fmt.Printf("%*s<%s>\n", depth*2, "", n.Data)
		depth++
	}
}

func endElement(n *html.Node) {
	if n.Type == html.ElementNode {
		depth--
		fmt.Printf("%*s</%s>\n", depth*2, "", n.Data)
	}
}
```

The functions also indent the output using another `fmt.Printf` trick. The `*` adverb in `%*s` prints a string padded with a variable number of spaces. The width and the string are provided by the arguments `depth*2` and `""`.

If we call `forEachNode` on an HTML document, like this:

```go
forEachNode(doc, startElement, endElement)
```

This will output:

```text
$ go build gopl.io/ch5/outline2
$ ./outline2 http://gopl.io
<html>
  <head>
    <meta>
    </meta>
    <title>
    </title>
    <style>
    </style>
  </head>
  <body>
    <table>
      <tbody>
        <tr>
          <td>
            <a>
              <img>
              </img>
...
```



### Anonymous Functions
### Variadic Functions
### Deferred Function Calls
### Panic
### Recover

### Doubts and Solution

#### Verbatim

##### **p131 on error handling**

> After checking an error, failure is usually dealt with before success.

<span class="text-danger">Question</span>: What does it mean exactly?
