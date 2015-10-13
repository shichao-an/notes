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

Utilization is the relative amount of use of a resource and is typically measured by inserting probes on the resources of interest. For example, the CPU utilization may be 80%. High utilization can be used as either of the following:

* An early warning indicator of problems with latency or throughput,
* A diagnostic tool used to find the cause of problems with latency or throughput.

The resources can either be at the infrastructure or application level:

* Hard resources such as CPU, memory, disk, or network are best measured by the infrastructure.
* Soft resources such as queues or thread pools can be measured either by the application or the infrastructure depending on where the resource lives.

Making sense of utilization frequently requires attributing usage to activities or applications. For example, *app1* is using 20% of the CPU, disk compression is using 30%, and so on. Thus, connecting the measurements with applications or activities is an important portion of data collection.

#### Capacity Planning

There two types of capacity planning:

* **Long-term capacity planning** involves humans and has a time frame on the order of days,
* **Short-term capacity planning** is performed automatically and has a time frame on the order of minutes.

##### **Long-Term Capacity Planning**

Long-term capacity planning is intended to match hardware needs (whether real or virtualized) with workload requirements.

* In a physical datacenter, it involves ordering hardware.
* In a virtualized public datacenter, it involves deciding on the number and characteristics of the virtual resources that are to be allocated.

In both cases, the input to the capacity planning process is a characterization of the current workload gathered from monitoring data and a projection of the future workload based on business considerations and the current workload. <u>Based on the future workload, the desired throughput and latency for the future workload, and the costs of various provisioning options, the organization will decide on one option and provide the budget for it.</u>

##### **Short-Term Capacity Planning**

In the cloud, short-term capacity planning means creating a new virtual machine (VM) for an application or deleting an existing VM.

* A common method of making and executing these decisions (creating and deleting VMs) is based on monitoring information collected by the infrastructure.
    * [Chapter 4](ch4.md) discusses various options for controlling the allocation of VM instances based on the current load.
    * Monitoring the usage of the current VM instances was an important portion of each option.
* Monitoring data is also used for billing in public clouds. In order to charge for use, the use must be determined, and this is accomplished through monitoring by the cloud provider.

#### User Interaction

User satisfaction is an important element of a business. It depends on four elements that can be monitored:

1. **The latency of a user request.** Users expect decent response times. Depending on the application, seemingly trivial variations in response can have a large impact.
2. **The reliability of the system with which the user is interacting.** Failure and failure detection are discussed earlier.
3. **The effect of a particular business offering or user interface modification.** A/B testing is discussed in [Chapters 5](ch5.md) and [Chapter 6](ch6.md). The measurements collected from A/B testing must be meaningful for the goal of the test, and the data must be associated with variant A or B of the system.
4. **The organization’s particular set of metrics.** These metrics should be important indicators either of the following:
    * User satisfaction,
    * The effectiveness of the organization’s computer-based services.

There are generally two types of user interaction monitoring.

1. **Real user monitoring** (RUM). RUM essentially records all user interactions with an application.
    * RUM data is used to assess the real service level a user experiences and whether server side changes are being propagated to users correctly.
    * RUM is usually passive in terms of not affecting the application payload without exerting load or changing the server-side application.
2. **Synthetic monitoring**. It is similar to developers performing stress testing on an application.
    * Expected user behaviors are scripted either using some emulation system or using actual client software (such as a browser). However, the goal is often not to stress test with heavy loads, but to monitor the user experience.
    * Synthetic monitoring allows you to monitor user experience in a systematic and repeatable fashion, not dependent on how users are using the system right now.
    * Synthetic monitoring may be a portion of the automated user acceptance tests discussed in [Chapter 5](ch5.md).

#### Intrusion Detection

Intruders can break into a system by subverting an application (for example, through incorrect authorization or a man-in-the-middle attack). Applications can monitor users and their activities to determine whether the activities are consistent with the users’ role in the organization or their past behavior.

For instance, if user John has a mobile phone using the application, and the phone is currently in Australia, any log-in attempts from, say, Nigeria should be seen as suspicious.

##### **Intrusion detector** *

An **intrusion detector** is a software application that monitors network traffic by looking for abnormalities. These abnormalities can be caused by:

* Attempts to compromise a system by unauthorized users,
* Violations of an organization’s security policies.

Intrusion detectors use a variety of different techniques to identify attacks. They frequently use historical data from an organization’s network to understand what is normal. They also use libraries that contain the network traffic patterns observed during various attacks. Current traffic on a network is compared to the expected (from an organization’s history) and the abnormal (from the attack history) to decide whether an attack is currently under way.

Intrusion detectors can also monitor traffic to determine whether an organization’s security policies are being violated without malicious intent.

Intrusion detectors generate alerts and alarms as discussed in [Section 7.5](#interpreting-monitoring-data). Problems with false positives and false negatives exist with intrusion detectors as they do with all monitoring systems.

### How to Monitor

Monitoring systems interact with the elements being monitored, as shown in the figure below.

[![Figure 7.1 Monitoring system interacting with the elements being monitored [Notation: Architecture]](figure_7.1.png)](figure_7.1.png "Figure 7.1 Monitoring system interacting with the elements being monitored [Notation: Architecture]")

The system to be monitored can be as broad as a collection of independent applications or services, or as narrow as a single application:

1. **Agentless monitoring**. If the system is actively contributing to the data being monitored (the arrow labeled "agentless") then the monitoring is intrusive and affects the system design.
2. **Agent-based monitoring**. If the system is not actively contributing to the data being monitored (the arrow labeled "agent-based") then the monitoring is nonintrusive and does not affect the system design.
3. **Health checks**. A third source of data is indicted by the arrow labeled "health checks". External systems can also monitor system or application-level states through health checks, performance-related requests, or transaction monitoring

The data collected either through agents or through agentless means is eventually sent to a central repository ("Monitoring data storage" in [Figure 7.1](figure_7.1.png)). The central repository is typically distributed (logically but not physically central). Each step from the initial collection to the central repository can do filtering and aggregation.

The considerations in determining the amount of filtering and aggregation are:

* The volume of data being generated,
* The potential failure of local nodes,
* The granularity of the necessary communication.

Retrieving the data from local nodes is important because the local node may fail and the data become unavailable. Sending all of the data directly to a central repository may introduce congestion to the network. Thus, selecting the intermediate steps from the local nodes to the central repository and the filtering and aggregation done at each step are important architectural decisions when setting up a monitoring framework.

Once monitoring data is collected, you can do many things:

* Alarms can be configured to trigger alerts that notify operators or other systems about major state changes.
* Graphing and dashboards can be used to visualize system state changes for human operators.
* A monitoring system also allows operators to drill down into detailed monitoring data and logs, which is important for error diagnosis, root cause analysis, and deciding on the best reaction to a problem.

The traditional view of the monitoring system (as discussed so far) is increasingly being challenged by new interactions between the monitoring system and other systems, which are shown outside of the dotted areas in [Figure 7.1](figure_7.1.png).

You can perform stream processing and (big) data analytics on monitoring data streams and historical data. Not only can you gain insights into system characteristics using system-level monitoring data, you may also gain insights into user behaviors and intentions using application- and user-level monitoring data.

Because of these growing different uses of monitoring data, many companies are starting to use a unified log and metrics-centric publish-subscribe architecture for both the monitoring system and the overall application system. More and more types of data, including nontraditional log and metrics data, are being put into a unified storage, where various other systems (whether monitoring-related or not) can subscribe to the data of interest. Several implications of the unified view are:

* It significantly reduces the coupling of any two systems. <u>Systems interact with the unified log in a publish-subscribe fashion that makes publishers ignorant of the specific identity of the subscriber and vice versa.</u>
* It simplifies the integration of multiple sources of data. <u>Using a central log store allows data to be correlated based on attributes such as time stamps rather than their source.</u> [p136]

The line between the monitoring system and the system to be monitored is getting blurred when application and user monitoring data are treated the same as system-level monitoring data: data from anywhere and at any level could contribute to insights about both systems and users.

The following sections discuss the method of retrieving monitoring data, monitoring operations, and data collection and storage:

#### Agent-Based and Agentless Monitoring

In some situations, the system to be monitored already has internal monitoring facilities that can be accessed through a defined protocol. For example:

* The [Simple Network Management Protocol](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol) (SNMP) is a common mechanism for gathering metrics from servers and network equipment. It is especially useful on network equipment because that equipment often comes as a closed system and you cannot install monitoring agents.
* You can use protocols like Secure Shell (SSH) to remotely access a system and retrieve available data.
* [Application Response Measurement](https://en.wikipedia.org/wiki/Application_Response_Measurement) (ARM) is an industry standard that provides ways for an application to trigger actions such as requesting an external ARMsupported system to start or stop tracking a transaction and correlating times spent in different systems for a single transaction.

 Agentless monitoring is particularly useful when you cannot install agents, and it can simplify the deployment of your monitoring system.

The agent-based and agentless approaches both have their strengths and weaknesses:

* The agentless approach is better in terms of deployment and maintenance effort. However, it is less secure if the collection repository is outside of your network because more ports need to be opened and firewall rules relaxed to allow different layers of a system to communicate its data to the external world.
* In contrast, an agent on a host can communicate with the OS and applications locally and send all collected information over a single channel. This also allows an agent-based approach to optimize network traffic and processing overhead.

#### Monitoring Operation Activities

#### Collection and Storage

### When to Change the Monitoring Configuration

### Interpreting Monitoring Data

### Challenges

### Tools
