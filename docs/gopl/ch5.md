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

Go's approach differs from many other languages in which failures are reported using *exceptions*, not ordinary values. Although Go does have an exception mechanism of sorts, which is discussed in [Section 5.9](#panic), it is used only for reporting truly unexpected errors that indicate a bug, not the routine errors that a robust program should be built to expect.

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

Named functions can be declared only at the package level, but we can use a *function literal* to denote a function value within any expression. A function literal is written like a function declaration, but without a name following the `func` keyword. It is an expression, and its value is called an [*anonymous function*](https://en.wikipedia.org/wiki/Anonymous_function).

Function literals let us define a function at its point of use. As an example, the earlier call to `strings.Map` in [Section 5.5](#function-values) can be rewritten as:

```go
strings.Map(func(r rune) rune { return r + 1 }, "HAL-9000")
```

<u>Functions defined in this way have access to the entire lexical environment, so the inner function can refer to variables from the enclosing function.</u> For example:

<small>[gopl.io/ch5/squares/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/squares/main.go)</small>

```go
// squares returns a function that returns
// the next square number each time it is called.
func squares() func() int {
	var x int
	return func() int {
		x++
		return x * x
	}
}

func main() {
	f := squares()
	fmt.Println(f()) // "1"
	fmt.Println(f()) // "4"
	fmt.Println(f()) // "9"
	fmt.Println(f()) // "16"
}
```

The function `squares` returns another function of type `func() int`. A call to `squares` creates a local variable `x` and returns an anonymous function that, each time it is called, increments `x` and returns its square. A second call to squares would create a second variable `x` and return a new anonymous function.

This example demonstrates:

* Function values are not just code but can have state.
    * <u>The anonymous inner function can access and update the local variables of the enclosing function. These hidden variable references are why we classify functions as reference types and why function values are not comparable.</u>
    * Function values like these are implemented using a technique called [*closures*](https://en.wikipedia.org/wiki/Closure_(computer_programming)), and Go programmers often use this term for function values.
* The lifetime of a variable is not determined by its scope
    * In the above example, the variable `x` exists after `squares` has returned within `main`, even though `x` is hidden inside `f`.

The following example is a problem of computing a sequence of computer science courses that satisfies the prerequisite requirements of each one. The prerequisites are given in the `prereqs` table below, which is a mapping from each course to the list of courses that must be completed before it.

<small>[gopl.io/ch5/toposort/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/toposort/main.go)</small>

```go
// prereqs maps computer science courses to their prerequisites.
var prereqs = map[string][]string{
	"algorithms": {"data structures"},
	"calculus":   {"linear algebra"},

	"compilers": {
		"data structures",
		"formal languages",
		"computer organization",
	},

	"data structures":       {"discrete math"},
	"databases":             {"data structures"},
	"discrete math":         {"intro to programming"},
	"formal languages":      {"discrete math"},
	"networks":              {"operating systems"},
	"operating systems":     {"data structures", "computer organization"},
	"programming languages": {"data structures", "computer organization"},
}
```

This kind of problem is known as [topological sorting](https://en.wikipedia.org/wiki/Topological_sorting). The prerequisite information forms a directed graph with a node for each course and edges from each course to the courses that it depends on. The graph is acyclic: there is no path from a course that leads back to itself. We can compute a valid sequence using depth-first search through the graph with the code below:

```go
func main() {
	for i, course := range topoSort(prereqs) {
		fmt.Printf("%d:\t%s\n", i+1, course)
	}
}

func topoSort(m map[string][]string) []string {
	var order []string
	seen := make(map[string]bool)
	var visitAll func(items []string)

	visitAll = func(items []string) {
		for _, item := range items {
			if !seen[item] {
				seen[item] = true
				visitAll(m[item])
				order = append(order, item)
			}
		}
	}

	var keys []string
	for key := range m {
		keys = append(keys, key)
	}

	sort.Strings(keys)
	visitAll(keys)
	return order
}
```

<u>When an anonymous function requires recursion, we must first declare a variable, and then assign the anonymous function to that variable.</u>

If two steps are combined in the declaration, the function literal would not be within the scope of the variable `visitAll` so it would have no way to call itself recursively:

```go
visitAll := func(items []string) {
	// ...
	visitAll(m[item]) // compile error: undefined: visitAll
	// ...
}
```

The output of the `toposort` program is shown below. It is deterministic, an often-desirable property that doesn't always come for free. The values of the `prereqs` map are slices, not more maps, so their iteration order is deterministic, and we sorted the keys of `prereqs` before making the initial calls to `visitAll`.

```text
1: intro to programming
2: discrete math
3: data structures
4: algorithms
5: linear algebra
6: calculus
7: formal languages
8: computer organization
9: compilers
10: databases
11: operating systems
12: networks
13: programming languages
```

Returning to the `findLinks` example, link-extraction function `links.Extract` is moved to its own package, since it'll be used again in [Chapter 8](ch8.md). We replaced the `visit` function with an anonymous function that appends to the `links` slice directly, and used `forEachNode` to handle the traversal. Since `Extract` needs only the `pre` function, it passes `nil` for the `post` argument.

<small>[gopl.io/ch5/links/links.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/links/links.go)</small>

```go


// Package links provides a link-extraction function.
package links

import (
	"fmt"
	"net/http"
	"golang.org/x/net/html"
)

// Extract makes an HTTP GET request to the specified URL, parses
// the response as HTML, and returns the links in the HTML document.
func Extract(url string) ([]string, error) {
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

	var links []string
	visitNode := func(n *html.Node) {
		if n.Type == html.ElementNode && n.Data == "a" {
			for _, a := range n.Attr {
				if a.Key != "href" {
					continue
				}
				link, err := resp.Request.URL.Parse(a.Val)
				if err != nil {
					continue // ignore bad URLs
				}
				links = append(links, link.String())
			}
		}
	}
	forEachNode(doc, visitNode, nil)
	return links, nil
}
```

Instead of appending the raw `href` attribute value to the `links` slice, this version parses it as a URL relative to the base URL of the document, [`resp.Request.URL`](https://golang.org/pkg/net/url/#URL.Parse). The resulting `link` is in absolute form, suitable for use in a call to `http.Get`.

Crawling the web is a problem of graph traversal. The `topoSort` example showed a depth-first traversal. The following web crawler uses breadth-first traversal. In [Chapter 8](ch8.md), we'll explore concurrent traversal.

The function below encapsulates the essence of a breadth-first traversal:

* The caller provides an initial list `worklist` of items to visit and a function value `f` to call for each item, which is identified by a string.
* The function `f` returns a list of new items to append to the worklist.
* The `breadthFirst` function returns when all items have been visited. It maintains a set of strings to ensure that no item is visited twice.

<small>[gopl.io/ch5/findlinks3/findlinks.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/findlinks3/findlinks.go)</small>

```go
// breadthFirst calls f for each item in the worklist.
// Any items returned by f are added to the worklist.
// f is called at most once for each item.
func breadthFirst(f func(item string) []string, worklist []string) {
	seen := make(map[string]bool)
	for len(worklist) > 0 {
		items := worklist
		worklist = nil
		for _, item := range items {
			if !seen[item] {
				seen[item] = true
				worklist = append(worklist, f(item)...)
			}
		}
	}
}
```

The argument "`f(item)...`" causes all the items in the list returned by `f` to be appended to the worklist.

In this crawler, items are URLs. The `crawl` function, which is passed to `breadthFirst`, prints the URL, extracts its links, and returns them so that they are also visited.

```go
func crawl(url string) []string {
	fmt.Println(url)
	list, err := links.Extract(url)
	if err != nil {
		log.Print(err)
	}
	return list
}
```

To start off the crawler, we use the command-line arguments as the initial URLs.

```go
func main() {
	// Crawl the web breadth-first,
	// starting from the command-line arguments.
	breadthFirst(crawl, os.Args[1:])
}
```

Crawl the web starting from `https://golang.org`:

```text
$ go build gopl.io/ch5/findlinks3
$ ./findlinks3 https://golang.org
https://golang.org/
https://golang.org/doc/
https://golang.org/pkg/
https://golang.org/project/
https://code.google.com/p/go-tour/
https://golang.org/doc/code.html
https://www.youtube.com/watch?v=XCsL89YtqCs
http://research.swtch.com/gotour
https://vimeo.com/53221560
...
```

The process ends when all reachable web pages have been crawled or the memory of the computer is exhausted.

#### Caveat: Capturing Iteration Variables

This section discusses a pitfall of Go's lexical scope rules that can cause surprising results.

Consider a program that must create a set of directories and later remove them. We can use a slice of function values to hold the clean-up operations. (All error handling in this example for brevity.)

```go
var rmdirs []func()
for _, d := range tempDirs() {
	dir := d               // NOTE: necessary!
	os.MkdirAll(dir, 0755) // creates parent directories too
	rmdirs = append(rmdirs, func() {
		os.RemoveAll(dir)
	})
}

// ...do some work...

for _, rmdir := range rmdirs {
	rmdir() // clean up
}
```

You may be wondering why we assigned the loop variable `d` to a new local variable `dir` within the loop body, instead of just using the loop variable `dir` as in this subtly incorrect variant:

```go
var rmdirs []func()
for _, dir := range tempDirs() {
	os.MkdirAll(dir, 0755)
	rmdirs = append(rmdirs, func() {
		os.RemoveAll(dir) // NOTE: incorrect!
	})
}
```

The reason is a consequence of the scope rules for loop variables. In the program immediately above:

1. The `for` loop introduces a new lexical block in which the variable `dir` is declared. All function values created by this loop "capture" and share the same variable, which is an addressable storage location, not its value at that particular moment.
2. The value of `dir` is updated in successive iterations, so by the time the cleanup functions are called, the `dir` variable has been updated several times by the now-completed `for` loop.
3. Thus `dir` holds the value from the final iteration, and consequently all calls to `os.RemoveAll` will attempt to remove the same directory.

Frequently, <u>the inner variable introduced to work around this problem (`dir` in the example above) is given the exact same name as the outer variable of which it is a copy.</u> This leads to odd-looking but crucial variable declarations like this:

```go
for _, dir := range tempDirs() {
	dir := dir // declares inner dir, initialized to outer dir
	// ...
}
```

The risk is not unique to `range`-based `for` loops. The loop in the example below suffers from the same problem due to unintended capture of the index variable `i`.

```go
var rmdirs []func()
dirs := tempDirs()
for i := 0; i < len(dirs); i++ {
	os.MkdirAll(dirs[i], 0755) // OK
	rmdirs = append(rmdirs, func() {
		os.RemoveAll(dirs[i]) // NOTE: incorrect!
	})
}
```

The problem of iteration variable capture is most often encountered when using the `go` statement ([Chapter 8](ch8.md)) or with `defer` (to be discussed later) since both may delay the execution of a function value until after the loop has finished. But the problem is not inherent to `go` or `defer`. See also [Common Mistakes](https://github.com/golang/go/wiki/CommonMistakes#using-goroutines-on-loop-iterator-variables).

### Variadic Functions

A [**variadic function**](https://en.wikipedia.org/wiki/Variadic_function) can be called with varying numbers of arguments. The most familiar examples are `fmt.Printf` and its variants. `Printf` requires one fixed argument at the beginning, then accepts any number of subsequent arguments.

To declare a variadic function, the type of the final parameter is preceded by an ellipsis, "`...`", which indicates that the function may be called with any number of arguments of this type.

<small>[gopl.io/ch5/sum/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/sum/main.go)</small>

```go
func sum(vals ...int) int {
	total := 0
	for _, val := range vals {
		total += val
	}
	return total
}
```

* The `sum` function above returns the sum of zero or more `int` arguments.
* Within the body of the function, the type of `vals` is an `[]int` slice.
* When `sum` is called, any number of values may be provided for its `vals` parameter.

```go
fmt.Println(sum())           // "0"
fmt.Println(sum(3))          // "3"
fmt.Println(sum(1, 2, 3, 4)) // "10"
```

<u>Implicitly, the caller allocates an array, copies the arguments into it, and passes a slice of the entire array to the function.</u>

To invoke a variadic function when the arguments are already in a slice, place an ellipsis after the final argument. The call below behaves the same as the last call above.

```go
values := []int{1, 2, 3, 4}
fmt.Println(sum(values...)) // "10"
```

Although the `...int` parameter behaves like a slice within the function body, the type of a variadic function is distinct from the type of a function with an ordinary slice parameter.

```go
func f(...int) {}
func g([]int)  {}

fmt.Printf("%T\n", f) // "func(...int)"
fmt.Printf("%T\n", g) // "func([]int)"
```

Variadic functions are often used for string formatting. The `errorf` function below constructs a formatted error message with a line number at the beginning. <u>The suffix `f` is a widely followed naming convention for variadic functions that accept a `Printf`-style format string.</u>

```go
func errorf(linenum int, format string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, "Line %d: ", linenum)
	fmt.Fprintf(os.Stderr, format, args...)
	fmt.Fprintln(os.Stderr)
}
linenum, name := 12, "count"
errorf(linenum, "undefined: %s", name) // "Line 12: undefined: count"
```

The `interface{}` type means that this function can accept any values for its final arguments, which is discussed in [Chapter 7](ch7.md).

### Deferred Function Calls

The `findLinks` examples used the output of `http.Get` as the input to `html.Parse`. However, many pages contain images, plain text, and other file formats instead of HTML. Feeding such files into an HTML parser could have undesirable effects.

The program below fetches an HTML document and prints its title. The `title` function inspects the [`Content-Type`](https://en.wikipedia.org/wiki/Media_type) header of the server's response and returns an error if the document is not HTML.

<small>[gopl.io/ch5/title1/title.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/title1/title.go)</small>

```go
func title(url string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}

	// Check Content-Type is HTML (e.g., "text/html; charset=utf-8").
	ct := resp.Header.Get("Content-Type")
	if ct != "text/html" && !strings.HasPrefix(ct, "text/html;") {
		resp.Body.Close()
		return fmt.Errorf("%s has type %s, not text/html", url, ct)
	}

	doc, err := html.Parse(resp.Body)
	resp.Body.Close()
	if err != nil {
		return fmt.Errorf("parsing %s as HTML: %v", url, err)
	}

	visitNode := func(n *html.Node) {
		if n.Type == html.ElementNode && n.Data == "title" &&
			n.FirstChild != nil {
			fmt.Println(n.FirstChild.Data)
		}
	}
	forEachNode(doc, visitNode, nil)
	return nil
}
```

```text
$ go build gopl.io/ch5/title1
$ ./title1 http://gopl.io
The Go Programming Language
$ ./title1 https://golang.org/doc/effective_go.html
Effective Go - The Go Programming Language
$ ./title1 https://golang.org/doc/gopher/frontpage.png
title: https://golang.org/doc/gopher/frontpage.png has type image/png, not text/html
```

The `resp.Body.Close()` call, which is duplicated, ensures that title closes the network connection on all execution paths, including failures. As functions grow more complex and have to handle more errors, such duplication of clean-up logic may become a maintenance problem. Go' `defer` mechanism makes things simpler.

Syntactically, a `defer` statement is an ordinary function or method call prefixed by the keyword `defer`.

* The function and argument expressions are evaluated when the statement is executed, but the actual call is *deferred* until the (caller) function that contains the `defer` statement has finished. The "finished" here means either normally or abnormally:
    * Normally: the caller function executing a return statement or falling off the end.
    * Abnormally: the caller function panicking.
* Any number of calls may be deferred; <u>they are executed in the reverse of the order in which they were deferred.</u>

A `defer` statement is often used with paired operations to ensure that resources are released in all cases no matter how complex the control flow. Some examples for such paired operations are:

* Open and close
* Connect and disconnect
* Lock and unlock

The right place for a `defer` statement that releases a resource is immediately after the resource has been successfully acquired. In the `title` function below, a single deferred call replaces both previous calls to `resp.Body.Close()`:

<small>[gopl.io/ch5/title2/title.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/title2/title.go)</small>

```go
func title(url string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	ct := resp.Header.Get("Content-Type")
	if ct != "text/html" && !strings.HasPrefix(ct, "text/html;") {
		return fmt.Errorf("%s has type %s, not text/html", url, ct)
	}

	doc, err := html.Parse(resp.Body)
	if err != nil {
		return fmt.Errorf("parsing %s as HTML: %v", url, err)
	}

	// ...print doc's title element...
	//!-
	visitNode := func(n *html.Node) {
		if n.Type == html.ElementNode && n.Data == "title" &&
			n.FirstChild != nil {
			fmt.Println(n.FirstChild.Data)
		}
	}
	forEachNode(doc, visitNode, nil)
	//!+

	return nil
}
```

The same pattern can be used for other resources. For example, close an open file:

<small>[io/ioutil/ioutil.go](https://golang.org/src/io/ioutil/ioutil.go)</small>

```go
package ioutil

func ReadFile(filename string) ([]byte, error) {
	f, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	return ReadAll(f)
}
```

Unlock a mutex ([Section 9.2](ch9.md#mutual-exclusion-syncmutex)):

```
var mu sync.Mutex
var m = make(map[string]int)

func lookup(key string) int {
	mu.Lock()
	defer mu.Unlock()
	return m[key]
}
```

#### On-entry and on-exit actions *

The `defer` statement can also be used to pair "on entry" and "on exit" actions when debugging a complex function.

The `bigSlowOperation` function below does two things:

1. It calls trace immediately, which does the "on entry" action.
2. Then, it returns a function value that, when called, does the corresponding "on exit" action.

<small>[gopl.io/ch5/trace/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/trace/main.go)</small>

```go
func bigSlowOperation() {
	defer trace("bigSlowOperation")() // don't forget the extra parentheses
	// ...lots of work...
	time.Sleep(10 * time.Second) // simulate slow operation by sleeping
}

func trace(msg string) func() {
	start := time.Now()
	log.Printf("enter %s", msg)
	return func() { log.Printf("exit %s (%s)", msg, time.Since(start)) }
}
```

<u>By deferring a call to the returned function in this way, we can instrument the entry point and all exit points of a function in a single statement and even pass values,</u> like the start time, between the two actions. Do not forget the final parentheses in the defer statement, or the "on entry" action will happen on exit and the on-exit action won't happen at all.

Each time `bigSlowOperation` is called, it logs its entry and exit and the elapsed time between them.

```
$ go build gopl.io/ch5/trace
$ ./trace
2015/11/18 09:53:26 enter bigSlowOperation
2015/11/18 09:53:36 exit bigSlowOperation (10.000589217s)
```

#### Accessing result variables *

Deferred functions run after return statements have updated the function's result variables.  Because an anonymous function can access its enclosing function's variables, including named results, a deferred anonymous function can observe the function's results.

For the following function:

```go
func double(x int) int {
	return x + x
}
```

By naming its result variable and adding a `defer` statement, we can make the function print its arguments and results each time it is called.

```go
func double(x int) (result int) {
	defer func() { fmt.Printf("double(%d) = %d\n", x, result) }()
	return x + x
}

_=double(4)
// Output:
// "double(4) = 8"
```

This is useful in functions with many return statements.

A deferred anonymous function can even change the values that the enclosing function returns to its caller:

```go
func triple(x int) (result int) {
	defer func() { result += x }()
	return double(x)
}
fmt.Println(triple(4)) // "12"
```

#### Caveats of deferred functions *

Because deferred functions aren't executed until the end of a function's execution, a `defer` statement in a loop deserves extra scrutiny. The code below could run out of file descriptors since no file will be closed until all files have been processed:

```go
for _, filename := range filenames {
	f, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer f.Close() // NOTE: risky; could run out of file descriptors
	// ...process f...
}
```

One solution is to move the loop body, including the `defer` statement, into another function that is called on each iteration:

```go
for _, filename := range filenames {
	if err := doFile(filename); err != nil {
		return err
	}
}

func doFile(filename string) error {
	f, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer f.Close()
	// ...process f...
}
```

The example below is an improved `fetch` program ([Section 1.5](ch1.md#fetching-a-url)) that writes the HTTP response to a local file instead of to the standard output. It derives the file name from the last component of the URL path, which it obtains using the `path.Base` function.

<small>[gopl.io/ch5/fetch/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch5/fetch/main.go)</small>

```go
// Fetch downloads the URL and returns the
// name and length of the local file.
func fetch(url string) (filename string, n int64, err error) {
	resp, err := http.Get(url)
	if err != nil {
		return "", 0, err
	}
	defer resp.Body.Close()

	local := path.Base(resp.Request.URL.Path)
	if local == "/" {
		local = "index.html"
	}
	f, err := os.Create(local)
	if err != nil {
		return "", 0, err
	}
	n, err = io.Copy(f, resp.Body)
	// Close file, but prefer error from Copy, if any.
	if closeErr := f.Close(); err == nil {
		err = closeErr
	}
	return local, n, err
}
```

1. The call to `resp.Body.Close` is deferred.
2. It's tempting to use a second deferred call, to `f.Close`, to close the local file, but this would be subtly wrong because `os.Create` opens a file for writing, creating it as needed. On many file systems, notably NFS, write errors are not reported immediately but may be postponed until the file is closed. Failure to check the result of the close operation could cause serious data loss to go unnoticed.
3. If both `io.Copy` and `f.Close` fail, we should prefer to report the error from `io.Copy` since it occurred first and is more likely to tell us the root cause.

### Panic

Go's type system catches many mistakes at compile time; other mistakes, such as an out-of-bounds array access or nil pointer dereference, require checks at run time. When the Go runtime detects these mistakes, it *panics*.

During a typical panic, normal execution stops, all deferred function calls in that goroutine are executed, and the program crashes with a log message:

1. This log message includes the panic value, which is usually an error message and a [stack trace](https://en.wikipedia.org/wiki/Stack_trace) (for each goroutine) showing the stack of function calls that were active at the time of the panic.
2. This log message often has enough information to diagnose the root cause of the problem without running the program again, so it should always be included in a bug report about a panicking program.



### Recover

### Doubts and Solution

#### Verbatim

##### **p131 on error handling**

> After checking an error, failure is usually dealt with before success.

<span class="text-danger">Question</span>: What does it mean exactly?
