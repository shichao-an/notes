### **Chapter 9. An Introduction to Kernel Synchronization**

In a shared memory application, developers must ensure that shared resources are protected from concurrent access. The kernel is no exception. Shared resources require protection from concurrent access because if multiple threads of execution access and manipulate the data at the same time, the threads may overwrite each other's changes or access data while it is in an inconsistent state. Concurrent access of shared data often results in instability is hard to track down and debug.

The term *threads of execution* implies any instance of executing code. For example, this includes any of the following:

* A task in the kernel
* An interrupt handler
* A bottom half
* A kernel thread

This chapter may shorten *threads of execution* to simply *threads*. Keep in mind that this term describes any executing code.

[p161]

[Symmetrical multiprocessing](https://en.wikipedia.org/wiki/Symmetric_multiprocessing) support was introduced in the 2.0 kernel. Multiprocessing support implies that kernel code can simultaneously run on two or more processors. Consequently, without protection, code in the kernel, running on two different processors, can simultaneously access shared data at exactly the same time. With the introduction of the 2.6 kernel, the Linux kernel is preemptive. This implies that (in the absence of protection) the scheduler can preempt kernel code at virtually any point and reschedule another task. Today, a number of scenarios enable for concurrency inside the kernel, and they all require protection.

This chapter discusses the issues of concurrency and synchronization in the abstract, as they exist in any operating system kernel. The [next chapter](ch10.md) details the specific mechanisms and interfaces that the Linux kernel provides to solve synchronization issues and prevent race conditions.

### Critical Regions and Race Conditions

* Code paths that access and manipulate shared data are called [**critical regions**](https://en.wikipedia.org/wiki/Critical_section) (also called **critical sections**). It is usually unsafe for multiple threads of execution to access the same resource simultaneously.
* To prevent concurrent access during critical regions, the programmer must ensure that code executes [*atomically*](https://en.wikipedia.org/wiki/Linearizability), which means that operations complete without interruption as if the entire critical region were one indivisible instruction.
* It is a bug if it is possible for two threads of execution to be simultaneously executing within the same critical region. When this occur, it is called a [**race condition**](https://en.wikipedia.org/wiki/Race_condition), so-named because the threads raced to get there first. Debugging race conditions is often difficult because they are not easily reproducible.
* Ensuring that unsafe concurrency is prevented and that race conditions do not occur is called [**synchronization**](https://en.wikipedia.org/wiki/Synchronization_(computer_science)).
