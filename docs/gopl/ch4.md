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

#### Array literals *

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

#### Comparison of arrays *

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

#### Arrays as function parameters *

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

### Slices

Slices represent variable-length sequences whose elements all have the same type. A slice type is written `[]T`, where the elements have type `T`. It looks like an array type without a size.

A slice is a lightweight data structure that gives access to a subsequence of its [*underlying array*](https://golang.org/ref/spec#Slice_types).

#### Components of a slice *

A slice has three components:

* **Pointer**: the pointer points to the first element of the array that is reachable through the slice, which is not necessarily the array's first element.
* **Length**: the length is the number of slice elements. It can't exceed the capacity.
* **Capacity**: the capacity is usually the number of elements between the start of the slice and the end of the underlying array.

The built-in functions `len` and `cap` the values of length and capacity respectively.

Multiple slices can share the same underlying array and may refer to overlapping parts of that array.

The following figure shows an array of strings for the months of the year, and two overlapping slices of it. The array is declared as:

```go
months := [...]string{1: "January", /* ... */, 12: "December"}
```

[![Figure 4.1. Two overlapping slices of an array of months.](figure_4.1_600.png)](figure_4.1.png "Figure 4.1. Two overlapping slices of an array of months.")

The slice operator `s[i:j]`, where 0 ≤ `i` ≤ `j` ≤ `cap(s)`, creates a new slice that refers to elements `i` through `j-1` of the sequence `s`. This sequence `s` may be any of the following:

* An array variable
* A pointer to an array
* Another slice

The resulting slice has `j-i` elements. If `i` is omitted, it's 0, and if `j` is omitted, it's `len(s)`. For example:

* The slice `months[1:13]` refers to the whole range of valid months, as does the slice `months[1:]`.
* The slice `months[:]` refers to the whole array.

Overlapping slices in the figure are defined like this:

```go
Q2 := months[4:7]
summer := months[6:9]
fmt.Println(Q2)     // ["April" "May" "June"]
fmt.Println(summer) // ["June" "July" "August"]
```

The following (inefficient) code is a test for common elements of the two slices, which outputs "June":

```go
for _, s := range summer {
	for _, q := range Q2 {
		if s == q {
			fmt.Printf("%s appears in both\n", s)
		}
	}
}
```

#### Substring operation and slice operator *

The [substring operation](ch3.md#the-substring-operation) on strings is similar to the slice operator on `[]byte` slices in that:

* Both are written `x[m:n]`.
* Both return a subsequence of the original bytes, sharing the underlying representation so that both operations take constant time.

The expression `x[m:n]` yields a string if `x` is a string, or a `[]byte` if `x` is a `[]byte`.

Since a slice contains a pointer to an element of an array, passing a slice to a function permits the function to modify the underlying array elements. In other words, copying a slice creates an *alias* ([Section 2.3.2](ch2.md#pointers)) for the underlying array.

#### Reversing and rotating slices *

The function `reverse` reverses the elements of an `[]int` slice in place, and it may be applied to slices of any length.

<small>[gopl.io/ch4/rev/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/rev/main.go)</small>

```go
// reverse reverses a slice of ints in place.
func reverse(s []int) {
	for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
		s[i], s[j] = s[j], s[i]
	}
}
```

To reverse the whole array `a`:

```go
a := [...]int{0, 1, 2, 3, 4, 5}
reverse(a[:])
fmt.Println(a) // "[5 4 3 2 1 0]"
```

A simple way to *rotate* a slice left by *n* elements is to apply the `reverse` function three times: first to the leading n elements, then to the remaining elements, and finally to the whole slice.  (To rotate to the right, make the third call first.)

```go
s := []int{0, 1, 2, 3, 4, 5}
// Rotate s left by two positions.
reverse(s[:2])
reverse(s[2:])
reverse(s)
fmt.Println(s) // "[2 3 4 5 0 1]"
```

In the above two examples, we can see that expression that initializes the slice `s` differs from that for the array `a`. A slice literal looks like an array literal, a sequence of values separated by commas and surrounded by braces, but the size is not given. <u>This implicitly creates an array variable of the right size and yields a slice that points to it.</u> As with [array literals](#array-literals), slice literals may specify the values in order, or give their indices explicitly, or use a mix of the two styles.

#### Comparison of slices *

Unlike arrays, slices are not comparable, so we cannot use `==` to test whether two slices contain the same elements. The standard library provides the highly optimized `bytes.Equal` function for comparing two slices of bytes (`[]byte`).

To compare other types of slice, we must do the comparison ourselves. For example:

```go
func equal(x, y []string) bool {
	if len(x) != len(y) {
		return false
	}
	for i := range x {
	  if x[i] != y[i] {
	  	return false
		}
	}
	return true
}
```

Although this "deep" equality test is natural and no more costly at run time than the `==` operator for arrays of strings, slice comparisons do not work this way. There are two reasons why deep equivalence is problematic:

1. Unlike array elements, the elements of a slice are indirect, making it possible for a slice to contain itself. There is no simple, efficient and obvious way to deal with such cases.
2. Because slice elements are indirect, a fixed slice value may contain different elements at different times as the contents of the underlying array are modified.
    * **Deep equivalence would make slices unsuitable for use as map keys.** Because Go's map type (hash table) makes only shallow copies of its keys, it requires that equality for each key remain the same throughout the lifetime of the map.
    * **Shallow equality test is useful but confusing.** For reference types like pointers and channels, the `==` operator tests reference identity, that is, whether the two entities refer to the same thing. An analogous "shallow" equality test for slices could be useful, and it would solve the problem with maps, but the inconsistent treatment of slices and arrays by the `==` operator would be confusing. <u>The safest choice is to disallow slice comparisons altogether.</u>

The only legal slice comparison is against `nil`:

```go
if summer == nil { /* ... */ }
```

#### The zero value of slices *

The zero value of a slice type is `nil`.

* A nil slice has no underlying array.
* A nil slice has length and capacity zero.

There are also non-nil slices of length and capacity zero, such as `[]int{}` or `make([]int, 3)[3:]`.

As with any type that can have nil values, the nil value of a particular slice type can be written using a conversion expression such as `[]int(nil)`.

```go
var s []int    // len(s) == 0, s == nil
s = nil        // len(s) == 0, s == nil
s = []int(nil) // len(s) == 0, s == nil
s = []int{}    // len(s) == 0, s != nil
```

To test whether a slice is empty, use `len(s) == 0`, not `s == nil`. Other than comparing equal to `nil`, a nil slice behaves like any other zero-length slice (for example, `reverse(nil)` is perfectly safe). <u>Unless clearly documented to the contrary, Go functions should treat all zero-length slices the same way, whether nil or non-nil.</u>

The built-in function `make` creates a slice of a specified element type, length, and capacity. The capacity argument may be omitted, in which case the capacity equals the length.

```go
make([]T, len)
make([]T, len, cap) // same as make([]T, cap)[:len]
```

* In the first form, the slice is a view of the entire array.
* In the second, the slice is a view of only the array's first `len` elements, but its capacity includes the entire array. The additional elements are set aside for future growth.

Behind the scene, `make` creates an unnamed array variable and returns a slice of it; the array is accessible only through the returned slice.



#### The `append` Function
