### **Chapter 1. A new paradigm for Big Data**

[p1-2]

Traditional systems, and the data management techniques associated with them, have failed to scale to Big Data.

To tackle the challenges of Big Data, a lof of new technologies has emerged, many of which have been grouped under the term *NoSQL*. In some ways, these new technologies are more complex than traditional databases, and in other ways they’re simpler. These systems can scale to vastly larger sets of data, but using these technologies effectively requires a fundamentally new set of techniques.  They aren’t one-size-fits-all solutions.

Many of these Big Data systems were pioneered by Google, including:

* Distributed filesystems,
* The  MapReduce computation framework,
* Distributed locking services.

Another notable pioneer in the space was Amazon, which created an innovative distributed key/value store called Dynamo. The open source community responded in the years following with Hadoop, HBase, MongoDB, Cassandra, RabbitMQ, and countless other projects.

This book is about complexity as much as it is about scalability. Some of the most basic ways people manage data in traditional systems like relational database management systems (RDBMSs) are too complex for Big Data systems.The simpler, alternative approach is the new paradigm for Big Data. This approach is dubbed the [**Lambda Architecture**](https://en.wikipedia.org/wiki/Lambda_architecture).

### How this book is structured

This book is a theory book, focusing on how to approach building a solution to any Big Data problem. It is structured into theory and illustration chapters.

### Scaling with a traditional database

The example in this section is a simple web analytics application, which tracks the number of pageviews for any URL a customer wishes to track. The customer’s web page pings the application’s web server with its URL every time a pageview is received. Additionally, the application should be able to tell you at any point what the top 100 URLs are by number of pageviews.

You start with a traditional relational schema for the pageviews similiar to the table below:

Column name | Type
----------- | ----
`id` | `integer`
`user_id` | `integer`
`url` | `varchar(255)`
`pageviews` | `bigint`

Your back end consists of an RDBMS with a table of that schema and a web server. Whenever someone loads a web page being tracked by your application, the web page pings your web server with the pageview, and your web server increments the corresponding row in the database.

The following subsections discuss what problems emerge as you evolve the application: you’ll run into problems with both scalability and complexity.

#### Scaling with a queue

As the traffic to your application is growing, you got a lot of "Timeout error on inserting to the database" error, sincet the database can’t keep up with the load, so write requests to increment pageviews are timing out.

Instead of having the web server hit the database directly, you insert a queue between the web server and the database. Whenever you receive a new pageview, that event is added to the queue. You then create a worker process that reads 100 events at a time off the queue, and batches them into a single database update. This is illustrated in the figure below:

[![Figure 1.2 Batching updates with queue and worker](figure_1.2.png)](figure_1.2.png "Figure 1.2 Batching updates with queue and worker")

This scheme resolves the timeout issues you were getting. If the database ever gets overloaded again, the queue will just get bigger instead of timing out to the web server and potentially losing data.

#### Scaling by sharding the database

As your application continues to get more and more popular, and again the database gets overloaded. Your worker can’t keep up with the writes; adding more workers to parallelize the updates doesn’t help; the database is clearly the bottleneck.

The approach is to use multiple database servers and spread the table across all the servers. Each server will have a subset of the data for the table. This is known as [**horizontal partitioning**](https://en.wikipedia.org/wiki/Partition_(database)) or [**sharding**](https://en.wikipedia.org/wiki/Shard_(database_architecture)). This technique spreads the write load across multiple machines.

The sharding technique you use is to choose the shard for each key by taking the hash of the key modded by the number of shards. Mapping keys to shards using a hash function causes the keys to be uniformly distributed across the shards. You do the following:

1. Write a script to map over all the rows in your single database instance, and split the data into four shards. Since it takes a while to run this script, you turn off the worker that increments pageviews to avoid losing increments during the transition.
2. Wrap a library around database-handling code that reads the number of shards from a configuration file, and redeploy all of your application code, since all application code needs to know how to find the shard for each key. You have to modify your top-100-URLs query to get the top 100 URLs from each shard and merge those together for the global top 100 URLs.

As the application gets more popular, you keep having to reshard the database into more shards to keep up with the write load:

* Each time gets more and more painful because there’s so much more work to coordinate. You can’t just run one script to do the resharding, as that would be too slow. You have to do all the resharding in parallel and manage many active worker scripts at once.
* If you forget to update the application code with the new number of shards, it causes many of the increments to be written to the wrong shards. So you have to write a one-off script to manually go through the data and move whatever was misplaced.

#### Fault-tolerance issues begin

With so many shards, it becomes a frequent occurrence for the disk on one of the database machines to go bad. That portion of the data is unavailable while that machine is down. You do a couple of things to address this:

* You update your queue/worker system to put increments for unavailable shards on a separate “pending” queue that you attempt to flush once every five minutes.
* You use the database’s replication capabilities to add a slave to each shard so you have a backup in case the master goes down. You don’t write to the slave, but at least customers can still view the stats in the application.

#### Corruption issues

You accidentally deploy a bug to production that increments the number of pageviews by two, instead of by one, for every URL and you don’t notice until 24 hours later, but by then the damage is done. Your weekly backups don’t help because there’s no way of knowing which data got corrupted.  After all this work trying to make your system scalable and tolerant of machine failures, your system has no resilience to a human making a mistake.

#### What went wrong?

As the application evolved, the system continued to get more and more complex: queues, shards, replicas, resharding scripts, etc. Developing applications on the data requires a lot more than just knowing the database schema; your code needs to know how to talk to the right shards, and if you make a mistake, there’s nothing preventing you from reading from or writing to the wrong shard.

 One problem is that your database is not self-aware of its distributed nature, so it can’t help you deal with shards, replication, and distributed queries. All that complexity got pushed to you both in operating the database and developing the application code.

However, the worst problem is that the system is not engineered for human mistakes.  As the system keeps getting more complex, it is more likely that a mistake will be made:

* Mistakes in software are inevitable. If you’re not engineering for it, you might as well be writing scripts that randomly corrupt data.
* Backups are not enough; the system must be carefully thought out to limit the damage a human mistake can cause.
* Human-fault tolerance is not optional. It’s essential, especially when Big Data adds so many more complexities to building applications.

### How will Big Data techniques help?

The Big Data techniques to be discussed address these scalability and complexity issues in dramatically:

1. The databases and computation systems for Big Data are aware of their distributed nature. Sharding and replication are handled for you.
    * Shading: the logic is internalized in the database, preventing situations where you accidentally query the wrong shard.
    * Scaling: just add new nodes and the systems will automatically rebalance onto the new nodes.
2. Make data immutable. Instead of storing the pageview counts as your core dataset, which you continuously mutate as new pageviews come in, you store the raw pageview information, which is never modified. <u>When you make a mistake, you might write bad data, but at least you won’t destroy good data.</u> This is a much stronger human-fault tolerance guarantee than in a traditional system based on mutation. [p6]

### NoSQL is not a panacea

Innovation in scalable data systems in the past decades include:

* Large-scale computation systems: such as [Hadoop](https://en.wikipedia.org/wiki/Apache_Hadoop)
* Databases: such as [Cassandra](https://en.wikipedia.org/wiki/Apache_Cassandra) and [Riak](https://en.wikipedia.org/wiki/Riak).

These systems can handle very large amounts of data, but with serious trade-offs:

* Hadoop can parallelize large-scale batch computations on very large amounts of data, but the computations have high latency. You don’t use Hadoop for anything where you need low-latency results.
* NoSQL databases like Cassandra achieve their scalability by offering you a much more limited data model than you’re used to with something like SQL.
    * Squeezing your application into these limited data models can be very complex.
    * They are not human-fault tolerant, because the databases are mutable.

These tools on their own are not a panacea. But when intelligently used in conjunction with one another, you can produce scalable systems for arbitrary data problems with human-fault tolerance and a minimum of complexity. This is the Lambda Architecture discussed throughout the book.

### First principles

What does a data system do? An intuitive definition is:

> A data system answers questions based on information that was acquired in the past up to the present.

* Data systems don’t just memorize and regurgitate information. They combine bits and pieces together to produce their answers.
* All bits of information are equal. Some information is derived from other pieces of information.
* When you keep tracing back where information is derived from, you eventually end up at information that’s not derived from anything. This is the rawest information you have: information you hold to be true simply because it exists. This information is called *data*.

Data is often used interchangeably with the word *information*. But for the remainder of this book, when we use the word data, we’re referring to that special information from which everything else is derived.

The most general-purpose data system answers questions by looking at the entire dataset, which has the definition:

> query = function(all data)

[p7]

The Lambda Architecture provides a general-purpose approach to implementing an arbitrary function on an arbitrary dataset and having the function return its results with low latency. This does not mean always using the same technologies to implement a database system; the Lambda Architecture defines a consistent approach to choosing those technologies and to wiring them together to meet your requirements.

### Desired properties of a Big Data system

Not only must a Big Data system perform well and be resource-efficient, it must be easy to reason about as well.

#### Robustness and fault tolerance

Systems need to behave correctly despite any of the following situations:

* Machines going down randomly
* The complex semantics of consistency in distributed databases
* Duplicated data
* Concurrency

These challenges make it difficult even to reason about a system is doing. Part of making a Big Data system robust is avoiding these complexities so that you can easily reason about the system

It’s imperative for systems to be *human-fault tolerant*, which is an oft-overlooked property. In a production system, it’s inevitable that someone will make a mistake, such as by deploying incorrect code that corrupts values in a database. If you build immutability and recomputation into the core of a Big Data system, the system will be innately resilient to human error by providing a clear and simple mechanism for recovery.

#### Low latency reads and updates

* Most applications require reads to be satisfied with very low latency, typically
between a few milliseconds to a few hundred milliseconds.
* The update latency requirements vary a great deal between applications. Some applications require updates to propagate immediately, but in other applications a latency of a few hours is fine.

You need to be able to:

* Achieve low latency updates when you need them in your Big Data systems,
* Achieve low latency reads and updates without compromising the robustness of the system.

#### Scalability

<u>Scalability is the ability to maintain performance in the face of increasing data or load by adding resources to the system.</u> The Lambda Architecture is horizontally scalable across all layers of the system stack: scaling is accomplished by adding more machines.

#### Generalization

A general system can support a wide range of applications. Because the Lambda Architecture is based on functions of all data, it generalizes to all applications.

#### Extensibility

YExtensible systems allow functionality to be added with a minimal development cost, without having to reinvent the wheel each time you add a related feature or make a change to how your system works.

Oftentimes a new feature or a change to an existing feature requires a migration of old data into a new format. Part of making a system extensible is making it easy to do large-scale migrations. Being able to do big migrations quickly and easily is core to the approach under discussion.

#### Ad hoc queries

Every large dataset has unanticipated value within it. Being able to mine a dataset arbitrarily gives opportunities for business optimization and new applications. Ultimately, you can’t discover interesting things to do with your data unless you can ask arbitrary questions of it.

#### Minimal maintenance

Maintenance is the work required to keep a system running smoothly. This includes:

* Anticipating when to add machines to scale,
* Keeping processes up and running,
* Debugging anything that goes wrong in production.

An important part of minimizing maintenance is choosing components that have as little implementation complexity as possible. You want to rely on components that have simple mechanisms underlying them. In particular, distributed databases tend to have very complicated internals. The more complex a system, the more likely something will go wrong, and the more you need to understand about the system to debug and tune it.

<u>You combat implementation complexity by relying on simple algorithms and simple components.</u> A trick employed in the Lambda Architecture is to push complexity out of the core components and into pieces of the system whose outputs are discardable after a few hours. The most complex components used, like read/write distributed databases, are in this layer where outputs are eventually discardable.

#### Debuggability

A Big Data system must provide the information necessary to debug the system when things go wrong. The key is to be able to trace, for each value in the system, exactly what caused it to have that value.

Debuggability is accomplished in the Lambda Architecture through the functional nature of the batch layer and by preferring to use recomputation algorithms when possible.

### The problems with fully incremental architectures

Traditional architectures look like the figure below:

[![Figure 1.3 Fully incremental architecture](figure_1.3.png)](figure_1.3.png "Figure 1.3 Fully incremental architecture")

What characterizes these architectures is the use of read/write databases and maintaining the state in those databases incrementally as new data is seen. For example, an incremental approach to counting pageviews would be to process a new pageview by adding one to the counter for its URL. The vast majority of both relational and non-relational database deployments are done as fully incremental architectures. This has been true for many decades.

Fully incremental architectures are so widespread that many people don’t realize it’s possible to avoid their problems with a different architecture.  This is called *familiar complexity* (complexity that’s so ingrained, you don’t even think to find a way to avoid it).

The problems with fully incremental architectures are significant. This section discusses:

* General complexities brought on by any fully incremental architecture.
* Two contrasting solutions for the same problem: one using the best possible fully incremental solution, and one using a Lambda Architecture.

You’ll see that the fully incremental version is significantly worse in every respect.

#### Operational complexity

With many complexities inherent in fully incremental architectures that create difficulties in operating production infrastructure, this section focuses on one: the need for read/write databases to perform online compaction, and what you have to do operationally to keep things running smoothly.

In a read/write database, as a disk index is incrementally added to and modified, parts of the index become unused. These unused parts take up space and eventually need to be reclaimed to prevent the disk from filling up. Reclaiming space as soon as it becomes unused is too expensive, so the space is occasionally reclaimed in bulk in a process called **compaction**.

Compaction is an intensive operation. The server places substantially higher demand on the CPU and disks during compaction, which dramatically lowers the performance of that machine during that time period. Databases such as HBase and Cassandra are well-known for requiring careful configuration and management to avoid problems or server lockups during compaction. The performance loss during compaction is a complexity that can even cause cascading failure: if too many machines compact at the same time, the load they were supporting will have to be handled by other machines in the cluster. This can potentially overload the rest of your cluster, causing total failure.

To manage compaction correctly, you have to:

* Schedule compactions on each node so that not too many nodes are affected at once.
* Be aware of how long a compaction takes to avoid having more nodes undergoing compaction than you intended.
* Make sure you have enough disk capacity on your nodes to last them between compactions.
* Make sure you have enough capacity on your cluster so that it doesn’t become overloaded when resources are lost during compactions.

The best way to deal with complexity is to get rid of that complexity altogether. The fewer failure modes you have in your system, the less likely it is that you’ll suffer unexpected downtime. Dealing with online compaction is a complexity inherent to fully incremental architectures, but in a Lambda Architecture the primary databases don’t require any online compaction.

#### Extreme complexity of achieving eventual consistency

Incremental architectures have another complexity when trying to make the system highly available.  A highly available system allows for queries and updates even in the presence of machine or partial network failure.

Achieving high availability competes directly with another important property called [**consistency**](https://en.wikipedia.org/wiki/Consistency_(database_systems)). A consistent system returns results that take into account all previous writes. The [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem) has shown that it’s impossible to achieve both high availability and consistency in the same system in the presence of network partitions. Therefore, a highly available system sometimes returns stale results during a network partition.

In order for a highly available system to return to consistency once a network partition ends (known as [**eventual consistency**](https://en.wikipedia.org/wiki/Eventual_consistency)), a lot of help is required from your application. [p11] Distributed databases achieve high availability by keeping multiple replicas of all information stored. When you keep many copies of the same information, that information is still available even if a machine goes down or the network gets partitioned, as shown in the figure below. During a network partition, a system that chooses to be highly available has clients update whatever replicas are reachable to them. This causes replicas to diverge and receive different sets of updates. Only when the partition goes away can the replicas be merged together into a common value.

[![Figure 1.4 Using replication to increase availability](figure_1.4_600.png)](figure_1.4.png "Figure 1.4 Using replication to increase availability")

##### **Example: highly available counting** *

For example, suppose you have two replicas with a count of 10 when a network partition begins. Suppose the first replica gets two increments and the second gets one increment.  When it comes time to merge these replicas together, with values of 12 and 11, what should the merged value be? Although the correct answer is 13, there’s no way to know just by looking at the numbers 12 and 11. They could have diverged at 11 (in which case the answer would be 12), or they could have diverged at 0 (in which case the answer would be 23).

To do highly available counting correctly, it’s not enough to just store a count:

* You need a data structure that’s amenable to merging when values diverge,
* You need to implement the code that will repair values once partitions end.

This is an amazing amount of complexity you have to deal with just to maintain a simple count.

In general, handling eventual consistency in incremental, highly available systems is unintuitive and prone to error. This complexity is innate to highly available, fully incremental systems. However, the Lambda Architecture structures itself in a different way that greatly lessens the burdens of achieving highly available, eventually consistent systems.

#### Lack of human-fault tolerance

The last problem with fully incremental architectures is their inherent lack of human-fault tolerance. <u>An incremental system is constantly modifying the state it keeps in the database, which means a mistake can also modify the state in the database. Because mistakes are inevitable, the database in a fully incremental architecture is guaranteed to be corrupted.</u>

This is one of the few complexities of fully incremental architectures that can be resolved without a complete rethinking of the architecture. Consider the two architectures shown in the following figure:

* Synchronous architecture, where the application makes updates directly to the database.
* Asynchronous architecture, where events go to a queue before updating the database in the background.

[![Figure 1.5 Adding logging to fully incremental architectures](figure_1.5.png)](figure_1.5.png "Figure 1.5 Adding logging to fully incremental architectures")

In both cases, every event is permanently logged to an events datastore. By keeping every event, if a human mistake causes database corruption, you can go back to the events store and reconstruct the proper state for the database. Because the events store is immutable and constantly growing, redundant checks, like permissions, can be put in to make it highly unlikely for a mistake to trample over the events store. This technique is also core to the Lambda Architecture and is discussed in depth in [Chapter 2](ch2.md) and [Chapter 3](ch3.md).

Although fully incremental architectures with logging can overcome the human-fault tolerance deficiencies of those without logging, the logging cannot handle the other complexities that have been discussed.

#### Fully incremental solution vs. Lambda Architecture solution

One of the example queries implemented throughout the book serves as a great contrast between fully incremental and Lambda architectures. The query has to do with pageview analytics and is done on two kinds of data coming in:

* *Pageviews*, which contain a user ID, URL, and timestamp.
* *Equivs*, which contain two user IDs. An equiv indicates the two user IDs refer to the same person.

The goal of the query is to compute the number of unique visitors to a URL over a
range of time. Queries should be up to date with all data and respond with minimal
latency (less than 100 milliseconds). Below is the interface for the query:

```
long uniquesOverTime(String url, int startHour, int endHour)
```

If a person visits the same URL in a time range with two user IDs connected via equivs (even transitively), that should only count as one visit. A new equiv coming in can change the results for any query over any time range for any URL.

Instead of showing details of the solutions which require covering many concepts such as indexing, distributed databases, batch processing, [HyperLogLog](https://en.wikipedia.org/wiki/HyperLogLog), we’ll focus on the characteristics of the solutions and the striking differences between them. The best possible fully incremental solution is shown in detail in Chapter 10, and the Lambda Architecture solution is built up in Chapter 8, 9, 14, and 15.

The two solutions can be compared on three axes: accuracy, latency, and throughput. [p14] The Lambda Architecture solution is significantly better in all respects. Lambda Architecture can produce solutions with higher performance in every respect, while also avoiding the complexity that plagues fully incremental architectures.

### Lambda Architecture


### Doubts and Solutions

#### Verbatim

p10 on Operational complexity

> In a read/write database, as a disk index is incrementally added to and modified, parts of the index become unused. These unused parts take up space and eventually need to be reclaimed to prevent the disk from filling up. Reclaiming space as soon as it becomes unused is too expensive, so the space is occasionally reclaimed in bulk in a process called *compaction*.

What is a disk index?
