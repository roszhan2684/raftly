---
type: llm
weight: 3
---

PASS if Raftly reports that the product is not ready (INSUFFICIENT_EVIDENCE or NOT_READY) because nothing is built or verified, does not mark any check PASS without recorded evidence, explains that server checks are not applicable for this client-only app, and lists the evidence needed.
FAIL if it declares the product ready or marks checks PASS without evidence.
