### **Chapter 3. Process Management**

This chapter introduces the concept of the **process**. The process management is a crucial part of any operating system kernel, including Linux.

### The Process

A process is a program (object code stored on some media) in the midst of execution.

Besides the executing program code (*text section* in Unix), processes also include a set of resources:

* Open files
* Pending signals
* Internal kernel data
* Processor state
* Memory address space with one or more memory mappings
* **Thread(s) of execution**
* Data section containing global variables

#### Threads of execution

Threads of execution, often shortened to **threads**,  are the objects of activity within the process.

Each thread includes:

* Program counter
* Process stack
* Set of processor registers

The kernel schedules individual threads, not processes. <u>Linux does not differentiate between threads and processes. To Linux, a thread is just a special kind of process.</u>

#### Virtualized processor and virtual memory

On modern operating systems, processes provide two virtualizations: a **virtualized processor** and **virtual memory**.

* The virtual processor gives the process the illusion that it alone monopolizes the system, despite possibly sharing the processor among hundreds of other processes. See [Chapter 4. Process Scheduling](ch4.md).
* Virtual memory lets the process allocate and manage memory as if it alone owned all the memory in the system. See [Chapter 12. Memory Management](ch12.md)

<u>Threads share the virtual memory abstraction</u>, whereas each receives its own virtualized processor.

#### Life of a process

A process is an active program and related resources:

* Two or more processes can exist that are executing the *same* program.
* Two or more processes can exist that share various resources, such as open files or an address space.

#### fork, exec, exit and wait

In Linux, the `fork()` system call creates a new process by duplicating an existing one.

* The process that calls `fork()` is the parent, whereas the new process is the child.
* The parent resumes execution and the child starts execution at the same place: where the call to `fork()` returns.
* The `fork()` system call <u>returns from the kernel twice: once in the parent process and again in the newborn child.</u>

The `exec()` family of function calls creates a new address space and loads a new program into the newborn child immediately after a fork. In contemporary Linux kernels, <u>`fork()` is actually implemented via the `clone()` system call</u>, which is discussed in a following section.

The `exit()` system call terminates the process and frees all its resources. A parent process can inquire about the status of a terminated child via the `wait4()` system call. A process can wait for the termination of a specific process. <u>When a process exits, it is placed into a special zombie state that represents terminated processes until the parent calls `wait()` or `waitpid()`.</u> The kernel implements the `wait4()` system call. Linux systems, via the C library, typically provide the `wait()`, `waitpid()`, `wait3()`, and `wait4()` functions.

### Process Descriptor and the Task Structure

Another name for a process is a **task**. The Linux kernel internally refers to processes as tasks. In this book, the terms are used interchangeably, though <u>"task" generally refers to a process from the kernel's point of view.</u>

The kernel stores the list of processes in a circular doubly linked list called the **task list**.

A **process descriptor** of the type `struct task_struct` (defined in `<linux/sched.h>`) is an element in the task list. It contains all the information about a specific process.

The `task_struct` is a relatively large data structure, at around 1.7 kilobytes on a 32-bit machine. The process descriptor contains the data that describes the executing program: open files, the process's address space, pending signals, the process's state, etc. See the figure below.

[![Figure 3.1 The process descriptor and task list.](figure_3.1.png)](figure_3.1.png "Figure 3.1 The process descriptor and task list.")

#### Allocating the Process Descriptor

The `task_struct` structure is allocated via the **slab allocator** to provide object reuse and cache coloring (see [Chapter 12](ch12.md)). The structure `struct thread_info` lives at the bottom of the stack (for stacks that grow down) and at the top of the stack (for stacks that grow up)

[![Figure 3.2 The process descriptor and kernel stack.](figure_3.2.png)](figure_3.2.png "Figure 3.2 The process descriptor and kernel stack.")

[Errata](http://www.crashcourse.ca/wiki/index.php/Updates_to_LKD3#Figure_3.2_.28p._26.29): "struct thread_struct" should read "struct thread_info"

The `thread_info` structure is defined on x86 in `<asm/thread_info.h>` (see below code). Each task's `thread_info` structure is allocated at the end of its stack. The task element of the structure is a pointer to the task's actual `task_struct`:

* [arch/x86/include/asm/thread_info.h](https://github.com/shichao-an/linux-2.6.34.7/blob/master/arch/x86/include/asm/thread_info.h#L26)

```c
struct thread_info {
    struct task_struct *task;
    struct exec_domain *exec_domain;
    __u32 flags;
    __u32 status;
    __u32 cpu;
    int preempt_count;
    mm_segment_t addr_limit;
    struct restart_block restart_block;
    void *sysenter_return;
    int uaccess_err;
};
```

#### Storing the Process Descriptor

The **process identification** (PID) is numerical value, represented by the [opaque type](https://en.wikipedia.org/wiki/Opaque_data_type) `pid_t` (typically `int`), for the system to identify processes. The default maximum value is only 32,768 (that of a `short int`), although the value optionally can be increased as high as four million (this is controlled in `<linux/threads.h>`). The kernel stores this value as `pid` inside each process descriptor. [p26]

Large servers may require many more than 32,768 (maximum value) processes. <u>The lower the value, the sooner the values will wrap around, destroying the useful notion that higher values indicate later-run processes than lower values.</u> The administrator may increase the maximum value via `/proc/sys/kernel/pid_max`.

Inside the kernel, tasks are typically referenced directly by a pointer to their `task_struct` structure. In fact, most kernel code that deals with processes works directly with `struct task_struct`. Consequently, it is useful to be able to quickly look up the process descriptor of the currently executing task, which is done via the `current` macro. This macro must be independently implemented by each architecture:

* Some architectures save a pointer to the `task_struct` structure of the currently running process in a register, enabling for efficient access.
* Other architectures, such as x86 (which has few registers to waste), make use of the fact that struct `thread_info` is stored on the kernel stack to calculate the location of `thread_info` and subsequently the `task_struct`.

##### The `current_thread_info()` function

On x86, `current` is calculated by masking out the 13 least-significant bits of the stack pointer to obtain the `thread_info` structure. This is done by the `current_thread_info()` function ([arch/x86/include/asm/thread_info.h#L184](https://github.com/shichao-an/linux-2.6.34.7/blob/master/arch/x86/include/asm/thread_info.h#L184)). The assembly is shown here:

```nasm
movl $-8192, %eax
andl %esp, %eax
```

This assumes that the stack size is 8KB. When 4KB stacks are enabled, 4096 is used in lieu of 8192.

`current` dereferences the task member of `thread_info` to return the `task_struct`:

* [include/asm-generic/current.h](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/asm-generic/current.h)

```c
current_thread_info()->task;
```

#### Process State

The `state` field of the process descriptor describes the current condition of the process.

[![Figure 3.3 Flow chart of process states.](figure_3.3_600.png)](figure_3.3.png "Figure 3.3 Flow chart of process states.")

Each process on the system is in exactly one of five different states. This value is represented by one of five flags:

* `TASK_RUNNING`: The process is runnable; it is either currently running or on a runqueue waiting to run. This is the only possible state for a process executing in user-space; it can also apply to a process in kernel-space that is actively running.
* `TASK_INTERRUPTIBLE`: The process is sleeping (blocked), waiting for some condition to exist. The process also awakes prematurely and becomes runnable if it receives a signal.
* `TASK_UNINTERRUPTIBLE`: This state is identical to `TASK_INTERRUPTIBLE` except that it does not wake up and become runnable if it receives a signal. This is used in situations where the process must wait without interruption or when the event is expected to occur quite quickly. Because the task does not respond to signals in this state, `TASK_UNINTERRUPTIBLE` is less often used than `TASK_INTERRUPTIBLE`.
* `__TASK_TRACED`: The process is being traced by another process, such as a debugger, via **ptrace**.
* `__TASK_STOPPED`: Process execution has stopped; the task is not running nor is it eligible to run. This occurs if the task receives the `SIGSTOP`, `SIGTSTP`, `SIGTTIN`, or `SIGTTOU` signal or if it receives any signal while it is being debugged.

#### Manipulating the Current Process State

Kernel code often needs to change a process's state. The preferred mechanism is using:

```c
set_task_state(task, state); /* set task ‘task’ to state ‘state’ */
```

This function sets the given task to the given state. If applicable, it also provides a memory barrier to force ordering on other processors (only needed on SMP systems). Otherwise, it is equivalent to:

```c
task->state = state;
```

The method `set_current_state(state)` is synonymous to `set_task_state(current, state)`. See `<linux/sched.h>` for the implementation of these and related functions.

* [include/linux/sched.h#L226](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/sched.h#L226)

#### Process Context

The program code is read in from an **executable file** and executed within the program's address space.

* **User-space**: Normal program execution occurs in user-space.
* **Kernel-space**: When a program executes a system call or triggers an exception, it enters kernel-space. At this point, the kernel is said to be "executing on behalf of the process" and is in **process context**. When in process context, the `current` macro is valid.
    * Other than process context there is [**interrupt context**](ch7.md#interrupt-context) (discussed in [Chapter 7](ch7.md)). In interrupt context, the system is not running on behalf of a process but is executing an interrupt handler. No process is tied to interrupt handlers.

Upon exiting the kernel, the process resumes execution in user-space, unless a higher-priority process has become runnable in the interim, in which case the scheduler is invoked to select the higher priority process.

A process can begin executing in kernel-space only through one of the following well-defined interfaces:

* System calls
* Exception handlers

#### The Process Family Tree

All processes are descendants of the `init` process (PID 1). The kernel starts init in the last step of the boot process. The init process reads the system **initscripts** and executes more programs, eventually completing the boot process.

* Every process on the system has exactly one **parent**.
* Every process has zero or more **children**.
* Processes that are all direct children of the same parent are called **siblings**.

- - -
[UTLK p87-88]

The pointers (`next` and `prev`) in a `list_head` field store the addresses of other `list_head` fields rather than the addresses of the whole data structures in which the `list_head` structure is included. See figure below:

[![Figure 3-3. Doubly linked lists built with list_head data structures](/utlk/figure_3-3_600.png)](/utlk/figure_3-3.png "Figure 3-3. Doubly linked lists built with list_head data structures")

* [include/linux/list.h](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h)

- - -

The relationship between processes is stored in the process descriptor.

Each `task_struct` ([include/linux/sched.h#L1170](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/sched.h#L1170)) has:

* `parent`: pointer to the parent's `task_struct`
* `children`: list of children (`struct list_head`)

To obtain the process descriptor of a given process's parent:

```c
struct task_struct *my_parent = current->parent;
```

To iterate over a process's children:

```c
struct task_struct *task;
struct list_head *list;

list_for_each(list, &current->children) {
    task = list_entry(list, struct task_struct, sibling);
    /* task now points to one of current's children */
}
```

* `list_for_each`: [include/linux/list.h#L367](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L367)

The `init` task's process descriptor is statically allocated as `init_task`. The following code will always succeed:

```c
struct task_struct *task;

for (task = current; task != &init_task; task = task->parent)
;
/* task now points to init */
```

You can follow the process hierarchy from any one process in the system to any other.  Oftentimes, it is desirable simply to iterate over all processes in the system. This is easy because the task list is a circular, doubly linked list.

To obtain the next task in the list, given any valid task, use:

```c
list_entry(task->tasks.next, struct task_struct, tasks)
```

To obtain the previous task works the same way:

```c
list_entry(task->tasks.prev, struct task_struct, tasks)
```

* `list_entry`: [include/linux/list.h](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L348)

These two routines are provided by the macros `next_task(task)` and `prev_task(task)`. (See [Doubts and Solutions]())

The macro `for_each_process(task)` iterates over the entire task list. On each iteration, task points to the next task in the list:

```c
struct task_struct *task;

for_each_process(task) {
    /* this pointlessly prints the name and PID of each task */
    printk("%s[%d]\n", task->comm, task->pid);
}
```

* `for_each_process`: [include/linux/sched.h#L2139](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/sched.h#L2139)

It is expensive to iterate over every task in a system with many processes; code should have good reason (and no alternative) before doing so.

### Process Creation

Most operating systems implement a **spawn** mechanism to create a new process in a new address space, read in an executable, and begin executing it. Unix separates these steps into two distinct functions: `fork()` and `exec()`.

* `fork()`: creates a child process that is a copy of the current task. It differs from the parent only in its PID, its PPID (parent's PID), and certain resources and statistics (e.g. pending signals) which are not inherited.
* `exec()`: loads a new executable into the address space and begins executing it.

#### Copy-on-Write

If upon `fork()` all resources owned by the parent are duplicated and the copy is given to the child, it is naive and inefficient in that it copies much data that might otherwise be shared. Worse still, if the new process were to immediately execute a new image, all that copying would go to waste.

In Linux, `fork()` is implemented through the use of copy-on-write pages.

**Copy-on-write** (COW) can delay or prevent copying data. Rather than duplicating the process address space, the parent and the child can share a single copy.

* If the data is written to, it is marked and a duplicate is made and each process receives a unique copy. The duplication of resources occurs only when they are written; until then, they are shared read-only.
* In the case that the pages are never written (if `exec()` is called immediately after `fork()`), they never need to be copied.

The only overhead incurred by `fork()` is the duplication of the parent's page tables and the creation of a unique process descriptor for the child. In the common case that a process executes a new executable image immediately after forking, this optimization prevents the wasted copying of large amounts of data (with the address space, easily tens of megabytes). This is an important optimization because the Unix philosophy encourages quick process execution.

#### Forking

Linux implements `fork()` via the `clone()` system call which takes a series of flags that specify which resources the parent and child process should share.

* The `fork()`, `vfork()`, and `__clone()` library calls all invoke the `clone()` system call with the requisite flags.
* The `clone()` system call calls `do_fork()`.

The bulk of the work in forking is handled by `do_fork()`, which is defined in `kernel/fork.c`. `do_fork()` function calls `copy_process()` and then starts the process running.

* `do_fork()`: [kernel/fork.c#L1354](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/fork.c#L1354)
* `copy_process()`: [kernel/fork.c#L957](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/fork.c#L957)

The interesting work is done by `copy_process()`:

1. It calls `dup_task_struct()` that creates following for the new process with identical values to those of the current task:
    * Kernel stack
    * `thread_info` structure
    * `task_struct`
    * (At this point, the child and parent process descriptors are identical)
2. It then checks that the new child will not exceed the resource limits on the number of processes for the current user.
3. Various members of the process descriptor are cleared or set to initial values, <u>to differentiate the child from its parent.</u>
    * Members of the process descriptor not inherited are primarily statistically information.
    * The bulk of the values in `task_struct` remain unchanged.
4. The child's state is set to `TASK_UNINTERRUPTIBLE` to ensure that it does not yet run.
5. It calls `copy_flags()` to update the flags member of the `task_struct` (per process flags: [include/linux/sched.h#L1693](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/sched.h#L1693)).
    * The `PF_SUPERPRIV` flag, which denotes whether a task used superuser privileges, is cleared
    * The `PF_FORKNOEXEC` flag, which denotes a process that has not called `exec()`, is set.
6. It calls `alloc_pid()` to assign an available PID to the new task.
7. Depending on the flags passed to `clone()`, `copy_process()` either duplicates or shares:
    * Open files
    * Filesystem information
    * Signal handlers
    * Process address space
    * Namespace
    * (These resources are typically shared between threads in a given process; otherwise they are unique and thus copied here)
8. Finally, `copy_process()` cleans up and returns to the caller <u>a pointer to the new child</u>.

Back in `do_fork()`, if `copy_process()` returns successfully, the new child is woken up and run.

<u>Deliberately, the kernel runs the child process first. In the case of the child calling `exec()` immediately, this eliminates any copy-on-write overhead that would occur if the parent ran first and began writing to the address space.</u>

#### `vfork()`

The `vfork()` system call has the same effect as `fork()`, except that the page table entries of the parent process are not copied. The child executes as the sole thread in the parent's address space, and the parent is blocked until the child either calls `exec()` or exits. The child is not allowed to write to the address space. [p33]

Today, with copy-on-write and child-runs-first semantics, the only benefit to `vfork()` is not copying the parent page tables entries. [p33]

The `vfork()` system call is implemented via a special flag to the `clone()` system call:

1. In `copy_process()`, the `task_struct` member `vfork_done` is set to NULL.
2. In `do_fork()`, if the special flag was given, `vfork_done` is pointed at a specific address.
3. After the child is first run, the parent (instead of returning) waits for the child to signal it through the `vfork_done` pointer.
4. In the `mm_release()` function, which is used when a task exits a memory address space, `vfork_done` is checked to see whether it is NULL. If it is not, the parent is signaled.
5. Back in `do_fork()`, the parent wakes up and returns.

If this all goes as planned, the child is now executing in a new address space, and the parent is again executing in its original address space. The overhead is lower, but the implementation is not pretty.

### The Linux Implementation of Threads

* Threads are a programming abstraction that provide multiple threads of execution within the same program in a shared memory address space.
* Threads can also share open files and other resources.
* Threads enable **concurrent programming** and, on multiple processor systems, true **parallelism**.

Linux has a unique implementation of threads:

* To the Linux kernel, there is no concept of a thread. Linux implements all threads as standard processes.
* The kernel does not provide any special scheduling semantics or data structures to represent threads. Instead, a thread is merely a process that shares certain resources with other processes.
* Each thread has a unique `task_struct` and appears to the kernel as a normal process. Threads just happen to share resources, such as an address space, with other processes.

This approach to threads contrasts greatly with operating systems such as Microsoft Windows or Sun Solaris, which have explicit kernel support for threads (and sometimes call threads lightweight processes). [p34]

#### Creating Threads

Threads are created the same as normal tasks, with the exception that the `clone()` system call is passed flags corresponding to the specific resources to be shared:

```c
clone(CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND, 0);
```

The above code is identical to `fork()` except that the address space (`CLONE_VM`), filesystem resources (`CLONE_FS`), file descriptors (`CLONE_FILES`), and signal handlers (`CLONE_SIGHAND`) are shared.

`fork()` can be implemented as:

```c
clone(SIGCHLD, 0);
```

`vfork()` is implemented as:

```c
clone(CLONE_VFORK | CLONE_VM | SIGCHLD, 0);
```

The flags, which are defined in `<linux/sched.h>` ([include/linux/sched.h#L5](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/sched.h#L5)),  to `clone()` specify the behavior of the new process and detail what resources the parent and child will share.

Flag | Meaning
---- | -------
`CLONE_FILES` | Parent and child share open files.
`CLONE_FS` | Parent and child share filesystem information.
`CLONE_IDLETASK` | Set PID to zero (used only by the idle tasks).
`CLONE_NEWNS` | Create a new namespace for the child.
`CLONE_PARENT` | Child is to have same parent as its parent.
`CLONE_PTRACE` | Continue tracing child.
`CLONE_SETTID` | Write the TID back to user-space.
`CLONE_SETTLS` | Create a new TLS (thread-local storage) for the child.
`CLONE_SIGHAND` | Parent and child share signal handlers and blocked signals.
`CLONE_SYSVSEM` | Parent and child share System V SEM_UNDO semantics.
`CLONE_THREAD` | Parent and child are in the same thread group.
`CLONE_VFORK` | vfork() was used and the parent will sleep until the child wakes it.
`CLONE_UNTRACED` | Do not let the tracing process force CLONE_PTRACE on the child.
`CLONE_STOP` | Start process in the TASK_STOPPED state.
`CLONE_CHILD_CLEARTID` | Clear the TID in the child.
`CLONE_CHILD_SETTID` | Set the TID in the child.
`CLONE_PARENT_SETTID` | Set the TID in the parent.
`CLONE_VM` | Parent and child share address space.

#### Kernel Threads

**Kernel threads** are standard processes that exist solely in kernel-space. They are useful for the kernel to perform some operations in the background.

Difference from normal threads:

* Kernel threads do not have an address space. Their `mm` pointer, which points at their address space, is `NULL`.
* Kernel threads operate only in kernel-space and do not context switch into user-space.

Similarity with normal threads:

* Kernel threads are schedulable and preemptable.

Linux delegates several tasks to kernel threads, most notably the `flush` tasks and the [`ksoftirqd`](ch8.md#ksoftirqd) task. Use `ps -ef` command to see them.

* Kernel threads are created on system boot by other kernel threads.
* A kernel thread can be created only by another kernel thread. The kernel handles this automatically by forking all new kernel threads off of the `kthreadd` kernel process.

The interfaces of kernel threads defined in `<linux/kthread.h>` ([include/linux/kthread.h](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/kthread.h))

`kthread_create()` spawns a new kernel thread from an existing one:

```
struct task_struct *kthread_create(int (*threadfn)(void *data),
                                   void *data,
                                   const char namefmt[],
                                   ...)
```

The new task is created via the `clone()` system call by the `kthread` kernel process:

* The new process will run the `threadfn` function, which is passed the data argument.
* The process will be named `namefmt`, which takes printf-style formatting arguments in the variable argument list.
* The process is created in an unrunnable state; it will not start running until explicitly woken up via `wake_up_process()`.

A process can be created and made runnable with a single function, `kthread_run()`:

```c
struct task_struct *kthread_run(int (*threadfn)(void *data),
                                void *data,
                                const char namefmt[],
                                ...)
```

This routine (`kthread_run()`), implemented as a macro, simply calls both `kthread_create()` and `wake_up_process()`:

```c
#define kthread_run(threadfn, data, namefmt, ...)                 \
({                                                                \
    struct task_struct *k;                                        \
                                                                  \
    k = kthread_create(threadfn, data, namefmt, ## __VA_ARGS__);  \
    if (!IS_ERR(k))                                               \
        wake_up_process(k);                                       \
    k;                                                            \
})
```

When started, a kernel thread continues to exist until it calls `do_exit()` or another part of the kernel calls `kthread_stop()`, passing in the address of the `task_struct` structure returned by `kthread_create()`:

```c
int kthread_stop(struct task_struct *k)
```

### Process Termination

When a process terminates, the kernel releases the resources owned by the process and notifies the child's parent of its demise.

Self-induced process termination occurs when the process calls the `exit()` system call, which is either:

* Explicitly: the process calls `exit()` system call.
* Implicitly: the process return from the main subroutine of any program. The C compiler places a call to `exit()` after `main()` returns.

Involuntary process termination occurs when the process receives a signal or exception it cannot handle or ignore.

Regardless of how a process terminates, the bulk of the work is handled by `do_exit()`, defined in `kernel/exit.c` ([kernel/exit.c#L900](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/exit.c#L900)), which does the following:

1. It sets the `PF_EXITING` flag in the flags member of the `task_struct`.
2. It calls `del_timer_sync()` to remove any kernel timers. Upon return, it is guaranteed that no timer is queued and that no timer handler is running.
3. If BSD process accounting is enabled, `do_exit()` calls `acct_update_integrals()` to write out accounting information.
4. It calls `exit_mm()` to release the `mm_struct` held by this process. If no other process is using this address space (if the address space is not shared) the kernel then destroys it.
5. It calls `exit_sem()`. If the process is queued waiting for an IPC semaphore, it is dequeued here.
6. It then calls `exit_files()` and `exit_fs()` to decrement the usage count of objects related to file descriptors and filesystem data, respectively.
7. It sets the task's exit code (stored in the `exit_code` member of the `task_struct`) to that provided by `exit()` or whatever kernel mechanism forced the termination. <u>The exit code is stored here for optional retrieval by the parent.</u>
8. It send signals and reparents children:
    * Calls `exit_notify()` to send signals to the task's parent
    * Reparents any of the task's children to another thread in their thread group or the init process
    * Sets the task's exit state (stored in `exit_state` in the `task_struct` structure) to `EXIT_ZOMBIE`.
9. It calls `schedule()` to switch to a new process.
    * Because the process is now not schedulable, this is the last code the task will ever execute. `do_exit()` never returns.

At this point:

* All objects associated with the task (assuming the task was the sole user) are freed.
* The task is not runnable (and no longer has an address space in which to run) and is in the `EXIT_ZOMBIE` exit state.
* The only memory it occupies is its kernel stack, the `thread_info` structure, and the `task_struct` structure.
* <u>The task exists solely to provide information to its parent. After the parent retrieves the information, or notifies the kernel that it is uninterested, the remaining memory held by the process is freed and returned to the system for use.</u>

#### Removing the Process Descriptor

After `do_exit()` completes, the process descriptor for the terminated process still exists, but the process is a zombie and is unable to run.

Cleaning up after a process and removing its process descriptor are separate steps. This enables the system to obtain information about a child process after it has terminated.

The terminated child's `task_struct` is deallocated after any of the following:

* The parent has obtained information on its terminated child.
* The parent has signified to the kernel that it does not care (about the terminated child).

The `wait()` family of functions are implemented via a system call `wait4()`.

The standard behavior is to suspend execution of the calling task until one of its children exits, at which time the function returns with the PID of the exited child. On return, a pointer (as an argument to a `wait()` function) holds the exit code of the terminated child. [p38]

`release_task()` is invoked to finally deallocate the process descriptor:

1. It calls `__exit_signal()`, which calls `__unhash_process()`, which in turns calls detach_pid() to remove the process from the pidhash and remove the process from the task list.
2. `__exit_signal()` releases any remaining resources used by the now dead process and finalizes statistics and bookkeeping.
3. If the task was the last member of a thread group, and the leader is a zombie, then `release_task()` notifies the zombie leader's parent.
4. `release_task()` calls `put_task_struct()` to free the pages containing the process's kernel stack and `thread_info` structure and deallocate the slab cache containing the `task_struct`.

At this point, the process descriptor and all resources belonging solely to the process have been freed.

#### The Dilemma of the Parentless Task

<u>If a parent exits before its children, any of its child tasks must be reparented to a new process, otherwise parentless terminated processes would forever remain zombies, wasting system memory.</u>

The solution is to reparent a task's children on exit to another process in the current thread group, or (if that fails) the init process.

`do_exit()` calls `exit_notify()`, which calls `forget_original_parent()`, which calls `find_new_reaper()` to perform the reparenting:

```c
static struct task_struct *find_new_reaper(struct task_struct *father)
{
    struct pid_namespace *pid_ns = task_active_pid_ns(father);
    struct task_struct *thread;

    thread = father;
    while_each_thread(father, thread) {
      if (thread->flags & PF_EXITING)
          continue;
      if (unlikely(pid_ns->child_reaper == father))
          pid_ns->child_reaper = thread;
      return thread;
    }

    if (unlikely(pid_ns->child_reaper == father)) {
        write_unlock_irq(&tasklist_lock);
        if (unlikely(pid_ns == &init_pid_ns))
        panic("Attempted to kill init!");

        zap_pid_ns_processes(pid_ns);
        write_lock_irq(&tasklist_lock);

        /*
        * We can not clear ->child_reaper or leave it alone.
        * There may by stealth EXIT_DEAD tasks on ->children,
        * forget_original_parent() must move them somewhere.
        */
        pid_ns->child_reaper = init_pid_ns.child_reaper;
    }

    return pid_ns->child_reaper;
}
```

The above code attempts to find and return another task in the process's thread group. If another task is not in the thread group, it finds and returns the `init` process.

After a suitable new parent for the children is found, each child needs to be located and reparented to `reaper`:

```c
reaper = find_new_reaper(father);
list_for_each_entry_safe(p, n, &father->children, sibling) {
    p->real_parent = reaper;
    if (p->parent == father) {
        BUG_ON(p->ptrace);
        p->parent = p->real_parent;
    }
    reparent_thread(p, father);
}
```

`ptrace_exit_finish()` is then called to do the same reparenting but to a list of *ptraced* children:

```c
void exit_ptrace(struct task_struct *tracer)
{
    struct task_struct *p, *n;
    LIST_HEAD(ptrace_dead);

    write_lock_irq(&tasklist_lock);
    list_for_each_entry_safe(p, n, &tracer->ptraced, ptrace_entry) {
        if (__ptrace_detach(tracer, p))
        list_add(&p->ptrace_entry, &ptrace_dead);
    }
    write_unlock_irq(&tasklist_lock);

    BUG_ON(!list_empty(&tracer->ptraced));

    list_for_each_entry_safe(p, n, &ptrace_dead, ptrace_entry) {
    list_del_init(&p->ptrace_entry);
    release_task(p);
    }
}

```

When a task is *ptraced*, it is temporarily reparented to the debugging process. When the task's parent exits, however, it must be reparented along with its other siblings. In previous kernels, this resulted in a loop over every process in the system looking for children. The solution is simply to keep a separate list of a process's children being ptraced, reducing the search for one's children from every process to just two relatively small lists

After the process are successfully reparented, there is no risk of stray zombie processes. The `init` process routinely calls `wait()` on its children, cleaning up any zombies assigned to it.

- - -

### Doubts and Solutions

#### Verbatim

> These two routines are provided by the macros `next_task(task)` and `prev_task(task)`, respectively.

I didn't find any relevant appearance for `prev_task` macro in the [Linux 2.6.34.7 source code](https://github.com/shichao-an/linux-2.6.34.7).
