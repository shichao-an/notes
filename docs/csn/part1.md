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
* `long long`: signed 64-bit integer (`long long int`).
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

When the operands for an operator has different types, conversion is required. Usually, the compiler performs [implicit conversions](http://en.cppreference.com/w/c/language/conversion), on the premise that information is not lost, to convert the "narrow" bit-width operand into the "wide" one.

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

This output is incomprehensible. Even if `long` has a greater rank than `unsigned int`, they are both 32-bit integers in 32-bit systems, and `long` is unable to hold all values of `unsigned int`. Therefore, the compiler will convert both operands to `unsigned long`, which is the unsigned greater rank. For this reason the result of `(unsigned long)a` turns into a very big integer.

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

Other implicit conversions are:

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

3. Any pointer can be implicitly converted to a `void` pointer and vice versa.
4. Any pointer can be implicitly converted to a pointer of a more specific type (including qualifiers such as `const`, `volatile` and `restrict`).

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

### Operators

Other than basic expressions and operator usages, let's document something special.

#### Compound Literals

Since C99, we can use the following syntax to declare a structure or array pointer.

```text
( type ) { initializer-list }
```

For example,

```c
int* i = &(int){ 123 };                              // integer variable, pointer
int* x = (int[]){ 1, 2, 3, 4 };                      // array, pointer
struct data_t* data = &(struct data_t){ .x = 123 };  // structure, pointer
func(123, &(struct data_t){ .x = 123 });             // function argument, structure pointer
```

For static or global variables, the initializer list must be compile-time constants.

#### `sizeof`

`sizeof` returns the memory storage size of the operator in bytes. The return type is `size_t` and the operator can be a type or a variable.

```c
size_t size;
int x = 1;
size = sizeof(int);
size = sizeof(x);
size = sizeof x;
size = sizeof(&x);
size = sizeof &x;
```

Do not use `int` in place of `size_t`, because `size_t` has different sizes on 32-bit and 64-bit platforms.

#### Comma Operator

The [comma operator](http://en.cppreference.com/w/c/language/operator_other#Comma_operator) is a binary operator, which guarantees that the operands are evaluated from left to right and returns the value and type of the right operand.

```c
int i = 1;
long long x = (i++, (long long)i);
printf("%lld\n", x);
```

#### Precedence

The precedence is C is a big trouble. Do not refrain from using "()".

The following table is the precedence list (from high to low):

Kind | Operator | Associativity
---- | -------- | -------------
Postfix operator | `++`, `--`, `[]`, `func()`, `.`, `->`, `(type){init}` | Left-to-right
Unary operator | `++`, `--`, `!`, `~`, `+`, `-`, `*`, `&`, `sizeof` | Right-to-left
Cast operator | `(type name)` | Right-to-left
Multiplication and division operator | `*`, `/`, `%` | Left-to-right
Addition and subtraction operator | `+`, `-` | Left-to-right
Bitwise shift operator | `<<`, `>>` | Left-to-right
Relational operator | `<`, `<=`, `>`, `>=` | Left-to-right
Equation operator | `==`, `!=` | Left-to-right
Bitwise operator | `&` | Left-to-right
Bitwise operator | `^` | Left-to-right
Bitwise operator | <code>&#124;</code> | Left-to-right
Logical operator | `&&` | Left-to-right
Logical operator | <code>&#124;&#124;</code> | Left-to-right
Conditional operator | `?:` | Right-to-left
Assignment operator | `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `^=`, <code>&#124;=</code>, `<<=`, `>>=` | Right-to-left
Comma operator | `,` | Left-to-right

If multiple operators in an expression have the same precedence, then their associativity determines how they are combined (left-to-right or right-to-left). For example, in `a = b = c`, the two `=` have the same precedence. According to its associativity, the expression is decomposed into `a = (b = c)`.

The following are some confusing operator precedence.

1. `.` is higher than `*`.

        Original: *p.f
        Erroneous: (*p).f
        Correct: *(p.f)

2. `[]` is higher than `*`.

        Original: int *ap[]
        Erroneous: int (*ap)[]
        Correct: int *(ap[])

3. `==` and `!=` are higher than bitwise operators.

        Original: val & mask != 0
        Erroneous: (val & mask) != 0
        Correct: val & (mask != 0)

4. `==` and `!=` are higher than assignment operators.

        Original: c = getchar() != EOF
        Erroneous: (c = getchar()) != EOF
        Correct: c = (getchar() != EOF)

5. Arithmetic operators are higher than bitwise shift operators.

        Original: msb << 4 + lsb
        Erroneous: (msb << 4) + lsb
        Correct: msb << (4 + lsb)

6. The comma operator has the lowest precedence.

        Original: i = 1, 2
        Erroneous: i = (1, 2)
        Correct: (i = 1), 2

### Statements

#### Statement Blocks

A block represents a [scope](http://en.cppreference.com/w/c/language/scope); the automatic variables declared inside the block will be released if beyond the scope. Apart from `{...}` which represents a regular block, it can also be used in complex assignments. This is often used in macros.

In the following code:

```c
int i = ({ char a = 'a'; a++; a; });
printf("%d\n", i);
```

The last expression can be treated as the return value of a block. The equivalent macro version of this code is:

```c
#define test() ({ \
 char _a = 'a'; \
 _a++; \
 _a; })
int i = test();
printf("%d\n", i);
```

In macros, the underline prefixes are usually used to avoid name conflicts with the upper block.

#### Loop Statements

C supports `while`, `for` and `do...while` loop statements (or iteration statements).

Note that in the following example, the loop causes the `get_len` function to be executed multiple times.

```c
size_t get_len(const char* s)
{
    printf("%s\n", __func__);
    return strlen(s);
}

int main(int argc, char* argv[])
{
    char *s = "abcde";
    for (int i = 0; i < get_len(s); i++)
    {
        printf("%c\n", s[i]);
    }

    printf("\n");

    return EXIT_SUCCESS;
}
```

#### Selection Statements

Selection statements include `if...else if...else...` and `switch { case ... }`.

GCC supports the `switch` [case range](https://gcc.gnu.org/onlinedocs/gcc/Case-Ranges.html) extension.

```c
int x = 1;
switch (x)
{
    case 0 ... 9: printf("0..9\n"); break;
    case 10 ... 99: printf("10..99\n"); break;
    default: printf("default\n"); break;
}

char c = 'C';
switch (c)
{
     case 'a' ... 'z': printf("a..z\n"); break;
     case 'A' ... 'Z': printf("A..Z\n"); break;
     case '0' ... '9': printf("0..9\n"); break;
     default: printf("default\n"); break;
}
```

#### Jump Statements

The [jump statements](http://en.cppreference.com/w/c/language/statements#Jump_statements) unconditionally transfer flow control.

* `break`
* `continue`
* [`goto`](http://en.cppreference.com/w/c/language/goto)
* `return`

`goto` only causes a jump within the function, which is commonly used to jump out of the nested loops. To jump out of the function, use [`longjmp`](http://en.cppreference.com/w/c/program/longjmp).

[`setjmp`](http://en.cppreference.com/w/c/program/setjmp) saves the current execution context into a variable `env` of type `jmp_buf` and returns 0. When the subsequent code calls `longjmp` to jump, a status code is required. The code execution will return to the call site of `setjmp`, and returns the status code passed to `longjmp`.

The following code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <setjmp.h>

void test(jmp_buf *env)
{
    printf("1....\n");
    longjmp(*env, 10);
}

int main(int argc, char* argv[])
{
    jmp_buf env;
    int ret = setjmp(env); // calling `longjmp` goes to here,
                           // and `ret` is the value passed to `longjmp`
    if (ret == 0)
    {
        test(&env);
    }
    else
    {
        printf("2....(%d)\n", ret);
    }

    return EXIT_SUCCESS;
}
```

will output:

```text
1....
2....(10)
```

### Functions

A function can be defined once, but can be declared and called multiple times.

#### Nested Functions

The GCC supports the [nested functions](https://gcc.gnu.org/onlinedocs/gcc/Nested-Functions.html) extension.

```c
typedef void(*func_t)();

func_t test()
{
    void func1()
    {
        printf("%s\n", __func__);
    };

    return func1;
}

int main(int argc, char* argv[])
{
    test()();
    return EXIT_SUCCESS;
}
```

The inner function can "read and write" the parameters and variables from the outer function; the outer variables have to be defined before the nested function.

The following code:

```c
#define pp() ({ \
    printf("%s: x = %d(%p), y = %d(%p), s = %s(%p);\n", __func__, x, &x, y, &y, s, s); \
})

void test2(int x, char *s)
{
    int y = 88;
    pp();

    void func1()
    {
        y++;
        x++;
        pp();
    }

    func1();

    x++;
    func1();
    pp();
}

int main (int argc, char * argv[])
{
    test2(1234, "abc");
    return EXIT_SUCCESS;
}
```

will output:

```text
test2: x = 1234(0xbffff7d4), y = 88(0xbffff7d8), s = abc(0x4ad3);
func1: x = 1235(0xbffff7d4), y = 89(0xbffff7d8), s = abc(0x4ad3);
func1: x = 1237(0xbffff7d4), y = 90(0xbffff7d8), s = abc(0x4ad3);
test2: x = 1237(0xbffff7d4), y = 90(0xbffff7d8), s = abc(0x4ad3);
```

#### Function Types

Do not confuse "function type" and "function pointer type". The name of a function is a pointer to that function.

```c
typedef void(func_t)();      // function type
typedef void(*func_ptr_t)(); // function pointer type

void test()
{
    printf("%s\n", __func__);
}

int main(int argc, char* argv[])
{
    func_t* func = test;     // delcare a pointer
    func_ptr_t func2 = test; // already a pointer type

    void (*func3)();         // declare a function pointer variable, which
                             // includes a function prototype
    func3 = test;

    func();
    func2();
    func3();

    return EXIT_SUCCESS;
}
```

#### Function Calls

By default, C uses the [cdecl](https://en.wikipedia.org/wiki/X86_calling_conventions#cdecl) calling convention. The arguments are pushed on the stack in the right-to-left order. It is the caller that pushes arguments on the stack and cleans arguments from the stack.

The following code:

```c
int main(int argc, char* argv[])
{
    int a()
    {
        printf("a\n");
        return 1;
    }

    char* s()
    {
        printf("s\n");
        return "abc";
    }

    printf("call: %d, %s\n", a(), s());
    return EXIT_SUCCESS;
}
```

will output:

```text
s
a
call: 1, abc
```

Every [object](http://en.cppreference.com/w/c/language/object) in C, including the pointer, is passed in a "[call by value](https://en.wikipedia.org/wiki/Evaluation_strategy#Call_by_value)" (pass by value) way. We can pass a "pointer to the pointer" as the argument.

```c
void test(int** x)
{
    int* p = malloc(sizeof(int));
    *p = 123;
    *x = p;
}

int main(int argc, char* argv[])
{
    int* p;
    test(&p);
    printf("%d\n", *p);
    free(p);
    return EXIT_SUCCESS;
}
```

Note: do not return the stack variable in `test`.

#### Storage-class Specifiers

C99 has the following storage-class specifiers:

* `extern`: default specifier.
    * On functions: used to specify that a function has external linkage. These functions can be used in any program files.
    * On variables: used to specify that a variable is defined in other [translation units](https://en.wikipedia.org/wiki/Translation_unit_(programming)).
* `static`: used to specify that a function is available only in its translation unit (source code file). It can also be used to represent static variables.
* [`inline`](http://en.cppreference.com/w/c/language/inline): used to recommend the compiler to inline the body the function to the [call site](https://en.wikipedia.org/wiki/Call_site), but the complier decides whether to perform inlining. Normally, the functions that contain loops and recursive functions cannot be defined as an inline function.

Some notes about [GNU inline](https://gcc.gnu.org/onlinedocs/gcc/Inline.html):

* `static inline`: internal linkage function. Inlining is performed within the current translation unit. When `-O0` is specified, the function is still called.
* `inline`: external linkage function. Inlining is performed within the current translation unit. In other translation unit, it is a normal external linkage function. (the `inline` keyword cannot be specified to the header files)

The `inline` keyword can only used in function definitions.

#### Variadic Arguments

Variadic arguments are used to implement [variadic functions](https://en.wikipedia.org/wiki/Variadic_function):

* `va_start`: initialize the argument pointer of type `va_list` with the argument preceding the variadic arguments.
* `va_arg`: access the current variadic argument and modify the argument pointer to point to the next argument.
* `va_end`: perform cleanup so that the argument pointer is no longer usable.
* `va_copy`: use the existing argument pointer (`va_list`) to initialize another pointer.

```c
#include <stdarg.h>
/* specify number of variadic arguments */

void test(int count, ...)
{
    va_list args;
    va_start(args, count);

    for (int i = 0; i < count; i++)
    {
        int value = va_arg(args, int);
        printf("%d\n", value);
    }

    va_end(args);
}

/* end by NULL */
void test2(const char* s, ...)
{
    printf("%s\n", s);

    va_list args;
    va_start(args, s);

    char* value;
    do
    {
        value = va_arg(args, char*);
        if (value) printf("%s\n", value);
    }
    while (value != NULL);

    va_end(args);
}

/* directly pass va_list to the other variadic function */
void test3(const char* format, ...)
{
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
}

int main(int argc, char* argv[])
{
    test(3, 11, 22, 33);
    test2("hello", "aa", "bb", "cc", "dd", NULL);
    test3("%s, %d\n", "hello, world!", 1234);
    return EXIT_SUCCESS;
}
```

### Arrays

#### [Variable-Length Arrays](https://en.wikipedia.org/wiki/Variable-length_array)

If an array has automatic storage duration and is without the `static` specifier, then it can be defined using a non-constant expression.

```c
void test(int n)
{
    int x[n];
    for (int i = 0; i < n; i++)
    {
        x[i] = i;
    }

    struct data { int x[n]; } d;
    printf("%d\n", sizeof(d));
}

int main(int argc, char* argv[])
{
    int x[] = { 1, 2, 3, 4 };
    printf("%d\n", sizeof(x));

    test(2);
    return EXIT_SUCCESS;
}
```

#### Subscripts

`x[i]` is equivalent to `*(x + i)`; the array name by default is a pointer that points to the first element.

```c
int x[] = { 1, 2, 3, 4 };

x[1] = 10;
printf("%d\n", *(x + 1));

*(x + 2) = 20;
printf("%d\n", x[2]);
```

Since C does not perform range checking on array subscripts, care must be taken to ensure [out-of-bounds checking](https://en.wikipedia.org/wiki/Bounds_checking) when coding. An array's name by default is a constant pointer to the first element; `&x[i]` returns a `int*` pointer, which points to element `x[i]`.

#### Initialization

Besides using subscripts, an array can also be [initialized](http://en.cppreference.com/w/c/language/array_initialization) using initializers.

```c
int x[] = { 1, 2, 3 };
int y[5] = { 1, 2 };
int a[3] = {};

int z[][2] =
{
    { 1, 1 },
    { 2, 1 },
    { 3, 1 },
};
```

Rules of initialization are:

* If the array has [static storage duration](http://en.cppreference.com/w/c/language/storage_duration#Storage_duration), then the initializers must be [constant expressions](http://en.cppreference.com/w/c/language/constant_expression).
* If initializers are present, then the size of the array can be omitted, which is determined by the last initializer.
* If both the size of the array and initializers are present, then the elements without initializers are initialized to 0 or `NULL`.

We can also initialize specific elements in the initializers. For example, the following code:

```c
int x[] = { 1, 2, [6] = 10, 11 };
int len = sizeof(x) / sizeof(int);

for (int i = 0; i < len; i++)
{
    printf("x[%d] = %d\n", i, x[i]);
}
```

will output:

```text
x[0] = 1
x[1] = 2
x[2] = 0
x[3] = 0
x[4] = 0
x[5] = 0
x[6] = 10
x[7] = 11
```

#### Strings

A string is a `char` array ending with `\0`.

The following code:

```c
char s[10] = "abc";
char x[] = "abc";

printf("s, size=%d, len=%d\n", sizeof(s), strlen(s));
printf("x, size=%d, len=%d\n", sizeof(x), strlen(x));
```

will output:

```text
s, size=10, len=3
x, size=4, len=3
```

#### Multidimensional Arrays

A multidimensional array is an array whose elements are arrays. Note that elements are arrays, not array pointers.

The first dimension subscript can be omitted.

The following code:

```c
int x[][2] =
{
    { 1, 11 },
    { 2, 22 },
    { 3, 33 }
};

int col = 2, row = sizeof(x) / sizeof(int) / col;

for (int r = 0; r < row; r++)
{
    for (int c = 0; c < col; c++)
    {
        printf("x[%d][%d] = %d\n", r, c, x[r][c]);
    }
}
```

will output:

```text
x[0][0] = 1
x[0][1] = 11
x[1][0] = 2
x[1][1] = 22
x[2][0] = 3
x[2][1] = 33
```

A two-dimensional array is usually called a "matrix", like a `row * column` table. For example, `x[3][2]` is a table with 3 rows and 2 columns.

The elements in a multidimensional array are contiguously allocated, which is another factor that differentiate it from a pointer array.

The following code:

```c
int x[][2] =
{
    { 1, 11 },
    { 2, 22 },
    { 3, 33 }
};

int len = sizeof(x) / sizeof(int);
int* p = (int*)x;

for (int i = 0; i < len; i++)
{
    printf("x[%d] = %d\n", i, p[i]);
}
```

will output:

```text
x[0] = 1
x[1] = 11
x[2] = 2
x[3] = 22
x[4] = 3
x[5] = 33
```

Similarly, we can initialize specific elements.

The following code:

```c
int x[][2] =
{
    { 1, 11 },
    { 2, 22 },
    { 3, 33 },
    [4][1] = 100,
    { 6, 66 },
    [7] = { 9, 99 }
};

int col = 2, row = sizeof(x) / sizeof(int) / col;

for (int r = 0; r < row; r++)
{
    for (int c = 0; c < col; c++)
    {
        printf("x[%d][%d] = %d\n", r, c, x[r][c]);
    }
}
```

will output:

```text
x[0][0] = 1
x[0][1] = 11
x[1][0] = 2
x[1][1] = 22
x[2][0] = 0
x[2][1] = 0
x[3][0] = 0
x[3][1] = 0
x[4][0] = 0
x[4][1] = 100
x[5][0] = 6
x[5][1] = 66
x[6][0] = 0
x[6][1] = 0
x[7][0] = 9
x[7][1] = 99
```

#### Array Arguments

When an array is used as a function parameter, it is always implicitly converted to a pointer that points to the first element of the array. This means `sizeof` is no longer available to be used to obtain the array size.

The following code:

```c
void test(int x[])
{
    printf("%d\n", sizeof(x));
}

void test2(int* x)
{
    printf("%d\n", sizeof(x));
}

int main(int argc, char* argv[])
{
    int x[] = { 1, 2, 3 };
    printf("%d\n", sizeof(x));
    test(x);
    test2(x);
    return EXIT_SUCCESS;
}
```

will output:

```text
12
4
4
```

In the above code, `sizeof(x)` in `test` and `test2` is actually `sizeof(int*)`. We must either explicitly pass the length of the array, or use a special character (`NULL`) to mark the end of the array.


C99 supports arrays of variable size used as function parameters. Possible forms of passing array arguments are:

<small>[array-params.c](https://gist.github.com/shichao-an/9497fd38d97760ceee5f#file-array-params-c)</small>

```c
/* the array name by default is a pointer to its first element,
 * similar to test2
 */
void test1(int len, int x[])
{
    int i;
    for (i = 0; i < len; i++)
    {
        printf("x[%d] = %d; ", i, x[i]);
    }

    printf("\n");
}

/* pass the pointer to the first element */
void test2(int len, int* x)
{
    for (int i = 0; i < len; i++)
    {
        printf("x[%d] = %d; ", i, *(x + i));
    }

    printf("\n");
}

/* array pointer: the array name by default points to the first element;
 * &array returns the pointer to the entire array
 */
void test3(int len, int(*x)[len])
{
    for (int i = 0; i < len; i++)
    {
        printf("x[%d] = %d; ", i, (*x)[i]);
    }

    printf("\n");
}

/* multidimensional array: the array name by default is a pointer to its
 * first elements, which is also int(*)[]
 */
void test4(int r, int c, int y[][c])
{
    for (int a = 0; a < r; a++)
    {
        for (int b = 0; b < c; b++)
        {
            printf("y[%d][%d] = %d; ", a, b, y[a][b]);
        }
    }

    printf("\n");
}

/* multidimensional array: pass the pointer to the first element */
void test5(int r, int c, int (*y)[c])
{
    for (int a = 0; a < r; a++)
    {
        for (int b = 0; b < c; b++)
        {
            printf("y[%d][%d] = %d; ", a, b, (*y)[b]);
        }

        y++;
    }

    printf("\n");
}

/* multidimensional array */
void test6(int r, int c, int (*y)[][c])
{
    for (int a = 0; a < r; a++)
    {
        for (int b = 0; b < c; b++)
        {
            printf("y[%d][%d] = %d; ", a, b, (*y)[a][b]);
        }
    }

    printf("\n");
}

/* pointer array whose elements are pointers, equivalent to test8 */
void test7(int count, char** s)
{
    for (int i = 0; i < count; i++)
    {
        printf("%s; ", *(s++));
    }

    printf("\n");
}

void test8(int count, char* s[count])
{
    for (int i = 0; i < count; i++)
    {
        printf("%s; ", s[i]);
    }

    printf("\n");
}

/* pointer array ending with NULL */
void test9(int** x)
{
    int* p;
    while ((p = *x) != NULL)
    {
        printf("%d; ", *p);
        x++;
    }

    printf("\n");
}

int main(int argc, char* argv[])
{
    int x[] = { 1, 2, 3 };

    int len = sizeof(x) / sizeof(int);
    test1(len, x);
    test2(len, x);
    test3(len, &x);

    int y[][2] =
    {
        {10, 11},
        {20, 21},
        {30, 31}
    };

    int a = sizeof(y) / (sizeof(int) * 2);
    int b = 2;
    test4(a, b, y);
    test5(a, b, y);
    test6(a, b, &y);

    char* s[] = { "aaa", "bbb", "ccc" };
    test7(sizeof(s) / sizeof(char*), s);
    test8(sizeof(s) / sizeof(char*), s);

    int* xx[] = { &(int){111}, &(int){222}, &(int){333}, NULL };
    test9(xx);

    return EXIT_SUCCESS;
}
```

The above code will output:

```text
x[0] = 1; x[1] = 2; x[2] = 3;
x[0] = 1; x[1] = 2; x[2] = 3;
x[0] = 1; x[1] = 2; x[2] = 3;
y[0][0] = 10; y[0][1] = 11; y[1][0] = 20; y[1][1] = 21; y[2][0] = 30; y[2][1] = 31;
y[0][0] = 10; y[0][1] = 11; y[1][0] = 20; y[1][1] = 21; y[2][0] = 30; y[2][1] = 31;
y[0][0] = 10; y[0][1] = 11; y[1][0] = 20; y[1][1] = 21; y[2][0] = 30; y[2][1] = 31;
aaa; bbb; ccc;
aaa; bbb; ccc;
111; 222; 333;
```

### Pointers

#### `void` Pointers

`void*` (`void` pointer, or [pointer to void](http://en.cppreference.com/w/c/language/pointer#Pointers_to_void)) is also called the "versatile pointer". It is able to store an address of any object, but does not have the type of this object. This means the pointer must be converted (to the correct type) before operating on the object. Pointer to object of any type can be implicitly converted to `void` pointer to void, and vice versa.

The following code:

```c
void test(void* p, size_t len)
{
    unsigned char* cp = p;

    for (int i = 0; i < len; i++)
    {
        printf("%02x ", *(cp + i));
    }

    printf("\n");
}

int main(int argc, char* argv[])
{
    int x = 0x00112233;
    test(&x, sizeof(x));
    return EXIT_SUCCESS;
}
```

will output:

```text
33 22 11 00
```

#### Initializing Pointers

A pointer can be initialized with an initializer:

* The null-pointer constant: `NULL`.
* A pointer of the same type, or a pointer of same type and with less qualifiers.
* A `void` pointer.

A non-automatic or static pointer variable must be initialized using a compile-time constant expression, such as a function name.

```c
char s[] = "abc";
char* sp = s;
int x = 5;
int* xp = &x;
void test() {}
typedef void(*test_t)();

int main(int argc, char* argv[])
{
    static int* sx = &x;
    static test_t t = test;
    return EXIT_SUCCESS;
}
```

Note that in the above code, `typedef void(*test_t)()` declares a pointer type (as discussed in [a prior section](#function-types)).

#### Pointer Operations

##### **Using equality operators** *

An [equality operator](http://en.cppreference.com/w/c/language/operator_comparison#Equality_operators) can be used to determine two pointers point to the same object.

```c
int x = 1;

int *a, *b;
a = &x;
b = &x;

printf("%d\n", a == b);
```

##### **Using addition operators** *

An addition operation on a pointer can get the pointer to the *n*-th element of the array. (See [pointer arithmetic](http://en.cppreference.com/w/c/language/operator_arithmetic#Pointer_arithmetic))

```c
int x[] = { 1, 2, 3 };
int* p = x;

printf("%d, %d\n", x[1], *(p + 1));
```

##### **Using subtraction operators** *

An subtraction operation on a pointer can get index number of the array element the pointer points to.

```c
int x[] = { 1, 2, 3 };

int* p = x;
p++; p++;
int index = p - x;

printf("x[%d] = %d\n", index, x[index]);
```

##### **Using relational operators** *

Using a [relation operator](http://en.cppreference.com/w/c/language/operator_comparison#Relational_operators) to compare pointers is equivalent to comparing index numbers of array elements.

The following code:

```c
int x[] = { 1, 2, 3 };

int* p1 = x;
int* p2 = x;
p1++; p2++; p2++;

printf("p1 < p2? %s\n", p1 < p2 ? "Y" : "N");
```

outputs:

```text
p1 < p2? Y
```

##### **Using `&x[i]`**

`&x[i]` can be used to get the pointer that points to the array element specified by index number `i`.

```c
int x[] = { 1, 2, 3 };
int* p = &x[1];
*p += 10;
printf("%d\n", x[1]);
```
Note that `[]` takes precedence over `&`, and `*` takes precedence over arithmetic operators.

#### Qualifiers

The `const` qualifier can be used to declare:

* A constant of pointer type.
* A pointer that points to a constant.

```c
int x[] = { 1, 2, 3 };

// constant of pointer type: the pointer itself is a constant, which cannot
// be modified, but the object it points to can be modified
int* const p1 = x;
*(p1 + 1) = 22;
printf("%d\n", x[1]);

// pointer that points to a constant: the object it points to is a constant,
// which cannot be modified, but the pointer can be modified
int const *p2 = x;  // equivalent to: const int *p2 = x;
p2++;
printf("%d\n", *p2);
```

They differ in whether `const` qualifies `p` or `*p`.
o

A pointer with a [`restrict`](http://en.cppreference.com/w/c/language/restrict) qualifier is called a restrict-qualified pointer (or restrict pointer). It suggests to the compiler that during the `lifetime` of the pointer it is only allowed to modify the object through this pointer, but the complier can decide on its own whether to adopt this suggestion.

#### Array Pointer

An array pointer is a pointer to the array, not a pointer to the first element.

```c
int x[] = { 1, 2, 3 };
int(*p)[] = &x;

for (int i = 0; i < 3; i++)
{
    printf("x[%d] = %d\n", i, (*p)[i]);
    printf("x[%d] = %d\n", i, *(*p + i));
}
```

`&x` returns a pointer to the array. `*p` obtains the same pointer as `x`, namely the pointer to the first element, and the subscript or pointer operation can be used to access elements.

#### Array of Pointers

An array of pointers is the one whose elements are pointers. It is usually used to represent an array of strings or a [jagged array](https://en.wikipedia.org/wiki/Jagged_array). This kind of array's elements are pointers to the target objects (which can be arrays or other objects) instead of actual contents.

The following code:

```c
int* x[3] = {};

x[0] = (int[]){ 1 };
x[1] = (int[]){ 2, 22 };
x[2] = (int[]){ 3, 33, 33 };

int* x1 = *(x + 1);
for (int i = 0; i < 2; i++)
{
    printf("%d\n", x1[i]);
    printf("%d\n", *(*(x + 1) + i));
}
```

will output:

```text
2
2
22
22
```

Array `x` has three pointers to (three) target objects (arrays). `*(x + 1)` obtains the target object, which is equivalent to `x[1]`.

### Structs

#### Imcomplete Structs

A [struct](http://en.cppreference.com/w/c/language/struct) cannot have a member of its own type, but it can have a member as a pointer to its own type. See also [incomplete types](http://en.cppreference.com/w/c/language/type#Incomplete_types).

```c
struct list_node
{
    struct list_node* prev;
    struct list_node* next;
    void* value;
};
```

Only a struct tag can be used to define an incomplete struct type. Using [`typedef`](https://en.wikipedia.org/wiki/Typedef) like below is not allowed:

```c
typedef struct
{
    list_node* prev;
    list_node* next;
    void* value;
} list_node;
```

This will result in compiler error:

```text
$ make
gcc -Wall -g -c -std=c99 -o main.o main.c
main.c:15: error: expected specifier-qualifier-list before ‘list_node’
```

`typedef` and the struct tag can be used together:

```c
typedef struct node_t
{
    struct node_t* prev;
    struct node_t* next;
    void* value;
} list_node;
```

The tag name can be the same as the type name defined by `typedef`:

```c
typedef struct node_t
{
    struct node_t* prev;
    struct node_t* next;
    void* value;
} node_t;
```

### Doubts and Solutions

#### Verbatim

##### **p29 on multidimensional arrays**

```c
int x[][2] =
{
    { 1, 11 },
    { 2, 22 },
    { 3, 33 }
};

int len = sizeof(x) / sizeof(int);
int* p = (int*)x;

for (int i = 0; i < len; i++)
{
    printf("x[%d] = %d\n", i, p[i]);
}
```

<span class="text-danger">Question</span>: The array `x` is cast into a pointer p of type `int*` and iterated over like a one-dimensional regular array. Does this mean `p` is a "flattened" version of `x`?


- - -

### References

* [C reference - cppreference.com](http://en.cppreference.com/w/c)
* [CPP] *C Primer Plus* (6th Edition)
