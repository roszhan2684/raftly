---
type: regex
target:
  source: file
  path: .raftly/state.yaml
pattern: 'mode: (RECOVERY|REVIEW)'
weight: 2
---
