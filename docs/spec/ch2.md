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

#### Tuning Efforts

#### Level of Appropriateness

#### Point-in-Time Recommendations

#### Load versus Architecture

#### Scalability

#### Known-Unknowns

#### Metrics

#### Utilization

#### Saturation

#### Profiling

#### Caching

### Doubts and Solutions

#### Verbatim

p17 on System under Test:

> The mere act of mapping the environment may help to reveal previously overlooked sources of perturbations. The environment may also be modeled as a network of queueing systems, for analytical study.

WTF?
