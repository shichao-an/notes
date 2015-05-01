## Chapter 4. Files and Directories

This chapter centers on I/O for regular files.

### `restrict` keyword

Added in C99, [`restrict`](https://en.wikipedia.org/wiki/Restrict) keyword is used to tell the compiler which pointer references can be optimized, by indicating that the object to which the pointer refers is accessed in the function only via that pointer. [p26]


### `stat`, `fstat`, `fstatat`, and `lstat` Functions

<script src="https://gist.github.com/shichao-an/dd0cdd90a54848ff3018.js"></script>

* `stat`: returns a structure of information about the named file
* `fstat`: returns a structure of information about the given file descriptor
* `lstat`: similar to `stat`, returns information about the symbolic link, not the file referenced by the symbolic link
* `fstatat`:  return the file statistics for a pathname relative to an open directory represented by the fd argument; the flag argument controls whether symbolic links are followed

The `buf` argument is a pointer to a [structure](http://en.wikipedia.org/wiki/Stat_(system_call)#stat_structure) that we must supply. The functions fill in the structure.

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

### File Access Permissions

1. Whenever we want to open any type of file by name, we must have execute permission in each directory mentioned in the name, including the current directory, if it is implied. Read permission for a directory and execute permission for a directory mean different things. Read permission lets us read the directory, obtaining a list of all the filenames in the directory. Execute permission lets us pass through the directory when it is a component of a pathname that we are trying to access. [p100]
2. We cannot create a new file in a directory unless we have write permission and execute permission in the directory.

### Ownership of New Files and Directories

1. The user ID of a new file is set to the effective user ID of the process
2. The group ID of a new file can be the effective group ID of the process; or group ID of the directory in which the file is being created.

FreeBSD 8.0 and Mac OS X 10.6.8 always copy the new file’s group ID from the directory. 

### `access` and `faccessat` Functions

<script src="https://gist.github.com/shichao-an/a0d8ab4d744d51be289f.js"></script>

These functions test accessibility based on the real user and group IDs.

The `flag` argument can be used to change the behavior of `faccessat`. If the `AT_EACCESS` flag is set, the access checks are made using the effective user and group IDs.

* [access.c](https://github.com/shichao-an/apue.3e/blob/master/filedir/access.c)

### `umask` Function

The Single UNIX Specification requires that the `umask` command support a symbolic mode of operation. Unlike the octal format, the symbolic format specifies which permissions are to be allowed instead of which ones are to be denied.

```text
$ umask  # first print the current file mode creation mask
002
$ umask -S  # print the symbolic form
u=rwx,g=rwx,o=rx
$ umask 027  # print the symbolic form
$ umask -S  # print the symbolic form
u=rwx,g=rx,o=
```

### `chmod`, `fchmod`, and `fchmodat` Functions

<script src="https://gist.github.com/shichao-an/9fa2e6e7e6e600cb62c1.js"></script>

`chmod` automatically clears the following permission bits under the following conditions:

1. Setting sticky bit on a regular file without superuser privileges (Solaris)
2. If the group ID of the new file does not equal either the effective group ID of the process or one of the process’s supplementary group IDs and if the process does not have superuser privileges, then the set-group-ID bit is automatically turned off. On FreeBSD 8.0, Linux 3.2.0 and Mac OS X 10.6.8, if a process that does not have superuser privileges writes to a file, the set-user-ID and set-group-ID bits are automatically turned off.

### Sticky Bit

Sticky Bit (`S_ISVTX`), or saved-text bit in the later versions of the UNIX System.

* On file: only on a minority of systems
* On directory: `/tmp` and `/var/tmp`

### `chown`, `fchown`, `fchownat`, and `lchown` Functions

<script src="https://gist.github.com/shichao-an/233e97d9b3d15aca39b2.js"></script>

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

```text
$ ls -l core
-rw-r--r-- 1 sar 8483248 Nov 18 12:18 core
$ du -s core
272 core
```

### File Truncation
<script src="https://gist.github.com/shichao-an/df5f6cc1cd7871670b11.js"></script>

These two functions truncate an existing file to *length* bytes. If the previous size of the file was greater than *length*, the data beyond *length* is no longer accessible. Otherwise, if the previous size was less than *length*, the file size will increase and the data between the old end of file and the new end of file will read as 0 (a hole is probably created in the file).


### File Systems

Most UNIX file systems support **case-sensitive** filenames. On Mac OS X, however, the HFS file system is **case-preserving** with **case-insensitive** comparisons.
