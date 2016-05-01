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

The built-in `append` function appends items to slices:

```go
var runes []rune
for _, r := range "Hello, 世界" {
	runes = append(runes, r)
}
fmt.Printf("%q\n", runes) // "['H' 'e' 'l' 'l' 'o' ',' '' '世' '界']"
```

The loop uses `append` to build the slice of nine runes encoded by the string literal. It is equivalent to using the built-in conversion: `[]rune("Hello, 世界")`.

The following examples discusses how the `append` works, which is crucial to understanding how slices work.

In the code below, `appendInt` is a function specialized for `[]int` slices:

<small>[gopl.io/ch4/append/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/append/main.go)</small>

```go
func appendInt(x []int, y int) []int {
	var z []int
	zlen := len(x) + 1
	if zlen <= cap(x) {
		// There is room to grow.  Extend the slice.
		z = x[:zlen]
	} else {
		// There is insufficient space.  Allocate a new array.
		// Grow by doubling, for amortized linear complexity.
		zcap := zlen
		if zcap < 2*len(x) {
			zcap = 2 * len(x)
		}
		z = make([]int, zlen, zcap)
		copy(z, x) // a built-in function; see text
	}
	z[len(x)] = y
	return z
}
```

Each call to `appendInt` checks whether the slice has sufficient capacity to hold the new elements in the existing array:

* If there is sufficient capacity, `appendInt` extends the slice by defining a larger slice (still within the original array), copies the element `y` into the new space, and returns the slice. The input `x` and the result `z` share the same underlying array.
* If there is insufficient space for growth, `appendInt` allocates a new array big enough to hold the result, copy the values from `x` into it, then append the new element `y`. The result `z` now refers to a different underlying array from `x`.

##### **The `copy` function** *

The built-in function `copy` copies elements from one slice to another of the same type. Its first argument is the destination and its second is the source, resembling the order of operands in an assignment like `dst = src`. The slices may refer to the same underlying array, or they may even overlap.

<u>`copy` actually copies `k` elements, where `k` is smaller of the two slice lengths, and returns `k`. There is no danger of running off the end or overwriting something out of range.</u> [p89]

For efficiency, expanding the array by doubling its size at each expansion avoids an excessive number of allocations and ensures that appending a single element takes constant time on average. The following program demonstrates the effect:

```go
func main() {
	var x, y []int
	for i := 0; i < 10; i++ {
		y = appendInt(x, i)
		fmt.Printf("%d cap=%d\t%v\n", i, cap(y), y)
		x = y
	}
}
```

Each change in capacity indicates an allocation and a copy:

```text
0 cap=1   [0]
1 cap=2   [0 1]
2 cap=4   [0 1 2]
3 cap=4   [0 1 2 3]
4 cap=8   [0 1 2 3 4]
5 cap=8   [0 1 2 3 4 5]
6 cap=8   [0 1 2 3 4 5 6]
7 cap=8   [0 1 2 3 4 5 6 7]
8 cap=16  [0 1 2 3 4 5 6 7 8]
9 cap=16  [0 1 2 3 4 5 6 7 8 9]
```

The following two figures show what happen at `i=3` iteration: appending with room to grow. [p89-90]

[![Figure 4.2. Appending with room to grow.](figure_4.2_600.png)](figure_4.2.png "Figure 4.2. Appending with room to grow.")

The following two figures show what happen at `i=4` iteration: appending without room to grow.  [p90]

[![Figure 4.3. Appending without room to grow.](figure_4.3_600.png)](figure_4.3.png "Figure 4.3. Appending without room to grow.")

##### **Updating the slice variable when calling `append`** *

The built-in `append` function uses a more sophisticated growth strategy than `appendInt`. Usually we don't know whether a given call to `append` will cause a reallocation, so we can't assume that the original slice refers to the same array as the resulting slice or not. This means we must not assume that operations on elements of the old slice will (or will not) be reflected in the new slice. As a result, <u>it's usual to assign the result of a call to `append` to the same slice variable whose value we passed to `append`:</u>

```go
runes = append(runes, r)
```

<u>Updating the slice variable is required not just when calling `append`, but for any function that may change the length or capacity of a slice or make it refer to a different underlying array.</u> To use slices correctly, remember that although the elements of the underlying array are indirect, the slice's pointer, length, and capacity are not. To update them requires an assignment like the one above. Slices are not "pure" reference types but resemble an aggregate type such as this struct:

```go
type IntSlice struct {
	ptr *int
	len, cap int
}
```

##### **Variadic functions** *

The `appendInt` function adds a single element to a slice, but the built-in `append` is able to add more than one new element, or a whole slice of them.

```go
var x []int
x = append(x, 1)
x = append(x, 2, 3)
x = append(x, 4, 5, 6)
x = append(x, x...) // append the slice x
fmt.Println(x)      // "[1 2 3 4 5 6 1 2 3 4 5 6]"
```

The following modification of `append` matches the behavior of the built-in `append`. The ellipsis "..." in the declaration of `appendInt` makes the function [**variadic**](https://gobyexample.com/variadic-functions): it accepts any number of final arguments. The corresponding ellipsis in the call above to `append` shows how to supply a list of arguments from a slice. Variadic functions are detailed in [Section 5.7](ch5.md#variadic-functions).

```go
func appendInt(x []int, y ...int) []int {
	var z []int
	zlen := len(x) + len(y)
	// ...expand z to at least zlen...
	copy(z[len(x):], y)
	return z
}
```

#### In-Place Slice Techniques

This section discusses examples of functions that modify the elements of a slice in place, like `rotate` and `reverse`.

Given a list of strings, the `nonempty` function returns the non-empty ones:

<small>[gopl.io/ch4/nonempty/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/nonempty/main.go)</small>

```go
// Nonempty is an example of an in-place slice algorithm.
package main

import "fmt"

// nonempty returns a slice holding only the non-empty strings.
// The underlying array is modified during the call.
func nonempty(strings []string) []string {
	i := 0
	for _, s := range strings {
		if s != "" {
			strings[i] = s
			i++
		}
	}
	return strings[:i]
}
```

The subtle part is that the input slice and the output slice share the same underlying array.  This avoids the need to allocate another array, though the contents of data are partly overwritten, as shown in the second `Printf` statement below:

```go
data := []string{"one", "", "three"}
fmt.Printf("%q\n", nonempty(data)) // `["one" "three"]`
fmt.Printf("%q\n", data)           // `["one" "three" "three"]`
```

The `nonempty` function can also be written using `append`:

```go
func nonempty2(strings []string) []string {
	out := strings[:0] // zero-length slice of original
	for _, s := range strings {
		if s != "" {
			out = append(out, s)
		}
	}
	return out
}
```

The above two variants, which reuse an array, requires that at most one output value is produced for each input value, which is true of many algorithms that filter out elements of a sequence or combine adjacent ones. Such usage is the exception, not the rule, but it can be clear, efficient, and useful on occasion.

#### Implementing a stack using a slice *

A slice can be used to implement a stack. Given an initially empty slice `stack`, we can push a new value onto the end of the slice with `append`:

```go
stack = append(stack, v) // push v
```

The top of the stack is the last element:

```go
top := stack[len(stack)-1] // top of stack
```

Shrink the stack by popping that element:

```go
stack = stack[:len(stack)-1] // pop
```

#### Removing an element from a slice *

To remove an element from the middle of a slice, preserving the order of the remaining elements, use `copy` to slide the higher-numbered elements down by one to fill the gap:

```go
func remove(slice []int, i int) []int {
  copy(slice[i:], slice[i+1:])
	return slice[:len(slice)-1]
}

func main() {
	s := []int{5, 6, 7, 8, 9}
	fmt.Println(remove(s, 2)) // "[5 6 8 9]"
}
```

If we don't need to preserve the order, just move the last element into the gap:

```go
func remove(slice []int, i int) []int {
	slice[i] = slice[len(slice)-1]
	return slice[:len(slice)-1]
}

func main() {
	s := []int{5, 6, 7, 8, 9}
	fmt.Println(remove(s, 2)) // "[5 6 9 8]
}
```

### Maps

The hash table is  an unordered collection of key/value pairs in which all the keys are distinct, and the value associated with a given key can be retrieved, updated, or removed using a constant number of key comparisons on the average, no matter how large the hash table.

In Go, a map is a reference to a hash table. See [Go maps in action](https://blog.golang.org/go-maps-in-action) for reference.

* A map type is written `map[K]V`.
    * `K` is the type of its keys.
    * `V` is the type of its values.
* All of the keys in a given map are of the same type, and all of the values are of the same type.
    * The keys need not be of the same type as the values.
* The key type `K` must be comparable using `==`, so that the map can test whether a given key is equal to one already within it.
    * Though floating-point numbers are comparable, it's a bad idea to compare floats for equality and bad if NaN is a possible value, as mentioned in [Chapter 3](ch3.md#special-values-inf-inf-and-nan).
* There are no restrictions on the value type V.

#### Initialization of maps *

The built-in function `make` can be used to create a map:

```go
ages := make(map[string]int) // mapping from strings to ints
```

A *map literal* can also be used to create a new map populated with some initial key/value pairs:

```go
ages := map[string]int{
	"alice": 31,
	"charlie": 34,
}
```

This is equivalent to:

```go
ages := make(map[string]int)
ages["alice"] = 31
ages["charlie"] = 34
```

An alternative expression for a new empty map is `map[string]int{}`.

#### Accessing and deleting map elements *

Map elements are accessed through the usual subscript notation:

```go
ages["alice"] = 32
fmt.Println(ages["alice"]) // "32"
```

Map elements are removed with the built-in function [`delete`](https://golang.org/pkg/builtin/#delete):

```go
delete(ages, "alice") // remove element ages["alice"]
```

These operations are safe even if the element isn't in the map:

* Deleting an element using a key that isn't present in the map is a no-op.
* A map lookup using a key that isn't present returns the zero value for its type
    * For instance, if `"bob"` is not yet a key in the map, value of `ages["bob"]` will be 0, so the following example works.

```go
ages["bob"] = ages["bob"] + 1 // happy birthday!
```

The shorthand assignment forms also work for map elements:

```go
ages["bob"] += 1
ages["bob"]++  // equivalent to above
```

A map element is not a variable and we cannot take its address:

```go
_ = &ages["bob"] // compile error: cannot take address of map element
```

One reason that we can't take the address of a map element is that growing a map might cause rehashing of existing elements into new storage locations, thus potentially invalidating the address.

#### Map iteration *

A `range`-based `for` loop can be used to enumerate all the key/value pairs in the map, which is similar to slices. Continuing the previous example, successive iterations of the loop cause the `name` and `age` variables to be set to the next key/value pair:

```go
for name, age := range ages {
	fmt.Printf("%s\t%d\n", name, age)
}
```

The order of map iteration is unspecified. Different implementations might have a different ordering due to a different hash function used. In practice, the order is random (varying from one execution to the next), which is an intentional behavior: <u>making the sequence vary helps force programs to be robust across implementations.</u>

To enumerate the key/value pairs in order, we must sort the keys explicitly. The following example is a common pattern which uses the `Strings` function from the `sort` package:

```go
import "sort"
var names []string
for name := range ages {  // omit the second loop variable
	names = append(names, name)
}
sort.Strings(names)
for _, name := range names {  // use the blank identifier _ to ignore the first variable
	fmt.Printf("%s\t%d\n", name, ages[name])
}
```

It is more efficient to allocate an array of the required size. The statement below creates a slice that is initially empty but has sufficient capacity to hold all the keys of the `ages` map:

```go
names := make([]string, 0, len(ages))
```

The zero value for a map type is `nil`, which means a reference to no hash table at all.

```go
var ages map[string]int
fmt.Println(ages == nil)     // "true"
fmt.Println(len(ages) == 0)  // "true"
```

Most operations on maps, including lookup, `delete`, `len`, and `range` loops, are safe to perform on a `nil` map reference, since it behaves like an empty map. But storing to a `nil` map causes a panic:

```go
ages["carol"] = 21 // panic: assignment to entry in nil map
```

You must allocate the map before you can store into it.

#### Test the presence of elements *

Accessing a map element by subscripting always yields a value:

* If the key is present in the map, you get the corresponding value.
* If the key is not present, you get the zero value for the element type.

To know whether the element was present or not, use a test like this:

```go
age, ok := ages["bob"]
if !ok { /* "bob" is not a key in this map; age == 0. */ }
```

These two statements can be combined and written like this:

```go
if age, ok := ages["bob"]; !ok { /* ... */ }
```

Subscripting a map in this context yields two values; the second is a boolean that reports whether the element was present. The boolean variable is often called `ok`, especially if it is immediately used in an `if` condition.

#### Comparison of maps *

As with slices, maps cannot be compared to each other; the only legal comparison is with `nil`.  To test whether two maps contain the same keys and the same associated values, we must write a loop:

```go
func equal(x, y map[string]int) bool {
	if len(x) != len(y) {
		return false
	}
	for k, xv := range x {
		if yv, ok := y[k]; !ok || yv != xv {
		return false
		}
	}
	return true
}
```

In this example, `!ok` (in the second `if` condition) is used to distinguish the "missing" and "present but zero" cases. [p96]

Since the keys of a map are distinct, a map can be used to create a "`set`" type, which is not available in Go. The following program `dedup` reads a sequence of lines and prints only the first occurrence of each distinct line. (It's a variant of the `dup` program showed in [Section 1.3](ch1.md#finding-duplicate-lines).)

<small>[gopl.io/ch4/dedup/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/dedup/main.go)</small>

```go
func main() {
	seen := make(map[string]bool) // a set of strings
	input := bufio.NewScanner(os.Stdin)
	for input.Scan() {
		line := input.Text()
		if !seen[line] {
			seen[line] = true
			fmt.Println(line)
		}
	}

	if err := input.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "dedup: %v\n", err)
		os.Exit(1)
	}
}
```

If we need a map or set whose keys are slices, this cannot be expressed directly, because a map's keys must be comparable. However, it can be done by using a helper function `k` that maps each key (slice) to a string (if `x` is equivalent to `y`, then `k(x) == k(y)`), creating a map whose keys are strings and applying the helper function to each key before we access the map.

The example below uses a map to record the number of times `Add` has been called with a given list of strings. It uses `fmt.Sprintf` to convert a slice of strings into a single string that is a suitable map key, quoting each slice element with `%q` to record string boundaries:

```go
var m = make(map[string]int)
func k(list []string) string { return fmt.Sprintf("%q", list) }
func Add(list []string) { m[k(list)]++ }
func Count(list []string) int { return m[k(list)] }
```

The same approach can be used for the following:

* Any non-comparable key type.
* Comparable key types with other definitions of equality than `==`, such as case-insensitive comparisons for strings.

Besides, the type of `k(x)` needn't be a string. It can be any comparable type with the desired equivalence property, such as integers, arrays, or structs.

The following program is another example of maps that counts the occurrences of each distinct Unicode code point in its input.

<small>[gopl.io/ch4/charcount/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/charcount/main.go)</small>

[p97-99]

The [`ReadRune`](https://golang.org/pkg/bufio/#Reader.ReadRune) method (from [`bufio`](https://golang.org/pkg/bufio/)) performs UTF-8 decoding and returns three values: the decoded rune, the length in bytes of its UTF-8 encoding, and an error value. The only error we expect is end-of-file. If the input was not a legal UTF-8 encoding of a rune, the returned rune is [`unicode.ReplacementChar`](https://golang.org/pkg/unicode/#pkg-constants) and the length is 1.

The value type of a map can be a composite type, such as a map or slice. In the following code, the key type of graph is `string` and the value type is `map[string]bool`, representing a set of strings. This graph maps a string to a set of related strings, its successors in a directed graph.

<small>[gopl.io/ch4/graph/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/graph/main.go)</small>

```go
var graph = make(map[string]map[string]bool)

func addEdge(from, to string) {
	edges := graph[from]
	if edges == nil {
		edges = make(map[string]bool)
		graph[from] = edges
	}
	edges[to] = true
}

func hasEdge(from, to string) bool {
	return graph[from][to]
}
```

* The `addEdge` function populates a map lazily, that is, to initialize each value as its key appears for the first time.
* The `hasEdge` function shows how the zero value of a missing map entry works: even if neither `from` nor `to` is present, `graph[from][to]` will always give a meaningful result.

### Structs

A **struct** is an aggregate data type that groups together zero or more named values of arbitrary types as a single entity. Each value is called a *field*. All of the fields are collected into a single entity that can be copied as a unit, passed to functions and returned by them, stored in arrays, etc.

These two statements declare a struct type called `Employee` and a variable called `dilbert` that is an instance of an `Employee`:

```go
type Employee struct {
	ID         int
	Name       string
	Address    string
	DoB        time.Time
	Position   string
	Salary     int
	ManagerID  int
}

var dilbert Employee
```

The individual fields of `dilbert` are accessed using dot notation like `dilbert.Name` and `dilbert.DoB`.

Because `dilbert` is a variable, its fields are also variables. A field may be assigned to like this:

```go
dilbert.Salary -= 5000
```

The address of the filed can be taken and accessed through a pointer:

```go
position := &dilbert.Position
*position = "Senior " + *position
```

The dot notation also works with a pointer to a struct:

```go
var employeeOfTheMonth *Employee = &dilbert
employeeOfTheMonth.Position += " (proactive team player)"
```

The last statement is equivalent to:

```go
(*employeeOfTheMonth).Position += " (proactive team player)"
```

The function `EmployeeByID` takes as input an employee's ID and returns a pointer to an `Employee` struct. We can use the dot notation to access its fields:

```go
func EmployeeByID(id int) *Employee { /* ... */ }
fmt.Println(EmployeeByID(dilbert.ManagerID).Position)
id := dilbert.ID
EmployeeByID(id).Salary = 0
```

The last statement updates the `Employee` struct that is pointed to by the result of the call to `EmployeeByID`. <u>If the result type of `EmployeeByID` were changed to `Employee` instead of `*Employee`, the assignment statement would not compile since its left-hand side would not identify a variable.</u>

Fields are usually written one per line, with the field's name preceding its type. However, consecutive fields of the same type may be combined, as with `Name` and `Address` here:

```go
type Employee struct {
	ID            int
	Name, Address string
	DoB           time.Time
	Position      string
	Salary        int
	ManagerID     int
}
```

Field order is significant to type identity:

* If we combined the declaration of the `Position` field (also a string), or interchanged `Name` and `Address`, we would be defining a different struct type.
* Typically we only combine the declarations of related fields.

The name of a struct field is exported if it begins with a capital letter. This is [Go's main access control mechanism](ch2.md#local-and-exported-names). A struct type may contain a mixture of exported and unexported fields.

Struct types tend to be verbose because they often involve a line for each field. Although we could write out the whole type each time it is needed, the repetition is unnecessary. Instead, struct types usually appear within the declaration of a named type like `Employee`.

A named struct type `S` can't declare a field of the same type `S`, because an aggregate value cannot contain itself. The analogous restriction also applies to arrays. But `S` may declare a field of the pointer type `*S`, which allows creating recursive data structures like linked lists and trees. The following example uses a binary tree to implement an insertion sort:

<small>[gopl.io/ch4/treesort/sort.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/treesort/sort.go)</small>

```go
type tree struct {
	value       int
	left, right *tree
}

// Sort sorts values in place.
func Sort(values []int) {
	var root *tree
	for _, v := range values {
		root = add(root, v)
	}
	appendValues(values[:0], root)
}

// appendValues appends the elements of t to values in order
// and returns the resulting slice.
func appendValues(values []int, t *tree) []int {
	if t != nil {
		values = appendValues(values, t.left)
		values = append(values, t.value)
		values = appendValues(values, t.right)
	}
	return values
}

func add(t *tree, value int) *tree {
	if t == nil {
		// Equivalent to return &tree{value: value}.
		t = new(tree)
		t.value = value
		return t
	}
	if value < t.value {
		t.left = add(t.left, value)
	} else {
		t.right = add(t.right, value)
	}
	return t
}
```

#### The zero value of a struct *

<u>The zero value for a struct is composed of the zero values of each of its fields.</u> It is usually desirable that the zero value be a natural or sensible default, but sometimes the type designer has to work at it.

For example:

* The initial value of the `bytes.Buffer` struct is a ready-to-use empty buffer.
* The zero value of [`sync.Mutex`](https://golang.org/pkg/sync/#Mutex) is a ready-to-use unlocked mutex (discussed [Chapter 9](ch9.md))

The struct type with no fields is called the *empty struct*, written as `struct{}`. It has size zero and carries no information. Some Go programmers use it instead of `bool` as the value type of a map that represents a set, to emphasize that only the keys are significant, but the space saving is marginal and the syntax more cumbersome, so we generally avoid it.

```go
seen := make(map[string]struct{}) // set of strings
// ...
if _, ok := seen[s]; !ok {
	seen[s] = struct{}{}
	// ...first time seeing s...
}
```

#### Struct Literals

A value of a struct type can be written using a **struct literal** that specifies values for its fields.

There are two forms of struct literal.

The first form, as shown below, requires that a value be specified for every field, in the right order. The writer and reader have to remember exactly what the fields are, and it makes the code fragile if the set of fields later grow or are reordered.

```go
type Point struct{ X, Y int }
p := Point{1, 2}
```

Accordingly, this form tends to be used only within the package that defines the struct type, or with smaller struct types for which there is an obvious field ordering convention, like `image.Point{x, y}` or `color.RGBA{red, green, blue, alpha}`.

The second form is more often used, in which a struct value is initialized by listing some or all of the field names and their corresponding values, as in this statement from the Lissajous program of [Section 1.4](ch1.md#animated-gifs):

```go
anim := gif.GIF{LoopCount: nframes}
```

<u>If a field is omitted in this form of literal, it is set to the zero value for its type.</u> Because names are provided, the order of fields doesn't matter.

The two forms cannot be mixed in the same literal. Also, you cannot use the (order-based) first form of literal to sneak around the rule that unexported identifiers may not be referred to from another package.

```go
package p
type T struct{ a, b int } // a and b are not exported
```

```
package q
import "p"
var _ = p.T{a: 1, b: 2} // compile error: can't reference a, b
var _ = p.T{1, 2}       // compile error: can't reference a, b
```

Struct values can be passed as arguments to functions and returned from them. For instance, the following function scales a `Point` by a specified factor:

```go
func Scale(p Point, factor int) Point {
	return Point{p.X * factor, p.Y * factor}
}
fmt.Println(Scale(Point{1, 2}, 5)) // "{5 10}"
```

For efficiency, larger struct types are usually passed to or returned from functions indirectly using a pointer, like:

```go
func Bonus(e *Employee, percent int) int {
	return e.Salary * percent / 100
}
```

This is required if the function must modify its argument, since in a [call-by-value](https://en.wikipedia.org/wiki/Evaluation_strategy#Call_by_value) language like Go, the called function receives only a copy of an argument, not a reference to the original argument.

```go
func AwardAnnualRaise(e *Employee) {
	e.Salary = e.Salary * 105 / 100
}
```

Because structs are so commonly dealt with through pointers, it's possible to use this shorthand notation to create and initialize a struct variable and obtain its address:

```go
pp := &Point{1, 2}
```

It is exactly equivalent to

```go
pp := new(Point)
*pp = Point{1, 2}
```

`&Point{1, 2}` can be used directly within an expression, such as a function call.

#### Comparing Structs

If all the fields of a struct are comparable, the struct itself is comparable. The two expressions of the same type may be compared using `==` or `!=`. The `==` operation compares the corresponding fields of the two structs in order. In the following example, the two printed expressions are equivalent:

```go
type Point struct{ X, Y int }
p := Point{1, 2}
q := Point{2, 1}
fmt.Println(p.X == q.X && p.Y == q.Y) // "false"
fmt.Println(p == q)                   // "false"
```

Comparable struct types, like other comparable types, may be used as the key type of a map.

```go
type address struct {
	hostname string
	port int
}

hits := make(map[address]int)
hits[address{"golang.org", 443}]++
```

#### Struct Embedding and Anonymous Fields

This section discusses Go's [*struct embedding*](https://golang.org/doc/effective_go.html#embedding) mechanism, which enables us to use one named struct type as an *anonymous field* of another struct type. This provides a convenient syntactic shortcut so that a simple dot expression like `x.f` can stand for a chain of fields like `x.d.e.f`.

For example:

```go
type Circle struct {
	X, Y, Radius int
}

type Wheel struct {
	X, Y, Radius, Spokes int
}
```

A `Circle` has fields for the `X` and `Y` coordinates of its center, and a `Radius`. A `Wheel` has all the features of a `Circle`, plus `Spokes` (number of radial spokes).

The following code creates a wheel:

```go
var w Wheel
w.X = 8
w.Y = 8
w.Radius = 5
w.Spokes = 20
```

It is convenient to factor out their common parts:

```go
type Point struct {
  X, Y int
}

type Circle struct {
	Center Point
	Radius int
}

type Wheel struct {
	Circle Circle
	Spokes int
}
```

This seems clearer, but accessing the fields of a `Wheel` is more verbose:

```go
var w Wheel
w.Circle.Center.X = 8
w.Circle.Center.Y = 8
w.Circle.Radius = 5
w.Spokes = 20
```

In Go, we can declare a field with a type but no name, called an *anonymous field*. The type of the field must be a named type or a pointer to a named type.

For example, in the code below, `Circle` and `Wheel` have one anonymous field each: `Point` is embedded within `Circle`, and a `Circle` is embedded within `Wheel`.

```go
type Circle struct {
	Point
	Radius int
}

type Wheel struct {
	Circle
	Spokes int
}
```

We can refer to the names at the leaves of the implicit tree without giving the intervening names:

```go
var w Wheel
w.X = 8        // equivalent to w.Circle.Point.X = 8
w.Y = 8        // equivalent to w.Circle.Point.Y = 8
w.Radius = 5   // equivalent to w.Circle.Radius = 5
w.Spokes = 20
```

The explicit forms shown in the comments above show that "anonymous field" is something of a misnomer. The fields `Circle` and `Point` do have names (that of the named type), but those names are optional in dot expressions. We may omit any or all of the anonymous fields when selecting their subfields.  However, there's no shorthand for this form of struct literal syntax, so neither of these will compile:

```go
w = Wheel{8, 8, 5, 20}                       // compile error: unknown fields
w = Wheel{X: 8, Y: 8, Radius: 5, Spokes: 20} // compile error: unknown fields
```

The struct literal must follow the shape of the type declaration, so we must use one of the two forms below, which are equivalent to each other:

<small>[gopl.io/ch4/embed/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/embed/main.go)</small>

```go
w = Wheel{Circle{Point{8, 8}, 5}, 20}

w = Wheel{
	Circle: Circle{
		Point:  Point{X: 8, Y: 8},
		Radius: 5,
	},
	Spokes: 20, // NOTE: trailing comma necessary here (and at Radius)
              // if the enclosing brace is in the next line
}

fmt.Printf("%#v\n", w)
// Output:
// Wheel{Circle:Circle{Point:Point{X:8, Y:8}, Radius:5}, Spokes:20}

w.X = 42

fmt.Printf("%#v\n", w)
// Output:
// Wheel{Circle:Circle{Point:Point{X:42, Y:8}, Radius:5}, Spokes:20}
```

Notice how the `#` adverb causes `Printf`'s `%v` verb to display values in a form similar to Go syntax, which includes the name of each field.

Because "anonymous" fields have implicit names, we can't have two anonymous fields of the same type since their names would conflict.

The visibility of the field is analogous to the name of the field, which is implicitly determined by its type, In the examples above, the `Point` and `Circle` anonymous fields are exported. If they are unexported (`point` and `circle`), we could still use the shorthand form

```go
w.X = 8 // equivalent to w.circle.point.X = 8
```

But the explicit long form shown in the comment would be forbidden outside the declaring package because `circle` and `point` would be inaccessible.

Anonymous fields need not be struct types (discussed later): any named type or pointer to a named type will do. The reason of embedding a type that has no subfields has to do with methods. The shorthand notation used for selecting the fields of an embedded type also works for selecting its methods. In effect, the outer struct type gains not only the fields of the embedded type but also its methods. This mechanism is the main way that complex object behaviors are composed from simpler ones. Composition is central to object-oriented programming in Go, detailed in [Section 6.3](ch6.md#composing-types-by-struct-embedding).

### JSON

[JavaScript Object Notation](https://en.wikipedia.org/wiki/JSON) (JSON) is a standard notation for sending and receiving structured information. Other notations include:

* XML
* [ASN.1](https://en.wikipedia.org/wiki/Abstract_Syntax_Notation_One)
* Google's [Protocol Buffers](https://en.wikipedia.org/wiki/Protocol_Buffers)

JSON is the most widely used because of its simplicity, readability, and universal support.

Go supports encoding and decoding these formats, provided by the standard library packages [`encoding/json`](https://golang.org/pkg/encoding/json/) (discussed in this section), [`encoding/xml`](https://golang.org/pkg/encoding/xml/) and [`encoding/asn1`](https://golang.org/pkg/encoding/asn1/). These packages all have similar APIs. See also [JSON and Go](http://blog.golang.org/json-and-go) for reference.

JSON is an encoding of JavaScript values (strings, numbers, booleans, arrays, and objects) as Unicode text, which is an efficient, readable representation for the basic data types of [Chapter 3](ch3.md) and the composite types of this chapter (arrays, slices, structs, and maps).

The basic JSON types are:

* Numbers (in decimal or scientific notation)
* Booleans (`true` or `false`)
* Strings, which are sequences of Unicode code points enclosed in double quotes, with backslash escapes using a similar notation to Go, though JSON's `\U`*hhhh* numeric escapes denote [UTF-16](https://en.wikipedia.org/wiki/UTF-16) codes, not runes.

These basic types may be combined recursively using JSON arrays and objects:

* A JSON array is an ordered sequence of values, written as a comma-separated list enclosed in square brackets
    * JSON arrays are used to encode Go arrays and slices.
* A JSON object is a mapping from strings to values, written as a sequence of `name:value` pairs separated by commas and surrounded by braces
    * JSON objects are used to encode Go maps (with string keys) and structs.

```text
boolean     true
number      -273.15
string      "She said \"Hello, BF\""
array       ["gold", "silver", "bronze"]
object      {"year": 1980,
             "event": "archery",
             "medals": ["gold", "silver", "bronze"]}
```

#### Marshaling data structures to JSON *

The following example declares a `Movie` data type and a typical list of values. The string literals after the `Year` and `Color` field declarations are `field tags`, which will be explained later.

```go
type Movie struct {
	Title  string
	Year   int  `json:"released"`
	Color  bool `json:"color,omitempty"`
	Actors []string
}

var movies = []Movie{
	{Title: "Casablanca", Year: 1942, Color: false,
		Actors: []string{"Humphrey Bogart", "Ingrid Bergman"}},
	{Title: "Cool Hand Luke", Year: 1967, Color: true,
		Actors: []string{"Paul Newman"}},
	{Title: "Bullitt", Year: 1968, Color: true,
		Actors: []string{"Steve McQueen", "Jacqueline Bisset"}},
	// ...
}
```

It's easy to convert such data structures to and from JSON. Converting a Go data structure to JSON is called [*marshaling*](https://en.wikipedia.org/wiki/Marshalling_(computer_science)), which is done by [`json.Marshal`](https://golang.org/pkg/encoding/json/#Marshal):

```go
data, err := json.Marshal(movies)
if err != nil {
	log.Fatalf("JSON marshaling failed: %s", err)
}
fmt.Printf("%s\n", data)
```

`Marshal` produces a byte slice containing a long string with no extraneous white space:

```text
[{"Title":"Casablanca","released":1942,"Actors":["Humphrey Bogart","Ingrid Bergman"]},{"Title":"Cool Hand Luke","released":1967,"color":true,"Actors":["Paul Newman"]},{"Title":"Bullitt","released":1968,"color":true,"Actors":["Steve McQueen","Jacqueline Bisset"]}]
```

To make it human-readable, a variant called [`json.MarshalIndent`](https://golang.org/pkg/encoding/json/#MarshalIndent) can be used to produces neatly indented output. Two additional arguments are:

* A prefix for each line of output.
* A string for each level of indentation.

```go
data, err := json.MarshalIndent(movies, "", "    ")
if err != nil {
	log.Fatalf("JSON marshaling failed: %s", err)
}
fmt.Printf("%s\n", data)
```

(output skipped) [p109]

Marshaling uses the Go struct field names as the field names for the JSON objects (through [*reflection*](http://blog.golang.org/laws-of-reflection), discussed in Section 12.6). <u>Only exported fields are marshaled, which is why we chose capitalized names for all the Go field names.</u>

Note that in the output, the name of the `Year` field changed to `released` and `Color` changed to `color`, because of the field tags. A field tag is a string of metadata associated at compile time with the field of a struct:

```go
Year int `json:"released"`
Color bool `json:"color,omitempty"`
```

A field tag may be any literal string, but it is conventionally interpreted as a space-separated list of `key:"value"` pairs. Since they contain double quotation marks, field tags are usually written with [raw string literals](ch3.md#raw-string-literal).

* The `json` key controls the behavior of the `encoding/json`
package, and other `encoding/...` packages follow this convention.
* The first part of the `json` field tag specifies an alternative JSON name for the Go field.
    * Field tags are often used to specify an idiomatic JSON name like `total_count` for a Go field named `TotalCount`.
* `omitempty` (which is an additional option in the tag for `Color`) indicates that no JSON output should be produced if the field has the zero value for its type (`false`, here); otherwise, it is the empty value.

#### Unmarshaling and decoding from JSON *

The inverse operation to marshaling is called `unmarshaling`. This is done by [`json.Unmarshal`](https://golang.org/pkg/encoding/json/#Unmarshal), which decodes JSON and populates a Go data structure. By defining suitable Go data structures, we can select which parts of the JSON input to decode and which to discard. The code below unmarshals the JSON movie data into a slice of structs whose only field is `Title`. When `Unmarshal` returns, it has filled in the slice with the `Title` information; other names in the JSON are ignored.

```go
var titles []struct{ Title string }
if err := json.Unmarshal(data, &titles); err != nil {
	log.Fatalf("JSON unmarshaling failed: %s", err)
}
fmt.Println(titles) // "[{Casablanca} {Cool Hand Luke} {Bullitt}]"
```

The following example queries the GitHub issue tracker using its [web-service interface](https://api.github.com/search/issues) (see also [https://developer.github.com/v3/](https://developer.github.com/v3/)). First, it defines the necessary types and constants:

<small>[gopl.io/ch4/github/github.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/github/github.go)</small>

```go
// Package github provides a Go API for the GitHub issue tracker.
// See https://developer.github.com/v3/search/#search-issues.
package github

import "time"

const IssuesURL = "https://api.github.com/search/issues"

type IssuesSearchResult struct {
	TotalCount int `json:"total_count"`
	Items      []*Issue
}

type Issue struct {
	Number    int
	HTMLURL   string `json:"html_url"`
	Title     string
	State     string
	User      *User
	CreatedAt time.Time `json:"created_at"`
	Body      string    // in Markdown format
}

type User struct {
	Login   string
	HTMLURL string `json:"html_url"`
}
```

* The names of all the struct fields must be capitalized even if their JSON names are not.
* The matching process that associates JSON names with Go struct names during unmarshaling is case-insensitive, so it's only necessary to use a field tag when there's an underscore in the JSON name but not in the Go name.
* In this example, we are being selective about which fields to decode. The GitHub search response contains considerably more information than shown here.

The `SearchIssues` function makes an HTTP request and decodes the result as JSON. Since the query terms presented by a user could contain characters like `?` and `&` that have special meaning in a URL, we use `url.QueryEscape` to ensure that they are taken literally.

<small>[gopl.io/ch4/github/search.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/github/search.go)</small>

```go
package github

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
)

// SearchIssues queries the GitHub issue tracker.
func SearchIssues(terms []string) (*IssuesSearchResult, error) {
	q := url.QueryEscape(strings.Join(terms, " "))
	resp, err := http.Get(IssuesURL + "?q=" + q)
	if err != nil {
		return nil, err
	}

	// We must close resp.Body on all execution paths.
	// (Chapter 5 presents 'defer', which makes this simpler.)
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		return nil, fmt.Errorf("search query failed: %s", resp.Status)
	}

	var result IssuesSearchResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		resp.Body.Close()
		return nil, err
	}
	resp.Body.Close()
	return &result, nil
}
```

The earlier examples used `json.Unmarshal` to decode the entire contents of a byte slice as a single JSON entity. For variety, this example uses the *streaming* decoder, [`json.Decoder`](https://golang.org/pkg/encoding/json/#Decoder), which allows several JSON entities to be decoded in sequence from the same stream, although we don't need that feature here. There is a corresponding streaming encoder called [`json.Encoder`](https://golang.org/pkg/encoding/json/#Encoder). The call to `Decode` populates the variable `result`. [p111]

<small>[gopl.io/ch4/issues/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/issues/main.go)</small>

```go
// Issues prints a table of GitHub issues matching the search terms.
package main

import (
	"fmt"
	"log"
	"os"

	"gopl.io/ch4/github"
)

func main() {
	result, err := github.SearchIssues(os.Args[1:])
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%d issues:\n", result.TotalCount)
	for _, item := range result.Items {
		fmt.Printf("#%-5d %9.9s %.55s\n",
			item.Number, item.User.Login, item.Title)
	}
}
```

The command-line arguments specify the search terms. The command below queries the Go project's issue tracker for the list of open bugs related to JSON decoding:

```text
$ go build gopl.io/ch4/issues
$ ./issues repo:golang/go is:open json decoder
13 issues:
#5680    eaigner encoding/json: set key converter on en/decoder
#6050  gopherbot encoding/json: provide tokenizer
#8658  gopherbot encoding/json: use bufio
...
```

### Text and HTML Templates

The formatting for the previous example can be done with the [`text/template`](https://golang.org/pkg/text/template/) and [`html/template`](https://golang.org/pkg/html/template/) packages, which provide a mechanism for substituting the values of variables into a text or HTML template.

A template is a string or file containing one or more portions enclosed in double braces, `{{...}}`, called *actions*. While most of the string is printed literally, the actions trigger other behaviors. Each action contains an expression in the template language, a notation for doing the following:

* Printing values
* Selecting struct fields
* Calling functions and methods
* Expressing control flow, such as `if`-`else` statements and `range` loops
* Instantiating other templates

A simple template string is shown below:

<small>[gopl.io/ch4/issuesreport/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/issuesreport/main.go)</small>

```go
const templ = `{{.TotalCount}} issues:
{{range .Items}}----------------------------------------
Number: {{.Number}}
User:   {{.User.Login}}
Title:  {{.Title | printf "%.64s"}}
Age:    {{.CreatedAt | daysAgo}} days
{{end}}`
```

Within an action, there is a notion of the current value, referred to as "dot" and written as "`.`", a period.

* The dot initially refers to the template's parameter, which is `github.IssuesSearchResult` in this example.
* The `{{.TotalCount}}` action expands to the value of the `TotalCount` field.
* The `{{range .Items}}` and `{{end}}` actions create a loop, so the text between them is expanded multiple times, with dot bound to successive elements of Items.

Within an action, the `|` notation makes the result of one operation the argument of another, analogous to a Unix shell pipeline.

* For `Title`, the second operation is the `printf` function, which is a built-in synonym for `fmt.Sprintf` in all templates.
* For `Age`, the second operation is the following function, `daysAgo`, which converts the `CreatedAt` field into an elapsed time, using [`time.Since`](https://golang.org/pkg/time/#Since):

```go
func daysAgo(t time.Time) int {
	return int(time.Since(t).Hours() / 24)
}
```

Note that the type of `CreatedAt` is `time.Time`, not `string`. In the same way that a type may control its string formatting ([Section 2.5](ch2.md#type-declarations)) by defining certain methods, a type may also define methods to control its JSON marshaling and unmarshaling behavior. The JSON-marshaled value of a `time.Time` is a string in a standard format.

#### Producing output with a template *

Producing output with a template is a two-step process:

1. Parse the template into a suitable internal representation (parsing need be done only once).
2. Execute it on specific inputs.

The code below creates and parses the template `templ` defined above.

```go
report, err := template.New("report").
	Funcs(template.FuncMap{"daysAgo": daysAgo}).
	Parse(templ)
if err != nil {
	log.Fatal(err)
}
```

Note the chaining of method calls:

1. `template.New` creates and returns a template.
2. `Funcs` adds `daysAgo` to the set of functions ([`FuncMap`](https://golang.org/pkg/text/template/#FuncMap)) accessible within this template, then returns that template.
3. `Parse` is called on the result.

Because templates are usually fixed at compile time, failure to parse a template indicates a fatal bug in the program. The [`template.Must`](https://golang.org/pkg/text/template/#Must) helper function makes error handling more convenient: it accepts a template and an error, checks that the error is nil (and panics otherwise), and then returns the template. This idea will be discussed in [Section 5.9](ch5.md#panic).

In the code below, the template is created, augmented with `daysAgo`, parsed, and checked (using `template.Must`), and then executed it using a `github.IssuesSearchResult` as the data source and `os.Stdout` as the destination:

```go
var report = template.Must(template.New("issuelist").
	Funcs(template.FuncMap{"daysAgo": daysAgo}).
	Parse(templ))

func main() {
	result, err := github.SearchIssues(os.Args[1:])
	if err != nil {
		log.Fatal(err)
	}
	if err := report.Execute(os.Stdout, result); err != nil {
		log.Fatal(err)
	}
}
```

The program prints a plain text report like this:

```text
$ go build gopl.io/ch4/issuesreport
$ ./issuesreport repo:golang/go is:open json decoder
13 issues:
----------------------------------------
Number: 5680
User:   eaigner
Title:  encoding/json: set key converter on en/decoder
Age:    750 days
----------------------------------------
Number: 6050
User:   gopherbot
Title:  encoding/json: provide tokenizer
Age:    695 days
----------------------------------------
...
```

#### The `html/template` package *

The `html/template` package uses the same API and expression language as `text/template` but adds features for automatic and context-appropriate escaping of strings appearing within HTML, JavaScript, CSS, or URLs. These features can help avoid a perennial security problem of HTML generation, an [injection attack](https://en.wikipedia.org/wiki/Code_injection).

The template below prints the list of issues as an HTML table:

<small>[gopl.io/ch4/issueshtml/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/issueshtml/main.go)</small>

The command below executes the new template on the results of a slightly different query:

```shell-session
$ go build gopl.io/ch4/issueshtml
$ ./issueshtml repo:golang/go commenter:gopherbot json encoder >issues.html
```

If there are issues whose titles contain HTML metacharacters like `&` and `<`, they are automatically HTML-escaped the titles so that they appear literally. If the `text/template` package is used by mistake, the four-character string `"&lt;"` would have been rendered as a less-than character `'<'`, and the string `"<link>"` would have become a link element, changing the structure of the HTML document and perhaps compromising its security.

To suppress this auto-escaping behavior for fields that contain trusted HTML data, use the named string type `template.HTML` instead of `string`. Similar named types exist for trusted JavaScript, CSS, and URLs. The program below demonstrates the principle by using two fields with the same value but different types: `A` is a `string` and `B` is a `template.HTML`.

<small>[gopl.io/ch4/autoescape/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch4/autoescape/main.go)</small>

```go
func main() {
	const templ = `<p>A: {{.A}}</p><p>B: {{.B}}</p>`
	t := template.Must(template.New("escape").Parse(templ))
	var data struct {
		A string        // untrusted plain text
		B template.HTML // trusted HTML
	}
	data.A = "<b>Hello!</b>"
	data.B = "<b>Hello!</b>"
	if err := t.Execute(os.Stdout, data); err != nil {
		log.Fatal(err)
	}
}
```

[p117]

This section shows only the most basic features of the template system. For more information, consult the package documentation:

```shell-session
$ go doc text/template
$ go doc html/template
```

### Doubts and Solution

#### Verbatim

##### **p100 on structs**

```go
...
EmployeeByID(id).Salary = 0
```

> If the result type of `EmployeeByID` were changed to `Employee` instead of `*Employee`, the assignment statement would not compile since its left-hand side would not identify a variable.

<span class="text-danger">Question</span>: Why is that?

##### **p107 on JSON**

> JSON's `\U`*hhhh* numeric escapes denote [UTF-16](https://en.wikipedia.org/wiki/UTF-16) codes, not runes.

<span class="text-danger">Question</span>: I didn't find any online references for this.

##### **p114 on text templates**

> In the same way that a type may control its string formatting ([Section 2.5](ch2.md#type-declarations)) by defining certain methods, a type may also define methods to control its JSON marshaling and unmarshaling behavior. The JSON-marshaled value of a `time.Time` is a string in a standard format.

<span class="text-danger">Question</span>: How to define methods to control its JSON marshaling and unmarshaling behavior?
