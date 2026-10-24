"""Tiny, safe Markdown -> HTML renderer for the static blueprint.

All input is HTML-escaped first; only a small, known set of constructs is
converted (headings, paragraphs, lists, task lists, tables, fenced code,
blockquotes, inline code, bold, italic, links). Links are limited to http(s),
mailto and relative paths so Raftly documents can never inject script.
"""

from __future__ import annotations

import html
import re

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_SAFE_URL = re.compile(r"^(https?://|mailto:|#|\.{0,2}/|[A-Za-z0-9_\-./]+$)")


def _inline(text: str) -> str:
    s = html.escape(text, quote=True)
    codes: list[str] = []

    def keep_code(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", keep_code, s)

    def link(m):
        label, url = m.group(1), html.unescape(m.group(2))
        if not _SAFE_URL.match(url) or url.lower().startswith(("javascript:", "data:")):
            return label
        ext = ' rel="noopener noreferrer"' if url.startswith("http") else ""
        return f'<a href="{html.escape(url, quote=True)}"{ext}>{label}</a>'

    s = _LINK_RE.sub(link, s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"<em>\1</em>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", s)
    return s


def render(md: str, heading_offset: int = 2) -> str:
    lines = (md or "").splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre{cls}><code>{html.escape(chr(10).join(buf))}</code></pre>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = min(6, len(m.group(1)) + heading_offset - 1)
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th scope=\"col\">{_inline(h)}</th>" for h in header)
            tb = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue
        if re.match(r"^\s*([-*]|\d+[.)])\s+", line):
            ordered = bool(re.match(r"^\s*\d+[.)]\s+", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+[.)])\s+", lines[i]):
                item = re.sub(r"^\s*([-*]|\d+[.)])\s+", "", lines[i])
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip() and not re.match(r"^\s*([-*]|\d+[.)])\s+", lines[i]):
                    item += " " + lines[i].strip()
                    i += 1
                tm = re.match(r"^\[( |x|X|~)\]\s+(.*)$", item)
                if tm:
                    mark = {"x": "done", "X": "done", "~": "na", " ": "open"}[tm.group(1)]
                    label = {"done": "Done", "na": "Not applicable", "open": "Open"}[mark]
                    items.append(f'<li class="task task-{mark}"><span class="task-mark" aria-label="{label}"></span>{_inline(tm.group(2))}</li>')
                else:
                    items.append(f"<li>{_inline(item)}</li>")
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        if stripped.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{_inline(' '.join(buf))}</blockquote>")
            continue
        if not stripped:
            i += 1
            continue
        buf = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|\||>|\s*([-*]|\d+[.)])\s)", lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{_inline(' '.join(buf))}</p>")
    return "\n".join(out)


def inline(text: str) -> str:
    return _inline(text or "")
