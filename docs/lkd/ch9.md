### **Chapter 9. An Introduction to Kernel Synchronization**

In a shared memory application, developers must ensure that shared resources are protected from concurrent access. The kernel is no exception. Shared resources require protection from concurrent access because if multiple threads of execution access and manipulate the data at the same time, the threads may overwrite each other's changes or access data while it is in an inconsistent state. Concurrent access of shared data often results in instability is hard to track down and debug.

The term *threads of execution* implies any instance of executing code. For example, this includes any of the following:

* A task in the kernel
* An interrupt handler
* A bottom half
* A kernel thread

This chapter may shorten *threads of execution* to simply *threads*. Keep in mind that this term describes any executing code.

[p161]

[Symmetrical multiprocessing](https://en.wikipedia.org/wiki/Symmetric_multiprocessing) support was introduced in the 2.0 kernel. Multiprocessing support implies that kernel code can simultaneously run on two or more processors. Consequently, without protection, code in the kernel, running on two different processors, can simultaneously access shared data at exactly the same time. With the introduction of the 2.6 kernel, the Linux kernel is preemptive. This implies that (in the absence of protection) the scheduler can preempt kernel code at virtually any point and reschedule another task. Today, a number of scenarios enable for concurrency inside the kernel, and they all require protection.

This chapter discusses the issues of concurrency and synchronization in the abstract, as they exist in any operating system kernel. The [next chapter](ch10.md) details the specific mechanisms and interfaces that the Linux kernel provides to solve synchronization issues and prevent race conditions.

### Critical Regions and Race Conditions

* Code paths that access and manipulate shared data are called [**critical regions**](https://en.wikipedia.org/wiki/Critical_section) (also called **critical sections**). It is usually unsafe for multiple threads of execution to access the same resource simultaneously.
* To prevent concurrent access during critical regions, the programmer must ensure that code executes [*atomically*](https://en.wikipedia.org/wiki/Linearizability), which means that operations complete without interruption as if the entire critical region were one indivisible instruction.
* It is a bug if it is possible for two threads of execution to be simultaneously executing within the same critical region. When this occur, it is called a [**race condition**](https://en.wikipedia.org/wiki/Race_condition), so-named because the threads raced to get there first. Debugging race conditions is often difficult because they are not easily reproducible.
* Ensuring that unsafe concurrency is prevented and that race conditions do not occur is called [**synchronization**](https://en.wikipedia.org/wiki/Synchronization_(computer_science)).

#### Why Do We Need Protection?

To best understand the need for synchronization, look at the ubiquity of race conditions.

The first example is a real-world case: an ATM (Automated Teller Machine, called a cash machine).

After the user has asked for a specific amount of money, the cash machine needs to
ensure that the money actually exists in that user's account and deducts the withdrawal from the total funds available. The code would be like:

```c
int total = get_total_from_account(); /* total funds in account */
int withdrawal = get_withdrawal_amount(); /* amount user asked to withdrawal */

/* check whether the user has enough funds in her account */
if (total < withdrawal) {
	error(“You do not have that much money!”)
	return -1;
}

/* OK, the user has enough money: deduct the withdrawal amount from her total */
total -= withdrawal;
update_total_funds(total);

/* give the user their money */
spit_out_money(withdrawal);
```

Assume that another deduction in the user's funds is happening at the same time, which could be: user's spouse is initiating another withdrawal at another ATM, a payee is electronically transferring funds out of the account, or the bank is deducting a fee from the account (as banks these days are so wont to do).

Both systems performing the withdrawal would have similar code as above: first check whether the deduction is possible, then compute the new total funds, and finally execute the physical deduction. Presume that the first deduction is a withdrawal from an ATM for $100 and that the second deduction is the bank applying a fee of $10 because the customer walked into the bank.  Assume the customer has a total of $105 in the bank. Obviously, one of these transactions cannot correctly complete.

Assume that the two transactions are initiated at roughly the same time. Both transactions verify that sufficient funds exist: $105 is more than both $100 and $10, so all is good. Then the withdrawal process subtracts $100 from $105, yielding $5. The fee transaction then does the same, subtracting $10 from $105 and getting $95. The withdrawal process then updates the user's new total available funds to $5. Now the fee transaction also updates the new total, resulting in $95 (free money).

Clearly, financial institutions must ensure that this can never happen. They must lock the account during certain operations, making each transaction atomic with respect to any other transaction. Such transactions must occur in their entirety, without interruption, or not occur at all.

#### The Single Variable

Consider a simple shared resource, a single global integer, and a simple critical region, the operation of merely incrementing it: `i++`;

This might translate into machine instructions to the computer's processor that resemble the following:

* Get the current value of `i` and copy it into a register.
* Add one to the value stored in the register.
* Write back to memory the new value of `i`.

Assume that there are two threads of execution, both enter this critical region, and the initial value of `i` is 7. The desired outcome is then similar to the following (with each row representing a unit of time):

Thread 1 | Thread 2
-------- | --------
get `i` (7) | —
increment `i` (7 -> 8) | —
write back `i` (8) | —
— | get `i` (8)
— | increment `i` (8 -> 9)
— | write back `i` (9)

As expected, 7 incremented twice is 9.

However, another possible outcome is the following:

Thread 1 | Thread 2
-------- | --------
get `i` (7) | get `i` (7)
increment `i` (7 -> 8) | —
— | increment `i` (7 -> 8)
write back `i` (8) | —
— | write back `i` (8)

If both threads of execution read the initial value of `i` before it is incremented, both threads increment and save the same value. As a result, the variable `i` contains the value 8 when, in fact, it should now contain 9. This is one of the simplest examples of a critical region. The solution is simple. We merely need a way to perform these operations in one indivisible step. Most processors provide an instruction to atomically read, increment, and write back a single variable. Using this atomic instruction, the only possible outcome (or conversely with Thread 2 incrementing `i` first) is:

Thread 1 | Thread 2
-------- | --------
increment & store `i` (7 -> 8) | —
— | increment & store `i` (8 -> 9)

It would never be possible for the two atomic operations to interleave. The processor would physically ensure that it was impossible. Using such an instruction would alleviate the problem. The kernel provides a set of interfaces that implement these atomic instructions, which are discussed in the next chapter.

### Locking

Assume you have a queue of requests that needs to be serviced and the implementation is a linked list, in which each node represents a request. Two functions manipulate the queue:

* One function adds a new request to the tail of the queue.
* One function removes a request from the head of the queue and service request.

Requests are continually being added, removed, and serviced, since various parts of the kernel invoke these two functions. Manipulating the request queues certainly requires multiple instructions. If one thread attempts to read from the queue while another is in the middle of manipulating it, the reading thread will find the queue in an inconsistent state. It should be apparent the sort of damage that could occur if access to the queue could occur concurrently. Often, when the shared resource is a complex data structure, the result of a race condition is corruption of the data structure.

How can you prevent one processor from reading from the queue while another processor is updating it?  Although it is feasible for a particular architecture to implement simple instructions, such as arithmetic and comparison, atomically it is ludicrous for architectures to provide instructions to support the indefinitely sized critical regions that would exist in the example. What is needed is a way of making sure that only one thread manipulates the data structure at a time, a mechanism for preventing access to a resource while another thread of execution is in the marked region.

A lock provides such a mechanism. [p165] Threads hold locks; locks protect data.

* Whenever there was a new request to add to the queue, the thread would first obtain the lock. Then it could safely add the request to the queue and ultimately release the lock.
* When a thread wanted to remove a request from the queue, it would also obtain the lock. Then it could read the request and remove it from the queue. Finally, it would release the lock.

Any other access to the queue would similarly need to obtain the lock.  Because the lock can be held by only one thread at a time, only a single thread can manipulate the queue at a time. If a thread comes along while another thread is already updating it, the second thread has to wait for the first to release the lock before it can continue. The lock prevents concurrency and protects the queue from race conditions.

Any code that accesses the queue first needs to obtain the relevant lock. If another thread of execution comes along, the lock prevents concurrency:

Thread 1 | Thread 2
-------- | --------
try to lock the queue | try to lock the queue
succeeded: acquired lock | failed: waiting...
access queue... | waiting...
unlock the queue | waiting...
... | succeeded: acquired lock
| access queue...
| unlock the queue

Notice that locks are *advisory* and *voluntary*. Locks are entirely a programming construct that the programmer must take advantage of. Nothing prevents you from writing code that manipulates the fictional queue without the appropriate lock, but such a practice would eventually result in a race condition and corruption.

Locks come in various shapes and sizes. Linux alone implements a handful of different locking mechanisms. The most significant difference between the various mechanisms is the behavior when the lock is unavailable because another thread already holds it:

* Some lock variants [busy wait](https://en.wikipedia.org/wiki/Busy_waiting) (spin in a tight loop, checking the status of the lock over and over, waiting for the lock to become available)
* Other locks put the current task to sleep until the lock becomes available.

The next chapter discusses the behavior of the different locks in Linux and their interfaces.

As you may notice, the lock does not solve the problem; it simply shrinks the critical region down to just the lock and unlock code: probably much smaller, but still a potential race. Fortunately, locks are implemented using atomic operations that ensure no race exists. A single instruction can verify whether the key is taken and, if not, seize it. How this is done is architecture-specific, but almost all processors implement an atomic [*test and set*](https://en.wikipedia.org/wiki/Test-and-set) instruction that tests the value of an integer and sets it to a new value only if it is zero. A value of zero means unlocked. On the popular x86 architecture, locks are implemented using such a similar instruction called [*compare and exchange*](https://en.wikipedia.org/wiki/Compare-and-swap).

#### Causes of Concurrency

In user-space, programs are scheduled preemptively at the will of the scheduler. Because a process can be preempted at any time and another process can be scheduled onto the processor, a process can be involuntarily preempted in the middle of accessing a critical region. If the newly scheduled process then enters the same critical region (for example, if the two processes manipulate the same shared memory or write to the same file descriptor), a race can occur. The same problem can occur with multiple single-threaded processes sharing files, or within a single program with signals, because signals can occur asynchronously. This type of concurrency in which two things do not actually happen at the same time but interleave with each other is called *pseudo-concurrency*.

If you have a symmetrical multiprocessing machine, two processes can actually be executed in a critical region at the exact same time. That is called *true concurrency*. Although the causes and semantics of true versus pseudo concurrency are different, they both result in the same race conditions and require the same sort of protection.

The kernel has similar causes of concurrency:

* **Interrupts**. An interrupt can occur asynchronously at almost any time, interrupting the currently executing code.
* **Softirqs and tasklets**. The kernel can raise or schedule a softirq or tasklet at almost any time, interrupting the currently executing code.
* **Kernel preemption**. Because the kernel is preemptive, one task in the kernel can preempt another.
* **Sleeping and synchronization with user-space**. A task in the kernel can sleep and thus invoke the scheduler, resulting in the running of a new process.
* ** Symmetrical multiprocessing**. Two or more processors can execute kernel code at exactly the same time.

Kernel developers need to understand and prepare for these causes of concurrency:

* It is a major bug if an interrupt occurs in the middle of code that is manipulating a resource and the interrupt handler can access the same resource.
* Similarly, it is a bug if kernel code is preemptive while it is accessing a shared resource.
* Likewise, it is a bug if code in the kernel sleeps while in the middle of a critical section.
* Finally, two processors should never simultaneously access the same piece of data.

With a clear picture of what data needs protection, it is not hard to provide the locking to keep the system stable. Rather, the hard part is identifying these conditions and realizing that to prevent concurrency, you need some form of protection.

##### **Design proper locking from the beginning** *

Implementing the actual locking in your code to protect shared data is not difficult, especially when done early on during the design phase of development. The tricky part is identifying the actual shared data and the corresponding critical sections. This is why designing locking into your code from the get-go, and not as an afterthought, is of paramount importance. It can be difficult to go in, ex post, and identify critical regions and retrofit locking into the existing code. The resulting code is often not pretty, either. The takeaway from this is to always design proper locking into your code from the beginning.

##### **Definitions of concurrency safe terms** *

* Code that is safe from concurrent access from an interrupt handler is said to be *interrupt-safe*.
* Code that is safe from concurrency on symmetrical multiprocessing machines is *SMP-safe*.
* Code that is safe from concurrency with kernel preemption is *preempt-safe* (barring a few exceptions, being SMP-safe implies being preempt-safe).

The actual mechanisms used to provide synchronization and protect against race conditions in all these cases is covered in the next chapter.

#### Knowing What to Protect

Identifying what data specifically needs protection is vital. Since any data that can be accessed concurrently almost assuredly needs protection, <u>it is often easier to identify what data does not need protection and work from there:</u>

* Obviously, any data that is local to one particular thread of execution does not need protection, because only that thread can access the data. For example, local automatic variables (and dynamically allocated data structures whose address is stored only on the stack) do not need any sort of locking because they exist solely on the stack of the executing thread.
* Likewise, data that is accessed by only a specific task does not require locking (because a process can execute on only one processor at a time).

##### **What does need locking?** *

Most global kernel data structures require locking. A good rule of thumb is that if another thread of execution can access the data, the data needs some sort of locking; if anyone else can see it, lock it. <u>Remember to lock data, not code.</u>

##### **CONFIG Options: SMP Versus UP** *

Because the Linux kernel is configurable at compile time, you can tailor the kernel specifically for a given machine:

* The `CONFIG_SMP` configure option controls whether the kernel supports SMP. Many locking issues disappear on uniprocessor machines; consequently, when `CONFIG_SMP` is unset, unnecessary code is not compiled into the kernel image. For example, such configuration enables uniprocessor machines to forego the overhead of spin locks.
* The same trick applies to `CONFIG_PREEMPT` (the configure option enabling kernel preemption).

This was an excellent design decision: the kernel maintains one clean source base, and the various locking mechanisms are used as needed. Different combinations of `CONFIG_SMP` and `CONFIG_PREEMPT` on different architectures compile in varying lock support.

In your code, provide appropriate protection for the most pessimistic case, SMP with kernel preemption, and all scenarios will be covered.

Ask yourself these questions whenever you write kernel code:

* Is the data global? Can a thread of execution other than the current one access it?
* Is the data shared between process context and interrupt context? Is it shared between two different interrupt handlers?
* If a process is preempted while accessing this data, can the newly scheduled process access the same data?
* Can the current process sleep (block) on anything? If it does, in what state does that leave any shared data?
* What prevents the data from being freed out from under me?
* What happens if this function is called again on another processor?
* Given the proceeding points, how am I going to ensure that my code is safe from concurrency?

In short, nearly all global and shared data in the kernel requires some form of the synchronization methods, discussed in the next chapter.

### Deadlocks

A [**deadlock**](https://en.wikipedia.org/wiki/Deadlock) is a condition involving one or more threads of execution and one or more resources, such that each thread waits for one of the resources, but all the resources are already held. The threads all wait for each other, but they never make any progress toward releasing the resources that they already hold. Therefore, none of the threads can continue, which results in a deadlock.

A good analogy is a [four-way traffic stop](https://en.wikipedia.org/wiki/All-way_stop). If each car at the stop decides to wait for the other cars before going, no car will ever proceed, and we have a traffic deadlock.

The simplest example of a deadlock is the self-deadlock. If a thread of execution attempts to acquire a lock it already holds, it has to wait for the lock to be released. But it will never release the lock, because it is busy waiting for the lock, and the result is deadlock:

```
acquire lock
acquire lock, again
wait for lock to become available
...
```

Some kernels prevent this type of deadlock by providing [recursive locks](https://en.wikipedia.org/wiki/Reentrant_mutex). These are locks that a single thread of execution may acquire multiple times. Linux does not provide recursive locks. This is widely considered a good thing. Although recursive locks might alleviate the self-deadlock problem, they very readily lead to sloppy locking semantics.

Similarly, consider *n* threads and *n* locks. If each thread holds a lock that the other thread wants, all threads block while waiting for their respective locks to become available. The most common example is with two threads and two locks, which is often called the *deadly embrace* or the *ABBA deadlock*:

Thread 1 | Thread 2
-------- | --------
acquire lock A | acquire lock B
try to acquire lock B | try to acquire lock A
wait for lock B | wait for lock A

Each thread is waiting for the other, and neither thread will ever release its original lock; therefore, neither lock will become available.

Prevention of deadlock scenarios is important.Although it is difficult to prove that code is free of deadlocks, you can write deadlock-free code following the rules below:

* Implement lock ordering. Nested locks must always be obtained in the same order. This prevents the deadly embrace deadlock. Document the lock ordering so others will follow it.
* Prevent [starvation](https://en.wikipedia.org/wiki/Starvation_(computer_science)). Ask yourself:
    * Does this code always finish?
    * If foo does not occur, will bar wait forever?
* Do not double acquire the same lock.
* Design for simplicity. Complexity in your locking scheme invites deadlocks.

The first point is most important and worth stressing. <u>If two or more locks are acquired at the same time, they must always be acquired in the same order.</u>

Assume you have the cat, dog, and fox locks that protect data structures of the same name. Now assume you have a function that needs to work on all three of these data structures simultaneously. Whatever the case, the data structures require locking to ensure safe access. If one function acquires the locks in the order cat, dog, and then fox, then every other function must obtain these locks (or a subset of them) in this same order. For example, it is a potential deadlock (and hence a bug) to first obtain the fox lock and then obtain the dog lock because the dog lock must always be acquired prior to the fox lock.

The following is an example that would cause a deadlock:

Thread 1 | Thread 2
-------- | --------
acquire lock cat | acquire lock fox
acquire lock dog | try to acquire lock dog
try to acquire lock fox | wait for lock dog
wait for lock fox | —

Thread one is waiting for the fox lock, which thread two holds, while thread two is waiting for the dog lock, which thread one holds. Neither ever releases its lock and hence both wait forever. If the locks were always obtained in the same order, a deadlock in this manner would not be possible.

Whenever locks are nested within other locks, a specific ordering must be obeyed. It is
good practice to place the ordering in a comment above the lock:

```c
/*
* cat_lock – locks access to the cat structure
* always obtain before the dog lock!
*/
```

<u>The order of *unlock* does not matter with respect to deadlock, although it is common practice to release the locks in an order inverse to that in which they were acquired.</u>

Preventing deadlocks is important. The Linux kernel has some basic debugging facilities for detecting deadlock scenarios in a running kernel, which are discussed in the next chapter.

### Doubts and Solution

#### Verbatim

##### **p169 on "Knowing What to Protect"**

> What prevents the data from being freed out from under me?

<span class="text-danger">Question</span>: What does it mean and why is it one of the questions asked to ensure the code is safe from concurrency.
