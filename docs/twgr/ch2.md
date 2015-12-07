### **Chapter 2. Objects, methods, and local variables**

Every line of Ruby code involves the concept of the object. What you do with objects, broadly speaking, is send them messages, most of which correspond to names of methods that you’re asking the object to execute. This chapter details the combined processes of message sending and method calling.

### Talking to objects

In any Ruby program, the bulk of the design, logic, and action revolves around objects. When you write Ruby programs, your main activities are creating objects, endowing them with abilities, and asking them to perform actions. When you want something done, you ask an object to do it. For example, rather than ask in the abstract whether *a* equals *b*, you ask a whether it considers itself equal to *b*. Generally, writing a Ruby program is largely a matter of engineering your objects so that each object plays a clear role and can perform actions related to that role.

#### Ruby and object orientation

Ruby comes to the idea of manipulating data through objects via the program language design principle [object orientation](https://en.wikipedia.org/wiki/Object-oriented_programming). In object-oriented programming (OOP), you perform calculations, data manipulation, and input/output operations by creating objects and asking them to perform actions and provide you with information.

Designing object-oriented software is largely a matter of figuring out what you want your objects to be:

* What they should do,
* How they’ll interact with each other,
* How many of each there should be (for example, many students, one registrar),
* Other such questions.

Ruby provides a complete set of tools for:

* Naming, creating, addressing, and manipulating objects,
* The data they operate on through the manipulation of those objects.

#### Creating a generic object

[p36]

The following code creates a generic object, which does not represent or model anything specific:

```ruby
obj = Object.new
```

Now you have an object and a variable through which you can address it.

All Ruby objects are created with certain methods that they know how to execute because they’re Ruby objects.


##### **Defining an object’s behavior**

Specifically, and more technically, you have to define a method for your object. You do this using a special term, the keyword `def`. The following code defines method `talk` for the object `obj`:

```ruby
def obj.talk
  puts "I am an object."
  puts "(Do you object?)"
end
```

The following figure shows analysis of the above code:

[![Figure 2.1 Anatomy of a method definition](figure_2.1.png)](figure_2.1.png "Figure 2.1 Anatomy of a method definition")

##### **Sending messages to objects**

Use the message-sending or method-calling syntax:

```ruby
obj.talk
```

The output is:

```text
I am an object.
(Do you object?)
```

The object `obj` *responds to* the message `talk`. <u>An object is said to respond to a message if the object has a method defined whose name corresponds to the message.</u>

A few things to consider about the dot-based message-sending syntax:

* The dot (`.`) is the message-sending operator. The message on the right is sent to the object (or *receiver*) on the left.
* The receiver can be often represented by a variable that stands in for an object; it can also be a literal object construct, e.g. a string in quotation marks.
* In practice, the message being sent is almost always the name of a method. The object always tries to act on the assumption that the message is the name of a method. If there’s no method by that name, error-handling measures are taken.

#### Methods that take arguments

In a method definition, you indicate the arguments by means of a list of variables in parentheses after the method name. Arguments can be required or optional. More precisely:

* The variables listed in the method definition are the method’s **formal parameters**.
* The values you supply to the method when you call it are the corresponding **arguments**.

However, it’s common to use the word *arguments*, informally, to refer to a method’s parameters as well as a method call’s arguments.

For example, define a method:

```ruby
def obj.c2f(c)
  c * 9.0 / 5 + 32
end
```

The method `obj.c2f` has one formal parameter, which means it takes one argument. When you call the method, you provide an argument:

```ruby
puts obj.c2f(100)
```

The result is:

```text
212.0
```

The parentheses are optional in both cases, you can also do this:

```ruby
def obj.c2f c
```
and this:

```ruby
obj.c2f 100
```

However, parentheses are not always optional, particularly when you’re stringing multiple
method calls together, so it’s good to lean toward using them rather than leaving them
out. You can make an exception for common or conventional cases where parentheses
are usually excluded, like calls to `puts`. But when in doubt, use the parentheses.

At the other end of the process, every method call *returns* a value.

#### The return value of a method

Ruby code is made up of expressions, each of which evaluates to a particular value.  The following table shows some examples of expressions and their values:

Expression | Value | Comments
---------- | ----- | --------
`2 + 2` | `4` | Arithmetic expressions evaluate to their results.
`"Hello"` | `"Hello"` | A simple, literal string (in quotation marks) evaluates to itself.
`"Hello" + " there"` | `"Hello there"` | Strings can be "added" to each other (concatenated) with the plus sign.
`c = 100` | `100` | When you assign to a variable, the whole assignment evaluates to the value you’ve assigned.
`c * 9/5 + 32` | 212 | The usual rules of precedence apply: multiplication and division bind more tightly than addition and are performed first.
`obj.c2f(100)` | `212` | A method call is an expression.

Every method call is an expression.  When you call a method, the method call evaluates to something. This result of calling a method is the method’s return value.

The return value of any method is the same as the value of the last expression evaluated during execution of the method. In the case of the temperature-conversion method (i.e. `obj.c2f`), the last expression evaluated is the only line of the method body.

Ruby gives you a keyword for making return values explicit: `return`. The use of this keyword is usually optional, but many programmers like to use it because it makes explicit what is otherwise implicit:

```ruby
def obj.c2f(c)
  return c * 9.0 / 5 + 32
end
```

This is equivalent to the earlier version of the method, but it’s more expressive about what it’s doing.

In some cases, the `return` is required:

* You have to use it if you return multiple values, which will be automatically wrapped up in an array: `return a,b,c` rather than just `a,b,c` (though you can also return multiple values in an explicit array, like `[a,b,c]`, without return).
* You also have to use `return` if you want to return from somewhere in the middle of a method.

Whether you use return or not, something will be returned from every method call. Even a call to an empty method body, consisting of just the `def` and `end` statements, returns `nil`.

At this point, the object is doing what we need it to do: listening to messages and acting on them. [p40]

### Crafting an object: The behavior of a ticket

#### The ticket object, behavior first

A ticket object should be able to provide data about itself. It should field requests for information about the event it’s for: when, where, name of event, performer, which seat, and cost.

```text
01/02/03
Town Hall
Author's reading
Mark Twain
Second Balcony, row J, seat 12
$5.50
```

##### **Creating the ticket object**

<small>[ch2/ticket.rb](https://github.com/shichao-an/twgr2E-code/blob/master/ch2/ticket.rb)</small>

```ruby
ticket = Object.new

def ticket.date
  "01/02/03"
end

def ticket.venue
  "Town Hall"
end

def ticket.event
  "Author's reading"
end

def ticket.performer
  "Mark Twain"
end

def ticket.seat
  "Second Balcony, row J, seat 12"
end

def ticket.price
  5.50
end
```

The majority of the methods defined here return string values. The `price` method returns a floating-point number.

##### **Querying the ticket object**

The use of `print` and `puts` can help get the information:

```ruby
print "This ticket is for: "
print ticket.event + ", at "
print ticket.venue + ", on "
puts ticket.date + "."
print "The performer is "
puts ticket.performer + "."
print "The seat is "
print ticket.seat + ", "
print "and it costs $"
puts "%.2f." % ticket.price
```

##### **Shortening the ticket code via string interpolation**

One of the most useful programming techniques available in Ruby is [**string interpolation**](https://en.wikipedia.org/wiki/String_interpolation).  The string-interpolation operator gives you a way to drop anything into a string: a variable, for example, or the return value of a method. This can save you a lot of back-and-forth between `print` and `puts`.

Strings can also be concatenated with the plus sign (`+`). The following code is an example of using string interpolation to insert the values of expressions into the string and using string addition to consolidate multiple `puts` calls into one:

```ruby
puts "This ticket is for: #{ticket.event}, at #{ticket.venue}." +
  "The performer is #{ticket.performer}." +
  "The seat is #{ticket.seat}, " +
  "and it costs $#{"%.2f." % ticket.price}"
```
