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

##### **Unary operators** *

There are also unary addition and subtraction operators:

* `+`: unary positive (no effect)
* `-`: unary negation

For integers, `+x` is a shorthand for `0+x` and `-x` is a shorthand for `0-x`; for floating-point and complex numbers, `+x` is just `x` and `-x` is the negation of `x`.

##### **Bitwise binary operators** *

The following are bitwise binary operators. The first four of them treat their operands as bit patterns with no concept of arithmetic carry or sign:

* `&`: bitwise AND
* `|`: bitwise OR
* `^`: bitwise XOR
* `&^`: bit clear (AND NOT)
* `<<`: left shift
* `>>`: right shift

The operator `^` has two usages:

* When used as a binary operator, it is bitwise exclusive OR (XOR)
* When used as a unary prefix operator, it is bitwise negation or complement, which means it returns a value with each bit in its operand inverted.

The `&^` operator is bit clear (AND NOT): in the expression `z = x &^ y`, each bit of `z` is 0 if the corresponding bit of `y` is 1; otherwise it equals the corresponding bit of `x`.

##### **Bitwise operation examples** *

The code below shows how bitwise operations can be used to interpret a `uint8` value as a compact and efficient set of 8 independent bits. It uses `Printf`'s `%b` verb to print a number’s binary digits; `08` modifies `%b` to pad the result with zeros to exactly 8 digits.


```go
var x uint8 = 1<<1 | 1<<5
var y uint8 = 1<<1 | 1<<2

fmt.Printf("%08b\n", x)    // "00100010", the set {1, 5}
fmt.Printf("%08b\n", y)    // "00000110", the set {1, 2}

fmt.Printf("%08b\n", x&y)  // "00000010", the intersection {1}
fmt.Printf("%08b\n", x|y)  // "00100110", the union {1, 2, 5}
fmt.Printf("%08b\n", x^y)  // "00100100", the symmetric difference {2, 5}
fmt.Printf("%08b\n", x&^y) // "00100000", the difference {5}

for i := uint(0); i < 8; i++ {
	if x&(1<<i) != 0 { // membership test
		fmt.Println(i) // "1", "5"
	}
}

fmt.Printf("%08b\n", x<<1) // "01000100", the set {2, 6}
fmt.Printf("%08b\n", x>>1) // "00010001", the set {0, 4}
```

[Section 6.5](ch6.md#example-bit-vector-type) shows an implementation of integer sets that can be much bigger than a byte.

In the shift operations `x<<n` and `x>>n`:

* The `n` operand determines the number of bit positions to shift and must be unsigned.
* The `x` operand may be unsigned or signed.

Arithmetically:

* A left shift `x<<n` is equivalent to multiplication by 2<sup>n</sup>.
* A right shift `x>>n` is equivalent to the floor of division by 2<sup>n</sup>.

For unsigned numbers, both left and right shifts fill the vacated bits with zeros. However, <u>right shifts of signed numbers fill the vacated bits with copies of the sign bit.</u> For this reason, it is important to use unsigned arithmetic when you’re treating an integer as a bit pattern.

##### **Usages of unsigned numbers**

Although Go provides unsigned numbers and arithmetic, we tend to use the signed `int` form even for quantities that can’t be negative, such as the length of an array (though `uint` might seem a more obvious choice). The built-in `len` function returns a signed `int`. Consider the following example:

```go
medals := []string{"gold", "silver", "bronze"}
	for i := len(medals) - 1; i >= 0; i-- {
		fmt.Println(medals[i]) // "bronze", "silver", "gold"
}
```

If `len` returned an unsigned number, then `i` would be a `uint`, and the condition `i >= 0` would always be true by definition. After the third iteration, in which `i == 0`, the `i--` statement would cause `i` to become not `−1`, but the maximum `uint` value (for example, 2<sup>64</sup>−1), and the evaluation of `medals[i]` would fail at run time, or panic ([Section 5.9](ch5.md#panic)), by attempting to access an element outside the bounds of the slice.

For this reason, unsigned numbers tend to be used only when their bitwise operators or peculiar arithmetic operators are required, such as

* Implementing bit sets
* Parsing binary file formats
* For hashing and cryptography.

They are typically not used for merely non-negative quantities.

Binary operators for arithmetic and logic (except shifts) must have operands of the same type. In cases where operands have different types, an explicit conversion is required. This eliminates a whole class of problems and makes programs easier to understand.

Consider this sequence:

```go
var apples int32 = 1
var oranges int16 = 2
var compote int = apples + oranges // compile error
```

Attempting to compile these three declarations produces an error message:

```text
invalid operation: apples + oranges (mismatched types int32 and int16)
```

This type mismatch can be fixed in several ways, most directly by converting everything to a common type:

```go
var compote = int(apples) + int(oranges)
```

As described in [Section 2.5](ch2.md#type-declarations), for every type `T`, the conversion operation `T(x)` converts the value `x` to type `T` if the conversion is allowed. Many integer-to-integer conversions do not entail any change in value, but only tell the compiler how to interpret a value. However, some conversions may change the value or lose precision:

* A conversion that narrows a big integer into a smaller one.
* A conversion from integer to floating-point or vice versa.

```go
f := 3.141 // a float64
i := int(f)
fmt.Println(f, i)
// "3.141 3"
f = 1.99
fmt.Println(int(f)) // "1"
```

Float to integer conversion discards any fractional part, truncating toward zero. You should avoid conversions in which the operand is out of range for the target type, because the behavior depends on the implementation:

```go
f := 1e100  // a float64
i := int(f) // result is implementation-dependent
```

Integer literals of any size and type can be written as one of the following:

* Ordinary decimal numbers,
* Octal numbers, if they begin with 0, e.g. 0666
* Hexadecimal, if they begin with 0x or 0X, e.g. 0xdeadbeef. Hex digits may be upper or lower case.

Nowadays octal numbers seem to be used for exactly one purpose: file permissions on POSIX systems. Hexadecimal numbers are widely used to emphasize the bit pattern of a number over its numeric value.  When printing numbers using the `fmt` package, we can control the [radix](https://en.wikipedia.org/wiki/Radix) and format with the `%d`, `%o`, and `%x` verbs, as shown in this example:

```go
o := 0666
fmt.Printf("%d %[1]o %#[1]o\n", o) // "438 666 0666"
x := int64(0xdeadbeef)
fmt.Printf("%d %[1]x %#[1]x %#[1]X\n", x)
// Output:
// 3735928559 deadbeef 0xdeadbeef 0XDEADBEEF
```

The above example describes two `fmt` tricks.

1. Usually a `Printf` format string containing multiple `%` verbs would require the same number of extra operands, but the `[1]` "adverbs" after `%` tell `Printf` to use the first operand.
2. The `#` adverb for `%o` or `%x` or `%X` tells `Printf` to emit a `0` or `0x` or `0X` prefix respectively.

Rune literals are written as a character within single quotes. The simplest example is an ASCII character like `'a'`, but it’s possible to write any Unicode code point either directly or with numeric escapes. This will be discussed in later sections.

Runes are printed with `%c`, or with `%q` if quoting is desired:

```go
ascii := 'a'
unicode := 'D'
newline := '\n'
fmt.Printf("%d %[1]c %[1]q\n", ascii)   // "97 a 'a'"
fmt.Printf("%d %[1]c %[1]q\n", unicode) // "22269 D 'D'"
fmt.Printf("%d %[1]q\n", newline)       // "10 '\n'"
```

### Floating-Point Numbers

There are two sizes of floating-point numbers, whose properties are governed by the [IEEE 754 standard](https://en.wikipedia.org/wiki/IEEE_floating_point) (implemented by all modern CPUs). The limits of floating-point values can be found in the `math` package.

* `float32`
    * The largest `float32` is the constant `math.MaxFloat32`, which is about `3.4e38`.
    * The smallest positive value is `1.4e-45`.
* `float64`
    * The largest `float64` is the constant `math.MaxFloat64`, which is about `1.8e308`.
    * The smallest positive value is `4.9e-324`.

A `float32` provides approximately six decimal digits of precision, whereas a `float64` provides about 15 digits. <u>`float64` should be preferred for most purposes because `float32` computations accumulate error rapidly if not careful</u>; the smallest positive integer that cannot be exactly represented as a `float32` is not large:

Floating-point numbers can be written literally using decimals. For example:

```go
const e = 2.71828 // (approximately)
```

Digits may be omitted before the decimal point (e.g. `.707`) or after it (e.g. `1.`). Very small or very large numbers are better written in scientific notation, with the letter `e` or `E` preceding the decimal exponent:

```go
const Avogadro = 6.02214129e23
const Planck = 6.62606957e-34
```

Floating-point values can be printed with `Printf`'s following verbs:

* `%g`: it chooses the most compact representation that has adequate precision, i.e. `%e` for large exponents, `%f` otherwise
* `%e` (exponent): decimal point with exponent (scientific notation)
* `%f`: decimal point but no exponent

All three verbs allow field width and numeric precision to be controlled.

```go
for x := 0; x < 8; x++ {
	fmt.Printf("x = %d e**x = %8.3f\n", x, math.Exp(float64(x)))
}
```

The code above prints the powers of *e* with three decimal digits of precision, aligned in an eight-character field:

```text
x = 0 e**x =    1.000
x = 1 e**x =    2.718
x = 2 e**x =    7.389
x = 3 e**x =   20.086
x = 4 e**x =   54.598
x = 5 e**x =  148.413
x = 6 e**x =  403.429
x = 7 e**x = 1096.633
```


### Doubts and Solution

#### Verbatim

##### **p53 on bitwise binary operator `&^`**

> The `&^` operator is bit clear (AND NOT): in the expression `z = x &^ y`, each bit of `z` is 0 if the corresponding bit of `y` is 1; otherwise it equals the corresponding bit of `x`.

<span class="text-danger">Question</span>: What does it mean?

<span class="text-info">Solution</span>:

* [Stack Overflow](http://stackoverflow.com/questions/28432398/difference-between-some-operators-golang): `x &^ y` means to get the bits that are in `x` AND NOT in `y`. See also [bitwise operation examples](#bitwise-operation-examples).
