### **Chapter 5. System Calls**

In any modern operating system, the kernel provides a set of interfaces by which processes running in user-space can interact with the system. These interfaces give applications: [p69]

* controlled access to hardware,
* a mechanism with which to create new processes and communicate with existing ones,
* and the capability to request other operating system resources.

The existence of these interfaces, and the fact that applications are not free to directly do whatever they want, is key to providing a stable system

### Communicating with the Kernel

System calls provide a layer between the hardware and user-space processes, which serves three primary purposes:

1. **Providing an abstracted hardware interface for userspace.**
    * For example, when reading or writing from a file, applications are not concerned with the type of disk, media, or even the type of filesystem on which the file resides.
2. **Ensuring system security and stability.** The kernel acts as a middleman between system resources and user-space, so it can arbitrate access based on permissions, users, and other criteria.
    * For example, this arbitration prevents applications from incorrectly using hardware, stealing other processes’ resources, or otherwise doing harm to the system.
3. **A single common layer between user-space and the rest of the system allows for the virtualized system provided to processes.**  It would be impossible to implement multitasking and virtual memory if applications were free to access access system resources without the kernel’s knowledge. [p69]

In Linux, system calls are the only means user-space has of interfacing with the kernel and the only legal entry point into the kernel other than exceptions and traps. Other interfaces, such as device files or `/proc`, are ultimately accessed via system calls. Interestingly, Linux implements far fewer system calls than most systems.

### APIs, POSIX, and the C Library

#### APIs *

Applications are typically programmed against an Application Programming Interface (API) implemented in user-space, not directly to system calls, because no direct correlation is needed between the interfaces used by applications and the actual interface provided by the kernel.

An API defines a set of programming interfaces used by applications. Those interfaces can be:

* implemented as a system call,
* implemented through multiple system calls, or
* implemented without the use of system calls at all.

The same API can exist on multiple systems and provide the same interface to applications while the implementation of the API itself can differ greatly from system to system.

The figure below shows relationship between a POSIX API, the C library, and system calls.

[![Figure 5.1 The relationship between applications, the C library, and the kernel with a call to printf().](figure_5.1_600.png)](figure_5.1.png "Figure 5.1 The relationship between applications, the C library, and the kernel with a call to printf().")

#### POSIX *

The most common APIs in the Unix world is based on POSIX. Technically, POSIX is composed of a series of standards from the [IEEE](https://en.wikipedia.org/wiki/Institute_of_Electrical_and_Electronics_Engineers) that aim to provide a portable operating system standard roughly based on Unix. Linux strives to be POSIX- and SUSv3-compliant where applicable.

On most Unix systems, the POSIX-defined API calls have a strong correlation to the system calls. Some systems that are rather un-Unix, such as Microsoft Windows, offer POSIX-compatible libraries. [p70]

#### The C Library *

The system call interface in Linux, as with most Unix systems, is provided in part by the C library.

The C library implements the main API on Unix systems, including:

* The standard C library
* The system call interface

The C library is used by all C programs and, because of C’s nature, is easily wrapped by other programming languages for use in their programs. The C library additionally provides the majority of the POSIX API.


From the application programmer’s point of view, system calls are irrelevant; all the programmer is concerned with is the API. Conversely, the kernel is concerned only with the system calls; what library calls and applications make use of the system calls is not of the kernel’s concern. Nonetheless, it is important for the kernel to keep track of the potential uses of a system call and keep the system call as general and flexible as possible.

A meme related to interfaces in Unix is "Provide mechanism, not policy". In other words, Unix system calls exist to provide a specific function in an abstract sense. The manner in which the function is used is not any of the kernel’s business.

### Syscalls

**System calls** (often called **syscalls** in Linux) are typically accessed via function calls defined in the C library.

* The functions can define zero, one, or more arguments (inputs) and might result in one or more side effects.
    *  Although nearly all system calls have a side effect (that is, they result in some change of the system’s state), a few syscalls, such as `getpid()`, merely return some data from the kernel.
* System calls also provide a return value of type `long` (for compatibility with 64-bit architectures) that signifies success or error.
    * Usually, although not always, a negative return value denotes an error.
    * A return value of zero is usually (not always) a sign of success.
    * The C library (when a system call returns an error) writes a special error code into the global `errno` variable, which can be translated into human-readable errors via library functions such as `perror()`.
* System calls have a defined behavior. (see the following example)

The system call `getpid()` is defined to return an integer that is the current process’s PID. The implementation of this syscall in the kernel is simple:

```c
SYSCALL_DEFINE0(getpid)
{
    return task_tgid_vnr(current); // returns current->tgid
}
```

The definition says nothing of the implementation. The kernel must provide the intended behavior of the system call but is free to do so with whatever implementation it wants as long as the result is correct. [p72]

`SYSCALL_DEFINE0` is simply a macro that defines a system call with no parameters (hence the 0). The expanded code looks like this:

<small>[include/linux/syscalls.h](https://github.com/shichao-an/linux/blob/v2.6.34/include/linux/syscalls.h##L285)</small>

```c
asmlinkage long sys_getpid(void);
```

* The `asmlinkage` modifier on the function definition is a directive to tell the compiler to look only on the stack for this function’s arguments. This is a required modifier for all system calls.
* The function returns a `long`. For compatibility between 32- and 64-bit systems, system calls defined to return an `int` in user-space return a `long` in the kernel.
* The naming convention taken with all system calls in Linux is: System call `bar()` is implemented in the kernel as function `sys_bar()`.

#### System Call Numbers

In Linux, each system call is assigned a unique **syscall number** that is used to reference a specific system call. When a user-space process executes a system call, the syscall number identifies which syscall was executed; the process does not refer to the syscall by name.

* When assigned, the syscall number cannot change; otherwise, compiled applications will break.
* If a system call is removed, its system call number cannot be recycled, or previously compiled code would aim to invoke one system call but would in reality invoke another.
* Linux provides a "not implemented" system call, `sys_ni_syscall()`, which does nothing except return `ENOSYS`, the error corresponding to an invalid system call. This function is used to "plug the hole" in the rare event that a syscall is removed or otherwise made unavailable.

The kernel keeps a list of all registered system calls in the system call table, stored in `sys_call_table`, on x86-64 it is defined in [arch/x86/kernel/syscall_64.c](https://github.com/shichao-an/linux/blob/v2.6.34/arch/x86/kernel/syscall_64.c).

The system call numbers are defined in the file [include/asm-generic/unistd.h](https://github.com/shichao-an/linux/blob/v2.6.34/include/asm-generic/unistd.h).

#### System Call Performance

System calls in Linux are faster than in many other operating systems, because of:

* Linux’s fast context switch times: entering and exiting the kernel is a streamlined and simple affair
* Simplicity of the system call handler and the individual system calls themselves

### System Call Handler

It is not possible for user-space applications to execute kernel code directly. They cannot simply make a function call to a method existing in kernel-space because the kernel exists in a protected memory space. Otherwise, system security and stability would be nonexistent.

User-space applications signal the kernel that they want to execute a system call and have the system switch to kernel mode, where the system call can be executed in kernel-space by the kernel on behalf of the application. This mechanism is software interrupt: incur an exception, and the system will switch to kernel mode and execute the **exception handler**. The exception handler in this case is actually the **system call handler**.

The defined software interrupt on x86 is interrupt number 128, which is incurred via the `int $0x80` instruction. It triggers a switch to kernel mode and the execution of exception vector 128, which is the system call handler. The system call handler is the aptly named function `system_call()`. It is architecture-dependent; on x86-64 it is implemented in assembly in `entry_64.S` ([arch/x86/kernel/entry_64.S](https://github.com/shichao-an/linux/blob/v2.6.34/arch/x86/kernel/entry_64.S)).

Recently, x86 processors added a feature known as *sysenter*, which provides a faster, more specialized way of trapping into a kernel to execute a system call than using the `int` interrupt instruction. Support for this feature was quickly added to the kernel. Regardless of how the system call handler is invoked, however, the important notion is that somehow user-space causes an exception or trap to enter the kernel.

#### Denoting the Correct System Call

For more details of Linux system call from the assembly perspective, see [Interfacing with Linux](../asm/index.md#interfacing-with-linux-system-calls).

Simply entering kernel-space alone is not sufficient: the system call number must be passed into the kernel.

On x86, the syscall number is passed to the kernel via the `eax` register.
