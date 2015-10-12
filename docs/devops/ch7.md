### **Chapter 7. Monitoring**

### Introduction

This chapter focuses on software monitoring. Software monitoring comprises myriad types of monitoring and the considerations that come with them. Activities as varied as collecting metrics at various levels (resources/OS/middleware/application-level), graphing and analyzing metrics, logging, generating alerts concerning system health status, and measuring user interactions all are a portion of what is meant by monitoring.

The insights available from monitoring fall into five different categories:

1. Identifying failures and the associated faults both at runtime and during postmortems held after a failure has occurred.
2. Identifying performance problems of both individual systems and collections of interacting systems.
3. Characterizing workload for both short-term and long-term capacity planning and billing purposes.
4. Measuring user reactions to various types of interfaces or business offerings. A/B testing is disucssed in [Chapters 5](ch5.md) and [Chapter 6](ch6.md).
5. Detecting intruders who are attempting to break into the system.

The term **monitoring** refers to the process of observing and recording system state changes and data flows:

* **State changes** can be expressed by direct measurement of the state or by logs recording updates that impact part of the state.
* **Data flows** can be captured by logging requests and responses between both internal components and external systems.

The software supporting such a process is called a **monitoring system**.

Monitoring a workload include the tools and infrastructure associated with operations activities. All of the activities in an environment contribute to a datacenter’s workload, and this includes both operations-centric and monitoring tools.

DevOps’ continuous delivery/ deployment practices and strong reliance on automation mean that changes to the system happen at a much higher frequency. Use of a microservice architecture also makes monitoring of data flows more challenging.

Some examples of the new challenges are:

* **Monitoring under continuous changes is difficult.**
    * Traditional monitoring relies heavily on anomaly detection. You know the profile of your system during normal operation. You set thresholds on metrics and monitor to detect abnormal behavior. If your system changes, you may have to readjust them. This approach becomes less effective if your system is constantly changing due to continuous deployment practices and cloud elasticity.
    * Setting thresholds based on normal operation will trigger multiple false alarms during a deployment. Disabling alarms during deployments will, potentially, miss critical errors when a system is already in a fairly unstable state. Multiple deployments can simultaneously occur as we discussed in Chapter 6, and these deployments further complicate the setting of thresholds.
* **The cloud environment introduces different levels from application programming interface (API) calls to VM resource usage.** Choosing between a top-down approach and a bottom-up approach for different scenarios and balancing the tradeoffs is not easy.
* **Monitoring requires attention to more moving parts** (when adopting the microservice architecture as introduced in [Chapter 4](ch4.md)).
    * It also requires logging more inter-service communication to ensure a user request traversing through a dozen services still meets your service level agreements. If anything goes wrong, you need to determine the cause through analysis of large volumes of (distributed) data.
* **Managing logs becomes a challenge in large-scale distributed systems.**
    * When you have hundreds or thousands of nodes, collecting all logs centrally becomes difficult or prohibitively expensive. Performing analysis on huge collections of logs is challenging as well, because of the sheer volume of logs, noise, and inconsistencies in logs from multiple independent sources.

Monitoring solutions must be tested and validated just as other portions of the infrastructure. Testing a monitoring solution in your various environments is one portion of the testing, but the scale of your non-production environments may not approach the scale of your production—which implies that your monitoring environments may be only partially tested prior to being placed into production

### What to Monitor

The following table lists the insights you might gain from the monitoring data and the portions of the stack where such data can be collected: [p129]

Goal of Monitoring | Source of Data
------------------ | --------------
Failure detection | Application and infrastructure
Performance degradation detection | Application and infrastructure
Capacity planning | Application and infrastructure
User reaction to business offerings | Application
Intruder detection | Application and infrastructure

The fundamental items to be monitored consist of inputs, resources, and outcomes:

* The resources can be hard resources such as CPU, memory, disk, and network (even if virtualized).
* They can also be soft resources such as queues, thread pools, or configuration specifications.
* The outcomes include items such as transactions and business-oriented activities.

#### Failure Detection

Any element of the physical infrastructure can fail. Total failures are relatively easy to detect: No data is flowing where data used to flow. It is the partial failures that are difficult to detect, for instance: a cable is not firmly seated and degrades performance; before a machine totally fails because of overheating it experiences intermittent failure; and so forth.

Detecting failure of the physical infrastructure is the datacenter provider’s problem. Instrumenting the operating system or its virtual equivalent will provide the data for the datacenter.

Software can also fail, either totally or partially. Total failure is relatively easy to detect. Partial software failures have myriad causes (similar to partial hardware failures):

* The underlying hardware may have a partial failure;
* A downstream service may have failed;
* The software (or its supporting software) may have been misconfigured.

Detecting software failures can be done in one of three fashions:

1. The monitoring software performs **health checks** on the system from an external point.
2. A **special agent inside the system** performs the monitoring.
3. The **system itself** detects problems and reports them.

Partial failures may also manifest as performance problems (discussed in the following subsection).

#### Performance Degradation Detection

Detecting performance degradations is the most common use of monitoring data. Degraded performance can be observed by comparing current performance to historical data, or by complaints from clients or end users. Ideally, the monitoring system catches performance degradation before users are impacted at a notable strength.

Performance measures include **latency**, **throughput**, and **utilization**.

##### **Latency**

Latency is the time from the initiation of an activity to its completion, which can be measured at various levels of granularity:

* At a coarse grain, latency can refer to the period from a user request to the satisfaction of that request.
* At a fine grain, latency can refer to the period from placing a message on a network to the receipt of that message.

Latency can also be measured at either the infrastructure or the application level. Measuring latency across different physical computers is more problematic because of the difficulty of synchronizing clocks.

Latency is cumulative in the sense that the latency of responding to a user request is the sum of the latency of all of the activities that occur until the request is satisfied, adjusted for parallelism. It is useful when diagnosing the cause of a latency problem to know the latency of the various subactivities performed in the satisfaction of the original request. [p131]

##### **Throughput**

Throughput is the number of operations of a particular type in a unit time. Although throughput could refer to infrastructure activities (e.g., the number of disk reads per minute), it is more commonly used at the application level. For example, the number of transactions per second is a common reporting measure.

<u>Throughput provides a system-wide measure involving all of the users, whereas latency has a single-user or client focus.</u> High throughput may or may not be related to low latency. The relation will depend on the number of users and their pattern of use.

A reduction in throughput is not, by itself, a problem. The reduction in throughput may be caused by a reduction in the number of users. Problems are indicated through the coupling of throughput and user numbers.

##### **Utilization**

#### Capacity Planning

#### User Interaction

#### Intrusion Detection

### How to Monitor

### When to Change the Monitoring Configuration

### Interpreting Monitoring Data

### Challenges

### Tools
