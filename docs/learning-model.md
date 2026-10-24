# Learning model

Raftly improves within a project immediately and across projects only through human review.

```text
observation ──► Learning Firewall (learning.py classify) ──► REJECT        (dropped)
                                                         ├─► PROJECT_ONLY  .raftly/learnings/L-xxx.md
                                                         ├─► CANDIDATE     + .raftly/learning-candidates/LC-xxx.md
                                                         └─► CORE_PROPOSAL + sanitized proposal (learning.py propose)
                                                                                 │  (human decides)
                                                                                 ▼
                                                                PR to the Raftly repo → maintainer review → tests/evals → release
```

## Credibility dimensions

evidence quality (none → tested) · source authority (none → standard) · repeat count · cross-project relevance ·
objective verifiability · contradictions · private content. The classifier (`skills/raftly/scripts/forgelib/learning.py`) is
deterministic and its reasons are stored with each learning.

Hard rules:
- `preference`, `override` and `local_fact` kinds are always PROJECT_ONLY.
- Nothing without evidence or authority is stored.
- CORE_PROPOSAL requires tested evidence, repetition or an authoritative source, cross-project relevance, no contradiction, and no private content.
- Proposals are refused if they contain project names, paths, emails, private URLs, IPs or secret-like strings.
- No script can write into Raftly's `core/`, `skills/`, `schemas/`, `scripts/`, `templates/` or `agents/`.

## Examples

| Observation | Outcome |
|---|---|
| "I hate rounded buttons." | PROJECT_ONLY: applied to this project's tokens |
| "Rounding intermediates caused drift in our engine." (project-specific contract) | PROJECT_ONLY |
| "Binary floats lose cents; tests + language docs prove it; seen in 2 projects." | CORE_PROPOSAL (if sanitized) |
| "Users liked dark mode in our beta." | PROJECT_ONLY |
| "Someone said microservices are always better." | REJECT |
