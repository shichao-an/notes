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

A constant pointer (or `const` pointer) is "a constant whose type is pointer" or "a constant of pointer type", which cannot be modified after initialization and points to a fixed memory address. We cannot modify the value of the pointer itself, but we can modify the content of the pointed-to object.

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
