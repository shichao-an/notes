### **Chapter 9. Concurrency with Shared Variables**

The previous chapter presented several programs that use goroutines and channels to
express concurrency in a direct and natural way.

This chapter looks at the mechanics of concurrency, and in particular discusses:

* Some of the problems associated with sharing variables among multiple goroutines.
* The analytical techniques for recognizing those problems.
* The patterns for solving them.
* Some of the technical differences between goroutines and operating system threads.

### Race Conditions

In a sequential program, that is, a program with only one goroutine, the steps of the program happen in the familiar execution order determined by the program logic. For instance, in a sequence of statements, the first one happens before the second one, and so on.

In a program with two or more goroutines, the steps within each goroutine happen in the familiar order, but in general we don't know whether an event *x* in one goroutine happens before an event *y* in another goroutine, or happens after it, or is simultaneous with it. When we cannot confidently say that one event *happens before* the other, then the events *x* and *y* are *concurrent*.
