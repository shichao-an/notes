### **Chapter 8. Bottom Halves and Deferring Work**

Interrupt handlers, discussed in the [previous chapter](ch7.md), can form only the first half of any interrupt processing solution, with the following limitations:

* Interrupt handlers run asynchronously and interrupt other potentially important code, including other interrupt handlers. Therefore, to avoid stalling the interrupted code for too long, interrupt handlers need to run as quickly as possible.
* Interrupt handlers run with one of the following conditions:
    * The current interrupt level is disabled (if `IRQF_DISABLED` is unset)
    * All interrupts on the current processor are disabled (if `IRQF_DISABLED` is set)

    Disabling interrupts prevents hardware from communicating with the operating systems, so interrupt handlers need to run as quickly as possible.

* Interrupt handlers are often timing-critical because they deal with hardware.
* Interrupt handlers do not run in process context, so they cannot block, which limits what they can do.

Operating systems need a quick, asynchronous, and simple mechanism for immediately responding to hardware and performing any time-critical actions. Interrupt handlers serve this function well. Less critical work can and should be deferred to a later point when interrupts are enabled.

Consequently, managing interrupts is divided into two parts, or **halves**.

1. The first part, interrupt handlers (**top halves**), are executed by the kernel asynchronously in immediate response to a hardware interrupt, as discussed in the previous chapter.
2. This chapter looks at the second part of the interrupt solution, **bottom halves**.

### Bottom Halves

The job of bottom halves is to perform any interrupt-related work not performed by the interrupt handler. You want the interrupt handler to perform as little work as possible and in turn be as fast as possible. By offloading as much work as possible to the bottom half, the interrupt handler can return control of the system to whatever it interrupted as quickly as possible.

However, the interrupt handler must perform some work; if the work is timing-sensitive, it makes sense to perform it in the interrupt handler. For example, the interrupt handler almost assuredly needs to acknowledge to the hardware the receipt of the interrupt. It may need to copy data to or from the hardware.

Almost anything else can be performed in the bottom half. For example, if you copy data from the hardware into memory in the top half, it makes sense to process it in the bottom half.

No hard and fast rules exist about what work to perform where. The decision is left entirely up to the device-driver author. Although no arrangement is *illegal*, an arrangement can certainly be *suboptimal*.

Since interrupt handlers run asynchronously, with at least the current interrupt line disabled, minimizing their duration is important. The following useful tips help decide how to divide the work between the top and bottom half:

* If the work is time sensitive, perform it in the interrupt handler.
* If the work is related to the hardware, perform it in the interrupt handler.
* If the work needs to ensure that another interrupt (particularly the same interrupt) does not interrupt it, perform it in the interrupt handler.
* For everything else, consider performing the work in the bottom half.

When attempting to write your own device driver, looking at other interrupt handlers and their corresponding bottom halves can help. When deciding how to divide your interrupt processing work between the top and bottom half, ask yourself what *must* be in the top half and what *can* be in the bottom half. Generally, the quicker the interrupt handler executes, the better.

#### Why Bottom Halves?

It is crucial to understand:

* Why to defer work
* When to defer it

You want to limit the amount of work you perform in an interrupt handler because:

* Interrupt handlers run with the current interrupt line disabled on all processors.
* Interrupt handlers that register with `IRQF_DISABLED` run with all interrupt lines disabled on the local processor (plus the current interrupt line disabled on all processors).

Thus, minimizing the time spent with interrupts disabled is important for system response and performance.

Besides, interrupt handlers run asynchronously with respect to other code, even other interrupt handlers. Therefore you should work to minimize how long interrupt handlers run. Processing incoming network traffic should not prevent the kernel's receipt of keystrokes.The solution is to defer some of the work until later.

##### **When is "later"?** *

*Later* is often simply *not now*. <u>The point of a bottom half is not to do work at some specific point in the future, but simply to defer work until any point in the future when the system is less busy and interrupts are again enabled.</u> Often, bottom halves run immediately after the interrupt returns. The key is that they run with all interrupts enabled.

Linux is not the only operating systems that separates the processing of hardware interrupts into two parts.

* The top half is quick and simple and runs with some or all interrupts disabled.
* The bottom half (however it is implemented) runs later with all interrupts enabled.

This design keeps system latency low by running with interrupts disabled for as little time as necessary.
