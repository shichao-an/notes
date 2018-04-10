### **Chatper 3. Storage and Retrieval**

On the most fundamental level, a database needs to do two things:

1. When you give it some data, it should store the data.
2. When you ask it again later, it should give the data back to you.

[Chapter 2](ch2.md) discussed data models and query languages, the format in which you (the application developer) give the database your data, and the mechanism by which you can ask for it again later.

This chapter is from the database's point of view: how we can store the data that we're given, and how we can find it again when we're asked for it.

As an application developer, you are probably not going to implement your own storage engine from scratch, but you do need to select a storage engine that is appropriate for your application. You need to care about how the database handles storage and retrieval internally.

In particular, there is a big difference between:

* Storage engines that are optimized for transactional workloads: see [Transaction Processing or Analytics?](#transaction-processing-or-analytics)
* Storage engines that are optimized for analytics: see [Column-Oriented Storage](#column-oriented-storage)

### Data Structures That Power Your Database

Consider the world's simplest database, implemented as two Bash functions:

```bash
#!/bin/bash

db_set () {
    echo "$1,$2" >> database
}

db_get () {
    grep "^$1," database | sed -e "s/^$1,//" | tail -n 1
}
```

These two functions implement a key-value store:

* You can call `db_set` key value, which will store key and value in the database. The key and value can be anything you like, e.g., the value could be a JSON document.
* You can then call `db_get` key, which looks up the most recent value associated with that particular key and returns it.

```shell-session
$ db_set 123456 '{"name":"London","attractions":["Big Ben","London Eye"]}'
$ db_set 42 '{"name":"San Francisco","attractions":["Golden Gate Bridge"]}'
$ db_get 42
{"name":"San Francisco","attractions":["Golden Gate Bridge"]}
```

The underlying storage format is very simple: a text file where each line contains a key-value pair, separated by a comma (roughly like a [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file, ignoring escaping issues). Every call to `db_set` appends to the end of the file, so if you update a key several times, the old versions of the value are not overwritten, you need to look at the last occurrence of a key in a file to find the latest value (hence the `tail -n 1` in `db_get`):

This `db_set` function actually has pretty good performance, because appending to a file is generally very efficient. Similarly to what `db_set` does, many databases internally use a log, which is an append-only data file. Real databases have more issues to deal with, for example:

* Concurrency control
* Reclaiming disk space so that the log doesn't grow forever
* Handling errors and partially written records

> <small>The word *log* is often used to refer to application logs, where an application outputs text that describes what’s happening. In this book, *log* is used in the more general sense: an append-only sequence of records. It doesn't have to be human-readable; it might be binary and intended only for other programs to read.</small>

On the other hand, the `db_get` function has terrible performance if you have a large number of records in your database. `db_get` has to scan the entire database file from beginning to end, looking for occurrences of the key. In algorithmic terms, the cost of a lookup is *O(n)*.

In order to efficiently find the value for a particular key in the database, we need a different data structure: an *index*. The general idea behind index is to keep some additional metadata on the side, which acts as a signpost and helps you to locate the data you want. If you want to search the same data in several different ways, you may need several different indexes on different parts of the data.

An index is an additional structure that is derived from the primary data. Many databases allow you to add and remove indexes, and this doesn't affect the contents of the database; it only affects the performance of queries. Maintaining additional structures incurs overhead, especially on writes. For writes, it's hard to beat the performance of simply appending to a file, because that's the simplest possible write operation. Any kind of index usually slows down writes, because the index also needs to be updated every time data is written.

<u>This is an important trade-off in storage systems: well-chosen indexes speed up read queries, but every index slows down writes.</u> For this reason, databases don't usually index everything by default, but require you (the application developer or database administrator) to choose indexes manually, using your knowledge of the application's typical query patterns. You can then choose the indexes that give your application the greatest benefit, without introducing more overhead than necessary.

#### Hash Indexes
