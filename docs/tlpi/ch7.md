### **Chapter 7. Memory Allocation**

Many system programs need to be able to allocate extra memory for dynamic data structures (e.g., linked lists and binary trees), whose size depends on information that is available only at run time. This chapter describes the functions that are used to allocate memory on the heap or the stack.

### Allocating Memory on the Heap

A process can allocate memory by increasing the size of the heap, a variable-size segment of contiguous virtual memory that begins just after the uninitialized data segment of a process and grows and shrinks as memory is allocated and freed ([Figure 6-1](figure_6-1.png)). The current limit of the heap is referred to as the **program break**.

#### Adjusting the Program Break: `brk()` and `sbrk()`

Resizing the heap (allocating or deallocating memory) is actually as simple as telling the kernel to adjust its idea of where the process’s program break is. Initially, the program break lies just past the end of the uninitialized data segment (the same location as `&end`, shown in [Figure 6-1](figure_6-1.png)).

After the program break is increased, the program may access any address in the newly allocated area, but no physical memory pages are allocated yet. The kernel automatically allocates new physical pages on the first attempt by the process to access addresses in those pages.

Traditionally, the UNIX system has provided two system calls for manipulating the program break, and these are both available on Linux: `brk()` and `sbrk()`.  Although these system calls are seldom used directly in programs, understanding them helps clarify how memory allocation works.

```c
#include <unistd.h>
int brk(void *end_data_segment);
/* Returns 0 on success, or –1 on error */

void *sbrk(intptr_t increment);
/* Returns previous program break on success, or (void *) –1 on error */
```

* The `brk()` system call sets the program break to the location specified by *end_data_segment*. Since virtual memory is allocated in units of pages, *end_data_segment* is effectively rounded up to the next page boundary.
    * Attempts to set the program break below its initial value (i.e., below `&end`) are likely to result in unexpected behavior, such as a segmentation fault (the `SIGSEGV` signal) when trying to access data in now nonexistent parts of the initialized or uninitialized data segments.
    * The precise upper limit on where the program break can be set depends on a range of factors, including:
        * The process resource limit for the size of the data segment (`RLIMIT_DATA`)
        * The location of memory mappings, shared memory segments, and shared libraries.
* A call to `sbrk()` adjusts the program break by adding increment to it. On Linux, `sbrk()` is a library function implemented on top of `brk()`.
    * The `intptr_t` type used to declare increment is an integer data type.
    * On success, `sbrk()` returns the previous address of the program break. In other words, if we have increased the program break, then the return value is a pointer to the start of the newly allocated block of memory.
    * The call `sbrk(0)` returns the current setting of the program break without changing it. This can be useful if we want to track the size of the heap, perhaps in order to monitor the behavior of a memory allocation package.

#### Allocating Memory on the Heap: `malloc()` and `free()`

In general, C programs use the `malloc` family of functions to allocate and deallocate memory on the heap. These functions offer several advantages over `brk()` and `sbrk()` in that:

* They are standardized as part of the C language;
* They are easier to use in threaded programs;
* They provide a simple interface that allows memory to be allocated in small units;
* They allow us to arbitrarily deallocate blocks of memory, which are maintained on a free list and recycled in future calls to allocate memory.

The `malloc()` function allocates *size* bytes from the heap and returns a pointer to the start of the newly allocated block of memory. The allocated memory is not initialized.

```c
#include <stdlib.h>

void *malloc(size_t size);
/* Returns pointer to allocated memory on success, or NULL on error */
```

Because `malloc()` returns `void *`, we can assign it to any type of C pointer. The block of memory returned by `malloc()` is always aligned on a byte boundary suitable for any type of C data structure. In practice, this means that it is allocated on an 8-byte or 16-byte boundary on most architectures.

SUSv3 specifies that the call `malloc(0)` may return either `NULL` or a pointer to a small piece of memory that can (and should) be freed with `free()`. On Linux, `malloc(0)` follows the latter behavior.

If memory could not be allocated (perhaps because we reached the limit to which the program break could be raised), then `malloc()` returns `NULL` and sets `errno` to indicate the error. Although the possibility of failure in allocating memory is small, all calls to `malloc()`, and the related functions that we describe later, should check for this error return.

The `free()` function deallocates the block of memory pointed to by its *ptr* argument, which should be an address previously returned by `malloc()` or one of the other heap memory allocation functions described later this chapter.

```c
#include <stdlib.h>

void free(void *ptr);
```

In general, `free()` doesn’t lower the program break, but instead adds the block of memory to a list of free blocks that are recycled by future calls to `malloc()`. This is done for several reasons:

* <u>The block of memory being freed is typically somewhere in the middle of the heap, rather than at the end, so that lowering the program break is not possible.</u>
* It minimizes the number of `sbrk()` calls that the program must perform. System calls have a small but significant overhead.
* In many cases, lowering the break would not help programs that allocate large amounts of memory, since they typically tend to hold on to allocated memory or repeatedly release and reallocate memory, rather than release it all and then continue to run for an extended period of time.

If the argument given to `free()` is a `NULL` pointer, then the call does nothing. In other words, it is not an error to give a `NULL` pointer to `free()`.

Making any use of *ptr* after the call to `free` (e.g. passing it to `free()` a second time) is an error that can lead to unpredictable results.
