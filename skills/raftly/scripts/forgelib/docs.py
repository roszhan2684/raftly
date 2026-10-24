"""Markdown helpers: generated sections, heading extraction, checklists.

Generated content inside documents lives between markers so humans and
Claude can edit the rest of the document freely:

    <!-- generated:graph:start -->
    ...generated...
    <!-- generated:graph:end -->

Older documents used a ``forge:`` prefix; those markers are recognised and upgraded.
"""

from __future__ import annotations

import re


LEGACY_PREFIXES = ("forge",)


def _markers(name: str, prefix: str = "generated") -> tuple[str, str]:
    return f"<!-- {prefix}:{name}:start -->", f"<!-- {prefix}:{name}:end -->"


def _upgrade_legacy(text: str, name: str) -> str:
    new_start, new_end = _markers(name)
    for prefix in LEGACY_PREFIXES:
        old_start, old_end = _markers(name, prefix)
        text = text.replace(old_start, new_start).replace(old_end, new_end)
    return text


def replace_section(text: str, name: str, content: str, heading: str | None = None) -> str:
    text = _upgrade_legacy(text, name)
    start, end = _markers(name)
    block = f"{start}\n{content.rstrip()}\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        return pattern.sub(lambda _m: block, text, count=1)
    suffix = f"\n## {heading}\n\n{block}\n" if heading else f"\n{block}\n"
    return text.rstrip() + "\n" + suffix


def get_section(text: str, name: str) -> str | None:
    text = _upgrade_legacy(text, name)
    start, end = _markers(name)
    m = re.search(re.escape(start) + r"\n?(.*?)\n?" + re.escape(end), text, re.S)
    return m.group(1) if m else None


def sections(text: str, level: int = 2) -> dict[str, str]:
    """Map heading text -> body for headings of exactly ``level``."""
    hashes = "#" * level
    out: dict[str, str] = {}
    current = None
    buf: list[str] = []
    in_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        m = None if in_code else re.match(rf"^{hashes}\s+(.+?)\s*#*\s*$", line)
        if m and not line.startswith(hashes + "#"):
            if current is not None:
                out[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
        elif current is not None:
            if not in_code and re.match(r"^#{1,%d}\s" % (level - 1), line) if level > 1 else False:
                out[current] = "\n".join(buf).strip()
                current = None
                buf = []
            else:
                buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf).strip()
    return out


def find_section(text: str, *names: str, level: int = 2) -> str | None:
    """Case-insensitive heading lookup; names may be prefixes (e.g. 'Vision')."""
    secs = sections(text, level)
    lowered = {k.lower(): v for k, v in secs.items()}
    for n in names:
        n = n.lower()
        if n in lowered:
            return lowered[n]
        for k, v in lowered.items():
            if re.sub(r"^\d+[.)]?\s*", "", k).startswith(n):
                return v
    return None


CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[( |x|X|~)\]\s+(.*)$")


def checklist(text: str) -> list[tuple[str, str]]:
    """Return [(state, item)] where state is 'done', 'open' or 'na' (``[~]``)."""
    out = []
    for line in text.splitlines():
        m = CHECKBOX_RE.match(line)
        if m:
            mark = m.group(1)
            state = "done" if mark in "xX" else ("na" if mark == "~" else "open")
            out.append((state, m.group(2).strip()))
    return out


def first_paragraph(text: str | None, max_chars: int = 400) -> str:
    if not text:
        return ""
    for block in re.split(r"\n\s*\n", text.strip()):
        b = block.strip()
        if b and not b.startswith(("#", "|", "```", "<!--")):
            b = re.sub(r"\s+", " ", b)
            if len(b) <= max_chars:
                return b
            cut = b[:max_chars]
            ends = [m.end() for m in re.finditer(r"[.!?](\s|$)", cut)]
            if ends and ends[-1] > max_chars * 0.4:
                return cut[: ends[-1]].rstrip()
            return cut.rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return ""


def bullets(text: str | None, limit: int = 8) -> list[str]:
    if not text:
        return []
    out = []
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(?!\[[ xX~]\])(.+)$", line)
        if m:
            out.append(m.group(1).strip())
            if len(out) >= limit:
                break
    return out
