### **Chapter 4. Process Scheduling**

This chapter discusses the **process scheduler**, the kernel subsystem that puts those processes to work.

The process scheduler (or simply the scheduler) divides the finite resource of processor time between the runnable processes on a system. It is responsible for best utilizing the system and giving users the impression that multiple processes are executing simultaneously. [p41]

To best utilize processor time, assuming there are runnable processes, a process should always be running. If there are more *runnable* processes than processors in a system, some processes will not be running at a given moment. These processes are *waiting to run*. Deciding which process runs next, given a set of runnable processes, is the fundamental decision that the scheduler must make.

### Multitasking

A **multitasking** operating system is one that can simultaneously interleave execution of more than one process.

* On single processor machines, this gives the illusion of multiple processes running concurrently.
* On multiprocessor machines, this enables processes to actually run concurrently, in parallel, on different processors.

On either type of machine, it also enables many processes to *block* or *sleep*. Although these processes are in memory, they are not *runnable*. These processes utilize the kernel to wait until some event (keyboard input, network data, passage of time, and so on) occurs. [p41]

Multitasking operating systems come in two flavors:

* **Cooperative multitasking**
* **Preemptive multitasking**

#### Preemptive multitasking

Linux, like all Unix variants and most modern operating systems, implements preemptive multitasking. In preemptive multitasking, the scheduler decides
when a process is to cease running and a new process is to begin running.

* **Preemption**: the act of involuntarily suspending a running process.
* **Timeslice** of a process: the time the process runs before it is preempted is usually predetermined.
    * Managing the timeslice enables the scheduler to make global scheduling decisions for the system and prevents any one process from monopolizing the processor.
    * On many modern operating systems, the timeslice is dynamically calculated as a function of process behavior and configurable system policy.
    * Linux’s unique "fair" scheduler does not employ timeslices *per se*, to interesting effect.

#### Cooperative multitasking

In cooperative multitasking, a process does not stop running until it voluntarily decides to do so. The act of a process voluntarily suspending itself is called **yielding**, but the operating system cannot enforce this.

The shortcomings of this approach are manifest:

* The scheduler cannot make global decisions regarding how long processes run;
* Processes can monopolize the processor for longer than the user desires;
* A hung process that never yields can potentially bring down the entire system.

[p42]

### Linux’s Process Scheduler

From Linux’s first version in 1991 through the 2.4 kernel series, the Linux scheduler was simple in design. It was easy to understand, but scaled poorly in light of many runnable processes or many processors.

During the 2.5 kernel development series, the **O(1) scheduler** solved the shortcomings of the previous Linux scheduler and introduced powerful new features and performance characteristics. By introducing a constant-time algorithm for timeslice calculation and per-processor runqueues, it rectified the design limitations of the earlier scheduler.

However, the O(1) scheduler had several pathological failures related to scheduling latency-sensitive applications (interactive processes). Thus, although the O(1) scheduler was ideal for large server workloads, which lack interactive processes, it performed below par on desktop systems, where interactive applications are the *raison d’être*.

Beginning in the 2.6 kernel series, developers introduced new process schedulers aimed at improving the interactive performance of the O(1) scheduler. The most notable of these was the **Rotating Staircase Deadline** scheduler, which introduced the concept of **fair scheduling**, borrowed from queuing theory, to Linux’s process scheduler. This concept was the inspiration for the O(1) scheduler’s eventual replacement in kernel version 2.6.23, the **Completely Fair Scheduler** (CFS).

This chapter discusses the fundamentals of scheduler design and how they apply to the Completely Fair Scheduler and its goals, design, implementation, algorithms, and related system calls. We also discuss the O(1) scheduler because its implementation is a more "classic" Unix process scheduler model.

### Policy

Policy is the behavior of the scheduler that determines what runs when.

#### I/O-Bound Versus Processor-Bound Processes

Processes can be classified as either **I/O-bound** or **processor-bound**.

* An **I/O-bound process** spends much of its time submitting and waiting on I/O requests. Such a process is runnable for only short durations, because it eventually blocks waiting on more I/O.
    * "I/O" means any type of blockable resource, such as keyboard input or network I/O, and not just disk I/O. Most graphical user interface (GUI) applications are I/O-bound, even if they never read from or write to the disk, because they spend most of their time waiting on user interaction via the keyboard and mouse.
* **Processor-bound processes** spend much of their time executing code. Thet tend to run until they are preempted because they do not block on I/O requests very often. System response does not dictate that the scheduler run them often. A scheduler policy for processor-bound processes tends to run such processes less frequently but for longer durations.
    * Examples of processor-bound processes include: a program executing an infinite loop, *ssh-keygen*, *MATLAB*.

These classifications are not mutually exclusive. Processes can exhibit both behaviors simultaneously:

* The X Window server is both processor and I/O intense.
* A word processor can be I/O-bound but dive into periods of intense processor action.

The scheduling policy in a system must attempt to satisfy two conflicting goals:

* Fast process response time (low latency)
* Maximal system utilization (high throughput)

##### **Favoring I/O-bound over processor-bound**

Schedulers often employ complex algorithms to determine the most worthwhile process to run while not compromising fairness to other processes with lower priority. [p43-44]

* The scheduler policy in Unix systems tends to explicitly favor I/O-bound processes, thus providing good process response time.
* Linux, aiming to provide good interactive response and desktop performance, optimizes for process response (low latency), thus favoring I/O-bound processes over processor-bound processes. This is done in a creative manner that does not neglect processor-bound processes.

#### Process Priority

The **priority-based** scheduling is a common type of scheduling algorithm, which isn’t exactly implemented on Linux. It means that processes with a higher priority run before those with a lower priority, whereas processes with the same priority are scheduled *round-robin* (one after the next, repeating). On some systems, processes with a higher priority also receive a longer timeslice. The runnable process with timeslice remaining and the highest priority always runs. [p44]

##### **nice value and real-time priority**

The Linux kernel implements two separate priority ranges:

* **nice value** (a number from –20 to +19 with a default of 0) is the standard priority range used in all Unix systems:
    * Processes with a lower nice value (higher priority) receive a larger proportion of the system’s processor, and vice versa.
    * In Linux, the nice value is a control over the *proportion* of timeslice. In other Unix-based systems, such as Mac OS X, the nice value is a control over the *absolute* timeslice allotted to a process;
    * The `ps -el` command lists processes with their nice values.
* **Real-time priority** (configurable values that by default range from 0 to 99)
    * Higher real-time priority values correspond to a greater priority.
    * All real-time processes are at a higher priority than normal processes.
    * Linux implements real-time priorities in accordance with the relevant Unix standards, specifically POSIX.1b.
    * The `ps -eo state,uid,pid,ppid,rtprio,time,comm` command lists processes and their real-time priority. A value of “-” means the process is not real-time.

#### Timeslice

The *timeslice* is the numeric value that represents how long a task can run until it is preempted.

* Too long a timeslice causes the system to have poor interactive performance.
* Too short a timeslice causes significant amounts of processor time to be wasted on the overhead of switching processes.

The conflicting goals of I/O bound versus processor-bound processes:

* I/O-bound processes do not need longer timeslices (although they do like to run often)
* Processor-bound processes crave long timeslices (to keep their caches hot).

##### **Timeslice on Linux**

Linux’s CFS scheduler does not directly assign timeslices to processes, but assigns processes a *proportion* of the processor. The amount of processor time that a process receives is a function of the load of the system. This assigned proportion is further affected by each process’s nice value. The nice value acts as a weight, changing the proportion of the processor time each process receives. Processes with higher nice values (a lower priority) receive a deflationary weight, yielding them a smaller proportion of the processor, and vice versa.

With the CFS scheduler, whether the process runs immediately (preempting the currently running process) is a function of how much of a proportion of the processor the newly runnable processor has consumed. If it has consumed a smaller proportion of the processor than the currently executing process, it runs immediately

#### The Scheduling Policy in Action

Consider a system with two runnable tasks: a text editor (I/O-bound) and a video encoder (processor-bound). [p45-46]

Ideally, the scheduler gives the text editor a larger proportion of the available processor than the video encoder, because the text editor is interactive. We have two goals for the text editor:

1. We want the text editor to have a large amount of processor time available to it; not because it needs a lot of processor (it does not) but because we want it to always have processor time available the moment it needs it.
2. We want the text editor to preempt the video encoder the moment it wakes up (say, when the user presses a key). This can ensure the text editor has good *interactive performance* and is responsive to user input.

**How the above two goals achieved**

1. Instead of assigning the text editor a specific priority and timeslice, the Linux guarantees the text editor a specific proportion of the processor. If the two are the only processes with same nice values, each would be guaranteed half of the processor’s time (the proportion is 50%). Because the text editor spends most of its time blocked, waiting for user key presses, it does not use anywhere near 50% of the processor. Conversely, the video encoder is free to use more than its allotted 50%, enabling it to finish the encoding quickly.
2. When the editor wakes up, CFS notes that it is allotted 50% of the processor but has used considerably less, and thus determines that the text editor has run for *less time* than the video encoder. Attempting to give all processes a fair share of the processor, it then preempts the video encoder and enables the text editor to run. [p46]


### The Linux Scheduling Algorithm

#### Scheduler Classes

The Linux scheduler is modular, enabling different algorithms to schedule different types of processes.This modularity is called **scheduler classes**. The base scheduler code, which is defined in [`kernel/sched.c`](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched.c), iterates over each scheduler class in order of priority.The highest priority scheduler class that has a runnable process wins, selecting who runs next.

The Completely Fair Scheduler (CFS) is the registered scheduler class for normal processes, called `SCHED_NORMAL` in Linux (and `SCHED_OTHER` in POSIX).  CFS is defined in [`kernel/sched_fair.c`](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c). The rest of this section discusses the CFS algorithm.

#### Process Scheduling in Unix Systems

To discuss fair scheduling, we must first describe how traditional Unix systems schedule processes.

Modern process schedulers have two common concepts: process priority and timeslice. Processes with a higher priority run more frequently and (on many systems) receive a higher timeslice. On Unix, the priority is exported to user-space in the form of nice values. This in practice leads to several problems:

1. Mapping nice values onto timeslices requires a decision about what absolute timeslice to allot each nice value, which leads to suboptimal switching behavior. [p47]
2. Nicing (down) a process by a relative nice value has wildly different effects depending on the starting nice value. [p47-48]
3. Absolute timeslice timeslice must be some integer multiple of the timer tick, which introduces several problems. [p48]
4. Handling process wake up in a priority-based scheduler that wants to optimize for interactive tasks may cause the scheduler providing one process an unfair amount of processor time, at the expense of the rest of the system. [p48]

The approach taken by CFS is a radical (for process schedulers) rethinking of timeslice allotment: Do away with timeslices completely and assign each process a proportion of the processor. CFS thus yields constant fairness but a variable switching rate.

#### Fair Scheduling

CFS is based on a simple concept: Model process scheduling as if the system had an ideal, perfectly multitasking processor. In such a system, each process would receive 1/*n* of the processor’s time, where *n* is the number of runnable processes, and we’d schedule them for infinitely small durations, so that in any measurable period we’d have run all *n* processes for the same amount of time. [p48]

It is not efficient to run processes for infinitely small durations; there is a switching cost to preempting one process for another: the overhead of swapping one process for another and the effects on caches. CFS will run each process for some amount of time, round-robin, selecting next the process that has run the least. Rather than assign each process a timeslice, CFS calculates how long a process should run as a function of the total number of runnable processes. Instead of using the nice value to calculate a timeslice, CFS uses the nice value to weight the proportion of processor a process is to receive. [p49]

<u>Each process runs for a "timeslice" proportional to its weight divided by the total weight of all runnable threads.</u> CFS sets a target for its
approximation of the "infinitely small" scheduling duration in perfect multitasking. This target is called the **targeted latency**. Smaller targets yield better interactivity and a closer approximation to perfect multitasking, at the expense of higher switching costs and thus worse overall throughput.  CFS imposes a floor on the timeslice assigned to each process, called the **minimum granularity** (by default 1 millisecond). Even as the number of runnable processes approaches infinity, each will run for at least 1 millisecond, to ensure there is a ceiling on the incurred switching costs

For the nice value on weighting the proportion, consider the case of two runnable processes with disimilar nice values. One with the default nice value (zero) and one with a nice value of 5. In this case, the weights work out to about a 1⁄3 penalty for the nice-5 process. If our target latency is again 20 milliseconds, our two processes will receive 15 milliseconds and 5 milliseconds each of processor time, respectively. Put generally, the proportion of processor time that any process receives is determined only by the relative difference in niceness between it and the other runnable processes.  The nice values, instead of yielding additive increases to timeslices, yield geometric differences. [p49-50]

### The Linux Scheduling Implementation

CFS’s actual implementation lives in [kernel/sched_fair.c](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c). Specifically,
this sections discusses four components of CFS:

* Time Accounting
* Process Selection
* The Scheduler Entry Point
* Sleeping and Waking Up

#### Time Accounting

All process schedulers must account for the time that a process runs. On each tick of the system clock, the timeslice is decremented by the tick period.When the timeslice reaches zero, the process is preempted in favor of another runnable process with a nonzero timeslice.

##### **The Scheduler Entity Structure**

CFS does not have the notion of a timeslice, but it must still keep account for the time that each process runs. [p50]

CFS uses the **scheduler entity structure**, `struct sched_entity`, defined in `<linux/sched.h>` ([include/linux/sched.h#L1090](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/sched.h#L1090)), to keep track of process accounting:

```c
struct sched_entity {
    struct load_weight load;
    struct rb_node run_node;
    struct list_head group_node;
    unsigned int on_rq;
    u64 exec_start;
    u64 sum_exec_runtime;
    u64 vruntime;
    u64 prev_sum_exec_runtime;
    u64 last_wakeup;
    u64 avg_overlap;
    u64 nr_migrations;
    u64 start_runtime;
    u64 avg_wakeup;

/* many stat variables elided, enabled only if CONFIG_SCHEDSTATS is set */
};
```

The scheduler entity structure is embedded in the process descriptor, `struct task_stuct`, as a member variable named `se` ([include/linux/sched.h#L1188](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/sched.h#L1188)).

##### Mapping of nice value to weight *

The mapping of nice to weight is defined in the `prio_to_weight` constant array ([/kernel/sched.c#L1362](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched.c#L1362)). The weight is roughly equivalent to `1024/(1.25)^(nice)`.

```c
static const int prio_to_weight[40] = {
 /* -20 */     88761,     71755,     56483,     46273,     36291,
 /* -15 */     29154,     23254,     18705,     14949,     11916,
 /* -10 */      9548,      7620,      6100,      4904,      3906,
 /*  -5 */      3121,      2501,      1991,      1586,      1277,
 /*   0 */      1024,       820,       655,       526,       423,
 /*   5 */       335,       272,       215,       172,       137,
 /*  10 */       110,        87,        70,        56,        45,
 /*  15 */        36,        29,        23,        18,        15,
};
```

##### **The Virtual Runtime**

The `vruntime` variable stores the **virtual runtime** of a process, which is the actual runtime (the amount of time spent running) normalized (or weighted) by the number of runnable processes. The virtual runtime’s units are nanoseconds and therefore `vruntime` is decoupled from the timer tick. Because processors are not capable of perfect multitasking and we must run each process in succession, CFS uses vruntime to account for how long a process has run and thus how much longer it ought to run.

The function `update_curr()`, defined in `kernel/sched_fair.c` ([kernel/sched_fair.c#L518](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c#L518)), manages this accounting:

```c
static void update_curr(struct cfs_rq *cfs_rq)
{
	struct sched_entity *curr = cfs_rq->curr;
	u64 now = rq_of(cfs_rq)->clock;
	unsigned long delta_exec;

	if (unlikely(!curr))
		return;

	/*
	 * Get the amount of time the current task was running
	 * since the last time we changed load (this cannot
	 * overflow on 32 bits):
	 */
	delta_exec = (unsigned long)(now - curr->exec_start);
	if (!delta_exec)
		return;

	__update_curr(cfs_rq, curr, delta_exec);
	curr->exec_start = now;

	if (entity_is_task(curr)) {
		struct task_struct *curtask = task_of(curr);

		trace_sched_stat_runtime(curtask, delta_exec, curr->vruntime);
		cpuacct_charge(curtask, delta_exec);
		account_group_exec_runtime(curtask, delta_exec);
	}
}
```

`update_curr()` calculates the execution time of the current process and stores that value in `delta_exec`. It then passes that runtime to `__update_curr()`, which weights the time by the number of runnable processes. The current process’s vruntime is then incremented by the weighted value:

```c
/*
 * Update the current task's runtime statistics. Skip current tasks that
 * are not in our scheduling class.
 */
static inline void
__update_curr(struct cfs_rq *cfs_rq, struct sched_entity *curr,
	      unsigned long delta_exec)
{
	unsigned long delta_exec_weighted;

	schedstat_set(curr->exec_max, max((u64)delta_exec, curr->exec_max));

	curr->sum_exec_runtime += delta_exec;
	schedstat_add(cfs_rq, exec_clock, delta_exec);
	delta_exec_weighted = calc_delta_fair(delta_exec, curr);

	curr->vruntime += delta_exec_weighted;
	update_min_vruntime(cfs_rq);
}
```

`update_curr()` is invoked periodically by the system timer and also whenever a process becomes runnable or blocks, becoming unrunnable. In this manner, vruntime is an accurate measure of the runtime of a given process and an indicator of what process should run next.

##### **The `calc_delta_fair()` function**

`__update_curr()` calls `calc_delta_fair()`, which in turn calls `calc_delta_mine()` (if `se->load.weight` does not equal `NICE_0_LOAD`) to calculate the weighted value:

<small>[kernel/sched_fair.c#L431](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c#L431)</small>

```c
/*
 * delta /= w
 */
static inline unsigned long
calc_delta_fair(unsigned long delta, struct sched_entity *se)
{
	if (unlikely(se->load.weight != NICE_0_LOAD))
		delta = calc_delta_mine(delta, NICE_0_LOAD, &se->load);

	return delta;
}
```
<small>[kernel/sched.c#L1300](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched.c#L1300)</small>

```c
/*
 * delta *= weight / lw
 */
static unsigned long
calc_delta_mine(unsigned long delta_exec, unsigned long weight,
		struct load_weight *lw)
{
	u64 tmp;

	if (!lw->inv_weight) {
		if (BITS_PER_LONG > 32 && unlikely(lw->weight >= WMULT_CONST))
			lw->inv_weight = 1;
		else
			lw->inv_weight = 1 + (WMULT_CONST-lw->weight/2)
				/ (lw->weight+1);
	}

	tmp = (u64)delta_exec * weight;
	/*
	 * Check whether we'd overflow the 64-bit multiplication:
	 */
	if (unlikely(tmp > WMULT_CONST))
		tmp = SRR(SRR(tmp, WMULT_SHIFT/2) * lw->inv_weight,
			WMULT_SHIFT/2);
	else
		tmp = SRR(tmp * lw->inv_weight, WMULT_SHIFT);

	return (unsigned long)min(tmp, (u64)(unsigned long)LONG_MAX);
}
```

This can be summarized as:

```text
delta_exec_weighted = delta_exec * NICE_0_LOAD / se->load
```

For division details, see [Explanation of the calc_delta_mine function](http://stackoverflow.com/questions/17776451).

#### Process Selection

CFS attempts to balance a process’s virtual runtime with a simple rule: <u>when deciding what process to run next, it picks the process with the smallest `vruntime`.</u>

CFS uses a [red-black tree](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree) to manage the list of runnable processes and efficiently find the process with the smallest `vruntime`. A red-black tree, called an *rbtree* in Linux ([include/linux/rbtree.h](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/rbtree.h), [lib/rbtree.c](https://github.com/shichao-an/linux-2.6.34.7/blob/master/lib/rbtree.c)), is a type of [self-balancing binary search tree](https://en.wikipedia.org/wiki/Self-balancing_binary_search_tree). It is a data structure that store nodes of arbitrary data, identified by a specific key, and that they enable efficient search for a given key. Specifically, obtaining a node identified by a given key is logarithmic in time as a function of total nodes in the tree.

##### **Picking the Next Task**

The process that CFS wants to run next, which is the process with the smallest `vruntime`, is the leftmost node in the tree. If you follow the tree from the root down through the left child, and continue moving to the left until you reach a leaf node, you find the process with the smallest `vruntime`. CFS’s process selection algorithm is thus summed up as "run the process represented by the leftmost node in the rbtree." [p53]

The function that performs this selection is `__pick_next_entity()`, defined in `kernel/sched_fair.c`([kernel/sched_fair.c#L377](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c#L377)):

```c
static struct sched_entity *__pick_next_entity(struct cfs_rq *cfs_rq)
{
	struct rb_node *left = cfs_rq->rb_leftmost;

	if (!left)
		return NULL;

	return rb_entry(left, struct sched_entity, run_node);
}
```

Note that `__pick_next_entity()` does not actually traverse the tree to find the leftmost node, because the value is cached by `rb_leftmost`, though it is efficient to walk the tree to find the leftmost node (`O(height of tree)`, which is `O(log N)` for `N` nodes if the tree is balanced).

The return value from this function is the process that CFS next runs. If the function returns NULL, there is no leftmost node, and thus no nodes in the tree. In that case, there are no runnable processes, and CFS schedules the idle task.
