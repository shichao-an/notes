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

In the location struct, the city, state, and country fields could have been stored as separate pieces of data. In this case, they're closely related so it makes sense to put them all into one struct as optional fields.

#### Tying everything together into data objects

At this point, the edges and properties are defined as separate types. However, it is ideal to store all of the data together because:

1. It provides a single interface to access your information.
2. It makes your data easier to manage if it's stored in a single dataset.

This is accomplished by wrapping every property and edge type into a `DataUnit` union:

```thrift
union DataUnit {
  1: PersonProperty person_property;
  2: PageProperty page_property;
  3: EquivEdge equiv;
  4: PageViewEdge page_view;
}

struct Pedigree {
  1: required i32 true_as_of_secs;
}

struct Data {
  1: required Pedigree pedigree;
  2: required DataUnit dataunit;
}
```

* Each `DataUnit` is paired with its metadata kept in a `Pedigree` struct.
* The pedigree contains the timestamp for the information, but could also potentially contain debugging information or the source of the data.
* The final `Data` struct corresponds to a fact from the fact-based model.

#### Evolving your schema

Thrift is designed so that schemas can evolve over time. The key to evolving Thrift schemas is the numeric identifiers associated with each field. Those IDs are used to identify fields in their serialized form. When you want to change the schema but still be backward compatible with existing data, you must obey the following rules:

* **Fields may be renamed**, because the serialized form of an object uses the field IDs, not the names, to identify fields.
* **A field may be removed, but you must never reuse that field ID**.
    * When deserializing existing data, Thrift will ignore all fields with field IDs not included in the schema.
    * If you were to reuse a previously removed field ID, Thrift would try to deserialize that old data into the new field, which will lead to either invalid or incorrect data.
* **Only optional fields can be added to existing structs**.
    * You can't add required fields because existing data won't have those fields and thus won't be deserializable.
    * This doesn't apply to unions, because unions have no notion of required and optional fields.

The following example shows changes to the SuperWebAnalytics.com schema to store a person's age and the links between web page (changes in bold font).

<pre>
union PersonPropertyValue {
  1: string full_name;
  2: GenderType gender;
  3: Location location;
  <b>4: i16 age;</b>
}

<b>struct LinkedEdge {
  1: required PageID source;
  2: required PageID target;
}</b>

union DataUnit {
  1: PersonProperty person_property;
  2: PageProperty page_property;
  3: EquivEdge equiv;
  4: PageViewEdge page_view;
  <b>5: LinkedEdge page_link;</b>
}
</pre>

Adding a new age property is done by adding it to the corresponding union structure, and a new edge is incorporated by adding it into the `DataUnit` union.

### Limitations of serialization frameworks

Serialization frameworks only check that all required fields are present and are of the expected type, but are unable to check richer properties like "Ages should be nonnegative" or "true-as-of timestamps should not be in the future". Data not matching these properties would indicate a problem in your system, and you wouldn't want them written to your master dataset.

[p52-53]

There are two approaches you can take to work around these limitations with a serialization framework like Apache Thrift:

* **Wrap your generated code in additional code that checks the additional properties you care about**, e.g. ages being non-negative.
    * This approach works well as long as you’re only reading/writing data from/to a single language. If you use multiple languages, you have to duplicate the logic in many languages.
* **Check the extra properties at the very beginning of your batch-processing workflow**. This step would split your dataset into "valid data" and "invalid data" and send a notification if any invalid data was found.
    * This approach makes it easier to implement the rest of your workflow, because anything getting past the validity check can be assumed to have the stricter properties you care about.
    * However, this approach doesn't prevent the invalid data from being written to the master dataset and doesn't help with determining the context in which the corruption happened.

Neither approach is ideal, and you have to decide whether you'd rather maintain the same logic in multiple languages or lose the context in which corruption was introduced. [p53]

### Summary

Implementing the enforceable graph schema for SuperWebAnalytics.com was mostly straightforward. The friction appears when using a serialization framework for this purpose: the inability to enforce every property you care about. The tooling will rarely work perfectly, but <u>it's important to know what would be possible with ideal tools, so you're cognizant of the trade-offs you're making and can keep an eye out for better tools (or make your own).</u>

The next chapter discusses how to physically store a master dataset in the batch layer so that it can be processed easily and efficiently.


### Doubts and Solutions

#### Verbatim

##### **p54 on limitations of serialization frameworks **

> This approach doesn't prevent the invalid data from being written to the master dataset and doesn't help with determining the context in which the corruption happened.

<span class="text-danger">Question</span>: What is "the context in which the corruption happened"?
