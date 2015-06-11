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

Most file systems support some kind of read-ahead to improve performance. When sequential reads are detected, the system tries to read in more data than an application requests, assuming that the application will read it shortly. The effect of read-ahead can be seen in Figure 3.6, where the elapsed time for buffer sizes as small as 32 bytes is as good as the elapsed time for larger buffer sizes.
