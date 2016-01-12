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

* **Agentless**. <u>The **agentless** approach is better in terms of deployment and maintenance effort.</u> However, it is less secure if the collection repository is outside of your network because more ports need to be opened and firewall rules relaxed to allow different layers of a system to communicate its data to the external world.
* **Agent-based**. In contrast, an **agent** on a host can communicate with the OS and applications locally and send all collected information over a single channel. <u>This also allows an agent-based approach to optimize network traffic and processing overhead.</u>
* **External**. In addition to collecting monitoring data from inside a system, you can collect information from an external viewpoint. You can set up **health checks** to periodically check a system or conduct performance monitoring from an external user’s point of view

Questions to be considered when designing a system include:

* Where does this information come from?
* How does this information fit into the application and monitoring architecture?
* What are the quality implications?

#### Monitoring Operation Activities

Some operations tools (such as Chef) monitor resources such as configuration settings to determine whether they conform to prespecified settings. We also mentioned monitoring resource specification files to identify changes. Both of these types of monitoring are best done by agents that periodically sample the actual values and the files that specify those values.

Treating infrastructure-as-code implies that infrastructure should contribute monitoring information in the same fashion as other applications, which can be through any of the means discussed: agents, agentless, or external.

[Chapter 14](ch14.md) discusses how to perform fine-grained monitoring of the behavior of operations tools and scripts. This can include assertions over monitoring data. <u>For instance, during a rolling upgrade a number of VMs are taken out of service to be replaced with VMs running a newer version of the application. Then you can expect the average CPU utilization of the remaining machines to increase by a certain factor.</u>

#### Collection and Storage

The core of monitoring is recoding and analyzing time series data (a sequence of time-stamped data points):

* These data points are acquired at successive intervals in time and represent certain aspects of states and state changes.
* The system being monitored will generate time-stamped event notifications at various levels of severity. These notifications are typically output as logs.

The monitoring system can conduct direct measurement or collect existing data, statistics, or logs and then turn them into metrics (with time and space). The data is then transferred to a repository. The incoming data streams need to be processed into a time series and stored in a time series database.

Three key challenges are: [p138]

* **Collating related items by time.** Time stamps in a distributed system are not going to be consistent.
    * Different nodes in a single cluster may differ in their clocks by several microseconds.
    * Different nodes across multiple clusters may differ by much more.
* **Collating related items by context.**
* **The volume of monitoring data.** You may need a retention policy to cope with the volume of data collected.

The [Round-Robin Database](https://en.wikipedia.org/wiki/RRDtool) (RRD) is a popular time series database, which is designed for storing and displaying time series data with good retention policy configuration capabilities. Big data storage and processing solutions are increasingly used for monitoring data. You can treat your monitoring data as data streams feeding into streaming systems for real-time processing, combined with (big) historical data. You can load all your data into big data storage systems such as Hadoop Distributed File System (HDFS) or archive it in relatively inexpensive online storage systems such as [Amazon Glacier](https://aws.amazon.com/glacier/).

### When to Change the Monitoring Configuration

Monitoring is either time-based or event-based. Timing frequency and generation of events should all be configurable and changed in response to events occurring in the datacenter.

Some examples of events that could change the monitoring configuration are:

* **An alert.** One consequence of an alert could be that the frequency of sampling is increased.  The frequency could be decreased if the alert does not turn into an alarm.
* **Deployment.** Any of the deployment scenarios can trigger changes to monitoring:
    * Canary deployment. The new versions under test should be monitored more closely
    * Rolling upgrade. Closer monitoring will help detect the occurrence of a race condition more quickly.
    * Feature activation or deactivation. Feature changes should trigger changes in the monitoring configuration.
* **Changes to any infrastructure software including DevOps tools.**
* **Changes to any configuration parameters.** One of the major sources of errors in modern distributed systems is incorrect parameters.

### Interpreting Monitoring Data

Assume that the monitoring data (both time-based and event-based) has been collected in a central repository. This data is being added and examined continually, by both other systems and humans.

#### Logs

A log is a time series of events. Records are typically appended to the end of the log. Logs usually record the actions performed that may result in a state change of the system.

[p140]

Logs are used:

* During operations to detect and diagnose problems.
* During debugging to detect errors.
* During post-problem forensics to understand the sequence that led to a particular problem.

Some general rules about writing logs are:

* Logs should have a consistent format.
* Logs should include an explanation for why this particular log message was produced.
* Log entries should include context information. Besides date and time, it also includes information to support tracking the log entry such as:
    * Source of the log entry within the code
    * Process ID for the process executing when the log entry was produced
    * Request ID for the request that caused that process to execute this log producer
    * VM ID for the VM that produced this message
* Logs should provide screening information. Log messages are collected in a repository that is accessed through queries. Severity levels are an example of screening information, alert levels are another.

#### Graphing and Display

Once you have all relevant data, it is useful to visualize it:

* Some monitoring systems have strong visualization capabilities embedded.
* There are also specialized systems just for visualization and querying, such as [Graphite](https://github.com/graphite-project/graphite-web), which support real-time graphing of large amounts of data.

You can set up a dashboard showing important real-time aspects of your system and its components at an aggregated level. You can also dive into the details interactively or navigate through history when you detect an issue. An experienced operator will use visual patterns of graphs to discern problems.

[p141]

#### Alarms and Alerts

Monitoring systems inform the operator of significant events. This information can be in the form of either an alarm or an alert:

* **Alerts** are raised for purposes of informing and may be in advance of an alarm (e.g., the datacenter temperature is rising);
* **Alarms** require action by the operator or another system (e.g., the datacenter is on fire).

Alarms and alerts can be triggered by any of the following:

* Events (e.g., a particular physical machine is not responding),
* Values crossing a threshold (e.g., the response time for a particular disk is greater than an acceptable value),
* Sophisticated combinations of values and trends.

[p141]

The typical issues are:

* How do you configure your monitoring system to reduce **false positives** (alarms without the necessity for action) and **false negatives** (the necessity for action without an alarm being raised)?
* How do you configure your monitoring system so that the alerts provide necessary information to diagnose an alarm?

A problem for operators is receiving false positive alarms or a flood of alerts from different channels about the same event. Under such conditions, operators will quickly get "alert fatigue" and start ignoring alerts or simply turn some of them off. On the other hand, if you try to reduce false positives, you may risk missing important events, which increases false negatives.

If your alarms are very specific in their triggering conditions, you may be informed about some subtle errors early in their occurrence. However, you may risk rendering your alarms less effective when the system undergoes changes over time, or when the system momentarily exhibits interference of legitimate but previously unknown operations. [p142]

Some general rules to improve the usefulness of alerts and alarms are:

* Introduce context to your alarms.
    * This could be as simple as disabling certain alerts during specific times or actions; for example, when replacing a physical computer it does not make sense to raise alarms about the computer’s health.
    * Other more complex contexts could be related to external events or interfering operations.
* <u>Alarms can not only go off if something happens, they can also be set to go off if an expected event did not happen</u>. This helps with drills and testing of your alarms since you can set an alarm to go off when an event that you know is not going to happen does not, in fact, happen.
* Aggregate different alerts that are likely referring to the same events.
* Set clear severity levels and urgency levels so people or systems receiving the alerts can act accordingly.

#### Diagnosis and Reaction

Operators often use monitoring systems to diagnose the causes and observe the progress of mitigation and recovery. However, monitoring systems are not designed for interactive or automated diagnosis. Thus, operators, in ad hoc ways, will try to correlate events, dive into details and execute queries, and examine logs. Concurrently, they manually trigger more diagnostic tests and recovery actions (such as restarting processes or isolating problematic components) and observe their effects from the monitoring system.

The essence of the skill of a reliability engineer is the ability to diagnose a problem in the presence of uncertainty. Once the problem has been diagnosed, frequently the reaction is clear although, at times, possible reactions have different business consequences. [p142-143]

#### Monitoring DevOps Processes

DevOps processes should be monitored so that they can be improved and problems can be detected.

Five things that are important to monitor:

1. A business metric
2. Cycle time
3. Mean time to detect errors
4. Mean time to report errors
5. Amount of scrap (rework)

### Challenges

#### Challenge 1: Monitoring Under Continuous Changes

##### **Deviation from normal behavior** *

In operation, a deviation from normal behavior is a problem. Normal behavior assumes the system is relatively stable over time. However, in a large-scale complex environment, changes are the norm. Besides varying workloads or dynamic aspects of your application, which are often well anticipated, the new challenges come from both of:

* Cloud elasticity makes infrastructure resources more volatile.
* Automated DevOps operations trigger various sporadic operations (such as upgrade, reconfiguration, or backups).
    * Sporadic operations and continuous deployment and deployment practices make software changes more frequent.

Deploying a new version into production multiple times a day is becoming a common practice:

* Each deployment is a change to the system and may impact monitoring.
* These changes may be happening simultaneously in different portions of an application or the infrastructure.

##### **How to use the past monitoring data to do performance management, capacity planning, anomaly detection, and error diagnosis for the new system?** *

In practice, operators may turn off monitoring during scheduled maintenance and upgrades as a work-around to reduce false positive alerts triggered by those changes. However, this can lead to no monitoring (e.g. flying blind).

The following techniques can solve this:

1. Carefully identify the non-changing portions of the data.
    * For example, use dimensionless data (i.e., ratios). You may find that although individual variables change frequently, the ratio of two variables is relatively constant.
2. Focus monitoring on things that have changed.
3. Compare performance of the canaries with historical performance. (As discussed in [Chapter 6](ch6.md), canary testing is a way of monitoring a small rollout of a new system for issues in production.) Changes that cannot be rationalized because of feature changes may indicate problems.

##### **Specification of monitoring parameters** *

The specification of monitoring parameters is another challenge related to monitoring under continuous changes [p144].

The complexity of setting up and maintaining a monitoring system consists of:

* Specifying what needs to be monitored
* Setting thresholds
* Defining the alerting logic

Continuous changes in the system infrastructure and the system itself complicate the setting of monitoring parameters. Your monitoring may need to be adjusted for  variance on the infrastructure side. [p144]

As a consequence, it makes sense to automate the configuration of alarms, alerts, and thresholds as much as possible. The monitoring configuration process is just another DevOps process to be automated:

* When you provision a new server, registering this server in the monitoring system automatically.
* When a server is terminated, a de-registration process should happen automatically.

#### Challenge 2: Bottom-Up vs. Top-Down and Monitoring in the Cloud

#### Challenge 3: Monitoring a Microservice Architecture

#### Challenge 4: Dealing with Large Volumes of Distributed (Log) Data

### Tools
