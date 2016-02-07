### **0x200 Programming**

**Hacker** is a term for both those who write code and those who exploit it. <u>Even though these two groups of hackers have different end goals, both groups use similar problem-solving techniques.</u> <u>An understanding of programming helps those who exploit, and an understanding of exploitation helps those who program.</u> <u>Hacking is really just the act of finding a clever and counterintuitive solution to a problem.</u>

##### **Hacks and Programming Hacks** *

The hacks found in program exploits usually use the rules of the computer to bypass security in ways never intended. Programming hacks are similar, but the final goal is efficiency or smaller source code, not necessarily a security compromise.

Programs that are small, efficient, and neat to accomplish a given task are said to have *elegance*, and the clever and inventive solutions that tend to lead to this efficiency are called *hacks*.

In the business world, more importance is placed on churning out functional code than on achieving clever hacks and elegance. [p6]

##### **What are Hackers** *

Hackers can be:

* Hobbyists whose end goal isn’t to make a profit but to squeeze every possible bit of functionality out of their old Commodore 64s,
* Exploit writers who need to write tiny and amazing pieces of code to slip through narrow security cracks
* Anyone else who appreciates the pursuit and the challenge of finding the best possible solution.

Hackers are people who get excited about programming and really appreciate the beauty of an elegant piece of code or the ingenuity of a clever hack.

An understanding of programming is a prerequisite to understanding how programs can be exploited.

### What Is Programming?

A program is a series of statements written in a specific language.

* An **assembler** translates assembly language into machine-readable code.
* A **compiler** converts a high-level language into machine language.

### Pseudo-code

Programmers have yet another form of programming language called [pseudo-code](https://en.wikipedia.org/wiki/Pseudocode). Pseudo-code is simply English arranged with a general structure similar to a high-level language.

### Control Structures
### More Fundamental Programming Concepts

### Getting Your Hands Dirty

For this book, Linux and an x86-based processor is used exclusively.

The `firstprog.c` program is a simple piece of C code that will print “Hello, world!” 10 times.

<small>[firstprog.c](https://github.com/shichao-an/hacking/blob/master/firstprog.c)</small>

```c
#include <stdio.h>

int main()
{
  int i;
  for(i=0; i < 10; i++)
  {
    printf("Hello World!\n");
  }
}
```

The first line is a C syntax that tells the compiler to include headers for a standard input/output (I/O) library named `stdio`. This header file is added to the program when it is compiled. It is located at `/usr/include/stdio.h`. A function prototype is needed for `printf()` before it can be used. This function prototype (along with many others) is included in the `stdio.h` header file. A lot of the power of C comes from its extensibility and libraries.

The [GNU Compiler Collection](https://en.wikipedia.org/wiki/GNU_Compiler_Collection) (GCC) is a free C compiler that translates C into machine language that a processor can understand. The outputted translation
is an executable binary file, which is called a.out by default.

```shell-session
$ gcc firstprog.c
$ ls -l a.out
-rwxr-xr-x 1 reader reader 6621 2007-09-06 22:16 a.out
$ ./a.out
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
```

#### The Bigger Picture

This has all been stuff you would learn in an elementary programming class. Most introductory programming classes just teach how to read and write C. Though being fluent in C is very useful and is enough to make you a decent programmer, but it’s only a piece of the bigger picture. <u>Most programmers learn the language from the top down and never see the big picture.</u>

Hackers get their edge from knowing how all the pieces interact within this bigger picture. To see the bigger picture in the realm of programming, simply realize that C code is meant to be compiled. The code can’t actually do anything until it’s compiled into an executable binary file. <u>Thinking of C-source as a program is a common misconception that is exploited by hackers every day.</u>

The binary `a.out`’s instructions are written in machine language. Compilers translate the language of C code into machine language for a variety of processor architectures. In this case, the processor is in a family that uses the [x86](https://en.wikipedia.org/wiki/X86) architecture. There are also [Sparc](https://en.wikipedia.org/wiki/SPARC) processor architectures (used in Sun Workstations) and the [PowerPC](https://en.wikipedia.org/wiki/PowerPC) processor architecture (used in pre-Intel Macs). The compiler acts as a middle ground: translating C code into machine language for the target architecture.

The average programmer is only concerned with source code, but a hacker realizes that the compiled program is what actually gets executed out in the real world. With a better understanding of how the CPU operates, a hacker can manipulate the programs that run on it.

The GNU development tools include a program called [objdump](https://en.wikipedia.org/wiki/Objdump), which can be used to examine compiled binaries. Let’s look at the machine code the `main()` function was translated into.

```shell-session
 $ objdump -D a.out | grep -A20 main.:
08048374 <main>:
 8048374: 55 push %ebp
 8048375: 89 e5 mov %esp,%ebp
 8048377: 83 ec 08 sub $0x8,%esp
 804837a: 83 e4 f0 and $0xfffffff0,%esp
 804837d: b8 00 00 00 00 mov $0x0,%eax
 8048382: 29 c4 sub %eax,%esp
 8048384: c7 45 fc 00 00 00 00 movl $0x0,0xfffffffc(%ebp)
 804838b: 83 7d fc 09 cmpl $0x9,0xfffffffc(%ebp)
 804838f: 7e 02 jle 8048393 <main+0x1f>
 8048391: eb 13 jmp 80483a6 <main+0x32>
 8048393: c7 04 24 84 84 04 08 movl $0x8048484,(%esp)
 804839a: e8 01 ff ff ff call 80482a0 <printf@plt>
 804839f: 8d 45 fc lea 0xfffffffc(%ebp),%eax
 80483a2: ff 00 incl (%eax)
 80483a4: eb e5 jmp 804838b <main+0x17>
 80483a6: c9 leave
 80483a7: c3 ret
 80483a8: 90 nop
 80483a9: 90 nop
 80483aa: 90 nop
```

The output is piped into `grep` with the command-line option to only display 20 lines after the regular expression `main.`:. Each byte is represented in hexadecimal notation, which is a base-16 numbering system. This is a convenient notation since a byte contains 8 bits, and each byte can be described with 2 hexadecimal digits.

The numbers such as `0x8048374` on the far left are memory addresses. Memory can be thought of as a row of bytes, each with its own memory address. Older Intel x86 processors use a 32-bit addressing scheme, while newer ones use a 64-bit one. The 32-bit processors have 2<sup>32</sup> (or 4,294,967,296) possible addresses, while the 64-bit ones have 2<sup>64</sup> (1.84467441 × 10<sup>19</sup>) possible addresses. The 64-bit processors can run in 32-bit compatibility mode, which allows them to run 32-bit code quickly.

#### The x86 Processor
