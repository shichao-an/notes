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

#### Some Basic Ruby

* Methods are defined with the keyword def, followed by the method name and the method’s parameters between parentheses (parentheses are optional). Ruby doesn’t use braces to delimit the bodies of compound statements and definitions. Instead, you simply finish the body with the keyword `end`.
* The most common way to create a string is to use **string literals**, which are sequences of characters between single or double quotation marks.
    * Single-quoted: with a few exceptions, what you enter in the string literal becomes the string’s value.
    * Double-quoted:
        * Substitutions: sequences that start with a backslash character are replaced with some binary value.
        * Expression interpolation: the sequence `#{expression}` is replaced by the value of `expression`.

Ruby uses a convention for names that may seem strange at first: the first characters of a name indicate
how the name is used.

1. Local variables, method parameters, and method names should all start with a lowercase letter or an underscore (non-ASCII characters are assumed to be lowercase letters).
2. Global variables are prefixed with a dollar sign (`$`)
3. Instance variables begin with an "at" sign (`@`).
4. Class variables start with two "at" signs (`@@`).
5. Class names, module names, and constants must start with an uppercase letter.

By convention, multiword instance variables are written with underscores between the words, and multiword class names are written in `MixedCase` (with each word capitalized). Method names may end with the characters `?`, `!`, and `=`.

The following table is an example of variable, class, and constant names:

  |
- | -
Local Variable | `name` `fish_and_chips` `x_axis` `thx1138` `_x` `_26`
Instance Variable | `@name` `@point_1` `@X` `@_` `@plan9`
Class Variable | `@@total` `@@symtab` `@@N` `@@x_pos` `@@SINGLE`
Global Variable | `$debug` `$CUSTOMER` `$_` `$plan9` `$Global`
Class Name | `String` `ActiveRecord` `MyClass`
Constant Name | `FEET_PER_MILE` `DEBUG`

#### Arrays and Hashes

Two ways to create and initialize a new array object using an **array literal**:

```ruby
a = [ 'ant', 'bee', 'cat', 'dog', 'elk' ]
# this is the same:
a = %w{ ant bee cat dog elk }
```

In many languages, the concept of `nil` (or null) means "no object". In Ruby, however, `nil` is an object that happens to represent nothing.

Ruby hashes are similar to arrays. A hash literal uses braces rather than square brackets. The literal must supply two objects for every entry: one for the key, the other for the value, separated by `=>`:

```ruby
inst_section = {
  'cello' => 'string',
  'clarinet' => 'woodwind',
  'drum' => 'percussion',
}
```

A hash by default returns `nil` when indexed by a key it doesn’t contain. To specify a default value (for example, 0) when you create a new, empty hash:

```ruby
histogram = Hash.new(0) # The default value is zero
histogram['ruby'] # => 0
```

#### Symbols

Most of the time, the actual numeric values of these constants are irrelevant (as long as they are unique). In Ruby, **symbols** are simply constant names that you don’t have to predeclare and that are guaranteed to be unique. A symbol literal starts with a colon and is normally followed by some kind of name, like `:north`, `:east`. There’s no need to assign some kind of value to a symbol; Ruby takes care of that for you.  Ruby also guarantees that no matter where it appears in your program, a particular symbol will have the same value.

Symbols are frequently used as keys in hashes:

```ruby
inst_section = {
  :cello => 'string',
  :clarinet => 'woodwind',
  :drum => 'percussion'
}
```

Symbols are so frequently used as hash keys that Ruby has a shortcut syntax (you can use `name: value` pairs to create a hash if the keys are symbols):

```ruby
inst_section = {
  cello: 'string',
  clarinet: 'woodwind',
  drum: 'percussion'
}
```

- - -

### References

* [PR12] *Programming Ruby 1.9 & 2.0: The Pragmatic Programmers' Guide* (4th Edition)
* [The Ruby Style Guide](https://github.com/bbatsov/ruby-style-guide)
