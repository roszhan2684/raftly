"""Shared CLI plumbing: --root/--json flags, error handling, output."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from .project import ForgeError, Project
from .yamlio import YAMLError
from .fsutil import ForgePathError


class _Parser(argparse.ArgumentParser):
    """Accept the global --root/--json flags anywhere on the command line.

    argparse only recognises top-level options before a subcommand; Claude and
    humans naturally append ``--json`` at the end, so hoist them first.
    """

    def parse_args(self, args=None, namespace=None):  # type: ignore[override]
        args = list(sys.argv[1:] if args is None else args)
        hoisted: list[str] = []
        rest: list[str] = []
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--json":
                hoisted.append(a)
            elif a == "--root" and i + 1 < len(args):
                hoisted += [a, args[i + 1]]
                i += 1
            elif a.startswith("--root="):
                hoisted.append(a)
            else:
                rest.append(a)
            i += 1
        return super().parse_args(hoisted + rest, namespace)


def parser(prog: str, description: str) -> argparse.ArgumentParser:
    p = _Parser(prog=prog, description=description)
    p.add_argument("--root", default=None, help="project root containing .raftly/ (default: current directory)")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    return p


def project(args) -> Project:
    return Project(args.root)


def emit(args, data: Any, text: Callable[[Any], str] | str | None = None) -> None:
    if getattr(args, "json", False) or text is None:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        print(text(data) if callable(text) else text)


def run(main: Callable[[list[str]], int | None]) -> None:
    try:
        code = main(sys.argv[1:])
    except (ForgeError, YAMLError, ForgePathError) as exc:
        from .brand import brand

        print(f"{brand()['skill_command']}: error: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)
    sys.exit(code or 0)


def parse_kv(pairs: list[str]) -> dict:
    """Parse ``key=value`` pairs. Values are parsed as YAML scalars/flow (``[a, b]``)."""
    from .yamlio import loads

    out = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise ForgeError(f"expected key=value, got {pair!r}")
        k, v = pair.split("=", 1)
        out[k.strip()] = loads(v) if v.strip() else ""
    return out


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]
