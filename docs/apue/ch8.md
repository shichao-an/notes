### **Chapter 8. Process Control**

### Process Identifiers

Every process has a unique process ID, a non-negative integer. As processes terminate, their IDs can be reused. <u>Most UNIX systems implement algorithms to delay reuse so that newly created processes are assigned IDs different from those used by processes that terminated recently. This prevents a new process from being mistaken for the previous process to have used the same ID.</u>

There are some special processes, but the details differ from implementation to implementation:

* Process ID 0: scheduler process (often known as the **swapper**), which is part of the kernel and is known as a system process
* Process ID 1: `init` process, invoked by the kernel at the end of the bootstrap procedure.
    * It is responsible for bringing up a UNIX system after the kernel has been bootstrapped. `init` usually reads the system-dependent initialization files (`/etc/rc*` files or `/etc/inittab` and the files in `/etc/init.d`) and brings the system to a certain state.
    * It never dies.
    * It is a normal user process, not a system process within the kernel.
    * It runs with superuser privileges.

<u>Each UNIX System implementation has its own set of kernel processes that provide operating system services.</u> For example, on some virtual memory implementations of the UNIX System, process ID 2 is the *pagedaemon*. This process is responsible for supporting the paging of the virtual memory system.
