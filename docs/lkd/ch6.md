### **Chapter 6. Kernel Data Structures**

This chapter introduces several built-in data structures for use in Linux kernel code: [p85]

* Linked lists
* Queues
* Maps
* Binary trees

These generic data structures are provided to encourage code reuse. Kernel developers should use these data structures whenever possible and not "roll your own" solutions.

### Linked Lists

As the simplest and most common data structure in the Linux kernel, a **linked list** is a data structure that allows the storage and manipulation of a variable number of *elements*, called the *nodes* of the list.

Unlike in a static array, the elements in a linked list are dynamically created and inserted into the list, which enables the management of a varying number of elements unknown at compile time. The elements do not necessarily occupy contiguous regions in memory and thus need to be linked together (each element in the list contains a pointer to the *next* element).

#### Singly and Doubly Linked Lists

The simplest data structure for a linked list is like:

```c
/* an element in a linked list */
struct list_element {
    void *data; /* the payload */
    struct list_element *next; /* pointer to the next element */
};
```

The following figure shows a linked list:

[![Figure 6.1 A singly linked list.](figure_6.1.png)](figure_6.1.png "Figure 6.1 A singly linked list.")

* A **singly linked lists**: each element does not have a pointer to the *previous* element.
* A **doubly linked lists**: each element also contains a pointer to the *previous* element (linked both forward and backward).

A data structure representing a doubly linked list would look similar to this:

```c
/* an element in a linked list */
struct list_element {
    void *data; /* the payload */
    struct list_element *next; /* pointer to the next element */
    struct list_element *prev; /* pointer to the previous element */
};
```

The following figure shows doubly linked list:

[![Figure 6.2 A doubly linked list.](figure_6.2.png)](figure_6.2.png "Figure 6.2 A doubly linked list.")

#### Circular Linked Lists

Normally, the last element in a linked list has no next element, so it is set to point to a special value, such as `NULL`. In a **circular linked list**, last element does not point to a special value, but points back to the first value.

<u>Circular linked lists can come in both doubly and singly linked versions. In a circular doubly linked list, the first node's "previous" pointer points at the last node.</u>

The following two figures are singly and doubly circular linked lists, respectively:

[![Figure 6.3 A circular singly linked list.](figure_6.3.png)](figure_6.3.png "Figure 6.3 A circular singly linked list.")
[![Figure 6.4 A circular doubly linked list.](figure_6.4.png)](figure_6.4.png "Figure 6.4 A circular doubly linked list.")

#### Moving Through a Linked List

To move through a linked list, simply follow the next pointer of an element, and visit the next element. This is linear movement.

<u>Linked lists are ill-suited for use cases where random access is an important operation.</u> Instead, you use linked lists when iterating over the whole list is important and the dynamic addition and removal of elements is required.

In linked list implementations:

* The first element is often represented by a special pointer, *head*, that enables easy access to the "start" of the list.
* In a noncircular-linked list, the last element is delineated by its next pointer being `NULL`.
* In a circular-linked list, the last element is delineated because it points to the *head* element.

[p87-88]

#### The Linux Kernel's Implementation

The Linux kernel's implementation is unique, in comparison to most linked list implementations including those described in the previous sections.

The common pattern for storing this structure in a linked list is to embed the list pointer in the structure. For example, to describe that member of the [*Canidae*](https://en.wikipedia.org/wiki/Canidae) family:

```c
struct fox {
    unsigned long tail_length; /* length in centimeters of tail */
    unsigned long weight; /* weight in kilograms */
    bool is_fantastic; /* is this fox fantastic? */
    struct fox *next; /* next fox in linked list */
    struct fox *prev; /* previous fox in linked list */
};
```

The Linux kernel approach is different. Instead of turning the structure into a linked list, the Linux approach is to "<u>embed a linked list node in the structure</u>".

##### **The Linked List Structure**

The linked-list code is declared in the header file `<linux/list.h>` ([include/linux/list.h#L19](https://github.com/shichao-an/linux/blob/v2.6.34/include/linux/list.h#L19)) and the data structure is simple:

```c
struct list_head {
    struct list_head *next
    struct list_head *prev;
};
```

The utility is in *how* the `list_head` structure is used:

```c
struct fox {
    unsigned long tail_length; /* length in centimeters of tail */
    unsigned long weight; /* weight in kilograms */
    bool is_fantastic; /* is this fox fantastic? */
    struct list_head list; /* list of all fox structures */
};
```

With this, `list.next` in fox points to the next element, and `list.prev` in fox points to the previous.

The kernel provides a family of routines to manipulate linked lists (for example, the `list_add()` method adds a new node to an existing linked list). These methods accept only `list_head` structures. <u>Using the macro `container_of()`, we can easily find the parent structure containing any given member variable. In C, the offset of a given variable into a structure is fixed by the ABI at compile time.</u>

<small>[include/linux/kernel.h#L709](https://github.com/shichao-an/linux/blob/v2.6.34/include/linux/kernel.h#L709)</small>

```c
#define container_of(ptr, type, member) ({ \
        const typeof( ((type *)0)->member ) *__mptr = (ptr); \
        (type *)( (char *)__mptr - offsetof(type,member) );})
```

Using `container_of()`, we can define a simple function to return the parent structure containing any `list_head`:

<small>[include/linux/list.h#L348](https://github.com/shichao-an/linux/blob/v2.6.34/include/linux/list.h#L348)</small>

```c
#define list_entry(ptr, type, member) \
        container_of(ptr, type, member)
```

With `list_entry()`, the kernel provides routines manipulate linked lists without knowing anything about the structures that the `list_head` resides within.

##### **Defining a Linked List**

A `list_head` is normally embedded inside your own structure:

```c
struct fox {
    unsigned long tail_length; /* length in centimeters of tail */
    unsigned long weight; /* weight in kilograms */
    bool is_fantastic; /* is this fox fantastic? */
    struct list_head list; /* list of all fox structures */
};
```

The list needs to be initialized before it can be used. Because most of the elements of the linked list are created dynamically, the most common way of initializing the linked list is at runtime using `INIT_LIST_HEAD`:

```c
struct fox *red_fox;
red_fox = kmalloc(sizeof(*red_fox), GFP_KERNEL);
red_fox->tail_length = 40;
red_fox->weight = 6;
red_fox->is_fantastic = false;
INIT_LIST_HEAD(&red_fox->list);
```

If the structure is statically created at compile time, and you have a direct reference to it, you can simply do this (using `LIST_HEAD_INIT`):

```c
struct fox red_fox = {
    .tail_length = 40,
    .weight = 6,
    .list = LIST_HEAD_INIT(red_fox.list),
};
```

##### **List Heads**

But before we can use kernel's linked list routines to manage our structure, we need a canonical pointer to refer to the list as a whole: a *head* pointer.

Since each contains a `list_head`, and we can iterate from any one node to the next. We need a special pointer that refers to your linked list, without being a list node itself. This special node is in fact a normal `list_head`: [p90]

```c
static LIST_HEAD(fox_list);
```

This defines and initializes a `list_head` named `fox_list`. The majority of the linked list routines accept one or two parameters: the `head` node or the `head` node plus an actual list node.

#### Manipulating Linked Lists

The kernel provides a family of functions to manipulate linked lists. They all take pointers to one or more `list_head` structures. The functions are implemented as inline functions in generic C and can be found in `<linux/list.h>` ([include/linux/list.h](https://github.com/shichao-an/linux/blob/v2.6.34/include/linux/list.h)).

All these functions are `O(1)`. This means they execute in constant time, regardless of the size of the list or any other inputs

##### **Adding a Node to a Linked List**

To add a node to a linked list:

<small>[include/linux/list.h#L64](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L64)</small>

```c
list_add(struct list_head *new, struct list_head *head)
```

This function adds the new node to the given list immediately after the `head` node. Because the list is circular and generally has no concept of first or last nodes, you can pass any element for head. If you pass the "last" element as `head`, this function can be used to implement a stack.

For example, assume we had a new `struct fox` to add to the `fox_list` list. We can do this:

```c
list_add(&f->list, &fox_list);
```

To add a node to the end of a linked list:

<small>[include/linux/list.h#L78](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L78)</small>

```c
list_add_tail(struct list_head *new, struct list_head *head)
```

If you pass the "first" element as `head`, this function can be used to implement a stack.

##### **Deleting a Node from a Linked List**

To delete a node from a linked list, use `list_del()`:

<small>[include/linux/list.h#L103](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L103)</small>

```c
list_del(struct list_head *entry)
```

This function removes the element entry from the list. Note that <u>`list_del` does not free any memory belonging to `entry` or the data structure in which it is embedded;</u> this function merely removes the element from the list. After calling this, you would typically destroy your data structure and the `list_head` inside it.

For example, to delete the fox node we previous added to `fox_list`:

```c
list_del(&f->list);
```

It simply receives a specific node and modifies the pointers of the previous and subsequent nodes such that the given node is no longer part of the list. The implementation is instructive:

<small>[include/linux/list.h#L90](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L90)</small>

```c
static inline void __list_del(struct list_head *prev, struct list_head *next)
{
    next->prev = prev;
    prev->next = next;
}

static inline void list_del(struct list_head *entry)
{
    __list_del(entry->prev, entry->next);
}
```

To delete a node from a linked list and reinitialize it, the kernel provides `list_del_init()`:

<small>[include/linux/list.h#L140](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L140)</small>

```c
list_del_init(struct list_head *entry)
```

This function behaves the same as `list_del()`, except it also reinitializes the given `list_head` with the rationale that you no longer want the entry in the list, but you can reuse the data structure itself.

##### **Moving and Splicing Linked List Nodes**

To move a node from one list to another:

<small>[include/linux/list.h#L151](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L151)</small>

```c
list_move(struct list_head *list, struct list_head *head)
```

This function removes the list entry from its linked list and adds it to the given list after the `head` element.

To move a node from one list to the end of another:

<small>[include/linux/list.h#L162](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L162)</small>

```c
list_move_tail(struct list_head *list, struct list_head *head)
```

This function does the same as `list_move()`, but inserts the list element before the head entry.

To check whether a list is empty:

<small>[include/linux/list.h#L184](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L184)</small>

```c
list_empty(struct list_head *head)
```

This returns nonzero if the given list is empty; otherwise, it returns zero.

To splice two unconnected lists together;

<small>[include/linux/list.h#L290](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L290)</small>

```c
list_splice(struct list_head *list, struct list_head *head)
```

This function splices together two lists by inserting the list pointed to by `list` to the given list after the element `head`.

To splice two unconnected lists together and reinitialize the old list:

<small>[include/linux/list.h#L302](https://github.com/shichao-an/linux-2.6.34.7/blob/master/include/linux/list.h#L302)</small>

```c
list_splice_init(struct list_head *list, struct list_head *head)
```

This function works the same as `list_splice()`, except that the emptied list pointed to by `list` is reinitialized.

If you already have the `next` and `prev` pointers available, you can save a couple cycles (specifically, the dereferences to get the pointers) by calling the internal list functions directly. For example, rather than call `list_del(list)`, you can call `__list_del(prev, next)`. [p92]

### Queues

### Maps

### Binary Trees

### Doubts and Solutions

#### Verbatim

p91 on `list_add` and `list_add_tail`:

> If you do pass the "last" element, however, this function (`list_add`) can be used to implement a stack
> ...
> This function (`list_add_tail`) can be used to implement a queue, however, if you pass the "first" element.

Implementation details are required to understand this.
