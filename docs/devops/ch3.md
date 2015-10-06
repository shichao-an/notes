### **Chapter 3. Operations**

### Introduction

[p47]

### Operations Services

An operations service can be the provisioning of hardware, the provisioning of software, or supporting various IT functions. Services provided by operations also include the specification and monitoring of [service level agreements](https://en.wikipedia.org/wiki/Service-level_agreement) (SLAs), capacity planning, business continuity, and information security.

#### Provisioning of Hardware

#### Provisioning of Software

#### IT Functions

Ops supports a variety of functions. These include:

* **Service desk operations**. The service desk staff is responsible for handling all incidents and service requests and acts as first-level support for all problems.
* **Technology experts**. Ops typically has experts for networks, information security, storage, databases, internal servers, web servers and applications, and telephony.
* **Day-to-day provisioning of IT services**. These include periodic and repetitive maintenance operations, monitoring, backup, and facilities management.

#### Service Level Agreements

[p50]

An organization has a variety of SLAs with external providers of services. For example, a cloud provider will guarantee a certain level of availability. Ops traditionally is responsible for monitoring and ensuring that the SLAs are adhered to.

#### Capacity Planning

[p51]

Ops is responsible for ensuring that adequate computational resources are available for the organization.

#### Business Continuity and Security

In the event a disaster occurs, an organization needs to keep vital services operational so that both internal and external customers can continue to do their business. Two key parameters enable an organization to perform a cost/benefit analysis of various alternatives to maintain business continuity:

* **Recovery point objective** (RPO). When a disaster occurs, what is the maximum period for which data loss is tolerable? If backups are taken every hour then the RPO would be 1 hour, since the data that would be lost is that which accumulated since the last backup.
* **Recovery time objective** (RTO). When a disaster occurs, what is the maximum tolerable period for service to be unavailable? For instance, if a recovery solution takes 10 minutes to access the backup in a separate datacenter and another 5 minutes to instantiate new servers using the backed-up data, the RTO is 15 minutes.

The two values are independent since some loss of data may be tolerable, but being without service is not. It is also possible that being without service is tolerable but losing data is not.

The following figure (Figure 3.2) shows three alternative backup strategies with different RPOs. [p52]

[![FIGURE 3.2 Database backup strategies. (a) An independent agent performing the backup. (b) The database management system performing the backup.  (c) The database management system performing the backup and logging all transactions. [Notation: Architecture]](figure_3.2_600.png)](figure_3.2.png "FIGURE 3.2 Database backup strategies. (a) An independent agent performing the backup. (b) The database management system performing the backup.  (c) The database management system performing the backup and logging all transactions. [Notation: Architecture]")

1. Figure 3.2a shows an external agent (the backup process) copying the database periodically. No application support is required but the backup process should copy a consistent version of the database, which means no updates are currently being applied. If the backup process is external to the database management system, then transactions may be in process and so the activation of the backup should be carefully performed. In this case, the RPO is the period between two backups. That is, if a disaster occurs just prior to the backup process being activated, all changes in the period from the last backup will be lost.
2. Figure 3.2b shows an alternative without an external agent. In this case, the database management system creates a copy periodically. The difference between 3.2a and 3.2b is that in 3.2b, guaranteeing consistency is done by the database management system, whereas in 3.2a, consistency is guaranteed by some mechanism that governs the activation of the backup process.  If the database is a relational database management system (RDBMS) offering some level of replication (i.e., a transaction only completes a commit when the replica database has executed the transaction as well), then transactions lost in the event of a disaster will be those not yet committed to the replicating database. The cost, however, is increased overhead per transaction.
3. Figure 3.2c modifies Figure 3.2b by having the database management system log every write. Then the data can be re-created by beginning with the backup database and replaying the entries in the log. If both the log and the backup database are available during recovery, the RPO is 0 since all data is either in the backup database or in the log. The protocol for committing a transaction to the production database is that no transaction is committed until the respective log entry has been written. It is possible in this scheme that some transactions have not been completed, but no data from a completed transaction will be lost. This scheme is used by high-reliability relational database management systems. It is also used by distributed file systems such as Hadoop Distributed File System (HDFS).
