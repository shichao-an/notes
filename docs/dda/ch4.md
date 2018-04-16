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

### Formats for Encoding Data

Programs usually work with data in two different representations:

1. In memory, data is kept in data structures such as objects, structs, lists, arrays, hash tables and trees, optimized for efficient access and manipulation by the CPU (typically using pointers).
2. When you want to write data to a file or send it over the network, you have to encode it as some kind of self-contained sequence of bytes (for example, a JSON document). Since a pointer wouldn't make sense to any other process, this sequence-of-bytes representation looks quite different from the data structures that are normally used in memory, with the exception of some special cases, such as certain [memory-mapped files](https://en.wikipedia.org/wiki/Memory-mapped_file) or when operating directly on compressed data (as described in [Column Compression](ch3.md#column-compression) in Chapter 3).

Thus, we need translation between the two representations:

* The translation from the in-memory representation to a byte sequence is called **encoding** (also known as [*serialization*](https://en.wikipedia.org/wiki/Serialization) or [*marshalling*](https://en.wikipedia.org/wiki/Marshalling_(computer_science))).
* The reverse is called **decoding** (*parsing*, *deserialization*, [*unmarshalling*](https://en.wikipedia.org/wiki/Unmarshalling)).

The term [*serialization*](https://en.wikipedia.org/wiki/Serializability) is also used in the context of [transactions](https://en.wikipedia.org/wiki/Database_transaction) (see [Chapter 7](ch7.md)), with a completely different meaning. We'll stick with *encoding* in this book.

#### Language-Specific Formats

Many programming languages come with built-in support for encoding in-memory
objects into byte sequences. For example:

* Java has [`java.io.Serializable`](https://docs.oracle.com/javase/8/docs/api/java/io/Serializable.html) (see [Java Object Serialization Specification](https://docs.oracle.com/javase/8/docs/platform/serialization/spec/serialTOC.html))
* Ruby has [`Marshal`](https://ruby-doc.org/core-2.5.0/Marshal.html)
* Python has [`pickle`](https://docs.python.org/3/library/pickle.html)

Many third-party libraries also exist, such as [Kryo](https://github.com/EsotericSoftware/kryo) for Java.

These encoding libraries are very convenient, because they allow in-memory objects to be saved and restored with minimal additional code, but they also have a number of problems:

* **Language-Specific**. The encoding is often tied to a particular programming language, and reading the data in another language is very difficult.
* **Security**. In order to restore data in the same object types, the decoding process needs to be able to instantiate arbitrary classes. This is a source of security problems: if an attacker can get your application to decode an arbitrary byte sequence, they can instantiate arbitrary classes, which in turn often allows them to do terrible things such as remotely executing arbitrary code.
* **Versioning**. As they are intended for quick and easy encoding of data, they often neglect the inconvenient problems of forward and backward compatibility.
* **Efficiency**. The efficiency such as the CPU time taken to encode or decode, and the size of the encoded structure, is also often an afterthought. For example, Java's built-in serialization is notorious for its bad performance and bloated encoding.

For these reasons it's generally a bad idea to use your language’s built-in encoding for anything other than very transient purposes.

#### JSON, XML, and Binary Variants

JSON and XML are the widely known and supported standardized encodings widely supported, XML is often criticized for being too verbose and unnecessarily complicated. JSON's popularity is mainly due to its built-in support in web browsers (by virtue of being a subset of JavaScript) and simplicity relative to XML. CSV is another popular language-independent format, albeit less powerful.

As textual formats, JSON, XML, and CSV also have some subtle problems:

* Ambiguity in numbers. In XML and CSV, you cannot distinguish between a number and a string that happens to consist of digits (except by referring to an external schema). JSON distinguishes strings and numbers, but it doesn't distinguish integers and floating-point numbers, and it doesn't specify a precision.
    * This is a problem when dealing with large numbers; for example, integers greater than 2<sup>53</sup> cannot be exactly represented in an [IEEE 754 double-precision floating-point](https://en.wikipedia.org/wiki/Double-precision_floating-point_format) number, so such numbers become inaccurate when parsed in a language that uses floating-point numbers (such as JavaScript). Such an example occurs on Twitter, which uses a 64-bit number to identify each tweet. The JSON returned by Twitter's API includes tweet IDs twice, once as a JSON number and once as a decimal string, to work around the fact that the numbers are not correctly parsed by JavaScript applications.
* Lacking binary strings support. JSON and XML have good support for Unicode character strings (i.e., human-readable text), but they don't support binary strings (sequences of bytes without a character encoding).
    * Binary strings are a useful feature, so people get around this limitation by encoding the binary data as text using [Base64](https://en.wikipedia.org/wiki/Base64). The schema is then used to indicate that the value should be interpreted as Base64-encoded. This works, but it’s somewhat hacky and increases the data size by 33%.
* There is optional schema support for both XML (see [XML Schema](https://www.w3.org/XML/Schema)) and JSON (see [JSON Schema](http://json-schema.org/)). Use of XML schemas is fairly widespread, but many JSON-based tools don't bother using schemas. Since the correct interpretation of data (such as numbers and binary strings) depends on the schema, applications that don't use XML/JSON schemas need to potentially hardcode the appropriate encoding/decoding logic instead.
* CSV does not have any schema, so it is up to the application to define the meaning of each row and column. If an application change adds a new row or column, you have to handle that change manually.

Despite these flaws, JSON, XML, and CSV are good enough for many purposes. It's likely that they will remain popular, especially as data interchange formats (i.e., for sending data from one organization to another).

##### **Binary encoding**
