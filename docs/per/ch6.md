### **Chapter 6. Functions and Functional Programming**

### Functions

### Parameter Passing and Return Values

### Scoping Rules

### Functions as Objects and Closures

### Decorators

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

[p101]

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

### Generators and yield

If a function uses the `yield` keyword, it defines an object known as a **generator**. A generator is a function that produces a sequence of values for use in iteration. For example:

```python
def countdown(n):
    print("Counting down from %d" % n)
    while n > 0:
        yield n
        n -= 1
    return
```

When this function is called, its code does not start executing. For example:

```pycon
>>> c = countdown(10)
>>>
```

Instead, a generator object is returned, which executes the function whenever `next()` is called (or `__next_ _()` in Python 3). For example:

```pycon
>>> c.next() # Use c.__next__() in Python 3
Counting down from 10
10
>>> c.next()
9
```

When `next()` is invoked, the generator function executes statements until it reaches a `yield` statement. The `yield` statement produces a result at which point execution of the function stops until `next()` is invoked again. Execution then resumes with the statement following `yield`.

You normally don’t call `next()` directly on a generator but use it with the for statement, `sum()`, or some other operation that consumes a sequence.

#### The `close()` method and `GeneratorExit` exception *

A problem with generators is the case where a generator function is
only partially consumed. For example:

```python
for n in countdown(10):
    if n == 2:
        break
```

Since the `for` loop aborts by calling `break`, the associated generator never runs to full completion. To handle this case, generator objects have a method `close()` that is used to signal a shutdown. When a generator is no longer used or deleted, close() is called.

Though it normally not necessary to call `close()`, you can also call it manually as shown here:

```pycon
>>> c = countdown(10)
>>> c.next()
Counting down from 10
10
>>> c.next()
9
>>> c.close()
>>> c.next()
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
StopIteration
>>>
```

Inside the generator function, `close()` is signaled by a `GeneratorExit` exception occurring on the `yield` statement. You can optionally catch this exception to perform cleanup actions.

```python
def countdown(n):
    print("Counting down from %d" % n)
    try:
        while n > 0:
            yield n
            n = n - 1
    except GeneratorExit:
        print("Only made it to %d" % n)
```
Note that:

* Although it is possible to catch `GeneratorExit`, it is illegal for a generator function to handle the exception and produce another output value using yield.
* If a program is currently iterating on generator, you should not call `close()` asynchronously on that generator from a separate thread of execution or from a signal handler.

### Coroutines and yield Expressions

Inside a function, the `yield` statement can also be used as an expression that appears on the right side of an assignment operator. For example:

```python
def receiver():
    print("Ready to receive")
    while True:
        n = (yield)
        print("Got %s" % n)
```

<u>A function that uses `yield` in this manner is known as a **coroutine**, and it executes in response to values being sent to it.</u> Its behavior is also very similar to a generator. For example:

```pycon
>>> r = receiver()
>>> r.next() # Advance to first yield (r._ _next_ _() in Python 3)
Ready to receive
>>> r.send(1)
Got 1
>>> r.send(2)
Got 2
>>> r.send("Hello")
Got Hello
>>>
```

In this example:

1. After the call to `next()`, the coroutine executes statements leading to the first `yield` expression. At this point, the coroutine suspends, waiting for a value to be sent to it using the `send()` method of the associated generator object `r`.
2. The value passed to `send()` is returned by the `(yield)` expression in the coroutine. Upon receiving a value, a coroutine executes statements until the next `yield` statement is encountered.

To avoid overlooking `next()` on a coroutine to be called, it is recommended that coroutines be wrapped with a decorator that automatically takes care of this step.

```python
def coroutine(func):
    def start(*args,**kwargs):
        g = func(*args,**kwargs)
        g.next()
        return g
    return start
```

Using this decorator, you would write and use coroutines using:

```python
@coroutine
def receiver():
    print("Ready to receive")
    while True:
        n = (yield)
        print("Got %s" % n)
# Example use
r = receiver()
r.send("Hello World") # Note : No initial .next() needed
```

A coroutine will typically run indefinitely unless:

* It is explicitly shut down (by calling `close()`).
* It exits on its own.

The `close()` method closes the stream of input values:

```python
>>> r.close()
>>> r.send(4)
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
StopIteration
```

Once closed, a `StopIteration` exception will be raised if further values are sent to a coroutine. The `close()` operation raises `GeneratorExit` (which can be caught using `except`) inside the coroutine.

#### Raise exceptions `throw()` method *

Exceptions can be raised inside a coroutine using the `throw(exctype [, value [, tb]])` method where `exctype` is an exception type, `value` is the exception value, and `tb` is a traceback object. For example:

```pycon
>>> r.throw(RuntimeError, "You're hosed!")
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
File "<stdin>", line 4, in receiver
RuntimeError: You're hosed!
```

* Exceptions raised using `throw()` will originate at the currently executing `yield` statement in the coroutine. A coroutine is able to catch exceptions and handle them as appropriate.
* It is not safe to use `throw()` as an asynchronous signal to a coroutine; it should never be invoked from a separate execution thread or in a signal handler.

#### Simultaneously receive and emit return values *

A coroutine may simultaneously receive and emit return values using `yield` if values are supplied in the `yield` expression. For example:

```python
def line_splitter(delimiter=None):
    print("Ready to split")
    result = None
    while True:
        line = (yield result)
        result = line.split(delimiter)
```

Now calls to `send()` also produce a result. For example:

```pycon
>>> s = line_splitter(",")
>>> s.next()
Ready to split
>>> s.send("A,B,C")
['A', 'B', 'C' ]
>>> s.send("100,200,300")
['100', '200', '300']
>>>
```

1. The first `next()` call advances the coroutine to `(yield result)`, which returns `None`, the initial value of `result`.
2. On subsequent `send()` calls, the received value is placed in `line` and split into `result`. The value returned by `send()` is the value passed to the next `yield` statement encountered. In other words, <u>the value returned by `send()` comes from the next `yield` expression, not the one responsible for receiving the value passed by `send()`.</u>

If a coroutine returns values, some care is required if exceptions raised with `throw()` are being handled. <u>If you raise an exception in a coroutine using `throw()`, the value passed to the next `yield` in the coroutine will be returned as the result of `throw()`. If you need this value and forget to save it, it will be lost.</u>
