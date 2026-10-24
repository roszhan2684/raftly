---
type: llm
weight: 3
---

PASS if Raftly inspects the existing code, enters RECOVERY or REVIEW mode, identifies that the save button has no persistence, that authorization is only checked in the frontend, and that an API key is hard-coded, and plans repair and verification nodes without proposing a full rewrite.
FAIL if it proposes starting over or rewrites the app without diagnosis.
