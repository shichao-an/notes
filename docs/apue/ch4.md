### **Chapter 4. Files and Directories**

This chapter centers on I/O for regular files.

### `restrict` keyword

Added in C99, [`restrict`](https://en.wikipedia.org/wiki/Restrict) keyword is used to tell the compiler which pointer references can be optimized, by indicating that the object to which the pointer refers is accessed in the function only via that pointer. [p26]


### `stat`, `fstat`, `fstatat`, and `lstat` Functions

<small>[apue_stat.h](https://gist.github.com/shichao-an/dd0cdd90a54848ff3018)</small>

```c
#include <sys/stat.h>

int stat(const char *restrict pathname, struct stat *restrict buf);
int fstat(int fd, struct stat *buf);
int lstat(const char *restrict pathname, struct stat *restrict buf);
int fstatat(int fd, const char *restrict pathname, struct stat *restrict buf, int flag);

/* All four return: 0 if OK, −1 on error */
```

* `stat`: returns a structure of information about the named file
* `fstat`: returns a structure of information about the given file descriptor
* `lstat`: similar to `stat`, returns information about the symbolic link, not the file referenced by the symbolic link
* `fstatat`:  return the file statistics for a pathname relative to an open directory represented by the fd argument; the flag argument controls whether symbolic links are followed

The `buf` argument is a pointer to a [structure](http://en.wikipedia.org/wiki/Stat_(system_call)#stat_structure) that we must supply. The functions fill in the structure.

```c
struct stat {
    mode_t    st_mode;
    ino_t    st_ino;
    dev_t    st_dev;
    dev_t    st_rdev;
    nlink_t    st_nlink;
    uid_t    st_uid;
    gid_t    st_gid;
    off_t    st_size;
    struct timespec    st_atim;
    struct timespec    st_mtim;
    struct timespec    st_ctim;
    blksize_t    st_blksize;
    blkcnt_t    st_blocks;
};
```

#### `timespec` structure
The `timespec` structure type defines time in terms of seconds and nanoseconds. It includes at least the following fields:

```c
time_t tv_sec;
long tv_nsec;
```

### File Types

* Regular file. All binary executable files conform to a format that allows the kernel to identify where to load a program’s text and data.
* Directory file. A file that contains the names of other files and pointers to information on these files. Any process that has read permission for a directory file can read the contents of the directory, but only the kernel can write directly to a directory file.
* Block special file
* Character special file
* FIFO
* Socket
* Symbolic link

This program prints the type of file for each command-line argument.

* [filetype.c](https://github.com/shichao-an/apue.3e/blob/master/filedir/filetype.c)

### Set-User-ID and Set-Group-ID

Every process has six or more IDs associated with it:

* The **real user ID** and **real group ID**: who we really are.
    * These two fields are taken from our entry in the password file when we log in.
    * Normally, these values don’t change during a login session, although there are ways for a superuser process to change them. ([Section 8.11](ch8.md#changing-user-ids-and-group-ids))
* The **effective user ID**, **effective group ID** and **supplementary group IDs**: used for file access permission checks.
* The **saved set-user-ID** and **saved set-group-ID**: saved by `exec` functions. They contain copies of the effective user ID and the effective group ID, when a program is executed. ([Section 8.11](ch8.md#changing-user-ids-and-group-ids))

Every file has an owner and a group owner:

* The owner is specified by the `st_uid` member of the `stat` structure;
* The group owner is specified by the `st_gid` member of the `stat` structure.

When we execute a program file, the effective user ID of the process is usually the real user ID, and the effective group ID is usually the real group ID. However, we can also set special flags in the file’s mode word (`st_mode`) that says:

* When this file is executed, set the effective user ID of the process to be the owner of the file (`st_uid`).
* When this file is executed, set the effective group ID of the process to be the group owner of the file (`st_gid`).

These two bits in the file’s mode word are called the **set-user-ID** (setuid) bit and the **set-group-ID** (setgid) bit.

For example:

* If the owner of the file is the superuser and if the file’s set-user-ID bit is set, then while that program file is running as a process, it has superuser privileges, regardless of the real user ID of the process that executes the file.
* `passwd(1)` is a set-user-ID program, so that the program can write the new password to the password file, typically either `/etc/passwd` or `/etc/shadow`, files that should be writable only by the superuser.

Because a process that is running set-user-ID to some other user usually assumes extra permissions, it must be written carefully.

[p99]

### File Access Permissions

1. Whenever we want to open any type of file by name, we must have execute permission in each directory mentioned in the name, including the current directory, if it is implied. Read permission for a directory and execute permission for a directory mean different things. Read permission lets us read the directory, obtaining a list of all the filenames in the directory. Execute permission lets us pass through the directory when it is a component of a pathname that we are trying to access. [p100]
2. We cannot create a new file in a directory unless we have write permission and execute permission in the directory.

### Ownership of New Files and Directories

1. The user ID of a new file is set to the effective user ID of the process
2. The group ID of a new file can be the effective group ID of the process; or group ID of the directory in which the file is being created.

FreeBSD 8.0 and Mac OS X 10.6.8 always copy the new file’s group ID from the directory.

### `access` and `faccessat` Functions

<small>[apue_access.h](https://gist.github.com/shichao-an/a0d8ab4d744d51be289f)</small>

```c
#include <unistd.h>

int access(const char *pathname, int mode);
int faccessat(int fd, const char *pathname, int mode, int flag);

/* Both return: 0 if OK, −1 on error */
```

These functions test accessibility based on the real user and group IDs.

The `flag` argument can be used to change the behavior of `faccessat`. If the `AT_EACCESS` flag is set, the access checks are made using the effective user and group IDs.

* [access.c](https://github.com/shichao-an/apue.3e/blob/master/filedir/access.c)

### `umask` Function

The Single UNIX Specification requires that the `umask` command support a symbolic mode of operation. Unlike the octal format, the symbolic format specifies which permissions are to be allowed instead of which ones are to be denied.

```
$ umask  # first print the current file mode creation mask
002
$ umask -S  # print the symbolic form
u=rwx,g=rwx,o=rx
$ umask 027  # print the symbolic form
$ umask -S  # print the symbolic form
u=rwx,g=rx,o=
```

### `chmod`, `fchmod`, and `fchmodat` Functions

<small>[apue_chmod.h](https://gist.github.com/shichao-an/9fa2e6e7e6e600cb62c1)</small>

```c
#include <sys/stat.h>

int chmod(const char *pathname, mode_t mode);
int fchmod(int fd, mode_t mode);
int fchmodat(int fd, const char *pathname, mode_t mode, int flag);

/* All three return: 0 if OK, −1 on error */
```

`chmod` automatically clears the following permission bits under the following conditions:

1. Setting sticky bit on a regular file without superuser privileges (Solaris)
2. If the group ID of the new file does not equal either the effective group ID of the process or one of the process’s supplementary group IDs and if the process does not have superuser privileges, then the set-group-ID bit is automatically turned off. On FreeBSD 8.0, Linux 3.2.0 and Mac OS X 10.6.8, if a process that does not have superuser privileges writes to a file, the set-user-ID and set-group-ID bits are automatically turned off.

### Sticky Bit

Sticky Bit (`S_ISVTX`), or saved-text bit in the later versions of the UNIX System.

* On file: only on a minority of systems
* On directory: `/tmp` and `/var/tmp`

### `chown`, `fchown`, `fchownat`, and `lchown` Functions

<small>[apue_chown.h](https://gist.github.com/shichao-an/233e97d9b3d15aca39b2)</small>

```c
#include <unistd.h>

int chown(const char *pathname, uid_t owner, gid_t group);
int fchown(int fd, uid_t owner, gid_t group);
int fchownat(int fd, const char *pathname, uid_t owner, gid_t group, int flag);
int lchown(const char *pathname, uid_t owner, gid_t group);

/* All four return: 0 if OK, −1 on error */
```

* `lchown` and `fchownat` (with the `AT_SYMLINK_NOFOLLOW` flag set) change the owners of the symbolic link itself.
* `fchown` operates on a open file, it can’t be used to change the ownership of a symbolic link.

Only the superuser can change the ownership of a file (FreeBSD 8.0, Linux 3.2.0, and Mac OS X 10.6.8)

When `_POSIX_CHOWN_RESTRICTED` is in effect, a non-superuser can’t change the user ID of your files; A nonsuperuser can change the group ID of files that he owns, but only to groups that he belongs to.

### File Size

The `st_size` member of the stat structure contains the size of the file in bytes. This field is meaningful only for regular files, directories, and symbolic links.

FreeBSD 8.0, Mac OS X 10.6.8, and Solaris 10 also define the file size for a pipe as the number of bytes that are available for reading from the pipe.

* For a regular file, a file size of 0 is allowed. We’ll get an end-of-file indication on the first read of the file.
* For a directory, the file size is usually a multiple of a number, such as 16 or 512.
* For a symbolic link, the file size is the number of bytes in the filename.

Most contemporary UNIX systems provide two fields:

* `st_blksize`: preferred block size for I/O for the file
* `st_blocks`: actual number of 512-byte blocks that are allocated

Be aware that different versions of the UNIX System use units other than 512-byte blocks for `st_blocks`. Use of this value is **nonportable**.

### Holes in a File

```
$ ls -l core
-rw-r--r-- 1 sar 8483248 Nov 18 12:18 core
$ du -s core
272 core
```

### File Truncation

<small>[apue_truncate.h](https://gist.github.com/shichao-an/df5f6cc1cd7871670b11)</small>

```c
#include <unistd.h>

int truncate(const char *pathname, off_t length);
int ftruncate(int fd, off_t length);

/* Both return: 0 if OK, −1 on error */
```

These two functions truncate an existing file to *length* bytes. If the previous size of the file was greater than *length*, the data beyond *length* is no longer accessible. Otherwise, if the previous size was less than *length*, the file size will increase and the data between the old end of file and the new end of file will read as 0 (a hole is probably created in the file).

### File Systems

Most UNIX file systems support **case-sensitive** filenames. On Mac OS X, however, the HFS file system is **case-preserving** with **case-insensitive** comparisons.

[![Figure 4.14 Cylinder group’s i-nodes and data blocks in more detail](figure_4.14_600.png)](figure_4.14.png "Figure 4.14 Cylinder group’s i-nodes and data blocks in more detail")

* Every i-node has a link count that contains the number of directory entries that point to it. Only when the link count (`st_nlink`) goes to 0 can the file be deleted.
* With a symbolic link (file type `S_IFLNK`), the actual contents of the file (the data blocks) store the name of the file that the symbolic link points to.
* The i-node contains all the information about the file: the file type, the file’s access permission bits, the size of the file, pointers to the file’s data blocks, and so on.
* Only two items are stored in the directory entry: the filename and the i-node number. The data type for the i-node number is `ino_t`.


### `link`, `linkat`, `unlink`, `unlinkat`, and `remove` Functions

<small>[apue_link.h](https://gist.github.com/shichao-an/a05542802e846a5e4a9d)</small>

```c
#include <unistd.h>

int link(const char *existingpath, const char *newpath);
int linkat(int efd, const char *existingpath, int nfd, const char *newpath,
           int flag);

/* Both return: 0 if OK, −1 on error */
```

When a file is closed, the kernel first checks the count of the number of processes that have the file open. If this count has reached 0, the kernel then checks the link count; if it is 0, the file’s contents are deleted.

When the `AT_REMOVEDIR` flag is set, then the `unlinkat` function can be used to remove a directory, similar to using `rmdir`.

<small>[apue_remove.h](https://gist.github.com/shichao-an/6ed5d4f09ca321b9969d)</small>

```c
#include <stdio.h>

int remove(const char *pathname);

/* Returns: 0 if OK, −1 on error */
```

### `rename` and `renameat` Functions

<small>[apue_rename.h](https://gist.github.com/shichao-an/b2751a71cdecc9845951)</small>

```c
#include <stdio.h>

int rename(const char *oldname, const char *newname);
int renameat(int oldfd, const char *oldname, int newfd, const char *newname);

/* Both return: 0 if OK, −1 on error */
```

### Symbolic Links

It is possible to introduce loops into the file system by using symbolic links. Most functions that look up a pathname return an `errno` of `ELOOP` when this occurs.

On Linux, the [`ftw`](http://linux.die.net/man/3/ftw) and `nftw` functions record all directories seen and avoid processing a directory more than once, so they don’t display this behavior.

* `ls -l`
* `ls -F`

<small>[apue_symlink.h](https://gist.github.com/shichao-an/487e3a881014019a5896)</small>

```c
#include <unistd.h>

int symlink(const char *actualpath, const char *sympath);
int symlinkat(const char *actualpath, int fd, const char *sympath);

/* Both return: 0 if OK, −1 on error */
```

Because the open function follows a symbolic link, we need a way to open the link itself and read the name in the link.

<small>[apue_readlink.h](https://gist.github.com/shichao-an/8ee1ce45f97503e1eadf)</small>

```c
#include <unistd.h>

ssize_t readlink(const char *restrict pathname, char *restrict buf,
                 size_t bufsize);

ssize_t readlinkat(int fd, const char *restrict pathname,
                   char *restrict buf, size_t bufsize);

/* Both return: number of bytes read if OK, −1 on error */
```

These functions combine the actions of `open`, `read`, and `close`.

### File Times

Field     | Description                         | Example          | ls(1) option
--------- | ----------------------------------- | ---------------- | ------------
`st_atim` | last-access time of file data       | `read`           | `-u`
`st_mtim` | last-modification time of file data | `write`          | default
`st_ctim` | last-change time of i-node status   | `chmod`, `chown` | `-c`

The system does not maintain the last-access time for an i-node. The functions `access` and `stat` don’t change any of the three times.

### `futimens`, `utimensat`, and `utimes` Functions

<small>[apue_futimens.h](https://gist.github.com/shichao-an/cbb255521bbfbd297ffe)</small>

```c
#include <sys/stat.h>

int futimens(int fd, const struct timespec times[2]);
int utimensat(int fd, const char *path, const struct timespec times[2], int flag);

/* Both return: 0 if OK, −1 on error */
```

In both functions, the first element of the times array argument contains the **access time**, and the second element contains the **modification time**.

* [apue_utimes](https://gist.github.com/shichao-an/45e1af258c8c65aef8e3)

```c
#include <sys/time.h>

int utimes(const char *pathname, const struct timeval times[2]);

/* Returns: 0 if OK, −1 on error */
```

We are unable to specify a value for the **changed-status time**, `st_ctim` (the time the i-node was last changed), as this field is automatically updated when the `utime` function is called.

### `mkdir`, `mkdirat`, and `rmdir` Functions

<small>[apue_rmdir.h](https://gist.github.com/shichao-an/72a28c9446973e80a80a.)</small>

```c
#include <unistd.h>

int rmdir(const char *pathname);

/* Returns: 0 if OK, −1 on error */
```

For a directory, we normally want at least one of the execute bits enabled, to allow access to filenames within the directory.

Solaris 10 and Linux 3.2.0 also have the new directory inherit the set-group-ID bit from the parent directory. Files created in the new directory will then inherit the group ID of that directory. With Linux, the file system implementation determines whether this behavior is supported. For example, the ext2, ext3, and ext4 file systems allow this behavior to be controlled by an option to the mount(1) command.

### Reading Directories

<small>[apue_opendir.h](https://gist.github.com/shichao-an/e98f9a012d74b7a96293)</small>

```c
#include <dirent.h>

DIR *opendir(const char *pathname);
DIR *fdopendir(int fd);
/* Both return: pointer if OK, NULL on error */

struct dirent *readdir(DIR *dp);
/* Returns: pointer if OK, NULL at end of directory or error */

void rewinddir(DIR *dp);
int closedir(DIR *dp);
/* Returns: 0 if OK, −1 on error */

long telldir(DIR *dp);
/* Returns: current location in directory associated with dp */

void seekdir(DIR *dp, long loc);
```

The `dirent` structure defined in <dirent.h> is implementation dependent, with at least the following two members:

```c
	ino_t  d_ino;                 /* i-node number */
	char   d_name[];              /* null-terminated filename */
```

The `DIR` structure is an internal structure used by these seven functions to maintain information about the directory being read. The purpose of the DIR structure is similar to that of the `FILE` structure maintained by the standard I/O library,

* [ftw8.c](https://github.com/shichao-an/apue.3e/blob/master/filedir/ftw8.c)

### `chdir`, `fchdir`, and `getcwd` Functions

<small>[apue_chdir.h](https://gist.github.com/shichao-an/fb972392bdd5ce97dc7e)</small>

```c
#include <unistd.h>

int chdir(const char *pathname);
int fchdir(int fd);

/* Both return: 0 if OK, −1 on error */
```

<small>[apue_getcwd.h](https://gist.github.com/shichao-an/090c8c9281d8da18bed5)</small>

```c
#include <unistd.h>

char *getcwd(char *buf, size_t size);

/* Returns: buf if OK, NULL on error */
```

#### Device Special Files

* Every file system is known by its **major** and **minor** device numbers, which are encoded in the primitive system data type `dev_t`.
* We can usually access the major and minor device numbers through two macros defined by most implementations: `major` and `minor`.

On Linux 3.2.0, `dev_t` is a 64-bit integer, only 12 bits are used for the major number and 20 bits are used for the minor number. Linux defines these macros in `<sys/sysmacros.h>`, which is included by `<sys/types.h>`.

The `st_dev` value for every filename on a system is the device number of the file system containing that filename and its corresponding i-node.

Only character special files and block special files have an `st_rdev` value. This value contains the device number for the actual device.

- - -

### Doubts and Solutions
#### Verbatim

Section 4.21 on `rmdir` [p130]:

> If the link count of the directory becomes 0 with this call, and if no other process has the directory open, then the space occupied by the directory is freed. If one or more processes have the directory open when the link count reaches 0, the last link is removed and the dot and dot-dot entries are removed before this function returns. Additionally, no new files can be created in the directory.

Does "link count" here mean number of entries (except dot and dot-dot)? Otherwise, this contradicts  "any leaf directory (a directory that does not contain any other directories) always has a link count of 2" in section 4.14 on page 115.
