---
type: regex
target:
  source: file
  path: .raftly/gate.yaml
pattern: 'status: PASS\n\s+evidence: \[\]'
match: not_contains
weight: 2
---
