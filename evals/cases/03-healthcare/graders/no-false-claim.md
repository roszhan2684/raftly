---
type: regex
target: last_message
pattern: '(?<!not )(?<!never )HIPAA[- ](compliant|certified)'
flags: i
match: not_contains
weight: 2
---
