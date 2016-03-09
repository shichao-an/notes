### **Chapter 4. Composite Types**

This chapter discusses composite types: arrays, slices, maps, and structs.

* Arrays and structs are *aggregate* types, whose values are concatenations of other values in memory.
    * Arrays are homogeneous. The elements all have the same type.
    * Structs are heterogeneous.

    Both arrays and structs are fixed size.

* Slices and maps are dynamic data structures that grow as values are added.

### Arrays

An array is a fixed-length sequence of zero or more elements of a particular type.

* Arrays are rarely used directly in Go due to fixed length. Slices are commonly used due to versatililty.
* The built-in function `len` returns the number of elements in the array.

```go
var a [3]int // array of 3 integers
fmt.Println(a[0]) // print the first element
fmt.Println(a[len(a)-1]) // print the last element, a[2]

// Print the indices and elements.
for i, v := range a {
	fmt.Printf("%d %d\n", i, v)
}

// Print the elements only.
for _, v := range a {
	fmt.Printf("%d\n", v)
}
```

By default, the elements of an array are initially set to the [zero value](https://golang.org/ref/spec#The_zero_value) for the element type.

#### Array Literals *

An **array literal** can be used to initialize an array with a list of values:

```go
var q [3]int = [3]int{1, 2, 3}
var r [3]int = [3]int{1, 2}
fmt.Println(r[2]) // "0"
```

If an ellipsis "..." appears in place of the length, then the array length is determined by the number of initializers. The definition of `q` in the above example can be simplified to:

```go
q := [...]int{1, 2, 3}
fmt.Printf("%T\n", q) // "[3]int"
```

The size of an array is part of its type. For example, `[3]int` and `[4]int` are different types. The size must be a constant expression, whose value can be computed as the program is being compiled.

```go
q := [3]int{1, 2, 3}
q = [4]int{1, 2, 3, 4} // compile error: cannot assign [4]int to [3]int
```

The literal syntax is similar for arrays, slices, maps, and structs, as discussed later. Besides specifying a list of values in order, but it is also possible to specify a list of index and value pairs, for example:

```go
type Currency int

const (
	USD Currency = iota
	EUR
	GBP
	RMB
)

symbol := [...]string{USD: "$", EUR: "€", GBP: "£", RMB: "¥"}
fmt.Println(RMB, symbol[RMB]) // "3 ¥"
```

Indices can appear in any order and some may be omitted. Unspecified values take on the zero value for the element type. For instance:

```go
r := [...]int{99: -1}
```

This defines an array `r` with 100 elements, all zero except for the last, which has value −1.

#### Comparison of Arrays *

If element type is comparable, then the array type is also comparable. We can directly compare two arrays of that type using the `==` operator, which reports whether all corresponding elements are equal. The `!=` operator is its negation.

```go
a := [2]int{1, 2}
b := [...]int{1, 2}
c := [2]int{1, 3}
fmt.Println(a == b, a == c, b == c) // "true false false"
d := [3]int{1, 2}
fmt.Println(a == d) // compile error: cannot compare [2]int == [3]int
```

[p83]

#### Arrays as Function Parameters *

When a function is called, a copy of each argument value is assigned to the corresponding parameter variable, so the function receives a copy, not the original. This also applies to arrays in Go. This behavior is different from languages that implicitly pass arrays by reference.

Passing large arrays in this way can be inefficient, and any changes that the function makes to array elements affect only the copy, not the original. We can explicitly pass a pointer to an array. For example, the following function `zero` zeroes the contents of a `[32]byte` array:

```go
func zero(ptr *[32]byte) {
	for i := range ptr {
		ptr[i] = 0
	}
}
```

The following function is a different version of `zero` that uses the array literal `[32]byte{}`, each element of which has the zero value (which is zero) for `byte`.

```go
func zero(ptr *[32]byte) {
	*ptr = [32]byte{}
}
```

Passing a pointer to an array is efficient and allows the called function to mutate the caller’s variable. However, arrays are still inherently inflexible because of their fixed size. In the above example:

* The `zero` function will not accept a pointer to a `[16]byte` variable
* There is no way to add or remove array elements.

For these reasons, other than special cases like [SHA256’s fixed-size hash](https://github.com/shichao-an/gopl.io/blob/master/ch4/sha256/main.go), arrays are seldom used as function parameters and instead, slices are used.
