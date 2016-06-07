### **Chapter 3. Processes**

The concept of a process is fundamental to any multiprogramming operating system.

* A process is usually defined as an instance of a program in execution
    * For example, if 16 users are running *vi* at once, there are 16 separate processes (although they can share the same executable code).
    * Processes are often called tasks or threads in the Linux source code.

This chapter discuses:

* Static properties of processes
* How process switching is performed by the kernel
* How processes can be created and destroyed
* How Linux supports multithreaded applications. As mentioned in [Chapter 1](ch1.md), it relies on so-called [lightweight processes](https://en.wikipedia.org/wiki/Light-weight_process) (LWP).

### Processes, Lightweight Processes, and Threads

A **process** is an instance of a program in execution. You might think of it as the collection of data structures that fully describes how far the execution of the program has progressed.

Processes have a more or less significant life, optionally generate one or more child processes, and eventually die. Each process has just one parent.

From the kernel's point of view, the purpose of a process is to act as an entity to which system resources (CPU time, memory, etc.) are allocated.

Earlier Unix kernels employed a simple model of processes:

* When a process is created, it is almost identical to its parent.
* It receives a (logical) copy of the parent's address space and executes the same code as the parent, beginning at the next instruction following the process creation system call.
* Although the parent and child may share the pages containing the program code (text), they have separate copies of the data (stack and heap), so that changes by the child to a memory location are invisible to the parent (and vice versa).

#### Multithreaded Applications *

Modern Unix systems support *multithreaded applications*:

* Multithreaded applications are user programs that have many relatively independent execution flows sharing a large portion of the application data structures.
* In such systems, a process is composed of several **user threads** (or simply **threads**), each of which represents an execution flow of the process.
* Nowadays, most multithreaded applications are written using standard sets of library functions called *pthread* ([POSIX thread](https://en.wikipedia.org/wiki/POSIX_Threads)) libraries.

Older versions of the Linux kernel offered no support for multithreaded applications.

From the kernel point of view, a multithreaded application was just a normal process. The multiple execution flows of a multithreaded application were created, handled, and scheduled entirely in User Mode, usually by means of a POSIX-compliant *pthread* library.

However, such an implementation of multithreaded applications is not very satisfactory.  For instance, suppose a chess program uses two threads:

* One of them controls the graphical chessboard, waiting for the moves of the human player and showing the moves of the computer, while the other thread ponders the next move of the game. While the first thread waits for the human move, the second thread should run continuously.
* However, if the chess program is just a single process, the first thread cannot simply issue a blocking system call waiting for a user action; otherwise, the second thread is blocked as well. Instead, the first thread must employ sophisticated nonblocking techniques to ensure that the process remains runnable.

Linux uses **lightweight processes** to offer better support for multithreaded applications:

* Two lightweight processes may share some resources, like the address space, the open files, etc.
* Whenever one of them modifies a shared resource, the other immediately sees the change.
* The two processes must synchronize themselves when accessing the shared resource.

<u>A straightforward way to implement multithreaded applications is to associate a lightweight process with each thread.</u>

* In this way, the threads can access the same set of application data structures by simply sharing the same memory address space, the same set of open files, etc.
* At the same time, each thread can be scheduled independently by the kernel so that one may sleep while another remains runnable.

Examples of POSIX-compliant *pthread* libraries that use Linux's lightweight processes are:

* [LinuxThreads](https://en.wikipedia.org/wiki/LinuxThreads)
* [Native POSIX Thread Library](https://en.wikipedia.org/wiki/Native_POSIX_Thread_Library) (NPTL)
* IBM's Next Generation Posix Threading Package (NGPT)

POSIX-compliant multithreaded applications are best handled by kernels that support "thread groups". In Linux, a *thread group* is basically a set of lightweight processes that implement a multithreaded application and act as a whole with regards to some system calls such as `getpid()`, `kill()`, and `_exit()`.
