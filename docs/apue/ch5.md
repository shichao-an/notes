## Chapter 5. Standard I/O Library

The standard I/O library handles such details as buffer allocation and performing I/O in optimal-sized chunks.

### Streams and `FILE` Objects

Standard I/O file streams can be used with both **single-byte** and **multibyte** ("wide") character sets. A stream’s orientation determines whether the characters that are read and written are single byte or multibyte. 

* This book deals only with **byte-oriented** (single byte) streams.
* This book refers to a pointer to a `FILE` object, the type `FILE *`, as a *file pointer*.

### Standard Input, Standard Output, and Standard Error

Three streams are predefined and automatically available to a process. They refer to file descriptors `STDIN_FILENO`, `STDOUT_FILENO`, and `STDERR_FILENO` (defined in `<unistd.h>`) [p9]. These three standard I/O streams are referenced through the predefined file pointers `stdin`, `stdout`,and `stderr`(defined in `<stdio.h>`).

### Buffering

1. **Fully buffered**
2. **Line buffered**
3. **Unbuffered**

Most implementations default to the following types of buffering:

* Standard error is always unbuffered.
* All other streams are line buffered if they refer to a terminal device; otherwise, they are fully buffered.

<script src="https://gist.github.com/shichao-an/70e28ba25f1b7276e834.js"></script>

* `setbuf`: *buf* must point to a buffer of length `BUFSIZ`, a constant defined in `<stdio.h>`
* `setvbuf`: type of buffering is specified with `_IOFBF`, `_IOLBF`, `_IONBF`.

The GNU C librarys use the value from the `st_blksize` member of the `stat` structure to determine the optimal standard I/O buffer size.

The `fflush` function causes any unwritten data for the stream to be passed to the kernel. If **fp** is `NULL`, `fflush` causes all output streams to be flushed.

<script src="https://gist.github.com/shichao-an/3fea32272cd9e1b574c6.js"></script>

* `fdopen` function is often used with descriptors returned by the functions that create pipes and network communication channels, because these special types of files cannot be opened with the `fopen` function.

### Doubts and Solutions
#### Verbatim

Section 5.4 on line buffering [p145]

> Second, whenever input is requested through the standard I/O library from either (a) an unbuffered stream or (b) a line-buffered stream (that requires data to be requested from the kernel), all line-buffered output streams are flushed. The reason for the qualifier on (b) is that the requested data may already be in the buffer, which doesn’t require data to be read from the kernel. Obviously, any input from an unbuffered stream, item (a), requires data to be obtained from the kernel.
