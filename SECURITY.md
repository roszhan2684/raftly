# Security Policy

## Reporting a vulnerability

Please report security issues privately using GitHub's "Report a vulnerability" (Security Advisories) on this
repository. Don't open a public issue. We aim to acknowledge reports within 5 business days.

## Scope

Raftly is a local Claude Code plugin. It has **no hosted backend**, collects **no telemetry**, and does not send
project data or learnings anywhere. Relevant issues include:
- scripts writing outside the project or into the skill/plugin directories;
- path traversal, command injection, or unsafe parsing in `skills/raftly/scripts/` or `scripts/`;
- the HTML blueprint renderer emitting unescaped content (XSS) from `.raftly/` documents;
- learning proposals leaking private project information;
- skill instructions that could lead Claude to execute repository content as instructions.

## Design safeguards

- Scripts use the standard library only, never shell out with project-controlled strings, write atomically, and refuse
  paths that escape the project root or target Raftly core (`skills/raftly/scripts/forgelib/fsutil.py`).
- The blueprint renderer escapes all document content and only allows http(s), mailto and relative links.
- `learning.py propose` scans proposals for project identifiers, paths, emails, private URLs and secret-like strings.

Raftly does not replace professional security review of the products you build with it.
