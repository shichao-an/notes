### **Chatper 4. Encoding and Evolution**

Applications change over time:

* Features are added or modified as new products are launched,
* User requirements become better understood, or,
* Business circumstances change.

[Chapter 1](ch1.md) introduced the idea of evolvability: we should aim to build systems that make it easy to adapt to change (see [Evolvability: Making Change Easy](ch1.md#evolvability-making-change-easy)).

[p111]

A change to an application's features also requires a change to data that it stores. The data models in [Chapter 2](ch2.md) have different ways of coping with such change:

* Relational databases generally assume that all data in the database conforms to one schema: although that schema can be changed (through schema migrations; i.e., `ALTER` statements), there is exactly one schema in force at any one point in time.
* By contrast, schema-on-read ("schemaless") databases don't enforce a schema, so the database can contain a mixture of older and newer data formats written at different times (see [Schema flexibility in the document model](ch2.md#schema-flexibility-in-the-document-model)).

When a data format or schema changes, a corresponding change to application code often needs to happen However, in a large application, code changes often cannot happen instantaneously:

* With server-side applications, you needs to perform a [*rolling upgrade*](https://en.wikipedia.org/wiki/Rolling_release) (also known as a *staged rollout*), deploying the new version to a few nodes at a time, checking whether the new version is running smoothly, and gradually working your way through all the nodes. This allows new versions to be deployed without service downtime, and thus encourages more frequent releases and better evolvability.
* With client-side applications you're at the mercy of the user, who may not install the update for some time.

This means that old and new versions of the code, and old and new data formats, may potentially all coexist in the system at the same time. In order for the system to continue running smoothly, we need to maintain compatibility in both directions:

* **Backward compatibility**. Newer code can read data that was written by older code. This is normally not hard to achieve: as author of the newer code, you know the format of data written by older code, and so you can explicitly handle it
(if necessary by simply keeping the old code to read the old data).
* **Forward compatibility**. Older code can read data that was written by newer code. This can be trickier, because it requires older code to ignore additions made by a newer version of the code

This chapter discusses the following topics:

* Several formats for encoding data, including JSON, XML, Protocol Buffers, Thrift, and Avro
* In particular, how those formats handle schema changes and how they support systems where old and new data and code need to coexist.
* How those formats are used for data storage and for communication: in web services, Representational State Transfer (REST), and remote procedure calls (RPC), as well as message-passing systems such as actors and message queues.
