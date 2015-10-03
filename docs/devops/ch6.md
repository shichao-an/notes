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


#### Multiple Versions of the Same Service Simultaneously Active

### Packaging

### Deploying to Multiple Environments

### Partial Deployment

#### Canary Testing

#### A/B Testing

### Rollback

### Tools
