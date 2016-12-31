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
