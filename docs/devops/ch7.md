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
* The cloud environment introduces different levels from application programming interface (API) calls to VM resource usage. Choosing between a top-down approach and a bottom-up approach for different scenarios and balancing the tradeoffs is not easy.
* Monitoring requires attention to more moving parts.
* Managing logs becomes a challenge in large-scale distributed systems.

### What to Monitor

### How to Monitor

### When to Change the Monitoring Configuration

### Interpreting Monitoring Data

### Challenges

### Tools
