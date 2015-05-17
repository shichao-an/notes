## Chapter 2. Memory Addressing

This chapter offers details in [x86](http://en.wikipedia.org/wiki/X86) microprocessors address memory chips and how Linux uses the available addressing circuits.

### Memory Addresses

* **Logical address**
* **Linear address** (also known as **virtual address**)
* **Physical address**

Memory Management Unit (MMU) transforms a logical address into a linear address, and the linear address into a physical address.

[![Figure 2-1. Logical address translation](figure_2-1_600.png)](figure_2-1.png "Figure 2-1. Logical address translation")

Memory arbiter: read or write operations on a RAM chip must be performed serially.

### Segmentation in Hardware

The following sections focus on address translation when **protected mode** is enabled, in Intel microprocessors starting with the 80286 model.

### Segment Selectors

A logical address consists of:

* **Segment Selector** (segment identifier): 16-bit
* Offset: 32-bit

### Segmentation registers

**Segmentation Registers** hold Segment Selectors.

* `cs`: code segment (program instructions); 2-bit field for CPU's Current Privilege Level (CPL), Linux uses only levels 0 and 3 for Kernel Mode and User Mode
* `ss`: stack segment (current program stack)
* `ds`: data segment (global and static data)
* `es`, `fs`, and `gs`: general purpose (arbitrary data)

### Segment Descriptors

Each segment is represented by an 8-byte **Segment Descriptor** that describes the segment characteristics. Segment Descriptors are stored either in the **Global Descriptor Table** (GDT) or in the **Local Descriptor Table** (LDT). The address and size of GDT and LDT are contained in `gdtr` and `ldtr` control registers respectively.

* Code Segment Descriptor: included in GDT or LDT
* Data Segment Descriptor: included in GDT or LDT
* Task State Segment Descriptor (TSSD): refers to a Task State Segment (TSS), a segment used to save the contents of the processor registers; included in GDT only
* Local Descriptor Table Descriptor (LDTD): refers to a segment containing an LDT; included in GDT only

### Fast Access to Segment Descriptors

Segmentation registers store only the Segment Selector. The x86 process provides an additional nonprogrammable register for each of the six programmable segmentation registers to speed up the translation of logical addresses into linear addresses. Each nonprogrammable register contains the 8-byte Segment Descriptor.

Segment Selector fields [p40]:

* `index`: identifies the Segment Descriptor entry contained in GDT or LDT
* `TI` (Table Indicator): specifies whether the Segment Descriptor is included in the GDT (`TI` = 0) or in the LDT (`TI` = 1).
* `RPL` (Requestor Privilege Level):  specifies the Current Privilege Level (CPL) of the CPU when the corresponding Segment Selector is loaded into the `cs` register

### Segmentation Unit

The **segmentation unit** performs the following operations to obtain the linear address:

[![Figure 2-5. Translating a logical address](figure_2-5.png)](figure_2-5.png "Figure 2-5. Translating a logical address")

* Examines the `TI` field of the Segment Selector to determine which Descriptor Table (GDT or LDT) stores the Segment Descriptor
* Computes the address of the Segment Descriptor from the `index` field of the Segment Selector
* Adds the offset of the logical address to the `Base` field of the Segment Descriptor

### Segmentation in Linux

All Linux processes running in User Mode use the same pair of segments to address instructions and data. This is similar to processes running in Kernel Mode.

* user code segment
* user data segment
* kernel code segment
* kernel data segment

Segment Selectors are defined by the macros:

* `__USER_CS`
* `__USER_DS`
* `__KERNEL_CS`
* `__KERNEL_DS`

To address the kernel code segment, for instance, the kernel just loads the value yielded by the `__KERNEL_CS` macro into the `cs` segmentation register.

The linear addresses associated with such segments all start at 0 and reach the addressing limit of 2<sup>32</sup> –1. This means that all processes, either in User Mode or in Kernel Mode, may use the same logical addresses.

#### [CPL](http://en.wikipedia.org/wiki/Protection_ring), `RPL` and registers

The Current Privilege Level (CPL) of the CPU indicates whether the processor is in User or Kernel Mode and is specified by the `RPL` field of the Segment Selector stored in the `cs` register. [p42]

Whenever the CPL is changed, some segmentation registers (e.g. `ds`, `ss`) must be correspondingly updated. [p42-43]

#### Implicit Segment Selector

Only Offset component of its logical address is specified:

* `ss`: kernel saves a pointer to an instruction or to a data structure
* `cs`: kernel invokes a function
* `ds`: kernel data structure
* `es`: user data structure

- - -
### Doubts and Solutions

Segmentation in Linux [p41]
> However, Linux uses segmentation in a very limited way. In fact, segmentation and paging are somewhat redundant, because both can be used to separate the physical address spaces of processes: segmentation can assign a different linear address space to each process, while paging can map the same linear address space into different physical address spaces. Linux prefers paging to segmentation for the following reasons:
