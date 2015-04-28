## Chapter 3. File I/O

This chapter discusses unbuffered I/O, which are not part of ISO C but are part of POSIX.1 and the Single UNIX Specification.

### File Descriptors

* All open files are referred to by file descriptors
* Non-negative integer
* Range from 0 to `OPEN_MAX - 1`. With FreeBSD 8.0, Linux 3.2.0, Mac OS X 10.6.8, and Solaris 10, the limit is essentially infinite, bounded by the amount of memory on the system, the size of an integer, and any hard and soft limits configured by the system administrator.

### `open` and `openat` Functions
