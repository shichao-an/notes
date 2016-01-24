### **Part 1: Language**

* [C99](https://en.wikipedia.org/wiki/C99) is discussed.
* The examples are based on 32-bit GCC.

### Data Types

#### Integers

The following are basic integer keywords:

* `char`: signed 8-bit integer.
* `short`: signed 16-bit integer.
* `int`: signed 32-bit integer.
* `long`: 32-bit integer on the 32-bit system (`long int`), and 64-bit integer on the 64-bit system.
* `long long`: signed 64-bit intger (`long long int`).
* `bool`: `_Bool` type, 8-bit integer. The macros `bool`, `true` and `false` are defined in `stdbool.h`.

Since on different systems `char` may represent a signed or unsigned 8-bit integer, it's recommended to use `unsigned char` or `signed char` to represent an exact type.

In `stdint.h`, more specific integer types are defined:

<small>[stdint.h](https://github.com/shichao-an/glibc-2.21/blob/master/sysdeps/generic/stdint.h)</small>

```c
typedef signed char                int8_t;
typedef short int                  int16_t;
typedef int                        int32_t;

typedef unsigned char              uint8_t;
typedef unsigned short int         uint16_t;
typedef unsigned int               uint32_t;

#if __WORDSIZE == 64
    typedef long int               int64_t;
    typedef unsigned long int      uint64_t;
#else
    __extension__
    typedef long long int          int64_t;
    typedef unsigned long long int uint64_t;
#endif
```

There are also size limits of these integer types:

```c
# define INT8_MIN (-128)
# define INT16_MIN (-32767-1)
# define INT32_MIN (-2147483647-1)
# define INT64_MIN (-__INT64_C(9223372036854775807)-1)

# define INT8_MAX (127)
# define INT16_MAX (32767)
# define INT32_MAX (2147483647)
# define INT64_MAX (__INT64_C(9223372036854775807))

# define UINT8_MAX (255)
# define UINT16_MAX (65535)
# define UINT32_MAX (4294967295U)
# define UINT64_MAX (__UINT64_C(18446744073709551615))
```

##### **Character Constants** *

A [character constant](http://en.cppreference.com/w/c/language/character_constant) by default is an integer of type `int`. However, the compiler determines whether to interpret it into `char` or `int`.

The following code:

```c
char c = 'a';
printf("%c, size(char)=%d, size('a')=%d;\n", c, sizeof(c), sizeof('a'));
```

will output:

```text
a, size(char)=1, size('a')=4;
```

##### **The Type of a Pointer** *

A pointer is a special-purpose integer, whose type is also defined in `stdint.h`.

```c
/* Types for `void *' pointers. */
#if __WORDSIZE == 64
    typedef unsigned long int uintptr_t;
#else
    typedef unsigned int uintptr_t;
#endif
```

But in the code we usually use the expression `sizeof(char*)` to save the trouble of differentiating 32-bit and 64-bit.

##### **Representing Integer Constants** *

We can use different suffixes to represent [integer constants](http://en.cppreference.com/w/c/language/integer_constant). The following code:

```c
printf("int size=%d;\n", sizeof(1));
printf("unsigned int size=%d;\n", sizeof(1U));
printf("long size=%d;\n", sizeof(1L));
printf("unsigned long size=%d;\n", sizeof(1UL));
printf("long long size=%d;\n", sizeof(1LL));
printf("unsigned long long size=%d;\n", sizeof(1ULL));
```

will output:

```
int size=4;
unsigned int size=4;
long size=4;
unsigned long size=4;
long long size=8;
unsigned long long size=8;
```

##### **Helper Macros: `__INT64_C` and `__UINT64_C`** *

Some helper macros are defined in `stdint.h`.

```c
# if __WORDSIZE == 64
# define __INT64_C(c) c ## L
# define __UINT64_C(c) c ## UL
# else
# define __INT64_C(c) c ## LL
# define __UINT64_C(c) c ## ULL
# endif
```

Note that the `##` operator in the macro means combining the left and right operands together as a symbol.

#### Floating-Point Numbers

##### **Real floating types** *

C has three types of different precisions for representing [real floating-point](http://en.cppreference.com/w/c/language/arithmetic_types#Real_floating_types) values:

* `float`: 32-bit, 4-byte floating-point number, which has a precision (number of significant decimal digits) of 6 (`FLT_DIG`, defined in `<float.h>`).
* `double`: 64-bit, 8-byte floating-point number, which has a precision of 15 (`DBL_DIG`).
* `long double`: 80-bit, 10-byte floating-point number, which has a precision of 19 (`LDBL_DIG`).

The default floating type is `double`. Suffix `F` represents `float` and `L` represents `long double`.

The following code:

```c
printf("float %f size=%d\n", 1.F, sizeof(1.F));
printf("double %f size=%d\n", .123, sizeof(.123));
printf("long double %Lf size=%d\n", 1.234L, sizeof(1.234L));
```

will output:

```text
float 1.000000 size=4
double 0.123000 size=8
long double 1.234000 size=12
```

##### **Complex floating types** *

C99 supports complex numbers, by using two same-type floating-point number to represent real and imaginary number of the complex number.

To represent complex types, simply append `_Complex` to `float`, `double` and `long double`:

* `float _Complex`
* `double _Complex`
* `long double _Complex`

If `<complex.h>` is included, they are also available as:

* `float complex`
* `double complex`
* `long double complex`

The following code:

```c
#include <complex.h>

printf("float complex size=%d\n", sizeof((float complex)1.0));
printf("double complex size=%d\n", sizeof((double complex)1.0));
printf("long double complex size=%d\n", sizeof((long double complex)1.0));
```

will output:

```text
float complex size=8
double complex size=16
long double complex size=24
```

#### Enumerations

An [enumerated type](http://en.cppreference.com/w/c/language/enum) (`enum`) is a distinct type whose value is restricted to one of several enumeration constants. It is declared with the following syntax:

```c
enum identifier { enumerator-list }
```

* Each enumerator in the body of an enumeration specifier becomes an integer constant with type `int` and can be used whenever integer constants are required.
* If enumerator is followed by `= constant-expression`, its value is the value of that constant expression.
* If enumerator is not followed by` = constant-expression`, its value is the value one greater than the value of the previous enumerator in the same enumeration.
* The value of the first enumerator (if it does not use `= constant-expression`) is zero.

The following code:

```c
enum color { black, red = 5, green, yellow };

enum color b = black;
printf("black = %d\n", b);

enum color r = red;
printf("red = %d\n", r);

enum color g = green;
printf("green = %d\n", g);

enum color y = yellow;
printf("yellow = %d\n", y);
```

will output:

```text
black = 0
red = 5
green = 6
yellow = 7
```

The values of enumerators can be the same:

The following code:

```c
enum color { black = 1, red, green = 1, yellow };
```

will output:

```text
black = 1
red = 2
green = 1
yellow = 2
```

Usually, the identifier can be omitted, so that enumerators can be used to avoid defining constants macros.

```c
enum { BLACK = 1, RED, GREEN = 1, YELLOW };

printf("black = %d\n", BLACK);
printf("red = %d\n", RED);
printf("green = %d\n", GREEN);
printf("yellow = %d\n", YELLOW);
```

### Literals

A [literal](http://en.cppreference.com/w/c/language/expressions#Constants_and_literals) in the source code is a token to represent a specific value, which can be an integer, a floating-point number, a character, or a string.

#### Integer Constants

Besides the common decimal expression, octal (beginning with `0`) and hexadecimal (beginning with `0x` or `0X`) expressions can be used.

The following code:

```c
int x = 010;
int y = 0x0A;
printf("x = %d, y = %d\n", x, y);
```

will output:

```text
x = 8, y = 10
```

Constant types is important. They can be differentiated using suffixes.

```text
0x200    -> int
200U     -> unsigned int
0L       -> long
0xf0f0UL -> unsigned long
0777LL   -> long long
0xFFULL  -> unsigned long long
```

#### Floating Constants

A [floating constant](http://en.cppreference.com/w/c/language/floating_constant) can be represented using decimal and hexadecimal expressions.

The default type of floating constants is `double`. The `F` suffix represents `float`, and the `L` suffix represents `long double`.

#### Character Constants

The default type for character constants is `int`, unless `L` is preposed to represent wide character constant of `wchar_t` type.

The following code:

```c
char c = 0x61;
char c2 = 'a';
char c3 = '\x61';
printf("%c, %c, %c\n", c, c2, c3);
```

will output:

```text
a, a, a
```

In Linux, the default [character encoding](https://en.wikipedia.org/wiki/Character_encoding) is [UTF-8](https://en.wikipedia.org/wiki/UTF-8). Conversion can be done using the [`wctomb`](http://en.cppreference.com/w/c/string/multibyte/wctomb) functions and the like.

`wchar_t` is 4 bytes in size by default, so it can hold any UCS-4 Unicode character.

```c
setlocale(LC_CTYPE, "en_US.UTF-8");

wchar_t wc = L'中';
char buf[100] = {};

int len = wctomb(buf, wc);
printf("%d\n", len);

for (int i = 0; i < len; i++)
{
    printf("0x%02X ", (unsigned char)buf[i]);
}
```

will output:

```text
3
0xE4 0xB8 0xAD
```

#### String Literals

In C, a string is a `char` array ending with `NULL` (`\0`).

An empty string takes up 1 byte in the memory, which includes a `NULL` character. This means, a string that has a length of 1 requires at least 2 bytes (what [`strlen`](http://en.cppreference.com/w/c/string/byte/strlen) and [`sizeof`](http://en.cppreference.com/w/c/language/sizeof) means are different).

```c
char s[] = "Hello, World!";
char* s2 = "Hello, C!";
```

As with character contants, the prefixing `L` declares a wide string literal.

The following code:

```c
setlocale(LC_CTYPE, "en_US.UTF-8");

wchar_t* ws = L"中国⼈";
printf("%ls\n", ws);

char buf[255] = {};
size_t len = wcstombs(buf, ws, 255);

for (int i = 0; i < len; i++)
{
    printf("0x%02X ", (unsigned char)buf[i]);
}
```

will output:

```text
中国⼈
0xE4 0xB8 0xAD 0xE5 0x9B 0xBD 0xE4 0xBA";
```

Similar to a `char` string, a `wchar_t` string ends with a 4-byte `NULL`.

The following code:

```c
wchar_t ws[] = L"中国⼈";
printf("len %d, size %d\n", wcslen(ws), sizeof(ws));

unsigned char* b = (unsigned char*)ws;
int len = sizeof(ws);

for (int i = 0; i < len; i++)
{
 printf("%02X ", b[i]);
}
```

will output:

```text
len 3, size 16
2D 4E 00 00 FD 56 00 00 BA 4E 00 00 00 00 00 00
```

The compiler will automatically concatenate adjacent strings. This is helpful for better dealing with strings in the macros or the code.

```c
#define WORLD "world!"
char* s = "Hello" " " WORLD "\n";
```

For very long strings in the source code, other than concatenating them, `\` in the end of a line can be used.

```c
char* s1 = "Hello"
 " World!";
char* s2 = "Hello \
World!";
```

Note that the spaces to the right of `\` will treated as part of the string.

### Type Conversions

When the operands for an operator has different types, conversion is required. Usually, the compiler performs [implict conversions](http://en.cppreference.com/w/c/language/conversion), on the premise that information is not lost, to convert the "narrow" bit-width operand into the "wide" one.

#### Arithmetic conversions

The compiler's default implicit conversion ranks:

```text
long double > doulbe > float > long long > long > int > char > _Bool
```

The conversion rank of floating-point types is greater than that of any integers. Signed integers have the same conversion rank as their unsigned equivalence.

In expressions, `char` and `short` may be by default converted to `int` (`unsigned int`) operands, but `float` will not be converted to `double` by default.

The following code:

```c
char a = 'a';
char c = 'c';
printf("%d\n", sizeof(c - a));
printf("%d\n", sizeof(1.5F - 1));
```

will output:

```text
4
4
```

<u>When dealing with unsigned operands, beware of checking whether the promoted type is able to hold all values of the unsigned type.</u>

```c
long a = -1L;
unsigned int b = 100;
printf("%ld\n", a > b ? a : b);
```

will output:

```text
-1
```

This output is incomprehensible. Even if `long` has a greater rank than `unsigned int`, they are both 32-bit integers in 32-bit systems, and `long` is unable to hold all values of `unsigned int`. Therefore, the compilter will convert both operands to `unsigned long`, which is the unsigned greater rank. For this reason the result of `(unsigned long)a` turns into a very big integer.

> If the signedness is different and the signed operand's rank is greater than unsigned operand's rank. In this case, if the signed type can represent all values of the unsigned type, then the operand with the unsigned type is implicitly converted to the type of the signed operand. Otherwise, both operands undergo implicit conversion to the unsigned type counterpart of the signed operand's type.
> <small>[Usual arithmetic conversions: 4)](http://en.cppreference.com/w/c/language/conversion#Usual_arithmetic_conversions)</small>

The following code:

```c
long a = -1L;
unsigned int b = 100;
printf("%lu\n", (unsigned long)a);
printf("%ld\n", a > b ? a : b);
```

will output:

```text
4294967295
-1
```

Other implict conversions are:

* In assignment and initialization, the type of the right operator is always converted to that of the left one.
* In a function call, the type of the actual parameter is always converted to that of the formal parameter.
* The type of the `return` expression result is converted to that of the function's return type.
* 0 value of any type and the `NULL` pointer is deemed `_Bool false`; otherwise, it is `true`.

When converting a "wide" type to a "narrow" type, the compiler will try to discard significant bits, to use rounding, or other techniques to return a approximate value.

#### Non-arithmetic conversions

1. The name or expression of an array is usually referred to as a pointer to its first element, unless:
    * It is used as the operand of `sizeof`.
    * The `&` operator is used on it to return a "array pointer".
    * It is a [string constant](#string-literals) are used to initialize a `char` or `wchar_t` array.
2. A pointer can be explicitly converted to a pointer of any other types.

        int x = 123, *p = &x;
        char* c = (char*)x;

3. Any pointer can be implictly converted to a `void` pointer and vice versa.
4. Any pointer can be implictly converted to a pointer of a more specific type (including qualifiers such as `const`, `volatile` and `restrict`).

        int x = 123, *p = &x;
        const int* p2 = p;

5. `NULL` can be converted to a pointer of any type.
6. A pointer can be explicitly converted to an integer and vice versa.

    The following code:

        int x = 123, *p = &x;
        int px = (int)p;

        printf("%p, %x, %d\n", p, px, *(int*)px);

    will output:

        0xbfc1389c, bfc1389c, 123

- - -

### References

* [C reference - cppreference.com](http://en.cppreference.com/w/c)
* [CPP] *C Primer Plus* (6th Edition)
