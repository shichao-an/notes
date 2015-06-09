### **Chapter 7. Process Environment**

### Introduction

### `main` Function

A C program starts execution with a function called `main`:

```c
int main(int argc, char *argv[]);
```

* *argc*: number of command-line arguments
* *argv*: an array of pointers to the arguments

When a C program is executed by the kernel (by one of the `exec` functions), a special start-up routine is called before the `main` function is called. The executable program file specifies this routine as the starting address for the program; this is set up by the link editor (linker) when it is invoked by the C compiler. This start-up routine takes values from the kernel (the command-line arguments and the environment) and sets things up so that the `main` function is called as shown earlier.

### Process Termination

Three functions terminate a program normally:

<script src="https://gist.github.com/shichao-an/8387fdff1497e1cc7fd6.js"></script>

* `_exit`: returns to the kernel immediately
* `_Exit`: same as `_exit`
* `exit`: performs certain cleanup processing and then returns to the kernel. Historically, it has always performed a clean shutdown of the standard I/O library: the `fclose` function is called for all open streams

All three exit functions expect a single integer argument (**exit status**).

The <u>exit status of the process is undefined</u>, if any of the following occurs:

* Any of these functions is called without an exit status
* `main` does a return without a return value
* `main` function is not declared to return an integer

If the return type of main is an integer and main "falls off the end" (an implicit return), the exit status of the process is 0.

Returning an integer value from the main function is equivalent to calling exit with the same value:

`exit(0);` is same as `return(0);` from the `main` function.

#### `atexit` Function

With ISO C, a process can register at least 32 functions that are automatically called by `exit`. These are called **exit handlers** and are registered by calling the `atexit` function.

<script src="https://gist.github.com/shichao-an/edfab5a8a91b62b4ba5b.js"></script>

* *func* argument is the address of the function to be called by `exit`. When this function is called, it is not passed any arguments and is not expected to return a value. The `exit` function calls these functions in reverse order of their registration. Each function is called as many times as it was registered.

With ISO C and POSIX.1, `exit` first calls the exit handlers and then closes (via `fclose`) all open streams. POSIX.1 extends the ISO C standard by specifying that any exit handlers installed will be cleared if the program calls any of the `exec` family of functions.

The only way a program can be executed by the kernel is if one of the `exec` functions is called. <u>The only way a process can voluntarily terminate is if `_exit` or `_Exit` is called</u>, either explicitly or implicitly (by calling `exit`). A process can also be involuntarily terminated by a signal.

### Command-Line Arguments

When a program is executed, the process that does the `exec` can pass command-line arguments to the new program. This is part of the normal operation of the UNIX system shells.


Example:
```c
#include "apue.h"

int
main(int argc, char *argv[])
{
    int i;
    for (i = 0; i < argc; i++) /* echo all command-line args */
        printf("argv[%d]: %s\n", i, argv[i]);
    exit(0);
}
```

We are guaranteed by both ISO C and POSIX.1 that argv[argc] is a null pointer. This lets us alternatively code the argument-processing loop as:

```c
for (i = 0; argv[i] != NULL; i++)
```

### Environment List

Each program is also passed an environment list, which is an array of character pointers, with each pointer containing the address of a null-terminated C string. It is contained in the global variable environ:

```c
extern char **environ;
```

[![Figure 7.5 Environment consisting of five C character strings](figure_7.5_600.png)](figure_7.5.png "Figure 7.5 Environment consisting of five C character strings")

* `environ` is called the **environment pointer**, the array of pointers the environment list, and the strings they point to the **environment strings**, which by convention is `name=value` strings. By convetion, predefined names are entirely uppercase.

### Memory Layout of a C Program

Historically, a C program has been composed of the following pieces:

* Text segment: consists of the machine instructions that the CPU executes
* Initialized data segment (or simply data segment): contains variables that are specifically initialized in the program
* Uninitialized data segment (often called the "bss" segment, which is named after "block started by symbol"): data in this segment is initialized by the kernel to arithmetic 0 or null pointers before the program starts executing
* Stack: stores automatic variables, along with information that is saved each time a function is called
* Heap is where dynamic memory allocation usually takes place

[![Figure 7.5 Environment consisting of five C character strings](figure_7.6.png)](figure_7.6.png "Figure 7.5 Environment consisting of five C character strings")

With Linux on a 32-bit Intel x86 processor, the text segment starts at location `0x08048000`, and the bottom of the stack starts just below `0xC0000000`. <u>The stack grows from higher-numbered addresses to lower-numbered addresses on this particular architecture.</u> The unused virtual address space between the top of the heap and the top of the stack is large

The `size(1)` command reports the sizes (in bytes) of the text, data, and bss segments:

```text
    $ size /usr/bin/cc /bin/sh
    text data bss dec hex filename
    346919 3576 6680 357175 57337 /usr/bin/cc
    102134 1776 11272 115182 1c1ee /bin/sh
```

### Shared Libraries

Shared libraries remove the common library routines from the executable file and maintains a single copy of the library routine somewhere in memory that all processes reference:

* Pros: reduces the size of each executable file; library functions can be replaced with new versions without having to relink edit every program that uses the library
* Cons: adds some runtime overhead, either when the program is first executed or the first time each shared library function is called

### Memory Allocation

<script src="https://gist.github.com/shichao-an/e4b320547e3c303af467.js"></script>

* `malloc`: allocates a specified number of bytes of memory
* `calloc`: allocates space for a specified number of objects of a specified size
* `realloc`: increases or decreases the size of a previously allocated area

The pointer returned by the three allocation functions is guaranteed to be suitably aligned so that it can be used for any data object.

Because the three `alloc` functions return a generic `void *` pointer, if we `#include <stdlib.h>` (to obtain the function prototypes), we do not explicitly have to cast the pointer returned by these functions when we assign it to a pointer of a different type. <u>The default return value for undeclared functions is int, so using a cast without the proper function declaration could hide an error on systems where the size of type int differs from the size of a function’s return value (a pointer in this case).</u>

* `free`: causes the space pointed to by *ptr* to be deallocated. This freed space is usually put into a pool of available memory and can be allocated in a later call to one of the three `alloc` functions.
