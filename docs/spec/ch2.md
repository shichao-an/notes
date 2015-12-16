### **Chapter 2. Methodology**

Performance issues can arise from software, hardware, and any component along the data path. Methodologies help us approach complex systems by showing where to start and what steps to take to locate and analyze performance issues. [p15]

### Terminology

The following are key terms for systems performance. Later chapters provide additional terms and describe some of these in different contexts.

* **IOPS**: Input/output operations per second is a measure of the rate of data transfer operations.
    * For disk I/O, IOPS refers to reads and writes per second.
* [**Throughput**](https://en.wikipedia.org/wiki/Throughput): the rate of work performed. Especially in communications, the term is used to refer to the [data rate](https://en.wikipedia.org/wiki/Data_rate_units) (bytes per second or bits per second).
    * In some contexts (e.g., databases), throughput can refer to the operation rate (operations per second or transactions per second).
* **Response time**: the time for an operation to complete. This includes any time spent waiting and time spent being serviced (service time), including the time to transfer the result.
* **Latency**: Latency is a measure of time an operation spends waiting to be serviced.
    * In some contexts, it can refer to the entire time for an operation, equivalent to response time ([Section 2.3](#Concepts)).
* **Utilization**:
    * For resources that service requests, utilization is a measure of how busy a resource is, based on how much time in a given interval it was actively performing work.
    * For resources that provide storage, utilization may refer to the capacity that is consumed (e.g., memory utilization).
* **Saturation**: the degree to which a resource has queued work it cannot service.
* **Bottleneck**: In system performance, a bottleneck is a resource that limits the performance of the system. Identifying and removing systemic bottlenecks is a key activity of systems performance.
* **Workload**: The input to the system or the load applied is the workload. For a database, the workload consists of the database queries and commands sent by the clients.
* **Cache**: a fast storage area that can duplicate or buffer a limited amount of data, to avoid communicating directly with a slower tier of storage, thereby improving performance. For economic reasons, a cache is smaller than the slower tier.

### Models

#### System under Test

The performance of a [system under test](https://en.wikipedia.org/wiki/System_under_test) (SUT) is shown below:

[![Figure 2.1 System under test](figure_2.1.png)](figure_2.1.png "Figure 2.1 System under test")

**Perturbations** (interference) can affect results, including those caused by:

* Scheduled system activity,
* Other users of the system,
* Oher workloads.

The origin of the perturbations may not be clear and determining it can be particularly difficult in some cloud environments, where other activity (by guest tenants) on the physical host system is not observable from within a guest SUT.

Another difficulty is that modern environments may be composed of several networked components needed to service the input workload, including load balancers, web servers, database servers, application servers, and storage systems. The mere act of mapping the environment may help to reveal previously overlooked sources of perturbations. The environment may also be modeled as a network of queueing systems, for analytical study.

#### Queueing System

Some components and resources can be modeled as a queueing system. The following figure shows a simple queueing system.

[![Figure 2.2 Simple queueing model](figure_2.2.png)](figure_2.2.png "Figure 2.2 Simple queueing model")

### Concepts

#### Latency

The **latency** is the time spent waiting before an operation is performed.  The following figure, as an example of latency, shows a network transfer (e.g. HTTP GET request):

[![Figure 2.3 Network connection latency](figure_2.3.png)](figure_2.3.png "Figure 2.3 Network connection latency")

In this example, the operation is a network service request to transfer data. Before this operation can take place, the system must wait for a network connection to be established, which is latency for this operation. The response time spans this latency and the operation time.

Depending on the target, the latency can be measured differently. For example, the load time for a website may be composed of three different times:

* DNS latency, which refers to the entire DNS operation.
* TCP connection latency, which refers to the initialization only (TCP handshake).
* TCP data transfer time.

At a higher level, the response time may be termed latency. [p19]

Time orders of magnitude and their abbreviations are listed in the following table:

Unit | Abbreviation | Fraction of 1 s
---- | ------------ | ---------------
Minute | m | 60
Second | s | 1
Millisecond | ms | 0.001 or 1/1000 or 1 x 10<sup>-3</sup>
Microsecond | μs | 0.000001 or 1/1000000 or 1 x 10<sup>-6</sup>
Nanosecond | ns | 0.000000001 or 1/1000000000 or 1 x 10<sup>-9</sup>
Picosecond | ps | 0.000000000001 or 1/1000000000000 or 1 x 10<sup>-12</sup>

When possible, other metric types can be converted to latency or time so that they can be compared. For example:

* Choosing the better performance between 100 network I/O or 50 disk I/O be a complicated choice, involving many factors: network hops, rate of network drops and retransmits, I/O size, random or sequential I/O, disk types, etc..
* Comparing 100 ms of total network I/O and 50 ms of total disk I/O is easier.

#### Time Scales

System components operate over vastly different time scales (orders of magnitude).

The following table is an example Time Scale of System Latencies (3.3 GHz processor):

Event | Latency | Scaled
----- | ------- | ------
1 CPU cycle | 0.3 ns | 1 s
Level 1 cache access | 0.9 ns | 3 s
Level 2 cache access | 2.8 ns | 9 s
Level 3 cache access | 12.9 ns | 43 s
Main memory access (DRAM, from CPU) | 120 ns | 6 min
Solid-state disk I/O (flash memory) | 50–150 μs | 2–6 days
Rotational disk I/O | 1–10 ms | 1–12 months
Internet: San Francisco to New York | 40 ms | 4 years
Internet: San Francisco to United Kingdom | 81 ms | 8 years
Internet: San Francisco to Australia | 183 ms | 19 years
TCP packet retransmit | 1–3 s | 105–317 years
OS virtualization system reboot | 4 s | 423 years
SCSI command time-out | 30 s | 3 millennia
Hardware (HW) virtualization system reboot | 40 s | 4 millennia
Physical system reboot | 5 m | 32 millennia

#### Trade-offs

Be aware of some common performance trade-offs. The figure below shows the good/fast/cheap "pick two" trade-off on the left alongside the terminology adjusted for IT projects on the right.

[![Figure 2.4 Trade-offs: pick two](figure_2.4.png)](figure_2.4.png "Figure 2.4 Trade-offs: pick two")

A common trade-off in performance tuning is that between CPU and memory:

* Memory can be used to cache results, reducing CPU usage.
* CPU may be spent to compress data to reduce memory usage. (On modern systems with an abundance of CPU)

[p21]

Tunable parameters often come with trade-offs. For examples:

* **File system record size** (or block size):
    * Small record sizes, close to the application I/O size, will perform better for random I/O workloads and make more efficient use of the file system cache while the application is running.
    * Large record sizes will improve streaming workloads, including file system backups.
* **Network buffer size**:
    * Small buffer sizes will reduce the memory overhead per connection, helping the system scale.
    * Large sizes will improve network throughput.

#### Tuning Efforts

<u>Performance tuning is most effective when done closest to where the work is performed (e.g. within application itself)).</u> The following table shows an example of software stack, with tuning possibilities.

Layer | Tuning Targets
----- | --------------
Application | database queries performed
Database | database table layout, indexes, buffering
System calls | memory-mapped or read/write, sync or async I/O flags
File system | record size, cache size, file system tunables
Storage | RAID level, number and type of disks, storage tunables

##### **Application Level** *

Tuning at the application level may improve performance significantly due to the following reasons:

1. It may be possible to eliminate or reduce database queries and improve performance by a large factor (e.g., 20x).
    * Tuning down to the storage device level may eliminate or improve storage I/O, but tuning efforts have already been made executing higher-level OS stack code, so this may improve resulting application performance by only percentages (e.g., 20%).
2. Since many of today’s environments target rapid deployment for features and functionality, application development and testing tend to focus on correctness, leaving little or no time for performance measurement or optimization before production deployment. These activities are conducted later, when performance becomes a problem.

The application isn’t necessarily the most effective level from which to base observation. Slow queries may be best understood from their time spent on-CPU, or from the file system and disk I/O that they perform. These are observable from operating system tools.

In many environments (especially cloud computing), the application level is under constant development, pushing software changes into production weekly or daily. Large performance improvment (including fixes for regressions) are frequently found as the application code changes. In these environments, tuning for the operating system and observability from the operating system can be easy to overlook. Remember that operating system performance analysis can also identify application-level issues, not just OS-level issues, in some cases more easily than from the application alone.

#### Level of Appropriateness

Different organizations and environments have different requirements for performance [p22]. This doesn’t necessarily mean that some organizations are doing it right and some wrong. It depends on the [return on investment](https://en.wikipedia.org/wiki/Return_on_investment) (ROI) for performance expertise:

* Organizations with large data centers or cloud environments may need a team of performance engineers who analyze everything, including kernel internals and CPU performance counters, and frequently use dynamic tracing. They may also formally model performance and develop accurate predictions for future growth.
* Small start-ups may have time only for superficial checks, trusting third-party monitoring solutions to check their performance and provide alerts.

#### Point-in-Time Recommendations

The performance characteristics of environments change over time, due to the addition of more users, newer hardware, and updated software or firmware.

[p23]

Performance recommendations, especially the values of tunable parameters, are valid only at a specific *point in time*. What may have been the best advice from a performance expert one week may become invalid a week later after a software or hardware upgrade, or after adding more users.

#### Load versus Architecture

An application can perform badly due to an issue with the software configuration and hardware on which it is running: its architecture. However, an application can also perform badly simply due to too much load applied, resulting in queueing and long latencies. Load and architecture are pictured in the figure below:

[![Figure 2.5 Load versus architecture](figure_2.5.png)](figure_2.5.png "Figure 2.5 Load versus architecture")

If analysis of the architecture shows queueing of work but no problems with how the work is performed, the issue may be one of too much load applied. In a cloud computing environment, this is the point where more nodes can be introduced to handle the work.

##### **Single-threaded and multithreaded application** *

For example,

* An **issue of architecture** may be a single-threaded application that is busy on-CPU, with requests queueing while other CPUs are available and idle. In this case, performance is limited by the application’s single-threaded architecture.
* An **issue of load** may be a multithreaded application that is busy on all available CPUs, with requests still queueing. In this case, performance is limited by the available CPU capacity, or put differently, by more load than the CPUs can handle.

#### Scalability

The performance of the system under increasing load is its **scalability**. The following figure shows a typical throughput profile as a system’s load increases:

[![Figure 2.6 Throughput versus load](figure_2.6.png)](figure_2.6.png "Figure 2.6 Throughput versus load")

For some period, linear scalability is observed. A point is then reached, marked with a dotted line, where contention for a resource begins to affect performance. This point can be described as a *knee point*, as it is the boundary between two pro files. Beyond this point, the throughput profile departs from linear scalability, as contention for the resource increases. Eventually the overheads for increased contention and coherency cause less work to be completed and throughput to decrease.

This point may occur when a component reaches 100% utilization: the *saturation point*. It may also occur when a component approaches 100% utilization, and queueing begins to be frequent and significant. This point may occur when a component reaches 100% utilization: the saturation
point. It may also occur when a component approaches 100% utilization, and
queueing begins to be frequent and significant.

An example system that may exhibit this profile is an application that performs heavy compute, with more load added as threads. As the CPUs approach 100% utilization, performance begins to degrade as CPU scheduler latency increases. After peak performance, at 100% utilization, throughput begins to decrease as more threads are added, causing more context switches, which consume CPU resources and cause less actual work to be completed.

The same curve can be seen if you replace "load" on the *x* axis with a resource such as CPU cores (detailed in [Modeling](#modeling))

The degradation of performance for nonlinear scalability, in terms of average response time or latency, is graphed in the following figure:

[![Figure 2.7 Performance degradation](figure_2.7.png)](figure_2.7.png "Figure 2.7 Performance degradation")

* The "fast" degradation profile may occur for memory load, when the system begins to page (or swap) to supplement main memory.
* The "slow" degradation profile may occur for CPU load.
* Another "fast" profile example is disk I/O. As load (and the resulting disk utilization) increases, I/O becomes more likely to queue behind other I/O. An idle rotational disk may serve I/O with a response time of about 1 ms, but when load increases, this can approach 10 ms.

<u>Linear scalability of response time could occur if the application begins to return errors when resources are unavailable, instead of queueing work. For example, a web server may return 503 "Service Unavailable" instead of adding requests to a queue, so that those requests that are served can be performed with a consistent response time.</u>

#### Known-Unknowns

The following notions are important:

* **Known-knowns**: These are things you know. You know you should be checking a performance metric, and you know its current value. For example, you know you should be checking CPU utilization, and you also know that the value is 10% on average.
* **Known-unknowns**: These are things you know that you do not know. You know you can check a metric or the existence of a subsystem, but you haven’t yet observed it. For example, you know you could be checking what is making the CPUs busy by the use of profiling but have yet to do so.
* **Unknown-unknowns**: These are things you do not know you do not know.  For example, you may not know that device interrupts can become heavy CPU consumers, so you are not checking them.

Performance is a field where "the more you know, the more you don’t know". It’s the same principle: the more you learn about systems, the more unknownunknowns you become aware of, which are then known-unknowns that you can check on.

#### Metrics

Performance metrics are statistics generated by the system, applications, or additional tools that measure activity of interest. They are studied for performance analysis and monitoring, either numerically at the command line or graphically using visualizations.

Common types of systems performance metrics include:

* **IOPS**: I/O operations per second
* **Throughput**: either operations or volume per second, depending on its context:
    * Database throughput is usually a measure of queries or requests (operations) per second.
    * Network throughput is a measure of bits or bytes (volume) per second.
* **Utilization**
* **Latency**

##### **Overhead**

Since CPU cycles must be spent to gather and store the metrics. This causes overhead, which can negatively affect the performance of the target of measurement. This is called the [**observer effect**](https://en.wikipedia.org/wiki/Observer_effect_(information_technology)).

##### **Issues**

The temptation is to assume that the software vendor has provided metrics that are well chosen, are bug-free, and provide complete visibility. In reality, metrics can be confusing, complicated, unreliable, inaccurate, and even plain wrong (due to bugs). Sometimes a metric was correct on one software version but did not get updated to reflect the addition of new code and code paths.

#### Utilization

The term *utilization* is often used for operating systems to describe device usage, such as for the CPU and disk devices. Utilization can be time-based or capacitybased.

##### **Time-Based**

Time-based utilization is the average amount of time the server or resource was busy, as defined in [queueing theory](https://en.wikipedia.org/wiki/Queueing_theory), along with the ratio:

> *U* = *B*/*T*

where:

* *U* = utilization
* *B* = total time the system was busy during *T*, the observation period

The "utilization" is also available from operating system performance tools. The disk monitoring tool [`iostat(1)`](http://man7.org/linux/man-pages/man1/iostat.1.html) calls this metric *%b* for percent busy, a term that better conveys the underlying metric: *B*/*T*.

This utilization metric means how busy a component is: when a component approaches 100% utilization, performance can seriously degrade when there is contention for the resource. Other metrics can be checked to confirm and to see if the component has therefore become a system bottleneck.

Some components can service multiple operations in parallel. Performance may not degrade much at 100% utilization, as they can accept more work. [p28]

* A disk that is 100% busy may also be able to accept and process more work, for example, by buffering writes in the on-disk cache to be completed later.
* Storage arrays frequently run at 100% utilization because some disk is busy 100% of the time, but the array has plenty of idle disks and can accept much more work.

##### **Capacity-Based**

The other definition of utilization in the context of capacity planning is:

> A system or component (such as a disk drive) is able to deliver a certain amount of throughput. At any level of performance, the system or component is working at some proportion of its capacity. That proportion is called the utilization.

This defines utilization in terms of capacity instead of time. It implies that a disk at 100% utilization cannot accept any more work. With the time-based definition, 100% utilization only means it is busy 100% of the time. Therefore, <u>100% busy does not mean 100% capacity.</u>

##### **Time-Based vs. Capacity-Based** *

Use elevator as an example:

* Time-Based Utilization: the elevator may be considered utilized when it is moving between floors, and not utilized when it is idle waiting. However, the elevator may be able to accept more passengers even when it is busy 100% of the time responding to calls.
* Capacity-Based Utilization: 100% capacity may mean the elevator is at its maximum payload capacity and cannot accept more passengers.

In an ideal world, we would be able to measure both types of utilization for a device, which usually isn't possible. [p29]

<u>In this book, *utilization* usually refers to the time-based version.</u> The capacity version is used for some volume-based metrics, such as memory usage.

##### **Non-Idle Time**

**Non-idle time** is a more accurate term to define utilization, but not yet in common usage. [p29]

#### Saturation

**Saturation** is the degree to which more work is requested of a resource than it can process. Saturation begins to occur at 100% utilization (capacity-based), as extra work cannot be processed and begins to queue. This is pictured in the following figure:

[![Figure 2.8 Utilization versus saturation](figure_2.8.png)](figure_2.8.png "Figure 2.8 Utilization versus saturation")

Any degree of saturation is a performance issue, as time is spent waiting (latency). For time-based utilization (percent busy), saturation may not begin at the 100% utilization mark, depending on the degree to which the resource can operate on work in parallel. [p30]

#### Profiling

**Profiling** is typically performed by [sampling](https://en.wikipedia.org/wiki/Sampling_(statistics)) the state of the system at timed intervals, and then studying the set of samples.

Unlike the previous metrics covered, including IOPS and throughput, the use of sampling provides a *coarse* view of the target’s activity, depending on the rate of sampling.

For example, CPU usage can be understood in reasonable detail by sampling the CPU program counter or stack backtrace at frequent intervals to gather statistics on the code paths that are consuming CPU resources, which is detailed in [Chapter 6](ch6.md).

#### Caching

Frequently used to improve performance, a cache stores results from a slower storage tier in a faster storage tier for reference. An example is caching disk blocks in main memory (RAM).

* Multiple tiers of caches may be used. CPUs commonly employ multiple hardware caches for main memory (Levels 1, 2, and 3), beginning with a very fast but small cache (Level 1) and increasing in both storage size and access latency. This is an economic trade-off between density and latency:level; and sizes are chosen for the best performance for the on-chip space available.
* There are many other caches present in a system, many of them implemented in software using main memory for storage.

Caching is detailed in [Section 3.2.11](ch3.md#caching).

##### **Cache metrics** *

**Hit ratio** is a metric of cache performance. It represents the number of times the needed data was found in the cache (hits) versus the number of times it was not (misses). The higher, the better, as a higher ratio reflects more data successfully accessed from faster media. The following figure shows the expected performance improvement for increasing cache hit ratios.

[![Figure 2.9 Cache hit ratio and performance](figure_2.9.png)](figure_2.9.png "Figure 2.9 Cache hit ratio and performance")

This is a nonlinear profile because of the difference in speed between cache hits and misses (the two storage tiers). The performance difference between 98% and 99% is much greater than that between 10% and 11%. The greater the difference, the steeper the slope becomes.

**Miss rate** is another metric, in terms of misses per second. This is proportional (linear) to the performance penalty of each miss.

The total runtime for each workload can be calculated as:

> runtime = (hit rate x hit latency) + (miss rate x miss latency)

This calculation uses the average hit and miss latencies and assumes the work is serialized.

##### **Algorithms**

Cache management algorithms and policies determine what to store in the limited space available for a cache:

* **Most recently used** (MRU) refers to a cache **retention policy**, which decides what to favor keeping in the cache: the objects that have been used most recently.
* **Least recently used** (LRU) can refer to an equivalent cache **eviction policy**, deciding what objects to remove from the cache when more space is needed.
* **Most frequently used** (MFU)
* **Least frequently used** (LFU)
* **Not frequently used** (NFU): an inexpensive but less thorough version of LRU.

##### **Hot, Cold, and Warm Caches**

The following words describe the state of the cache:

* Cold: A **cold cache** is empty, or populated with unwanted data. The hit ratio for a cold cache is zero (or near zero as it begins to warm up).
* Hot: A **hot cache** is populated with commonly requested data and has a high hit ratio, for example, over 99%.
* Warm: A **warm cache** is one that is populated with useful data but doesn’t have a high enough hit ratio to be considered hot.
* Warmth: Cache warmth describes how hot or cold a cache is. An activity that improves cache warmth is one that aims to improve the cache hit ratio.

When caches are first initialized, they begin cold and then warm up over time.  When the cache is large or the next-level storage is slow (or both), the cache can take a long time to become populated and warm.

[p32]

### Perspectives

There are two common perspectives for performance analysis: **workload analysis** and **resource analysis**, which can be thought of as either top-down or bottom-up analysis of the operating system software stack, as show in the figure below:

[![Figure 2.10 Analysis perspectives](figure_2.10.png)](figure_2.10.png "Figure 2.10 Analysis perspectives")

#### Resource Analysis

Resource analysis begins with analysis of the system resources: CPUs, memory, disks, network interfaces, busses, and interconnects. It is most likely performed by system administrators, who are responsible for the physical environment resources.

##### **Activities** *

* **Performance issue investigations:** to see if a particular type of resource is responsible
* **Capacity planning**: for information to help size new systems, and to see when existing system resources may become exhausted

##### **Metrics with utilization as a focus** *

Resource analysis focuses on utilization to identify when resources are at or approaching their limit.

* Some resource types, such as CPUs, have utilization metrics readily available.
* Utilization for other resources can be estimated based on available metrics, for example, estimating network interface utilization by comparing the send and receive megabits per second (throughput) with the known maximum bandwidth.

[Metrics](#metrics) best suited for resource analysis include:

* IOPS
* Throughput
* [Utilization](#utilization)
* [Saturation](#saturation)

These metrics measure the following:

* What the resource is being asked to do
* How utilized or saturated
it is for a given load. Ot

Other types of metrics, including latency, are also of use to see how well the resource is responding for the given workload.

##### **Documentation on "stat" tools** *

Resource analysis is a common approach to performance analysis, in part because of the widely available documentation on the topic. Such documentation focuses on the operating system "stat" tools: [`vmstat(1)`](http://man7.org/linux/man-pages/man8/vmstat.8.html), [`iostat(1)`](http://man7.org/linux/man-pages/man1/iostat.1.html), [`mpstat(1)`](http://man7.org/linux/man-pages/man1/mpstat.1.html). Resource analysis is a perspective, but not the only perspective.

#### Workload Analysis

### Methodology

### Modeling

### Capacity Planning

### Statistics

### Monitoring

### Visualizations

### Doubts and Solutions

#### Verbatim

p17 on System under Test:

> The mere act of mapping the environment may help to reveal previously overlooked sources of perturbations. The environment may also be modeled as a network of queueing systems, for analytical study.

WTF?

p21 on Trade-offs:

> File system record size and network buffer size: small vs large

Further reading may be required to understand these trade-offs.
