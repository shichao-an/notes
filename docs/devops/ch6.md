### **Chapter 6. Deployment**

### Introduction

**Deployment** is the process of placing a version of a service into production. The initial deployment of a service can be viewed as going from no version of the service to the initial version of the service. Because an initial deployment happens only once for most systems and new versions happen frequently, this chapter discuss upgrading a service.

The overall goal of a deployment is to place an upgraded version of the service into production with minimal impact to the users of the system, whether it is through failures or downtime.

There are three reasons for changing a service:

* To fix an error
* To improve some quality of the service
* To add a new feature

The initial discussion assumes that deployment is an all-or-nothing process: at the end of the deployment either all of the virtual machines (VMs) running a service have had the upgraded version deployed or none of them have. Later this chapter, partial deployments are discussed.

[![Figure 6.1 Microservice 3 is being upgraded. (Adapted from Figure 4.1.) [Notation: Architecture]](figure_6.1_600.png)](figure_6.1.png "Figure 6.1 Microservice 3 is being upgraded. (Adapted from Figure 4.1.) [Notation: Architecture]")

In the figure above, Microservice 3 is being upgraded (shown in dark gray). Microservice 3 depends on microservices 4 and 5, and microservices 1 and 2 (clients of microservice 3) depend on it. For now, assume that any VM runs exactly one service. Other options are discussed later in this chapter.

The goal of a deployment is to move from the current state that has N VMs of the old version, A, of a service executing, to a new state where there are N VMs of the new version, B, of the same service in execution.

### Strategies for Managing a Deployment

There are two popular strategies for managing a deployment: **blue/green deployment** and **rolling upgrade**. They differ in terms of costs and complexity.

Before discussing these strategies in more detail, we need to make the following two assumptions:

1. **Service to the clients should be maintained while the new version is being deployed.**
    * Maintaining service to the clients with no downtime is essential for many Internet e-commerce businesses.
    * Organizations that have customers primarily localized in one geographic area can afford scheduled downtime, but scheduled off-hours during downtime requires system administrators and op operators to work in the off-hours.
2. **Any development team should be able to deploy a new version of their service at any time without coordinating with other teams.**
    * This may have an impact on client services developed by other teams, but removes one cause for [synchronous coordination](ch1.md#coordination).

The placement of a new VM with a version into production takes time. In order to place an upgraded VM of a service into production, the new version must be loaded onto a VM and be initialized and integrated into the environment, sometimes with dependency on placements of some other services first. This can take on the order of minutes. Consequently, depending on how parallel some actions can be and their impact on the system still serving clients, the upgrade of hundreds or thousands of VMs can take hours or, in extreme cases, even days.

#### Blue/Green Deployment

A **blue/green deployment** (sometimes called **big flip** or **red/black deployment**) consists of maintaining the N VMs containing version A in service while provisioning N VMs of virtual machines containing version B.

Once N VMs have been provisioned with version B and are ready to service requests, then client requests can be routed to version B. This is a matter of instructing the domain name server (DNS) or load balancer to change the routing of messages. This routing switch can be done in a single stroke for all requests. After a supervisory period, the N VMs provisioned with version A are removed from the system. If anything goes wrong during the supervisory period, the routing is switched back, so that the requests go to the VMs running version A again.

This strategy is conceptually simple, but has some disadvantage:

* It is expensive in terms of both VM and software licensing costs.
    * The provisioning of the N VMs containing version B prior to terminating all version A VMs is the source of the cost. For this period of time, the VM-based cost doubles.
    * The provisioning of the hundred (or more) new VMs (even if it can be done in parallel) hundreds of VMs can be time-consuming.
* <u>Long-running requests and stateful data during the switch-over and rollback require special care.</u>

<u>A variation of this model is to do the traffic switching gradually. A small percentage of requests are first routed to version B, effectively conducting a canary test.</u> Canary testing is mentioned in Chapter 5 and discuss it in more detail in the section [Canary Testing](#canary-testing). If everything goes well for a while, more version B VMs can be provisioned and more requests can be routed to this pool of VMs, until all requests are routed to version B.  This increases confidence in your deployment, but also introduces a number of consistency issues (discussed in [Section 6.3](#logical-consistency)).

#### Rolling Upgrade

A **rolling upgrade** consists of deploying a small number of version B VMs at a time directly to the current production environment, while switching off the same number of VMs running version A. For example, we deploy one version B VM at a time. Once an additional version B VM has been deployed and is receiving requests, one version A VM is removed from the system. Repeating this process N times results in a complete deployment of version B.

This strategy is inexpensive but more complicated. It may cost a small number of additional VMs for the duration of the deployment, but again introduces a number of issues of consistency and more risks in disturbing the current production environment.

The following figure provides a representation of a rolling upgrade within the Amazon cloud:

[![Figure 6.2 Representation of a rolling upgrade [Notation: BPMN]](figure_6.2.png)](figure_6.2.png "Figure 6.2 Representation of a rolling upgrade [Notation: BPMN]")

1. Each VM (containing one service) is *decommissioned* (removed, deregistered from the elastic load balancer (ELB), and terminated)
2. Then, a new VM is started and registered with the ELB.
3. This process continues until all of the VMs containing version A have been replaced with VMs containing version B.

The additional cost of a rolling upgrade can be low if you conduct your rolling upgrade when your VMs are not fully utilized, and your killing of one or a small number of VMs at a time still maintains your expected service level. It may cost a bit if you add a small number of VMs before you start the rolling upgrade to mitigate the performance impact and risk of your rolling upgrade.

During a rolling upgrade, one subset of the VMs is providing service with version A, and the remainder of the VMs are providing service with version B.  This creates the possibility of failures as a result of mixed versions. This type of failure is discussed in the [next section](#logical-consistency).

### Logical Consistency

There are some types of logical consistency:

* **Mixed versions in deployment**. The deployment using a rolling upgrade introduces one type of logical inconsistency (multiple versions of the same service will be simultaneously active). This may also happen with those variants of the blue/green deployment that put new versions into service prior to the completion of the deployment.
* **Inconsistency in functionality between a service and its clients**. Revisiting [Figure 6.1](figure_6.1.png), A service being deployed without synchronous coordination with its client or dependent services may introduce a possible source of logical inconsistency.
* **Inconsistency between a service and data kept in a database.**

#### Multiple Versions of the Same Service Simultaneously Active

The following figure shows an instance of an inconsistency because of two active versions of the same service. Two components are shown: the client and two versions (versions A and B) of a service.

1. The client sends a message that is routed to version B.
2. Version B performs its actions and returns some state to the client.
3. The client then includes that state in its next request to the service.
4. The second request is routed to version A, and this version does not know what to make of the state, because the state assumes version B. Therefore, an error occurs.

This problem is called a **mixed-version race condition**.

[![Figure 6.3 Mixed-version race condition, leading to an error [Notation: UML Sequence Diagram]](figure_6.3.png)](figure_6.3.png "Figure 6.3 Mixed-version race condition, leading to an error [Notation: UML Sequence Diagram]")

Several techniques can prevent this situation:

* **Make the client version aware** so that it knows that its initial request was serviced by a version B VM. Then it can require its second request to be serviced by a version B VM.
    * [Chapter 4](ch4.md) describes how a service is registered with a registry/load balancer. This registration can contain the version number. The client can then request a specific version of the service.  Response messages from the service should contain a tag so that the client is aware of the version of the service with which it has just interacted.
* **Toggle the new features** contained in version B and the client so that only one version is offering the service at any given time.
* **Make the services forward and backward compatible**, and enable the clients to recognize when a particular request has not been satisfied.

These options are not mutually exclusive (some of these options can be used together). For example, you can use feature toggles within a backward compatible setting. Within a rolling upgrade you will have installed some VMs of the new version while still not having activated the new features. This requires the new version to be backward compatible.

##### **Feature Toggling**

[p107]

To coordinate the activation of the feature in two directions:

1. All of the VMs for the service you just deployed must have the service’s portion of the feature activated.
2. All of the services involved in implementing the feature must have their portion of the feature activated.

Feature toggles (described in [Chapter 5](ch5.md#feature-toggles)) can be used to control whether a feature is activated. A feature toggle is a piece of code within an *if* statement where the *if* condition is based on an externally settable feature variable. Using this technique means that the problems associated with activating a feature are:

* Determining that all services involved in implementing a feature have been sufficiently upgraded,
* Activating the feature in all of the VMs of these services at the same time.

Both of these problems are examples of synchronizing across the elements of a distributed system. The primary modern methods for performing such synchronization are based on the Paxos or ZAB algorithms, which are difficult to implement correctly. However, standard implementations are available in systems such as ZooKeeper.

**Example of feature toggling with ZooKeeper**

Assume the service being deployed implements a portion of a single feature, *Feature X*. When a VM of the service is deployed, it registers itself as being interested in *FeatureXActivationFlag*. If the flag is false, then the feature is toggled off; if the flag is true, the feature is toggled on. If the state of the *FeatureXActivationFlag* changes, then the VM is informed of this and reacts accordingly.

An agent (which can human or automated) external to any of the services in the system being upgraded is responsible for setting *FeatureXActivationFlag*. The flag is maintained in ZooKeeper and thus kept consistent across the VMs involved. As long as all of the VMs are informed simultaneously of the toggling, then the feature is activated simultaneously and there is no version inconsistency that could lead to failures. The simultaneous information broadcast is performed by ZooKeeper. This particular use of ZooKeeper for feature toggling is often implemented in other tools. For example, Netflix’s [Archaius](https://github.com/Netflix/archaius) tool provides configuration management for distributed systems. The configuration being managed can be feature toggles or any other property.

<u>The agent is aware of the various services implementing *Feature X* and does not activate the feature until all of these services have been upgraded. </u>

One complication comes from deciding when the VMs have been "sufficiently upgraded". VMs may fail or become unavailable. Waiting for these VMs to be upgraded before activating the feature is not desirable. The use of a registry/ load balancer as described in [Chapter 4](ch4.md) enables the activation agent to avoid these problems. Recall that each VM must renew its registration periodically to indicate that it is still active. The activation agent examines the relevant VMs that are registered to determine when all VMs of the relevant services have been upgraded to the appropriate versions.

##### **Backward and Forward Compatibility**

* **Backward compatibility** means the new version of the service behaves as the old version. For requests that are known to the old version of a service, the new version provides the same behavior. In other words, the external interfaces provided by version B of a service are a superset of the external interfaces provided by version A of that service.
* **Forward compatibility** means that a client deals gracefully with error responses indicating an incorrect method call. Suppose a client wishes to utilize a method that will be available in version B of a service but the method is not present in version A. Then if the service returns an error code indicating it does not recognize the method call, the client can infer that it has reached version A of the service.

Maintaining backward compatibility can be done using the pattern depicted in the figure below:

[![Figure 6.4 Maintaining backward compatibility for service interfaces [Notation: Architecture]](figure_6.4.png)](figure_6.4.png "Figure 6.4 Maintaining backward compatibility for service interfaces [Notation: Architecture]")

The service being upgraded makes a distinction between internal and external interfaces:

* **External interfaces** include all of the existing interfaces from prior versions as well as, possibly, new ones added with this version.
* **Internal interfaces** can be restructured with every version.
* In-between the external interfaces and the internal interfaces is a **translation layer** that maps the old interfaces to the new ones.

As far as a client is concerned, the old interfaces are still available for the new version. If a client wishes to use a new feature, then a new interface is available for that feature.

One consequence of using this pattern is that obsolete interfaces may be maintained beyond the point where any clients use them. Determining which clients use which interfaces can be done through monitoring and recording all service invocations. Once there are no usages for a sufficiently long time, the interface can be deprecated. The deprecating of an interface may result in additional maintenance work, so it should not be done lightly.

Forward and backward compatibility allows for independent upgrade for services under your control. Not all services will be under your control. In particular, third-party services, libraries, or legacy services may not be backward compatible. In this case, there are several techniques you can use, although none of them are foolproof:

* **Discovery**.
* **Exploration**.
* **Portability layer**. The following figure shows the concept of a portability layer. A portability layer provides a single interface that can be translated into the interfaces for a variety of similar systems. This technique has been used to port applications to different operating systems, to allow multiple different devices to look identical from the application perspective, or to allow for the substitution of different database systems.

[![Figure 6.5 Portability layer with two versions of the external system coexisting [Notation: Architecture]](figure_6.5.png)](figure_6.5.png "Figure 6.5 Portability layer with two versions of the external system coexisting [Notation: Architecture]")

#### Compatibility with Data Kept in a Database

Besides the compatibility of services, some services must also be able to read and write to a database in consistently. For example, that the data schema changes: In the old version of the schema, there is one field for customer address; in the new version, the address is broken into street, city, postal code, and country. Inconsistency, in this case, means that a service intends to write the address as a single field using the schema that has the address broken into portions.

Inconsistencies are triggered by a change in the database schema. A schema can be either explicit such as in relational database management systems (RDBMSs) or implicit such as in various NoSQL database management systems.

The most basic solution to such a schema change is <u>not to modify existing fields but only to add new fields or tables</u>, which can be done without affecting existing code. The use of the new fields or tables can be integrated into the application incrementally. <u>One method for accomplishing this is to treat new fields or tables as new features in a release</u>. That is, either the use of the new field or table is under the control of a feature toggle or the services are forward and backward compatible with respect to database fields and tables.

If a change to the schema is absolutely required you have two options:

1. Convert the persistent data from the old schema to the new one.
2. Convert data into the appropriate form during reads and writes. This could be done either by the service or by the database management system.

These options are not mutually exclusive. You might perform the conversion in the background and convert data on the fly while the conversion is ongoing.  Modern RDBMSs provide the ability to reorganize data from one schema to another online while satisfying requests, although at a storage and performance cost. Database systems typically do not provide this capability, and so, if you use them, you have to engineer a solution for your particular situation. [p111]

### Packaging

This section discusses consistency of the build process in terms of getting the latest versions into the services. Deciding that components package services and that each service is packaged as exactly one component (discussed in [Chapter 4](ch4.md)), does not end your packaging decisions. You must decide on the binding time among components residing on the same VM and a strategy for placing services into VMs. Packaging components onto a VM image is called **baking** and the options range from **lightly baked** to **heavily baked** (discussed in [Chapter 5](ch5.md)). What we add to that discussion here is the number of processes loaded into each VM.

A VM is an image that is running on top of a hypervisor that enables sharing a single bare metal processor, memory, and network among multiple tenants or VMs. The image of the VM is loaded onto the hypervisor from which it is scheduled.

A VM image could include multiple independent processes, each a service. The question is: **Should multiple services be placed in a single VM image?** The following figure shows two options:

* In the top option, a developer commits a service for deployment, which is embedded into a single VM image. For example, Netflix claims they package one service per VM.
* In the bottom option, different developers commit different services into a single VM image. <u>The emergence of lightweight containers often assumes one service per container, but with the possibility to have multiple containers per VM.</u>

[![Figure 6.6 Different options for packaging services [Notation: Architecture]](figure_6.6.png)](figure_6.6.png "Figure 6.6 Different options for packaging services [Notation: Architecture]")

One minor difference in these two options is the number of times that a VM image must be baked:

* If there is one service per VM, then that VM image is created when a change in its service is committed.
* If there are two services per VM, then the VM image must be rebaked whenever a change to either the first or second service is committed.

A more important difference occurs when service 1 sends a message to service 2:

* If the two are in the same VM, then the message does not need to leave the VM to be delivered.
* If they are in different VMs, then more handling and network communication are involved.

This means the latency for messages will be higher when each service is packaged into a single VM.

However, packaging multiple services into the same VM image opens up the possibility of deployment race conditions, because different development teams do not coordinate over their deployment schedules and they may be deploying their upgrades at (roughly) the same time.

The examples below assume the upgraded services are included in the deployed portion of the VM (heavily baked) and not loaded later by the deployed software.

* In Figure 6.7 (below), development team 1 creates a new image with a new version (v<sub>m+1</sub>) of service 1 (S1) and an old version of service 2 (S2). Development team 2 creates a new image with an old version of service 1 and a new version (v<sub>n+1</sub>) of service 2. The provisioning processes of the two teams overlap, which causes a deployment race condition.

[![Figure 6.7 One type of race condition when two development teams deploy independently [Notation: UML Sequence Diagram]](figure_6.7.png)](figure_6.7.png "Figure 6.7 One type of race condition when two development teams deploy independently [Notation: UML Sequence Diagram]")

* In Figure 6.8 (below), development team 1 builds their image after development team 2 has committed their changes. The result is similar in that the final version that is deployed does not have the latest version of both service 1 and service 2.

[![Figure 6.8 A different type of race condition when two development teams deploy independently [Notation: UML Sequence Diagram]](figure_6.8.png)](figure_6.8.png "Figure 6.8 A different type of race condition when two development teams deploy independently [Notation: UML Sequence Diagram]")

The tradeoff for including multiple services into the same VM is between reduced latency and the possibility of deployment race conditions.

### Deploying to Multiple Environments

As long as services are independent and communicate only through messages, deployment to multiple environments (e.g. VMware and Amazon EC2) is possible basically with the design we have presented. The registry/load balancer discussed in [Chapter 4](ch4.md) needs to be able to direct messages to different environments.

#### Business Continuity

Introduced in [Chapter 2](ch2.md), **business continuity** is the ability for a business to maintain service when facing a disaster or serious outages. It is achieved by deploying to sites that are physically and logically separated from each other. This section differentiates between deploying to a public cloud and a private cloud, although the essential element, the management of state, is the same. Disaster recovery is discussed in [Chapter 10](ch10.md) and case study in [Chapter 11](ch11.md).

##### **Public Cloud**

Public clouds are extremely reliable in the aggregate. They consist of hundreds of thousands of physical servers and provide extensive replication and failover services. Failures do occur, which can be to particular VMs of your system or to other cloud services.

* A failure to a VM is not a rare occurrence.
    * Cloud providers achieve economies of scale partially by purchasing commodity hardware. Any element of the hardware can fail: memory, disk, motherboard, network, or CPU.
    * Failures may be total or partial. A partial failure in the underlying hardware can make your VM run slowly although it is still executing. In either case, you must architect your system to detect VM failures and respond to them. This is outside the scope of this chapter.
* A failure to the cloud infrastructure is a rare but not impossible occurrence.
    * A quick search on "public cloud outages" can give you information about the latest high-profile outages that have occurred.
    * Other outages are lower-profile but do still occur. You can survive many outages by choosing how you deploy your VMs.

Amazon EC2 has multiple regions (nine as of this writing) scattered around the globe. Each region has multiple availability zones. Each availability zone is housed in a location that is physically distinct from other availability zones and that has its own power supply, physical security, and so forth:

* If you deploy VMs of your system to different availability zones within the same region, you have some measure of protection against a cloud outage.
* If you deploy VMs of your system to different regions, then you have much more protection against outages, since some of the services such as elastic load balancing are per-region.

Two considerations to keep in mind when you deploy to different availability zones or regions are state management and latency:

1. **State management**. Making services stateless has several advantages, as discussed in [Chapter 4](ch4.md).
    * If a service is stateless then additional VMs can be created at any time to handle increased workload. Additional VMs can also be created in the event of a VM failure.
    * The disadvantages of stateless services are that state must be maintained somewhere in the system and latency may increase when the service needs to obtain or change this state.
2. **Latency**. Sending messages from one availability zone to another adds a bit of latency; messages sent from one region to another adds more latency to your system.

##### **Private Cloud**

[p116]

### Partial Deployment

Up to this point the discussion has been focused on all-or-nothing deployments.  Now we discuss two types of partial deployments: canary testing and A/B testing.

#### Canary Testing

A new version is deployed into production after having been tested in a staging environment, which is as close to a production environment as possible. There is still a possibility of errors existing in the new version. <u>These errors can be either functional or have a quality impact. Performing an additional step of testing in a real production environment is the purpose of canary testing.</u> A canary test is conceptually similar to a beta test in the shrink-wrapped software world.

One question is to whom to expose the canary servers. This can be a random sample of users. An alternative is to decide the question based on the organization a user belongs to, for example, the employees of the developing organization, or particular customers. The question could also be answered based on geography, for example, such that all requests that are routed to a particular datacenter are served by canary versions.

The mechanism for performing the canary tests depends on whether features are activated with feature toggles or whether services are assumed to be forward or backward compatible. In either case, a new feature cannot be fully tested in production until all of the services involved in delivering the feature have been partially deployed.

Messages can be routed to the canaries by making the registry/load balancer canary-aware and having it route messages from the designated testers to the canary versions. More and more messages can be routed until a desired level of performance has been exhibited.

* If new features are under the control of feature toggles, then turning on the toggle for the features on the canary versions activates these features and enables the tests to proceed.
* If the services use forward and backward compatibility, then the tests will be accomplished once all of the services involved in a new feature have been upgraded to the new version.

In either case, you should carefully monitor the canaries, and they should be rolled back in the event an error is detected.

#### A/B Testing

A/B testing is introduced in [Chapter 5](ch5.md). It is another form of testing that occurs in the production environment through partial deployment. The "A" and "B" refer to two different versions of a service that present either different user interfaces or different behavior. In this case, it is the behavior of the user when presented with these two different versions that is being tested.

If either A or B shows preferable behavior in terms of some business metric such as orders placed, then that version becomes the production version and the other version is retired.

Implementing A/B testing is similar to implementing canaries. The registry/ load balancer must be made aware of A/B testing and ensure that a single customer is served by VMs with either the A behavior or the B behavior but not both. The choice of users that are presented with version B (or A) may be randomized, or it may be deliberate. If deliberate, factors such as geographic location, age group (for registered users), or customer level (e.g., "gold" frequent flyers), may be taken into account.

### Rollback

The new version of a service is on probation for some period after deployment. It has gone through testing of a variety of forms but it still is not fully trusted.

**Rolling back** means reverting to a prior release. It is also possible to roll forward, to correct the error and generate a new release with the error fixed. Rolling forward is essentially just an instance of upgrading.

Because of the sensitivity of a rollback and the possibility of rolling forward, rollbacks are rarely triggered automatically. <u>A human should be in the loop who decides whether the error is serious enough to justify discontinuing the current deployment.</u> The human then must decide whether to roll back or roll forward.

#### Rollback for blue/green deployment

If you still have VMs with version A available, as in the blue/green deployment model before decommissioning all version A VMs, rolling back can be done by simply redirecting the traffic back to these. <u>One way of dealing with the persistent state problem is to keep version A VMs receiving a replicated copy of the requests version B has been receiving during the probation period.</u>

#### Rollback for rolling upgrade deployment

With a rolling upgrade model or you cannot simply replace version B by version A as a whole, you have to replace a version B VM with a version A VM in more complicated ways. The new version B can be in one of four states during its lifetime:

* **Uninstalled**: cannot be rolled back.
* **Partially installed**: have rollback possibilities (see below).
* **Fully installed but on probation**: rollback possibilities (see below).
* **Committed into production**: cannot be rolled back, although the old version could be treated as a new deployment and be redeployed.
    *  As in [Chapter 5](ch5.md), if version B has been committed then removal of all of the feature toggles that have been activated within version B should be put on the development teams’ list of activities to perform.

The strategy for rolling back (version B is partially installed or fully installed but on probation) depends on whether feature toggles are being used and have been activated. This pertains to both of the remaining two states:

* **Not using feature toggles**. Rolling back VMs in this case is a matter of disabling those VMs and reinstalling VMs running version A of the service.
* **Using feature toggles**.
    * If the features have not been activated, then we have the prior version. Disable VMs running version B and reinstall version A.
    * If the feature toggles have been activated, then deactivate them. If this prevents further errors, then no further action is required. If it does not, then we have the situation as if feature toggles were not present.

The remaining case deals with persistent data and is the most complicated. <u>Suppose all of the version B VMs have been installed and version B’s features activated, but a rollback is necessary. Rolling back to the state where version B is installed but no features activated is a matter of toggling off the new features, which is a simple action.</u> The complications come from consideration of persistent data.

A concern when an error is detected is that incorrect values have been written into the database. Dealing with erroneous database values is a delicate operation with significant business implications.

[p119-120]

Identifying and correcting incorrect values in the database is a delicate and complicated operation requiring the collection of much metadata.

### Tools

One method for categorizing tools is to determine whether they directly affect the internals of the entity being deployed. As in [Chapter 5](ch5.md), if a VM image contains all the required software including the new version, you can replace a whole VM of the old version with a whole VM of the new version. This is called using a **heavily baked** deployment approach.

Alternatively, you can use tools to change the internals of a VM, so as to deploy the new version by replacing the old version without terminating the VM. Even if you terminate the VM with the old version, you can start a new **lightly baked** VM but then access the machine from the inside to deploy the new version at a later stage of the deployment process.

* [Netflix Asgard](https://github.com/Netflix/asgard) is an open source, web-based tool for managing cloud-based applications and infrastructure. Asgard is not interested in the contents of these VMs. It uses a VM image that contains the new version and creates VMs for these images. One of the features of Asgard is that it understands deployment processes such as rolling upgrade. It allows specification of the number of VMs to be upgraded in a single cycle.
* Infrastructure-as-a-Service (IaaS) vendors also provide specific tools for coordinated VM provisioning, which is used as a part of a deployment. For example, Amazon allows users to use [CloudFormation](https://aws.amazon.com/cloudformation/) scripts as a parameterized, declarative approach for deployment of VMs. CloudFormation scripts understand dependencies and rollback.
* [Chef](https://www.chef.io/chef/) and [Puppet](https://puppetlabs.com/) are two examples of tools that manage the items inside a virtual machine. They can replace a version of a piece of software inside a VM and ensure that configuration settings conform to a specification.
* One emerging trend is the use of lightweight container tools, such as [Docker](https://www.docker.com/), in deployment. A lightweight container is an OS-level virtualization technique for running multiple isolated OSs on a single host (VM or physical machine). They are like VMs, but they are smaller and start much faster.
* Image management and testing tools such as [Vagrant](https://www.vagrantup.com/) and [Test Kitchen](http://kitchen.ci/) help control both VMs and items inside the VMs. A developer can spin up production-like environments for pre-commit testing and integration testing to reveal issues that would only surface in production.

### Summary

Strategies for deploying multiple VMs of a service include blue/green deployment and rolling upgrade:

* A blue/green deployment does not introduce any logical problems but requires allocating twice the number of VMs required to provide a service.
* A rolling upgrade is more efficient in how it uses resources but introduces a number of logical consistency problems:
    * Multiple different versions of a single service can be simultaneously active. These multiple versions may provide inconsistent versions of the service.
    * A client may assume one version of a dependent service and actually be served by a different version.
    * Race conditions can exist because of the choice of packing multiple and dependent services and multiple development teams performing concurrent deployment. Choosing the number of services to be packed into a single VM is often a tradeoff among resource utilization, performance, and complexity of deployment.

Solutions to the problems of logical consistency involve using some combination of feature toggles, forward and backward compatibility, and version awareness.

Deployments must occasionally be rolled back. Feature toggles support rolling back features, but the treatment of persistent data is especially sensitive when rolling back a deployment.

Deployment also plays an important role for achieving business continuity. Deploying into distinct sites provides one measure of continuity. Having an architecture that includes replication allows for a shorter time to repair and to resume processing in the event of an unexpected outage.

A variety of tools exist for managing deployment. The emergence of lightweight containers and image management tools is helping developers to deploy into small-scale production-like environments more easily for testing.
