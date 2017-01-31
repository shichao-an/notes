### **Chapter 1. Reliable, Scalable and Maintainable Applications**

Many applications today are **data-intensive**, as opposed to **compute-intensive**. Raw CPU power is rarely a limiting factor for these applications. Bigger problems are usually the amount of data, the complexity of data, and the speed at which it is changing.

A data-intensive application is typically built from standard building blocks which provide common functionality, such as:

* Store data so that they can be found later (*databases*)
* Remember the result of an expensive operation, to speed up reads (*caches*)
* Allow users to search data by keyword or filter it in various ways (*search indexes*)
* Send a message to another process, to be handled asynchronously (*stream processing*)
* Periodically crunch a large amount of accumulated data (*batch processing*)

When building an application, most engineers wouldn't write a new data storage engine from scratch, because databases are a perfectly good tool for the job. However, there are many database systems with different characteristics, because different applications have different requirements. When building an application, we still need to figure out which tools and which approaches are the most appropriate for the task at hand. Sometimes it can be hard to combine several tools when you need to do something that a single tool cannot do alone.

This chapter starts by exploring the fundamentals of what we are trying to achieve: reliable, scalable and maintainable data systems and then clarify what those things mean, outline some ways of thinking about them, and go over the basics need for later chapters.

### Thinking About Data Systems

Typically, databases, queues, caches, etc. are very different categories of tools. Although a database and a message queue have some superficial similarity (both store data for some time), they have very different access patterns, which means different performance characteristics, and thus very different implementations.

Why do we label them under an umbrella term like *data systems*?

First, many new tools for data storage and processing have emerged in recent years, which are optimized for a variety of different use cases, and they no longer fit into traditional categories. For example, there are data stores that are also used as message queues (Redis), and there are message queues with database-like durability guarantees (Kafka). The boundaries between the categories are becoming blurred.

Second, increasingly many applications now have such demanding or wide-ranging requirements that a single tool can no longer meet all of its data processing and storage needs. Instead, the work is broken down into tasks that can be performed efficiently on a single tool, and those different tools are stitched together using application code.

For example, if you have an application-managed caching layer (using memcached or similar), or a full-text search server separate from your main database (such as Elasticsearch or Solr), it is normally the application code's responsibility to keep those caches and indexes in sync with the main database. The following figure is one possible architecture (which will be detailed in later chapters):

[![Figure 1-1. One possible architecture for a data system that combines several components.](figure_1-1_600.png)](figure_1-1.png "Figure 1-1. One possible architecture for a data system that combines several components.")

When you combine several tools in order to provide a service, the service's interface or API usually hides those implementation details from clients. You have essentially created a new, special-purpose data system from smaller, general-purpose components. Your composite data system may provide certain guarantees, e.g. that the cache will be correctly invalidated or updated on writes, so that outside clients see consistent results.

If you are designing a data system or service, a lot of tricky questions arise:

* How do you ensure that the data remains correct and complete, even when things go wrong internally?
* How do you provide consistently good performance to clients, even when parts of your system are degraded?
* How do you scale to handle an increase in load?
* What does a good API for the service look like?

There are many factors that may influence the design of a data system, including:

* Skills and experience of the people involved
* Legacy system dependencies
* Time‐scale for delivery
* Organization's tolerance of different kinds of risk
* Regulatory constraints

This book focuses on three concerns that are important in most software systems:

* **Reliability**. The system should continue to work correctly (performing the correct function at the desired performance) even in the face of adversity (hardware or software faults, and even human error). See [Reliability](#reliability).
* **Scalability**. As the system grows (in data volume, traffic volume or complexity), there should be reasonable ways of dealing with that growth. See [Scalability](#scalability).
* **Maintainability**. Over time, many different people will work on the system (engineering and operations, both maintaining current behavior and adapting the system to new use cases), and they should all be able to work on it productively. See [Maintainability](#maintainability).

### Reliability

Typical expectations for software include:

* The application performs the function that the user expected.
* It can tolerate the user making mistakes, or using the software in unexpected ways.
* Its performance is good enough for the required use case, under expected load and data volume.
* The system prevents any unauthorized access and abuse.

If all those things together mean "working correctly", then *reliability* roughly means "continuing to work correctly, even when things go wrong".

The things that can go wrong are called *faults*, and systems that anticipate faults and can cope with them are called [*fault-tolerant*](https://en.wikipedia.org/wiki/Fault_tolerance) or *resilient*. The term is slightly misleading: it suggests that we could make a system tolerant of every possible kind of fault, which in reality is not feasible. It only makes sense to talk about tolerating certain *types of fault*.

Note that a *fault* is not the same as a *failure*.

* A fault is usually defined as one component of the system deviating from its spec.
* A failure is when the system as a whole stops providing the required service to the user.

It is impossible to reduce the probability of a fault to zero; therefore it is usually best to design fault tolerance mechanisms that prevent faults from causing failures. This book covers several techniques for building reliable systems from unreliable parts.

Counter-intuitively, in such fault-tolerant systems, it can make sense to increase the rate of faults by triggering them deliberately (for example, by randomly killing individual processes without warning). Many critical bugs are actually due to poor error handling; by deliberately inducing faults, you ensure that the fault-tolerance machinery is continually exercised and tested, which can increase your confidence that faults will be handled correctly when they occur naturally. The Netflix [chaos monkey](https://github.com/Netflix/chaosmonkey) is an example of this approach.

Although we generally prefer tolerating faults over preventing faults, there are cases where prevention is better than cure (e.g. because no cure exists). This is the case with security matters, for example: if an attacker has compromised a system and gained access to sensitive data, that event cannot be undone. However, this book mostly deals with the kinds of fault that can be cured, as described in the following sections.

#### Hardware faults

Hardware faults are a common cause of system failure. For example:

* Hard disks crash
* RAM becomes faulty
* The power grid has a blackout
* Someone unplugs the wrong network cable

These things happen *all the time* when you have a lot of machines.

Hard disks are reported as having a [mean time to failure](https://en.wikipedia.org/wiki/Mean_time_between_failures) (MTTF) of about 10 to 50 years. Thus, on a storage cluster with 10,000 disks, we should expect on average one disk to die per day.

Adding redundancy to the individual hardware components can reduce the failure rate of the system. For example:

* Disks may be set up in a RAID configuration.
* Servers may have dual power supplies and hot-swappable CPUs.
* Data centers may have batteries and diesel generators for backup power.

When one component dies, the redundant component can take its place while the broken component is replaced. This approach cannot completely prevent hardware problems from causing failures, but it is well understood, and can often keep a machine running uninterrupted for years.

Redundancy of hardware components was sufficient for most applications, since it makes total failure of a single machine fairly rare. As long as you can restore a backup onto a new machine fairly quickly, the downtime in case of failure is not catastrophic in most applications. Thus, multi-machine redundancy was only required by a small number of applications for which high availability was absolutely essential.

However, as data volumes and computing demands increase, more applications are using larger numbers of machines, which proportionally increases the rate of hardware faults. Moreover, in some "cloud" platforms such as Amazon Web Services it is fairly common for virtual machine instances to become unavailable without warning, as the platform is designed to prioritize flexibility and [elasticity](https://en.wikipedia.org/wiki/Elasticity_(cloud_computing)) over single-machine reliability.

Hence there is a move towards systems that can tolerate the loss of entire machines, by using [software fault-tolerance](https://en.wikipedia.org/wiki/Software_fault_tolerance) techniques in preference to hardware redundancy. Such systems also have operational advantages: a single-server system requires planned downtime if you need to reboot the machine (to apply operating system security patches, for example), whereas a system that can tolerate machine failure can be patched one node at a time, without downtime of the entire system.
