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

#### Software errors

Hardware faults are usually considered as being random and independent from each other: one machine's disk failing does not imply that another machine's disk is going to fail. There may be weak correlations (for example due to a common cause, such as the temperature in the server rack), but otherwise it is unlikely that a large number of hardware components will fail at the same time.

Another class of fault is a systematic error within the system, which are harder to anticipate. Because they are correlated across nodes, they tend to cause many more system failures than uncorrelated hardware faults. Examples include:

* A software bug that causes every instance of an application server to crash when given a particular bad input. For example, consider the [leap second](https://en.wikipedia.org/wiki/Leap_second) on [June 30, 2012](https://en.wikipedia.org/wiki/Leap_second#Examples_of_problems_associated_with_the_leap_second) that caused many applications to hang simultaneously, due to a bug in the Linux kernel.
* A runaway process uses up some shared resource: CPU time, memory, disk space or network bandwidth.
* A service that the system depends on slows down, becomes unresponsive or starts returning corrupted responses.
* [Cascading failures](https://en.wikipedia.org/wiki/Cascading_failure), where a small fault in one component triggers a fault in another component, which in turn triggers further faults.

The bugs that cause these kinds of software fault often lie dormant for a long time until they are triggered by an unusual set of circumstances. In those circumstances, it is revealed that the software is making some kind of assumption about its environment, and while that assumption is usually true, it eventually stops being true for some reason.

There is no quick solution to systematic faults in software, but many small things can help:

* Carefully thinking about assumptions and interactions in the system
* Thorough testing
* Process isolation
* Allowing processes to crash and restart
* Measuring, monitoring and analyzing system behavior in production

If a system is expected to provide some guarantee (for example, in a message queue the number of incoming messages equals the number of outgoing messages), it can constantly check itself while it is running, and raise an alert if a discrepancy is found.

#### Human errors

Humans design and build software systems, and the operators who keep the system running are also human. Even when they have the best intentions, humans are known to be unreliable. A study of large Internet services found that configuration errors by operators were the leading cause of outages, whereas hardware faults (servers or network) cause only 10–25% of outages.

The best systems combine several approaches in spite of unreliable humans:

* Design systems that minimizes opportunities for error. For example, well-designed abstractions, APIs and admin interfaces make it easy to do "the right thing", and discourage "the wrong thing". However, if the interfaces are too restrictive, people will work around them, negating their benefit, so this is a tricky balance to get right.
* Decouple the places where people make the most mistakes from the places where they can cause failures. In particular, provide fully-featured non-production sandbox environments where people can explore and experiment safely, using real data, without affecting real users.
* Test thoroughly at all levels, from unit tests to whole-system integration tests and manual tests. Automated testing is widely used and valuable for covering corner cases that rarely arise in normal operation.
* Allow quick and easy recovery from human errors, to minimize the impact in the case of a failure. For example:
    * Make it fast to roll back configuration changes.
    * Roll out new code gradually (so that any unexpected bugs affect only a small subset of users).
    * Provide tools to recompute data (in case it turns out that the old computation was incorrect).
* Set up detailed and clear monitoring, such as performance metrics and error rates. In other engineering disciplines this is referred to as [*telemetry*](https://en.wikipedia.org/wiki/Telemetry) (for example, once a rocket has left the ground, telemetry is essential for tracking what is happening and for understanding failures). Monitoring can show us early warning signals, and allow us to check whether any assumptions or constraints are being violated. When a problem occurs, metrics can be invaluable in diagnosing the issue.
* Good management practices and training.

#### How important is reliability?

Bugs in business applications cause lost productivity (and legal risks if figures are reported incor‐ rectly), and outages of e-commerce sites can have huge costs in terms of lost revenue and reputation. Even in "non-critical" applications we have a responsibility to our users.

There are situations in which we may choose to sacrifice reliability in order to reduce development cost (e.g. when developing a prototype product for an unproven market) or operational cost (e.g. for a service with a very narrow profit margin), but we should be very conscious of when we are cutting corners.

### Scalability

That a system is working reliably today doesn't mean it will necessarily work
reliably in future. One common reason for degradation is increased load:

* Perhaps it has grown from 10,000 concurrent users to 100,000 concurrent users.
* Perhaps it is processing much larger volumes of data than it did before.

Scalability is the term to describe a system's ability to cope with increased load. It is not a one-dimensional label that we can attach to a system: it is meaningless to say "X is scalable" or "Y doesn't scale". Rather, discussing scalability means to discuss the question: if the system grows in a particular way, what are our options for coping with the growth? How can we add computing resources to handle the additional load?

#### Describing load

Load can be described with a few numbers which we call *load parameters*. The best choice of parameters depends on the architecture of your system. For example, it can be:

* Requests per second to a webserver
* Ratio of reads to writes in a database
* The number of simultaneously active users in a chat room
* The hit rate on a cache

Perhaps the average case is what matters for you, or perhaps your bottleneck is dominated by a small number of extreme cases.

Consider Twitter as an example, using data published in November 2012. Two of Twitter's main operations are:

* *Post tweet*. A user can publish a new message to their followers (4.6 k requests/sec on average, over 12 k requests/sec at peak).
* *Home timeline*. A user can view tweets recently published by the people they follow (300 k requests/sec).

Simply handling 12,000 writes per second (the peak rate for posting tweets) would be fairly easy. However, Twitter's scaling challenge is not primarily due to tweet volume, but due to [fan-out](https://en.wikipedia.org/wiki/Fan-out_(software)) (In transaction processing systems, we use it to describe the number of requests to other services that we need to make in order to serve one incoming request): each user follows many people, and each user is followed by many people.

There are broadly two approaches to implementing these two operations:

Approach 1: posting a tweet inserts the new tweet into a global collection of tweets. When a user requests home timeline:

1. Look up all the people they follow.
2. Find all recent tweets for each of those users
3. Merge them (sorted by time).

In a relational database like the one in the following figure:

[![Figure 1-2. Simple relational schema for implementing a Twitter home timeline.](figure_1-2_600.png)](figure_1-2.png "Figure 1-2. Simple relational schema for implementing a Twitter home timeline.")

The SQL query of it would be like:

```sql
SELECT tweets.*, users.* FROM tweets
 JOIN users ON tweets.sender_id = users.id
 JOIN follows ON follows.followee_id = users.id
 WHERE follows.follower_id = current_user
```

Approach 2: maintain a cache for each user's home timeline (see figure below). When a user posts a tweet, look up all the people who follow that user, and insert the new tweet into each of their home timeline caches. The request to read the home timeline is cheap, because its result has been computed ahead of time.

[![Figure 1-3. Twitter's data pipeline for delivering tweets to followers, with load parameters as of November 2012](figure_1-3_600.png)](figure_1-3.png "Figure 1-3. Twitter's data pipeline for delivering tweets to followers, with load parameters as of November 2012")

The first version of Twitter used approach 1, but the systems struggled to keep up with the load of home timeline queries, so the company switched to approach 2. This works better because the average rate of published tweets is almost two orders of magnitude lower than the rate of home timeline reads, so it's preferable to do more work at write time and less at read time.

However, the downside of approach 2 is that posting a tweet now requires a lot of extra work. A tweet is delivered to about 75 followers on average, so 4.6 k tweets per second become 345 k writes per second to the home timeline caches. However, the number of followers per user varies wildly, and some users have over 30 million followers. This means that a single tweet may result in over 30 million writes to home timelines. It is a significant challenge to deliver tweets to followers in a timely manner.

In Twitter, the distribution of followers per user (maybe weighted by how often those users tweet) is a key load parameter for discussing scalability, since it determines the fan-out load. Now that approach 2 is robustly implemented, Twitter is moving to a hybrid of both approaches. Most users' tweets continue to be fanned out to home timelines at the time when they are posted, but a small number of users with a very large number of followers are excepted from this fan-out. Instead, when the home timeline is read, the tweets from celebrities followed by the user are fetched separately and merged with the home timeline when the timeline is read, like in approach 1. This hybrid approach is able to deliver consistently good performance.
