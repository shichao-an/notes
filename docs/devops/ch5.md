### **Chapter 5. Building and Testing**

### Introduction

The infrastructure used to support the development and deployment process should support the following requirements (some ignored):

* The code produced by one team can be easily integrated with code produced by other teams.
* An integrated version of the system can be easily deployed into various environments (e.g., testing, staging, and production).
* An integrated version of the system can be easily and fully tested without affecting the production version of the system.
* A recently deployed new version of the system can be closely supervised.
* Older versions of the code are available in case a problem develops once the code has been placed into production.
* Code can be rolled back in the case of a problem.

A **deployment pipeline** (as shown in the figure below) consists of the steps that are taken between a developer committing code and the code actually being promoted into normal production, while ensuring high quality.

[![Figure 5.1 Deployment pipeline [Notation: BPMN]](figure_5.1.png)](figure_5.1.png "Figure 5.1 Deployment pipeline [Notation: BPMN]")

The deployment pipeline has following steps:

1. **Pre-commit tests**. The developer performs a series of pre-commit tests on their local environment
2. **Commit**. The developer commits code to the joint versioning system
3. **Integration tests**. A commit then triggers an integration build of the service being developed. This build is tested by integration tests.
4. **Staging tests**. If these tests are successful, the build is promoted to a quasi-production environment, the staging environment, where it is tested once more.
5. **Production**. Then, it is promoted to production under close supervision for another period of close supervision
6. **Normal production**. It is promoted to normal production.

The specific tasks may vary a bit for different organizations. For example, a small company may not have a staging environment or special supervision for a recently deployed version. A larger company may have several different production environments for different purposes. Some of these different production environments are described in [Chapter 6](ch6.md).

Some definitions:

* **Continuous integration** is to have automatic triggers between one phase and the next, up to <u>integration tests</u>.
    * If the build is successful then integration tests are triggered. If not, the developer responsible for the failure is notified.
* **Continuous delivery** is having automated triggers as far as the <u>staging system</u>.
* **Continuous deployment** means that the next to last step (deployment into the production system) is automated as well.

Once a service is deployed into production it is closely monitored for a period and then it is promoted into normal production. At this final stage, monitoring and testing still exist but the service is no different from other services in this regard. In this chapter, we are concerned with the building and testing aspects of this pipeline.

[Chapter 6](ch6.md) describes deployment practices, and [Chapter 7](ch7.md) discusses monitoring methods.

### Moving a System Through the Deployment Pipeline

Committed code moves through the steps shown in [Figure 5.1](figure_5.1.png). It is moved by tools, which are controlled by their programs (called *scripts* in this context) or by developer/operator commands. Two aspects of this movement are of interest in this section:

1. Traceability
2. The environment associated with each step of the pipeline

#### Traceability

Traceability means that, for any system in production, it is possible to determine exactly how it came to be in production. This means keeping track not only of source code but also of all the commands to all the tools that acted on the elements of the system.

A movement called **Infrastructure as Code** uses the rationale that:

* The scripts and associated configuration parameters should be kept under version control, just as the application code.
* Tests are also maintained in version control.
* Configuration parameters can be kept as files that are stored in version control or handled through dedicated configuration management systems.

Treating infrastructure-as-code means that this code should be subject to the same quality control as application source code.

A complication to the requirement to keep everything in version control is the treatment of third-party software such as Java libraries. Software project management tools like Apache Maven can go a long way to managing the complexities of library usage. [p82]

#### The Environment

An executing system can be viewed as a collection of executing code, an environment, configuration, systems outside of the environment with which the primary system interacts, and data.

[![Figure 5.2 A sample environment [Notation: Architecture]](figure_5.2.png)](figure_5.2.png "Figure 5.2 A sample environment [Notation: Architecture]")

As the system moves through the deployment pipeline, these items work together to generate the desired behavior or information:

* **Pre-commit**. The environment is typically a laptop or a desktop, the external systems are stubbed out or mocked, and only limited data is used for testing. Read-only external systems (e.g. RSS feed) can be accessed during the pre-commit stage. Configuration parameters should reflect the environment and also control the debugging level.
* **Build and integration testing**. The environment is usually a continuous integration server.
    * The code is compiled, and the component is built and baked into a VM image. The image can be either heavily or lightly baked (see the later section on [packaging](#packaging)).
    * During integration testing, a set of test data forms a test database (not production), which consists of a sufficient amount of data to perform the automated tests associated with integration.
    * The configuration parameters connect the built system with an integration testing environment
* **UAT/staging/performance testing**. The environment is as close to production as possible.
    *  Automated acceptance tests are run, and stress testing is performed through the use of artificially generated workloads.
    * The database should have some subset of actual production data in it. The subset should be large enough to enable the tests to be run in a realistic setting.
    * Configuration parameters connect the tested system with the larger test environment. Access to the production database should not be allowed from the staging environment.
* **Production**. The production environment should access the live database and have sufficient resources to adequately handle its workload. Configuration parameters connect the system with the production environment.

The configuration for each of these environments will be different, for example:

* Logging. Logging in development environment is usually in much detailed fashion to help debugging, since the performance overhead created does not matter as much.
* Credentials. The credentials for accessing production resources (e.g. the live customer database), should not be made available to developers.

<u>While some changes in configuration are unavoidable, it is important to keep these changes to a minimum to prevent affecting the behavior of the system. As such, testing with a vastly different configuration from the production system will not be helpful.</u>

Wikipedia has a longer list of environments:

* Local: Developer’s laptop/desktop/workstation
* Development: Development server, a.k.a. sandbox
* Integration: Continuous integration (CI) build target, or for developer testing of side effects
* Test/QA: For functional, performance testing, quality assurance, etc.
* UAT: User acceptance testing
* Stage/Pre-production: Mirror of production environment
* Production/Live: Serves end-users/clients

### Crosscutting Aspects

This section discusses various crosscutting aspects of a deployment pipeline:

* **Test harnesses**. A test harness is a collection of software and test data configured to test a program unit by running it under varying conditions and monitoring its behavior and output.
    * Test harnesses are essential in order to automate tests.
    * A critical feature of a test harness is that it generates a report. It should, at a minimum, identify which tests failed.
    * Most of the types of tests discussed in this chapter should be able to be automated and driven by the test harness.
* **Negative tests**. It is also important to test if the system behaves in a defined way without the assumptions, which are about the environment hold and the user performs actions expectedly (in the right order with the right inputs).
    * Examples are users performing actions in the wrong order (clicking buttons, calling commands) or simulated connectivity issues(external services becoming unavailable, connections being dropped at unexpected points in time).
    * The common expectation is that:
        * The application should degrade or fail gracefully
        * If failure is unavoidable, provide meaningful error messages and exit in a controlled manner.
* **Regression testing**.
* **Traceability of errors** (also referred to as lineage or a form of provenance).

### Development and Pre-commit Testing

### Build and Integration Testing

#### Build Scripts

#### Packaging

#### Continuous Integration and Build Status

#### Integration Testing

### UAT/Staging/Performance Testing

### Production

#### Early Release Testing

This subsection focuses on the testing method. [Chapter 6](ch6.md) discusses how to release the application to achieve early release testing.

* **Beta release** is the most traditional approach. A selected few users, often subscribed to a beta program, are given access to a prerelease (beta) version of the application. Beta testing is primarily used for [on-premises use of software](https://en.wikipedia.org/wiki/On-premises_software).
* **Canary testing** is a method of deploying the new version to a few servers first, to see how they perform. It is the cloud equivalent of beta testing.
    * One or a few of the application servers are upgraded from the current version to a stable, well-tested release candidate version of the application. Load balancers direct a small portion of the user requests to the candidate version, while monitoring is ongoing. If the candidate servers are acceptable in terms of some metrics (e.g., performance, scalability, number of errors) the candidate version is rolled out to all servers.
* **A/B testing** is similar to canary testing, except that the tests are intended
to determine which version performs better in terms of certain business-level key performance indicators. For example, a new algorithm for recommending products may increase revenue, or UI changes may lead to more click-throughs.

#### Error Detection

#### Live Testing

### Incidents
