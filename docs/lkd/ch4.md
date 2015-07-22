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

### Policy

Policy is the behavior of the scheduler that determines what runs when.

#### I/O-Bound Versus Processor-Bound Processes

Processes can be classified as either **I/O-bound** or **processor-bound**.

* An **I/O-bound process** spends much of its time submitting and waiting on I/O requests. Such a process is runnable for only short durations, because it eventually blocks waiting on more I/O.
    * "I/O" means any type of blockable resource, such as keyboard input or network I/O, and not just disk I/O. Most graphical user interface (GUI) applications are I/O-bound, even if they never read from or write to the disk, because they spend most of their time waiting on user interaction via the keyboard and mouse.
* **Processor-bound processes** spend much of their time executing code. Thet tend to run until they are preempted because they do not block on I/O requests very often. System response does not dictate that the scheduler run them often. A scheduler policy for processor-bound processes tends to run such processes less frequently but for longer durations.
    * Examples of processor-bound processes include: a program executing an infinite loop, *ssh-keygen*, *MATLAB*.

These classifications are not mutually exclusive. Processes can exhibit both behaviors simultaneously:

* The X Window server is both processor and I/O intense.
* A word processor can be I/O-bound but dive into periods of intense processor action.

The scheduling policy in a system must attempt to satisfy two conflicting goals:

* Fast process response time (low latency)
* Maximal system utilization (high throughput)

##### Favoring I/O-bound over processor-bound
Schedulers often employ complex algorithms to determine the most worthwhile process to run while not compromising fairness to other processes with lower priority. [p43-44]

* The scheduler policy in Unix systems tends to explicitly favor I/O-bound processes, thus providing good process response time.
* Linux, aiming to provide good interactive response and desktop performance, optimizes for process response (low latency), thus favoring I/O-bound processes over processor-bound processes. This is done in a creative manner that does not neglect processor-bound processes.

#### Process Priority

The **priority-based** scheduling is a common type of scheduling algorithm, which isn’t exactly implemented on Linux. It means that processes with a higher priority run before those with a lower priority, whereas processes with the same priority are scheduled *round-robin* (one after the next, repeating). On some systems, processes with a higher priority also receive a longer timeslice. The runnable process with timeslice remaining and the highest priority always runs. [p44]

##### nice value and real-time priority

The Linux kernel implements two separate priority ranges:

* **nice value** (a number from –20 to +19 with a default of 0) is the standard priority range used in all Unix systems:
    * Processes with a lower nice value (higher priority) receive a larger proportion of the system’s processor, and vice versa.
    * In Linux, the nice value is a control over the *proportion* of timeslice. In other Unix-based systems, such as Mac OS X, the nice value is a control over the *absolute* timeslice allotted to a process;
    * The `ps -el` command lists processes with their nice values.
* **Real-time priority** (configurable values that by default range from 0 to 99)
    * Higher real-time priority values correspond to a greater priority.
    * All real-time processes are at a higher priority than normal processes.
    * Linux implements real-time priorities in accordance with the relevant Unix standards, specifically POSIX.1b.
    * The `ps -eo state,uid,pid,ppid,rtprio,time,comm` command lists processes and their real-time priority. A value of “-” means the process is not real-time.

#### Timeslice

The *timeslice* is the numeric value that represents how long a task can run until it is preempted.

* Too long a timeslice causes the system to have poor interactive performance.
* Too short a timeslice causes significant amounts of processor time to be wasted on the overhead of switching processes.

The conflicting goals of I/O bound versus processor-bound processes:

* I/O-bound processes do not need longer timeslices (although they do like to run often)
* Processor-bound processes crave long timeslices (to keep their caches hot).

##### Timeslice on Linux

Linux’s CFS scheduler does not directly assign timeslices to processes, but assigns processes a *proportion* of the processor. The amount of processor time that a process receives is a function of the load of the system. This assigned proportion is further affected by each process’s nice value. The nice value acts as a weight, changing the proportion of the processor time each process receives. Processes with higher nice values (a lower priority) receive a deflationary weight, yielding them a smaller proportion of the processor, and vice versa.

With the CFS scheduler, whether the process runs immediately (preempting the currently running process) is a function of how much of a proportion of the processor the newly runnable processor has consumed. If it has consumed a smaller proportion of the processor than the currently executing process, it runs immediately

#### The Scheduling Policy in Action

Consider a system with two runnable tasks: a text editor (I/O-bound) and a video encoder (processor-bound). [p45-46]

Ideally, the scheduler gives the text editor a larger proportion of the available processor than the video encoder, because the text editor is interactive. We have two goals for the text editor:

1. We want the text editor to have a large amount of processor time available to it; not because it needs a lot of processor (it does not) but because we want it to always have processor time available the moment it needs it.
2. We want the text editor to preempt the video encoder the moment it wakes up (say, when the user presses a key). This can ensure the text editor has good *interactive performance* and is responsive to user input.

**How the above two goals achieved**

1. Instead of assigning the text editor a specific priority and timeslice, the Linux guarantees the text editor a specific proportion of the processor. If the two are the only processes with same nice values, each would be guaranteed half of the processor’s time (the proportion is 50%). Because the text editor spends most of its time blocked, waiting for user key presses, it does not use anywhere near 50% of the processor. Conversely, the video encoder is free to use more than its allotted 50%, enabling it to finish the encoding quickly.
2. When the editor wakes up, CFS notes that it is allotted 50% of the processor but has used considerably less, and thus determines that the text editor has run for *less time* than the video encoder. Attempting to give all processes a fair share of the processor, it then preempts the video encoder and enables the text editor to run. [p46]


### The Linux Scheduling Algorithm

#### Scheduler Classes

The Linux scheduler is modular, enabling different algorithms to schedule different types of processes.This modularity is called **scheduler classes**. The base scheduler code, which is defined in [`kernel/sched.c`](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched.c), iterates over each scheduler class in order of priority.The highest priority scheduler class that has a runnable process wins, selecting who runs next.

The Completely Fair Scheduler (CFS) is the registered scheduler class for normal processes, called `SCHED_NORMAL` in Linux (and `SCHED_OTHER` in POSIX).  CFS is defined in [`kernel/sched_fair.c`](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c). The rest of this section discusses the CFS algorithm.

#### Process Scheduling in Unix Systems

To discuss fair scheduling, we must first describe how traditional Unix systems schedule processes.

Modern process schedulers have two common concepts: process priority and timeslice. Processes with a higher priority run more frequently and (on many systems) receive a higher timeslice. On Unix, the priority is exported to user-space in the form of nice values. This in practice leads to several problems:

1. Mapping nice values onto timeslices requires a decision about what absolute timeslice to allot each nice value, which leads to suboptimal switching behavior. [p47]
2. Nicing (down) a process by a relative nice value has wildly different effects depending on the starting nice value. [p47-48]
3. Absolute timeslice timeslice must be some integer multiple of the timer tick, which introduces several problems. [p48]
4. Handling process wake up in a priority-based scheduler that wants to optimize for interactive tasks may cause the scheduler providing one process an unfair amount of processor time, at the expense of the rest of the system. [p48]

The approach taken by CFS is a radical (for process schedulers) rethinking of timeslice allotment: Do away with timeslices completely and assign each process a proportion of the processor. CFS thus yields constant fairness but a variable switching rate.
