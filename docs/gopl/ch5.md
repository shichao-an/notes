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
### Multiple Return Values
### Errors
### Function Values
### Anonymous Functions
### Variadic Functions
### Deferred Function Calls
### Panic
### Recover
