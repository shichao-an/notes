### **Part 2: Advanced**

### Pointer Overview

#### Constants and Pointers *

See also [constness](http://en.cppreference.com/w/cpp/language/pointer#Constness).

Position of `const` | Syntax | Name | Description
------------------- | ------ | ---- | -----------
Before `*` | `const T*` | pointer to constant | a pointer to a constant object
Before `*` | `T const*` | pointer to constant | a pointer to a constant object
After `*` | `T* const` | constant pointer | a constant pointer to an object
After `*` | `const T* const` | constant pointer to constant | a constant pointer to a constant object

#### Constant Pointer

A **constant pointer** (or `const` pointer) is "a constant whose type is pointer" or "a constant of pointer type", which cannot be modified after initialization and points to a fixed memory address. We cannot modify the value of the pointer itself, but we can modify the content of the pointed-to object.

```c
int x[] = { 1, 2, 3, 4 };
int* const p = x;

for (int i = 0; i < 4; i++)
{
    int v = *(p + i);
    *(p + i) = ++v;
    printf("%d\n", v);
    //p++; // Compile Error!
}
```

In the above example, pointer `p` always points to the first element of array `x`, equivalent to the array name `x`. Because the pointer itself is a constant, operations such as `++p` and `p++` are not allowed, and will lead to a compilation error.

#### Pointer to Constant

A **pointer to constant** is "a pointer that points to constant data (object)". The pointed-to object is treated as a constant (though the original object is not necessarily a constant). Assignment is not allowed through the pointer. Since the pointer itself is not a constant, it can point to other locations.

```c
int x = 1, y = 2;

int const* p = &x;
//*p = 100; ! ! // Compile Error!

p = &y;
printf("%d\n", *p);

//*p = 100; ! ! // Compile Error!
```

It is recommended to place `const` in the front for better recognition.

Some special cases are:

(1) It is said that the following code won't compile with Visual C++, but can compile with GCC:

```c
const int x = 1;
int* p = &x;

printf("%d\n", *p);

*p = 1234;
printf("%d\n", *p);
```

(2) It perfectly makes sense for `const int* p` to point to `const int`, but modification (of the pointed-to value) through the pointer is not allowed.

```c
const int x = 1;
const int* p = &x;

printf("%d\n", *p);

*p = 1234; ! ! ! // Compile Error!
```

(3) Declaring "a constant pointer to constant" is rare, but understandable.

```c
int x = 10;
const int* const p = &i;

p++; ! ! ! ! // Compile Error!
*p = 20; ! ! ! // Compile Error!
```

It's easy to differentiate between a constant pointer and a pointer to constant by investigating what `const` qualifies, that is, whether `*` is left to or right to `const`. See also [constants and pointers](#constants-and-pointers).

* `int* const p`: `const` qualifies the pointer variable `p`, so the pointer is a constant.
* `int const *p`: `const` qualifies the pointed-to object `*p`, so it's a pointer to constant. It can also be written as `const int *p`.
* `const int* const p`: a constant pointer to constant. The right `const` qualifies `p` as constant, and the left `const` means that `*p` is a constant.

#### Pointer to Pointer

The pointer itself is a variable of data in a memory region. It can be pointed to by other pointers.

```c
int x = 10;
int* p = &x;
int** p2 = &p;

printf("p = %p, *p = %d\n", p, *p);
printf("p2 = %p, *p2 = %x\n", p2, *p2);
printf("x = %d, %d\n",*p, **p2);
```

will output:

```
p = 0xbfba3e5c, *p = 10
p2 = 0xbfba3e58, *p2 = bfba3e5c
x = 10, 10
```

We can see that `p2` stores the address of pointer `p`; that's what makes "pointer to pointer".

#### Pointer to Array

By default, the name of an array is a constant pointer to this array's first element.

```c
int x[] = { 1, 2, 3, 4 };
int* p = x;

for (int i = 0; i < 4; i++)
{
    printf("%d, %d, %d\n", x[i], *(x + i), *p++);
}
```

We can access array elements with `*(x + 1)`, but cannot do `x++` or `x--` operations.

A "pointer to array" does not have the same type as the array name. The pointer to array views the entire array as an object, not an element within.

```c
int x[] = { 1, 2, 3, 4 };

int* p = x;
int (*p2)[] = &x;          // pointer to array

for(int i = 0; i < 4; i++)
{
    printf("%d, %d\n", *p++, (*p2)[i]);
}
```

See [Pointer to Array](part1.md#pointer-to-array) for details.
