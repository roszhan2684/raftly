"""DIAGRAMS.md: the five product diagrams, as Mermaid, and their checks.

Each diagram has its own section. A section holds a ```mermaid block of an
allowed type, or a line "Not applicable: <reason>" when the product genuinely
has no such thing (for example no screens for a pure API).
"""

from __future__ import annotations

import re

from . import docs

DIAGRAMS_DOC = "DIAGRAMS.md"

# (key, heading keywords, title, allowed Mermaid diagram types)
DIAGRAMS = [
    ("architecture", ("architecture",), "System architecture",
     ("flowchart", "graph", "C4Context", "C4Container", "C4Component", "C4Deployment", "architecture-beta")),
    ("user-flow", ("user flow", "user journey"), "User flow",
     ("flowchart", "graph", "journey", "stateDiagram", "stateDiagram-v2")),
    ("screens", ("screen", "navigation"), "Screen map and navigation",
     ("flowchart", "graph", "stateDiagram", "stateDiagram-v2")),
    ("data", ("data model", "data"), "Data model",
     ("erDiagram", "classDiagram", "stateDiagram", "stateDiagram-v2", "flowchart", "graph")),
    ("sequence", ("sequence",), "Critical path sequence",
     ("sequenceDiagram",)),
]

MERMAID_RE = re.compile(r"```mermaid[ \t]*\n(.*?)```", re.S)
NA_RE = re.compile(r"^\s*(?:\*\*)?Not applicable(?:\*\*)?\s*:\s*(.{10,})$", re.I | re.M)
HEADING_RE = re.compile(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", re.M)


def sections(text: str) -> dict[str, tuple[str, str]]:
    """Map diagram key -> (heading, section body) for the sections present."""
    found: dict[str, tuple[str, str]] = {}
    for m in HEADING_RE.finditer(text):
        heading = m.group(1)
        low = heading.lower()
        for key, words, _title, _types in DIAGRAMS:
            if key not in found and any(w in low for w in words):
                found[key] = (heading, docs.find_section(text, heading) or "")
                break
    return found


def diagram_type(block: str) -> str:
    for line in block.splitlines():
        line = line.strip()
        if line and not line.startswith("%%") and not line.startswith("---"):
            return line.split()[0]
    return ""


def parse(text: str) -> list[dict]:
    """One entry per expected diagram: title, status, type, source, note."""
    found = sections(text)
    out = []
    for key, _words, title, types in DIAGRAMS:
        entry = {"key": key, "title": title, "allowed": types, "heading": None, "status": "missing",
                 "type": None, "source": None, "intro": "", "na_reason": None}
        if key in found:
            heading, body = found[key]
            entry["heading"] = heading
            entry["intro"] = docs.first_paragraph(MERMAID_RE.sub("", body), 300)
            m = MERMAID_RE.search(body)
            na = NA_RE.search(body)
            if m:
                src = m.group(1).rstrip()
                entry.update(source=src, type=diagram_type(src))
                entry["status"] = "ok" if entry["type"] in types else "wrong-type"
                if entry["status"] == "ok" and len([ln for ln in src.splitlines() if ln.strip()]) < 3:
                    entry["status"] = "too-small"
            elif na:
                entry.update(status="not-applicable", na_reason=na.group(1).strip())
            else:
                entry["status"] = "empty"
        out.append(entry)
    return out


def problems(text: str) -> list[str]:
    """Human-readable problems; an empty list means DIAGRAMS.md is complete."""
    out = []
    for d in parse(text):
        if d["status"] == "missing":
            out.append(f"DIAGRAMS.md has no '{d['title']}' section")
        elif d["status"] == "empty":
            out.append(f"DIAGRAMS.md '{d['title']}' needs a ```mermaid block or 'Not applicable: <reason>'")
        elif d["status"] == "wrong-type":
            out.append(f"DIAGRAMS.md '{d['title']}' is a {d['type'] or 'blank'} diagram; use one of: {', '.join(d['allowed'])}")
        elif d["status"] == "too-small":
            out.append(f"DIAGRAMS.md '{d['title']}' diagram is too small to be useful")
    if all(d["status"] == "not-applicable" for d in parse(text)):
        out.append("DIAGRAMS.md marks every diagram not applicable")
    return out
