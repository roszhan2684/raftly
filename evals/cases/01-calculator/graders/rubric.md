---
type: llm
weight: 3
---

PASS if the reply and created files (a) treat this as a simple consumer utility, (b) explicitly avoid a backend, authentication, database, queues and Kubernetes, (c) separate the calculation engine from the UI, (d) define calculator semantics including precedence, repeated equals, precision and divide by zero, and (e) mark server-side production controls as not applicable.
FAIL if it proposes a backend, accounts, a database or microservices for V1, or omits calculator semantics.
