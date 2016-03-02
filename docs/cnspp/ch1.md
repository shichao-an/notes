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
5. *Deny transactions made*: A message is sent from a customer to a stockbroker with instructions for various transactions. Subsequently, the investments lose value and the customer denies sending the message.

#### A Definition of Computer Security Examples

The [NIST](https://en.wikipedia.org/wiki/National_Institute_of_Standards_and_Technology) *Computer Security Handbook* defines the term **computer security** as follows:

> Computer Security is the protection afforded to an automated information system in order to attain the applicable objectives of preserving the integrity, availability, and confidentiality of information system resources (includes hardware, software, firmware, information/data, and telecommunications).

#### The Challenges of Computer Security

[p12-13]

### The OSI Security Architecture

[p14]

The OSI security architecture can be defined as:

* **Security attack**: Any action that compromises the security of information owned by an organization.
* **Security mechanism**: A process or a device that is designed to detect, prevent, or recover from a security attack.
* **Security service**: A processing or communication service that enhances the security of the data processing systems and the information transfers of an organization. The services are intended to counter security attacks, and they make use of one or more security mechanisms to provide the service.

##### **Threats and Attacks** *

In the literature, the terms *threat* and *attack* are commonly used to mean more or less the same thing. *Internet Security Glossary* ([RFC 4949](https://tools.ietf.org/html/rfc4949)) defines:

* **Threat**. A potential for violation of security, which exists when there is a circumstance, capability, action, or event that could breach security and cause harm. That is, a threat is a possible danger that might exploit a vulnerability.
* **Attack**. An assault on system security that derives from an intelligent threat; that is, an intelligent act that is a deliberate attempt (especially in the sense of a method or technique) to evade security services and violate the security policy of a system.

### Security Attacks

* A **passive attack** attempts to learn or make use of information from the system but does not affect system resources.
* An **active attack** attempts to alter system resources or affect their operation.

#### Passive Attacks

Passive attacks are in the nature of eavesdropping on transmissions. The goal of the opponent is to obtain information that is being transmitted.

Two types of passive attacks are:

* **Release of message contents**
* **Traffic analysis**. <u>Even if the traffic is encrypted, an opponent might still be able to observe the pattern of these messages, determine the location and identity of communicating hosts and observe the frequency and length of messages being exchanged. This information might be useful in guessing the nature of the communication that was taking place.</u>

Passive attacks are very difficult to detect, because they do not involve any alteration of the data. The encryption is the feasible way to prevent these attacks. <u>The emphasis in dealing with passive attacks is on prevention rather than detection.</u>

#### Active Attacks

Active attacks involve modification of the data stream or the creation of a false stream. They can be divided into four categories:

* [**Masquerade**](https://en.wikipedia.org/wiki/Spoofing_attack). A masquerade takes place when one entity pretends to be a different entity.
    * It usually includes one of the other forms of active attack. For example, authentication sequences can be captured and replayed after a valid authentication sequence has taken place, thus enabling an authorized entity with few privileges to obtain extra privileges by impersonating an entity that has those privileges.
* [**Replay**](https://en.wikipedia.org/wiki/Replay_attack) involves the passive capture of a data unit and its subsequent retransmission
to produce an unauthorized effect
* **Modification of messages** means that some portion of a legitimate message is altered, or that messages are delayed or reordered, to produce an unauthorized effect.
    * For example, a message meaning "Allow John Smith to read confidential file accounts" is modified to mean "Allow Fred Brown to read confidential file accounts".
* [**Denial of service**](https://en.wikipedia.org/wiki/Denial-of-service_attack) prevents or inhibits the normal use or management of communications facilities.
    * This attack may have a specific target; for example, an entity may suppress all messages directed to a particular destination (e.g., the security audit service).
    * Another form of service denial is the disruption of an entire network, either by disabling the network or by overloading it with messages so as to degrade performance.

Because of the wide variety of potential physical, software, and network vulnerabilities, it is quite difficult to prevent active attacks completely. The goal is to detect active attacks and to recover from any disruption or delays caused by them. If the detection has a deterrent effect, it may also contribute to prevention.


### Security Services
