### **Chatper 2. Data Models and Query Languages**

Data models are perhaps the most important part of developing software, because they have such a profound effect: not only on how the software is written, but also on how we *think about the problem* that we are solving.

Most applications are built by layering one data model on top of another. For each layer, the key question is: how is it *represented* in terms of the next-lower layer? For example:

1. As an application developer, you look at the real world and model it in terms of objects or data structures, and APIs that manipulate those data structures. Those structures are often specific to your application.
2. When you want to store those data structures, you express them in terms of a general-purpose data model, such as JSON or XML documents, tables in a relational database, or a graph model.
3. The engineers who built your database software decided on a way of representing that JSON/XML/relational/graph data in terms of bytes in memory, on disk, or on a network. The representation may allow the data to be queried, searched, manipulated, and processed in various ways.
4. On lower levels, hardware engineers have figured out how to represent bytes in terms of electrical currents, pulses of light, magnetic fields, and more.

In a complex application there may be more intermediary levels, such as APIs built upon APIs, but the basic idea is still the same: each layer hides the complexity of the layers below it by providing a clean data model. These abstractions allow different groups (e.g. database engineers and application developers) of people to work together effectively.

There are many different kinds of data models, and every data model embodies assumptions about how it is going to be used. [p28]

It can take a lot of effort to master just one data model. Building software is hard enough, even when working with just one data model and without worrying about its inner workings. But since the data model has such a profound effect on what the software above it can and can't do, it's important to choose one that is appropriate to the application.

This chapter covers a range of general-purpose data models for data storage and querying (point 2 in the preceding list), in particular, comparing the relational model, the document model, and a few graph-based data models. We will also look at various query languages and compare their use cases. In [Chapter 3](ch3.md) we will discuss how storage engines work; that is, how these data models are actually implemented (point 3 in the list).

### Relational Model Versus Document Model

The best-known data model today is probably that of SQL, based on the [relational model](https://en.wikipedia.org/wiki/Relational_model) proposed by [Edgar Codd](https://en.wikipedia.org/wiki/Edgar_F._Codd) in 1970: data is organized into *relations* (called *tables* in SQL), where each relation is an unordered collection of *tuples* (*rows* in SQL).

The relational model was a theoretical proposal, and many people at the time doubted whether it could be implemented efficiently. However, by the mid-1980s, [relational database management systems](https://en.wikipedia.org/wiki/Relational_database_management_system) (RDBMSes) and SQL had become the tools of choice for most people who needed to store and query data with some kind of regular structure. The dominance of relational databases has lasted around 25‒30 years, an eternity in computing history.

The roots of relational databases lie in *business data processing*, which was performed on mainframe computers in the 1960s and 1970s. The use cases appear mundane from today's perspective:

* Transaction processing: entering sales or banking transactions, airline reservations, stock-keeping in warehouse.
* Batch processing: customer invoicing, payroll, reporting.

Other databases at that time forced application developers to think a lot about the internal representation of the data in the database. The goal of the relational model was to hide that implementation detail behind a cleaner interface.

Over the years, there have been many competing approaches to data storage and querying:

* The network model and the hierarchical model were the main alternatives in the 1970s and early 1980s, but the relational model came to dominate them.
* Object databases came and went again in the late 1980s and early 1990s.
* XML databases appeared in the early 2000s, but have only seen niche adoption.

Each competitor to the relational model generated a lot of hype in its time, but it never lasted.

As computers became vastly more powerful and networked, they started being used for increasingly diverse purposes. Relational databases turned out to generalize very well, beyond their original scope of business data processing, to a broad variety of use cases. Much of what you see on the web today is still powered by relational databases, be it online publishing, discussion, social networking, ecommerce, games, software-as-a-service productivity applications, etc.

#### The Birth of NoSQL

Now, in the 2010s, NoSQL is the latest attempt to overthrow the relational model's dominance. The name "NoSQL" is unfortunate, since it doesn't actually refer to any particular technology. [p29] A number of interesting database systems are now associated with the NoSQL, and it has been retroactively reinterpreted as *Not Only SQL*.

There are several driving forces behind the adoption of NoSQL databases:

* A need for greater scalability than relational databases can easily achieve, including very large datasets or very high write throughput
* A widespread preference for free and open source software over commercial database products
* Specialized query operations that are not well supported by the relational model
* Frustration with the restrictiveness of relational schemas, and a desire for a more dynamic and expressive data model

Different applications have different requirements. It therefore seems likely that in the foreseeable future, relational databases will continue to be used alongside a broad variety of nonrelational datastores—an idea that is sometimes called [*polyglot persistence*](https://en.wikipedia.org/wiki/Polyglot_persistence).

#### The Object-Relational Mismatch

Most application development today is done in object-oriented programming languages, which leads to a common criticism of the SQL data model: if data is stored in relational tables, an awkward translation layer is required between the objects in the application code and the database model of tables, rows, and columns. The disconnect between the models is sometimes called an [*impedance mismatch*](https://en.wikipedia.org/wiki/Object-relational_impedance_mismatch).

[Object-relational mapping](https://en.wikipedia.org/wiki/Object-relational_mapping) (ORM) frameworks like ActiveRecord and Hibernate reduce the amount of boilerplate code required for this translation layer, but they can't completely hide the differences between the two models.

For example, the following figure illustrates how a LinkedIn profile could be
expressed in a relational schema.

[![Figure 2-1. Representing a LinkedIn profile using a relational schema. ](figure_2-1_600.png)](figure_2-1.png "Figure 2-1. Representing a LinkedIn profile using a relational schema.")

The profile as a whole can be identified by a unique identifier, `user_id`. Fields like `first_name` and `last_name` appear exactly once per user, so they can be modeled as columns on the `users` table. However, most people have had more than one job in their career (positions), and people may have varying numbers of periods of education and any number of pieces of contact information.  There is a one-to-many relationship from the user to these items, which can be represented in various ways:

* In the traditional SQL model (prior to [SQL:1999](https://en.wikipedia.org/wiki/SQL:1999)), the most common normalized representation is to put positions, education, and contact information in separate tables, with a foreign key reference to the users table, as in [Figure 2-1](figure_2-1.png).
* Later versions of the SQL standard added support for structured datatypes and XML data; this allowed multi-valued data to be stored within a single row, with support for querying and indexing inside those documents. These features are supported to varying degrees by Oracle, IBM DB2, MS SQL Server, and PostgreSQL. A JSON datatype is also supported by several databases, including IBM DB2, MySQL, and PostgreSQL.
* A third option is to encode jobs, education, and contact info as a JSON or XML document, store it on a text column in the database, and let the application interpret its structure and content. In this setup, you typically cannot use the database to query for values inside that encoded column.

For a data structure like a résumé, which is mostly a self-contained document, a JSON representation can be quite appropriate: see the following example 2-1. JSON has the appeal of being much simpler than XML. Document-oriented databases like MongoDB, RethinkDB, CouchDB, and Espresso support this data model.

<small>Example 2-1. Representing a LinkedIn profile as a JSON document</small>

```json
  "user_id": 251,
  "first_name": "Bill",
  "last_name": "Gates",
  "summary": "Co-chair of the Bill & Melinda Gates... Active blogger.",
  "region_id": "us:91",
  "industry_id": 131,
  "photo_url": "/p/7/000/253/05b/308dd6e.jpg",
  "positions": [
    {
      "job_title": "Co-chair",
      "organization": "Bill & Melinda Gates Foundation"
    },
    {
      "job_title": "Co-founder, Chairman",
      "organization": "Microsoft"
    }
  ],
  "education": [
    {
      "school_name": "Harvard University",
      "start": 1973,
      "end": 1975
    },
    {
      "school_name": "Lakeside School, Seattle",
      "start": null,
      "end": null
    }
  ],
  "contact_info": {
    "blog": "http://thegatesnotes.com",
    "twitter": "http://twitter.com/BillGates"
  }
}
```

Some think that the JSON model reduces the impedance mismatch between the application code and the storage layer. However, as we shall see in [Chapter 4](ch4.md), there are also problems with JSON as a data encoding format. The lack of a schema is often cited as an advantage, which will be discussed this in [Schema flexibility in the docu‐ ment model](#schema-flexibility-in-the-document-model).

The JSON representation has better *locality* than the multi-table schema in [Figure 2-1](figure_2-1.png). If you want to fetch a profile in the relational example, you need to either perform multiple queries (query each table by `user_id`) or perform a messy multi-way join between the users table and its subordinate tables. In the JSON representation, all the relevant information is in one place, and one query is sufficient.

The one-to-many relationships from the user profile to the user's positions, educational history, and contact information imply a tree structure in the data, and the JSON representation makes this tree structure explicit (see [Figure 2-2](figure_2-2.png) below).

[![Figure 2-2. One-to-many relationships forming a tree structure.](figure_2-2_600.png)](figure_2-2.png "Figure 2-2. One-to-many relationships forming a tree structure.")

#### Many-to-One and Many-to-Many Relationships

In the previous example, `region_id` and `industry_id` are given as IDs, not as plain-text strings "`Greater Seattle Area`" and "`Philanthropy`". Why?

If the user interface has free-text fields for entering the region and the industry, it makes sense to store them as plain-text strings. But there are advantages to having standardized lists of geographic regions and industries, and letting users choose from a drop-down list or autocompleter:

* Consistent style and spelling across profiles
* Avoiding ambiguity (e.g., if there are several cities with the same name)
* Ease of updating. The name is stored in only one place, so it is easy to update across the board if it ever needs to be changed (e.g., change of a city name due to political events)
* Localization support. When the site is translated into other languages, the stand‐ ardized lists can be localized, so the region and industry can be displayed in the viewer's language
* Better search. For example, a search for philanthropists in the state of Washington can match this profile, because the list of regions can encode the fact that Seattle is in Washington (which is not apparent from the string "`Greater Seattle Area`")

Whether you store an ID or a text string is a question of duplication:

* When you use an ID, the information that is meaningful to humans (such as the word *Philanthropy*) is stored in only one place, and everything that refers to it uses an ID (which only has meaning within the database).
* When you store the text directly, you are duplicating the human-meaningful information in every record that uses it.

<u>The advantage of using an ID is that because it has no meaning to humans, it never needs to change: the ID can remain the same, even if the information it identifies changes.</u> Anything that is meaningful to humans may need to change sometime in the future. If that information is duplicated, all the redundant copies need to be updated. That incurs write overheads, and risks inconsistencies (where some copies of the information are updated but others aren't). Removing such duplication is the key idea behind *normalization* in databases.

Unfortunately, normalizing this data requires [*many-to-one*](https://en.wikipedia.org/wiki/One-to-many_(data_model)) relationships (e.g. many people live in one particular region, many people work in one particular industry), which don't fit nicely into the document model.

* In relational databases, it's normal to refer to rows in other tables by ID, because joins are easy.
* In document databases, joins are not needed for one-to-many tree structures, and support for joins is often weak.

If the database itself does not support joins, you have to emulate a join in application code by making multiple queries to the database. In the example, the lists of regions and industries are probably small and slow-changing enough that the application can simply keep them in memory. But nevertheless, the work of making the join is shifted from the database to the application code.

Even if the initial version of an application fits well in a join-free document model, data has a tendency of becoming more interconnected as features are added to applications. For example, consider some changes we could make to the résumé example:

* Organizations and schools as entities. In the previous description, `organization` and `school_name` are just strings. Perhaps they should be references to entities instead? Then:
    * Each organization, school, or university could have its own web page (with logo, news feed, etc.)
    * Each résumé could link to the organizations and schools that it mentions, and include their logos and other information.
* Recommendations. For instance, you want to add a new feature: one user can write a recommendation for another user. The recommendation is shown on the résumé of the user who was recommended, together with the name and photo of the user making the recom‐ mendation. If the recommender updates their photo, any recommendations they have written need to reflect the new photo. Therefore, the recommendation should have a reference to the author's profile.

[Figure 2-4](figure_2-4.png) below illustrates how these new features require many-to-many relationships. The data within each dotted rectangle can be grouped into one document, but the references to organizations, schools, and other users need to be represented as references, and require joins when queried.

[![Figure 2-4. Extending résumés with many-to-many relationships.](figure_2-4_600.png)](figure_2-4.png "Figure 2-4. Extending résumés with many-to-many relationships.")

#### Are Document Databases Repeating History?

While many-to-many relationships and joins are routinely used in relational databases, document databases and NoSQL reopened the debate on how best to represent such relationships in a database. This debate is much older than NoSQL; in fact, it goes back to the very earliest computerized database systems.

The most popular database for business data processing in the 1970s was IBM's [Information Management System](https://en.wikipedia.org/wiki/IBM_Information_Management_System) (IMS), originally developed for stock-keeping in the Apollo space program and first commercially released in 1968. It is still in use and maintained today, running on [OS/390](https://en.wikipedia.org/wiki/OS/390) on IBM mainframes.

The design of IMS used a fairly simple data model called the [*hierarchical model*](https://en.wikipedia.org/wiki/Hierarchical_database_model), which has some remarkable similarities to the JSON model used by document databases. It represented all data as a tree of records nested within records, much like the JSON structure of [Figure 2-2](figure_2-2.png).

Like document databases, IMS worked well for one-to-many relationships, but it made many-to-many relationships difficult, and it didn't support joins. Developers had to decide whether to duplicate (denormalize) data or to manually resolve references from one record to another. These problems of the 1960s and 1970s were very much like the problems that developers are running into with document databases today.

Various solutions were proposed to solve the limitations of the hierarchical model.  The two most prominent were:

* [*Relational model*](https://en.wikipedia.org/wiki/Relational_model) (which became SQL, and took over the world)
* [*Network model*](https://en.wikipedia.org/wiki/Network_model) (which initially had a large following but eventually faded into obscurity).

The "great debate" between these two camps lasted for much of the 1970s.

##### **The network model**

The network model was standardized by a committee called the [Conference on Data Systems Languages](https://en.wikipedia.org/wiki/CODASYL) (CODASYL) and implemented by several different database vendors; it is also known as the *CODASYL model*.

The CODASYL model was a generalization of the hierarchical model. In the tree structure of the hierarchical model, every record has exactly one parent; in the network model, a record could have multiple parents. For example, there could be one record for the "`Greater Seattle Area`" region, and every user who lived in that region could be linked to it. This allowed many-to-one and many-to-many relationships to be modeled.

The links between records in the network model were not foreign keys, but more like pointers in a programming language (while still being stored on disk). The only way of accessing a record was to follow a path from a root record along these chains of links. This was called an *access path*.

In the simplest case, an access path could be like the traversal of a linked list: start at the head of the list, and look at one record at a time until you find the one you want.  But in a world of many-to-many relationships, several different paths can lead to the same record, and a programmer working with the network model had to keep track of these different access paths in their head.

A query in CODASYL was performed by moving a cursor through the database by iterating over lists of records and following access paths. If a record had multiple parents (i.e., multiple incoming pointers from other records), the application code had to keep track of all the various relationships. Even CODASYL committee members admitted that this was like navigating around an *n*-dimensional data space.

Although manual access path selection was able to make the most efficient use of the very limited hardware capabilities in the 1970s (such as tape drives, whose seeks are extremely slow), the problem was that they made the code for querying and updating the database complicated and inflexible. With both the hierarchical and the network model, if you didn't have a path to the data you wanted, you were in a difficult situation. You could change the access paths, but then you had to go through a lot of handwritten database query code and rewrite it to handle the new access paths. It was difficult to make changes to an application's data model.

##### **The relational model**

By contrast, the relational model laid out all the data in the open: a relation (table) is simply a collection of tuples (rows):

* There are no labyrinthine nested structures, no complicated access paths to follow if you want to look at the data.
* You can read any or all of the rows in a table, selecting those that match an arbitrary condition.
* You can read a particular row by designating some columns as a key and matching on those.
* You can insert a new row into any table without worrying about foreign key relationships to and from other tables. (Foreign key constraints allow you to restrict modifications, but such constraints are not required by the relational model. Even with constraints, joins on foreign keys are performed at query time, whereas in CODASYL, the join was effectively done at insert time.)

In a relational database, the query optimizer automatically decides which parts of the query to execute in which order, and which indexes to use. Those choices are effectively the "access path", but the big difference is that they are made automatically by the query optimizer, not by the application developer, so we rarely need to think about them.

If you want to query your data in new ways, you can just declare a new index, and queries will automatically use whichever indexes are most appropriate. You don't need to change your queries to take advantage of a new index. (See also [Query Languages for Data](#query-languages-for-data)) The relational model thus made it much easier to add new features to applications.

Query optimizers for relational databases are complicated beasts, and they have consumed many years of research and development effort. But a key insight of the relational model was this: you only need to build a query optimizer once, and then all applications that use the database can benefit from it. If you don't have a query optimizer, it's easier to [handcode](https://en.wikipedia.org/wiki/Hand_coding) the access paths for a particular query than to write a general-purpose optimize, but the general-purpose solution wins in the long run.

##### **Comparison to document databases**

Document databases reverted back to the hierarchical model in one aspect: storing nested records (one-to-many relationships, like `positions`, `education`, and `contact_info` in [Figure 2-1](figure_2-1.png)) within their parent record rather than in a separate table.

However, when it comes to representing many-to-one and many-to-many relationships, relational and document databases are not fundamentally different: in both cases, the related item is referenced by a unique identifier, which is called a foreign key in the relational model and a document reference in the document model. <u>That identifier is resolved at read time by using a join or follow-up queries.</u> To date, document databases have not followed the path of CODASYL.
