### **Chapter 8. Security and Security Audits**

### What Is Security?

Security is easily remembered by the acronym CIA, which stands for **confidentiality**, **integrity**, and **availability**:

* **Confidentiality** means that no unauthorized people are able to access information;
* **Integrity** means that no unauthorized people are able to modify information;
* **Availability** means that authorized people are able to access information.

The case study in [Chapter 12](ch12.md) discusses an approach that advocates integrating the security team into the adoption process. Other DevOps activities that are candidates for the discussion of security are:

* **Security audits.** When a security audit is imminent, coordination between Dev and Ops becomes quite important.
* **Securing the deployment pipeline.** The deployment pipeline itself is an attractive target for malicious attackers.
* **Microservice architectures.** The adoption of a microservice architecture introduces new security challenges.

[p155]

One of the catchphrases in DevOps is "infrastructure-as-code", which means treating scripts and DevOps process specifications as code, and applying the same quality control practices as you do with code. Security policies, governance rules, and configurations can be naturally embedded in the infrastructure code and automation for easier auditing.

### Threats

The point of view of an attacker provides one perspective for you to take when designing your system or subsystem. Microsoft has introduced the acronym **STRIDE** for a threat model.

* **Spoofing identity**. An example of identity spoofing is illegally accessing and then using another user’s authentication information, such as username and password.
* **Tampering with data**. Data tampering involves the malicious modification of data.
* **Repudiation**. Repudiation threats are associated with users who deny performing an action without other parties having a way to prove otherwise.
* **Information disclosure**. Information disclosure threats involve the exposure of information to individuals who are not supposed to have access to it.
* **Denial of service**. Denial of service (DoS) attacks target the service availability to valid users, for example, by making a web server temporarily unavailable or unusable.
* **Elevation of privilege**. In this type of threat, an unprivileged user gains privileged access and thereby has sufficient access to compromise or destroy the entire system.

### Resources to Be Protected

### Security Roles and Activities

### Identity Management

### Access Control

### Detection, Auditing, and Denial of Service

### Development

### Auditors

### Application Design Considerations

### Deployment Pipeline Design Considerations
