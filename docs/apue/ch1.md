### **Chapter 1. UNIX System Overview**

### Introduction

This chapter gives basic Unix system concepts that are familiar to system administrators, from a programmer's perspective.

### UNIX Architecture

An operating system can be defined as the software that controls the hardware resources of the computer and provides an environment under which programs can run. This software is generally called the **kernel**, since it is relatively small and resides at the core of the environment. The figure below shows a diagram of the UNIX System architecture.

[![Figure 1.1 Architecture of the UNIX operating system](figure_1.1.png)](figure_1.1.png "Figure 1.1 Architecture of the UNIX operating system")

* The interface to the kernel is a layer of software called the **system calls**.
* Libraries of common functions are built on top of the system call interface, but applications are free to use both.
* The shell is a special application that provides an interface for running other applications.

Linux is the kernel used by the GNU operating system. Some people refer to this combination as the GNU/Linux operating system, but it is more commonly referred to as simply Linux. Although this usage may not be correct in a strict sense, it is understandable, given the dual meaning of the phrase *operating system*.

### Logging In

#### Shells

A **shell** is a command-line interpreter that reads user input and executes commands. The user input to a shell is normally from the terminal (an interactive shell) or sometimes from a file (called a **shell script**).

### Files and Directories

#### File system

The UNIX file system is a hierarchical arrangement of directories and files. Everything starts in the directory called root, whose name is the single character `/`.

#### Filename

The names in a directory are called filenames. The only two characters that cannot appear in a filename are the slash character (/) and the null character. The slash separates the filenames that form a pathname (described next) and the null character terminates a pathname. For portability, POSIX.1 recommends restricting filenames to consist of the following characters: letters (`a-z`, `A-Z`), numbers (`0-9`), period (`.`), dash (`-`), and underscore (`_`).

#### Pathname

A sequence of one or more filenames, separated by slashes and optionally starting with a slash, forms a **pathname**. A pathname that begins with a slash is called an **absolute pathname**; otherwise, it’s called a **relative pathname**.

#### Working Directory

Every process has a working directory, sometimes called the **current working directory**. This is the directory from which all relative pathnames are interpreted. A process can change its working directory with the `chdir` function.

#### Home Directory

The working directory is set to our home directory, which is obtained from our entry in the password file.

### Input and Output

#### File Descriptors

File descriptors are normally small non-negative integers that the kernel uses to identify the files accessed by a process. Whenever it opens an existing file or creates a new file, the kernel returns a file descriptor that we use when we want to read or write the file

#### Standard Input, Standard Output, and Standard Error

By convention, all shells open three descriptors whenever a new program is run: standard input, standard output, and standard error.

### Programs and Processes

#### Program

A **program** is an executable file residing on disk in a directory.

#### Processes and Process ID

An executing instance of a program is called a **process**.

The UNIX System guarantees that every process has a unique numeric identifier called the **process ID**. The process ID is always a non-negative integer.

#### Process Control
#### Threads and Thread IDs

Threads are identified by IDs. Thread IDs are local to a process. A thread ID from one process has no meaning in another process. We use thread IDs to refer to specific threads as we manipulate the threads within a process.

### Error Handling

When an error occurs in one of the UNIX System functions, a negative value is often returned, and the integer `errno` is usually set to a value that tells why.  Some functions use a convention other than returning a negative value. For example:

* The `open` function returns either a non-negative file descriptor if all is OK or −1 if an error occurs.
* Most functions that return a pointer to an object return a null pointer to indicate an error.

The file `<errno.h>` defines the symbol errno and constants for each value that errno can assume. Each of these constants begins with the character `E`. On Linux, the error constants are listed in the [errno(3)](http://man7.org/linux/man-pages/man3/errno.3.html) manual page

POSIX and ISO C define `errno` as a symbol expanding into a modifiable lvalue of type integer. This can be either an integer that contains the error number or a function that returns a pointer to the error number. The historical definition is:

```c
extern int errno;
```

But in an environment that supports threads, the process address space is shared among multiple threads, and each thread needs its own local copy of errno to prevent one thread from interfering with another. Linux supports multithreaded access to `errno` by defining it as:

```c
extern int *_ _errno_location(void);
#define errno (*_ _errno_location())
```

There are two rules to be aware of with respect to `errno`:

1. The value of `errno` is never cleared by a routine if an error does not occur. Therefore, we should examine its value only when the return value from a function indicates that an error occurred.
2. The value of `errno` is never set to 0 by any of the functions, and none of the constants defined in `<errno.h>` has a value of 0.

The following functions are defined by the C standard to help with printing error messages.

The `strerror` function maps errnum, which is typically the `errno` value, into an error message string and returns a pointer to the string.

```c
#include <string.h>

char *strerror(int errnum);

/* Returns: pointer to message string */
```

The `perror` function produces an error message on the standard error, based on the current value of `errno`, and returns. It outputs the string pointed to by msg, followed by a colon and a space, followed by the error message corresponding to the value of `errno`, followed by a newline.

```c
#include <stdio.h>

void perror(const char *msg);
```

The following code shows the use of these two error functions.

```c
#include "apue.h"
#include <errno.h>

int
main(int argc, char *argv[])
{
      fprintf(stderr, "EACCES: %s\n", strerror(EACCES));
      errno = ENOENT;
      perror(argv[0]);
      exit(0);
}
```

If this program is compiled into the file `a.out`, we have:

```shell-session
$ ./a.out
EACCES: Permission denied
./a.out: No such file or directory
```

### User Identification

### Signals

### Time Values

### System Calls and Library Functions

* Linux 3.2.0 has 380 system calls and FreeBSD 8.0 has over 450
* Each system call has a function of the same name in the standard C library
* An application can either make a system call or call a library routine
