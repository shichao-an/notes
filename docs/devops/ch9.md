### **Chapter 9. Other Ilities**

### Introduction

[p181]

This chapter uses the word DevOps pipeline to represent all aspects of DevOps.

In software architecture, the word "ility" is used to describe quality concerns other than those that focus on the basic functionalities and their correctness. In terms of DevOps, ilities correspond to questions such as:

* How well are these functionalities in your pipeline performing?
* Can you precisely repeat your DevOps operations when needed?
* How much time has passed between a business concept and its final release?
* How can different tools in your pipeline interoperate?

Previous chapters discuss some major concerns such as monitoring and security. This chapter covers additional concerns. The following table is a list of the ilities and their primary quality concerns:

Ilities | Quality Concerns
------- | ----------------
Repeatability | The degree to which repeating the same operation is possible
Performance | The time and resources required to execute a DevOps operation
Reliability | The degree to which the DevOps pipeline and individual pieces of software within it maintain their services for defined periods of time
Recoverability | The degree to which a failed DevOps operation can be brought back to a desired state with minimal impacts to the application being operated on
Interoperability | The degree to which different DevOps tools can usefully exchange information via interfaces in a particular context
Testability | The ease with which the DevOps operation software can be made to demonstrate its faults through testing
Modifiability | The amount of effort required to change the DevOps software, processes, or the operation environment of an application

We focus on the ilities of the DevOps pipeline itself rather than the application the pipeline produces and operates on. There are certainly strong connections between the pipeline and the application. For example, the performance and recoverability of an upgrade operation may have significant impacts on the performance and recoverability of the application being upgraded—but we do not explore these connections here. We consider the ility issues of the DevOps pipeline from two different perspectives: product and process.

