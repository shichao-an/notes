### **x86 Assembly**

>  If you don't assemble the (assembly) code, it's complete gibberish to the computer.
> <small>Wikibooks</small>

### Introduction

<small>[Introduction](https://en.wikibooks.org/wiki/X86_Assembly/Introduction)</small>

#### Why Learn Assembly?

* With assembly, the programmer can precisely track the flow of data and execution in a program in a mostly human-readable form.
    * Debuggers will frequently only show program code in assembly language.
* Assembly language is also the preferred tool for implementing some low-level tasks, such as bootloaders and low-level kernel components. Code written in assembly has less overhead than code written in high-level languages
    * As hardware manufacturers such as Intel and AMD add new features and new instructions to their processors, often times the only way to access those features is to use assembly routines, at least until the major compiler vendors add support for those features.

### Basic FAQ

<small>[Basic FAQ](https://en.wikibooks.org/wiki/X86_Assembly/Basic_FAQ)</small>

#### How Computer Reads Assembly

The computer cannot read the assembly language that you write. Your assembler will convert the assembly language into a form of binary information called "machine code" that your computer uses to perform its operations.

#### Platform differences

The basic x86 machine code is dependent only on the processor. The x86 versions of Windows and Linux are obviously built on the x86 machine code. There are a few differences between Linux and Windows programming in x86 Assembly:

1. On a Linux computer, the most popular assemblers are the GAS assembler, which uses the AT&T syntax for writing code, and the Netwide Assembler, also known as NASM, which uses a syntax similar to MASM.
2. On a Windows computer, the most popular assembler is MASM, which uses the Intel syntax.
3. The available software interrupts, and their functions, are different on Windows and Linux.
4. The available code libraries are different on Windows and Linux.

### x86 Family

<small>[x86 Family](https://en.wikibooks.org/wiki/X86_Assembly/X86_Family)</small>

The term "x86" can refer both to an instruction set architecture and to microprocessors which implement it. The name x86 is derived from the fact that many of Intel's early processors had names ending in "86".

The x86 instruction set architecture originated at Intel and has evolved over time by the addition of new instructions as well as the expansion to 64-bits. As of 2009, x86 primarily refers to [IA-32](https://en.wikipedia.org/wiki/IA-32) (Intel Architecture, 32-bit) and/or [x86-64](https://en.wikipedia.org/wiki/X86-64), the extension to 64-bit computing.

Versions of the x86 instruction set architecture have been implemented by Intel, AMD and several other vendors, with each vendor having its own family of x86 processors.

### x86 Architecture

<small>[x86 Architecture](https://en.wikibooks.org/wiki/X86_Assembly/X86_Architecture)</small>

#### The x86 Architecture

The x86 architecture has:

* 8 General-Purpose Registers (GPR)
* 6 Segment Registers
* 1 Flags Register
* 1 Instruction Pointer

64-bit x86 has additional registers.

#### General-Purpose Registers (GPR) (32-bit naming conventions)

The 8 GPRs are:

1. Accumulator register (AX). Used in arithmetic operations.
2. Counter register (CX). Used in shift/rotate instructions and loops.
3. Data register (DX). Used in arithmetic operations and I/O operations.
4. Base register (BX). Used as a pointer to data (located in segment register DS, when in segmented mode).
5. Stack Pointer register (SP). Pointer to the top of the stack.
6. Stack Base Pointer register (BP). Used to point to the base of the stack.
7. Source Index register (SI). Used as a pointer to a source in stream operations.
8. Destination Index register (DI). Used as a pointer to a destination in stream operations.

The order in which they are listed here is for a reason: it is the same order that is used in a push-to-stack operation, which will be covered later.

All registers can be accessed in 16-bit, 32-bit and 64-bit modes:

* 16-bit: the register is identified by its two-letter abbreviation from the list above. For example, 'AX'.
* 32-bit: the two-letter abbreviation is prefixed with an 'E' (extended). For example, 'EAX'.
* 64-bit: the two-letter abbreviation is prefixed with an 'R'. For example, 'RAX'.

It is also possible to address the first four registers (AX, CX, DX and BX) in their size of 16-bit as two 8-bit halves:

* The least significant byte (LSB), or low half, is identified by replacing the 'X' with an 'L'.
& The most significant byte (MSB), or high half, uses an 'H' instead.

For example, CL is the LSB of the counter register, whereas CH is its MSB.

The following table summarizes five ways to access the accumulator, counter, data and base registers: 64-bit, 32-bit, 16-bit, 8-bit LSB, and 8-bit MSB:

[![Five ways to access the accumulator, counter, data and base registers: 64-bit, 32-bit, 16-bit, 8-bit LSB, and 8-bit MSB](figure_1_600.png)](figure_1.png "Five ways to access the accumulator, counter, data and base registers: 64-bit, 32-bit, 16-bit, 8-bit LSB, and 8-bit MSB")

#### Segment Registers

The 6 Segment Registers are:

* Stack Segment (SS). Pointer to the stack.
* Code Segment (CS). Pointer to the code.
* Data Segment (DS). Pointer to the data.
* Extra Segment (ES). Pointer to extra data ('E' stands for 'Extra').
* F Segment (FS). Pointer to more extra data ('F' comes after 'E').
* G Segment (GS). Pointer to still more extra data ('G' comes after 'F').

Most applications on most modern operating systems (FreeBSD, Linux or Microsoft Windows) use a memory model that points nearly all segment registers to the same place and uses paging instead, effectively disabling their use. Typically the use of FS or GS is an exception to this rule, instead being used to point at thread-specific data.

#### EFLAGS Register

The EFLAGS is a 32-bit register used as a collection of bits representing Boolean values to store the results of operations and the state of the processor.

[![EFLAGS bits](figure_2_600.png)](figure_2.png "EFLAGS bits")

The bits named 0 and 1 are reserved bits and shouldn't be modified.

The different use of these flags are:

* 0 CF : Carry Flag. Set if the last arithmetic operation carried (addition) or borrowed (subtraction) a bit beyond the size of the register. This is then checked when the operation is followed with an add-with-carry or subtract-with-borrow to deal with values too large for just one register to contain.
* 2 PF : Parity Flag. Set if the number of set bits in the least significant byte is a multiple of 2.
* 4 AF : Adjust Flag. Carry of Binary Code Decimal (BCD) numbers arithmetic operations.
* 6 ZF : Zero Flag. Set if the result of an operation is Zero (0).
* 7 SF : Sign Flag. Set if the result of an operation is negative.
* 8 TF : Trap Flag. Set if step by step debugging.
* 9 IF : Interruption Flag. Set if interrupts are enabled.
* 10 DF : Direction Flag. Stream direction. If set, string operations will decrement their pointer rather than incrementing it, reading memory backwards.
* 11 OF : Overflow Flag. Set if signed arithmetic operations result in a value too large for the register to contain.
* 12-13 IOPL : I/O Privilege Level field (2 bits). I/O Privilege Level of the current process.
* 14 NT : Nested Task flag. Controls chaining of interrupts. Set if the current process is linked to the next process.
* 16 RF : Resume Flag. Response to debug exceptions.
* 17 VM : Virtual-8086 Mode. Set if in 8086 compatibility mode.
* 18 AC : Alignment Check. Set if alignment checking of memory references is done.
* 19 VIF : Virtual Interrupt Flag. Virtual image of IF.
* 20 VIP : Virtual Interrupt Pending flag. Set if an interrupt is pending.
* 21 ID : Identification Flag. Support for CPUID instruction if can be set.

#### Instruction Pointer

The EIP register contains the address of the next instruction to be executed if no branching is done.

EIP can only be read through the stack after a `call` instruction.

#### Memory

The x86 architecture is [little-endian](https://en.wikipedia.org/wiki/Endianness#Little-endian), meaning that multi-byte values are written least significant byte first. (This refers only to the ordering of the bytes, not to the bits.)

[![Little Endian](figure_3.png)](figure_3.png "Little Endian")

The 32 bit value B3B2B1B0<sub>16</sub> on an x86 would be represented in memory as:

```text
+----+----+----+----+
| B0 | B1 |	B2 | B3 |
+----+----+----+----+
```

The 32 bits double word 0x1BA583D4 (the 0x denotes hexadecimal) would be written in memory as:

```text
+----+----+----+----+
| D4 | 83 |	A5 | 1B |
+----+----+----+----+
```

This will be seen as `0xD4 0x83 0xA5 0x1B` when doing a memory dump.

#### Two's Complement Representation

Two's complement is the standard way of representing negative integers in binary. The sign is changed by inverting all of the bits and adding one.

For example,

```text
+----------+------+
| Start:   | 0001 |
+----------+------+
| Invert:  | 1110 |
+----------+------+
| Add One: | 1111 |
+----------+------+
```

* 0001 represents decimal 1
* 1111 represents decimal -1

#### Addressing modes

The addressing mode indicates how the operand is presented.

##### **Register Addressing**

Operand address R is in the address field.

```nasm
mov ax, bx  ; moves contents of register bx into ax
```

##### **Immediate**

Aactual value is in the field.

```nasm
mov ax, 1   ; moves value of 1 into register ax
```

Or:

```nasm
mov ax, 010Ch ; moves value of 0x010C into register ax
```

##### **Direct memory addressing**

Operand address is in the address field.

```nasm
.data
my_var dw 0abcdh ; my_var = 0xabcd
.code
mov ax, [my_var] ; copy my_var content in ax (ax=0xabcd)
```

##### **Direct offset addressing**

Uses arithmetics to modify address.

```nasm
byte_tbl db 12,15,16,22,..... ; Table of bytes
mov al,[byte_tbl+2]
mov al,byte_tbl[2] ; same as the former
```

##### **Register Indirect**

Field points to a register that contains the operand address.

```nasm
mov ax,[di]
```

The registers used for indirect addressing are BX, BP, SI, DI

##### **Base-index**

```nasm
mov ax,[bx + di]
```

For example, if we are talking about an array, BX contains the address of the beginning of the array, and DI contains the index into the array.

##### **Base-index with displacement**

```nasm
mov ax,[bx + di + 10]
```

#### General-Purpose Registers (GPR) (64-bit naming conventions)

<small>[16 32 and 64 Bits](https://en.wikibooks.org/wiki/X86_Assembly/16_32_and_64_Bits)</small>

64-bit x86 adds 8 more general-purpose registers, named R8, R9, R10 and so on up to R15. It also introduces a new naming convention that must be used for these new registers and can also be used for the old ones (except that AH, CH, DH and BH have no equivalents). In the new convention:

* R0 is RAX.
* R1 is RCX.
* R2 is RDX.
* R3 is RBX.
* R4 is RSP.
* R5 is RBP.
* R6 is RSI.
* R7 is RDI.
* R8, R9, R10, R11, R12, R13, R14, R15 are the new registers and have no other names.
* R0D~R15D are the lowermost 32 bits of each register. For example, R0D is EAX.
* R0W~R15W are the lowermost 16 bits of each register. For example, R0W is AX.
* R0L~R15L are the lowermost 8 bits of each register. For example, R0L is AL.

For 128-bit registers, see [SSE](https://en.wikibooks.org/wiki/X86_Assembly/SSE).

### Stack

The stack is a Last In First Out (LIFO) data structure; data is pushed onto it and popped off of it in the reverse order.

```nasm
mov ax, 006Ah
mov bx, F79Ah
mov cx, 1124h
; Push the value in AX, BX, and CX onto the top of the stack
push ax
push bx
push cx
```

Now the stack has $006A, $F79A, and $1124.

```nasm
call do_stuff
```

Do some stuff. The function is not forced to save the registers it uses, hence us saving them.

```nasm
pop cx ;Pop the last element pushed onto the stack into CX, $1124; the stack now has $006A and $F79A.
pop bx ;Pop the last element pushed onto the stack into BX, $F79A; the stack now has just $006A.
pop ax ;Pop the last element pushed onto the stack into AX, $006A; the stack is empty.
```

The stack has two common uses:

* Passing arguments to functions or procedures and also keeping track of control flow when the `call` instruction is used.
* Temporarily saving registers.

### CPU Operation Modes

<small>[CPU Operation Modes](https://en.wikibooks.org/wiki/X86_Assembly/X86_Architecture#CPU_Operation_Modes)</small>

#### Real Mode

Real Mode is a holdover from the original Intel 8086. The Intel 8086 accessed memory using 20-bit addresses. But, as the processor itself was 16-bit, Intel invented an addressing scheme that provided a way of mapping a 20-bit addressing space into 16-bit words. Today's x86 processors start in the so-called Real Mode, which is an operating mode that mimics the behavior of the 8086, with some very tiny differences, for backwards compatibility.

#### Protected Mode

##### **Flat Memory Model**

If programming in a modern operating system (such as Linux, Windows), you are basically programming in flat 32-bit mode. Any register can be used in addressing, and it is generally more efficient to use a full 32-bit register instead of a 16-bit register part. Additionally, segment registers are generally unused in flat mode, and it is generally a bad idea to touch them.

##### **Multi-Segmented Memory Model**

Using a 32-bit register to address memory, the program can access (almost) all of the memory in a modern computer. For earlier processors (with only 16-bit registers) the segmented memory model was used. The 'CS', 'DS', and 'ES' registers are used to point to the different chunks of memory. For a small program (small model) the CS=DS=ES. For larger memory models, these 'segments' can point to different locations.

### Comments

When writing code, it is very helpful to use some comments explaining what is going on. A comment is a section of regular text that the assembler ignores when turning the assembly code into the machine code. In assembly comments are usually denoted with a semicolon ";", although GAS uses "#" for single line comments and "/* ... */" for multi-line comments.

For example:

```nasm
Label1:
   mov ax, bx    ;move contents of bx into ax
   add ax, bx    ;add the contents of bx into ax
   ...
```

### 16 32 and 64 Bits

<small>[16 32 and 64 Bits](https://en.wikibooks.org/wiki/X86_Assembly/16_32_and_64_Bits)</small>

### Intrinsic Data Types

Strictly speaking, assembly has no predefined data types like higher-level programming languages. Any general purpose register can hold any sequence of two or four bytes, whether these bytes represent numbers, letters, or other data. In the same way, there are no concrete types assigned to blocks of memory; you can assign to them whatever value you like.

That said, one can group data in assembly into two categories: integer and floating point. While you could load a floating point value into a register and treat it like an integer, the results would be unexpected, so it is best to keep them separate.

#### Integer

An integer represents a whole number, either positive or negative.

* Under the 8086 architecture, it originally came in 8-bit and 16-bit sizes, which served the most basic operations.
* Later, starting with the 80386, the data bus was expanded to support 32-bit operations and thus allow operations on integers of that size.
* The newest systems under the x86 architecture support 64-bit instructions; however, this requires a 64-bit operating system for optimal effect.

Some assembly instructions behave slightly differently in regards to the sign bit; as such, there is a minor distinction between signed and unsigned integers.

#### Floating Point Numbers

Floating point numbers are used to approximate the **real numbers** that usually contain digits before and after the decimal point (like π, 3.14159...). Unlike integers where the decimal point is understood to be after all digits, in floating point numbers the decimal point floats anywhere in the sequence of digits. The precision of floating point numbers is limited and thus a number like π can only be represented approximately.

Originally, floating point was not part of the main processor, requiring the use of emulating software. However, there were floating point coprocessors that allowed operations on this data-type, and starting with the 486DX, were integrated directly with the CPU.

As such, floating point operations are not necessarily compatible with all processors. If you need to perform this type of arithmetic, you may want to use a software library as a backup code path.

### x86 Instructions

#### Conventions

* [GAS Syntax](https://en.wikibooks.org/wiki/X86_Assembly/GAS_Syntax)
* [MASM Syntax](https://en.wikibooks.org/wiki/X86_Assembly/MASM_Syntax)

Instructions that take no operands:

<pre>
<b>Instr</b>
</pre>

Instructions that take 1 operand:

<pre>
<b>Instr</b> arg
</pre>

Instructions that take 2 operands. Notice how the format of the instruction is different for different assemblers.

<pre>
<b>Instr</b> src, dest	  # <a href="https://en.wikibooks.org/wiki/X86_Assembly/GAS_Syntax">GAS Syntax</a>
<b>Instr</b> dest, src	  ; <a href="MASM Syntax">Intel syntax</a>
</pre>

Instructions that take 3 operands. Notice how the format of the instruction is different for different assemblers.

<pre>
<b>Instr</b> aux, src, dest	  # <a href="https://en.wikibooks.org/wiki/X86_Assembly/GAS_Syntax">GAS Syntax</a>
<b>Instr</b> dest, src, aux	  ; <a href="MASM Syntax">Intel syntax</a>
</pre>

#### Suffixes

<small>[Operation Suffixes](https://en.wikibooks.org/wiki/X86_Assembly/GAS_Syntax#Operation_Suffixes)</small>

Some instructions require the use of suffixes to specify the size of the data which will be the subject of the operation, such as:

* b (byte) = 8 bits
* w (word) = 16 bits
* l (long) = 32 bits
* q (quad) = 64 bits

An example of the usage with the `mov` instruction on a 32-bit architecture, GAS syntax:

```gas
movl $0x000F, %eax          # Store the value F into the eax register
```

### Data Transfer Instructions

#### Move: `mov`

```gas
mov src, dest  # GAS Synatx
```
```nasm
mov dest, src  ; Intel Syntax
```

The `mov` instruction copies the `src` operand into the `dest` operand.

**Operands**

* `src`:
    * Immediate
    * Register
    * Memory
* `dest`:
    * Register
    * Memory

**Modified flags**: No FLAGS are modified by this instruction.

#### Data swap: `xchg` and `cmpxchg`

```gas
xchg src, dest
```
```nasm
xchg dest, src
```

The `xchg` instruction swaps the `src` operand with the dest operand. It's like doing three move operations: from dest to a temporary (another register), then from `src` to dest, then from the temporary to `src`, except that no register needs to be reserved for temporary storage.

If one of the operands is a memory address, then the operation has an implicit `LOCK` prefix, that is, the exchange operation is atomic. This can have a large performance penalty.

It's also worth noting that the common `NOP` (no op) instruction, `0x90`, is the opcode for `xchgl %eax, %eax`.

**Operands**.

* `src`
    * Register
    * Memory
* `dest`
    * Register
    * Memory (only one operand can be in memory: the other must be a register)

**Modified flags**: No FLAGS are modified by this instruction.

```gas
cmpxchg arg2, arg1
```
```nasm
cmpxchg arg1, arg2
```

Compare and exchange.

#### Move with zero extend

```gas
movz src, dest
```
```nasm
movzx dest, src
```

#### Sign Extend

```gas
movs src, dest
```
```nasm
movsx dest, src
```

#### Move String

```nasm
movsb
```

`movsb`: Move byte

```nasm
movsw
```

`movsw`: Move word

#### Load Effective Address

```gas
lea src, dest
```
```nasm
lea dest, src
```

### Control Flow Instructions

Almost all programming languages have the ability to change the order in which statements are evaluated, and assembly is no exception. The instruction pointer (EIP) register contains the address of the next instruction to be executed. To change the flow of control, the programmer must be able to modify the value of EIP. This is where control flow functions come in.

#### Comparison: `test` and `cmp`

```gas
test arg1, arg2
```
```nasm
test arg2, arg1
```

Performs a bit-wise logical AND on `arg1` and `arg2` the result of which we will refer to as Temp and sets the ZF (zero), SF (sign) and PF (parity) flags based on `Temp`. `Temp` is then discarded.

```gas
cmp arg2, arg1
```
```nasm
cmp arg1, arg2
```

#### Jump Instructions
##### **Unconditional Jumps**

```nasm
jmp loc
```

##### **Jump on Equality**

```nasm
je loc
```

##### **Jump on Inequality**

```nasm
jne loc
```

##### **Jump if Greater**

##### **Jump if Less**

##### **Jump on Zero**

##### **Jump on Sign**

#### Function Calls

```nasm
call proc
```

Pushes the address of the next opcode onto the top of the stack, and jumps to the specified location. This is used mostly for subroutines.

```nasm
ret [val]
```

Loads the next value on the stack into EIP, and then pops the specified number of bytes off the stack. If `val` is not supplied, the instruction will not pop any values off the stack after returning.

#### Loop Instructions

```nasm
loop arg
```

The loop instruction decrements ECX and jumps to the address specified by arg unless decrementing ECX caused its value to become zero. For example:

```nasm
mov ecx, 5
start_loop:
; the code here would be executed 5 times
loop start_loop
```

#### Enter and Leave

```nasm
enter arg
```

`enter` creates a stack frame with the specified amount of space allocated on the stack.

```nasm
leave
```
`leave` destroys the current stack frame, and restores the previous frame. Using Intel syntax this is equivalent to:

```nasm
mov esp, ebp
pop ebp
```

#### Other Control Instructions

```nasm
hlt
```

Halts the processor. Execution will be resumed after processing next hardware interrupt, unless IF is cleared.

```nasm
nop
```

No operation. This instruction doesn't do anything, but wastes an instruction cycle in the processor. This instruction is often represented as an XCHG operation with the operands EAX and EAX.

```nasm
lock
```

Asserts #LOCK prefix on next instruction.

```nasm
wait
```

Waits for the FPU to finish its last calculation.

### Arithmetic Instructions
### Logic Instructions
### Shift and Rotate Instructions
### Other Instructions
#### Stack Instructions

```nasm
push arg
```

This instruction decrements the stack pointer and stores the data specified as the argument into the location pointed to by the stack pointer.

```nasm
pop arg
```
This instruction loads the data stored in the location pointed to by the stack pointer into the argument specified and then increments the stack pointer.

#### Flags instructions
### x86 Interrupts

Interrupts are special routines that are defined on a per-system basis. This means that the interrupts on one system might be different from the interrupts on another system. Therefore, it is usually a bad idea to rely heavily on interrupts when you are writing code that needs to be portable.

#### Interrupt Instruction

```nasm
int arg
```

This instruction issues the specified interrupt. For instance:

```nasm
int 0x0A
```

Calls interrupt 10 (0x0A (hex) = 10 (decimal)).

#### Types of Interrupts

There are 3 types of interrupts: Hardware Interrupts, Software Interrupts and Exceptions.

##### **Hardware Interrupts**

Hardware interrupts are triggered by hardware devices. Hardware interrupts are typically asynchronous: their occurrence is unrelated to the instructions being executed at the time they are raised.

##### **Software Interrupts**

Software interrupts are usually used to transfer control to a function in the operating system kernel. Software interrupts are triggered by the instruction `int`. For example, the instruction `int 14h` triggers interrupt `0x14`. The processor then stops the current program, and jumps to the code to handle interrupt 14. When interrupt handling is complete, the processor returns flow to the original program.

##### **Exceptions**

Exceptions are caused by exceptional conditions in the code which is executing, for example an attempt to divide by zero or access a protected memory area. The processor will detect this problem, and transfer control to a handler to service the exception. This handler may re-execute the offending code after changing some value (for example, the zero dividend), or if this cannot be done, the program causing the exception may be terminated.

### x86 Assemblers
### GAS Syntax
### MASM Syntax

### Interfacing with Linux: System Calls

<small>[Interfacing with Linux](https://en.wikibooks.org/wiki/X86_Assembly/Interfacing_with_Linux)</small>

#### Syscalls

Syscalls are the interface between user programs and the Linux kernel. They are used to let the kernel perform various system tasks, such as file access, process management and networking. In the C programming language, you would normally call a wrapper function which executes all required steps or even use high-level features such as the standard IO library.

On Linux, there are several ways to make a syscall. This page will focus on making syscalls by calling a software interrupt using `int $0x80` (x86 and x86_64) or `syscall` (x86_64). This is an easy and intuitive method of making syscalls in assembly-only programs.

#### Making a syscalls

To make a syscall using an interrupt, you have to pass all required information to the kernel by copying them into general purpose registers. Each syscall has a fixed number (note the numbers differ between `int $0x80` and `syscall` in the following text). You specify the syscall by writing the number into the `eax`/`rax` register and pass the parameters by writing them in the appropriate registers before making the actual calls. Parameters are passed in the order they appear in the function signature of the corresponding C wrapper function.

After everything is set up correctly, you call the interrupt using `int $0x80` or `syscall` and the kernel performs the task.

The return or error value of a syscall is written to `eax` or `rax`.

The kernel uses its own stack to perform the actions. The user stack is not touched in any way.

#### `int 0x80`

On both Linux x86 and Linux x86_64 systems you can make a syscall by calling interrupt 0x80 using the `int $0x80` command. Parameters are passed by setting the general purpose registers as following:

Syscall # | Param 1 | Param 2 | Param 3 | Param 4 | Param 5 | Param 6
--------- | ------- | ------- | ------- | ------- | ------- | -------
`eax` | `ebx` | `ecx` | `edx` | `esi` | `edi` | `ebp`

The return value is in the `eax` register.

The syscall numbers are described in the Linux source file [arch/x86/include/asm/unistd_32.h](https://github.com/shichao-an/linux/blob/v2.6.34/arch/x86/include/asm/unistd_32.h).

All registers are preserved during the syscall.

#### `syscall`

The x86_64 architecture introduced a dedicated instruction to make a syscall. It does not access the interrupt descriptor table and is faster. Parameters are passed by setting the general purpose registers as following:

The syscall numbers are described in the Linux source file [arch/x86/include/asm/unistd_64.h](https://github.com/shichao-an/linux/blob/v2.6.34/arch/x86/include/asm/unistd_64.h).

Syscall # | Param 1 | Param 2 | Param 3 | Param 4 | Param 5 | Param 6
--------- | ------- | ------- | ------- | ------- | ------- | -------
`rax` | `rdi` | `rsi` | `rdx` | `rcx` | `r8` | `r9`

The return value is in the `rax` register.

All registers, except `rcx` and `r11`, are preserved during the syscall.

#### Hello World example

This example will write the text "Hello World" to stdout using the `write` syscall and quit the program using the `_exit` syscall.

Syscall signatures:

```c
ssize_t write(int fd, const void *buf, size_t count);
void _exit(int status);
```

The following is the C program of this example:

```c
#include <unistd.h>

int main(int argc, char *argv[])
{
    write(1, "Hello World\n", 12); /* write "Hello World" to stdout */
    _exit(0);                      /* exit with error code 0 (no error) */
}
```

Both of the assembly examples start alike: a string stored in the data segment and `_start` as a global symbol.

```gas
.data
msg: .ascii "Hello World\n"

.text
.global _start
```

##### **`int 0x80`**

As defined in `arch/x86/include/asm/unistd_32.h`, the syscall numbers for write and _exit are:

```c
#define __NR_exit 1
#define __NR_write 4
```

The parameters are passed exactly as one would in a C program, using the correct registers. After everything is set up, the syscall is made using `int $0x80`.

```gas
_start:
    movl $4, %eax   # use the write syscall
    movl $1, %ebx   # write to stdout
    movl $msg, %ecx # use string "Hello World"
    movl $12, %edx  # write 12 characters
    int $0x80       # make syscall

    movl $1, %eax   # use the _exit syscall
    movl $0, %ebx   # error code 0
    int $0x80       # make syscall
```

##### **`syscall`**

In arch/x86/include/asm/unistd_64.h, the syscall numbers are defined as following:

```c
#define __NR_write 1
#define __NR_exit 60
```

Parameters are passed just like in the `int $0x80` example, except that the order of the registers is different. The syscall is made using `syscall`.

```gas
_start:
    movq $1, %rax   # use the write syscall
    movq $1, %rdi   # write to stdout
    movq $msg, %rsi # use string "Hello World"
    movq $12, %rdx  # write 12 characters
    syscall         # make syscall

    movq $60, %rax  # use the _exit syscall
    movq $0, %rdi   # error code 0
    syscall         # make syscall
```
- - -

### References

* [x86 Assembly](https://en.wikibooks.org/wiki/X86_Assembly): [X86 Assembly/Print Version](https://en.wikibooks.org/wiki/X86_Assembly/Print_Version)
* [x86 assembly language](https://en.wikipedia.org/wiki/X86_assembly_language)
