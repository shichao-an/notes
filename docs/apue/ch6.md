## Chapter 6. System Data Files and Information

This chapter covers portable interfaces to data files, system identification functions and the time and date functions.

### Password File

The UNIX System's password file, called the user database by POSIX.1, contains the following fields:

[![Figure 6.1 Fields in /etc/passwd file](figure_6.1_600.png)](figure_6.1.png "Figure 6.1 Fields in /etc/passwd file")

Historically, the password file has been stored in `/etc/passwd` and has been an ASCII file.

* `root` has a user ID of 0 (superuser)
* The encrypted password field contains a single character as a placeholder (`x`) 
* Some fields can be empty
* The shell field contains the user's login shell. The default value for an empty shell field is usually `/bin/sh`. Other executable that prevents a user from loggin in to a system:
    * `/dev/null`
    * `/bin/false`: exits with an unsuccessful (nonzero) status
    * `/bin/true`: exits with a successful (zero) status
    * `nologin`: prints a customizable error message and exits with a nonzero exit status
* `nobody` user name can be used to allow people to log in to a system, but with a user ID (65534) and group ID (65534) that provide no privileges.
* Some systems that provide the `finger(1)` command support additional information in the comment field

Some systems provide the `vipw` command to allow administrators to edit the password file.

<script src="https://gist.github.com/shichao-an/00b608f959de8dad0b1b.js"></script>

* `getpwuid`: used by the `ls(1)` program to map the numerical user ID contained in an i-node into a user's login name.
* `getpwnam`: used by the `login(1)` program when we enter our login name

Both functions return a pointer to a passwd structure that the functions fill in. This structure is usually a static variable within the function, so its contents are overwritten each time we call either of these functions.

<script src="https://gist.github.com/shichao-an/ffbbc20702760d6a4fab.js"></script>

* `getpwent`: returns the next entry (a pointer to a structure that it has filled in, this structure is overwritten each time we call this function) in the password file.
* `setpwent`: rewinds files
* `endpwent`: closes files

Example:

* [getpwnam.c](https://github.com/shichao-an/apue.3e/blob/master/datafiles/getpwnam.c)

`setpwent` at the beginning of this function is self-defense: we ensure that the files are rewound, in case the caller has already opened them by calling getpwent.

### Shadow Passwords

Systems store the encrypted password in another file, often called the **shadow password file**. Minimally, this file has to contain the user name and the encrypted password.

[![Figure 6.3 Fields in /etc/shadow file](figure_6.3_600.png)](figure_6.3.png "Figure 6.3 Fields in /etc/shadow file")

The shadow password file should not be readable by the world. Only a few programs need to access encrypted passwords, e.g. `login(1)` and `passwd(1)`, and these programs are often set-user-ID root. With shadow passwords, the regular password file, `/etc/passwd`, can be left readable by the world.

<script src="https://gist.github.com/shichao-an/bad119e8e6ed442e25bf.js"></script>

### Group File

The UNIX System’s group file, called the group database by POSIX.1, contains the following fields:

[![Figure 6.4 Fields in /etc/group file](figure_6.4_600.png)](figure_6.4.png "Figure 6.4 Fields in /etc/group file")

The field `gr_mem` is an array of pointers to the user names that belong to this group. This array is terminated by a null pointer.

<script src="https://gist.github.com/shichao-an/c280f5fa5d15b006e8af.js"></script>

Like the password file functions, both of these functions normally return pointers to a static variable, which is overwritten on each call.

<script src="https://gist.github.com/shichao-an/98d14c0850ac1f357993.js"></script>

* `getgrent`: reads the next entry from the group file, opening the file first, if it’s not already open

### Supplementary Group IDs

`newgrp(1)` can be used to change the real group ID to the new group’s ID. We could always go back to our original group (as listed in `/etc/passwd`) by executing `newgrp` without any arguments.

With 4.2BSD, the concept of **supplementary group IDs** was introduced. The file access permission checks were modified so that in addition to comparing the the file’s group ID to the process effective group ID, it was also compared to all the supplementary group IDs.

The constant `NGROUPS_MAX` specifies the number of supplementary group IDs.

<script src="https://gist.github.com/shichao-an/72cd85f9279a4501249c.js"></script>

* `getgroups`
    * *gidsetsize* > 0: the function fills in the array up to *gidsetsize* supplementary group IDs
    * *gidsetsize* = 0: the function returns only the number of supplementary group IDs; `grouplist` is not modified
* `setgroups`: called by the superuser to set the supplementary group ID list for the calling process
* `initgroups`: reads the entire group file with the functions `getgrent`, `setgrent`, and `endgrent` and determines the group membership for username.  It then calls setgroups to initialize the supplementary group ID list for the user. It includes *basegid* in the supplementary group ID list; basegid is the group ID from the password file for username. See [Setting the Group IDs](http://www.gnu.org/software/libc/manual/html_node/Setting-Groups.html)


### Implementation Differences

[p184-185]


### Other Data Files

Numerous other files are used by UNIX systems in normal day-to-day operation.

Services and networks:

* `/etc/services`
* `/etc/protocols`
* `/etc/networks`

The general principle is that every data file has at least three functions:

* `get`: reads the next record, opening the file
* `set`: opens the file, if not already open, and rewinds the file
* `end`: closes the data file

Description | Data file | Header | Structure | Additional keyed lookup functions
----------- | --------- | ------ | --------- | ---------------------------------
passwords | `/etc/passwd` | `<pwd.h>` | `passwd` | `getpwnam`, `getpwuid`
groups | `/etc/group` | `<grp.h>` | `group` | `getgrnam`, `getgrgid`
shadow | `/etc/shadow` | `<shadow.h>` | `spwd` | `getspnam`
hosts | `/etc/hosts` | `<netdb.h>` | `hostent` | `getnameinfo`, `getaddrinfo`
networks | `/etc/networks` | `<netdb.h>` | `netent` | `getnetbyname`, `getnetbyaddr`
protocols | `/etc/protocols` | `<netdb.h>` | `protoent` | `getprotobyname`, `getprotobynumber`
services | `/etc/services` | `<netdb.h>` | `servent` | `getservbyname`, `getservbyport`

### Login Accounting

Two data files provided with most UNIX systems:

* `utmp`: keeps track of all the users currently logged in
* `wtmp`: keeps track of all logins and logouts

```c
struct utmp {
    char ut_line[8]; /* tty line: "ttyh0", "ttyd0", "ttyp0", ... */
    char ut_name[8]; /* login name */
    long ut_time; /* seconds since Epoch */
};
```

On login, the `login` program fills one of these structures, and writes it to the `utmp` and `wtmp` file. On logout, the `init` process erases this entry (fills with null bytes) in `utmp` file and appends a new logout entry. This logout entry in the `wtmp` file had the `ut_name` field zeroed out. Special entries were appended to the `wtmp` file to indicate when the system was rebooted and right before and after the system’s time and date was changed.

The `who(1)` program read the `utmp` file and printed its contents in a readable form


### System Identification

<script src="https://gist.github.com/shichao-an/7477d4a7e401fc628fe9.js"></script>

```c
struct utsname {
    char sysname[]; /* name of the operating system */
    char nodename[]; /* name of this node */
    char release[]; /* current release of operating system */
    char version[]; /* current version of this release */
    char machine[]; /* name of hardware type */
};
```

<script src="https://gist.github.com/shichao-an/bd385512d7844d84cf2b.js"></script>
