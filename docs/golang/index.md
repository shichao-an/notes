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
* Method set: collection of all the methods on a given type T (or *T)
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

- - -

### References

* [TWTG] *The Way To Go: A Thorough Introduction To The Go Programming Language*
* [EG] [Effective Go](https://golang.org/doc/effective_go.html)
* [TGB] [The Go Blog](https://blog.golang.org/)
