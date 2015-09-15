### **Chapter 9. Memory Management**

This chapter covers the allocation, manipulation, and eventual release of memory.

### The Process Address Space

Linux virtualizes its physical resource of memory. Processes do not directly address physical memory. Instead, the kernel associates each process with a unique **virtual address space**:

* This address space is *linear*, with addresses starting at zero, increasing contiguously to some maximum value.
* The address space is also *flat*: it exists in one space, directly accessible, without the need for segmentation.

#### Pages and Paging

For the purposes of memory management, the page is the most important of these: it is the smallest addressable unit of memory that the memory management unit (MMU) can manage. Thus the virtual address space is carved up into pages. The machine architecture determines the page size. Typical sizes include 4 KB for 32-bit systems and 8 KB for 64-bit systems.

A 32-bit address space contains roughly a million 4 KB pages; a 64-bit address space with 8 KB pages contains several magnitudes more. A process cannot necessarily access all of those pages (they may not correspond to anything). Thus, pages are either valid or invalid:

* A **valid page** is associated with an actual page of data, either in physical memory (RAM) or on secondary storage (e.g a swap partition or file on disk).
* An **invalid page** is not associated with anything and represents an unused, unallocated piece of the address space. Accessing an invalid page results in a segmentation violation.

##### **Page fault, paging in and paging out ***

If a valid page is associated with data on secondary storage, a process cannot access that page until the data is brought into physical memory. When a process attempts to access such a page, the memory management unit generates a **page fault**. The kernel then intervenes, transparently **paging in** the data from secondary storage to physical memory.

Because there is considerably more virtual memory than physical memory, the kernel may have to move data out of memory to make room for the data paging in. **Paging out** is the process of moving data from physical memory to secondary storage. To minimize subsequent page-ins, the kernel attempts to page out the data that is the least likely to be used in the near future.

### Sharing and copy-on-write

Multiple pages of virtual memory, even in different virtual address spaces owned by different processes, may map to a single physical page. This allows different virtual address spaces to share the data in physical memory. For example, many processes on the system are using the standard C library. With shared memory, each of these processes may map the library into their virtual address space, but only one copy need exist in physical memory. As a more explicit example, two processes may both map into memory a large database. While both of these processes will have the database in their virtual address spaces, it will exist in RAM only once.

The shared data may be read-only, writable, or both readable and writable. When a process writes to a shared writable page, one of two things can happen. The simplest is that the kernel allows the write to occur, in which case all processes sharing the page can see the results of the write operation. Usually, allowing multiple processes to read from or write to a shared page requires some level of coordination and synchronization among the processes, but at the kernel level the write "just works" and all processes sharing the data instantly see the modifications.

Alternatively, the MMU can intercept the write operation and raise an exception; the kernel, in response, will transparently create a new copy of the page for the writing process, and allow the write to continue against the new page. We call this approach **copy-on-write** (COW). Effectively, processes are allowed read access to shared data, which saves space. But when a process wants to write to a shared page, it receives a unique copy of that page on the fly, thereby allowing the kernel to act as if the process always had its own private copy. As copy-on-write occurs on a page-by-page basis, with this technique a huge file may be efficiently shared among many processes, and the individual processes will receive unique physical pages only for those pages to which they themselves write.

#### Memory Regions

The kernel arranges pages into blocks that share certain properties (e.g. access permissions). These blocks are called **mappings**, **memory areas**, or **memory regions**. Certain types of memory regions can be found in every process:

* The **text segment** contains a process’s program code, string literals, constant vari‐ ables, and other read-only data. In Linux, this segment is marked read-only and is mapped in directly from the object file (the program executable or a library).
* The **stack** contains the process’s execution stack, which grows and shrinks dynamically as the stack depth increases and decreases. The execution stack contains local variables and function return data. In a multithreaded process, there is one stack per thread.
* The **data segment**, or **heap**, contains a process’s dynamic memory. This segment is writable and can grow or shrink in size. `malloc()` can satisfy memory requests from this segment.
* The **bss segment** contains uninitialized global variables. These variables contain special values (all zeros), per the C standard.

### Doubts and Solution

#### Verbatim

p295 on memory regions

> The **data segment**, or **heap**, contains a process’s dynamic memory. This segment is writable and can grow or shrink in size. `malloc()` can satisfy memory requests from this segment.

data segment = heap ?
