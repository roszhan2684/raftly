User: "Store every to-do on a blockchain."

**GREENFIELD · PRODUCT · Recommendation: no blockchain. A tamper-evident audit log meets the need.**

**[Principal Software Architect]** What problem should the blockchain solve? If the need is *tamper-evident history*,
an append-only audit log with hashed entries and signed exports gives that guarantee. It costs nothing per write, has
zero latency, and avoids wallet UX and regulatory exposure. If the need is *user-owned data*, export and import do
that more simply.

Recorded ADR-006 (RECOMMEND, 88): blockchain rejected, with the reasons and the revisit trigger "a requirement for
trustless verification by third parties who do not trust the operator".

If you still want it, tell me and I'll record it as a founder override with its consequences (fees, latency, key-loss UX, complexity).
