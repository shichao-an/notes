### **Bash**

### Introduction

#### What is Bash?

Bash is the shell, or command language interpreter, for the GNU operating system. The name is an acronym for the "**B**ourne-**A**gain **SH**ell", a pun on [Stephen Bourne](https://en.wikipedia.org/wiki/Stephen_R._Bourne), the author of the direct ancestor of the current Unix shell `sh`.

#### What is a shell?

A shell is simply a macro processor that executes commands. The term "macro processor" means functionality where text and symbols are expanded to create larger expressions.

A Unix shell is both a command interpreter and a programming language:

* As a command interpreter, the shell provides the user interface to the rich set of GNU utilities.
* The programming language features allow these utilities to be combined. Files containing commands can be created, and become commands themselves. These new commands have the same status as system commands in directories such as `/bin`, allowing users or groups to establish custom environments to automate their common tasks.

Shells may be used interactively or non-interactively:

* In interactive mode, they accept input typed from the keyboard.
* When executing non-interactively, shells execute commands read from a file.

A shell allows execution of GNU commands, both synchronously and asynchronously:

* The shell waits for synchronous commands to complete before accepting more input;
* Asynchronous commands continue to execute in parallel with the shell while it reads and executes additional commands.
* The redirection constructs permit fine-grained control of the input and output of those commands. Moreover, the shell allows control over the contents of commands’ environments.

Shells also provide a small set of built-in commands (builtins) implementing functionality impossible or inconvenient to obtain via separate utilities. For example:

* `cd`, `break`, `continue`, and `exec` cannot be implemented outside of the shell because they directly manipulate the shell itself.
* The `history`, `getopts`, `kill`, or `pwd` builtins, among others, could be implemented in separate utilities, but they are more convenient to use as builtin commands.

While executing commands is essential, most of the power (and complexity) of shells is due to their embedded programming languages. Like any high-level language, the shell provides variables, flow control constructs, quoting, and functions.

Shells offer features geared specifically for interactive use rather than to augment the programming language. These interactive features include job control, command line editing, command history and aliases.

### Definitions

* **POSIX**: A family of open system standards based on Unix. Bash is primarily concerned with the Shell and Utilities portion of the POSIX 1003.1 standard.

* **blank**: A space or tab character.

* **builtin**: A command that is implemented internally by the shell itself, rather than by an executable program somewhere in the file system.

* **control operator**: A token that performs a control function. It is a newline or one of the following: ‘||’, ‘&&’, ‘&’, ‘;’, ‘;;’, ‘|’, ‘|&’, ‘(’, or ‘)’.

* **exit status**: The value returned by a command to its caller. The value is restricted to eight bits, so the maximum value is 255.

* **field**: A unit of text that is the result of one of the shell expansions. After expansion, when executing a command, the resulting fields are used as the command name and arguments.

* **filename**: A string of characters used to identify a file.

* **job**: A set of processes comprising a pipeline, and any processes descended from it, that are all in the same process group.

* **job control**: A mechanism by which users can selectively stop (suspend) and restart (resume) execution of processes.

* **metacharacter**: A character that, when unquoted, separates words. A metacharacter is a *blank* or one of the following characters: ‘|’, ‘&’, ‘;’, ‘(’, ‘)’, ‘<’, or ‘>’.

* **name**: A **word** consisting solely of letters, numbers, and underscores, and beginning with a letter or underscore. Names are used as shell variable and function names. Also referred to as an **identifier**.

* **operator**: A **control operator** or a **redirection operator**. See [Redirections](#redirections), for a list of redirection operators. Operators contain at least one unquoted **metacharacter**.

* **process group**: A collection of related processes each having the same **process group ID**.

* **process group ID**: A unique identifier that represents a **process group** during its lifetime.

* **reserved word**: A word that has a special meaning to the shell. Most reserved words introduce shell flow control constructs, such as `for` and `while`.

* **return status**: A synonym for **exit status**.

* **signal**: A mechanism by which a process may be notified by the kernel of an event occurring in the system.

* **special builtin**: A shell builtin command that has been classified as special by the POSIX standard.

* **token**: A sequence of characters considered a single unit by the shell. It is either a **word** or an **operator**.

* **word**: A sequence of characters treated as a unit by the shell. Words may not include unquoted **metacharacters**.

#### Relationships of some definitions *

* token
    * word
        * name
        * reserved word
    * operator
        * control operator
        * redirection operator
* metacharacter
    * blank
    * ‘|’, ‘&’, ‘;’, ‘(’, ‘)’, ‘<’, or ‘>’
* builtin
    * special bulitin

### Basic Shell Features

All of the Bourne shell builtin commands are available in Bash, The rules for evaluation and quoting are taken from the POSIX specification for the "standard" Unix shell.

This chapter briefly summarizes the shell’s "building blocks": commands, control structures, shell functions, shell parameters, shell expansions, redirections, which are a way to direct input and output from and to named files, and how the shell executes commands.

#### Shell Syntax

* If the input indicates the beginning of a comment, the shell ignores the comment symbol (‘#’), and the rest of that line.
* Otherwise, <u>the shell reads its input and divides the input into words and operators</u>, employing the quoting rules to select which meanings to assign various words and characters.

[[s3.1](http://www.gnu.org/software/bash/manual/bash.html#Shell-Syntax)]

##### **Shell Operation**

Basically, the shell does the following:

1.  Reads its input in one of the following way:
    * from a file (see [Shell Scripts](#shell-scripts)),
    * from a string supplied as an argument to the `-c` invocation option (see [Invoking Bash](#invoking-bash)),
    * from the user’s terminal.
2.  Breaks the input into words and operators, obeying the quoting rules described in [Quoting](#quoting). These tokens are separated by `metacharacters`. Alias expansion is performed by this step (see [Aliases](#aliases)).
3.  Parses the tokens into simple and compound commands (see [Shell Commands](#shell-commands)).
4.  Performs the various shell expansions (see [Shell Expansions](#shell-expansions)), breaking the expanded tokens into lists of filenames (see [Filename Expansion](#filename-expansion)) and commands and arguments.
5.  Performs any necessary redirections (see [Redirections](#redirections)) and removes the redirection operators and their operands from the argument list.
6.  Executes the command (see [Executing Commands](#executing-commands)).
7.  Optionally waits for the command to complete and collects its exit status (see [Exit Status](#exit-status)).

##### **Quoting**

Quoting is used to remove the special meaning of certain characters or words to the shell. It is used to:

* Disable special treatment for special characters,
* Prevent reserved words from being recognized as such,
* Prevent parameter expansion.

There are three quoting mechanisms: the **escape character**, single quotes, and double quotes.

###### **Escape Character**

A non-quoted backslash ‘\’ is the Bash escape character. It preserves the literal value of the next character that follows, with the exception of newline. If a \newline pair appears, and the backslash itself is not quoted, the \newline is treated as a line continuation.

###### **Single Quotes**

Enclosing characters in single quotes (‘'’) preserves the literal value of each character within the quotes. A single quote may not occur between single quotes, even when preceded by a backslash.

###### **Double Quotes**

Enclosing characters in double quotes (‘"’) preserves the literal value of all characters within the quotes, with the exception of ‘$’, ‘`’, ‘\’, and, when history expansion is enabled, ‘!’.

* ‘$’ and ‘`’ retain their special meaning within double quotes (see [Shell Expansions](#shell-expansions)).
* The backslash retains its special meaning only when followed by one of the following characters: ‘$’, ‘`’, ‘"’, ‘\’, or newline. Within double quotes, backslashes that are followed by one of these characters are removed. Backslashes preceding characters without a special meaning are left unmodified.
* A double quote may be quoted within double quotes by preceding it with a backslash.
* History expansion (if enabled) will be performed unless an ‘!’ appearing in double quotes is escaped using a backslash.
* The backslash preceding the ‘!’ is not removed.

Examples on history expansion and ‘!’ (history expansion enabled):

```shell-session
$ foo
-bash: foo: command not found
$ echo "!!"
echo "foo"
foo
$ echo "\!!"
\!!
```



- - -

### References

* [The GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
* [Bash Hackers Wiki](http://wiki.bash-hackers.org/start)
