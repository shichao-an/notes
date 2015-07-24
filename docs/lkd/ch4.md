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

##### **Mapping of nice value to weight** *

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

##### **Adding Processes to the Tree**

CFS adds processes to the rbtree and caches the leftmost node, when a process becomes runnable (wakes up) or is first created via `fork()`. Adding processes to the tree is performed by `enqueue_entity()`:

<small>[kernel/sched_fair.c#L773](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c#L773)</small>

```c
static void
enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
	/*
	 * Update the normalized vruntime before updating min_vruntime
	 * through callig update_curr().
	 */
	if (!(flags & ENQUEUE_WAKEUP) || (flags & ENQUEUE_MIGRATE))
		se->vruntime += cfs_rq->min_vruntime;

	/*
	 * Update run-time statistics of the 'current'.
	 */
	update_curr(cfs_rq);
	account_entity_enqueue(cfs_rq, se);

	if (flags & ENQUEUE_WAKEUP) {
		place_entity(cfs_rq, se, 0);
		enqueue_sleeper(cfs_rq, se);
	}

	update_stats_enqueue(cfs_rq, se);
	check_spread(cfs_rq, se);
	if (se != cfs_rq->curr)
		__enqueue_entity(cfs_rq, se);
}
```

This function updates the runtime and other statistics and then invokes `__enqueue_entity()` to perform the actual heavy lifting of inserting the entry into the red-black tree.

<small>[kernel/sched_fair.c#L328](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c#L328)</small>

```c
/*
 * Enqueue an entity into the rb-tree:
 */
static void __enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
	struct rb_node **link = &cfs_rq->tasks_timeline.rb_node;
	struct rb_node *parent = NULL;
	struct sched_entity *entry;
	s64 key = entity_key(cfs_rq, se);
	int leftmost = 1;

	/*
	 * Find the right place in the rbtree:
	 */
	while (*link) {
		parent = *link;
		entry = rb_entry(parent, struct sched_entity, run_node);
		/*
		 * We dont care about collisions. Nodes with
		 * the same key stay together.
		 */
		if (key < entity_key(cfs_rq, entry)) {
			link = &parent->rb_left;
		} else {
			link = &parent->rb_right;
			leftmost = 0;
		}
	}

	/*
	 * Maintain a cache of leftmost tree entries (it is frequently
	 * used):
	 */
	if (leftmost)
		cfs_rq->rb_leftmost = &se->run_node;

	rb_link_node(&se->run_node, parent, link);
	rb_insert_color(&se->run_node, &cfs_rq->tasks_timeline);
}
```

This function traverses the tree in the `while()` loop to search for a matching key (inserted process’s `vruntime`). It moves to the left child if the key is smaller than the current node’s key and to the right child if the key is larger.  If it ever moves to the right, even once, it knows the inserted process cannot be the new leftmost node, and it sets leftmost to zero. If it moves only to the left, `leftmost` remains one, and we have a new leftmost node and can update the cache by setting `rb_leftmost` to the inserted process. When out of the loop, the function calls `rb_link_node()` on the parent node, making the inserted process the new child. The function `rb_insert_color()` updates the self-balancing properties of the tree.

##### **Removing Processes from the Tree**

CFS removes processes from the red-black tree when a process blocks (becomes unrunnable) or terminates (ceases to exist):

<small>[kernel/sched_fair.c#L815](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c#L815)</small>

```c
static void
dequeue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int sleep)
{
	/*
	 * Update run-time statistics of the 'current'.
	 */
	update_curr(cfs_rq);

	update_stats_dequeue(cfs_rq, se);
	clear_buddies(cfs_rq, se);

	if (se != cfs_rq->curr)
		__dequeue_entity(cfs_rq, se);
	account_entity_dequeue(cfs_rq, se);
	update_min_vruntime(cfs_rq);

	/*
	 * Normalize the entity after updating the min_vruntime because the
	 * update can refer to the ->curr item and we need to reflect this
	 * movement in our normalized position.
	 */
	if (!sleep)
		se->vruntime -= cfs_rq->min_vruntime;
}
```

Similarly, the real work is performed by a helper function, `__dequeue_entity()`:

```c
static void __dequeue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
	if (cfs_rq->rb_leftmost == &se->run_node) {
		struct rb_node *next_node;

		next_node = rb_next(&se->run_node);
		cfs_rq->rb_leftmost = next_node;
	}

	rb_erase(&se->run_node, &cfs_rq->tasks_timeline);
}
```

Removing a process from the tree is much simpler because the rbtree implementation provides the `rb_erase()` function that performs all the work. The rest of this function updates the `rb_leftmost` cache. If the process-to-remove is the leftmost node, the function invokes `rb_next()` to find what would be the next node in an in-order traversal. This is what will be the leftmost node when the current leftmost node is removed.

#### The Scheduler Entry Point

The main entry point into the process schedule is the function `schedule()`, defined in `kernel/sched.c` ([kernel/sched.c#L3701](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched.c#L3701)). This is the function that the rest of the kernel uses to invoke the process scheduler, deciding which process to run and then running it.

<u>`schedule()` is generic to scheduler classes. It finds the highest priority scheduler class with a runnable process and asks it what to run next.</u> Thus, `schedule()` is simple. The only important part of the function is its invocation of `pick_next_task()`, defined in `kernel/sched.c` ([kernel/sched.c#L3670](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched.c#L3670)), which goes through each scheduler class, starting with the highest priority, and selects the highest priority process in the highest priority class:

```c
/*
 * Pick up the highest-prio task:
 */
static inline struct task_struct *
pick_next_task(struct rq *rq)
{
	const struct sched_class *class;
	struct task_struct *p;

	/*
	 * Optimization: we know that if all tasks are in
	 * the fair class we can call that function directly:
	 */
	if (likely(rq->nr_running == rq->cfs.nr_running)) {
		p = fair_sched_class.pick_next_task(rq);
		if (likely(p))
			return p;
	}

	class = sched_class_highest;
	for ( ; ; ) {
		p = class->pick_next_task(rq);
		if (p)
			return p;
		/*
		 * Will never be NULL as the idle class always
		 * returns a non-NULL p:
		 */
		class = class->next;
	}
}
```

Note the optimization at the beginning of the function. CFS is the scheduler class for normal processes, and most systems run mostly normal processes, there is a small hack to quickly select the next CFS-provided process if the number of runnable processes is equal to the number of CFS runnable processes (which suggests that all runnable processes are provided by CFS).

The core of the function is the `for()` loop, which iterates over each class in priority order, starting with the highest priority class. Each class implements the `pick_next_task()` function, which returns a pointer to its next runnable process or, if there is not one, `NULL`.The first class to return a non-`NULL` value has selected the next runnable process. CFS’s implementation of `pick_next_task()` calls `pick_next_entity()`, which in turn calls the `__pick_next_entity()` function (see [Picking the Next Task](#picking-the-next-task) in the previous section).

##### **`fair_sched_class` scheduler class** *

`fair_sched_class` is a `struct sched_class` (defined in [include/linux/sched.h](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/sched.h#L1029)) structure defined in `kernel/sched_fair.c` ([kernel/sched_fair.c#L3688](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched_fair.c#L3688)). `kernel/sched_fair.c` is included by `/kernel/sched.c` ([kernel/sched.c#L1936](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched.c#L1936)), so `fair_sched_class` is avaialble to the `pick_next_task` function in `/kernel/sched.c`.

#### Sleeping and Waking Up

Tasks that are sleeping (blocked) are in a special non-runnable state. [p58]

A task sleeps while it is waiting for some event, which may be:

* a specified amount of time;
* more data from a file I/O;
* another hardware event

A task can also involuntarily go to sleep when it tries to obtain a contended semaphore in the kernel.

Whatever the case, the kernel behavior is the same. The task does the following in turn:

* marks itself as sleeping,
* puts itself on a wait queue,
* removes itself from the red-black tree of runnable,
* and calls `schedule()` to select a new process to execute.

Waking back up is the inverse: The task is set as runnable, removed from the wait queue, and added back to the red-black tree.

Two states are associated with sleeping:

* `TASK_INTERRUPTIBLE`
* `TASK_UNINTERRUPTIBLE`

They differ only in that tasks in the `TASK_UNINTERRUPTIBLE` state ignore signals, whereas tasks in the `TASK_INTERRUPTIBLE` state wake up prematurely and respond to a signal if one is issued. Both types of sleeping tasks sit on a wait queue, waiting for an event to occur, and are not runnable.

##### **Wait Queues**

Sleeping is handled via wait queues. A wait queue is a simple list of processes waiting for an event to occur.

Wait queues are represented in the kernel by `wake_queue_head_t`. They are created statically via `DECLARE_WAITQUEUE()` or dynamically via `init_waitqueue_head()`. Processes put themselves on a wait queue and mark themselves not runnable. When the event associated with the wait queue occurs, the processes on the queue are awakened.

 It is important to implement sleeping and waking correctly, to avoid race conditions. Otherwise, it is possible to go to sleep after the condition becomes true, in which case the task might sleep indefinitely. Therefore, the recommended method for sleeping in the kernel is a bit more complicated:

```c
/* `q' is the wait queue we wish to sleep on */
DEFINE_WAIT(wait);

add_wait_queue(q, &wait);
while (!condition) { /* condition is the event that we are waiting for */
    prepare_to_wait(&q, &wait, TASK_INTERRUPTIBLE);
    if (signal_pending(current))
        /* handle signal */
    schedule();
}
finish_wait(&q, &wait);
```

The task performs the following steps to add itself to a wait queue:

1. Creates a wait queue entry via the macro `DEFINE_WAIT()`.
2. Adds itself to a wait queue via `add_wait_queue()`. This wait queue awakens the process when the condition for which it is waiting occurs. Of course, there needs to be code elsewhere that calls wake_up() on the queue when the event actually does occur.
3. Calls `prepare_to_wait()` to change the process state to either `TASK_INTERRUPTIBLE` or `TASK_UNINTERRUPTIBLE`. This function also adds the task back to the wait queue if necessary, which is needed on subsequent iterations of the loop.
4. If the state is set to `TASK_INTERRUPTIBLE`, a signal wakes the process up. This is called a **spurious wake up** (a wake-up not caused by the occurrence of the event). So check and handle signals.
5. When the task awakens, it again checks whether the condition is true. If it is, it exits the loop. Otherwise, it again calls `schedule()` and repeats.
6. After the condition is true, the task sets itself to `TASK_RUNNING` and removes itself from the wait queue via `finish_wait()`.

If the condition occurs before the task goes to sleep, the loop terminates, and the task does not erroneously go to sleep. Note that kernel code often has to perform various other tasks in the body of the loop. For example, it might need to release locks before calling `schedule()` and reacquire them after or react to other events.

The function `inotify_read()` in [fs/notify/inotify/inotify_user.c](https://github.com/shichao-an/linux-2.6.34.7/blob/master/fs/notify/inotify/inotify_user.c#L229), which handles reading from the inotify file descriptor, is a straightforward example of using wait queues:

```c
static ssize_t inotify_read(struct file *file, char __user *buf,
			    size_t count, loff_t *pos)
{
	struct fsnotify_group *group;
	struct fsnotify_event *kevent;
	char __user *start;
	int ret;
	DEFINE_WAIT(wait);

	start = buf;
	group = file->private_data;

	while (1) {
		prepare_to_wait(&group->notification_waitq, &wait, TASK_INTERRUPTIBLE);

		mutex_lock(&group->notification_mutex);
		kevent = get_one_event(group, count);
		mutex_unlock(&group->notification_mutex);

		if (kevent) {
			ret = PTR_ERR(kevent);
			if (IS_ERR(kevent))
				break;
			ret = copy_event_to_user(group, kevent, buf);
			fsnotify_put_event(kevent);
			if (ret < 0)
				break;
			buf += ret;
			count -= ret;
			continue;
		}

		ret = -EAGAIN;
		if (file->f_flags & O_NONBLOCK)
			break;
		ret = -EINTR;
		if (signal_pending(current))
			break;

		if (start != buf)
			break;

		schedule();
	}

	finish_wait(&group->notification_waitq, &wait);
	if (start != buf && ret != -EFAULT)
		ret = buf - start;
	return ret;
}
```
Some notes of the function above:

* It checks for the condition in the body of the `while()` loop, instead of in the `while()` statement itself, since checking the condition is complicated and requires grabbing locks.
* The loop is terminated via `break`.

##### **Waking Up**

`wake_up()` wakes up all the tasks waiting on the given wait queue. It does the following:

* Calls `try_to_wake_up()`, which sets the task’s state to `TASK_RUNNING`
* Calls `enqueue_task()` to add the task to the red-black tree
* Sets `need_resched` if the awakened task’s priority is higher than the priority of the current task. <u>The code that causes the event to occur typically calls `wake_up()` itself</u>.
    * For example, when data arrives from the hard disk, the VFS calls `wake_up()` on the wait queue that holds the processes waiting for the data.

Since there are spurious wake-ups, just because a task is awakened does not mean that the event for which the task is waiting has occurred. Sleeping should always be handled in a loop that ensures that the condition for which the task is waiting has indeed occurred.
The figure below depicts the relationship between each scheduler state.

[![Figure 4.1 Sleeping and waking up.](figure_4.1_600.png)](figure_4.1.png "Figure 4.1 Sleeping and waking up.")

### Preemption and Context Switching

Context switching, the switching from one runnable task to another, is handled by the `context_switch()` function defined in [kernel/sched.c](https://github.com/shichao-an/linux-2.6.34.7/blob/master/kernel/sched.c#L2908). It is called by `schedule()` when a new process has been selected to run. It does two basic jobs:

* Calls `switch_mm()`, declared in [`<asm/mmu_context.h>`](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/asm-generic/mmu_context.h), to switch the virtual memory mapping from the previous process’s to that of the new process.
* Calls `switch_to()`, declared in [`<asm/system.h>`](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/asm-generic/system.h), to switch the processor state from the previous process’s to the current’s. This involves saving and restoring stack information and the processor registers and any other architecture-specific state that must be managed and restored on a per-process basis.

##### **The `need_resched` flag** *

The kernel must know when to call `schedule()`. If it called `schedule()` only when code explicitly did so, user-space programs could run indefinitely.

The kernel provides the `need_resched` flag to signify whether a reschedule should be performed.

* This flag is set by `scheduler_tick()` (in timer interrupt handler, see [The Timer Interrupt Handler](/lkd/ch11#the-timer-interrupt-handler)) when a process should be preempted.
* This flag is set by `try_to_wake_up()` when a process that has a higher priority than the currently running process is awakened.

The kernel checks the flag, sees that it is set, and calls `schedule()` to switch to a new process.
