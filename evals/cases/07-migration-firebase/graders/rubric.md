---
type: llm
weight: 3
---

PASS if Raftly enters MIGRATION mode, inspects Firebase usage, and plans forward migration, backward compatibility (dual-write or expand/contract), backups, phased cutover, application and data rollback, verification and an abort trigger, recorded with an ADR.
FAIL if it proposes a big-bang switch without rollback or backup reasoning.
