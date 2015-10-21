### **Ruby**

### OO Language

#### Ruby Is an Object-Oriented Language

In Ruby, you’d define a **class** to represent entities. With classes, you’ll typically want to create a number of **instances** of each. The word **object** is used interchangeably with **class instance**.

These objects are created by calling a **constructor**, a special method associated with a class. The standard constructor is called `new`.

```ruby
song1 = Song.new("Ruby Tuesday")
song2 = Song.new("Enveloped in Python")
# and so on
```

These instances are both derived from the same class, but they have unique characteristics:

1. Every object has a unique **object identifier** (abbreviated as **object ID**).
2. You can define instance variables, variables with values that are unique to each instance.

Within each class, you can define **instance methods**. These instance methods have access to the object’s instance variables and hence to the object’s state.

Methods are invoked by sending a message to an object. The message contains the method’s name, along with any parameters the method may need. When an object receives a message, it looks into its own class for a corresponding method (and execute it if it exists).

It’s worth noting here a major difference between Ruby and most other languages. For example, Java, you’d find the absolute value of some number by calling a separate function and passing in that number, like:

```java
num = Math.abs(num) // Java code
```

In Ruby, the ability to determine an absolute value is built into numbers: they take care of the details internally. You simply send the message abs to a number object and let it do the work:

```ruby
num = -1234 # => -1234
positive = num.abs # => 1234
```

- - -

### References

* [PR12] *Programming Ruby 1.9 & 2.0: The Pragmatic Programmers' Guide* (4th Edition)
* [The Ruby Style Guide](https://github.com/bbatsov/ruby-style-guide)
