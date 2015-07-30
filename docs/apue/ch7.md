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

There are eight ways for a process to terminate.

* Normal termination occurs in five ways:

    1. Return from `main`
    2. Calling `exit`
    3. Calling `_exit` or `_Exit`
    4. Return of the last thread from its start routine (Section 11.5)
    5. Calling `pthread_exit` (Section 11.5) from the last thread

* Abnormal termination occurs in three ways:

    6. Calling `abort` (Section 10.17)
    7. Receipt of a signal (Section 10.2)
    8. Response of the last thread to a cancellation request (Sections 11.5 and 12.7)

#### Exit Functions

Three functions terminate a program normally:

<small>[apue_exit.h](https://gist.github.com/shichao-an/8387fdff1497e1cc7fd6)</small>

```c
#include <stdlib.h>

void exit(int status);
void _Exit(int status);

#include <unistd.h>

void _exit(int status);
```

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

<small>[apue_atexit.h](https://gist.github.com/shichao-an/edfab5a8a91b62b4ba5b)</small>

```c
#include <stdlib.h>

int atexit(void (*func)(void));

/* Returns: 0 if OK, nonzero on error */
```

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

```
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

<small>[apue_malloc.h](https://gist.github.com/shichao-an/e4b320547e3c303af467)</small>

```c
#include <stdlib.h>

void *malloc(size_t size);
void *calloc(size_t nobj, size_t size);
void *realloc(void *ptr, size_t newsize);

/* All three return: non-null pointer if OK, NULL on error */

void free(void *ptr);
```

* `malloc`: allocates a specified number of bytes of memory
* `calloc`: allocates space for a specified number of objects of a specified size
* `realloc`: increases or decreases the size of a previously allocated area. The final argument to realloc is the new size of the region, not the
difference between the old and new sizes

The pointer returned by the three allocation functions is guaranteed to be suitably aligned so that it can be used for any data object.

Because the three `alloc` functions return a generic `void *` pointer, if we `#include <stdlib.h>` (to obtain the function prototypes), we do not explicitly have to cast the pointer returned by these functions when we assign it to a pointer of a different type. <u>The default return value for undeclared functions is int, so using a cast without the proper function declaration could hide an error on systems where the size of type int differs from the size of a function’s return value (a pointer in this case).</u>

* `free`: causes the space pointed to by *ptr* to be deallocated. This freed space is usually put into a pool of available memory and can be allocated in a later call to one of the three `alloc` functions.

The allocation routines are usually implemented with the `sbrk(2)` system call. This system call expands (or contracts) the heap of the process. Although `sbrk` can expand or contract the memory of a process, most versions of `malloc` and free never decrease their memory size. <u>The space that we free is available for a later allocation, but the freed space is not usually returned to the kernel; instead, that space is kept in the `malloc` pool.</u>

#### Alternate Memory Allocators

[p209]

* `libmalloc`
* `vmalloc`
* `quick-fit`
* `jemalloc`
* `TCMalloc`
* `alloca` Function: has the same calling sequence as `malloc`; however, instead of allocating memory from the heap, the memory is allocated from the stack frame of the current function

### Environment Variables

The environment strings are usually of the form:

```
name=value
```

The UNIX kernel never looks at these strings; their interpretation is up to the various applications.

<small>[apue_getenv.h](https://gist.github.com/shichao-an/618104c2fa3a6caba3b3)</small>

```c
#include <stdlib.h>

char *getenv(const char *name);
/* Returns: pointer to value associated with name, NULL if not found */

int putenv(char *str);
/* Returns: 0 if OK, nonzero on error */

int setenv(const char *name, const char *value, int rewrite);
int unsetenv(const char *name);

/* Both return: 0 if OK, −1 on error */
```

* `getenv`: returns a pointer to the value of a `name=value` string. We should always use `getenv` to fetch a specific value from the environment, instead of accessing `environ` directly

[![Figure 7.7 Environment variables defined in the Single UNIX Specification](figure_7.7_600.png)](figure_7.7.png "Figure 7.7 Environment variables defined in the Single UNIX Specification")

* `putenv`: takes a string of the form `name=value` and places it in the environment list. If name already exists, its old definition is first removed.
* `setenv`: sets *name* to *value*. If name already exists in the environment, then:
    * If *rewrite* is nonzero, the existing definition for *name* is first removed
    * If *rewrite* is 0, the existing definition for *name* is not removed, *name* is not set to the new value, and no error occurs
* `unsetenv`: removes any definition of name. It is not an error if such a definition does not exist.

Note the difference between `putenv` and `setenv`. Whereas `setenv` must allocate memory to create the `name=value` string from its arguments, `putenv` is free to place the string passed to it directly into the environment. Indeed, many implementations do exactly this, so <u>it would be an error to pass putenv a string allocated on the stack, since the memory would be reused after we return from the current function.</u>

* Deleting a string: we just find the pointer in the environment list and move all subsequent pointers down one.
* Modifying a existing *name*:
    * If new *value* is smaller than or equal to old: we just copy the string
    * If new *value* is larger than old: we must `malloc` and replace the old pointer in the environment list for *name* with the pointer to this allocated area
* Adding a new *name*:
    * First time: we call `malloc`, copy the old environment list to this new area and store a pointer to the `name=value` string at the end of
this list of pointers. We also store a null pointer at the end of this list, of course. Finally, we set `environ` to point to this new list of pointers. <u>If the original environment list was contained above the top of the stack, as is common, then we have moved this list of pointers to the heap. But most of the pointers in this list still point to `name=value` strings above the top of the stack.</u>
    * Not first time: we call `realloc` to allocate room for one more pointer. The pointer to the new `name=value` string is stored at the end of the list (on top of the previous null pointer), followed by a null pointer.

### `setjmp` and `longjmp` Functions

In C, we can't `goto` a label that’s in another function. Instead, we must use the `setjmp` and `longjmp` functions to perform this type of branching. These two functions are useful for handling error conditions that occur in a deeply nested function call.

<small>[apue_setjmp.h](https://gist.github.com/shichao-an/4d30742d979b1b83dc69)</small>

```c
#include <setjmp.h>

int setjmp(jmp_buf env);
/* Returns: 0 if called directly, nonzero if returning from a call to longjmp */

void longjmp(jmp_buf env, int val);
```

Examples:

* [cmd1.c](https://github.com/shichao-an/apue.3e/blob/master/environ/cmd1.c)
* [cmd2.c](https://github.com/shichao-an/apue.3e/blob/master/environ/cmd2.c)

#### Automatic, Register, and Volatile Variables

When we return to `main` as a result of the `longjmp`, implementations do not try to roll back these automatic variables and register variables (in `main`), though standards say only that their values are indeterminate.

Example:

* [testjmp.c](https://github.com/shichao-an/apue.3e/blob/master/environ/testjmp.c)

Compile the above program, with and without compiler optimizations, the results are different:

```text
$ gcc testjmp.c compile without any optimization
$ ./a.out
in f1():
globval = 95, autoval = 96, regival = 97, volaval = 98, statval = 99
after longjmp:
globval = 95, autoval = 96, regival = 97, volaval = 98, statval = 99
$ gcc -O testjmp.c compile with full optimization
$ ./a.out
in f1():
globval = 95, autoval = 96, regival = 97, volaval = 98, statval = 99
after longjmp:
globval = 95, autoval = 2, regival = 3, volaval = 98, statval = 99
```

The optimizations don’t affect the global, static, and volatile variables. The `setjmp(3)` manual page on one system states that variables stored in memory will have values as of the time of the `longjmp`, whereas variables in the CPU and floating-point registers are restored to their values when `setjmp` was called. Without optimization, all five variables are stored in memory. When we enable optimization, both `autoval` and `regival` go into registers, even though the former wasn't declared `register`, and the `volatile` variable stays in memory.

#### Potential Problem with Automatic Variables

<u>An automatic variable can never be referenced after the function that declared it returns.</u>

Incorrect usage of an automatic variable:

```c
#include <stdio.h>
FILE *
open_data(void)
{
    FILE *fp;
    char databuf[BUFSIZ]; /* setvbuf makes this the stdio buffer */
    if ((fp = fopen("datafile", "r")) == NULL)
        return(NULL);
    if (setvbuf(fp, databuf, _IOLBF, BUFSIZ) != 0)
        return(NULL);
    return(fp); /* error */
}
```

The problem is that when `open_data` returns, the space it used on the stack will be used by the stack frame for the next function that is called. But the standard I/O library will still be using that portion of memory for its stream buffer. Chaos is sure to result. To correct this problem, the array `databuf` needs to be allocated from global memory, either statically (`static` or `extern`) or dynamically (one of the `alloc` functions).


### `getrlimit` and `setrlimit` Functions

Every process has a set of resource limits, some of which can be queried and changed by the `getrlimit` and `setrlimit` functions.

<small>[apue_getrlimit.h](https://gist.github.com/shichao-an/4562094dcbbca444ec4b)</small>

```c
#include <sys/resource.h>

int getrlimit(int resource, struct rlimit *rlptr);
int setrlimit(int resource, const struct rlimit *rlptr);

/* Both return: 0 if OK, −1 on error */
```

These two functions are defined in the XSI option in the Single UNIX Specification. The resource limits for a process are normally established by process 0 when the system is initialized and then inherited by each successive process. Each implementation has its own way of tuning the various limits.

* *rlptr*: a pointer to the following structure:

```c
struct rlimit {
    rlim_t rlim_cur; /* soft limit: current limit */
    rlim_t rlim_max; /* hard limit: maximum value for rlim_cur */
};
```
* *resource* argument takes on one of the following values:

    * `RLIMIT_AS`: The maximum size in bytes of a process’s total available memory. This affects the `sbrk` function and the `mmap` function.
    * `RLIMIT_CORE`: The maximum size in bytes of a core file. A limit of 0 prevents the creation of a core file.
    * `RLIMIT_CPU`: The maximum amount of CPU time in seconds. When the soft limit is exceeded, the SIGXCPU signal is sent to the process.
    * `RLIMIT_DATA`: The maximum size in bytes of the data segment: the sum of the initialized data, uninitialized data, and heap from [Figure 7.6](figure_7.6.png).
    * `RLIMIT_FSIZE`: The maximum size in bytes of a file that may be created.  When the soft limit is exceeded, the process is sent the `SIGXFSZ` signal.
    * `RLIMIT_MEMLOCK`: The maximum amount of memory in bytes that a process can lock into memory using `mlock(2)`.
    * `RLIMIT_MSGQUEUE`: The maximum amount of memory in bytes that a process can allocate for POSIX message queues.
    * `RLIMIT_NICE`: The limit to which a process’s nice value can be raised to affect its scheduling priority.
    * `RLIMIT_NOFILE`: The maximum number of open files per process. Changing this limit affects the value returned by the `sysconf` function for its `_SC_OPEN_MAX` argument.
    * `RLIMIT_NPROC`: The maximum number of child processes per real user ID. Changing this limit affects the value returned for `_SC_CHILD_MAX` by the `sysconf` function.
    * `RLIMIT_NPTS`: The maximum number of pseudo terminals that a user can have open at one time.
    * `RLIMIT_RSS`: Maximum resident set size (RSS) in bytes. If available physical memory is low, the kernel takes memory from processes that exceed their RSS.
    * `RLIMIT_SBSIZE`: The maximum size in bytes of socket buffers that a user can consume at any given time.
    * `RLIMIT_SIGPENDING`: The maximum number of signals that can be queued for a process. This limit is enforced by the sigqueue function
    * `RLIMIT_STACK`: The maximum size in bytes of the stack. See [Figure 7.6](figure_7.6.png).
    * `RLIMIT_SWAP`: The maximum amount of swap space in bytes that a user can consume.
    * `RLIMIT_VMEM` This is a synonym for `RLIMIT_AS`.

Rules of changing resource limits:

1. A process can change its soft limit to a value less than or equal to its hard limit.
2. A process can lower its hard limit to a value greater than or equal to its soft limit. <u>This lowering of the hard limit is irreversible for normal users.</u>
3. Only a superuser process can raise a hard limit.

The resource limits affect the calling process and are inherited by any of its children. This means that the setting of resource limits needs to be built into the shells to affect all our future processes. Indeed, the Bourne shell, the GNU Bourne-again shell, and the Korn shell have the built-in `ulimit` command, and the C shell has the built-in limit command. (The `umask` and `chdir` functions also have to be handled as shell built-ins.)

Example:

* [getrlimit.c](https://github.com/shichao-an/apue.3e/blob/master/environ/getrlimit.c)

### Summary

Understanding the environment of a C program within a UNIX system’s environment is a prerequisite to understanding the process control features of the UNIX System. This chapter discusses process start and termination, and how a process is passed  an argument list and an environment. Although both the argument list and the environment are uninterpreted by the kernel, it is the kernel that passes both from the caller of `exec` to the new process.  This chapter also examines the typical memory layout of a C program and how a process can dynamically allocate and free memory.
