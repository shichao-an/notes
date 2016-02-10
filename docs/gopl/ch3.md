### **Chapter 3. Basic Data Types**

Computers operate fundamentally on fixed-size numbers called **words**, which are interpreted as integers, floating-point numbers, bit sets, or memory addresses, then combined into larger aggregates.

Go’s types fall into four categories:

* Basic types: numbers, strings, and booleans.
* Aggregate types: arrays and structs.
* Reference types: pointers, slices, maps, functions, and channels .
* Interface types

Basic types (discussed in this chapter) include numbers, strings, and booleans.

### Integers

Go provides both signed and unsigned integer arithmetic. There are four distinct sizes of
signed integers: 8, 16, 32, and 64 bits. They represented by:

* Signed: `int8`, `int16`, `int32`, and `int64`;
* Unsigned: `uint8`, `uint16`, `uint32`, and `uint64`.

There are also two types `int` and `uint` that are the natural or most efficient size for signed and unsigned integers on a particular platform: `int` is by far the most widely used numeric type. Both these types have the same size, either 32 or 64 bits, but one must not make assumptions about which; different compilers may make different choices even on identical hardware.

* The type `rune` is an synonym for `int32` and conventionally indicates that a value is a Unicode
code point. The two names may be used interchangeably.
* The type `byte` is an synonym for `uint8`, and emphasizes that the value is a piece of raw data rather than a small numeric quantity.
* `uintptr` is an unsigned integer type, whose width is not specified but is sufficient to hold all the bits of a pointer value. The `uintptr` type is used only for low-level programming, such as at the boundary of a Go program with a C library or an operating system (discussed with the `unsafe` package in [Chapter 13](ch13.md)).

Regardless of their size, `int`, `uint`, and `uintptr` are different types from their explicitly sized siblings. Thus `int` is not the same type as `int32`, even if the natural size of integers is 32 bits, and an explicit conversion is required to use an `int` value where an `int32` is needed, and vice versa.

#### Signedness *

Signed numbers are represented in [2’s-complement](https://en.wikipedia.org/wiki/Two%27s_complement) form, in which the high-order bit is reserved for the sign of the number and the range of values of an n-bit number is from −2<sup>*n*−1</sup> to 2<sup>*n*−1</sup>−1. Unsigned integers use the full range of bits for non-negative values and thus have the range 0 to 2<sup>*n*−1</sup>. For instance, the range of `int8` is −128 to 127, whereas the range of `uint8` is 0 to 255.

#### Binary operators *

Go’s binary operators for arithmetic, logic, and comparison are listed here in order of decreasing precedence:

```text
* / % << >> & &^
+ - | ^
== != < <= > >=
&&
||
```

There are only five levels of precedence for binary operators. Operators at the same level associate to the left; parentheses may be required for clarity, or to make the operators evaluate in the intended order in an expression like `mask & (1 << 28)`.

Each operator in the first two lines of the table above, has a corresponding assignment operator. For instance, `+` has `+=` that may be used to abbreviate an assignment statement.

##### **Arithmetic operators** *

The integer [arithmetic operators](https://golang.org/ref/spec#Arithmetic_operators) `+`, `-`, `*`, and `/` may be applied to integer, floating-point, and complex numbers, but the remainder operator `%` applies only to integers.

* The behavior of `%` for negative numbers varies across programming languages. In Go, the sign of the remainder is always the same as the sign of the [dividend](https://en.wikipedia.org/wiki/Division_(mathematics)), so `-5%3` and `-5%-3` are both `-2`.
* The behavior of `/` depends on whether its operands are integers, so `5.0/4.0` is `1.25`, but `5/4` is `1` because integer division truncates the result toward zero.

##### **Integer overflow** *

If the result of an arithmetic operation, whether signed or unsigned, has more bits than can be represented in the result type, it is said to *overflow*. The high-order bits that do not fit are silently discarded. If the original number is a signed type, the result could be negative if the leftmost bit is a 1, as in the `int8` example here:

```go
var u uint8 = 255
fmt.Println(u, u+1, u*u) // "255 0 1"

var i int8 = 127
fmt.Println(i, i+1, i*i) // "127 -128 1"
```

##### **Comparison and comparability** *

Binary comparison operators are:

* `==`: equal to
* `!=`: not equal to
* `<`: less than
* `<=`: less than or equal to
* `>`: greater than
* `>=`: greater than or equal to

The type of a comparison expression is a boolean.

* All values of basic type (booleans, numbers, and strings) are *comparable*. This means two values of the same type may be compared using the `==` and `!=` operators.
* Integers, floating-point numbers, and strings are *ordered* by the comparison operators.
* The values of many other types are not comparable, and no other types are ordered.

There are also unary addition and subtraction operators:

* `+`: unary positive (no effect)
* `-`: unary negation

For integers, `+x` is a shorthand for `0+x` and `-x` is a shorthand for `0-x`; for floating-point and complex numbers, `+x` is just `x` and `-x` is the negation of `x`.
