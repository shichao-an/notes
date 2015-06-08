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
