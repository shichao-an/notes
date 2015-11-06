### **Chapter 1. Tutorial**

This chapter is a tour of the basic components of Go. We hope to provide enough information and examples to get you off the ground and doing useful things as quickly as possible.

When you’re learning a new language, there’s a natural tendency to write code as you would have written it in a language you already know. Be aware of this bias as you learn Go and try to avoid it. We’ve tried to illustrate and explain how to write good Go, so use the code here as a guide when you’re writing your own.

### Hello, World

We'll start with the now-traditional "hello, world" example, which appears at the beginning of [*The C Programming Language*](https://en.wikipedia.org/wiki/The_C_Programming_Language), published in 1987.

<small>[gopl.io/ch1/helloworld/main.go](https://github.com/shichao-an/gopl.io/blob/master/ch1/helloworld/main.go)</small>

```go
package main

import "fmt"

func main() {
	fmt.Println("Hello, 世界")
}
```

Go is a compiled language. The Go toolchain converts a source program and the things it depends on into instructions in the native machine language of a computer. These tools are accessed through a single command called `go` that has a number of subcommands. The simplest of these subcommands is `run`, which compiles the source code from one or more source files whose names end in `.go`, links it with libraries, then runs the resulting executable file.

```shell-session
$ go run helloworld.go
```
