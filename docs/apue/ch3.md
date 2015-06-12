### **Chapter 3. File I/O**

This chapter discusses unbuffered I/O, which are not part of ISO C but are part of POSIX.1 and the Single UNIX Specification.

### File Descriptors

* All open files are referred to by file descriptors
* Non-negative integer
* Range from 0 to `OPEN_MAX - 1`. With FreeBSD 8.0, Linux 3.2.0, Mac OS X 10.6.8, and Solaris 10, the limit is essentially infinite, bounded by the amount of memory on the system, the size of an integer, and any hard and soft limits configured by the system administrator.

### `open` and `openat` Functions

<script src="https://gist.github.com/shichao-an/84b85f42bf03c30fa75b.js"></script>

`oflag` argument is formed by ORing one or more of the following constants from `<fcntl.h>` [p62]:

Required:

* `O_RDONLY`
* `O_WRONLY`
* `O_RDWR`
* `O_EXEC`
* `O_SEARCH`: Open for search only (applies to directories).

Optional:

* `O_APPEND`
* `O_CLOEXEC`: Set the [`FD_CLOEXEC`](https://www.gnu.org/software/libc/manual/html_node/Descriptor-Flags.html) file descriptor flag
* `O_CREAT`: Create the file if it doesn’t exist
* `O_DIRECTORY`: Generate an error if `O_CREAT` is also specified and the file already exists. This test for whether the file already exists and the creation of the file if it doesn’t exist is an atomic operation
* `O_EXCL`
* `O_NOCTTY`
* `O_NOFOLLOW`
* `O_NONBLOCK`
* `O_SYNC`: Have each `write` wait for physical I/O to complete
* `O_TRUNC`
* `O_TTY_INIT`
* `O_DSYNC`
* `O_RSYNC`

#### TOCTTOU
`openat`, for example, provides a way to avoid [time-of-check-to-time-of-use](http://en.wikipedia.org/wiki/Time_of_check_to_time_of_use) (TOCTTOU) errors. A program is vulnerable if it makes two file-based function calls where the second call depends on the results of the first call (two calls are not atomic).

### Filename and Pathname Truncation

Most modern file systems support a maximum of 255 characters for filenames.


### `creat` Function

<script src="https://gist.github.com/shichao-an/e0ac0fe91b023280e33f.js"></script>

This function is equivalent to:

```c
open(path, O_WRONLY | O_CREAT | O_TRUNC, mode);
```

With `creat`, the file is opened only for writing. To read and write a file, use [p66]:

```c
open(path, O_RDWR | O_CREAT | O_TRUNC, mode);
```

### `close` Function

<script src="https://gist.github.com/shichao-an/84758a089b6cb82b7495.js"></script>

When a process terminates, all of its open files are closed automatically by the kernel. Many programs take advantage of this fact and don’t explicitly close open files.


### `lseek` Function

Every open file has a "current file offset", normally a non-negative integer that measures the number of bytes from the beginning of the file.

<script src="https://gist.github.com/shichao-an/b9b0bc7d6dca91b7afd6.js"></script>

The *whence* argument can be:

* `SEEK_SET`: the file’s offset is set to *offset* bytes from the beginning of the file
* `SEEK_CUR`: the file’s offset is set to its current value plus the *offset*. The *offset* can be positive or negative.
* `SEEK_END`: the file’s offset is set to the size of the file plus the *offset*. The *offset* can be positive or negative.

To determine the current offset, <u>seek zero bytes from the current position</u>:

```c
off_t currpos;
currpos = lseek(fd, 0, SEEK_CUR);
```

This technique (above code) can also be used to determine if a file is capable of seeking. If the file descriptor refers to a pipe, FIFO, or socket, `lseek` sets `errno` to `ESPIPE` and returns −1.

* Negative offsets are possible for certain devices, but for regular files, the offset must be non-negative.
* `lseek` only records the current file offset within the kernel and does not cause any I/O to take place. This offset is then used by the next read or write operation.
* Hole in a file: file’s offset can be greater than the file’s current size, in which case the next `write` to the file will extend the file. This creates a hole in the file.
    * Bytes in the hole (bytes that have not been writen) are read back as 0. 
    * A hole in a file isn’t required to have storage backing it on disk.

### `read` Function

<script src="https://gist.github.com/shichao-an/ed695671abeb99a2a4b4.js"></script>

* *buf*: type `void *` is used for generic pointers.
* Return value is required to be a signed integer (`ssize_t`) to return a positive byte count, 0 (for end of file), or −1 (for an error).

Several cases in which the number of bytes actually read is less than the amount requested:

* Regular file: if the end of file is reached before the requested number of bytes has been read.
* Terminal device: up to one line is read at a time
* Network: buffering within the network may cause less than the requested amount to be returned
* Pipe or FIFO: if the pipe contains fewer bytes than requested, `read` will return only what is available
* Record-oriented device
* Interrupted by a signal and a partial amount of data has already been read

### `write` Function

<script src="https://gist.github.com/shichao-an/dc05a71e1e7eb4c18a0f.js"></script>

The return value is usually equal to the *nbytes* argument; otherwise, an error has occurred. 

Common causes for a `write` error: 

* Filling up a disk
* Exceeding the file size limit for a given process

For a regular file, the write operation starts at the file’s current offset. If the `O_APPEND` option was specified when the file was opened, the file’s offset is set to the current end of file before each write operation. After a successful write, the file’s offset is incremented by the number of bytes actually written.

### I/O Efficiency

* [mycat.c](https://github.com/shichao-an/apue.3e/blob/master/fileio/mycat.c)

```c
#include "apue.h"

#define BUFFSIZE 4096

int
main(void)
{
    int n;
    char buf[BUFFSIZE];

    while ((n = read(STDIN_FILENO, buf, BUFFSIZE)) > 0)
    if (write(STDOUT_FILENO, buf, n) != n)
        err_sys("write error");

    if (n < 0)
        err_sys("read error");

    exit(0);
}
```

Caveats of the above program:

* It reads from standard input and writes to standard output, assuming that these have been set up by the shell before this program is executed.
* It doesn’t close the input file or output file. Instead, the program uses the feature of the <u>UNIX kernel that closes all open file descriptors in a process when that process terminates.</u>
* This example works for both text files and binary files, since there is no difference between the two to the UNIX kernel.

Timing results for reading with different buffer sizes (`BUFFSIZE`) on Linux:

[![Figure 3.6 Timing results for reading with different buffer sizes on Linux](figure_3.6_600.png)](figure_3.6.png "Figure 3.6 Timing results for reading with different buffer sizes on Linux")

The file was read using the program shown above, with standard output redirected to `/dev/null`. The file system used for this test was the Linux ext4 file system with 4,096-byte blocks (the `st_blksize` value is 4,096). This accounts for the minimum in the system time occurring at the few timing measurements starting around a `BUFFSIZE` of 4,096. Increasing the buffer size beyond this limit has little positive effect.

Most file systems support some kind of read-ahead to improve performance. When sequential reads are detected, the system tries to read in more data than an application requests, assuming that the application will read it shortly. The effect of read-ahead can be seen in Figure 3.6, where the elapsed time for buffer sizes as small as 32 bytes is as good as the elapsed time for larger buffer sizes. [p73]

### File Sharing

The UNIX System supports the sharing of open files among different processes.

[![Figure 3.7 Kernel data structures for open files](figure_3.7_600.png)](figure_3.7.png "Figure 3.7 Kernel data structures for open files")

The kernel uses three data structures to represent an open file, and the relationships among them determine the effect one process has on another with regard to file sharing.

* **Process table entry**: every process has an entry in the process table. Each process table entry has a table of open file descriptors. Associated with each file descriptor are:
    * [**File descriptor flags**](http://www.gnu.org/software/libc/manual/html_node/Descriptor-Flags.html) (close-on-exec)
    * Pointer to a file table entry:
* **File table entry**: the kernel maintains a file table for all open files. Each file table entry contains:
    * [**File status flags**](http://www.gnu.org/software/libc/manual/html_node/File-Status-Flags.html)
    * Current file offset
    * Pointer to the v-node table entry for the file
* **v-node** structure: contains information about the type of file and pointers to functions that operate on the file
    * This information is read from disk when the file is opened, so that all the pertinent information about the file is readily available
    * v-node also contains the **i-node** for the file
    * Linux has no v-node. Instead, a generic i-node structure is used. [p75] Instead of splitting the data structures into a v-node and an i-node, Linux uses a file system–independent i-node and a file system–dependent i-node. [p76]

[Figure 3.7](/apue/figure_3.7.png) shows a pictorial arrangement of these three tables for a single process that has two different files open: one file is open on standard input (file descriptor 0), and the other is open on standard output (file descriptor 1).

If two independent processes have the same file open, we could have the arrangement shown in Figure 3.8 (below).

[![Figure 3.8 Two independent processes with the same file open](figure_3.8_600.png)](figure_3.8.png "Figure 3.8 Two independent processes with the same file open")

Each process that opens the file gets its own file table entry, but only a single v-node table entry is required for a given file. One reason <u>each process gets its own file table entry is so that each process has its own current offset for the file.</u>

#### Specific operations

* File offset: After each `write` is complete, the current file offset in the file table entry is incremented by the number of bytes written. If this causes the current file offset to exceed the current file size, the current file size in the i-node table entry is set to the current file offset (the file is extended).
* `O_APPEND`: If a file is opened with the `O_APPEND` flag, a corresponding flag is set in the file status flags of the file table entry. Each time a `write` is performed for a file with this append flag set, the current file offset in the file table entry is first set to the current file size from the i-node table entry. Th is forces every `write` to be appended to the current end of file.
* `lseek`
    * If a file is positioned to its current end of file using `lseek`, all that happens is the current file offset in the file table entry is set to the current file size from the i-node table entry. <u>This is not the same as if the file was opened with the `O_APPEND` flag.</u>
    * The `lseek` function modifies only the current file offset in the file table entry. No I/O takes place.

It is possible for more than one file descriptor entry to point to the same file table entry:

* `dup`
* `fork`: the parent and the child share the same file table entry for each open descriptor

#### File descriptor flags vs. the file status flags

* File descriptor flags: apply only to a single descriptor in a single process
* File status flags: apply to all descriptors in any process that point to the given file table entry
* `fcntl` is used to fetch and modify both of them

### Atomic Operations

Older versions of the UNIX System didn’t support the `O_APPEND` option if a single process wants to append to the end of a file. The program would be:

```c
if (lseek(fd, 0L, 2) < 0) /* position to EOF, 2 means SEEK_END */
    err_sys("lseek error");
if (write(fd, buf, 100) != 100) /* and write */
    err_sys("write error");
```

This works fine for a single process, but problems arise if multiple processes (or multiple instances of the same program) use this technique to append to the same file. The problem here is that our logical operation of "position to the end of file and write" requires two separate function calls. The solution is to have the positioning to the current end of file and the write be an atomic operation with regard to other processes. Any operation that requires more than one function call cannot be atomic, as there is always the possibility that the kernel might temporarily suspend the process between the two function calls. The UNIX System provides an atomic way to do this operation if we set the `O_APPEND` flag when a file is opened. This causes the kernel to position the file to its current end of file before each `write`. We no longer have to call lseek before each `write`.

### `pread` and `pwrite` Functions

The Single UNIX Specification includes two functions that allow applications to seek and perform I/O atomically:

<script src="https://gist.github.com/shichao-an/2f2fb4d9288fd1fa79b3.js"></script>

* `pread`: equivalent to calling `lseek` followed by a call to `read`, with the following exceptions:
    * There is no way to interrupt the two operations that occur calling `pread`.
    * The current file offset is not updated.
* `pwrite`:  equivalent to calling lseek followed by a call to write, with similar exceptions to `pread`.

#### Creating a File

##### **Atomic operation**

When both of `O_CREAT` and `O_EXCL` options are specified, the `open` will fail if the file already exists. The check for the existence of the file and the creation of the file was performed as an atomic operation.

##### **Non-atomic operation**

If we didn’t have this atomic operation, we might try:

```c
if ((fd = open(path, O_WRONLY)) < 0) {
    if (errno == ENOENT) {
        if ((fd = creat(path, mode)) < 0)
            err_sys("creat error");
    } else {
        err_sys("open error");
    }
}
```

The problem occurs if the file is created by another process between the `open` and the `creat`. If the file is created by another process between these two function calls, and if that other process writes something to the file, that data is erased when this `creat` is executed. Combining the test for existence and the creation into a single atomic operation avoids this problem.

**Atomic operation** refers to an operation that might be composed of multiple steps. <u>If the operation is performed atomically, either all the steps are performed (on success) or none are performed (on failure). It must not be possible for only a subset of the steps to be performed.</u>
