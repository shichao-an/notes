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

At this point, our login shell is running. Its parent process ID is the original `init` process (process ID 1), so when our login shell terminates, `init` is sent a `SIGCHLD` signal and it starts the whole procedure over again for this terminal. File descriptors 0, 1, and 2 for our login shell are set to the terminal device.

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

As part of the system start-up, `init` invokes a shell that executes the shell script `/etc/rc`, which starts `inetd` along with other daemons. Once the shell script terminates, the parent process of `inetd` becomes `init`; inetd waits for TCP/IP connection requests to arrive at the host. When a connection request arrives for it to handle, `inetd` does a `fork` and `exec` of the appropriate program.
