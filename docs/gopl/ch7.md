### **Chapter 7. Interfaces**

Interface types express generalizations or abstractions about the behaviors of other types. By generalizing, interfaces facilitate more flexible and adaptable functions because they are not tied to the details of one particular implementation.

Different from the notion of interfaces in other object-oriented languages, Go's interfaces is distinctive in that they are satisfied implicitly. In other words, there's no need to declare all the interfaces that a given concrete type satisfies; simply possessing the necessary methods is enough. With this design, you are able to create new interfaces that are satisfied by existing concrete types without changing the existing types, which is particularly useful for types defined in packages that you don't control.

This chapter discusses:

* Basic mechanics of interface types and their values
* Several important interfaces from the standard library
* Type assertions and type switches

### Interfaces as Contracts

#### Concrete type and interface type *

All the types discussed so far are *concrete types*. A concrete type specifies the exact representation of its values and exposes the intrinsic operations of that representation, such as arithmetic for numbers, or indexing, `append`, and `range` for slices. A concrete type may also provide additional behaviors through its methods. When you have a value of a concrete type, you know exactly what it is and what you can do with it.

There is another kind of type in Go called an *interface type*. An interface is an *abstract type*. It doesn't expose the representation or internal structure of its values, or the set of basic operations they support; it reveals only some of their methods. When you have a value of an interface type, you know nothing about what it is; you know only what it can do, or more precisely, what behaviors are provided by its methods.
