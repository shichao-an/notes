### **Chapter 2. The Cloud as a Platform**

The [National Institute of Standards and Technology](https://en.wikipedia.org/wiki/National_Institute_of_Standards_and_Technology) (NIST) has provided a characterization of the cloud with the following elements:

* **On-demand self-service**
* **Broad network access**
* **Resource pooling**
* **Rapid elasticity**
* **Measured service**

NIST also characterizes the various types of services available from cloud providers, as shown in the table below:

Service Model | Examples
------------- | --------
**SaaS**: Software as a Service | E-mail, online games, Customer Relationship Management, virtual desktops, etc.
**PaaS**: Platform as a Service | Web servers, database, execution runtime, development tools, etc.
**IaaS**: Infrastructure as a Service | Virtual machines, storage, load balancers, networks, etc.

### Features of the Cloud

#### Virtualization

[p29]

##### **Creating a Virtual Machine**

[p30]

##### **Loading a Virtual Machine**

[p30]

The process of creating a VM image is called *baking* the image:

* A *heavily baked* image contains all of the software required to run an application,
* A *lightly baked* image contains only a portion of the software required, such as an operating system and a middleware container.

Virtualization introduces several types of uncertainty should be aware of.

* Because a VM shares resources with other VMs on a single physical machine, there may be some performance interference among the VMs. This situation may be particularly difficult for cloud consumers as they usually have no visibility into the co-located VMs owned by other consumers.
* There are also time and dependability uncertainties when loading a VM, depending on the underlying physical infrastructure and the additional software that needs to be dynamically loaded. DevOps operations often create and destroy VMs frequently for setting up different environments or deploying new versions of software.

#### IP and Domain Name System Management

##### **DNS**

##### **Persistence of IP Addresses with Respect to VMs**

The IP address assigned to a virtual machine on its creation persists as long as that VM is active. A VM becomes inactive when it is terminated, paused, or stopped. In these cases, the IP address is returned to the cloud provider’s pool for reassignment.

##### **Platform as a Service**

The additional abstraction of PaaS over IaaS means that you can focus on the important bits of your system—the application:

* Pros: You do not have to deal with the network configuration, load balancers, operating systems, security patches on the lower layers, and so on.
* Cons: It also means you give up visibility into and control over the underlying layers. Where this is acceptable, it might be well worthwhile to use a PaaS solution. However, when you end up needing the additional control at a later stage, the migration might be increasingly hard.

#### Distributed Environment

This section explores some of the implications of having hundreds of thousands of servers within a cloud provider’s environment. These implications concern the time involved for various operations, the probability of failure, and the consequences of these two aspects on the consistency of data.

##### **Time**

* Accessing 1MB (roughly one million bytes) sequentially from main memory takes on the order of 12µs (microseconds).
* Accessing an item from a spinning disk requires on the order of 4ms (milliseconds) to move the disk head to the correct location.

Then, reading 1MB takes approximately 2ms.

In a distributed environment where messages are the means of communication between the various processes involved in an application:

* A round trip within the same datacenter takes approximately 500µ.
* A round trip between California and the Netherlands takes around 150ms.

Consequences:

* Determining what data to maintain in memory or on the disk is a critical performance decision. Caching allows for maintaining some data in both places but introduces the problem of keeping the data consistent.
* Where persistent data is physically located will also have a large impact on performance.

Combining these two consequences with the possibility of failure, discussed in the next section, leads to a discussion of keeping data consistent using different styles of database management systems.

##### **Failure**

Although any particular cloud provider may guarantee high availability, these guarantees are typically for large segments of their cloud as a whole and do not refer to the components.  Individual component failure can thus still impact your application.

The possibilities for individual element failure are significant. Amazon released some data stating that in a datacenter with ~64,000 servers with 2 disks each, on average more than 5 servers and 17 disks fail each day.

Below is a list of problems arising in a datacenter in its first year of operation (from a presentation by [Jeff Dean](https://en.wikipedia.org/wiki/Jeff_Dean_(computer_scientist)), Google):

* ~0.5 overheating (power down most machines in <5 minutes, ~1–2 days to recover)
* ~1 PDU failure (~500–1,000 machines suddenly disappear, ~6 hours to come back)
* ~1 rack-move (plenty of warning, ~500–1,000 machines powered down, ~6 hours)
* ~1 network rewiring (rolling ~5% of machines down over 2-day span)
* ~20 rack failures (40–80 machines instantly disappear, 1–6 hours to get back)
* ~5 racks go wonky (40–80 machines see 50% packet loss)
* ~8 network maintenances (4 might cause ~30-minute random connectivity losses)
* ~12 router reloads (takes out DNS for a couple minutes)
* ~3 router failures (have to immediately pull traffic for an hour)
* ~dozens of minor 30-second blips for DNS
* ~1,000 individual machine failures
* ~thousands of hard drive failures
* slow disks, bad memory, misconfigured machines, flaky machines, etc.
* long-distance links: wild dogs, sharks, dead horses, drunken hunters, etc.

What do these failure statistics mean from an application or operations perspective?

1. First, any particular VM or portion of a network may fail. This VM or network may be performing application or operation functionality.
2. Second, since the probability of failure of serial use of components is related to the product of the failure rate of the individual components, the more components involved in a request, the higher the probability of failure.

##### **Failure of a VM**

One of the major decisions the architect of a distributed system makes is how to divide state among the various pieces of an application. If a stateless component fails, it can be replaced without concern for state. On the other hand, state must be maintained somewhere accessible to the application, and getting state and computation together in the same VM will involve some level of overhead. We distinguish three main cases:

1. **A stateless component**. If a VM is stateless, then failure of a VM is recovered by creating another instance of the same VM image and ensuring that messages are correctly routed to it. This is the most desirable situation from the perspective of recovering from failure.
2. **Client state**. A session is a dialogue between two or more components or devices. Typically, each session is given an ID to provide continuity within the dialogue.
    * For example, you may log in to a website through one interaction between your browser and a server. Session state allows your browser to inform the server in successive messages that you have been successfully logged in and that you are who you purport to be. Sometimes the client will add additional state for security or application purposes. Since client state must be sent with a message to inform the server of the context or a set of parameters, it should be kept to a minimum.
3. **Application state** contains the information specific to an application or a particular user of an application. It may be extensive, such as a knowledge base or the results of a web crawler, or it may be small, such as the current position of a user when watching a streaming video. We identify three categories of application states:
    * **Small amounts of persistent state.** The persistent state must be maintained across multiple sessions or across failure of either servers or clients. The application can maintain this state either per user or for the whole application. Small amounts of persistent state can be:
        * Maintained in a flat file or other structure on a file system.
        * Cached using a tool that maintains a persistent state across VM instances such as ZooKeeper or Memcached.
    * **Moderate amounts of persistent or semi-persistent state**. It is advantageous to cache those portions of persistent state that are used frequently in computations and to maintain state across different instances of a VM that allows the sharing of this state. In some sense, this is equivalent to shared memory at the hardware level except that it is done across different VMs across a network. Tools such as Memcached are intended to manage moderate amounts of shared state that represent cached database entries or generated pages. Memcached automatically presents a consistent view of the data to its clients, and by sharing the data across servers, it provides resilience in the case of failure of a VM.
    * **Large amounts of persistent state**. Large amounts of persistent state can be kept in either of the following: [p37]
        * A database managed by a database management system,
        * A distributed file system such as Hadoop Distributed File System (HDFS).

##### **The Long Tail**

[p37-39]

In the cloud, many phenomena such as response time to requests show a long-tail distribution.  This result is often due to the increased probability of failure with more entities involved, and the failure of one component causes response time to be an order slower than usual (e.g., until a network packet is routed through a different link, after the main network link broke and the error has been detected).

Simple requests such as computation, reading a file, or receiving a local message will have a distribution closer to normal. Complicated requests such as extensive map-reduce jobs, searches across a large database, or launching virtual instances will have a skewed distribution such as a long tail.

A request that takes an exceedingly long time to respond should be treated as a failure. However, one problem with such a request is that there is no way of knowing whether the request has failed altogether or is going to eventually complete. One mechanism to combat the long tail is to cancel a request that takes too long.

##### **Consistency**

[p39]

Consistency is maintained in a distributed system by introducing locks that control the sequence of access to individual data items. Locking data items introduces delays in accessing those data items; consequently, there are a variety of different schemes for maintaining consistency and reducing the delay caused by locks. Regardless of the scheme used, the availability of data items will be impacted by the delays caused by the introduction of locks.

In addition, in the cloud persistent data may be partitioned among different locales to reduce access time, especially if there is a large amount of data. Per a theoretical result called the [CAP](https://en.wikipedia.org/wiki/CAP_theorem) (Consistency, Availability, Partition Tolerance) theorem, it is not possible to simultaneously have fully available, consistent, and partitioned data.

[Eventual consistency](https://en.wikipedia.org/wiki/Eventual_consistency) means that distributed, partitioned, and replicated data will be consistent after a period of time even if not immediately upon a change to a data item; the replicas will become consistent eventually.

##### **NoSQL Databases**

For a variety of reasons, including the CAP theorem and the overhead involved in setting up a relational database system, a collection of database systems have been introduced that go under the name NoSQL. Originally the name literally meant *No* SQL, but since some of the systems now support SQL, it now stands for *Not Only* SQL.

NoSQL systems use a different data model than relational systems. Relational systems are based on presenting data as tables. NoSQL systems use data models ranging from key-value pairs to graphs. The rise of NoSQL systems has had several consequences:

* NoSQL systems are not as mature as relational systems, and many features of relational systems such as transactions, schemas, and triggers are not supported by these systems. The application programmer must implement these features if they are needed in the application.
* The application programmer must decide which data model(s) are most appropriate for their use. Different applications have different needs with respect to their persistent data, and these needs must be understood prior to choosing a database system.
* Applications may use multiple database systems for different needs.
    * [Key-value stores](https://en.wikipedia.org/wiki/Key-value_database) can deal with large amounts of semistructured data efficiently.
    * [Graph database](https://en.wikipedia.org/wiki/Graph_database) systems can maintain connections among data items efficiently.

    The virtue of using multiple different database systems is that you can better match a system with your needs.

##### **Elasticity**

Rapid elasticity and provisioning is one of the characteristics of the cloud identified by NIST. Elasticity means that the number of resources such as VMs used to service an application can grow and shrink according to the load.  Monitoring the utilization of the existing resources is one method for measuring the load.

The following figure clients accessing VMs through a load balancer and a monitor determining CPU and I/O utilization of the various VMs, grouped together in a scaling group. The monitor sends its information to the scaling controller, which has a collection of rules that determine when to add or remove the server in the scaling group.

[![FIGURE 2.4 Monitoring used as input to scaling [Notation: Architecture]](figure_2.4.png)](figure_2.4.png "FIGURE 2.4 Monitoring used as input to scaling [Notation: Architecture]")

### DevOps Consequences of the Unique Cloud Features

Three of the unique aspects of the cloud that impact DevOps are:

* The ability to create and switch environments simply,
* The ability to create VMs easily,
* The management of databases.

#### Environments

An environment in our context is a set of computing resources sufficient to execute a software system, including all of the supporting software, data sets, network communications, and defined external entities necessary to execute the software system.

The essence of this definition is that an environment is self-contained except for explicitly defined external entities. An environment is typically isolated from other environments. Chapter 5 covers a number of environments such as the Dev, integration, user testing, and production environments. In the case study in Chapter 12, the life cycle of an environment is explicitly a portion of their deployment pipeline. [p41]

The isolation of one environment from another is enforced by having no modifiable shared resources. <u>Resources that are read-only, such as feeds of one type or another, can be shared without a problem. Since an environment communicates with the outside world only through defined external entities, these entities can be accessed by URLs and, hence, managed separately.</u> Writing to or altering the state of these external entities should only be done by the production environment, and separate external entities must be created (e.g., as dummies or test clones) for all other environments.

The following figure shows two variants of two different environments: a testing environment and a production environment: Each contains slightly different versions of the same system. The two load balancers, responsible for their respective environments, have different IP addresses.

* a. Testing can be done by forking the input stream to the production environment and sending a copy to the testing environment as shown in part (a) in the figure. <u>In this case, it is important that the test database be isolated from the production database.</u>
* b. Part b shows an alternative situation. In this case, some subset of actual production messages is sent to the test environment that performs live testing. Canary testing and other methods of live testing are discussed in [Chapter 6](ch6.md).

[![FIGURE 2.5 (a) Using live data to test. (b) Live testing with a subset of users.  [Notation: Architecture]](figure_2.5a.png)](figure_2.5a.png "FIGURE 2.5 (a) Using live data to test. (b) Live testing with a subset of users.  [Notation: Architecture]")
[![FIGURE 2.5 (a) Using live data to test. (b) Live testing with a subset of users.  [Notation: Architecture]](figure_2.5b.png)](figure_2.5b.png "FIGURE 2.5 (a) Using live data to test. (b) Live testing with a subset of users.  [Notation: Architecture]")

Moving between environments can be accomplished in a single script that can be tested for correctness prior to utilizing it. Chapter 6 also discusses other techniques for moving between testing and production environments.

A consequence of easily switching production from one environment to another is that achieving business continuity becomes easier. Business continuity means that businesses can continue to operate in the event of a disaster occurring either in or to their main datacenter. [Chapter 11](ch11.md) dicusses a case study about managing multiple datacenters, but for now observe that there is no requirement that the two environments be co-located in the same datacenter. There is a requirement that the two databases be synchronized if the goal is quickly moving from one environment to a backup environment.

#### Creating Virtual Machines Easily

One of the problems that occurs in administering the cloud from a consumer’s perspective arises because it is so easy to allocate new VMs, which may lead to:

* **Security risk**. Virtual machines need to have the latest patches applied, just as physical machines, and need to be accounted for. Unpatched machines constitute a security risk.
* **Cost**. In a public cloud, the consumer pays for the use of VMs.

The term **VM sprawl** is used to describe the complexity in managing too many VMs. Similarly, the challenges of having too many VM images is called **image sprawl**. Developing and enforcing a policy on the allocation of machines and archiving of VM images is one of the activities necessary when utilizing the cloud as a platform.

#### Data Considerations

The economic viability of the cloud coincided with the advent of NoSQL database systems. Many systems utilize multiple different database systems, both relational and NoSQL. Furthermore, large amounts of data are being gathered from a variety of sources for various business intelligence or operational purposes. Just as computational resources can be added in the cloud by scaling, storage resources can also be added.

##### **HDFS**

HDFS provides storage for applications in a cluster. HDFS also provides the file system for many NoSQL database systems. HDFS suppors commands such as open, create, read, write, close through a normal file system interface.

Since the storage provided by HDFS is shared by multiple applications, a manager controls the name space of file names and allocates space when an application wishes to write a new block. This manager also provides information so that applications can perform direct access to particular blocks.

In HDFS, the manager is called the NameNode, and each element of the storage pool is called a DataNode. There is one NameNode with provision for a hot backup. Each DataNode is a separate physical computer or VM.  Applications are restricted to write a fixed-size block (typically 64MB). When an application wishes to write a new block to a file, it contacts the NameNode and asks for the DataNodes where this block will be stored. Each block is replicated some number of times, typically three. The NameNode responds to a request for a write with a list of the DataNodes where the block to be written will be stored, and the application then writes its block to each of these DataNodes.

Many features of HDFS are designed to guard against failure of the individual DataNodes and to improve the performance of HDFS. For our purposes, the essential element is that HDFS provides a pool of storage sites that are shared across applications.

##### **Operational Considerations**

The operational considerations associated with a shared file system such as HDFS are twofold.

1. **Who manages the HDFS installation?** HDFS can be either a shared system among multiple applications, or it can be instantiated for a single application.  In case of a single application, its management will be the responsibility of the development team for that application. In the shared case, the management of the system must be assigned somewhere within the organization.
2. **How is the data stored within HDFS protected in the case of a disaster?** HDFS itself replicates data across multiple DataNodes, but a general failure of a datacenter may cause HDFS to become unavailable or the data being managed by HDFS to become corrupted or lost. Consequently, business continuity for those portions of the business dependent on the continued execution of HDFS and access to the data stored within HDFS is an issue that must be addressed.

### Summary

[p44-45]
