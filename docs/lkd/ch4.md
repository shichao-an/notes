### **Chapter 4. Process Scheduling**

This chapter discusses the **process scheduler**, the kernel subsystem that puts those processes to work.

The process scheduler (or simply the scheduler) divides the finite resource of processor time between the runnable processes on a system. It is responsible for best utilizing the system and giving users the impression that multiple processes are executing simultaneously. [p41]

To best utilize processor time, assuming there are runnable processes, a process should always be running. If there are more *runnable* processes than processors in a system, some processes will not be running at a given moment. These processes are *waiting to run*. Deciding which process runs next, given a set of runnable processes, is the fundamental decision that the scheduler must make.

### Multitasking

A **multitasking** operating system is one that can simultaneously interleave execution of more than one process.

* On single processor machines, this gives the illusion of multiple processes running concurrently.
* On multiprocessor machines, this enables processes to actually run concurrently, in parallel, on different processors.

On either type of machine, it also enables many processes to *block* or *sleep*. Although these processes are in memory, they are not *runnable*. These processes utilize the kernel to wait until some event (keyboard input, network data, passage of time, and so on) occurs. [p41]

Multitasking operating systems come in two flavors:

* **Cooperative multitasking**
* **Preemptive multitasking**

#### Preemptive multitasking

Linux, like all Unix variants and most modern operating systems, implements preemptive multitasking. In preemptive multitasking, the scheduler decides
when a process is to cease running and a new process is to begin running.

* **Preemption**: the act of involuntarily suspending a running process.
* **Timeslice** of a process: the time the process runs before it is preempted is usually predetermined.
    * Managing the timeslice enables the scheduler to make global scheduling decisions for the system and prevents any one process from monopolizing the processor.
    * On many modern operating systems, the timeslice is dynamically calculated as a function of process behavior and configurable system policy.
    * Linux’s unique "fair" scheduler does not employ timeslices *per se*, to interesting effect.

#### Cooperative multitasking

In cooperative multitasking, a process does not stop running until it voluntarily decides to do so. The act of a process voluntarily suspending itself is called **yielding**, but the operating system cannot enforce this.

The shortcomings of this approach are manifest:

* The scheduler cannot make global decisions regarding how long processes run;
* Processes can monopolize the processor for longer than the user desires;
* A hung process that never yields can potentially bring down the entire system.

[p42]

### Linux’s Process Scheduler

From Linux’s first version in 1991 through the 2.4 kernel series, the Linux scheduler was simple in design. It was easy to understand, but scaled poorly in light of many runnable processes or many processors.

During the 2.5 kernel development series, the **O(1) scheduler** solved the shortcomings of the previous Linux scheduler and introduced powerful new features and performance characteristics. By introducing a constant-time algorithm for timeslice calculation and per-processor runqueues, it rectified the design limitations of the earlier scheduler.

However, the O(1) scheduler had several pathological failures related to scheduling latency-sensitive applications (interactive processes). Thus, although the O(1) scheduler was ideal for large server workloads, which lack interactive processes, it performed below par on desktop systems, where interactive applications are the *raison d’être*.

Beginning in the 2.6 kernel series, developers introduced new process schedulers aimed at improving the interactive performance of the O(1) scheduler. The most notable of these was the **Rotating Staircase Deadline** scheduler, which introduced the concept of **fair scheduling**, borrowed from queuing theory, to Linux’s process scheduler. This concept was the inspiration for the O(1) scheduler’s eventual replacement in kernel version 2.6.23, the **Completely Fair Scheduler** (CFS).

This chapter discusses the fundamentals of scheduler design and how they apply to the Completely Fair Scheduler and its goals, design, implementation, algorithms, and related system calls. We also discuss the O(1) scheduler because its implementation is a more "classic" Unix process scheduler model.
