### **Chapter 7. Classes and Object-Oriented Programming**

### The `class` Statement
### Class Instances
### Scoping Rules
### Inheritance
### Polymorphism Dynamic Binding and Duck Typing

### Static Methods and Class Methods

#### Static Methods *

Besides [instance methods](ch3.md#methods) there are two other common kinds of methods that can be defined. [p123]

A **static method** is an ordinary function that lives in the namespace defined by a class. It does not operate on any kind of instance. To define a static method, use the `@staticmethod` decorator as shown here:

```python
class Foo(object):
    @staticmethod
    def add(x,y):
        return x + y
```

To call a static method, you just prefix it by the class name. You do not pass it any additional
information. For example:

```python
x = Foo.add(3,4) # x = 7
```

A common use of static methods is in writing classes where you might have many different ways to create new instances. Because there can only be one `__init__()` function, alternative creation functions are often defined as shown here:

```c
class Date(object):
    def __init__(self,year,month,day):
        self.year = year
        self.month = month
        self.day = day

    @staticmethod
    def now():
        t = time.localtime()
        return Date(t.tm_year, t.tm_mon, t.tm_day)

    @staticmethod
    def tomorrow():
        t = time.localtime(time.time() + 86400)
        return Date(t.tm_year, t.tm_mon, t.tm_day)
```

#### Class Methods *

**Class methods** are methods that operate on the class itself as an object. Defined using the `@classmethod` decorator, a class method is different than an instance method in that the class is passed as the first argument which is named `cls` by convention. For example:

```python
class Times(object):
    factor = 1

    @classmethod
    def mul(cls, x):
        return cls.factor * x


class TwoTimes(Times):
    factor = 2


x = TwoTimes.mul(4) # Calls Times.mul(TwoTimes, 4) -> 8
```

Notice how the class `TwoTimes` is passed to `mul()` as an object. These are practical but subtle uses of class methods. [p124]

Suppose that you defined a class that inherited from the `Date` class shown previously and customized it slightly:

```python
class EuroDate(Date):
    # Modify string conversion to use European dates
    def __str__(self):
    return "%02d/%02d/%4d" % (self.day, self.month, self.year)
```

Because the class inherits from `Date`, it has all of the same features. However, the `now()` and `tomorrow()` methods are slightly broken. For example, if someone calls `EuroDate.now()`, a `Date` object is returned instead of a `EuroDate` object. A class method can fix this:

```python
class Date(object):
    ...
    @classmethod
    def now(cls):
        t = time.localtime()
        # Create an object of the appropriate type
        return cls(t.tm_year, t.tm_month, t.tm_day)

class EuroDate(Date):
    ...

a = Date.now() # Calls Date.now(Date) and returns a Date
b = EuroDate.now() # Calls Date.now(EuroDate) and returns a EuroDate
```

<u>One caution about static and class methods is that Python does not manage these methods in a separate namespace than the instance methods. As a result, they can be invoked on an instance.</u> For example:

```python
d = Date(1967,4,9)
b = d.now() # Calls Date.now(Date)
```

This is potentially quite confusing because a call to d.now() doesn’t really have anything to do with the instance `d`.This behavior is one area where the Python object system differs from that found in other OO languages such as Ruby. In those languages, class methods are strictly separate from instance methods.
