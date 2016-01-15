### **Part 1: Language**

The examples are based on GCC 32-bit.

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

##### **Character Literals** *

A [**character constants**](http://en.cppreference.com/w/c/language/character_constant) by default is an integer of type `int`. However, the compiler determines whether to interpret it into `char` or `int`.

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

##### **Representing Integer Literals** *

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
