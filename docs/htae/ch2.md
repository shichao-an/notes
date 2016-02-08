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

##### **`objdump`** *

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

##### **Description of output from `objdump`** *

The output is piped into `grep` with the command-line option to only display 20 lines after the regular expression `main.`:. Each byte is represented in hexadecimal notation, which is a base-16 numbering system. This is a convenient notation since a byte contains 8 bits, and each byte can be described with 2 hexadecimal digits.

* The numbers such as `0x8048374` on the far left are memory addresses.
    * Memory can be thought of as a row of bytes, each with its own memory address. Older Intel x86 processors use a 32-bit addressing scheme, while newer ones use a 64-bit one. The 32-bit processors have 2<sup>32</sup> (or 4,294,967,296) possible addresses, while the 64-bit ones have 2<sup>64</sup> (1.84467441 × 10<sup>19</sup>) possible addresses. The 64-bit processors can run in 32-bit compatibility mode, which allows them to run 32-bit code quickly.
* The hexadecimal bytes in the middle are the machine language instructions for the x86 processor. The machine code is displayed as hexadecimal bytes and each instruction is put on its own line.
* The instructions on the far right are in assembly language.

##### **The Assembly Language** *

Unlike C and other compiled languages, assembly language instructions have a direct one-to-one relationship with their corresponding machine language instructions. This means that since every processor architecture has different machine language instructions, each also has a different form of assembly language. Assembly is a way to represent the machine language instructions of the processor.

There are the two main types of assembly language syntax:

* AT&T syntax.
* Intel syntax.

The assembly shown in the output above is AT&T syntax. Nearly all of Linux’s disassembly tools use this syntax by default. It’s easy to recognize AT&T syntax by the cacophony of `%` and `$` symbols prefixing everything. The same code can be shown in Intel syntax by providing an additional command-line option, `-M intel`, to `objdump`, as shown in the output below.

```shell-session
$ objdump -M intel -D a.out | grep -A20 main.:
08048374 <main>:
 8048374: 55 push ebp
 8048375: 89 e5 mov ebp,esp
 8048377: 83 ec 08 sub esp,0x8
 804837a: 83 e4 f0 and esp,0xfffffff0
 804837d: b8 00 00 00 00 mov eax,0x0
 8048382: 29 c4 sub esp,eax
 8048384: c7 45 fc 00 00 00 00 mov DWORD PTR [ebp-4],0x0
 804838b: 83 7d fc 09 cmp DWORD PTR [ebp-4],0x9
 804838f: 7e 02 jle 8048393 <main+0x1f>
 8048391: eb 13 jmp 80483a6 <main+0x32>
 8048393: c7 04 24 84 84 04 08 mov DWORD PTR [esp],0x8048484
 804839a: e8 01 ff ff ff call 80482a0 <printf@plt>
 804839f: 8d 45 fc lea eax,[ebp-4]
 80483a2: ff 00 inc DWORD PTR [eax]
 80483a4: eb e5 jmp 804838b <main+0x17>
 80483a6: c9 leave
 80483a7: c3 ret
 80483a8: 90 nop
 80483a9: 90 nop
 80483aa: 90 nop
```

Intel syntax is much more readable and easier to understand; this book will use this syntax.  Regardless of the assembly language representation, the commands a processor understands are quite simple. These instructions consist of an operation and sometimes additional arguments that describe the destination and/or the source for the operation. These operations move memory around, perform some sort of basic math, or interrupt the processor to get it to do something else. In the end, that’s all a computer processor can really do.

Processors also have their own set of special variables called [registers](https://en.wikipedia.org/wiki/Processor_register). Most of the instructions use these registers to read or write data, so understanding the registers of a processor is essential to understanding the instructions.

#### The x86 Processor

The x86 processor has several registers, which are like internal variables for the processor. The GNU development tools also include a debugger called [GDB](https://en.wikipedia.org/wiki/GNU_Debugger). Debuggers are used by programmers to step through compiled programs, examine program memory, and view processor registers. A debugger can view the execution from all angles, pause it, and change anything along the way. [p23]

Below, GDB is used to show the state of the processor registers right before the program starts.

```shell-session
$ gdb -q ./a.out
Using host libthread_db library "/lib/tls/i686/cmov/libthread_db.so.1".
(gdb) break main
Breakpoint 1 at 0x804837a
(gdb) run
Starting program: /home/reader/booksrc/a.out
Breakpoint 1, 0x0804837a in main ()
(gdb) info registers
eax 0xbffff894 -1073743724
ecx 0x48e0fe81 1222704769
edx 0x1 1
ebx 0xb7fd6ff4 -1208127500
esp 0xbffff800 0xbffff800
ebp 0xbffff808 0xbffff808
esi 0xb8000ce0 -1207956256
edi 0x0 0
eip 0x804837a 0x804837a <main+6>
eflags 0x286 [ PF SF IF ]
cs 0x73 115
ss 0x7b 123
ds 0x7b 123
es 0x7b 123
fs 0x0 0
gs 0x33 51
(gdb) quit
The program is running. Exit anyway? (y or n) y
```

A breakpoint is set on the `main()` function so execution will stop right before our code is executed. Then GDB runs the program, stops at the breakpoint, and is told to display all the processor registers and their current states.

##### **EAX, ECX, EDX, and EBX registers** *

The first four registers (EAX, ECX, EDX, and EBX) are known as general-purpose registers. These are called the *Accumulator*, *Counter*, *Data*, and *Base* registers, respectively. They are used for a variety of purposes, but they mainly act as temporary variables for the CPU when it is executing machine instructions.

##### **ESP, EBP, ESI, and EDI registers** *

The second four registers (ESP, EBP, ESI, and EDI) are also general-purpose registers, but they are sometimes known as pointers and indexes. These stand for *Stack Pointer*, *Base Pointer*, *Source Index*, and *Destination Index*, respectively.

* The ESP and EBP registers are called pointers because they store 32-bit addresses, which essentially point to that location in memory. These registers are fairly important to program execution and memory management.
* The ESI and EDI registers are also technically pointers, which are commonly used to point to the source and destination when data needs to be read from or written to. There are load and store instructions that use these registers, but for the most part, these registers can be thought of as just simple general-purpose registers.

##### **EIP register** *

The EIP register is the *Instruction Pointer* register, which points to the current instruction the processor is reading. This register is quite important and will be used a lot while debugging. Currently, it points to a memory address at 0x804838a.

##### **EFLAGS register** *

The remaining EFLAGS register actually consists of several bit flags that are used for comparisons and memory segmentations. The actual memory is split into several different segments and these registers keep track of that. For the most part, these registers can be ignored since they rarely need to be accessed directly.

#### Assembly Language

To use Intel syntax assembly language, our tools must be configured to use this syntax. Inside GDB, the disassembly syntax can be set to Intel by `typing set disassembly intel` or `set dis intel`. You can configure this setting to run every time GDB starts up by putting the command in the file `.gdbinit` in your home directory.

```shell-session
$ gdb -q
(gdb) set dis intel
(gdb) quit
$ echo "set dis intel" > ~/.gdbinit
```

The assembly instructions in Intel syntax generally follow this style:

```text
operation <destination>, <source>
```

The destination and source values will either be a register, a memory address, or a value. The operations are usually intuitive mnemonics. For example:

* `mov` will move a value from the source to the destination.
* `sub` will subtract.
* `inc` will increment.

The instructions below will move the value from ESP to EBP and then subtract 8 from ESP (storing the result in ESP).

```text
8048375: 89 e5         mov ebp,esp
8048377: 83 ec 08      sub esp,0x8
```

There are also operations that are used to control the flow of execution.

* The `cmp` operation is used to compare values.
* Basically any operation beginning with `j` is used to jump to a different part of the code (depending on the result of the comparison).

In the example below:

* `cmp` compares a 4-byte value located at EBP minus 4 with the number 9.
* The next instruction `jle` is shorthand for "jump if less than or equal to", referring to the result of the previous comparison. If that value is less than or equal to 9, execution jumps to the instruction at 0x8048393. Otherwise, execution flows to the next instruction
* `jmp` means an unconditional jump. If the value isn’t less than or equal to 9, execution will jump to 0x80483a6.

```text
804838b: 83 7d fc 09   cmp DWORD PTR [ebp-4],0x9
804838f: 7e 02         jle 8048393 <main+0x1f>
8048391: eb 13         jmp 80483a6 <main+0x32>
```

The `-g` flag can be used by the GCC compiler to include extra debugging information, which will give GDB access to the source code.

```shell-session
$ gcc -g firstprog.c
$ ls -l a.out
-rwxr-xr-x 1 matrix users 11977 Jul 4 17:29 a.out
$ gdb -q ./a.out
Using host libthread_db library "/lib/libthread_db.so.1".
(gdb) list
1 #include <stdio.h>
2
3 int main()
4 {
5 int i;
6 for(i=0; i < 10; i++)
7 {
8 printf("Hello, world!\n");
9 }
10 }
(gdb) disassemble main
Dump of assembler code for function main():
0x08048384 <main+0>: push ebp
0x08048385 <main+1>: mov ebp,esp
0x08048387 <main+3>: sub esp,0x8
0x0804838a <main+6>: and esp,0xfffffff0
0x0804838d <main+9>: mov eax,0x0
0x08048392 <main+14>: sub esp,eax
0x08048394 <main+16>: mov DWORD PTR [ebp-4],0x0
0x0804839b <main+23>: cmp DWORD PTR [ebp-4],0x9
0x0804839f <main+27>: jle 0x80483a3 <main+31>
0x080483a1 <main+29>: jmp 0x80483b6 <main+50>
0x080483a3 <main+31>: mov DWORD PTR [esp],0x80484d4
0x080483aa <main+38>: call 0x80482a8 <_init+56>
0x080483af <main+43>: lea eax,[ebp-4]
0x080483b2 <main+46>: inc DWORD PTR [eax]
0x080483b4 <main+48>: jmp 0x804839b <main+23>
0x080483b6 <main+50>: leave
0x080483b7 <main+51>: ret
End of assembler dump.
(gdb) break main
Breakpoint 1 at 0x8048394: file firstprog.c, line 6.
(gdb) run
Starting program: /hacking/a.out
Breakpoint 1, main() at firstprog.c:6
6 for(i=0; i < 10; i++)
(gdb) info register eip
eip 0x8048394 0x8048394
(gdb)
```

1. The source code is listed and the disassembly of the `main()` function is displayed.
2. A breakpoint is set at the start of `main()`, and the program is run.
    * This breakpoint tells the debugger to pause the execution when it gets to that point. Since the breakpoint has been set at the start of the `main()` function, the program hits the breakpoint and pauses before actually executing any instructions in `main()`.
3. The value of EIP (the Instruction Pointer) is displayed.

Notice that EIP contains a memory address (i.e. 0x8048394) that points to an instruction in the `main()` function’s disassembly. The instructions before this (from 0x08048384 to 0x08048392) are collectively known as the [function prologue](https://en.wikipedia.org/wiki/Function_prologue) and are generated by the compiler to set up memory for the rest of the `main()` function’s local variables. Part of the reason why variables need to be declared in C is to aid the construction of this section of code. The debugger knows this part of the code is automatically generated and is smart enough to skip over it.

##### **Examining memory with GDB's *examine* command** *

The GDB provides a direct method to examine memory, using the command `x`, which is short for *examine*. Examining memory is a critical skill for any hacker. With a debugger like GDB, every aspect of a program’s execution can be deterministically examined, paused, stepped through, and repeated as often as needed. Since a running program is mostly just a processor and segments of memory, examining memory is the first way to look at what’s really going on.

The *examine* command expects two arguments:

* The location in memory to examine.
* How to display that memory.

The display format also uses a single-letter shorthand, which is optionally preceded by a count of how many items to examine. Some common format letters are as follows:

* `o`: Display in octal.
* `x`: Display in hexadecimal.
* `u`: Display in unsigned, standard base-10 decimal.
* `t`: Display in binary.

In the following example, the current address of the EIP register is used. Shorthand commands are often used with GDB, and even `info register eip` can be shortened to just `i r eip`.

```text
(gdb) i r eip
eip 0x8048384 0x8048384 <main+16>
(gdb) x/o 0x8048384
0x8048384 <main+16>: 077042707
(gdb) x/x $eip
0x8048384 <main+16>: 0x00fc45c7
(gdb) x/u $eip
0x8048384 <main+16>: 16532935
(gdb) x/t $eip
0x8048384 <main+16>: 00000000111111000100010111000111
(gdb)
```


