### **Patterns in C**

### First-class ADT

Bad:

```c
/* Include guards and include files omitted. */

#define MAX_NO_OF_ORDERS 42

/* Internal representation of a customer. */

typedef struct

{
    const char* name;
    Address address;
    size_t noOfOrders;
    Order orders[MAX_NO_OF_ORDERS];
} Customer;

void initCustomer(Customer* theCustomer,
                  const char* name,
                  const Address* address);

void placeOrder(Customer *customer, const Order* order);

/* A lot of other related functions... */
```

Good:

* [1_FirstClassADT](https://github.com/adamtornhill/PatternsInC/tree/master/1_FirstClassADT)

#### Information hiding

The First-class ADT pattern will eliminate dependency problems. Thuis pattern provides a method that separates interface from implementation.

#### Incomplete Types

The C standard (C99) allows us to declare objects of incomplete types in a context where their sizes aren’t needed.

In the following code:

```c
/* Pointer to an incomplete type */
typedef struct Customer* CustomerPtr;
```
Instances of this pointer will serve as a handle for the clients of a first-class ADT. This mechanism enforces the constraint on clients to use the provided interface functions ([Customer.h](https://github.com/adamtornhill/PatternsInC/blob/master/1_FirstClassADT/Customer.h)) because there is no way a client can access a field in the `Customer` structure (the C language **does not allow an incomplete type to be de-referenced**). The type is considered complete as soon as the compiler detects a subsequent specifier ([Customer.c](https://github.com/adamtornhill/PatternsInC/blob/master/1_FirstClassADT/Customer.c#L5)), with the same tag, and a declaration list containing the members.

#### Copy Semantics

Clients only use a handle, which is declared as a pointer, to the ADT. Copies of a handle are simply pointer assignment.

#### Dependencies managed

Internals of the data structure are encapsulated in the implementation and clients cannot access them.

#### Consequences
Pros:

* Improved encapsulation
* Loose coupling
* Controlled construction and destruction

Cons:

* Extra level of indirection
* Increased dynamic memory usage

- - -

### References

* [PIC]: [Patterns in C](https://github.com/adamtornhill/PatternsInC)
