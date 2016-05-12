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

### Composing Types by Struct Embedding

### Method Values and Expressions

### Example: Bit Vector Type

### Encapsulation
