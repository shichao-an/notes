## Golang

### Structs
#### Visibility

The naming of the struct type and its fields adheres to the visibility rule. It is possible that an exported struct type has a mix of fields: some exported, others not.

#### Factory methods

Force using factory methods on a private type [TWTG p233]:

```go
wrong := new(matrix.matrix)    // will NOT compile (matrix is private)
right := matrix.NewMatrix(...)   // the ONLY way to instantiate a matrix
```

#### Structs with tags

Only the package `reflect` can access tag content. `reflect.TypeOf()` on a variable gives the right type; if this is a struct type, it can be indexed by `Field`, and then the `Tag` property can be used. For example:

* [struct_tag.go](https://github.com/shichao-an/twtg/blob/master/code_examples/chapter_10/struct_tag.go)

#### Anonymous fields and embedded structs

Conflicting names [TWTG p239]

1. An outer name hides an inner name. This provides a way to override a field or method.
2. If the same name appears twice at the same level, it is an error if the name is used by the program.

### Methods

* Receiver type
* Method set: collection of all the methods on a given type `T` (or `*T`)
* No method overloading
* A method and the type on which it acts must be defined in the same package
* Pointer or value as receiver: if for a type `T` a method `Meth()` exists on `*T` and `t` is a variable of type `T`, then `t.Meth()` is automatically translated to `(&t).Meth()` [TWTG p246]

#### Methods on embedded types and inheritance

* Overriding: [method4.go](https://github.com/shichao-an/twtg/blob/master/code_examples/chapter_10/method4.go) [TWTG p250]
* Embedding multiple anonymous types

#### Embed functionality in a type

1. Aggregation (or composition): include a named field of the type of the wanted functionality
2. Embedding

#### Format specifiers

* `%T`: complete type specification
* `%#v` complete output of the instance with its fields

### Interfaces

Interfaces in Go provide a way to specify the behavior of an object: if something can do this, then it can be used here.

* A type doesn’t have to state explicitly that it implements an interface: interfaces are satisfied implicitly. Multiple types can implement the same interface.
* A type that implements an interface can also have other functions. 
* A type can implement many interfaces.
* An interface type can contain a reference to an instance of any of the types that implement the interface (an interface has what is called a dynamic type)

The interface variable both contains the value of the receiver instance and a pointer to the appropriate method in a method table.

* [interfaces_poly.go](https://github.com/shichao-an/twtg/blob/master/code_examples/chapter_11/interfaces_poly.go)

#### Interface embedding interfaces
An interface can contain the name of one or more other interface(s), which is equivalent to explicitly enumerating the methods of the embedded interface in the containing interface. [TWTG p270]

#### Detect and convert the type of an interface variable: type assertions

We can test if `varI` (interface variable) contains at a certain moment a variable of type `T` with the type assertion test [TWTG p271]:

```go
if v, ok := varI.(T); ok {
	// checked type assertion
}
```

* [type_interfaces.go](https://github.com/shichao-an/twtg/blob/master/code_examples/chapter_11/type_interfaces.go)

#### The type switch

* [Type switch](https://golang.org/doc/effective_go.html#type_switch)

#### Testing if a value implements an interface

`v` is a value and we want to test whether it implements the `Stringer` interface:

```go
if sv, ok := v.(Stringer); ok {
	fmt.Printf(“v implements String(): %s\n”, sv.String()); // note: sv, not v
}
```

Writing functions so that they accept an interface variable as a parameter makes them more general. Use interfaces to make code more generally applicable.

#### Using method sets with interfaces

1. Pointer methods can be called with pointers.
2. Value methods can be called with values.
3. Value-receiver methods can be called with pointer values because they can be dereferenced first.
4. Pointer-receiver methods **cannot** be called with values, however, because the value stored inside an interface has no address.

Examples:

* [methodset2.go](https://github.com/shichao-an/twtg/blob/master/code_examples/chapter_11/methodset2.go)
* [sort.go](https://github.com/shichao-an/twtg/blob/master/code_examples/chapter_11/sort/sort.go)
* [sortmain.go](https://github.com/shichao-an/twtg/blob/master/code_examples/chapter_11/sortmain.go)

#### Empty Interface

A variable of empty interface type `interface{}` can through assignment receive a variable of any type.

#### Interface Slice
* [Interface slice](https://github.com/golang/go/wiki/InterfaceSlice)

#### Interface to interface

An interface value can also be assigned to another interface value, as long as the underlying value implements the necessary methods. 

<script src="https://gist.github.com/shichao-an/4f97af9d9b7333f95b87.js"></script>

- - -

### References

* [TWTG] *The Way To Go: A Thorough Introduction To The Go Programming Language*
* [EG] [Effective Go](https://golang.org/doc/effective_go.html)
* [TGB] [The Go Blog](https://blog.golang.org/)
