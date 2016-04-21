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
### Errors
### Function Values
### Anonymous Functions
### Variadic Functions
### Deferred Function Calls
### Panic
### Recover
