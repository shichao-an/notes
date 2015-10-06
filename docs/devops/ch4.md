### **Chapter 4. Overall Architecture**

DevOps achieves its goals partially by replacing explicit coordination with implicit and often less coordination. [p65]

### Do DevOps Practices Require Architectural Change?

### Overall Architecture Structure

* A **module** is a code unit with coherent functionality.
* A **component** is an executable unit.

A compiler or interpreter turns modules into binaries, and a builder turns the binaries into components. The development team directly develops modules. Components are results of the modules developed by development teams.

Development teams using DevOps processes are usually small and have limited inter-team coordination. <u>When a team deploys a component, it cannot go into production unless the component is compatible with other components with which it interacts.</u> Ensuring this compatibility require either of the following:

* Explicit multi-team coordination,
* Implicitly definition of the architecture.

An organization can introduce continuous deployment without major architectural modifications. However, dramatically reducing the time required to place a component into production requires architectural support:

* **Deploying without explicit coordination** with other teams reduces the time required to place a component into production.
* ** Allowing for different versions of the same service** to be simultaneously in production leads to different team members deploying without coordination with other members of their team.
* **Rolling back a deployment** in the event of errors allows for various forms of live testing.

**Microservice architecture** is an architectural style that satisfies these requirements. It is a good general basis for projects that are adopting DevOps practices. By definition, a microservice architecture consists of a collection of services where each service provides a small amount of functionality and the total functionality of the system is derived from composing multiple services.

The following figure describes a microservice architecture. A user interacts with a single consumer-facing service, which in turn utilizes a collection of other services. We use the terminology **service** to refer to a component that provides a service and **client** to refer to a component that requests a service. A single component can be a client in one interaction and a service in another. In a system such as LinkedIn, the service depth may reach as much as 70 for a single user request.

[![Figure 4.1 User interacting with a single service that, in turn, utilizes multiple other services [Notation: Architecture]](figure_4.1.png)](figure_4.1.png "Figure 4.1 User interacting with a single service that, in turn, utilizes multiple other services [Notation: Architecture]")

To minimize inter-team coordination, there are three categories of design decisions that can be made globally as a portion of the architecture design, thus removing the need for inter-team coordination: the coordination model, management of resources, and mapping among architectural elements.

#### Coordination Model

If two services interact, there are two details of the coordination:

* How a client discovers a service that it wishes to use,
* How the individual services communicate.

The following figure gives an overview of the interaction between a service and its client:

* The service registers with a registry. The registration includes a name for the service as well as information on how to invoke it (e.g. an endpoint location as a URL or an IP address),
* A client can retrieve the information about the service from the registry and invoke the service using this information. If the registry provides IP addresses, it acts as a local DNS server, because typically the registry is not open to the general Internet but is within the environment of the application.

[![Figure 4.2 An instance of a service registers itself with the registry, the client queries the registry for the address of the service and invokes the service.  [Notation: Architecture]](figure_4.2.png)](figure_4.2.png "Figure 4.2 An instance of a service registers itself with the registry, the client queries the registry for the address of the service and invokes the service.  [Notation: Architecture]")

[Netflix Eureka](https://github.com/Netflix/eureka) is an example of a cloud service registry that acts as a DNS server and serves as a catalogue of available services, and can further be used to track aspects such as versioning, ownership, service level agreements (SLAs) for the set of services in an organization. Extensions to the registry are further discussed in [Chapter 6](ch6.md)

#### Management of Resources

Two types of resource management decisions can be made globally and incorporated in the architecture: provisioning/deprovisioning VMs and managing variation in demand.

##### **Provisioning and Deprovisioning VMs**

[p70]

Determining which component controls the provisioning and deprovisioning of a new instance for a service is another important aspect. Three possibilities exist for the controlling component:

1. A service itself can be responsible for (de)provisioning additional instances.
2. A client or a component in the client chain can be responsible for (de) provisioning instances of a service
3. An external component monitors the performance of service instances (e.g., their CPU load) and (de)provisions an instance when the load reaches a given threshold. Amazon’s autoscaling groups provide this capability, in collaboration with the CloudWatch monitoring system.

##### **Managing Demand**

The number of instances of an individual service that exist should reflect the demand on the service from client requests. We just discussed several different methods for provisioning and deprovisioning instances, and these methods make different assumptions about how demand is managed.

[p71]

* One method for managing demand is to monitor performance.
* Another possible technique is to use SLAs to control the number of instances.

#### Mapping Among Architectural Elements

We discuss two different types of mappings: work assignments and allocation. Both of these are decisions that are made globally.

* **Work assignments**. A single team may work on multiple modules, but having multiple development teams work on the same module requires a great deal of coordination among those development teams.
    * Since coordination takes time, an easier structure is to package the work of a single team into modules and develop interfaces among the modules to allow modules developed by different teams to interoperate. In fact, the original definition of a module by David Parnas in the 1970s was as a work assignment of a team.
    * Although not required, it is reasonable that each component (i.e., microservice) is the responsibility of a single development team. That is, the set of modules that, when linked, constitute a component are the output of a single development team. This does not preclude a single development team from being responsible for multiple components but it means that any coordination involving a component is settled within a single development team, and that any coordination involving multiple development teams goes across components. Given the set of constraints on the architecture we are describing, cross-team coordination requirements are limited.
* **Allocation**. Allocation. Each component (i.e., microservice) will exist as an independent deployable unit. This allows each component to be allocated to a single (virtual) machine or container, or it allows multiple components to be allocated to a single (virtual) machine. The redeployment or upgrade of one microservice will not affect any other microservices. This choice is explored in [Chapter 6](ch6.md)

### Quality Discussion of Microservice Architecture
