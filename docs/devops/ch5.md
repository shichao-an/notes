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
    * Regression testing seeks to uncover new software bugs, or regressions, in existing functional and non-functional areas of a system after changes such as enhancements, patches or configuration changes, have been made to them.
    * Another use of regression testing is to ensure that any fixed bugs are not reintroduced later on.
    * It is possible to automate the regression test creation: Failures detected at later points in the deployment pipeline (during staging testing) can be automatically recorded and added as new tests into unit or integration testing.
* **Traceability of errors** (also referred to as lineage or a form of provenance).

### Development and Pre-commit Testing

#### Version Control and Branching

Core features of version control are: the ability to identify distinct versions of the source code, sharing code revisions between developers, recording who made a change from one version to the next, and recording the scope of a change.

* CVS and SVN are centralized solutions, where each developer checks out code from a central server and commits changes back to that server.
* Git is a distributed version control system: Every developer has a local clone (or copy) of a Git repository that holds all contents.
    * Commits are done to the local repository.
    * A set of changes can be synchronized against a central server, where changes from the server are synchronized with the local repository (using the `pull` command) and local changes can be forwarded to the server (using the `push` command).
    * Push can only be executed if the local repository is up-to-date, hence a push is usually preceded by a pull.
    * During the pull, changes to the same files are merged automatically. However, this merge can fail, in which case the developer has to resolve any conflicts locally. The resulting changes from an (automatic or semi-manual) merge are committed locally and then pushed to the server.

Almost all version control systems support the creation of new branches. A branch is essentially a copy of a repository (or a portion) and allows independent evolution of two or more streams of work.

For example, if part of the development team is working on a set of new features while a previous version is in production and a critical error is discovered in the production system, the version currently in production must be fixed. This can be done by creating a branch for the fix based on the version of the code that was released into production.  After the error has been fixed and the fixed version has been released into production, the branch with the fix is typically merged back into the main branch (also called the trunk, mainline, or master branch).

This example is useful in highlighting the need for traceability that we discussed previously. In order to fix the error, the code that was executing needs to be determined (traceability of the code). The error may be due to a problem with the configuration (traceability of the configuration) or with the tool suite used to promote it into production (traceability of the infrastructure).

Although the branch structure is useful and important, two problems exist in using branches.

1. You may have too many branches and lose track of which branch you should be working on for a particular task. For this reason, short-lived tasks should not create a new branch.
2. Merging two branches can be difficult. Different branches evolve concurrently, and often developers touch many different parts of the code.

An alternative to branching is to have all developers working on the trunk directly. Instead of reintegrating a big branch, a developer deals with integration issues at each commit, which is a simpler solution, but requires more frequent action than using branches.

The problem with doing all of the development on one trunk is that a developer may be working on several different tasks within the same module simultaneously.  When one task is finished, the module cannot be committed until the other tasks are completed. To do so would introduce incomplete and untested code for the new feature into the deployment pipeline. Solving this problem is the rationale for feature toggles.

#### Feature Toggles

A **feature toggle** (also called a **feature flag** or a **feature switch**) is an "if" statement around immature code. A new feature that is not ready for testing or production is disabled in the source code itself, for example, by setting a global Boolean variable.

However, there are certain dangers in feature toggles.

* Lesson 1: Do not reuse toggle names.
* Lesson 2: Integrate the feature and get rid of the toggle tests as soon as is timely.

When there are many feature toggles, managing them becomes complicated. It would be useful to have a specialized tool or library that knows about all of the feature toggles in the system, is aware of their current state, can change their state, and can eventually remove the feature toggle from your code base.

#### Configuration Parameters

A configuration parameter is an externally settable variable that changes the behavior of a system. A configuration setting may be: the language you wish to expose to the user, the location of a data file, the thread pool size, the color of the background on the screen, or the feature toggle settings.

In this book, we are interested in configuration settings that either control the relation of the system to its environment or control behavior related to the stage in the deployment pipeline in which the system is currently run.

[p90]

One decision to make about configuration parameters is whether the values should be the same in the different steps of the deployment pipeline. If the production system’s values are different, you must also decide whether they must be kept confidential. These decisions yield three categories.

1. Values are the same in multiple environments. Feature toggles and performance-related values (e.g., database connection pool size) should be the same in performance testing/UAT/staging and production, but may be different on local developer machines.
2. Values are different depending on the environment. The number of virtual machines (VMs) running in production is likely bigger than that number for the testing environments.
3. Values must be kept confidential. The credentials for accessing the production database or changing the production infrastructure must be kept confidential and only shared with those who need access to them: no sizeable organization can take the risk that a development intern walks away with the customer data.

Keeping values of configuration parameters confidential introduces some complications to the deployment pipeline. The overall goal is to make these values be the current ones in production but keep them confidential.

* One technique is to give meta-rights to the deployment pipeline and restrict access to the pipeline.  When, for instance, a new VM is deployed into production, the deployment pipeline can give it rights to access a key store with the credentials required to operate in production.
* Another technique is for the deployment pipeline to set the network configuration in a virtual environment for a machine such that it gets to access the production database servers, the production configuration server, and so forth, if the machine is to be part of the production environment. In this case, only the deployment pipeline should have the right to create machines in the production portion of the network.

#### Testing During Development and Pre-commit Tests

[p91]

* **Test-driven development**. When following this philosophy, before writing the actual code for a piece of functionality, you develop an automated test for it. Then the functionality is developed, with the goal of fulfilling the test. Once the test passes, the code can be refactored to meet higher-quality standards.
* **Unit tests**. Unit tests are code-level tests, each of which is testing individual classes and methods.

While these tests can be run by the developer at any point, a modern practice is to enforce **pre-commit tests**. These tests are run automatically before a commit is executed. Typically they include a relevant set of unit tests, as well as a few smoke tests. <u>Smoke tests are specific tests that check in a fast (and incomplete) manner that the overall functionality of the service can still be performed.</u> The goal is that any bugs that pass unit tests but break the overall system can be found long before integration testing. Once the pre-commit tests succeed, the commit is executed.

### Build and Integration Testing

Build is the process of creating an executable artifact from input such as source code and configuration. It primarily consists of compiling source code and packaging all files that are required for execution. Once the build is complete, a set of automated tests are executed that test whether the integration with other parts of the system uncovers any errors. The unit tests can be repeated here to generate a history available more broadly than to a single developer.

#### Build Scripts

[p91-92]

The build and integration tests are performed by a continuous integration (CI) server. The input to this server should be scripts that can be invoked by a single command. This practice ensures that the build is repeatable and traceable.

#### Packaging

The goal of building is to create something suitable for deployment. There are several standard methods of packaging the elements of a system for deployment.  The appropriate method of packaging will depend on the production environment.  Some packaging options are:

* **Runtime-specific packages**, such as Java archives, web application archives, and federal acquisition regulation archives in Java, or .NET assemblies.
* **Operating system packages**. If the application is packaged into software packages of the target OS (such as the Debian or Red Hat package system),
a variety of well-proven tools can be used for deployment.
* **VM images** can be created from a template image, to include the changes from the latest revision.
* **Lightweight containers**

There are two dominant strategies for applying changes in an application when using VM images or lightweight containers: **heavily baked** versus **lightly baked images.** Heavily baked images cannot be changed at runtime. This concept is also termed **immutable servers**: Once a VM has been started, no changes (other than configuration values) are applied to it.

[p93]

#### Continuous Integration and Build Status

[p93-94]

#### Integration Testing

Integration testing is the step in which the built executable artifact is tested.  The environment includes connections to external services, such as a surrogate database. Including other services requires mechanisms to distinguish between production and test requests, so that running a test does not trigger any actual transactions, such as production, shipment, or payment.

[p94-95]

### UAT/Staging/Performance Testing

[p95]

Staging is the last step of the deployment pipeline prior to deploying the system into production. The staging environment mirrors, as much as possible, the production environment. The types of tests that occur at this step are the following:

* **User acceptance tests** (UATs) are tests where prospective users work with a current revision of the system through its UI and test it, either according to a test script or in an exploratory fashion.
* **Automated acceptance tests** are the automated version of repetitive UATs. Such tests control the application through the UI, trying to closely mirror what a human user would do. Automation takes some load off the UATs, while ensuring that the interaction is done in exactly the same way each time. As such, automated acceptance tests enable a higher rate of repetition than is possible with relatively expensive human testers.
* **Smoke tests** are a subset of the automated acceptance tests that are used to quickly analyze if a new commit breaks some of the core functions of the application.
* **Nonfunctional tests** test aspects such as performance, security, capacity, and availability.

### Production

#### Early Release Testing

This subsection focuses on the testing method. [Chapter 6](ch6.md) discusses how to release the application to achieve early release testing.

* **Beta release** is the most traditional approach. A selected few users, often subscribed to a beta program, are given access to a prerelease (beta) version of the application. Beta testing is primarily used for [on-premises use of software](https://en.wikipedia.org/wiki/On-premises_software).
* **Canary testing** is a method of deploying the new version to a few servers first, to see how they perform. It is the cloud equivalent of beta testing.
    * One or a few of the application servers are upgraded from the current version to a stable, well-tested release candidate version of the application. Load balancers direct a small portion of the user requests to the candidate version, while monitoring is ongoing. If the candidate servers are acceptable in terms of some metrics (e.g., performance, scalability, number of errors) the candidate version is rolled out to all servers.
* **A/B testing** is similar to canary testing, except that the tests are intended
to determine which version performs better in terms of certain business-level key performance indicators. For example, a new algorithm for recommending products may increase revenue, or UI changes may lead to more click-throughs.

#### Error Detection

Even systems that have passed all of their tests may still have errors. <u>These errors can be either functional or nonfunctional.</u> Techniques used to determine nonfunctional errors include monitoring of the system for indications of poor behavior.  This can consist of monitoring the timing of the response to user requests, the queue lengths, and so forth.

Once an alert has been raised, tracking and finding its source can be quite difficult. Logs produced by the system are important in enabling this tracking ([Chapter 7](ch7.md)). It is important that the provenance of the software causing the alert and the user requests that triggered the alert all can be easily obtained. Enabling the diagnosis of errors is one of the reasons for the emphasis on using automated tools that maintain histories of their activities.

<u>In any case, once the error is diagnosed and repaired, the cause of the error can be made one of the regression tests for future releases.</u>

#### Live Testing

Monitoring is a passive form of testing: the systems run in their normal fashion and data is gathered about their behavior and performance. Another form of testing after the system has been placed in production is to actually perturb the running system. This form is called **live testing**. Netflix has a set of test tools called the Simian Army. The elements of the Simian Army are both passive and active. The passive elements examine running instances to determine unused resources, expired certificates, health checks on instances, and adherence to best practices.

### Incidents

No matter how well you test or organize a deployment, errors will exist once a system gets into production. Understanding potential causes of post-deployment errors helps to more quickly diagnose problems. Here are several anecdotes we have heard from IT professionals:

* A developer connected test code to a production database.
* Version dependencies existing among the components. When dependencies exist among components, the order of deployment becomes important and it is possible if the order is incorrect that errors will result.
* A change in a dependent system coincided with a deployment. For instance, a dependent system removed a service on which an application depended, and this removal happened after all of the staging tests had been passed.
* Parameters for dependent systems were set incorrectly. For example, queues overflowed or resources were exhausted in dependent systems. Adjusting the configurations for the dependent systems and adding monitoring rules were the fixes adopted by the affected organization.

### Summary

Having an appropriate deployment pipeline is essential for rapidly creating and deploying systems. The pipeline has at least five major step: pre-commit, build and integration testing, UAT/staging/performance tests, production, and promoting to normal production.

Each step operates within a different environment and with a set of different configuration parameter values—although this set should be limited in size as much as possible. As the system moves through the pipeline, you can have progressively more confidence in its correctness. Even systems promoted to normal production, however, can have errors and can be improved from the perspective of performance or reliability. Live testing is a mechanism to continue to test even after placing a system in production or promoting it to normal production.

Feature toggles are used to make code inaccessible during production. They allow incomplete code to be contained in a committed module. They should be removed when no longer necessary because otherwise they clutter the code base; also, repurposed feature toggles can cause errors.

Tests should be automated, run by a test harness, and report results back to the development team and other interested parties. Many incidents after placing a system in production are caused by either developer or configuration errors.

An architect involved in a DevOps project should ensure the following:

* The various tools and environments are set up to enable their activities to be traceable and repeatable.
* Configuration parameters should be organized based on whether they will change for different environments and on their confidentiality.
* Each step in the deployment pipeline has a collection of automated tests with an appropriate test harness.
* Feature toggles are removed when the code they toggle has been placed into production and been judged to be successfully deployed.
