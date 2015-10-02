### **Python**

### A Tutorial Introduction

#### Generators

Instead of returning a single value, a function can generate an entire sequence of results if it uses the `yield` statement. For example:

```python
def countdown(n):
    print "Counting down!"
    while n > 0:
        yield n # Generate a value (n)
        n -= 1
```

Any function that uses `yield` is known as a **generator**. Calling a generator function creates an object that produces a sequence of results through successive calls to a `next()` method (or `__next__()` in Python 3). For example:

```pycon
>>> c = countdown(5)
>>> c.next()
Counting down!
5
>>> c.next()
4
>>> c.next()
3
```

The `next()` call makes a generator function run until it reaches the next `yield` statement. At this point, the value passed to `yield` is returned by `next()`, and the function suspends execution. The function resumes execution on the statement following `yield` when `next()` is called again. This process continues until the function returns.

Normally you would not manually call next() as shown. Instead, you hook it up to
a for loop like this:

Normally you would not manually call `next()` as shown. Instead, you hook it up to a `for` loop like this:

```python
>>> for i in countdown(5):
... print i,
Counting down!
5 4 3 2 1
```

Generators are an extremely powerful way of writing programs based on processing pipelines, streams, or data flow. For example, the following generator function mimics the behavior of the UNIX `tail -f` command that’s commonly used to monitor log files:

```python
# tail a file (like tail -f)
import time
def tail(f):
    f.seek(0,2) # Move to EOF
    while True:
        line = f.readline() # Try reading a new line of text
        if not line: # If nothing, sleep briefly and try again
            time.sleep(0.1)
            continue
        yield line
```

Here’s an example of hooking both of these generators together to create a simple processing pipeline:

```python
# A python implementation of Unix "tail -f | grep python"
wwwlog = tail(open("access-log"))
pylines = grep(wwwlog,"python")
for line in pylines:
    print line,
```

A subtle aspect of generators is that they are often mixed together with other iterable
objects such as lists or files. Specifically, when you write a statement such as `for item
in s`, `s` could represent the following:

* A list of items,
* The lines of a file,
* The result of a generator function,
* Any number of other objects that support iteration.

The fact that you can just plug different objects in for `s` can be a powerful tool for creating extensible programs.

#### Coroutines

Normally, functions operate on a single set of input arguments. However, a function can also be written to operate as a task that processes a sequence of inputs sent to it. This type of function is known as a **coroutine** and is created by using the `yield` statement as an expression `(yield)` as shown in this example:

```python
def print_matches(matchtext):
    print "Looking for", matchtext
    while True:
        line = (yield) # Get a line of text
        if matchtext in line:
            print line
```

To use this function, you first call it, advance it to the first `(yield)`, and then start sending data to it using `send()`. For example:

```pycon
>>> matcher = print_matches("python")
>>> matcher.next() # Advance to the first (yield)
Looking for python
>>> matcher.send("Hello World")
>>> matcher.send("python is cool")
python is cool
>>> matcher.send("yow!")
>>> matcher.close() # Done with the matcher function call
>>>
```

A coroutine is suspended until a value is sent to it using `send()`. When this happens, that value is returned by the `(yield)` expression inside the coroutine and is processed by the statements that follow. Processing continues until the next `(yield)` expression is encountered, at which point the function suspends. This continues until the coroutine function returns or `close()` is called on it as shown in the previous example.

```python
# A set of matcher coroutines
matchers = [
print_matches("python"),
print_matches("guido"),
print_matches("jython")
]

# Prep all of the matchers by calling next()
for m in matchers: m.next()

# Feed an active log file into all matchers. Note for this to work,
# a web server must be actively writing data to the log.
wwwlog = tail(open("access-log"))
for line in wwwlog:
    for m in matchers:
        m.send(line) # Send data into each matcher coroutine
```

Coroutines are detailed in [Chapter 6](#functions-and-functional-programming).

### Functions and Functional Programming

#### Decorators

A **decorator** is a function whose primary purpose is to wrap another function or class.  The primary purpose of this wrapping is to transparently alter or enhance the behavior of the object being wrapped. Syntactically, decorators are denoted using the special `@` symbol as follows:

```python
@trace
def square(x):
    return x*x
```

The preceding code is shorthand for the following:

```python
def square(x):
    return x*x
square = trace(square)
```

In the example, a function `square()` is defined. However, immediately after its definition, the function object itself is passed to the function `trace()`, which returns an object that replaces the original `square`.

[PER p101]

##### **Order of multiple decorators** *

When decorators are used, they must appear on their own line immediately prior to a function or class definition. More than one decorator can also be applied. For example:

```python
@foo
@bar
@spam
def grok(x):
    pass
```

In this case, the decorators are applied in the order listed.The result is the same as this:

```python
def grok(x):
    pass
grok = foo(bar(spam(grok)))
```

##### **Decorators with arguments** *

A decorator can also accept arguments. For example:

```python
@eventhandler('BUTTON')
def handle_button(msg):
    # ...
@eventhandler('RESET')
def handle_reset(msg):
    # ...
```

If arguments are supplied, the semantics of the decorator are as follows:

```python
def handle_button(msg):
    # ...
temp = eventhandler('BUTTON') # Call decorator with supplied arguments
handle_button = temp(handle_button) # Call the function returned by the decorato
```

In this case, the decorator function only accepts the arguments supplied with the `@` specifier. It then returns a function that is called with the function as an argument.

```python
# Event handler decorator
event_handlers = { }
def eventhandler(event):
    def register_function(f):
        event_handlers[event] = f
        return f
    return register_function
```
Decorators can also be applied to class definitions. For example:

```python
@foo
class Bar(object):
    def __init__(self,x):
        self.x = x
    def spam(self):
        # statements
```

For class decorators, you should always have the decorator function return a class object as a result. Code that expects to work with the original class definition may want to reference members of the class directly such as `Bar.spam`. This won’t work correctly if the decorator function `foo()` returns a function.

Decorators can interact strangely with other aspects of functions such as recursion, documentation strings, and function attributes. These issues are described later in this chapter.

- - -

### References

* [PER] *Python Essential Reference* (4th Edition)
