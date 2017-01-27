### **Chapter 1. Reliable, Scalable and Maintainable Applications**

Many applications today are **data-intensive**, as opposed to **compute-intensive**. Raw CPU power is rarely a limiting factor for these applications. Bigger problems are usually the amount of data, the complexity of data, and the speed at which it is changing.

A data-intensive application is typically built from standard building blocks which provide common functionality, such as:

* Store data so that they can be found later (*databases*)
* Remember the result of an expensive operation, to speed up reads (*caches*)
* Allow users to search data by keyword or filter it in various ways (*search indexes*)
* Send a message to another process, to be handled asynchronously (*stream processing*)
* Periodically crunch a large amount of accumulated data (*batch processing*)

When building an application, most engineers wouldn't write a new data storage engine from scratch, because databases are a perfectly good tool for the job. However, there are many database systems with different characteristics, because different applications have different requirements. When building an application, we still need to figure out which tools and which approaches are the most appropriate for the task at hand. Sometimes it can be hard to combine several tools when you need to do something that a single tool cannot do alone.

This chapter starts by exploring the fundamentals of what we are trying to achieve: reliable, scalable and maintainable data systems and then clarify what those things mean, outline some ways of thinking about them, and go over the basics need for later chapters.

### Thinking About Data Systems

Typically, databases, queues, caches, etc. are very different categories of tools. Although a database and a message queue have some superficial similarity (both store data for some time), they have very different access patterns, which means different performance characteristics, and thus very different implementations.

Why do we label them under an umbrella term like *data systems*?

First, many new tools for data storage and processing have emerged in recent years, which are optimized for a variety of different use cases, and they no longer fit into traditional categories. For example, there are data stores that are also used as message queues (Redis), and there are message queues with database-like durability guarantees (Kafka). The boundaries between the categories are becoming blurred.

Second, increasingly many applications now have such demanding or wide-ranging requirements that a single tool can no longer meet all of its data processing and storage needs. Instead, the work is broken down into tasks that can be performed efficiently on a single tool, and those different tools are stitched together using application code.

For example, if you have an application-managed caching layer (using memcached or similar), or a full-text search server separate from your main database (such as Elasticsearch or Solr), it is normally the application code's responsibility to keep those caches and indexes in sync with the main database. The following figure is one possible architecture (which will be detailed in later chapters):

[![Figure 1-1. One possible architecture for a data system that combines several components.](figure_1-1_600.png)](figure_1-1.png "Figure 1-1. One possible architecture for a data system that combines several components.")

When you combine several tools in order to provide a service, the service's interface or API usually hides those implementation details from clients. You have essentially created a new, special-purpose data system from smaller, general-purpose components. Your composite data system may provide certain guarantees, e.g. that the cache will be correctly invalidated or updated on writes, so that outside clients see consistent results.

If you are designing a data system or service, a lot of tricky questions arise:

* How do you ensure that the data remains correct and complete, even when things go wrong internally?
* How do you provide consistently good performance to clients, even when parts of your system are degraded?
* How do you scale to handle an increase in load?
* What does a good API for the service look like?

There are many factors that may influence the design of a data system, including:

* Skills and experience of the people involved
* Legacy system dependencies
* Time‐scale for delivery
* Organization's tolerance of different kinds of risk
* Regulatory constraints

This book focuses on three concerns that are important in most software systems:

* **Reliability**. The system should continue to work correctly (performing the correct function at the desired performance) even in the face of adversity (hardware or software faults, and even human error). See [Reliability](#reliability).
* **Scalability**. As the system grows (in data volume, traffic volume or complexity), there should be reasonable ways of dealing with that growth. See [Scalability](#scalability).
* **Maintainability**. Over time, many different people will work on the system (engineering and operations, both maintaining current behavior and adapting the system to new use cases), and they should all be able to work on it productively. See [Maintainability](#maintainability).
