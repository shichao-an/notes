### **Chapter 2. Memory Addressing**

This chapter discusses addressing techniques by offering details in [80×86](http://en.wikipedia.org/wiki/X86) microprocessors address memory chips and how Linux uses the available addressing circuits.

### Memory Addresses

Programmers casually refer to a **memory address** as the way to access the contents of a memory cell. However, when dealing with 80×86 microprocessors, we have to distinguish three kinds of addresses:

* **Logical address**: included in the machine language instructions to specify the address of an operand or of an instruction.
    * This type of address embodies the well-known [80×86 segmented architecture](https://en.wikipedia.org/wiki/X86_memory_segmentation).
    * Each logical address consists of a *segment* and an *offset* (or *displacement*) that denotes the distance from the start of the segment to the actual address.
* **Linear address** (also known as **virtual address**): a single 32-bit unsigned integer that can be used to address up to 4 GB, that is, up to 4,294,967,296 memory cells.
    * Linear addresses are usually represented in hexadecimal notation: from `0x00000000` to `0xffffffff`.
* **Physical address**: used to address memory cells in memory chips. They correspond to the electrical signals sent along the address pins of the microprocessor to the memory bus.
    * <u>Physical addresses are represented as 32-bit or 36-bit unsigned integers.</u>

#### Memory Management Unit *

[Memory Management Unit](https://en.wikipedia.org/wiki/Memory_management_unit) (MMU) transforms a logical address into a linear address (using a hardware circuit called a segmentation unit), and the linear address into a physical address (using a second hardware circuit called a paging unit), as shown in the figure below:

[![Figure 2-1. Logical address translation](figure_2-1_600.png)](figure_2-1.png "Figure 2-1. Logical address translation")

#### Memory Arbiter *

The [**memory arbiter**](https://en.wikipedia.org/wiki/Arbiter_(electronics)) is a hardware circuit inserted between the bus and every RAM chip. Its role is to grant access to a CPU if the chip is free and to delay it if the chip is busy servicing a request by another processor.

* In multiprocessor systems, RAM chips may be accessed concurrently by independent CPUs, since all CPUs usually share the same memory. Thus, memory arbiters are need, because read or write operations on a RAM chip must be performed serially.
* Uniprocessor systems also use memory arbiters, because they include specialized processors called [*DMA controllers*](https://en.wikipedia.org/wiki/Direct_memory_access) that operate concurrently with the CPU.

For multiprocessor systems, the structure of the arbiter is more complex because it has more input ports. The dual Pentium, for instance, maintains a two-port arbiter at each chip entrance and requires that the two CPUs exchange synchronization messages before attempting to use the common bus. From the programming point of view, the arbiter is hidden because it is managed by hardware circuits.

### Segmentation in Hardware

Starting with the [80286](https://en.wikipedia.org/wiki/Intel_80286) model, Intel microprocessors perform address translation in two different ways called [**real mode**](https://en.wikipedia.org/wiki/Real_mode) and [**protected mode**](https://en.wikipedia.org/wiki/Protected_mode). The following sections focus on address translation when **protected mode** is enabled. Real mode exists mostly to maintain processor compatibility with older models and to allow the operating system to bootstrap.

#### Segment Selectors and Segmentation Registers

A logical address consists of two parts:

* Segment identifier: 16-bit field called **Segment Selector** ([described later](#fast-access-to-segment-descriptors))
* Offset: 32-bit field

[![Figure 2-2. Segment Selector format](figure_2-2_600.png)](figure_2-2.png "Figure 2-2. Segment Selector format")

To retrieve segment selectors easily and quickly, the processor provides **segmentation registers** whose only purpose is to hold Segment Selectors:

* `cs`: code segment register, which points to a segment containing program instructions
    * It includes 2-bit field for CPU's [Current Privilege Level](https://en.wikipedia.org/wiki/Privilege_level) (CPL), Linux uses only levels 0 and 3 for Kernel Mode and User Mode
* `ss`: stack segment register, which points to a segment containing the current program stack
* `ds`: data segment register, which points to a segment containing global and static data
* `es`, `fs`, and `gs`: general purpose registers, which may refer to arbitrary data

Despite only six of them, a program can reuse the same segmentation register for different purposes by saving its content in memory and then restoring it later.

#### Segment Descriptors

Each segment is represented by an 8-byte **Segment Descriptor** that describes the segment characteristics. Segment Descriptors are stored either in the [**Global Descriptor Table**](https://en.wikipedia.org/wiki/Global_Descriptor_Table) (GDT) or in the [**Local Descriptor Table**](https://en.wikipedia.org/wiki/Global_Descriptor_Table#Local_Descriptor_Table) (LDT).

Usually only one GDT is defined, while each process is permitted to have its own LDT if it needs to create additional segments besides those stored in the GDT. The address and size of the GDT in main memory are contained in the `gdtr` [control register](https://en.wikipedia.org/wiki/Control_register), while the address and size of the currently used LDT are contained in the `ldtr` control register.

The Segment Descriptor format is illustrated in the following figure:

[![Figure 2-3. Segment Descriptor format](figure_2-3_600.png)](figure_2-3.png "Figure 2-3. Segment Descriptor format")

Segment Descriptor fields are explained in the following table:

Field name | Description
---------- | -----------
`Base` | Contains the linear address of the first byte of the segment.
`G` | *Granularity flag*: if it is cleared (equal to 0), the segment size is expressed in bytes; otherwise, it is expressed in multiples of 4096 bytes.
`Limit` | Holds the offset of the last memory cell in the segment, thus binding the segment length. When G is set to 0, the size of a segment may vary between 1 byte and 1 MB; otherwise, it may vary between 4 KB and 4 GB.
`S` | *System flag*: if it is cleared, the segment is asystem segment that stores critical data structures such as the Local Descriptor Table; otherwise, it is a normal code or data segment.
`Type` | Characterizes the segment type and its access rights (see the text that follows this table).
`DPL` | *Descriptor Privilege Level*: used to restrict accesses to the segment. It represents the minimal CPU privilege level requested for accessing the segment. Therefore, a segment with its DPL set to 0 is accessible only when the CPL is 0—that is, in Kernel Mode—while a segment with its DPL set to 3 is accessible with every CPL value.
`P` | *Segment-Present flag*: is equal to 0 if the segment is not stored currently in main memory. Linux always sets this flag (bit 47) to 1, because it never swaps out whole segments to disk.
`D` or `B` | Called `D` or `B` depending on whether the segment contains code or data. Its meaning is slightly different in the two cases, but it is basically set (equal to 1) if the addresses used as segment offsets are 32 bits long, and it is cleared if they are 16 bits long (see the Intel manual for further details).
`AVL` | May be used by the operating system, but it is ignored by Linux.

There are several types of segments, and thus several types of Segment Descriptors. The following list shows the types that are widely used in Linux:

* **Code Segment Descriptor**: indicates that the Segment Descriptor refers to a code segment; included in GDT or LDT.
    * This descriptor has the S flag set (non-system segment).
* **Data Segment Descriptor**: indicates that the Segment Descriptor refers to a data segment; included in GDT or LDT
    * This descriptor has the S flag set.
    * Stack segments are implemented by means of generic data segments.
* **Task State Segment Descriptor** (TSSD): refers to a [Task State Segment](https://en.wikipedia.org/wiki/Task_state_segment) (TSS), a segment used to save the contents of the processor registers; included in GDT only
    * The corresponding `Type` field has the value 11 or 9, depending on whether the corresponding process is currently executing on a CPU.
    * The `S` flag of such descriptors is set to 0.
* **Local Descriptor Table Descriptor** (LDTD): refers to a segment containing an LDT; included in GDT only
    * The corresponding `Type` field has the value 2.
    * The `S` flag of such descriptors is set to 0.

#### Fast Access to Segment Descriptors

Recall that <u>logical addresses consist of a 16-bit Segment Selector and a 32-bit Offset, and that segmentation registers store only the Segment Selector.</u>

To speed up the translation of logical addresses into linear addresses, the 80×86 processor provides an additional nonprogrammable register, which cannot be set by a programmer, for each of the six programmable segmentation registers.

1. Each nonprogrammable register contains the 8-byte Segment Descriptor specified by the Segment Selector contained in the corresponding segmentation register.
2. Every time a Segment Selector is loaded in a segmentation register, the corresponding Segment Descriptor is loaded from memory into the matching nonprogrammable CPU register.
3. From then on, translations of logical addresses referring to that segment can be performed without accessing the GDT or LDT stored in main memory; the processor can refer only directly to the CPU register containing the Segment Descriptor.
4. Accesses to the GDT or LDT are necessary only when the contents of the segmentation registers change.

The Segment Selector includes three fields, described in the following table:

Field name | Description
---------- | -----------
`index` | Identifies the Segment Descriptor entry contained in the GDT or in the LDT.
`TI` | *Table Indicator*: specifies whether the Segment Descriptor is included in the GDT (TI = 0) or in the LDT (`TI` = 1).
`RPL` | *Requestor Privilege Level:* specifies the [Current Privilege Level](#cpl-rpl-and-registers) (CPL)  of the CPU when the corresponding Segment Selector is loaded into the `cs` register; it also may be used to selectively weaken the processor privilege level when accessing data segments.

Because a Segment Descriptor is 8 bytes long, its relative address inside the GDT or the LDT is obtained by multiplying the 13-bit `index` field ([Figure 2-2](figure_2-2.png)) of the Segment Selector by 8. For instance, if the GDT is at `0x00020000` (the value stored in the `gdtr` register) and the `index` specified by the Segment Selector is 2, the address of the corresponding Segment Descriptor is `0x00020000 + (2 × 8)`, or `0x00020010`.

The first entry of the GDT is always set to 0. This ensures that logical addresses with a null Segment Selector will be considered invalid, thus causing a processor exception. The maximum number of Segment Descriptors that can be stored in the GDT is 8,191 (2<sup>13</sup>–1).

#### Segmentation Unit

The **segmentation unit** performs the following operations to obtain the linear address:

[![Figure 2-5. Translating a logical address](figure_2-5_600.png)](figure_2-5.png "Figure 2-5. Translating a logical address")

* Examines the `TI` field of the Segment Selector to determine which Descriptor Table (GDT or LDT) stores the Segment Descriptor.
    * If the Descriptor is in the GDT, then the segmentation unit gets the base linear address of the GDT from the `gdtr` register.
    * If the Descriptor is in the active LDT, then the segmentation unit gets the base linear address of that LDT from the `ldtr` register.
* Computes the address of the Segment Descriptor from the `index` field of the Segment Selector.
    * The `index` field is multiplied by 8 (the size of a Segment Descriptor), and the result is added to the content of the `gdtr` or `ldtr` register.
* Adds the offset of the logical address to the `Base` field of the Segment Descriptor to obtain the linear address.

Thanks to the nonprogrammable registers associated with the segmentation registers, the first two operations need to be performed only when a segmentation register has been changed.

### Segmentation in Linux

Segmentation has been included in 80×86 microprocessors to encourage programmers to split their applications into logically related entities, such as subroutines or global and local data areas. However, Linux uses segmentation in a very limited way. Both segmentation and paging can be used to separate the physical address spaces of processes:

* Segmentation can assign a different linear address space to each process.
* Paging can map the same linear address space into different physical address spaces.

Linux prefers paging to segmentation for the following reasons:

* Memory management is simpler when all processes use the same segment register values: they share the same set of linear addresses.
* Paging makes Linux is portable to a wide range of architectures; RISC architectures in particular have limited support for segmentation.

<u>The 2.6 version of Linux uses segmentation only when required by the 80×86 architecture.</u>

* All Linux processes running in User Mode use the same pair of segments to address instructions and data, called **user code segment** and **user data segment**, respectively.
* All Linux processes running in Kernel Mode use the same pair of segments to address instructions and data, called **kernel code segment** and **kernel data segment**, respectively.

The following table shows the values of the Segment Descriptor fields for these four crucial segments.

Segment | Base | G | Limit | S | Type | DPL | D/B | P
------- | ---- | - | ----- | - | ---- | --- | --- | -
user code | `0x00000000` | 1 | `0xfffff` | 1 | 10 | 3 | 1 | 1
user data | `0x00000000` | 1 | `0xfffff` | 1 | 2 | 3 | 1 | 1
kernel code | `0x00000000` | 1 | `0xfffff` | 1 | 10 | 0 | 1 | 1
kernel data | `0x00000000` | 1 | `0xfffff` | 1 | 2 | 0 | 1 | 1

Segment Selectors are defined by the macros:

* `__USER_CS`
* `__USER_DS`
* `__KERNEL_CS`
* `__KERNEL_DS`

To address the kernel code segment, for instance, the kernel just loads the value yielded by the `__KERNEL_CS` macro into the `cs` segmentation register.

The linear addresses associated with such segments all start at 0 and reach the addressing limit of 2<sup>32</sup> –1. This means that all processes, either in User Mode or in Kernel Mode, may use the same logical addresses.

Another important consequence of having all segments start at `0x00000000` is that in Linux, logical addresses coincide with linear addresses: the value of the Offset field of a logical address always coincides with the value of the corresponding linear address.

#### [CPL](http://en.wikipedia.org/wiki/Protection_ring), `RPL` and registers *

The Current Privilege Level (CPL) of the CPU indicates whether the processor is in User or Kernel Mode and is specified by the `RPL` field of the Segment Selector stored in the `cs` register. [p42]

Whenever the CPL is changed, some segmentation registers must be correspondingly updated. For instance:

* When the CPL is equal to 3 (User Mode), the `ds` register must contain the Segment Selector of the user data segment; when the CPL is equal to 0, it must contain the Segment Selector of the kernel data segment.
* When the CPL is 3, the `ss` must refer to a User Mode stack inside the user data segment; when the CPL is 0, it must refer to a Kernel Mode stack inside the kernel data segment. When switching from User Mode to Kernel Mode, Linux always makes sure that the `ss` register contains the Segment Selector of the kernel data segment.

#### Implicit Segment Selector *

When saving a pointer to an instruction or to a data structure, the kernel does not need to store the Segment Selector component of the logical address, because the `ss` register contains the current Segment Selector.

For example, when the kernel invokes a function, it executes a `call` assembly language instruction specifying only the Offset component of its logical address; the Segment Selector is implicitly selected as the one referred to by the `cs` register. Because there is only one segment of type "executable in Kernel Mode", namely the code segment identified by `__KERNEL_CS`, it is sufficient to load `__KERNEL_CS` into `cs` whenever the CPU switches to Kernel Mode.

The same argument goes for pointers to kernel data structures (implicitly using the `ds` register), as well as for pointers to user data structures (the kernel explicitly uses the `es` register).

* `ss`: kernel saves a pointer to an instruction or to a data structure
* `cs`: kernel invokes a function
* `ds`: kernel data structure
* `es`: user data structure

Besides the four segments described, Linux makes use of a few other specialized segments (discussed in The Linux GDT).

#### The Linux GDT

In multiprocessor systems there is one GDT for every CPU [p43].

* All GDTs are stored in the [`cpu_gdt_table`](https://github.com/shichao-an/linux-2.6.11.12/blob/master/arch/i386/kernel/head.S#L479) array.
* The addresses and sizes of the GDTs (used when initializing the `gdtr` registers) are stored in the [`cpu_gdt_descr`](https://github.com/shichao-an/linux-2.6.11.12/blob/master/arch/i386/kernel/head.S) array.

These symbols are defined in the file [arch/i386/kernel/head.S](https://github.com/shichao-an/linux-2.6.11.12/blob/master/arch/i386/kernel/head.S).

The layout of the GDTs is shown schematically in the following figure:

[![Figure 2-6. The Global Descriptor Table](figure_2-6_600.png)](figure_2-6.png "Figure 2-6. The Global Descriptor Table")

Each GDT includes 18 segment descriptors and 14 null, unused, or reserved entries. Unused entries are inserted on purpose so that Segment Descriptors usually accessed together are kept in the same 32-byte line of the [hardware cache](#hardware-cache).

The 18 segment descriptors included in each GDT point to the following segments:

* Four user and kernel code and data segments (see [previous section](#segmentation-in-linux))
* [Task State Segment](https://en.wikipedia.org/wiki/Task_state_segment) (TSS): different for each processor in the system.
    * The linear address space corresponding to a TSS is a small subset of the linear address space corresponding to the kernel data segment.
    * The Task State Segments are sequentially stored in the `init_tss` array; in particular, the `Base` field of the TSS descriptor for the *n*th CPU points to the *n*th component of the `init_tss` array.
    * The `G` (granularity) flag is cleared, while the `Limit` field is set to `0xeb`, because the TSS segment is 236 bytes long.
    * The `Type` field is set to 9 or 11 (available 32-bit TSS), and the `DPL` is set to 0, because processes in User Mode are not allowed to access TSS segments.
* A segment including the default Local Descriptor Table (LDT), usually shared by all processes
* Three [Thread-Local Storage](https://en.wikipedia.org/wiki/Thread-local_storage) (TLS) segments: allows multithreaded applications to make use of up to three segments containing data local to each thread. The `set_thread_area()` and `get_thread_area()` system calls, respectively, create and release a TLS segment for the executing process.
* Three segments related to [Advanced Power Management](https://en.wikipedia.org/wiki/Advanced_Power_Management) (APM)
* Five segments related to [Plug and Play](https://en.wikipedia.org/wiki/Plug_and_play) (PnP) BIOS services
* A special TSS segment used by the kernel to handle "Double fault" exceptions

There is a copy of the GDT for each processor in the system. All copies of the GDT store identical entries, except for a few cases:

1. Each processor has its own TSS segment, thus the corresponding GDT's entries differ.
2. A few entries in the GDT may depend on the process that the CPU is executing (LDT and TLS Segment Descriptors).
3. In some cases a processor may temporarily modify an entry in its copy of the GDT, for instance, when invoking an APM's BIOS procedure.

#### The Linux LDTs

Most Linux User Mode applications do not make use of a Local Descriptor Table. The kernel defines a default LDT to be shared by most processes. It has five entries but only two are used by the kernel:

* A [call gate](http://en.wikipedia.org/wiki/Call_gate) for [iBCS](http://en.wikipedia.org/wiki/Intel_Binary_Compatibility_Standard) executables
* A call gate for Solaris/x86 executables

**Call gates** are a mechanism provided by 80×86 microprocessors to change the privilege level of the CPU while invoking a predefined function.

In some cases, processes may require to set up their own LDT, such as applications (such as [Wine](https://en.wikipedia.org/wiki/Wine_(software))) that execute segment-oriented Microsoft Windows applications. The [`modify_ldt()`](http://man7.org/linux/man-pages/man2/modify_ldt.2.html) system call allows a process to do this.

Any custom LDT created by `modify_ldt()` also requires its own segment. When a processor starts executing a process having a custom LDT, the LDT entry in the CPU-specific copy of the GDT is changed accordingly.

User Mode applications also may allocate new segments by means of `modify_ldt()`; the kernel, however, never makes use of these segments, and it does not have to keep track of the corresponding Segment Descriptors, because they are included in the custom LDT of the process.

### Paging in Hardware

The paging unit translates linear addresses into physical ones. Its key task is to check the requested access type against the access rights of the linear address, and generates a [Page Fault](https://en.wikipedia.org/wiki/Page_fault) exception if memory access is not valid.

* **Pages**: grouped fixed-length intervals of linear addresses; contiguous linear addresses within a page are mapped into contiguous physical addresses. The term "page" to refer both to a set of linear addresses and to the data contained in this group of addresses.
* **Page frames** (or **physical pages**): the paging unit thinks of all RAM as partitioned into fixed-length page frames.
    * Each page frame contains a page, thus the length of a page frame coincides with that of a page.
    * A page frame is a constituent of main memory, and hence it is a storage area.
    * It is important to distinguish a page from a page frame: the former is just a block of data, which may be stored in any page frame or on disk.
* **Page table**: data structures that map linear to physical addresses
    * Page tables are stored in main memory and must be properly initialized by the kernel before enabling the paging unit.

Starting with the [80386](https://en.wikipedia.org/wiki/Intel_80386), all 80×86 processors support paging; it is enabled by setting the `PG` flag of a control register named `cr0`. When `PG = 0`, linear addresses are interpreted as physical addresses.

#### Regular Paging

Starting with the 80386, the paging unit of Intel processors handles 4 KB pages.

The 32 bits of a linear address are divided into three fields:

* **Directory**: the most significant 10 bits
* **Table**: the intermediate 10 bits
* **Offset**: the least significant 12 bits

The translation of linear addresses is accomplished in two steps, each based on a
type of translation table.

1. The first translation table is called the **Page Directory**.
2. The second is called the **Page Table**.

In the following texts, the lowercase "page table" term denotes any page storing the mapping between linear and physical addresses, while the capitalized "Page Table" term denotes a page in the last level of page tables.

The aim of this two-level scheme is to reduce the amount of RAM required for per-process Page Tables:

* If a simple one-level Page Table was used, then it would require up to 2<sup>20</sup> entries (at 4 bytes per entry, 4 MB of RAM) to represent the Page Table for each process (if the process used a full 4 GB linear address space), even though a process does not use all addresses in that range.
* <u>The two-level scheme reduces the memory by requiring Page Tables only for those virtual memory regions actually used by a process.</u>

Each active process must have a Page Directory assigned to it. However, there is no need to allocate RAM for all Page Tables of a process at once; it is more efficient to allocate RAM for a Page Table only when the process effectively needs it.

* The physical address of the Page Directory in use is stored in a control register named `cr3`.
* The Directory field within the linear address determines the entry in the Page Directory that points to the proper Page Table.
* The Table field determines the entry in the Page Table that contains the physical address of the page frame containing the page.
* The Offset field determines the relative position within the page frame (see the following figure).
    * Because it is 12 bits long, each page consists of 4096 bytes of data.

[![Figure 2-7. Paging by 80 × 86 processors](figure_2-7_600.png)](figure_2-7.png "Figure 2-7. Paging by 80 × 86 processors")

Both the Directory and the Table fields are 10 bits long, so Page Directories and Page Tables can include up to 1,024 entries. Thus, a Page Directory can address up to 1024 × 1024 × 4096=2<sup>32</sup> memory cells, which is expected in 32-bit addresses.

The entries of Page Directories and Page Tables have the same structure. Each entry includes the following fields:

#### Extended Paging
