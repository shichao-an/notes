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

#### A World of Bottom Halves

While the top half is implemented entirely via the interrupt handler, multiple mechanisms are available for implementing a bottom half. These mechanisms are different interfaces and subsystems that enable you to implement bottom halves. This chapter discusses multiple methods of implementing bottom halves. [p135]

##### **The Original "Bottom Half"**

In the beginning, Linux provided only the "bottom half" for implementing bottom halves. This name was logical because at the time that was the only means available for deferring work. The infrastructure was also known as *BH* to avoid confusion with the generic term *bottom half*.

The BH interface was simple.

* It provided a statically created list of 32 bottom halves for the entire system.
* The top half could mark whether the bottom half would run by setting a bit in a 32-bit integer.
* Each BH was globally synchronized. No two could run at the same time, even on different processors.

This was simple and easy to use, but was also inflexible and a bottleneck.

##### **Task Queues**

The kernel developers later introduced *task queues* both as a method of deferring work and as a replacement for the BH mechanism.

The kernel defined a family of queues.

* Each queue contained a linked list of functions to call.
* The queued functions were run at certain times, depending on which queue they were in.
* Drivers could register their bottom halves in the appropriate queue.

This worked fairly well, but it was still too inflexible to replace the BH interface entirely. It also was not lightweight enough for performance-critical subsystems, such as networking.

##### **Softirqs and Tasklets**

The *softirqs* and *tasklets* were introduced during the 2.3 development series, to completely replace the BH interface.

* Softirqs are a set of statically defined bottom halves that can run simultaneously on any processor; even two of the same type can run concurrently.
* Tasklets are flexible, dynamically created bottom halves built on top of softirqs.
  * Two different tasklets can run concurrently on different processors, but two of the same type of tasklet cannot run simultaneously.

Tasklets are a good trade-off between performance and ease of use. For most bottom-half processing, the tasklet is sufficient. Softirqs are useful when performance is critical, such as with networking. Using softirqs requires more care, however, because two of the same softirq can run at the same time. In addition, softirqs must be registered statically at compile time. Conversely, code can dynamically register tasklets.

While developing the 2.5 kernel, all BH users were converted to the other bottom-half interfaces. Additionally, the task queue interface was replaced by the work queue interface. Work queues are a simple yet useful method of queuing work to later be performed in process context.

Consequently, the 2.6 kernel has three bottom-half mechanisms in the kernel:

* Softirqs
* tasklets
* Work queues

##### **Kernel Timers** *

*Kernel timers* is another mechanism for deferring work. Unlike the mechanisms discussed in the chapter, timers defer work for a specified amount of time. That is, although the tools discussed in this chapter are useful to defer work to any time but now, you use timers to defer work until at least a specific time has elapsed.

Therefore, timers have different uses than the general mechanisms discussed in this chapter.  A full discussion of timers is given in [Chapter 11 Timers and Time Management](ch11.md).

##### **Dispelling the Confusion**

*Bottom half* is a generic operating system term referring to the deferred portion of interrupt processing. All the kernel's mechanisms for deferring work are "bottom halves". Some people also confusingly call all bottom halves "softirqs".

Bottom half also refers to the original deferred work mechanism in Linux. This mechanism is also known as a BH, so we call it by that name now and leave the former as a generic description. The BH mechanism was deprecated a while back and fully removed in the 2.5 development kernel series.

In the current three methods exist for deferring work, tasklets are built on softirqs and work queues are their own subsystem. The following table presents a history of bottom halves.

Bottom Half | Status
----------- | ------
BH | Removed in 2.5
Task queues | Removed in 2.5
Softirq | Available since 2.3
Tasklet | Available since 2.3
Work queues | Available since 2.5

### Softirqs

Softirqs are rarely used directly; tasklets, which are built on softirqs are a much more common form of bottom half. The softirq code lives in the file [kernel/softirq.c](https://github.com/shichao-an/linux/blob/v2.6.34/kernel/softirq.c) in the kernel source tree.

Softirqs are statically allocated at compile time. Unlike tasklets, you cannot dynamically register and destroy softirqs. Softirqs are represented by the `softirq_action` structure, which is defined in [`<linux/interrupt.h>`](https://github.com/shichao-an/linux/blob/v2.6.34/include/linux/interrupt.h):

<small>[include/linux/interrupt.h#L366](https://github.com/shichao-an/linux/blob/v2.6.34/include/linux/interrupt.h#L366)</small>

```c
struct softirq_action
{
	void	(*action)(struct softirq_action *);
};
```

A 32-entry array of this structure is declared in [kernel/softirq.c](https://github.com/shichao-an/linux/blob/v2.6.34/kernel/softirq.c):

```c
static struct softirq_action softirq_vec[NR_SOFTIRQS];
```

Each registered softirq consumes one entry in the array. Consequently, there are `NR_SOFTIRQS` registered softirqs. The number of registered softirqs is statically determined at compile time and cannot be changed dynamically. The kernel enforces a limit of 32 registered softirqs. In the current kernel, only nine exist.

##### **The Softirq Handler**

The prototype of a softirq handler, `action`, looks like:

```c
void softirq_handler(struct softirq_action *);
```

When the kernel runs a softirq handler, it executes this `action` function with a pointer to the corresponding `softirq_action` structure as its argument. For example, if `my_softirq` pointed to an entry in the `softirq_vec` array, the kernel would invoke the softirq handler function as:

```c
my_softirq->action(my_softirq);
```

Note that the kernel passes the entire structure to the softirq handler. This trick enables future additions to the structure without requiring a change in every softirq handler.

A softirq never preempts another softirq. The only event that can preempt a softirq is an interrupt handler. Another softirq (even the same one) can run on another processor, however.

##### **Executing Softirqs**

A registered softirq must be marked before it will execute. This is called *raising the softirq*. Usually, an interrupt handler marks its softirq for execution before returning. Then, at a suitable time, the softirq runs. Pending softirqs are checked for and executed in the following places:

* In the return from hardware interrupt code path
* In the `ksoftirqd` kernel thread
* In any code that explicitly checks for and executes pending softirqs, such as the networking subsystem

Regardless of the method of invocation, softirq execution occurs in [`__do_softirq()`](https://github.com/shichao-an/linux/blob/v2.6.34/kernel/softirq.c#L191), which is invoked by [`do_softirq()`](https://github.com/shichao-an/linux/blob/v2.6.34/kernel/softirq.c#L253). The function is quite simple. If there are pending softirqs, `__do_softirq()` loops over each one, invoking its handler.

The following code is a simplified variant of the important part of `__do_softirq()`:

```c
u32 pending;

pending = local_softirq_pending();
if (pending) {
    struct softirq_action *h;

    /* reset the pending bitmask */
    set_softirq_pending(0);

    h = softirq_vec;
    do {
        if (pending & 1)
            h->action(h);
        h++;
        pending >>= 1;
    } while (pending);
}
```

It checks for, and executes, any pending softirqs. It specifically does the following:

1. It sets the `pending` local variable to the value returned by the `local_softirq_pending()` macro.
    * This is a 32-bit mask of pending softirqs: if bit `n` is set, the `n`th softirq is pending.
2. After the pending bitmask of softirqs is saved, it clears the actual bitmask.
3. The pointer `h` is set to the first entry in the `softirq_vec`.
4. If the first bit in pending is set, `h->action(h)` is called.
5. The pointer `h` is incremented by one so that it now points to the second entry in the `softirq_vec` array.
6. The bitmask `pending` is right-shifted by one.
    * This discards the first bit and moves all other bits one place to the right.
7. The pointer `h` now points to the second entry in the array, and the pending bitmask now has the second bit as the first. Repeat the previous steps.
8. Continue repeating until pending is zero, at which point there are no more pending softirqs and the work is done.
    * This check is sufficient to ensure `h` always points to a valid entry in `softirq_vec` because `pending` has at most 32 set bits and thus this loop executes at most 32 times.
