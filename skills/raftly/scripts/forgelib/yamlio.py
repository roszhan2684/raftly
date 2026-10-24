"""Minimal, dependency-free YAML subset reader/writer.

Raftly keeps project state in YAML so humans and Claude can read and edit it.
To avoid a PyYAML dependency this module supports the subset Raftly files use:

* block mappings and block sequences (including ``- key: value`` items)
* flow collections: ``[a, b]`` and ``{a: 1, b: [x, y]}``
* plain, single-quoted and double-quoted scalars
* block scalars: ``|``, ``|-``, ``>``, ``>-``
* comments (``# ...``), blank lines and a leading ``---``
* scalars: null/~, true/false, integers, floats. Dates and timestamps stay
  strings on purpose (no implicit date conversion).

Anchors, aliases, tags, multi-document streams and complex keys are not
supported and raise ``YAMLError`` instead of being silently misread.
"""

from __future__ import annotations

import json
import re
from typing import Any

__all__ = ["YAMLError", "loads", "dumps", "load_file", "dump_file"]


class YAMLError(ValueError):
    """Raised when input is outside the supported subset or malformed."""

    def __init__(self, message: str, line: int | None = None):
        self.line = line
        super().__init__(f"line {line}: {message}" if line else message)


# ---------------------------------------------------------------------------
# Scalars
# ---------------------------------------------------------------------------

_INT_RE = re.compile(r"^[-+]?(0|[1-9][0-9_]*)$")
_FLOAT_RE = re.compile(r"^[-+]?(\d[\d_]*)?\.\d+([eE][-+]?\d+)?$|^[-+]?\d[\d_]*[eE][-+]?\d+$")
_NULLS = {"", "~", "null", "Null", "NULL"}
_TRUES = {"true", "True", "TRUE"}
_FALSES = {"false", "False", "FALSE"}


def _plain_scalar(text: str) -> Any:
    t = text.strip()
    if t in _NULLS:
        return None
    if t in _TRUES:
        return True
    if t in _FALSES:
        return False
    if _INT_RE.match(t):
        return int(t.replace("_", ""))
    if _FLOAT_RE.match(t):
        return float(t.replace("_", ""))
    if t in (".inf", "+.inf"):
        return float("inf")
    if t == "-.inf":
        return float("-inf")
    if t.startswith(("&", "*", "!")):
        raise YAMLError(f"anchors, aliases and tags are not supported: {t!r}")
    return t


def _parse_double_quoted(s: str, line: int) -> tuple[str, int]:
    """Parse a double-quoted scalar starting at s[0] == '"'. Returns (value, end_index)."""
    i = 1
    out = []
    while i < len(s):
        c = s[i]
        if c == "\\":
            if i + 1 >= len(s):
                raise YAMLError("unterminated escape in double-quoted string", line)
            n = s[i + 1]
            simple = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/", "0": "\0", " ": " ", "b": "\b", "f": "\f"}
            if n in simple:
                out.append(simple[n])
                i += 2
            elif n == "u":
                out.append(chr(int(s[i + 2 : i + 6], 16)))
                i += 6
            elif n == "x":
                out.append(chr(int(s[i + 2 : i + 4], 16)))
                i += 4
            else:
                raise YAMLError(f"unsupported escape \\{n}", line)
        elif c == '"':
            return "".join(out), i + 1
        else:
            out.append(c)
            i += 1
    raise YAMLError("unterminated double-quoted string", line)


def _parse_single_quoted(s: str, line: int) -> tuple[str, int]:
    i = 1
    out = []
    while i < len(s):
        c = s[i]
        if c == "'":
            if i + 1 < len(s) and s[i + 1] == "'":
                out.append("'")
                i += 2
                continue
            return "".join(out), i + 1
        out.append(c)
        i += 1
    raise YAMLError("unterminated single-quoted string", line)


def _strip_comment(s: str) -> str:
    """Remove a trailing ``# comment`` that is outside quotes."""
    in_s = in_d = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and in_d:
            i += 2
            continue
        if c == "'" and not in_d:
            in_s = not in_s
        elif c == '"' and not in_s:
            in_d = not in_d
        elif c == "#" and not in_s and not in_d and (i == 0 or s[i - 1] in " \t"):
            return s[:i].rstrip()
        i += 1
    return s.rstrip()


# ---------------------------------------------------------------------------
# Flow collections
# ---------------------------------------------------------------------------


class _Flow:
    def __init__(self, text: str, line: int):
        self.s = text
        self.i = 0
        self.line = line

    def ws(self) -> None:
        while self.i < len(self.s) and self.s[self.i] in " \t\n":
            self.i += 1

    def parse(self) -> Any:
        self.ws()
        v = self.value()
        self.ws()
        if self.i != len(self.s):
            raise YAMLError(f"unexpected trailing text in flow value: {self.s[self.i:]!r}", self.line)
        return v

    def value(self) -> Any:
        self.ws()
        if self.i >= len(self.s):
            return None
        c = self.s[self.i]
        if c == "[":
            return self.seq()
        if c == "{":
            return self.map()
        if c == '"':
            v, end = _parse_double_quoted(self.s[self.i :], self.line)
            self.i += end
            return v
        if c == "'":
            v, end = _parse_single_quoted(self.s[self.i :], self.line)
            self.i += end
            return v
        start = self.i
        while self.i < len(self.s) and self.s[self.i] not in ",]}":
            if self.s[self.i] == ":" and (self.i + 1 >= len(self.s) or self.s[self.i + 1] in " ,]}"):
                break
            self.i += 1
        return _plain_scalar(self.s[start : self.i])

    def seq(self) -> list:
        self.i += 1
        out: list = []
        self.ws()
        if self.i < len(self.s) and self.s[self.i] == "]":
            self.i += 1
            return out
        while True:
            out.append(self.value())
            self.ws()
            if self.i >= len(self.s):
                raise YAMLError("unterminated flow sequence", self.line)
            if self.s[self.i] == ",":
                self.i += 1
                self.ws()
                if self.i < len(self.s) and self.s[self.i] == "]":
                    self.i += 1
                    return out
                continue
            if self.s[self.i] == "]":
                self.i += 1
                return out
            raise YAMLError(f"expected ',' or ']' in flow sequence near {self.s[self.i:]!r}", self.line)

    def map(self) -> dict:
        self.i += 1
        out: dict = {}
        self.ws()
        if self.i < len(self.s) and self.s[self.i] == "}":
            self.i += 1
            return out
        while True:
            key = self.value()
            self.ws()
            if self.i >= len(self.s) or self.s[self.i] != ":":
                raise YAMLError("expected ':' in flow mapping", self.line)
            self.i += 1
            out[_key(key, self.line)] = self.value()
            self.ws()
            if self.i >= len(self.s):
                raise YAMLError("unterminated flow mapping", self.line)
            if self.s[self.i] == ",":
                self.i += 1
                self.ws()
                if self.i < len(self.s) and self.s[self.i] == "}":
                    self.i += 1
                    return out
                continue
            if self.s[self.i] == "}":
                self.i += 1
                return out
            raise YAMLError("expected ',' or '}' in flow mapping", self.line)


def _key(k: Any, line: int) -> str:
    if isinstance(k, (dict, list)):
        raise YAMLError("complex mapping keys are not supported", line)
    if k is None:
        return "null"
    if isinstance(k, bool):
        return "true" if k else "false"
    return str(k)


# ---------------------------------------------------------------------------
# Block parser
# ---------------------------------------------------------------------------


class _Line:
    __slots__ = ("no", "indent", "text", "raw")

    def __init__(self, no: int, indent: int, text: str, raw: str):
        self.no = no
        self.indent = indent
        self.text = text
        self.raw = raw


def _split_key(text: str, line: int) -> tuple[str, str] | None:
    """If ``text`` is ``key: rest`` return (key, rest) else None."""
    if text.startswith('"'):
        k, end = _parse_double_quoted(text, line)
        rest = text[end:]
        if rest.startswith(":") and (len(rest) == 1 or rest[1] in " \t"):
            return k, rest[1:].strip()
        return None
    if text.startswith("'"):
        k, end = _parse_single_quoted(text, line)
        rest = text[end:]
        if rest.startswith(":") and (len(rest) == 1 or rest[1] in " \t"):
            return k, rest[1:].strip()
        return None
    if text.startswith(("[", "{")):
        return None
    m = re.match(r"^([^:#\s][^:]*?|[^:#\s]):(\s+|$)(.*)$", text)
    if not m:
        return None
    return m.group(1).strip(), m.group(3)


class _Parser:
    def __init__(self, text: str):
        self.raw_lines = text.splitlines()
        self.lines: list[_Line] = []
        for idx, raw in enumerate(self.raw_lines, start=1):
            if "\t" in raw[: len(raw) - len(raw.lstrip())]:
                raise YAMLError("tabs are not allowed for indentation", idx)
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped == "---" and not self.lines:
                continue
            if stripped in ("---", "...") and self.lines:
                if stripped == "...":
                    break
                raise YAMLError("multiple YAML documents are not supported", idx)
            indent = len(raw) - len(raw.lstrip(" "))
            self.lines.append(_Line(idx, indent, raw.strip(), raw))
        self.pos = 0

    def parse(self) -> Any:
        if not self.lines:
            return None
        value = self.block(self.lines[0].indent)
        if self.pos < len(self.lines):
            ln = self.lines[self.pos]
            raise YAMLError(f"unexpected content (bad indentation?): {ln.text!r}", ln.no)
        return value

    def peek(self) -> _Line | None:
        return self.lines[self.pos] if self.pos < len(self.lines) else None

    def block(self, indent: int) -> Any:
        ln = self.peek()
        if ln is None:
            return None
        if ln.text == "-" or ln.text.startswith("- "):
            return self.seq(ln.indent)
        if _split_key(_strip_comment(ln.text), ln.no) is not None:
            return self.mapping(ln.indent)
        # single scalar document / flow value
        self.pos += 1
        return self.inline_value(_strip_comment(ln.text), ln, ln.indent)

    def mapping(self, indent: int) -> dict:
        out: dict = {}
        while True:
            ln = self.peek()
            if ln is None or ln.indent < indent:
                return out
            if ln.indent > indent:
                raise YAMLError(f"unexpected indentation: {ln.text!r}", ln.no)
            text = _strip_comment(ln.text)
            if text == "-" or text.startswith("- "):
                return out
            kv = _split_key(text, ln.no)
            if kv is None:
                raise YAMLError(f"expected 'key: value', got {ln.text!r}", ln.no)
            key, rest = kv
            if key in out:
                raise YAMLError(f"duplicate key {key!r}", ln.no)
            self.pos += 1
            out[key] = self.value_after_key(rest, ln, indent)

    def value_after_key(self, rest: str, ln: _Line, indent: int) -> Any:
        if rest == "":
            nxt = self.peek()
            if nxt is None:
                return None
            if nxt.indent > indent:
                return self.block(nxt.indent)
            # YAML allows a sequence at the same indent as its parent key
            if nxt.indent == indent and (nxt.text == "-" or nxt.text.startswith("- ")):
                return self.seq(indent)
            return None
        return self.inline_value(rest, ln, indent)

    def inline_value(self, rest: str, ln: _Line, indent: int) -> Any:
        if rest.startswith(("|", ">")) and re.match(r"^[|>][-+]?$", rest):
            return self.block_scalar(rest, indent)
        if rest.startswith(("[", "{")):
            text = rest
            # allow flow collections spanning multiple lines
            depth_ok = _balanced(text)
            while not depth_ok:
                nxt = self.peek()
                if nxt is None:
                    raise YAMLError("unterminated flow collection", ln.no)
                text += " " + _strip_comment(nxt.text)
                self.pos += 1
                depth_ok = _balanced(text)
            return _Flow(text, ln.no).parse()
        if rest.startswith('"'):
            v, end = _parse_double_quoted(rest, ln.no)
            if rest[end:].strip():
                raise YAMLError(f"unexpected text after quoted string: {rest[end:]!r}", ln.no)
            return v
        if rest.startswith("'"):
            v, end = _parse_single_quoted(rest, ln.no)
            if rest[end:].strip():
                raise YAMLError(f"unexpected text after quoted string: {rest[end:]!r}", ln.no)
            return v
        # plain multi-line scalars: continuation lines indented deeper
        parts = [rest]
        while True:
            nxt = self.peek()
            if nxt is None or nxt.indent <= indent:
                break
            t = _strip_comment(nxt.text)
            if t.startswith("- ") or _split_key(t, nxt.no) is not None:
                break
            parts.append(t)
            self.pos += 1
        if len(parts) > 1:
            return " ".join(p.strip() for p in parts)
        return _plain_scalar(rest)

    def block_scalar(self, header: str, indent: int) -> str:
        style, chomp = header[0], header[1:] or ""
        # collect raw lines (including blank lines) belonging to the scalar
        start_line_no = self.lines[self.pos - 1].no if self.pos > 0 else 0
        collected: list[str] = []
        block_indent = None
        raw_idx = start_line_no  # raw_lines index of next raw line (0-based == line number)
        while raw_idx < len(self.raw_lines):
            raw = self.raw_lines[raw_idx]
            if raw.strip() == "":
                collected.append("")
                raw_idx += 1
                continue
            ind = len(raw) - len(raw.lstrip(" "))
            if block_indent is None:
                if ind <= indent:
                    break
                block_indent = ind
            if ind < block_indent:
                break
            collected.append(raw[block_indent:])
            raw_idx += 1
        # advance self.pos past consumed logical lines
        while self.pos < len(self.lines) and self.lines[self.pos].no <= raw_idx:
            self.pos += 1
        # trailing blank lines
        while collected and collected[-1] == "" and chomp != "+":
            collected.pop()
        if style == "|":
            text = "\n".join(collected)
        else:
            text = ""
            prev_blank = False
            for c in collected:
                if c == "":
                    text += "\n"
                    prev_blank = True
                else:
                    if text and not text.endswith("\n") and not prev_blank:
                        text += " "
                    text += c
                    prev_blank = False
        if chomp == "-":
            return text
        return text + "\n" if text else text

    def seq(self, indent: int) -> list:
        out: list = []
        while True:
            ln = self.peek()
            if ln is None or ln.indent < indent:
                return out
            if ln.indent > indent:
                raise YAMLError(f"unexpected indentation in sequence: {ln.text!r}", ln.no)
            text = _strip_comment(ln.text)
            if not (text == "-" or text.startswith("- ")):
                return out
            self.pos += 1
            item = text[1:].strip()
            if item == "":
                nxt = self.peek()
                if nxt is not None and nxt.indent > indent:
                    out.append(self.block(nxt.indent))
                else:
                    out.append(None)
                continue
            content_indent = indent + (len(text) - len(text[1:].lstrip()))
            kv = _split_key(item, ln.no) if not item.startswith(("[", "{", '"', "'")) or _split_key(item, ln.no) else None
            if kv is not None and not item.startswith(("[", "{")):
                # mapping that starts on the dash line
                key, rest = kv
                m: dict = {}
                m[key] = self.value_after_key(rest, ln, content_indent)
                nxt = self.peek()
                if nxt is not None and nxt.indent == content_indent and not (
                    nxt.text == "-" or nxt.text.startswith("- ")
                ):
                    more = self.mapping(content_indent)
                    for k, v in more.items():
                        if k in m:
                            raise YAMLError(f"duplicate key {k!r}", nxt.no)
                        m[k] = v
                out.append(m)
            elif item.startswith("- "):
                raise YAMLError("nested inline sequences ('- - x') are not supported; use a block", ln.no)
            else:
                out.append(self.inline_value(item, ln, indent))


def _balanced(text: str) -> bool:
    depth = 0
    in_s = in_d = False
    i = 0
    while i < len(text):
        c = text[i]
        if in_d:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_d = False
        elif in_s:
            if c == "'":
                in_s = False
        elif c == '"':
            in_d = True
        elif c == "'":
            in_s = True
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
        i += 1
    return depth <= 0


def loads(text: str) -> Any:
    """Parse YAML text (supported subset) into Python objects."""
    return _Parser(text).parse()


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------

_PLAIN_SAFE = re.compile(r"^[A-Za-z0-9_./@()+$%^&=~<>\-][A-Za-z0-9 _./@()+$%^&=~<>,\-]*$")
_RESERVED_WORDS = _NULLS | _TRUES | _FALSES | {"yes", "no", "Yes", "No", "YES", "NO", "on", "off", "On", "Off"}


def _needs_quotes(s: str) -> bool:
    if s == "" or s != s.strip():
        return True
    if s in _RESERVED_WORDS:
        return True
    if _INT_RE.match(s) or _FLOAT_RE.match(s):
        return True
    if s.startswith(("-", "?", ":", "&", "*", "!", "|", ">", "%", "@", "`", "~")) and not re.match(r"^-\w", s):
        return True
    if s.startswith("-") and len(s) > 1 and s[1] == " ":
        return True
    if ": " in s or " #" in s or s.endswith(":"):
        return True
    return not bool(_PLAIN_SAFE.match(s))


def _scalar(v: Any) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v != v:
            return ".nan"
        if v in (float("inf"), float("-inf")):
            return ".inf" if v > 0 else "-.inf"
        return repr(v)
    s = str(v)
    if _needs_quotes(s):
        return json.dumps(s, ensure_ascii=False)
    return s


def _dump(value: Any, indent: int, out: list[str]) -> None:
    pad = " " * indent
    if isinstance(value, dict):
        for k, v in value.items():
            key = _scalar(str(k))
            if isinstance(v, dict) and v:
                out.append(f"{pad}{key}:")
                _dump(v, indent + 2, out)
            elif isinstance(v, list) and v:
                out.append(f"{pad}{key}:")
                _dump(v, indent + 2, out)
            elif _is_block(v):
                out.append(f"{pad}{key}: {_block_header(v)}")
                for line in v.rstrip("\n").split("\n"):
                    out.append(f"{pad}  {line}" if line else "")
            else:
                out.append(f"{pad}{key}: {_inline(v)}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item:
                first = True
                for k, v in item.items():
                    prefix = f"{pad}- " if first else f"{pad}  "
                    first = False
                    key = _scalar(str(k))
                    if isinstance(v, (dict, list)) and v:
                        out.append(f"{prefix}{key}:")
                        _dump(v, indent + 4, out)
                    elif _is_block(v):
                        out.append(f"{prefix}{key}: {_block_header(v)}")
                        for line in v.rstrip("\n").split("\n"):
                            out.append(f"{pad}    {line}" if line else "")
                    else:
                        out.append(f"{prefix}{key}: {_inline(v)}")
            elif isinstance(item, list) and item:
                out.append(f"{pad}-")
                _dump(item, indent + 2, out)
            elif _is_block(item):
                out.append(f"{pad}- {_block_header(item)}")
                for line in item.rstrip("\n").split("\n"):
                    out.append(f"{pad}  {line}" if line else "")
            else:
                out.append(f"{pad}- {_inline(item)}")
    else:
        out.append(f"{pad}{_inline(value)}")


def _is_block(v: Any) -> bool:
    """Multi-line strings are written as literal blocks when safe to do so."""
    return isinstance(v, str) and "\n" in v and not v.startswith((" ", "\n")) and "\t" not in v


def _block_header(s: str) -> str:
    return "|" if s.endswith("\n") else "|-"


def _inline(v: Any) -> str:
    if isinstance(v, dict):
        if not v:
            return "{}"
        return "{" + ", ".join(f"{_scalar(str(k))}: {_inline(x)}" for k, x in v.items()) + "}"
    if isinstance(v, list):
        if not v:
            return "[]"
        return "[" + ", ".join(_inline(x) for x in v) + "]"
    if isinstance(v, str) and "\n" in v:
        return json.dumps(v, ensure_ascii=False)
    return _scalar(v)


def dumps(value: Any, header: str | None = None) -> str:
    """Serialise Python data to YAML using the supported subset.

    The output always round-trips through :func:`loads`.
    """
    out: list[str] = []
    if header:
        for line in header.strip().splitlines():
            out.append(f"# {line}" if line else "#")
    if isinstance(value, (dict, list)) and not value:
        out.append(_inline(value))
    else:
        _dump(value, 0, out)
    return "\n".join(out) + "\n"


def load_file(path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return loads(fh.read())


def dump_file(path, value: Any, header: str | None = None) -> None:
    from .fsutil import atomic_write

    atomic_write(path, dumps(value, header=header))
