### **Chapter 9. Process Relationships**

### Introduction

Every process has a parent process (the initial kernel-level process is usually its own parent). The parent is notified when the child terminates, and the parent can obtain the child’s exit status.

This chapter details process groups and the concept of session introduced by POSIX.1, as well as relationship between the login shell that is invoked when a user logs in and all the processes that are started from the login shell.

The concept of UNIX system signal mechanism in [Chapter 10](/apue/ch10/) is needed.


### Terminal Logins

In early UNIX systems, the terminals (dumb terminals that are hard-wired connected to the host) were either local (directly connected) or remote (connected through a modem). These logins came through a terminal device driver in the kernel. [p285]

As bitmapped graphical terminals became available, windowing systems were developed to provide users with new ways to interact with host computers.  Applications were developed to create "terminal windows" to emulate character-based terminals, allowing users to interact with hosts in familiar ways (i.e., via the shell command line).

Today, some platforms allow you to start a windowing system after logging in, whereas other platforms automatically start the windowing system for you. In the latter case, you might still have to log in, depending on how the windowing system is configured (some windowing systems can be configured to log you in automatically).

The procedure that we now describe is used to log in to a UNIX system using a terminal. The procedure is similar regardless of the type of terminal we use. It could be a:

* character-based terminal,
* a graphical terminal emulating a simple character-based terminal,
* or a graphical terminal running a windowing system.

#### BSD Terminal Logins

The file `/etc/ttys` (created by the system administrator) has one line per terminal device. Each line specifies the name of the device and other parameters (e.g. baud rate) that are passed to the `getty` program.

After the system is bootstrapped, the kernel creates the `init` process (PID 1) which brings the system up in multiuser mode. The `init` process reads the file `/etc/ttys` and, for every terminal device that allows a login, does a `fork` followed by an `exec` of the program `getty`.

[![Figure 9.2 State of processes after login has been invoked](figure_9.2.png)](figure_9.2.png "Figure 9.2 State of processes after login has been invoked")

All the processes shown in the figure above have a real user ID of 0 and an effective user ID of 0 (they all have superuser privileges). All the processes other than the original `init` process have a parent process ID of 1.

* The `init` process `exec`s the `getty` program with an empty environment.
* `getty` calls `open` to open terminal device for reading and writing. File descriptors 0, 1, and 2 are set to the device.
* Then, `getty` outputs something like `login:` and waits for us to enter our user name. `getty` can detect special characters to change the terminal's speed (baud rate). [p287]
* When we enter our user name, `getty`’s job is complete, and it then invokes the `login` program, similar to:

        execle("/bin/login", "login", "-p", username, (char *)0, envp);

* Though `init` invokes `getty` with an empty environment, `getty` creates an environment for `login` (the `envp` argument) with the name of the terminal (something like `TERM=foo`, where the type of terminal `foo` is taken from the `gettytab` file) and any environment strings that are specified in the `gettytab`. The `-p` flag to `login` tells it to preserve the environment that it is passed and to add to that environment, not replace it.
* `login` does the following things:
    * It calls `getpwnam` to fetch our password file entry.
    * It calls `getpass(3)` to display the prompt `Password:` and read our password (with echoing disabled).
    * It calls `crypt(3)` to encrypt the password that we entered and compares the encrypted result to the `pw_passwd` field from our shadow password file entry.
    * If the login attempt fails because of an invalid password (after a few tries), `login` calls `exit` with an argument of 1. This termination will be noticed by the parent (`init`), and it will do another `fork` followed by an `exec` of `getty`, starting the procedure over again for this terminal.

This is the traditional authentication procedure used on UNIX systems. Modern UNIX systems have evolved to support multiple authentication procedures. FreeBSD, Linux, Mac OS X, and Solaris all support a more flexible scheme known as PAM ([Pluggable Authentication Modules](https://en.wikipedia.org/wiki/Pluggable_authentication_module)). PAM allows an administrator to configure the authentication methods to be used to access services that are written to use the PAM library. [p288]

If we log in correctly, `login` will:

* Change to our home directory (`chdir`)
* Change the ownership of our terminal device (`chown`) so we own it
* Change the access permissions for our terminal device so we have permission to read from and write to it
* Set our group IDs by calling `setgid` and `initgroups`
* Initialize the environment with all the information that login has:
    * our home directory (`HOME`),
    * shell (`SHELL`),
    * user name (`USER` and `LOGNAME`),
    * and a default path (`PATH`).
* Change to our user ID (`setuid`) and invoke our login shell, as in

        execl("/bin/sh", "-sh", (char *)0);

    The minus sign as the first character of `argv[0]` is a flag to all the shells that indicates they are being invoked as a **login shell**. The shells can look at this character and modify their start-up accordingly.

The `login` can optionally print the [message-of-the-day](https://en.wikipedia.org/wiki/Motd_(Unix)) file, check for new mail, and performs other tasks.

Since it is called by a superuser process, `setuid` changes all three user IDs: the real user ID, effective user ID, and saved set-user-ID. The call to `setgid` that was done earlier by `login` has the same effect on all three group IDs.

At this point, our login shell is running. Its parent process ID is the original `init` process (process ID 1), so when our login shell terminates, `init` is sent a `SIGCHLD` signal and it starts the whole procedure over again for this terminal. File descriptors 0, 1, and 2 for our login shell are set to the terminal device. See the figure below:

[![Figure 9.3 Arrangement of processes after everything is set for a terminal login](figure_9.3.png)](figure_9.3.png "Figure 9.3 Arrangement of processes after everything is set for a terminal login")

Our login shell now reads its start-up files (`.profile` for the Bourne shell and Korn shell; `.bash_profile`, `.bash_login`, or `.profile` for the GNU Bourne-again shell; and `.cshrc` and `.login` for the C shell). These start-up files usually change some of the environment variables and add many other variables to the environment. For example, most users set their own `PATH` and often prompt for the actual terminal type (`TERM`). When the start-up files are done, we finally get the shell’s prompt and can enter commands.

#### Mac OS X Terminal Logins

On Mac OS X, the terminal login process follows essentially the same steps as in the BSD login process (since Mac OS X is based in part on FreeBSD) with the following differences:

* The work of `init` is performed by `launchd`.
* We are presented with a graphical-based login screen from the start.

#### Linux Terminal Logins

The Linux login procedure is very similar to the BSD procedure. The login command is derived from 4.3BSD. The main difference is in terminal configuration.

Some Linux distributions ship with a version of the `init` program that uses administrative files patterned after System V’s `init` file formats. where `/etc/inittab` specifies the terminal devices for which `init` should start a `getty` process. Other Linux distributions, such as Ubuntu, ship with a version of init that is known as "[Upstart](https://en.wikipedia.org/wiki/Upstart)". It uses configuration files named `*.conf` that are
stored in the `/etc/init` directory. For example, the specifications for running `getty` on `/dev/tty1` might be found in the file `/etc/init/tty1.conf`.

Depending on the version of `getty` in use, the terminal characteristics are specified either on the command line (as with `agetty`) or in the file `/etc/gettydefs` (as with `mgetty`).

#### Solaris Terminal Logins

[p290]


### Network Logins

The main difference between a serial terminal login and a network login is that the connection between the terminal and the computer isn’t point-to-point. In this case, `login` is simply a service available, just like any other network service, such as FTP or SMTP.

With the terminal logins, `init` knows which terminal devices are enabled for logins and spawns a `getty` process for each device. In the case of network logins, however, all the logins come through the kernel’s network interface drivers (e.g., the Ethernet driver), and we don’t know ahead of time how many of these will occur. Instead of having a process waiting for each possible login, we now have to wait for a network connection request to arrive.

To allow the same software to process logins over both terminal logins and network logins, a software driver called a **pseudo terminal** (detailed in [Chapter 19](/apue/ch19/)) is used to emulate the behavior of a serial terminal and map terminal operations to network operations, and vice versa.


#### BSD Network Logins

In BSD, the `inetd` process, sometimes called the *Internet superserver*, waits for most network connections.

As part of the system start-up, `init` invokes a shell that executes the shell script `/etc/rc`, which starts `inetd` along with other daemons. Once the shell script terminates, the parent process of `inetd` becomes `init`; `inetd` waits for TCP/IP connection requests to arrive at the host. When a connection request arrives for it to handle, `inetd` does a `fork` and `exec` of the appropriate program.

Assume a TCP connection request arrives for the TELNET server (a remote login application). The remote user initiates the login by starting the TELNET client:

```sh
telnet hostname
```

The client opens a TCP connection to *hostname* and the user who started the client program is now logged in to the server’s host. The figure below shows the sequence of processes involved in executing the TELNET server, called `telnetd`:

[![Figure 9.4 Sequence of processes involved in executing TELNET server](figure_9.4.png)](figure_9.4.png "Figure 9.4 Sequence of processes involved in executing TELNET server")

Then, <u>the `telnetd` process then opens a pseudo terminal device and splits into two processes using `fork`,</u> which do the following:

* The parent (`telnetd`) handles the communication across the network connection.
* The child `exec`s the `login` program.
* The parent and the child are connected through the pseudo terminal. Before doing the `exec`, the child sets up file descriptors 0, 1, and 2 to the pseudo terminal.
* If we log in correctly, login performs the same steps described in [Section 9.2](#bsd-terminal-logins): it changes to our home directory and sets our group IDs, user ID, and our initial environment. Then `login` replaces itself with our login shell by calling `exec`.

[![Figure 9.5 Arrangement of processes after everything is set for a network login](figure_9.5.png)](figure_9.5.png "Figure 9.5 Arrangement of processes after everything is set for a network login")

Whether we log in through a terminal ([Figure 9.3](figure_9.3.png)) or a network ([Figure 9.5](figure_9.5.png)), we have a login shell with its standard input, standard output, and standard error connected to either a terminal device or a pseudo terminal device.

In the coming sections, we'll see that the login shell is the start of a POSIX.1 session, and that the terminal or pseudo terminal is the controlling terminal for the session.

#### Mac OS X Network Logins

The network login on Mac OS X is identical to that on BSD, except that the `telnet` daemon is run from `launchd`. By default, the `telnet` daemon is disabled on Mac OS X (although it can be enabled with the `launchctl(1)` command). The preferred way to perform a network login on Mac OS X is with `ssh`, the secure shell command.

#### Linux Network Logins

Network logins under Linux are the same as under BSD, except that some distributions use an alternative `inetd` process called the extended Internet services daemon, `xinetd`. The `xinetd` process provides a finer level of control over services it starts compared to `inetd`.

#### Solaris Network Logins

[p293]

### Process Groups

In addition to having a process ID, each process belongs to a **process group**.

* A process group is a collection of one or more processes (usually associated with the same job) that can receive signals from the same terminal.
* Each process group has a unique process group ID. Process group IDs are similar to process IDs: they are positive integers and can be stored in a `pid_t` data type.

The function `getpgrp` returns the process group ID of the calling process. The `getpgid` function took a *pid* argument and returned the process group for that process.

* [apue_getpgrp.h](https://gist.github.com/shichao-an/08bcc3cf9a23ca95c00a)

<script src="https://gist.github.com/shichao-an/08bcc3cf9a23ca95c00a.js"></script>

For `getpgid`, if *pid* is 0, the process group ID of the calling process is returned. Thus,

```c
getpgid(0);
```

is equivalent to:

```c
getpgrp();
```

Each process group can have a **process group leader**, whose process group ID equals to its process ID.

#### Process group lifetime

The process group life time is the period of time that begins when the group is created and ends when the last remaining process leaves the group. It is possible for a process group leader to create a process group, create processes in the group, and then terminate. The process group still exists, as long as at least one process is in the group, regardless of whether the group leader terminates. The last remaining process in the process group can either terminate or enter some other process group.

#### `setpgid` function

A process can join an existing process group or creates a new process group by calling `setpgid`.

* [apue_setpgid.h](https://gist.github.com/shichao-an/0b1832544be00d3a9490)

<script src="https://gist.github.com/shichao-an/0b1832544be00d3a9490.js"></script>

The `setpgid` function sets the process group ID of the process whose process ID equals *pid* to *pgid*.

Arguments:

* If *pid* == *pgid*, the process specified by *pid* becomes a process group leader.
* If *pid* == 0, the process ID of the caller is used.
* If *pgid* == 0, then the specified *pid* is used as the process group ID.

Rules:

* A process can set the process group ID of only itself or any of its children.
* A process cannot change the process group ID of one of its children after that child has called one of the `exec` functions.

##### Job-control shells

In most job-control shells, this function is called after a `fork` to have the parent set the process group ID of the child, and to have the child set its own process group ID. <u>One of these calls is redundant, but by doing both, we are guaranteed that the child is placed into its own process group before either process assumes that this has happened.  If we didn’t do this, we would have a race condition, since the child’s process group membership would depend on which process executes first.</u> (See [Doubts and Solutions](##doubts-and-solutions) for details) [p294]


##### Process groups and signals

We can send a signal to either a single process (identified by its process ID) or a process group (identified by its process group ID). Similarly, the `waitpid` function lets us wait for either a single process or one process from a specified process group.

### Sessions

A session is a collection of one or more process groups.

[![Figure 9.6 Arrangement of processes into process groups and sessions](figure_9.6_600.png)](figure_9.6.png "Figure 9.6 Arrangement of processes into process groups and sessions")

The processes in a process group are usually placed there by a shell pipeline. The arrangement in the figure above is generated by the shell commands of the form:

```sh
proc1 | proc2 &
proc3 | proc4 | proc5
```

#### The `setsid` function

A process establishes a new session by calling the `setsid` function.

* [apue_setsid.h](https://gist.github.com/shichao-an/48edc52023515e0df704)

<script src="https://gist.github.com/shichao-an/48edc52023515e0df704.js"></script>

If the calling process is not a process group leader, this function creates a new session. Three things happen:

1. The process becomes the **session leader** of this new session. (A session leader is the process that creates a session.) The process is the only process in this new session
2. The process becomes the process group leader of a new process group. The new process group ID is the process ID of the calling process.
3. The process has no controlling terminal. If the process had a controlling terminal before calling `setsid`, that association is broken.

This function returns an error if the caller is already a process group leader.

#### Ensuring the successful call of `setsid`

Since the `setsid` function returns an error if the caller is a process group leader, to ensure this is not the case, the usual practice is to call `fork` and have the parent terminate and the child continue. It is guaranteed that the child is not a process group leader, because the process group ID of the parent is inherited by the child, but the child gets a new process ID. Hence, it is impossible for the child’s process ID to equal its inherited process group ID.

#### Session Leader and Session ID

The Single UNIX Specification talks only about a "session leader"; there is no "session ID" similar to a process ID or a process group ID. A session leader is a single process that has a unique process ID, so we could talk about a session ID that is the process ID of the session leader. This concept of a session ID was introduced in SVR4.

#### The `getsid` function

The `getsid` function returns the process group ID of a process’s session leader.

* [apue_getsid.h](https://gist.github.com/shichao-an/745eaee552865545e529)

<script src="https://gist.github.com/shichao-an/745eaee552865545e529.js"></script>

If *pid* is 0, `getsid` returns the process group ID of the calling process’s session leader. For security reasons, some implementations may restrict the calling process from obtaining the process group ID of the session leader if *pid* doesn’t belong to the same session as the caller.

### Controlling Terminal

Sessions and process groups have a few other characteristics.

* A session can have a single **controlling terminal**. This is usually the terminal device (in the case of a [terminal login](##terminal-logins)) or pseudo terminal device (in the case of a [network login](#network-logins)) on which we log in.
* The session leader that establishes the connection to the controlling terminal is called the **controlling process**.
* The process groups within a session can be divided into a single **foreground process group** and one or more **background process groups**.
* If a session has a controlling terminal, it has a single foreground process group and all other process groups in the session are background process groups.
* Whenever we press the terminal’s interrupt key (often DELETE or Control-C), the interrupt signal is sent to all processes in the foreground process group.
* Whenever we press the terminal’s quit key (often Control-backslash), the quit signal is sent to all processes in the foreground process group.
* If a modem (or network) disconnect is detected by the terminal interface, the hang-up signal is sent to the controlling process (the session leader).

These characteristics are shown in the figure below:

[![Figure 9.7 Process groups and sessions showing controlling terminal](figure_9.7_600.png)](figure_9.7.png "Figure 9.7 Process groups and sessions showing controlling terminal")

Usually, the controlling terminal is established automatically when we log in.

#### Mechanisms of allocating a controlling terminal

##### System V

Systems derived from UNIX System V allocate the controlling terminal for a session when the session leader opens the first terminal device that is not already associated with a session, as long as the call to `open` does not specify the `O_NOCTTY` flag.

##### BSD

BSD-based systems allocate the controlling terminal for a session when the session leader calls `ioctl` with a request argument of `TIOCSCTTY` (the third argument is a null pointer). The session cannot already have a controlling terminal for this call to succeed. Normally, this call to `ioctl` follows a call to `setsid`, which guarantees that the process is a session leader without a controlling terminal.

Note that although Mac OS X 10.6.8 is derived from BSD, it behaves like System V when allocating a controlling terminal.

Method | FreeBSD 8.0 | Linux 3.2.0 | Mac OS X 10.6.8 | Solaris 10
------ | ----------- | ----------- | --------------- | ----------
`open` without `O_NOCTTY` | | x | x | x
`TIOCSCTTY` `ioctl` command | x | x | x | x

When a program wants to talk to the controlling terminal, regardless of whether the standard input or standard output is redirected, it can `open` the file `/dev/tty`. This special file is a synonym within the kernel for the controlling terminal. If the program doesn’t have a controlling terminal, the `open` of this device will fail.

The classic example is the `getpass(3)` function, which reads a password (with terminal echoing turned off, of course). [p298]

### `tcgetpgrp`, `tcsetpgrp`, and `tcgetsid` Functions

We need a way to tell the kernel which process group is the foreground process group, so that the terminal device driver knows where to send the terminal input and the terminal-generated signals. ([Figure 9.7](figure_9.7.png))

* [apue_tcgetpgrp.h](https://gist.github.com/shichao-an/93937e8a69a6f2971055)

<script src="https://gist.github.com/shichao-an/93937e8a69a6f2971055.js"></script>

* The function `tcgetpgrp` returns the process group ID of the foreground process group associated with the terminal open on *fd*.
* If the process has a controlling terminal, the process can call `tcsetpgrp` to set the foreground process group ID to *pgrpid*. The value of *pgrpid* must be the process group ID of a process group in the same session, and *fd* must refer to the controlling terminal of the session.

These two functions are normally called by job-control shells.

The `tcgetsid` function allows an application to obtain the process group ID for the session leader given a file descriptor for the controlling TTY.

* [apue_tcgetsid.h](https://gist.github.com/shichao-an/16ba6f5516fc48ec7f84)

<script src="https://gist.github.com/shichao-an/16ba6f5516fc48ec7f84.js"></script>

Applications that need to manage controlling terminals can use `tcgetsid` to identify the session ID of the controlling terminal’s session leader, which is equivalent to the session leader’s process group ID.

### Job Control

**Job control** allows us to start multiple jobs (groups of processes) from a single terminal and to control which jobs can access the terminal and which jobs are run in the background. Job control requires three forms of support:

1. A shell that supports job control
2. The terminal driver in the kernel must support job control
3. The kernel must support certain job-control signals

From our perspective, when using job control from a shell, we can start a job in either the foreground or the background. A job is simply a collection of processes, often a pipeline of processes.

For example, start a job consisting of one process in the foreground:

```sh
vi main.c
```

Start two jobs in the background (all the processes invoked by these background jobs are in the background.):

```sh
pr *.c | lpr &
make all &
```

#### Korn shell example

When we start a background job, the shell assigns it a job identifier and prints one or more of the process IDs.

```text
$ make all > Make.out &
[1] 1475
$ pr *.c | lpr &
[2] 1490
$   # just press RETURN
[2] + Done pr *.c | lpr &
[1] + Done make all > Make.out &
```

* The `make` is job number 1 and the starting process ID is 1475. The next pipeline is job number 2 and the process ID of the first process is 1490.
* When the jobs are done and we press RETURN, the shell tells us that the jobs are complete. The reason we have to press RETURN is to have the shell print its prompt. The shell doesn’t print the changed status of background jobs at any random time (only after we press RETURN and right before it prints its prompt, to let us enter a new command line). If the shell didn’t do this, it could produce output while we were entering an input line.
* The interaction with the terminal driver arises because a special terminal character affects the foreground job. The terminal driver looks for three special characters, which generate signals to (all processes in ) the foreground process group:
    * `SIGINT`: The interrupt character (typically DELETE or Control-C) generates `SIGINT`.
    * `SIGQUIT`: The quit character (typically Control-backslash) generates `SIGQUIT`.
    * `SIGTSTP`: The suspend character (typically Control-Z) generates `SIGTSTP`.

While we can have a foreground job and one or more background jobs, only the foreground job receives terminal input (the characters that we enter at the terminal). It is not an error for a background job to try to read from the terminal, but the terminal driver detects this and sends a special signal to the background job: `SIGTTIN`. This signal normally stops the background job; by using the shell, we are notified of this event and can bring the job into the foreground so that it can read from the terminal.

```text
cat > temp.foo &   # start in background, but it’ll read from standard input
[1] 1681
$                  # we press RETURN
[1] + Stopped (SIGTTIN) cat > temp.foo &
$ fg %1            # bring job number 1 into the foreground
cat > temp.foo     # the shell tells us which job is now in the foreground
hello, world       # enter one line
ˆD                 # type the end-of-file character
$ cat temp.foo     # check that the one line was put into the file
hello, world
```

* `SIGTTIN`: When the background `cat` tries to read its standard input (the controlling terminal), the terminal driver, knowing that it is a background job, sends the `SIGTTIN` signal to the background job.
* The shell detects the change in status of its child (see `wait` and `waitpid` function in [Section 8.6](/apue/ch8/#wait-and-waitpid-functions)) and tells us that the job has been stopped.
* The shell’s `fg` command move the stopped job into the foreground, which causes the shell to place the job into the foreground process group (tcsetpgrp) and send the continue signal (`SIGCONT`) to the process group.
* Since it is now in the foreground process group, the job can read from the controlling terminal.

Note that this example doesn’t work on Mac OS X 10.6.8. When we try to bring the cat command into the foreground, the read fails with errno set to EINTR. Since Mac OS X is based on FreeBSD, and FreeBSD works as expected, this must be a bug in Mac OS X.

There is an option that we can allow or disallow a background job to send its output to the controlling terminal. Normally, we use the `stty(1)` command to change this option.

```shell-session
$ cat temp.foo &   # execute in background
[1] 1719
$ hello, world     # the output from the background job appears after the prompt
we press RETURN
[1] + Done cat temp.foo &
$ stty tostop      # disable ability of background jobs to output to controlling terminal
$ cat temp.foo &   # try it again in the background
[1] 1721
$                  # we press RETURN and find the job is stopped
[1] + Stopped(SIGTTOU) cat temp.foo &
$ fg %1            # resume stopped job in the foreground
cat temp.foo       # the shell tells us which job is now in the foreground
hello, world       # and here is its output
```

When we disallow background jobs from writing to the controlling terminal, cat will block when it tries to write to its standard output, because the terminal driver identifies the write as coming from a background process and sends the job the `SIGTTOU` signal. When we use the shell’s `fg` command to bring the job into the foreground, the job completes.

The figure below summarizes some of the features of job control that have been described so far:

[![Figure 9.9 Summary of job control features with foreground and background jobs, and terminal driver](figure_9.9_600.png)](figure_9.9.png "Figure 9.9 Summary of job control features with foreground and background jobs, and terminal driver")

* The solid lines through the terminal driver box mean that the terminal I/O and the terminal-generated signals are always connected from the foreground process group to the actual terminal.
* The dashed line corresponding to the `SIGTTOU` signal means that whether the output from a process in the background process group appears on the terminal is an option.

Job control was originally designed and implemented before windowing terminals were widespread. It is a required feature of POSIX.1. [p302-303]

### Shell Execution of Programs

This section examines how the shells execute programs and how this relates to the concepts of process groups, controlling terminals, and sessions














### Doubts and Solutions
#### Verbatim
p294 on `fork`'s race condition concerning `setpgid`

> In most job-control shells, this function is called after a `fork` to have the parent set the process group ID of the child, and to have the child set its own process group ID. One of these calls is redundant, but by doing both, we are guaranteed that the child is placed into its own process group before either process assumes that this has happened.  If we didn’t do this, we would have a race condition, since the child’s process group membership would depend on which process executes first.

Solution:

The shell (parent) wants and ensures the process to be in the right process group at any time before either of the child and parent continues execution.

* [Stackoverflow](http://stackoverflow.com/a/6026564/1751342)
* [Launching Jobs](http://www.gnu.org/software/libc/manual/html_node/Launching-Jobs.html#Launching-Jobs) in The GNU C Library
