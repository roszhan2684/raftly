"""Filesystem helpers: atomic writes, path containment, plugin-core protection."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

# The skill directory (skills/forge/). Everything Raftly needs at runtime lives inside it,
# so the skill also works when copied on its own into a skills directory.
SKILL_ROOT = Path(__file__).resolve().parents[2]
# When installed as a plugin, the plugin root is two levels above the skill.
PLUGIN_ROOT = SKILL_ROOT.parents[1] if SKILL_ROOT.parent.name == "skills" else None


class ForgePathError(ValueError):
    """Raised when a path escapes its allowed root or targets Raftly core."""


def atomic_write(path, content: str) -> None:
    """Write text atomically: temp file in the same directory, fsync, rename."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        # mkstemp creates 0600 files; keep the existing mode, or use the umask default
        try:
            mode = path.stat().st_mode & 0o777
        except FileNotFoundError:
            umask = os.umask(0)
            os.umask(umask)
            mode = 0o666 & ~umask
        os.chmod(tmp, mode)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def resolve_inside(root, relative) -> Path:
    """Resolve ``relative`` under ``root`` and refuse anything that escapes it."""
    root_p = Path(root).resolve()
    candidate = (root_p / relative).resolve()
    try:
        candidate.relative_to(root_p)
    except ValueError as exc:
        raise ForgePathError(f"path escapes project root: {relative}") from exc
    return candidate


def is_inside(path, root) -> bool:
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def protected_roots() -> list[Path]:
    roots = [SKILL_ROOT]
    if PLUGIN_ROOT is not None:
        roots += [PLUGIN_ROOT / ".claude-plugin", PLUGIN_ROOT / "agents", PLUGIN_ROOT / "skills"]
    return roots


def assert_not_plugin_core(path) -> None:
    """Constitution rule 21: never mutate the installed Raftly core from a project.

    Refuses writes anywhere inside the skill directory and, in a plugin install, the
    plugin manifest and agents. Writes elsewhere in a plugin checkout (for example the
    shipped ``examples/``) are allowed.
    """
    p = Path(path).resolve()
    for root in protected_roots():
        if is_inside(p, root):
            raise ForgePathError(
                f"refusing to write inside Raftly core ({root.name}/): {p}. "
                "Generate a learning proposal instead (learning.py propose)."
            )


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_len: int = 48) -> str:
    s = _SLUG_RE.sub("-", text.lower()).strip("-")
    return (s[:max_len].rstrip("-")) or "item"


def read_text(path) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()
