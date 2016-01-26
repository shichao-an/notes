### **Chapter 1. Overview**

### Computer Security Concepts

This book focuses on two broad areas:

* **Cryptographic algorithms and protocols**, which have a broad range of applications.
* **Network and Internet security**, which rely heavily on cryptographic techniques.

##### **Cryptographic algorithms and protocols** *

Cryptographic algorithms and protocols can be grouped into four main areas:

* **Symmetric encryption**: used to conceal the contents of blocks or streams of data of any size, including messages, files, encryption keys, and passwords.
* **Asymmetric encryption**: used to conceal small blocks of data, such as encryption keys and hash function values, which are used in digital signatures.
* **Data integrity algorithms**: used to protect blocks of data, such as messages, from alteration.
* **Authentication protocols**. These are schemes based on the use of cryptographic algorithms designed to authenticate the identity of entities.

##### **Network and Internet security** *

Network and Internet security consists of measures to deter, prevent, detect, and correct security violations that involve the transmission of information. Consider the following examples of security violations:

1. *Capture a copy*: User A transmits a file to user B. The file contains sensitive information (e.g., payroll records) that is to be protected from disclosure. User C, who is not authorized to read the file, is able to monitor the transmission and capture a copy of the file during its transmission.
2. *Alter contents*: A network manager, D, transmits a message to a computer, E, under its management. The message instructs computer E to update an authorization file to include the identities of a number of new users who are to be given access to that computer. User F intercepts the message, alters its contents to add or delete entries, and then forwards the message to computer E, which accepts the message as coming from manager D and updates its authorization file accordingly.
3. *Forge a message*: Rather than intercepting a message, user F constructs its own message with the desired entries and transmits that message to computer E as if it had come from manager D. Computer E accepts the message as coming from manager D and updates its authorization file accordingly.
4. *Delay*: An employee is fired without warning. The personnel manager sends a message to a server system to invalidate the employee’s account. When the invalidation is accomplished, the server is to post a notice to the employee’s file as confirmation of the action. The employee is able to intercept the message and delay it long enough to make a final access to the server to retrieve sensitive information. The message is then forwarded, the action taken, and the confirmation posted. The employee’s action may go unnoticed for some considerable time.
5. *Denies transactions made*: A message is sent from a customer to a stockbroker with instructions for various transactions. Subsequently, the investments lose value and the customer denies sending the message.

#### A Definition of Computer Security Examples

The [NIST](https://en.wikipedia.org/wiki/National_Institute_of_Standards_and_Technology) *Computer Security Handbook* defines the term **computer security** as follows:

> Computer Security is the protection afforded to an automated information system in order to attain the applicable objectives of preserving the integrity, availability, and confidentiality of information system resources (includes hardware, software, firmware, information/data, and telecommunications).

#### The Challenges of Computer Security

### The OSI Security Architecture

### Security Attacks

#### Passive Attacks
#### Active Attacks

### Security Services
