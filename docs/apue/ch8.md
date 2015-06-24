### **Chapter 8. Process Control**

### Process Identifiers

Every process has a unique process ID, a non-negative integer. As processes terminate, their IDs can be reused. <u>Most UNIX systems implement algorithms to delay reuse so that newly created processes are assigned IDs different from those used by processes that terminated recently. This prevents a new process from being mistaken for the previous process to have used the same ID.</u>

There are some special processes, but the details differ from implementation to implementation:

* Process ID 0: scheduler process (often known as the **swapper**), which is part of the kernel and is known as a system process
* Process ID 1: `init` process, invoked by the kernel at the end of the bootstrap procedure.
    * It is responsible for bringing up a UNIX system after the kernel has been bootstrapped. `init` usually reads the system-dependent initialization files (`/etc/rc*` files or `/etc/inittab` and the files in `/etc/init.d`) and brings the system to a certain state.
    * It never dies.
    * It is a normal user process, not a system process within the kernel.
    * It runs with superuser privileges.

<u>Each UNIX System implementation has its own set of kernel processes that provide operating system services.</u> For example, on some virtual memory implementations of the UNIX System, process ID 2 is the *pagedaemon*. This process is responsible for supporting the paging of the virtual memory system.

<script src="https://gist.github.com/shichao-an/4afacfab973219fb4721.js"></script>

None of these functions has an error return.

### `fork` Function

An existing process can create a new one by calling the `fork` function.

<script src="https://gist.github.com/shichao-an/1d1bfd83197d3c929164.js"></script>

* The new process created by `fork` is called the **child process**. This function is called once but returns twice. The only difference in the returns is that the return value in the child is 0, whereas the return value in the parent is the process ID of the new child. [p299]
    * `fork` returns child's process ID in parent: a process can have more than one child, and <u>there is no function that allows a process to obtain the process IDs of its children</u>
    * `fork` returns 0 in child: <u>a process can have only a single parent, and the child can always call `getppid` to obtain the process ID of its parent</u>
* Both the child and the parent continue executing with the instruction that follows the call to `fork`. The child is a copy of the parent; the parent and the child do not share these portions of memory. The parent and the child do share the text segment.
* Copy-on-write (COW) is used on modern implementations: a complete copy of the parent’s data, stack and heap is not performed. The shared regions are changed to read-only by the kernel. The kernel makes a copy of that piece of memory only if either process tries to modify these regions.

Variations of the `fork` function are provided by some platforms. All four platforms discussed in this book support the `vfork(2)` variant discussed in the next section. Linux 3.2.0 also provides new process creation through the `clone(2)` system call. This is a generalized form of `fork` that allows the caller to control what is shared between parent and child.

Example ([fork1.c](https://github.com/shichao-an/apue.3e/blob/master/proc/fork1.c)):

```c
#include "apue.h"

int globvar = 6; /* external variable in initialized data */
char buf[] = "a write to stdout\n";

int
main(void)
{
    int var; /* automatic variable on the stack */
    pid_t pid;

    var = 88;
    if (write(STDOUT_FILENO, buf, sizeof(buf)-1) != sizeof(buf)-1)
        err_sys("write error");
    printf("before fork\n"); /* we don’t flush stdout */

    if ((pid = fork()) < 0) {
        err_sys("fork error");
    } else if (pid == 0) { /* child */
        globvar++; /* modify variables */
        var++;
    } else {
        sleep(2); /* parent */
    }

    printf("pid = %ld, glob = %d, var = %d\n", (long)getpid(), globvar,
           var);
    exit(0);
}
```

```text
$ ./a.out
a write to stdout
before fork
pid = 430, glob = 7, var = 89 # child’s variables were changed
pid = 429, glob = 6, var = 88 # parent’s copy was not changed
$ ./a.out > temp.out
$ cat temp.out
a write to stdout
before fork
pid = 432, glob = 7, var = 89
before fork
pid = 431, glob = 6, var = 88
```

Analysis:

* Whether the child starts executing before the parent or vice versa is not known. The order depends on the scheduling algorithm used by the kernel. If it’s required that the child and parent synchronize their actions, some form of interprocess communication is required.
* `sizeof(buf)-1` (subtracting 1 from the size of `buf`) avoids writing the terminating null byte. `strlen` calculates the length of a string not including the terminating null byte, while `sizeof` calculates the size of the buffer, including the terminating null byte. However, using `strlen` requires a function call, whereas `sizeof` calculates the buffer length at compile time.
* "a write to stdout" (once): `write` function is not buffered and is called before the `fork`, its data is written once to standard output
* "before fork" (once in the first case, twice in the second case): <u>`printf` from the standard I/O library is buffered</u>
    * First case (running the program interactively): standard I/O is <u>line buffered</u> and standard output buffer is flushed by the newline
    * Second case (redirect stdout to a file): standard I/O is <u>fully buffered</u>. The `printf` (`printf("before fork\n");`) before the `fork` is called once, but the line remains in the buffer when `fork` is called. <u>This buffer is then copied into the child when the parent’s data space is copied to the child. Both the parent and the child now have a standard I/O buffer with this line in it.</u> The second `printf` (`printf("pid = %ld, glob = %d, var = %d\n", ...);`), right before the exit, just appends its data to the existing buffer. When each process terminates, its copy of the buffer is finally flushed.

#### File Sharing

One characteristic of `fork` is that all file descriptors that are open in the parent are duplicated in the child, because it’s as if the `dup` function had been called for each descriptor. The parent and the child shareafile table entry for every open descriptor.

For a process that has three different files opened for standard input, standard output, and standard error, on return from `fork`, we have the arrangement shown below:

[![Figure 8.2 Sharing of open files between parent and child after fork](figure_8.2_600.png)](figure_8.2.png "Figure 8.2 Sharing of open files between parent and child after fork")

It is important that the parent and the child share the same file offset. Otherwise, this type of interaction would be more difficult to accomplish and would require explicit actions by the parent.

There are two normal cases for handling the descriptors after a `fork`:

1. The parent waits for the child to complete.
2. Both the parent and the child go their own ways. After the fork, both the parent and child close the descriptors that they don't need, so neither interferes with the other’s open descriptors. This scenario is often found with network servers.

Besides the open files, other properties of the parent are inherited by the child:

* Real user ID, real group ID, effective user ID, and effective group ID
* Supplementary group IDs
* Process group ID
* Session ID
* Controlling terminal
* The set-user-ID and set-group-ID flags
* Current working directory
* Root directory
* File mode creation mask
* Signal mask and dispositions
* The close-on-exec flag for any open file descriptors
* Environment
* Attached shared memory segments
* Memory mappings
* Resource limits

The differences between the parent and child are:

* The return values from fork are different.
* The process IDs are different.
* The two processes have different parent process IDs: the parent process ID of the child is the parent; the parent process ID of the parent doesn’t change.
* The child’s `tms_utime`, `tms_stime`, `tms_cutime`, and `tms_cstime` values are set to 0 (these times are discussed in Section 8.17).
* File locks set by the parent are not inherited by the child.
* Pending alarms are cleared for the child.
* The set of pending signals for the child is set to the empty set

#### The two main reasons for `fork` to fail

1. If too many processes are already in the system, which usually means that something else is wrong
2. If the total number of processes for this real user ID exceeds the system’s limit. (`CHILD_MAX` specifies the maximum number of simultaneous processes per real user ID.)

#### The two uses for `fork`

1. When a process wants to duplicate itself so that the parent and the child can each execute different sections of code at the same time.
    * This is common for network servers—the parent waits for a service request from a client. When the request arrives, the parent calls `fork` and lets the child handle the request. The parent goes back to waiting for the next service request to arrive.
2. When a process wants to execute a different program.
    * This is common for shells. In this case, the child does an `exec` right after it returns from the `fork`.

Some operating systems combine the operations from step 2, a `fork` followed by an `exec`, into a single operation called a `spawn`. The UNIX System separates the two, as there are numerous cases where it is useful to `fork` without doing an `exec`. Also, separating the two operations allows the child to change the per-process attributes between the `fork` and the `exec`, such as I/O redirection, user ID, signal disposition, and so on

### `vfork` Function

The function `vfork` has the same calling sequence and same return values as `fork`, but the semantics of the two functions differ.

The `vfork` function was intended to create a new process for the purpose of executing a new program (step 2 at the end of the previous section). <u>The `vfork` function creates the new process, just like `fork`, without copying the address space of the parent into the child</u>, as the child won’t reference that address space; the child simply calls `exec` (or `exit`) right after the `vfork`. Instead, <u>the child runs in the address space of the parent until it calls either `exec` or `exit`.</u>

This optimization is more efficient on some implementations of the UNIX System, but leads to undefined results if the child:

* modifies any data (except the variable used to hold the return value from `vfork`)
* makes function calls
* returns without calling `exec` or `exit`

Another difference between the two functions is that `vfork` guarantees that the child runs first, until the child calls `exec` or `exit`. When the child calls either of these functions, the parent resumes. (This can lead to deadlock if the child depends on further actions of the parent before calling either of these two functions.)


Example ([vfork1.c](https://github.com/shichao-an/apue.3e/blob/master/proc/vfork1.c))

The program is a modified version of the program from [fork1.c](https://github.com/shichao-an/apue.3e/blob/master/proc/fork1.c). We’ve replaced the call to `fork` with `vfork` and removed the write to standard output. Also, we don’t need to have the parent call `sleep`, as we’re guaranteed that it is put to sleep by the kernel until the child calls either `exec` or `exit`.

```c
#include "apue.h"

int globvar = 6; /* external variable in initialized data */

int
main(void)
{
    int var; /* automatic variable on the stack */
    pid_t pid;

    var = 88;
    printf("before vfork\n"); /* we don’t flush stdio */
    if ((pid = vfork()) < 0) {
        err_sys("vfork error");
    } else if (pid == 0) { /* child */
        globvar++; /* modify parent’s variables */
        var++;
        _exit(0); /* child terminates */
    }

    /* parent continues here */
    printf("pid = %ld, glob = %d, var = %d\n", (long)getpid(), globvar,
           var);
    exit(0);
}
```
Running this program gives us

```text
$ ./a.out
before vfork
pid = 29039, glob = 7, var = 89
```

Analysis:

* The incrementing of the variables done by the child changes the values in the parent. Because the child runs in the address space of the parent.
* `_exit` is called instead of `exit`, because `_exit` does not perform any flushing of standard I/O buffers. If we call `exit` instead, the results are indeterminate. Depending on the implementation of the standard I/O library, we might see no difference in the output, or we might find that the output from the <u>first `printf`</u> (see [Doubts and Solutions](#doubts-and-solutions)) in the parent has disappeared.
    * If the implementation only flushes the standard I/O streams, then we will see no difference from the output generated if the child called `_exit`.
    * If the implementation also closes the standard I/O streams, however, the memory representing the `FILE` object for the standard output will be cleared out. Because the child is borrowing the parent’s address space, when the parent resumes and calls `printf`, no output will appear and `printf` will return −1.
    * The parent’s `STDOUT_FILENO` is still valid, as the child gets a copy of the parent’s file descriptor array


Most modern implementations of `exit` do not close the streams. Because the process is about to exit, the kernel will close all the file descriptors open in the process. Closing them in the library simply adds overhead without any benefit.

### `exit` Functions

A process can terminate normally in five ways (as described in [Section 7.3](ch7/#process-termination)):

1. Executing a return from the `main` function. This is equivalent to calling `exit`.
2. Calling the exit function, which includes the calling of all exit handlers that have been registered by calling `atexit` and closing all standard I/O streams. 
    * ISO C does not deal with file descriptors, multiple processes (parents and children), and job control. The definition of this function is incomplete for a UNIX system.
3. Calling the `_exit` or `_Exit` function.
    * `_Exit`: defined by ISO C to provide a way for a process to terminate without running exit handlers or signal handlers
    * `_exit`: called by `exit` and handles the UNIX system-specific details; `_exit` is specified by POSIX.1.
    * Whether standard I/O streams are flushed depends on the implementation.
    * On UNIX systems, `_Exit` and `_exit` are synonymous and do not flush standard I/O streams.
4. Executing a `return` from the start routine of the last thread in the process.
    * The return value of the thread is not used as the return value of the process. When the last thread returns from its start routine, the process exits with a termination status of 0.
5. Calling the `pthread_exit` function from the last thread in the process.

The three forms of abnormal termination:

1. Calling `abort`. This is a special case of the next item, as it generates the `SIGABRT` signal.
2. When the process receives certain signals. The signal can be generated by:
    * the process itself, e.g. calling the `abort` function
    * some other processes
    * the kernel, e.g. the process references a memory location not within its address space or tries to divide by 0
3. The last thread responds to a cancellation request. By default, cancellation occurs in a deferred manner: one thread requests that another be canceled, and sometime later the target thread terminates.

Regardless of how a process terminates, the same code in the kernel is eventually executed. This kernel code closes all the open descriptors for the process, releases the memory that it was using, and so on.

The terminating process is to be able to notify its parent how it terminated by by passing an exit status as the argument to one of the three exit functions. In the case of an abnormal termination, the kernel (not the process) generates a termination status to indicate the reason for the abnormal termination. In any case, the parent of the process can obtain the termination status from either the `wait` or the `waitpid` function.

#### Exit status vs. termination status

* **Exit status**: is the argument to one of the three exit functions or the return value from main.
* **Termination status**: the exit status is converted into a termination status by the kernel when `_exit` is finally called. If the child terminated normally, the parent can obtain the exit status of the child.


#### Orphan process

**Orphan process** (or **orphaned child process**) is any process whose parent terminates.

The child has a parent process after the call to `fork`. What happens if the parent terminates before the child? The answer is the `init` process becomes the parent process of any process whose parent terminates. This is called "the process has been inherited by `init`". Whenever a process terminates, the kernel goes through all active processes to see whether the terminating process is the parent of any process that still exists. If so, the parent process ID of the surviving process is changed to be 1 (the process ID of `init`). This way, it's guaranteed that every process has a parent.

#### Zombie process

**Zombie process** is a process that has terminated, but whose parent has not yet waited for it. The `ps(1)` command prints the state of a zombie process
as *Z*.

What happens when a child terminates before its parent?

If the child completely disappeared, the parent wouldn’t be able to fetch its termination status when and if the parent was finally ready to check if the child had terminated. The kernel keeps a small amount of information for every terminating process, so that the information is available when the parent of the terminating process calls `wait` or `waitpid`. This information consists of the process ID, the termination status of the process, and the amount of CPU time taken by the process. The kernel can discard all the memory used by the process and close its open files.

#### `init`'s children

What happens when a process that has been inherited by `init` terminates? It does not become a zombie. `init` is written so that whenever one of its children terminates, `init` calls one of the `wait` functions to fetch the termination status. By doing this, init prevents the system from being clogged by zombies.

One of init’s children refers to either of the following:

* A process that `init` generates directly (e.g. `getty`)
* A process whose parent has terminated and has been subsequently inherited by `init`.


### `wait` and `waitpid` Functions
<u>When a process terminates, either normally or abnormally, the kernel notifies the parent by sending the `SIGCHLD` signal to the parent.</u> Because the termination of a child is an asynchronous event (it can happen at any time while the parent is running). This signal is the asynchronous notification from the kernel to the parent. The parent can choose to ignore this signal, or it can provide a function that is called when the signal occurs: a signal handler. <u>The default action for this signal is to be ignored.</u>

A process that calls `wait` or `waitpid` can:

* Block, if all of its children are still running
* Return immediately with the termination status of a child, if a child has terminated and is waiting for its termination status to be fetched
* Return immediately with an error, if it doesn’t have any child processes

If the process is calling `wait` because it received the `SIGCHLD` signal, we expect wait to return immediately. But if we call it at any random point in time, it can block.

<script src="https://gist.github.com/shichao-an/8eef8437e6dd5a045c18.js"></script>

The differences between these two functions are:

* The `wait` function can block the caller until a child process terminates, whereas `waitpid` has an option that prevents it from blocking.
* The `waitpid` function doesn’t wait for the child that terminates first; it has a number of options that control which process it waits for.

If a child has already terminated and is a zombie, `wait` returns immediately with that child’s status. Otherwise, it blocks the caller until a child terminates. If the caller blocks and has multiple children, `wait` returns when one terminates. We can always tell which child terminated, because the process ID is returned by the function.

The argument `statloc` is is a pointer to an integer. If this argument is not a null pointer, the termination status of the terminated process is stored in the location pointed to by the argument.

The integer status that these two functions return has been defined by the implementation, with certain bits indicating the exit status (for a normal return), other bits indicating the signal number (for an abnormal return), one bit indicating whether a core file was generated, and so on.

Four mutually exclusive macros are defined in `<sys/wait.h>` to tell us how the process terminated, and they all begin with `WIF`. Based on which of these four macros is true, other macros are used to obtain the exit status, signal number, and the like.

Macros to examine the termination status returned by `wait` and `waitpid`:

Macro | Description
----- | -----------
`WIFEXITED(status)` | True if status was returned for a child that terminated normally. In this case, we can execute `WEXITSTATUS(status)` to fetch the low-order 8 bits of the argument that the child passed to `exit`, `_exit`, or `_Exit`.
`WIFSIGNALED(status)` | True if status was returned for a child that terminated abnormally, by receipt of a signal that it didn’t catch. In this case, we can execute `WTERMSIG(status)` to fetch the signal number that caused the termination. Additionally, some implementations (but not the Single UNIX Specification) define the macro `WCOREDUMP(status)` that returns true if a core file of the terminated process was generated.
`WIFSTOPPED(status)` | True if status was returned for a child that is currently stopped. In this case, we can execute `WSTOPSIG(status)` to fetch the signal number that caused the child to stop.
`WIFCONTINUED(status)` | True if status was returned for a child that has been continued after a job control stop (XSI option; `waitpid` only).

The function `pr_exit` uses these macros (above) to print a description of the termination status.

* [lib/prexit.c](https://github.com/shichao-an/apue.3e/blob/master/lib/prexit.c)

```c
#include "apue.h"
#include <sys/wait.h>

void
pr_exit(int status)
{
	if (WIFEXITED(status))
		printf("normal termination, exit status = %d\n",
				WEXITSTATUS(status));
	else if (WIFSIGNALED(status))
		printf("abnormal termination, signal number = %d%s\n",
				WTERMSIG(status),
#ifdef	WCOREDUMP
				WCOREDUMP(status) ? " (core file generated)" : "");
#else
				"");
#endif
	else if (WIFSTOPPED(status))
		printf("child stopped, signal number = %d\n",
				WSTOPSIG(status));
}
```

* [wait1.c](https://github.com/shichao-an/apue.3e/blob/master/proc/wait1.c)

```c
#include "apue.h"
#include <sys/wait.h>

int
main(void)
{
	pid_t	pid;
	int		status;

	if ((pid = fork()) < 0)
		err_sys("fork error");
	else if (pid == 0)				/* child */
		exit(7);

	if (wait(&status) != pid)		/* wait for child */
		err_sys("wait error");
	pr_exit(status);				/* and print its status */

	if ((pid = fork()) < 0)
		err_sys("fork error");
	else if (pid == 0)				/* child */
		abort();					/* generates SIGABRT */

	if (wait(&status) != pid)		/* wait for child */
		err_sys("wait error");
	pr_exit(status);				/* and print its status */

	if ((pid = fork()) < 0)
		err_sys("fork error");
	else if (pid == 0)				/* child */
		status /= 0;				/* divide by 0 generates SIGFPE */

	if (wait(&status) != pid)		/* wait for child */
		err_sys("wait error");
	pr_exit(status);				/* and print its status */

	exit(0);
}
```

Results:

```text
$ ./a.out
normal termination, exit status = 7
abnormal termination, signal number = 6 (core file generated)
abnormal termination, signal number = 8 (core file generated)
```

We print the signal number from `WTERMSIG`. We can look at the `<signal.h>` header to verify that `SIGABRT` has a value of 6 and that `SIGFPE` has a value of 8.


#### `wait` for a specific process: `waitpid`

If we have more than one child, `wait` returns on termination of any of the children. If we want to wait for a specific process to terminate (assuming we know which process ID we want to wait for), in older versions of the UNIX System, we would have to call `wait` and compare the returned process ID with the one we’re interested in. The POSIX.1 `waitpid` function can be used to wait for a specific process.

The interpretation of the pid argument for waitpid depends on its value:

* *pid* == −1 - Waits for any child process. In this respect, `waitpid` is equivalent to `wait`.
* *pid* > 0 - Waits for the child whose process ID equals *pid*.
* *pid* == 0 - Waits for any child whose **process group ID** equals that of the calling process.
* *pid* < −1 - Waits for any child whose process group ID equals the absolute value of *pid*.

The `waitpid` function returns the process ID of the child that terminated and stores the child’s termination status in the memory location pointed to by *statloc*. 

##### Errors of `wait` and `waitpid`

* With `wait`, the only real error is if the calling process has no children. (Another error return is possible, in case the function call is interrupted by a signal) [p242]
* With `waitpid`, it’s possible to get an error if the specified process or process group does not exist or is not a child of the calling process

##### *options* argument of `waitpid`

The *options* argument either is 0 or is constructed from the bitwise OR of the constants in the table below.

The *options* constants for `waitpid`:

Constant | Description
-------- | -----------
`WCONTINUED` |  If the implementation supports job control, the status of any child specified by *pid* that has been continued after being stopped, but whose status has not yet been reported, is returned (XSI option).
`WNOHANG` | The `waitpid` function will not block if a child specified by *pid* is not immediately available. In this case, the return value is 0.
`WUNTRACED` | If the implementation supports job control, the status of any child specified by *pid* that has stopped, and whose status has not been reported since it has stopped, is returned. The `WIFSTOPPED` macro determines whether the return value corresponds to a stopped child process.

The `waitpid` function provides three features that aren’t provided by the `wait` function:

1. The `waitpid` function lets us wait for one particular process, whereas the `wait` function returns the status of any terminated child (`popen` function)
2. The `waitpid` function provides a nonblocking version of `wait`. There are times when we want to fetch a child’s status, but we don’t want to block.
3. The `waitpid` function provides support for job control with the `WUNTRACED` and `WCONTINUED` options.

Example ([fork2.c](https://github.com/shichao-an/apue.3e/blob/master/proc/fork2.c))

If we want to write a process so that it `fork`s a child but we don’t want to wait for the child to complete and we don’t want the child to become a zombie until we terminate, <u>the trick is to call fork twice.</u>

```c
#include "apue.h"
#include <sys/wait.h>

int
main(void)
{
	pid_t	pid;

	if ((pid = fork()) < 0) {
		err_sys("fork error");
	} else if (pid == 0) {		/* first child */
		if ((pid = fork()) < 0)
			err_sys("fork error");
		else if (pid > 0)
			exit(0);	/* parent from second fork == first child */

		/*
		 * We're the second child; our parent becomes init as soon
		 * as our real parent calls exit() in the statement above.
		 * Here's where we'd continue executing, knowing that when
		 * we're done, init will reap our status.
		 */
		sleep(2);
		printf("second child, parent pid = %ld\n", (long)getppid());
		exit(0);
	}

	if (waitpid(pid, NULL, 0) != pid)	/* wait for first child */
		err_sys("waitpid error");

	/*
	 * We're the parent (the original process); we continue executing,
	 * knowing that we're not the parent of the second child.
	 */
	exit(0);
}
```

Results:

```text
$ ./a.out
$ second child, parent pid = 1
```

Analysis:

We call `sleep` in the second child to ensure that the first child terminates before printing the parent process ID. After a `fork`, either the parent or the child can continue executing; we never know which will resume execution first. If we didn’t put the second child to sleep, and if it resumed execution after the `fork` before its parent, the parent process ID that it printed would be that of its parent, not process ID 1.

<u>Note that the shell prints its prompt when the original process terminates, which is before the second child prints its parent process ID.</u>

### `waitid` Function

The Single UNIX Specification includes an additional `waitid` function to retrieve the exit status of a process.

<script src="https://gist.github.com/shichao-an/30873cd97704d1465d3f.js"></script>

Like `waitpid`, `waitid` allows a process to specify which children to wait for. Instead of encoding this information in a single argument combined with the process ID or process group ID, two separate arguments are used. The `id` parameter is interpreted based on the value of *idtype*.

* The *idtype* constants for `waitid`:

    Constant | Description
    -------- | -----------
    `P_PID` | Wait for a particular process: *id* contains the process ID of the child to wait for.
    `P_PGID` | Wait for any child process in a particular process group: *id* contains the process group ID of the children to wait for.
    `P_ALL` | Wait for any child process: *id* is ignored.

* The *options* argument is a bitwise OR of the flags shown below:

    Constant | Description
    -------- | -----------
    `WCONTINUED` | Wait for a process that has previously stopped and has been continued, and whose status has not yet been reported.
    `WEXITED` | Wait for processes that have exited.
    `WNOHANG` | Return immediately instead of blocking if there is no child exit status available.
    `WNOWAIT` | Don’t destroy the child exit status. The child’s exit status can be retrieved by a subsequent call to `wait`, `waitid`, or `waitpid`.
    `WSTOPPED` | Wait for a process that has stopped and whose status has not yet been reported.

    At least one of `WCONTINUED`, `WEXITED`, or `WSTOPPED` must be specified in the options argument.

* The *infop* argument is a pointer to a `siginfo` structure. This structure contains detailed information about the signal generated that caused the state change in the child process. (Section 10.14)











### Doubts and Solutions
#### Verbatim

p235 on `vfork`
> If we call `exit` instead, the results are indeterminate. Depending on the implementation of the standard I/O library, we might see no difference in the output, or we might find that the output from the first `printf` in the parent has disappeared.

I think "first `printf`" should be "second `printf`", because the output of the first `printf` is flushed. For the second `printf`, it says "no output will appear and `printf` will return −1".
