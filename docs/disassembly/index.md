### **x86 Disassembly**

### Stack

<small>[The Stack](https://en.wikibooks.org/wiki/X86_Disassembly/The_Stack)</small>

#### The Stack

A **stack** is a data structure that stores data values contiguously in memory.

* To read from the stack is said "to pop".
* To write to the stack is said "to push".

A stack is also known as a LIFO queue (Last In First Out) since values are popped from the stack in the reverse order that they are pushed onto it. Popped data disappears from the stack.

All x86 architectures use a stack as a temporary storage area in RAM that allows the processor to quickly store and retrieve data in memory.

* The current top of the stack is pointed to by the ESP register.
* The stack "grows" downward, from high to low memory addresses. Values recently pushed onto the stack are located in memory addresses above the ESP pointer.
* No register specifically points to the bottom of the stack. However, most operating systems monitor the stack bounds to detect both of the following conditions:
    * "underflow" (popping an empty stack)
    * "overflow" (pushing too much information on the stack)

When a value is popped off the stack, the value remains sitting in memory until overwritten. However, <u>you should never rely on the content of memory addresses below ESP, because other functions may overwrite these values without your knowledge.</u>

#### Push and Pop

The following lines of ASM code are basically equivalent:

##### **Push**

```nasm
push eax
```
is equivalent to:

```nasm
sub esp, 4
mov DWORD PTR SS:[esp], eax
```

##### **Pop**

```nasm
pop eax
```
is equivalent to:

```nasm
mov eax, DWORD PTR SS:[esp]
add esp, 4
```

In the above assembly code:

* [`DWORD`](https://msdn.microsoft.com/en-us/library/6ykwckb8.aspx) [`PTR`](https://msdn.microsoft.com/en-us/library/ek20ye9k.aspx): specifies a pointer to a double word (4 bytes) type.
* `SS:[esp]`: the [colon](https://msdn.microsoft.com/en-us/library/94b6khh4.aspx) (:) indicates overriding the default segment of `[esp]` with the Stack Segment (SS) register. SS is used as a segment prefix and ESP is dereferenced.

The single command actually performs much faster than the alternative. It can be visualized that the stack grows from right to left, and ESP decreases as the stack grows in size.


- - -

### References

* [x86 Disassembly](https://en.wikibooks.org/wiki/X86_Disassembly)
* [Microsoft Macro Assembler Reference](https://msdn.microsoft.com/en-us/library/afzk3475.aspx)
