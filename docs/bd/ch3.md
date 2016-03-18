### **Chapter 3. Data model for Big Data: Illustration**

The last chapter discusses the principles of forming a data model:

* The value of raw data
* Semantic normalization
* Importance of immutability

This chapter is the first *illustration chapter*, which demonstrates the concepts of the previous chapter using real-world tools.

### Why a serialization framework?

Schemaless format, like JSON, is easy to get started. However, it quickly leads to problems due to bugs or misunderstandings between different developer and data corruption inevitably occurs. Data corruption errors are some of the most time-consuming to debug.

#### Data corruption *

Data corruption issues are hard to debug because there's very little context on how the corruption occurred. Typically the problem is noticed when there's an error downstream in the processing, long after the corrupt data was written.

For example, you might get a null pointer exception due to a mandatory field being missing. You'll quickly realize that the problem is a missing field, but you'll have absolutely no information about how that data got there in the first place.

#### Enforcing schema *

Creating an enforceable schema is good because:

* You get errors at the time of writing the data, giving you full context as to how and why the data became invalid (like a [stack trace](https://en.wikipedia.org/wiki/Stack_trace)).
* The error prevents the program from corrupting the master dataset by writing that data.

Serialization frameworks are an easy approach to making an enforceable schema. They generate code for any languages for reading, writing, and validating objects that match your schema.

### Apache Thrift

[Apache Thrift](https://en.wikipedia.org/wiki/Apache_Thrift) ([http://thrift.apache.org/](http://thrift.apache.org/)) is a tool that can be used to define statically typed, enforceable schemas. It provides an interface definition language to describe the schema in terms of generic data types, and this description can later be used to automatically generate the actual implementation in multiple programming languages.

Other tools similar to Apache Thrift include [Protocol Buffers](https://en.wikipedia.org/wiki/Protocol_Buffers) and [Avro](https://en.wikipedia.org/wiki/Apache_Avro).

The primary elements of Thrif are *struct* and *union* [type definitions](https://thrift.apache.org/docs/idl#definition). They're composed
of other fields, such as:

* Primitive data types (strings, integers, longs, and doubles)
* Collections of other types (lists, maps, and sets)
* Other structs and unions

The general usage is:

* Nodes: unions are useful for representing nodes.
* Edges: structs are natural representations of edges.
* Properties: combination of both.

#### Nodes

In the SuperWebAnalytics.com example, an individual is identified either by a user ID or a browser cookie, but not both. This pattern is common for nodes matches with a union data type: a single value that may have any of several representations.  In Thrift, unions are defined by listing all possible representations. For example:


```thrift
union PersonID {
  1: string cookie;
  2: i64 user_id;
}

union PageID {
  1: string url;
}
```

Unions can also be used for nodes with a single representation, which allows the schema to evolve as the data evolves.


#### Edges

<u>Each edge can be represented as a struct containing two nodes.</u> The name of an edge struct indicates the relationship it represents, and the fields in the edge struct contain the entities involved in the relationship. For example:

```thrift
struct EquivEdge {
  1: required PersonID id1;
  2: required PersonID id2;
}

struct PageViewEdge {
  1: required PersonID person;
  2: required PageID page;
  3: required i64 nonce;
}
```

The fields of a Thrift struct can be denoted as `required` or `optional`. If a field is defined as required, then a value for that field must be provided, or else Thrift will give an error upon serialization or deserialization. Because each edge in a graph schema must have two nodes, they are required fields in this example.

#### Properties

A property contains a node and a value for the property. The value can be one of many types, so it's best represented using a union structure. For example:

```thrift
union PagePropertyValue {
  1: i32 page_views;
}

struct PageProperty {
  1: required PageID id;
  2: required PagePropertyValue property;
}
```

The following example defines the properties for people. The location property is more complex and requires another struct (location) to be defined:

```thrift
struct Location {
  1: optional string city;
  2: optional string state;
  3: optional string country;
}

enum GenderType {
  MALE = 1,
  FEMALE = 2
}

union PersonPropertyValue {
  1: string full_name;
  2: GenderType gender;
  3: Location location;
}

struct PersonProperty {
  1: required PersonID id;
  2: required PersonPropertyValue property;
}
```

In the location struct, the city, state, and country fields could have been stored as separate pieces of data. In this case, they're so closely related it makes sense to put them all into one struct as optional fields.
