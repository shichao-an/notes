## Chapter 1. Introduction

This chapter gives an overview of major features of Linux, as well as Unix kernels. This book is based on [Linux 2.6.11](https://github.com/shichao-an/linux-2.6.11.12) source code.

### Linux Versus Other Unix-Like Kernels

Several differences between Linux and Unix implementations:

* Kernel threading
* Preemptive kernel: Linux 2.6 can arbitrarily interleave execution flows while they are in privileged mode
* Multiprocessor support: Linux 2.6 supports symmetric multiprocessing (SMP)
* [STREAMS](http://en.wikipedia.org/wiki/STREAMS) is not included in Linux

### The Process/Kernel Model

* Users processes
* Kernel threads:
	1. run in Kernel Mode;
	2. are non-interactive;
	3. created during system startup
* Kernel routines can be activated in: 
	1. system call;
	2. exception signaled by a process; 
	3. interrupt by a peripheral device;
	4. kernel thread executed

### Process Implementation

**Process descriptor** contains registers:

* Program counter (PC) registers
* Stack pointer (SP) registers
* General purpose registers
* Floating point registers
* Processor control registers
* Memory management registers

### Reentrant Kernels
A **kernel control** path denotes the sequence of instructions executed by the kernel to handle a system call, an exception, or an interrupt.

### Process Address Space
### Synchronization and Critical Regions
### Signals and Interprocess Communication

* Unix signals
* System V IPC: semaphores, message queues, and shared memory

### Process Management

* `fork()`, `_exit()`, and `exec()`-like system calls
* `wait4()`
* Process groups and login sessions

### Memory Management

* Virtual memory acts as a logical layer between the application memory requests and the hardware Memory Management Unit (MMU).
* Kernel Memory Allocator: Linux’s KMA uses a Slab allocator on top of a buddy system.
* Process virtual address space


- - -

### Doubts and Solutions

#### Verbatim

p3:
> Linux uses kernel threads in a very limited way to execute a few kernel functions periodically; however, they do not represent the basic execution context abstraction. 

### Summary

#### Kernel Architecture

* The Linux kernel, as with most Unix kernels, is **monolithic**: each kernel layer is integrated into the whole kernel program and runs in Kernel Mode on behalf of the current process. [p11]
