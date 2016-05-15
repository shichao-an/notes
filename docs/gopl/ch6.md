### **Chapter 6. Methods**

An *object* is a value or variable that has methods, and a *method* is a function associated with a particular type. An object-oriented program uses methods to express the properties and operations of each data structure so that clients need not access the object's representation directly.

[p155]

This chapter discusses the following topics on methods:

* How to define and use methods effectively
* Encapsulation
* Composition

### Method Declarations

A method is declared with a variant of the ordinary function declaration in which an extra parameter appears before the function name. The parameter attaches the function to the type of that parameter.

<small>[gopl.io/ch6/geometry/geometry.go](https://github.com/shichao-an/gopl.io/blob/master/ch6/geometry/geometry.go)</small>

```go
package geometry

import "math"

type Point struct{ X, Y float64 }

// traditional function
func Distance(p, q Point) float64 {
	return math.Hypot(q.X-p.X, q.Y-p.Y)
}

// same thing, but as a method of the Point type
func (p Point) Distance(q Point) float64 {
	return math.Hypot(q.X-p.X, q.Y-p.Y)
}
```

The extra parameter `p` is called the method's *receiver*, a legacy from early object-oriented languages that described calling a method as "sending a message to an object".

In Go, the receiver does not have a special name like `this` or `self`; it's naming is similar to any other parameter. Since the receiver name will be frequently used, it's a good idea to choose something short and to be consistent across methods. A common choice is the first letter of the type name, like `p` for `Point`.

In a method call, the receiver argument appears before the method name. This parallels the declaration, in which the receiver parameter appears before the method name.

```go
p := Point{1, 2}
q := Point{4, 6}
fmt.Println(Distance(p, q)) // "5", function call
fmt.Println(p.Distance(q))  // "5", method call
```

There's no conflict between the two declarations of functions called `Distance` above:

* The first declares a package-level function called `geometry.Distance`.
* The second declares a method of the type `Point` called `Point.Distance`.

Since each type has its own name space for methods, we can use the name `Distance` for other methods as long as they belong to different types. The following example defines a type `Path` that represents a sequence of line segments and a `Distance` method:

```go
// A Path is a journey connecting the points with straight lines.
type Path []Point

// Distance returns the distance traveled along the path.
func (path Path) Distance() float64 {
	sum := 0.0
	for i := range path {
		if i > 0 {
			sum += path[i-1].Distance(path[i])
		}
	}
	return sum
}
```

Although `Path` is a named slice type, not a struct type like `Point`, we can still define methods for it.

Unlike many other object-oriented languages, <u>Go allows methods to be associated with any type, such as numbers, strings, slices, maps, and even functions.</u> Methods may be declared on any named type defined in the same package, so long as its underlying type is neither a pointer nor an interface.

The two `Distance` methods have different types. They're not related to each other at all, though `Path.Distance` uses `Point.Distance` internally to compute the length of each segment that connects adjacent points.

The following code calls the new method to compute the perimeter of a right triangle:

```go
perim := Path{
	{1, 1},
	{5, 1},
	{5, 4},
	{1, 1},
}

fmt.Println(perim.Distance()) // "12"
```

In the two examples above, there are two calls to methods named `Distance`. <u>The compiler determines which function to call based on both the method name and the type of the receiver.</u>

* In the first, `path[i-1]` has type `Point` so `Point.Distance` is called.
* In the second, `perim` has type `Path`, so `Path.Distance` is called.

All methods of a given type must have unique names, but different types can use the same name for a method, like the `Distance` methods for `Point` and `Path`; there's no need to qualify function names (for example, `PathDistance`) to disambiguate. The first benefit to using methods over ordinary functions is: method names can be shorter. This benefit is magnified for calls originating outside the package, since they can use the shorter name and omit the package name:

```go
import "gopl.io/ch6/geometry"
perim := geometry.Path{{1, 1}, {5, 1}, {5, 4}, {1, 1}}
fmt.Println(geometry.PathDistance(perim)) // "12", standalone function
fmt.Println(perim.Distance())             // "12", method of geometry.Path
```

### Methods with a Pointer Receiver

Calling a function makes a copy of each argument value. If either of the following occurs, we must pass the address of the variable using a pointer:

* The function needs to update a variable.
* An argument is so large that we wish to avoid copying it.

The same goes for methods that need to update the receiver variable: we attach them to the pointer type, such as `*Point`. For example:

```go
func (p *Point) ScaleBy(factor float64) {
	p.X *= factor
	p.Y *= factor
}
```

The name of this method is `(*Point).ScaleBy`. The parentheses are necessary; without them, the expression would be parsed as `*(Point.ScaleBy)`.

Convention dictates that if any method of `Point` has a pointer receiver, then all methods of `Point` should have a pointer receiver, even ones that don't strictly need it.  We've broken this rule for `Point` so that we can show both kinds of method.

Named types (`Point`) and pointers to them (`*Point`) are the only types that may appear in a
receiver declaration. <u>To avoid ambiguities, method declarations are not permitted on named types that are themselves `pointer` types</u>:

```go
type P *int
func (P) f() { /* ... */ } // compile error: invalid receiver type
```

The `(*Point).ScaleBy` method can be called by providing a `*Point` receiver. The following three cases are equivalent:

```go
r := &Point{1, 2}
r.ScaleBy(2)
fmt.Println(*r) // "{2, 4}"
```

```go
p := Point{1, 2}
pptr := &p
pptr.ScaleBy(2)
fmt.Println(p) // "{2, 4}"
```

```go
p := Point{1, 2}
(&p).ScaleBy(2)
fmt.Println(p) // "{2, 4}"
```

The last two cases are verbose; <u>if the receiver `p` is a variable of type `Point` but the method requires a *Point receiver, the compiler will perform an implicit `&p` on the variable.</u> So we can use the following shorthand:

```go
p.ScaleBy(2)
```

This works only for variables, including struct fields like `p.X` and array or slice elements like `perim[0]`. We cannot call a `*Point` method on a non-addressable `Point` receiver, because there's no way to obtain the address of a temporary value. For example:

```go
Point{1, 2}.ScaleBy(2) // compile error: can't take address of Point literal
```

However, we can call a `Point` method (e.g. `Point.Distance`) with a `*Point` receiver, because there is a way to obtain the value from the address by loading the value pointed to by the receiver. The compiler will perform an implicit `*` on the variable. These two function calls are equivalent:

```go
pptr.Distance(q)
(*pptr).Distance(q)
```

#### Summary of three cases *

In every valid method call expression, exactly one of these three statements is true.

**Case 1: the receiver argument has the same type as the receiver parameter.** For example, both have type `T` or both have type `*T`:

```go
Point{1, 2}.Distance(q) // Point
pptr.ScaleBy(2)         // *Point
```

**Case 2: the receiver argument is a variable of type `T` and the receiver parameter has type `*T`.** The compiler implicitly takes the address of the variable. For example:

```go
p.ScaleBy(2) // implicit (&p)
```

**Case 3: the receiver argument has type `*T` and the receiver parameter has type `T`.** The compiler implicitly dereferences the receiver, in other words, loads the value. For example:

```go
pptr.Distance(q) // implicit (*pptr)
```

If all the methods of a named type `T` have a receiver type of `T` itself (not `*T`), it is safe to copy instances of that type; calling any of its methods necessarily makes a copy. For example, `time.Duration` values are liberally copied, including as arguments to functions.

But if any method has a pointer receiver, you should avoid copying instances of `T` because doing so may violate internal invariants. For example, copying an instance of `bytes.Buffer` would cause the original and the copy to alias ([Section 2.3.2](ch2.md#pointers)) the same underlying array of bytes. Subsequent method calls would have unpredictable effects.

#### Nil Is a Valid Receiver Value

Some methods allow nil pointers as their receivers, especially if `nil` is a meaningful zero value of the type (e.g. maps and slices), just as some functions allow nil pointers as arguments. For example, `nil` represents the empty list:

```go
// An IntList is a linked list of integers.
// A nil *IntList represents the empty list.
type IntList struct {
	Value int
	Tail *IntList
}

// Sum returns the sum of the list elements.
func (list *IntList) Sum() int {
	if list == nil {
		return 0
	}
	return list.Value + list.Tail.Sum()
}
```

When you define a type whose methods allow nil as a receiver value, it's worth documenting this explicitly in the comment, as in the example above.

The following is part of the definition of the Values type from the [`net/url`](https://golang.org/pkg/net/url/) package:

```go
package url

// Values maps a string key to a list of values.
type Values map[string][]string

// Get returns the first value associated with the given key,
// or "" if there are none.
func (v Values) Get(key string) string {
	if vs := v[key]; len(vs) > 0 {
		return vs[0]
	}
	return ""
}

// Add adds the value to key.
// It appends to any existing values associated with key.
func (v Values) Add(key, value string) {
	v[key] = append(v[key], value)
}
```

It exposes its representation as a map but also provides methods to simplify access to the map, whose values are slices of strings; it's a [*multimap*](https://en.wikipedia.org/wiki/Multimap). Its clients can use its intrinsic operators (`make`, slice literals, `m[key]`, and so on), or its methods, or both:

<small>[gopl.io/ch6/urlvalues/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch6/urlvalues/main.go)</small>

```go
m := url.Values{"lang": {"en"}} // direct construction
m.Add("item", "1")
m.Add("item", "2")

fmt.Println(m.Get("lang")) // "en"
fmt.Println(m.Get("q"))    // ""
fmt.Println(m.Get("item")) // "1"      (first value)
fmt.Println(m["item"])     // "[1 2]"  (direct map access)

m = nil
fmt.Println(m.Get("item")) // ""
m.Add("item", "3")         // panic: assignment to entry in nil map
```

In the final call to `Get`, the nil receiver behaves like an empty map. It is equivalent to being written as `Values(nil).Get("item"))`, not `nil.Get("item")`, which will not compile because the type of `nil` has not been determined (see [modified version of the example above](https://play.golang.org/p/fW0q7pRRUp)). By contrast, the final call to `Add` panics as it tries to update a `nil` map.

Because `url.Values` is a map type and a map refers to its key/value pairs indirectly, any updates and deletions that `url.Values.Add` makes to the map elements are visible to the caller. However, as with ordinary functions, any changes a method makes to the reference itself, like setting it to `nil` or making it refer to a different map data structure, will not be reflected in the caller.

### Composing Types by Struct Embedding

The following example defines a `ColoredPoint` type:

```go
import "image/color"

type Point struct{ X, Y float64 }

type ColoredPoint struct {
	Point
	Color color.RGBA
}
```

We could have defined `ColoredPoint` as a struct of three fields, but instead we embedded a `Point` to provide the `X` and `Y` fields. As discussed in [Section 4.4.3](ch4.md#struct-embedding-and-anonymous-fields), embedding enables us to take a syntactic shortcut to defining a `ColoredPoint` that contains all the fields of `Point`, plus some more. We can select the fields of `ColoredPoint` that were contributed by the embedded `Point` without mentioning `Point`:

```go
var cp ColoredPoint
cp.X = 1
fmt.Println(cp.Point.X) // "1"
cp.Point.Y = 2
fmt.Println(cp.Y) // "2"
```

A similar mechanism applies to the methods of `Point`. We can call methods of the embedded `Point` field using a receiver of type `ColoredPoint`, even though `ColoredPoint` has no declared methods:

```go
red := color.RGBA{255, 0, 0, 255}
blue := color.RGBA{0, 0, 255, 255}
var p = ColoredPoint{Point{1, 1}, red}
var q = ColoredPoint{Point{5, 4}, blue}
fmt.Println(p.Distance(q.Point)) // "5"
p.ScaleBy(2)
q.ScaleBy(2)
fmt.Println(p.Distance(q.Point)) // "10"
```

The methods of `Point` have been *promoted* to `ColoredPoint`. In this way, <u>embedding allows complex types with many methods to be built up by the *composition* of several fields, each providing a few methods.</u>

Note that it is a mistake to view `Point` as a base class and `ColoredPoint` as a subclass or derived class, or to interpret the relationship between these types as if a `ColoredPoint` "is a" Point, from a object-oriented language perspective. Notice the calls to `Distance` above. `Distance` has a parameter of type `Point`, and `q` is not a `Point`, so although `q` does have an embedded field of that type, we must explicitly select it. Attempting to pass `q` would be an error:

```go
p.Distance(q) // compile error: cannot use q (ColoredPoint) as Point
```

A `ColoredPoint` is not a `Point`, but it "has a" `Point`, and it has two additional methods `Distance` and `ScaleBy` promoted from `Point`. In terms of implementation, the embedded field instructs the compiler to generate additional wrapper methods that delegate to the declared methods, equivalent to these:

```go
func (p ColoredPoint) Distance(q Point) float64 {
	return p.Point.Distance(q)
}
func (p *ColoredPoint) ScaleBy(factor float64) {
	p.Point.ScaleBy(factor)
}
```

When `Point.Distance` is called by the first of these wrapper methods, its receiver value is `p.Point`, not `p`. <u>There is no way for the `Point.Distance` method to access the `ColoredPoint` in which the `Point` is embedded.</u>

The type of an anonymous field may be a pointer to a named type, in which case fields and methods are promoted indirectly from the pointed-to object. Adding another level of indirection enables us to share common structures and vary the relationships between objects dynamically. The declaration of `ColoredPoint` below embeds a `*Point`:

```go
type ColoredPoint struct {
	*Point
	Color color.RGBA
}

p := ColoredPoint{&Point{1, 1}, red}
q := ColoredPoint{&Point{5, 4}, blue}
fmt.Println(p.Distance(*q.Point)) // "5"
q.Point = p.Point                 // p and q now share the same Point
p.ScaleBy(2)
fmt.Println(*p.Point, *q.Point) // "{2 2} {2 2}"
```

A struct type may have more than one anonymous field. If the declaration of `ColoredPoint` is:

```go
type ColoredPoint struct {
	Point
	color.RGBA
}
```

Then a value of this type would have the following:

* All the methods of `Point`
* All the methods of `RGBA`
* Any additional methods declared on `ColoredPoint` directly

When the compiler resolves a selector such as `p.ScaleBy` to a method, it looks for that method in the following order:

1. Directly declared method named `ScaleBy`
2. Methods promoted once from `ColoredPoint`'s embedded fields
3. Methods promoted twice from embedded fields within `Point` and `RGBA`, and so on

The compiler reports an error if the selector was ambiguous because two methods were promoted from the same rank.

Methods can be declared only on named types (e.g. `Point`) and pointers to them (e.g. `*Point`). With embedding, it's possible and sometimes useful for *unnamed* struct types to have methods.

The following example shows part of a simple cache implemented using two package-level variables, a mutex ([Section 9.2](ch9.md##mutual-exclusion-syncmutex)) and the map that it guards:

```go
var (
	mu sync.Mutex // guards mapping
	mapping = make(map[string]string)
)

func Lookup(key string) string {
	mu.Lock()
	v := mapping[key]
	mu.Unlock()
	return v
}
```

The version below is functionally equivalent but groups together the two related variables in a single package-level variable, cache:

```go
var cache = struct {
	sync.Mutex
	mapping map[string]string
} {
	mapping: make(map[string]string),
}

func Lookup(key string) string {
	cache.Lock()
	v := cache.mapping[key]
	cache.Unlock()
	return v
}
```

The new variable gives more expressive names to the variables related to the cache, and because the `sync.Mutex` field is embedded within it, its `Lock` and `Unlock` methods are promoted to the unnamed struct type, allowing us to lock the `cache` with a self-explanatory syntax.

### Method Values and Expressions

### Example: Bit Vector Type

### Encapsulation

### Doubts and Solution

#### Verbatim

##### **p161 pointer receiver**

> Any changes a method makes to the reference itself, like setting it to `nil` or making it refer to a different map data structure, will not be reflected in the caller.

<span class="text-danger">Question</span>: What does it mean?

<span class="text-info">Solution</span>:

The "will not be reflected in the caller" probably means "no effect" in the caller function. This is similar to setting an argument (within the callee function) to `nil` or making it refer to another object.
