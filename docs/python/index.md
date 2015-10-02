### **Python**

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
