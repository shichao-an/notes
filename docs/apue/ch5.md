### **Chapter 5. Standard I/O Library**

The standard I/O library handles such details as buffer allocation and performing I/O in optimal-sized chunks.

### Streams and `FILE` Objects

Standard I/O file streams can be used with both **single-byte** and **multibyte** ("wide") character sets. A stream’s orientation determines whether the characters that are read and written are single byte or multibyte.

* This book deals only with **byte-oriented** (single byte) streams.
* This book refers to a pointer to a `FILE` object, the type `FILE *`, as a *file pointer*.

### Standard Input, Standard Output, and Standard Error

Three streams are predefined and automatically available to a process. They refer to file descriptors `STDIN_FILENO`, `STDOUT_FILENO`, and `STDERR_FILENO` (defined in `<unistd.h>`) [p9]. These three standard I/O streams are referenced through the predefined file pointers `stdin`, `stdout`,and `stderr`(defined in `<stdio.h>`).

### Buffering

The goal of the buffering provided by the standard I/O library is to use the minimum number of read and write calls. This library also tries to do its buffering automatically for each I/O stream, obviating the need for the application to worry about it.

Three types of buffering are provided:

1. **Fully buffered**. Actual I/O takes place when the standard I/O buffer is filled.
    * Files residing on disk are normally fully buffered by the standard I/O library.
    * The buffer used is usually obtained by one of the standard I/O functions calling `malloc` ([Section 7.8](ch7.md#memory-allocation)) the first time I/O is performed on a stream.
    * The term *flush* describes the writing of a standard I/O buffer. A buffer can be flushed automatically by the standard I/O routines, such as when a buffer fills, or we can call the function `fflush` to flush a stream. Unfortunately, in the UNIX environment, *flush* means two different things:
        1. In terms of the standard I/O library, it means writing out the contents of a buffer, which may be partially filled.
        2. In terms of the terminal driver, such as the `tcflush` function in [Chapter 18](ch18.md), it means to discard the data that's already stored in a buffer.
2. **Line buffered**. The standard I/O library performs I/O when a newline character is encountered on input or output.
    * <u>This allows us to output a single character at a time (with the standard I/O `fputc` function), knowing that actual I/O will take place only when we finish writing each line.</u>
    * Line buffering is typically used on a stream when it refers to a terminal, such as standard input and standard output.
    * Line buffering has two caveats:
        1. The size of the buffer that the standard I/O library uses to collect each line is fixed, so I/O might take place if this buffer is filled before writing a newline.
        2. Whenever input is requested through the standard I/O library from either (a) an unbuffered stream or (b) a line-buffered stream (that requires data to be requested from the kernel), all line-buffered output streams are flushed. The reason for the qualifier on (b) is that the requested data may already be in the buffer, which doesn't require data to be read from the kernel. Obviously, any input from an unbuffered stream, item (a), requires data to be obtained from the kernel.
3. **Unbuffered**. The standard I/O library does not buffer the characters. For example:
    * If we write 15 characters with the standard I/O `fputs` function, we expect these 15 characters to be output as soon as possible, probably with the `write` function from [Section 3.8](ch3.md#write-function).
    * The standard error stream is normally unbuffered so that any error messages are displayed as quickly as possible, regardless of whether they contain a newline.

ISO C requires the following buffering characteristics:

* Standard input and standard output are fully buffered, if and only if they do not refer to an interactive device.
* Standard error is never fully buffered.

However, this *doesn't* tell us either of the following:

* Whether standard input and standard output are unbuffered or line buffered if they refer to an interactive device
* Whether standard error should be unbuffered or line buffered

Most implementations default to the following types of buffering:

* Standard error is always unbuffered.
* All other streams are line buffered if they refer to a terminal device; otherwise, they are fully buffered.

<small>[apue_setbuf.h](https://gist.github.com/shichao-an/70e28ba25f1b7276e834)</small>

```c
#include <stdio.h>

void setbuf(FILE *restrict fp, char *restrict buf );
int setvbuf(FILE *restrict fp, char *restrict buf, int mode, size_t size);

/* Returns: 0 if OK, nonzero on error */
```

* `setbuf`: *buf* must point to a buffer of length `BUFSIZ`, a constant defined in `<stdio.h>`
* `setvbuf`: type of buffering is specified with `_IOFBF`, `_IOLBF`, `_IONBF`.

The GNU C librarys use the value from the `st_blksize` member of the `stat` structure to determine the optimal standard I/O buffer size.

The `fflush` function causes any unwritten data for the stream to be passed to the kernel. If *fp* is `NULL`, `fflush` causes all output streams to be flushed.

### Opening a Stream

<small>[apue_fopen.h](https://gist.github.com/shichao-an/3fea32272cd9e1b574c6)</small>

```c
#include <stdio.h>

FILE *fopen(const char *restrict pathname, const char *restrict type);
FILE *freopen(const char *restrict pathname,
              const char *restrict type,
              FILE *restrict fp);
FILE *fdopen(int fd, const char *type);

/* All three return: file pointer if OK, NULL on error */
```

* `fdopen` function is often used with descriptors returned by the functions that create pipes and network communication channels, because these special types of files cannot be opened with the `fopen` function.

**type** argument has 15 values as specifed by ISO C:

**type** | Description | `open`(2) Flags
---- | ----------- | ---------------
`r`, `rb` | open for reading | <code>O_RDONLY</code>
`w`, `wb` | truncate to 0 length or create for writing | <code>O_WRONLY&#124;O_CREAT&#124;O_TRUNC</code>
`a`, `ab` | append; open for writing at end of file, or create for writing | <code>O_WRONLY&#124;O_CREAT&#124;O_APPEND</code>
`r+`, `r+b`, `rb+` | open for reading and writing | <code>O_RDWR</code>
`w+`, `w+b`, `wb+` | truncate to 0 length or create for reading and writing | <code>O_RDWR&#124;O_CREAT&#124;O_TRUNC</code>
`a+`, `a+b`, `ab+` | open or create for reading and writing at end of file | <code>O_RDWR&#124;O_CREAT&#124;O_APPEND</code>

Character `b` allows the standard I/O system to differentiate between a text file and a binary file. The UNIX kernel doesn’t differentiate between these types of files, thus character `b` has no effect.

* **Write**: The `fdopen` function cannot truncate any file it opens for writing
* **Append**: each write will take place at the then current end of file. If multiple processes open the same file with the standard I/O append mode, the data from each process will be correctly written to the file
* **Read and write** (`+` sign in type): Output cannot be directly followed by input without an intervening `fflush`, `fseek`, `fsetpos`, or `rewind`. Input cannot be directly followed by output without an intervening `fseek`, `fsetpos`, or `rewind`, or an input operation that encounters an end of file.

<small>[apue_fclose.h](https://gist.github.com/shichao-an/3c8458270dc1f08325f4)</small>

```c
#include <stdio.h>

int fclose(FILE *fp);

/* Returns: 0 if OK, EOF on error */
```

An open stream is closed by calling `fclose`:

* Any buffered output data is flushed before the file is closed
* Any input data that may be buffered is discarded

When a process terminates normally, either by calling the exit function directly or by returning from the main function, all standard I/O streams with unwritten buffered data are flushed and all open standard I/O streams are closed.

### Reading and Writing a Stream

Unformatted I/O:

* Character-at-a-time I/O.
* Line-at-a-time I/O: `fgets` and `fputs`. Each line is terminated with a newline character.
* Direct I/O (binary I/O, object-at-a-time I/O, record-oriented I/O, or structure-oriented I/O): `fread` and `fwrite`. For each I/O operation, we read or write some number of objects, where each object is of a specified size

#### Input Functions

<small>[apue_getc.h](https://gist.github.com/shichao-an/afcad88f5484e55327c4)</small>

```c
#include <stdio.h>

int getc(FILE *fp);
int fgetc(FILE *fp);
int getchar(void);

/* All three return: next character if OK, EOF on end of file or error */
```

* The function `getchar` is defined to be equivalent to `getc(stdin)`.
* `getc` can be implemented as a macro, whereas `fgetc` cannot be implemented as a macro.
* These three functions return the next character as an `unsigned char` converted to an `int`. Thus, all possible character values can be returned, along with an indication that either an error occurred or the end of file has been encountered. The constant EOF in `<stdio.h>` is required to be a negative value. Its value is often −1.

These functions return the same value whether an error occurs or the end of file is reached. To distinguish between the two, we must call either `ferror` or `feof`:

<small>[apue_ferror.h](https://gist.github.com/shichao-an/fe81c6d98b62e487aaf3)</small>

```c
#include <stdio.h>

int ferror(FILE *fp);
int feof(FILE *fp);

/* Both return: nonzero (true) if condition is true, 0 (false) otherwise */

void clearerr(FILE *fp);
```

In most implementations, two flags are maintained for each stream in the `FILE` object:

* An error flag
* An end-of-file flag

Both flags are cleared by calling `clearerr`.

##### **Pushback**

After reading from a stream, we can push back characters by calling `ungetc`.

<small>[apue_ungetc.h](https://gist.github.com/shichao-an/1de26637c53e6de17b25)</small>

```c
#include <stdio.h>

int ungetc(int c, FILE *fp);

/* Returns: c if OK, EOF on error */
```

* The characters that are pushed back are returned by subsequent reads on the stream in reverse order of their pushing.
* The character that is pushed back does not have to be the same character that was read.
* When characters are pushed back with `ungetc`, they are not written back to the underlying file or device. Instead, they are kept incore in the standard I/O library’s buffer for the stream. EOF cannot be pushed back.
* Used for peeking characters.

#### Output Functions

<small>[apue_putc.h](https://gist.github.com/shichao-an/3aaa0731d3fbbe68da0c)</small>

```c
#include <stdio.h>

int putc(int c, FILE *fp);
int fputc(int c, FILE *fp);
int putchar(int c);

/* All three return: c if OK, EOF on error */
```

* `putchar(c)` is equivalent to `putc(c, stdout)`
* `putc` can be implemented as a macro, whereas `fputc` cannot be implemented as a macro.

### Line-at-a-Time I/O

<small>[apue_fgets.h](https://gist.github.com/shichao-an/2c9049288e8634b92734)</small>

```c
#include <stdio.h>

char *fgets(char *restrict buf, int n, FILE *restrict fp);
char *gets(char *buf);

/* Both return: buf if OK, NULL on end of file or error */
```

* `gets` function reads from standard input, whereas `fgets` reads from the specified stream.
* `fgets`: reads *n - 1* characters (including the newline) or partial line if longer than *n - 1* into the buffer, then the buffer is (always) null terminated.
* `gets`: should never be used. Without specifying buffer size, this may cause buffer to overflow if the line is longer than the buffer, writing over whatever happens to follow the buffer in memory. `gets` is marked as an obsolescent interface in SUSv4 and has been omitted from the latest version of the ISO C standard

<small>[apue_fputs.h](https://gist.github.com/shichao-an/5a2fdd9294a2e4c37aad)</small>

```c
#include <stdio.h>

int fputs(const char *restrict str, FILE *restrict fp);
int puts(const char *str);

/* Both return: non-negative value if OK, EOF on error */
```

* `fputs`: writes the null-terminated string to the specified stream without writing the null byte
* `puts`: writes the null-terminated string to the standard output without writing the null byte, and then writes a newline character to the standard output. `puts` should be avoided being used to prevent having to remember whether it appends a newline.

### Standard I/O Efficiency

Function | User CPU (seconds) | System CPU (seconds) | Clock time (seconds) | Bytes of program text
-------- | ------------------ | -------------------- | -------------------- | ---------------------
best time from Figure 3.6 | 0.05 | 0.29 | 3.18 |
`fgets`, `fputs` | 2.27 | 0.30 | 3.49 | 143
`getc`, `putc` | 8.45 | 0.29 | 10.33 | 114
`fgetc`, `fputc` | 8.16 | 0.40 | 10.18 | 114
single byte time from Figure 3.6 | 134.61 | 249.94 | 394.95 |

* One advantage of using the standard I/O routines is that we don’t have to worry about buffering or choosing the optimal I/O size.
* Usually, `getc` and `putc` are implemented as macros, but in the GNU C library implementation the macro simply expands to a function call.
* The line-at-a-time functions are implemented using `memccpy(3)`. Often, the memccpy function is implemented in assembly language instead of C, for efficiency.

### Binary I/O

If doing binary I/O, we often want to read or write an entire structure at a time. There are problems with the previous functions:

* `getc`, `putc`: we have to loop through the entire structure one byte a time
* `fputs`: stops writing when it hits a null byte
* `fgets`: won't work correctly on input if any data bytes are null or newlines

<small>[apue_fread.h](https://gist.github.com/shichao-an/a90609694cb97c765ca2)</small>

```c
#include <stdio.h>

size_t fread(void *restrict ptr, size_t size, size_t nobj,
             FILE *restrict fp);
size_t fwrite(const void *restrict ptr, size_t size, size_t nobj,
              FILE *restrict fp);

/* Both return: number of objects read or written */
```

These functions have two common uses:

Read or write a binary array (e.g write elements 2 through 5 of a floating-point array):

```c
float   data[10];

if (fwrite(&data[2], sizeof(float), 4, fp) != 4)
    err_sys("fwrite error");
```

Read or write a structure:

```c
struct {
    short  count;
    long   total;
    char   name[NAMESIZE];
} item;

if (fwrite(&item, sizeof(item), 1, fp) != 1)
    err_sys("fwrite error");
```

* `fread`: return value can be less than *nobj* if an error occurs or if the end of file is encountered
* `fwrite`: if the return value is less than the requested `nobj`, an error has occurred

These two functions won't work on different systems (sometimes even on the same system):

1. The offset of a member within a structure can differ between compilers and systems because of different [alignment requirements](http://en.wikipedia.org/wiki/Data_structure_alignment#Typical_alignment_of_C_structs_on_x86). Even on a single system, the binary layout of a structure can differ, depending on compiler options. [p157]
2. The binary formats used to store multibyte integers and floating-point values differ among machine architectures


### Positioning a Stream

<small>[apue_ftell.h](https://gist.github.com/shichao-an/18d258b1815658a84cf7)</small>

```c
#include <stdio.h>

long ftell(FILE *fp);

/* Returns: current file position indicator if OK, −1L on error */

int fseek(FILE *fp, long offset, int whence);

/* Returns: 0 if OK, −1 on error */

void rewind(FILE *fp);
```

* `ftell`: return file's position indicator (bytes from the beginning of the file)
* `fseek`:
    * Binary file: *whence* can be `SEEK_SET`, `SEEK_CUR`, and `SEEK_END`
    * Text file: *whence* has to be `SEEK_SET`; *offset* can only be 0 (rewind the file to its beginning) or a value that was returned by `ftell` for that file.
* `rewind`: set the stream to the beginning of the file



<small>[apue_ftello.h](https://gist.github.com/shichao-an/530b106fa164cb197077)</small>

```c
#include <stdio.h>

off_t ftello(FILE *fp);

/* Returns: current file position indicator if OK, (off_t)−1 on error */

int fseeko(FILE *fp, off_t offset, int whence);

/* Returns: 0 if OK, −1 on error */
```

<small>[apue_fgetpos.h](https://gist.github.com/shichao-an/e37050a7db81810e78cc)</small>

```c
#include <stdio.h>

int fgetpos(FILE *restrict fp, fpos_t *restrict pos);
int fsetpos(FILE *fp, const fpos_t *pos);

/* Both return: 0 if OK, nonzero on error */
```

### Formatted I/O

#### Formatted Output

<small>[apue_printf.h](https://gist.github.com/shichao-an/558af328d4915c8d77b8)</small>

```c
#include <stdio.h>

int printf(const char *restrict format, ...);
int fprintf(FILE *restrict fp, const char *restrict format, ...);
int dprintf(int fd, const char *restrict format, ...);

/* All three return: number of characters output if OK, negative value if output error */

int sprintf(char *restrict buf, const char *restrict format, ...);
/* Returns: number of characters stored in array if OK, negative value if encoding error */

int snprintf(char *restrict buf, size_t n, const char *restrict format, ...);
/* Returns: number of characters that would have been stored in array if buffer was
   large enough, negative value if encoding error */
```

* `sprintf`: automatically appends a null byte at the end of the array, but this null byte is not included in the return value. `sprintf` is possible to overflow the buffer.
* `snprintf`: returns the number of characters that would have been written to the buffer had it been big enough. If `snprintf` returns a positive value less than the buffer size n, then the output was not truncated.

##### **Conversion specification**

```
%[flags][fldwidth][precision][lenmodifier]convtype
```

* Flag

    Flag | Description
    ---- | -----------
    `’` | (apostrophe) format integer with thousands grouping characters
    `-` | left-justify the output in the field
    `+` | always display sign of a signed conversion
    (space) | prefix by a space if no sign is generated
    `#` | convert using alternative form (include 0x prefix for hexadecimal format, for example)
    `0` | prefix with leading zeros instead of padding with spaces

* `fldwidth` specifies a minimum field width for the conversion
* `precision` specifies the minimum number of digits to appear for integer conversions, the minimum number of digits to appear to the right of the decimal point for floating-point conversions, or the maximum number of bytes for string conversions
* `lenmodifier` pecifies the size of the argument

    Length modifier | Description
    --------------- | -----------
    `hh` | signed or unsigned `char`
    `h` | signed or unsigned `short`
    `l` | signed or unsigned `long` or wide character
    `ll` | signed or unsigned `long` `long`
    `j` | `intmax_t` or `uintmax_t`
    `z` | `size_t`
    `t` | `ptrdiff_t`
    `L` | `long double`

* `convtype` is required.

Conversion type | Description
--------------- | -----------
`d`,`i` | signed decimal
`o` | unsigned octal
`u` | unsigned decimal
`x`,`X` | unsigned hexadecimal
`f`,`F` | double floating-point number
`e`,`E` | double floating-point number in exponential format
`g`,`G` | interpreted as `f`, `F`, `e`, or `E`, depending on value converted
`a`,`A` | double floating-point number in hexadecimal exponential format
`c` | character (with `l` length modifier, wide character)
`s` | string (with `l` length modifier, wide character string)
`p` | pointer to a void
`n` | pointer to a signed integer into which is written the number of characters written so far
`%` | a `%` character
`C` | wide character (XSI option, equivalent to `lc`)
`S` | wide character string (XSI option, equivalent to `ls`)


With the normal conversion specification, conversions are applied to the arguments in the order they appear after the format argument. An alternative conversion specification syntax allows the arguments to be named explicitly with the sequence `%n$` representing the *n*th argument.

The following five variants of the printf family are similar to the previous five, but the variable argument list (`...`) is replaced with `arg`.

<small>[apue_vprintf.h](https://gist.github.com/shichao-an/dbc3fe7bcb50f823951b)</small>

```c
#include <stdarg.h>
#include <stdio.h>

int vprintf(const char *restrict format, va_list arg);
int vfprintf(FILE *restrict fp, const char *restrict format,
             va_list arg);
int vdprintf(int fd, const char *restrict format, va_list arg);

/* All three return: number of characters output if OK, negative value if output error */

int vsprintf(char *restrict buf, const char *restrict format, va_list arg);

/* Returns: number of characters stored in array if OK, negative value if encoding error */

int vsnprintf(char *restrict buf, size_t n,
              const char *restrict format, va_list arg);

/* Returns: number of characters that would have been stored in array if buffer was
   large enough, negative value if encoding error */
```

#### Formatted Output

<small>[apue_scanf.h](https://gist.github.com/shichao-an/ee777644c2ea82bf38c0)</small>

```c
#include <stdio.h>

int scanf(const char *restrict format, ...);
int fscanf(FILE *restrict fp, const char *restrict format, ...);
int sscanf(const char *restrict buf, const char *restrict format, ...);

/* All three return: number of input items assigned, EOF if input error
   or end of file before any conversion */
```

Except for the conversion specifications and white space, other characters in the format have to match the input. If a character doesn’t match, processing stops, leaving the remainder of the input unread.

##### **Conversion specification**

```
%[*][fldwidth][m][lenmodifier]convtype
```

* `*` (leading asterisk) causes the result not stored in an argument
* `m`: **assignment-allocation character**, used with the `%c`, `%s`, and `%[` to force a memory  buffer to be allocated to hold the converted string. The caller is responsible for freeing the buffer.

* `convtype`

Conversion type | Description
--------------- | -----------
`d` | signed decimal, base 10
`i` | signed decimal, base determined by format of input
`o` | unsigned octal (input optionally signed)
`u` | unsigned decimal, base 10 (input optionally signed)
`x`,`X` | unsigned hexadecimal (input optionally signed)
`a`,`A`,`e`,`E`,`f`,`F`,`g`,`G` | floating-point number
`c` | character (with `l` length modifier, wide character)
`s` | string (with `l` length modifier, wide character string)
`[` | matches a sequence of listed characters, ending with `]`
`[ˆ` | matches all characters except the ones listed, ending with `]`
`p` | pointer to a void
`n` | pointer to a signed integer into which is written the number of characters read so far
`%` | a `%` character
`C` | wide character (XSI option, equivalent to `lc`)
`S` | wide character string (XSI option, equivalent to `ls`)

### Implementation Details

<small>[apue_fileno.h](https://gist.github.com/shichao-an/938ed0cb122d71d66cfc)</small>

```c
#include <stdio.h>

int fileno(FILE *fp);

/* Returns: the file descriptor associated with the stream */
```

Each standard I/O stream has an associated file descriptor, and we can obtain the descriptor for a stream by calling `fileno`.

* [`FILE`](https://github.com/shichao-an/glibc-2.21/blob/master/libio/libio.h#L245) implementaion in GNU C.
* [`buf.c`](https://github.com/shichao-an/apue.3e/blob/master/stdio/buf.c) (Figure 5.11): print buffering for various standard I/O streams

Result on OS X 10.10:

```text
$ ./buf
enter any character

one line to standard error
stream = stdin, line buffered, buffer size = 4096
stream = stdout, line buffered, buffer size = 4096
stream = stderr, unbuffered, buffer size = 1
stream = /etc/passwd, fully buffered, buffer size = 4096

$ ./buf < /etc/group > std.out 2> std.err
$ cat std.out
enter any character
stream = stdin, fully buffered, buffer size = 4096
stream = stdout, fully buffered, buffer size = 4096
stream = stderr, unbuffered, buffer size = 1
stream = /etc/passwd, fully buffered, buffer size = 4096
$ cat std.err
one line to standard error
```

### Temporary Files

<small>[apue_tmpnam.h](https://gist.github.com/shichao-an/5679ebc6a3221a63c196)</small>

```c
#include <stdio.h>

char *tmpnam(char *ptr);
FILE *tmpfile(void);

/* Returns: pointer to unique pathname Returns: file pointer if OK, NULL on error */
```

* `tmpnam`: generates a string that is a valid pathname that does not match any existing file. This function generates a different pathname each time it is called, up to `TMP_MAX` times.
    * When *ptr* is `NULL`: pathname is stored in a static area
    * When *ptr* is not `NULL`: it is assumed that it points to an array of at least `L_tmpnam` characters. The generated pathname is stored in this array, and *ptr* is returned as the value of the function.
* `tmpfile`: creates a temporary binary file (type `wb+`) that is automatically removed when it is closed or on program termination.



<small>[apue_mkdtemp.h](https://gist.github.com/shichao-an/f2065b6923b100974256)</small>

```c
#include <stdlib.h>

char *mkdtemp(char *template);

/* Returns: pointer to directory name if OK, NULL on error */

int mkstemp(char *template);

/* Returns: file descriptor if OK, −1 on error */
```

* `mkdtemp`: creates a uniquely named directory
* `mkstemp`: creates a uniquely named regular file
* *template*: a pathname whose last six characters are set to `XXXXXX` (`/tmp/dirXXXXXX`)

Unlike `tmpfile`, the temporary file created by `mkstemp` is not removed automatically for us.

The `tmpfile` and `mkstemp` functions should be used instead of `tmpnam`. [p169]

Example:

* [apue_stdio_mkstemp.c](https://gist.github.com/shichao-an/ef04db13cfdaecb65f4b): the array variable is allocated on the stacl. For a pointer to a string literal, only the pointer itself resides on the stack; the (constant) string is stored in the read-only segment of the program.

### Memory Streams

**Memory streams** are standard I/O streams for which there are no underlying files, although they are still accessed with `FILE` pointers. All I/O is done by transferring bytes to and from buffers in main memory.

<small>[apue_fmemopen.h](https://gist.github.com/shichao-an/1e2ecfc1323bdae6ff58)</small>

```c
#include <stdio.h>

FILE *fmemopen(void *restrict buf, size_t size,
               const char *restrict type);

/* Returns: stream pointer if OK, NULL on error */
```

* *buf*: points to the beginning of the user-allocated buffer and the size argument specifies the size of the buffer in bytes. If the buf argument is null, then the fmemopen function allocates a buffer of *size* bytes.
* *type*: controls how the stream can be used [p171]

Note:

* Under append mode, the current file position is set to the first null byte in the buffer. If the buffer contains no null bytes, then the current position is set to one byte past the end of the buffer. Under non-append mode, the current position is set to the beginning of the buffer. Thus, memory streams aren’t well suited for storing binary data (which might contain null bytes before the end of the data).
* If the *buf* argument is a null pointer, it makes no sense to open the stream for only reading or only writing. Because the buffer is allocated by `fmemopen` in this case, there is no way to find the buffer's address
* A null byte is written at the current position in the stream whenever we increase the amount of data in the stream’s buffer and call `fclose`, `fflush`, `fseek`, `fseeko`, or `fsetpos`.

### Alternatives to Standard I/O

When we use the line-at-a-time functions, `fgets` and `fputs`, the data is usually copied twice: once between the kernel and the standard I/O buffer (when the corresponding read or write is issued) and again between the standard I/O buffer and our line buffer.

### Doubts and Solutions
#### Verbatim

Section 5.4 on line buffering [p145]

> Second, whenever input is requested through the standard I/O library from either (a) an unbuffered stream or (b) a line-buffered stream (that requires data to be requested from the kernel), all line-buffered output streams are flushed. The reason for the qualifier on (b) is that the requested data may already be in the buffer, which doesn’t require data to be read from the kernel. Obviously, any input from an unbuffered stream, item (a), requires data to be obtained from the kernel.

Section 5.8 Standard I/O Efficiency [p155]

> The version using line-at-a-time I/O is almost twice as fast as the version using character-at-a-time I/O. If the fgets and fputs functions are implemented using getc and putc, then we would expect the timing to be similar to the getc version. Actually, we might expect the line-at-a-time version to take longer, since we would be adding the overhead of 200 million extra function calls to the existing 6 million ones.

Section 5.14 on Memory Stream [p172]
> Third, a null byte is written at the current position in the stream whenever we increase the amount of data in the stream’s buffer and call fclose, fflush, fseek, fseeko, or fsetpos.
