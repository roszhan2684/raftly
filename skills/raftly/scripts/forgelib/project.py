"""Access to a project's ``.raftly/`` directory and, for new projects, its ``docs/`` folder.

Two layouts:
- classic: everything (machine state and readable documents) lives in ``.raftly/``;
  build outputs go to ``artifacts/``. Used for existing repositories.
- docs: machine state (YAML) stays in ``.raftly/``; every readable document and
  document folder lives in ``docs/``, together with the build outputs. Used for
  projects Raftly creates from scratch. Recorded as ``engine.docs_dir`` in state.yaml.
"""

from __future__ import annotations

import datetime as _dt
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from . import FORGE_VERSION, SCHEMA_VERSION, model, yamlio
from .brand import brand
from .fsutil import assert_not_plugin_core, atomic_write, read_text, resolve_inside, slugify
from .schema import validate_named

FORGE_DIR = brand()["state_dir"]
LEGACY_DIRS = [d for d in brand().get("legacy_state_dirs") or [] if d != FORGE_DIR]

# Registry files: name -> (top-level list key, schema name)
REGISTRIES = {
    "requirements.yaml": ("requirements", "requirements"),
    "assumptions.yaml": ("assumptions", "assumptions"),
    "risks.yaml": ("risks", "risks"),
    "dependencies.yaml": ("dependencies", "dependencies"),
    "build-graph.yaml": ("nodes", "build-graph"),
    "experiments.yaml": ("experiments", "experiments"),
}

# Markdown record directories: kind -> (directory, frontmatter schema)
RECORD_DIRS = {
    "decision": ("decisions", "decision"),
    "feature": ("features", "feature"),
    "debt": ("debt", "debt"),
    "learning": ("learnings", "learning"),
    "candidate": ("learning-candidates", "learning-candidate"),
    "postmortem": ("postmortems", "postmortem"),
}

# Document folders that move to docs/ in the docs layout. Project memory
# (learnings/, learning-candidates/) stays with the machine state.
DOC_DIRS = {"decisions", "features", "prompts", "research", "postmortems", "debt", "brand", "design"}
DEFAULT_DOCS_DIR = "docs"


def is_doc_path(relative: str) -> bool:
    """True for a top-level Markdown document or anything inside a document folder."""
    parts = PurePosixPath(str(relative).replace("\\", "/")).parts
    if not parts:
        return False
    if len(parts) == 1:
        return parts[0].lower().endswith(".md") or parts[0] in DOC_DIRS
    return parts[0] in DOC_DIRS


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)


class ForgeError(Exception):
    """User-facing error (bad input, missing project, rule violation)."""


def now_iso() -> str:
    override = os.environ.get("FORGE_NOW")  # deterministic tests/golden files
    if override:
        return override
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return now_iso()[:10]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    data = yamlio.loads(m.group(1)) or {}
    if not isinstance(data, dict):
        raise ForgeError("frontmatter must be a mapping")
    return data, text[m.end():]


def render_frontmatter(data: dict, body: str) -> str:
    return "---\n" + yamlio.dumps(data) + "---\n" + body.lstrip("\n")


class Project:
    def __init__(self, root: str | os.PathLike | None = None):
        self.root = Path(root or os.getcwd()).resolve()
        self.forge = self.root / FORGE_DIR
        self.legacy_dir = None
        if not (self.forge / "state.yaml").exists():
            for legacy in LEGACY_DIRS:  # older installs: keep reading/writing until migrated
                if (self.root / legacy / "state.yaml").exists():
                    self.legacy_dir = self.root / legacy
                    self.forge = self.legacy_dir
                    break
        self._docs_dir: str | None | bool = False  # False = not read yet

    # -- basics -------------------------------------------------------------

    @property
    def exists(self) -> bool:
        return (self.forge / "state.yaml").exists()

    def require(self) -> "Project":
        if not self.exists:
            raise ForgeError(
                f"no {brand()['short_name']} project at {self.root} ({FORGE_DIR}/state.yaml missing). Run init_project.py first."
            )
        return self

    def docs_dir_name(self) -> str | None:
        """``engine.docs_dir`` from state.yaml (docs layout), or None (classic layout)."""
        if self._docs_dir is False:
            name = None
            state_file = self.forge / "state.yaml"
            if state_file.exists():
                try:
                    name = ((yamlio.load_file(state_file) or {}).get("engine") or {}).get("docs_dir")
                except yamlio.YAMLError:
                    name = None
            self._docs_dir = name or None
        return self._docs_dir or None

    def use_docs_dir(self, name: str | None) -> None:
        """Set the layout before state.yaml exists (init)."""
        self._docs_dir = name or None

    @property
    def docs(self) -> Path:
        """Folder holding readable documents."""
        name = self.docs_dir_name()
        return resolve_inside(self.root, name) if name else self.forge

    @property
    def artifacts(self) -> Path:
        """Folder for build outputs (blueprint.html, deck.md)."""
        return self.docs if self.docs_dir_name() else self.root / "artifacts"

    def path(self, relative: str) -> Path:
        base = self.docs if is_doc_path(relative) else self.forge
        return resolve_inside(base, relative)

    def write_text(self, relative: str, content: str) -> Path:
        p = self.path(relative)
        assert_not_plugin_core(p)
        atomic_write(p, content)
        return p

    # -- yaml ---------------------------------------------------------------

    def load_yaml(self, relative: str, default: Any = None) -> Any:
        p = self.path(relative)
        if not p.exists():
            return default
        try:
            return yamlio.load_file(p)
        except yamlio.YAMLError as exc:
            raise ForgeError(f"{relative}: {exc}") from exc

    def save_yaml(self, relative: str, data: Any, schema: str | None = None, header: str | None = None) -> Path:
        if schema:
            errors = validate_named(data, schema)
            if errors:
                raise ForgeError(f"{relative} failed schema '{schema}':\n  " + "\n  ".join(errors[:20]))
        p = self.path(relative)
        assert_not_plugin_core(p)
        yamlio.dump_file(p, data, header=header)
        return p

    # -- state --------------------------------------------------------------

    def state(self) -> dict:
        self.require()
        data = self.load_yaml("state.yaml")
        if not isinstance(data, dict):
            raise ForgeError("state.yaml is empty or not a mapping")
        return data

    def save_state(self, state: dict, event: str | None = None) -> None:
        state.setdefault("project", {})["updated_at"] = now_iso()
        if event:
            state.setdefault("history", []).append({"at": now_iso(), "event": event})
        self.save_yaml("state.yaml", state, schema="state", header=STATE_HEADER)

    # -- registries -----------------------------------------------------------

    def registry(self, filename: str) -> list[dict]:
        key, _ = REGISTRIES[filename]
        data = self.load_yaml(filename, default=None) or {}
        items = data.get(key) or []
        if not isinstance(items, list):
            raise ForgeError(f"{filename}: '{key}' must be a list")
        return items

    def save_registry(self, filename: str, items: list[dict], extra: dict | None = None) -> None:
        key, schema = REGISTRIES[filename]
        data = self.load_yaml(filename, default=None) or {}
        if extra:
            data.update(extra)
        data[key] = items
        self.save_yaml(filename, data, schema=schema)

    def evidence(self) -> dict:
        data = self.load_yaml("evidence.yaml", default=None) or {}
        data.setdefault("entities", [])
        data.setdefault("links", [])
        data.setdefault("records", [])
        return data

    def save_evidence(self, data: dict) -> None:
        self.save_yaml("evidence.yaml", data, schema="evidence")

    def gate(self) -> dict | None:
        return self.load_yaml("gate.yaml", default=None)

    def save_gate(self, data: dict) -> None:
        self.save_yaml("gate.yaml", data, schema="gate")

    # -- markdown records ----------------------------------------------------

    def records(self, kind: str) -> list[tuple[Path, dict, str]]:
        directory, _ = RECORD_DIRS[kind]
        d = self.path(directory)
        out = []
        if not d.is_dir():
            return out
        for p in sorted(d.glob("*.md")):
            if p.name.lower() == "readme.md":
                continue
            fm, body = parse_frontmatter(read_text(p))
            out.append((p, fm, body))
        return out

    def find_record(self, kind: str, identifier: str) -> tuple[Path, dict, str]:
        for p, fm, body in self.records(kind):
            if fm.get("id") == identifier:
                return p, fm, body
        raise ForgeError(f"{kind} {identifier} not found")

    def write_record(self, kind: str, fm: dict, body: str, filename: str | None = None) -> Path:
        directory, schema = RECORD_DIRS[kind]
        errors = validate_named(fm, schema)
        if errors:
            raise ForgeError(f"{kind} frontmatter invalid:\n  " + "\n  ".join(errors[:20]))
        if filename is None:
            filename = f"{fm['id']}-{slugify(fm.get('title') or fm.get('name') or fm.get('statement') or 'record')}.md"
        return self.write_text(f"{directory}/{filename}", render_frontmatter(fm, body))

    def update_record(self, path: Path, fm: dict, body: str, kind: str) -> None:
        _, schema = RECORD_DIRS[kind]
        errors = validate_named(fm, schema)
        if errors:
            raise ForgeError(f"{kind} frontmatter invalid:\n  " + "\n  ".join(errors[:20]))
        assert_not_plugin_core(path)
        atomic_write(path, render_frontmatter(fm, body))

    # -- ids -----------------------------------------------------------------

    def existing_ids(self, kind: str) -> list[str]:
        if kind in RECORD_DIRS:
            return [fm.get("id") for _, fm, _ in self.records(kind) if fm.get("id")]
        if kind == "requirement":
            return [r.get("id") for r in self.registry("requirements.yaml")]
        if kind == "assumption":
            return [r.get("id") for r in self.registry("assumptions.yaml")]
        if kind == "risk":
            return [r.get("id") for r in self.registry("risks.yaml")]
        if kind == "node":
            return [r.get("id") for r in self.registry("build-graph.yaml")]
        if kind == "evidence":
            return [r.get("id") for r in self.evidence()["records"]]
        if kind == "experiment":
            return [r.get("id") for r in self.registry("experiments.yaml")]
        raise ForgeError(f"no id sequence for kind {kind!r}")

    def next_id(self, kind: str) -> str:
        nums = [model.id_number(i) for i in self.existing_ids(kind) if i]
        return model.format_id(kind, (max(nums) + 1) if nums else 1)

    def all_known_ids(self) -> set[str]:
        ids: set[str] = set()
        for kind in ("requirement", "assumption", "risk", "node", "evidence", "experiment"):
            ids.update(i for i in self.existing_ids(kind) if i)
        for kind in RECORD_DIRS:
            ids.update(i for i in self.existing_ids(kind) if i)
        ids.update(e.get("id") for e in self.evidence()["entities"] if e.get("id"))
        return ids

    def prompts(self) -> list[Path]:
        d = self.path("prompts")
        return sorted(d.glob("[0-9][0-9][0-9]-*.md")) if d.is_dir() else []


STATE_HEADER = """Project state. Canonical source of truth for mode, stage and progress.
Edit with scripts/state.py where possible; validate with scripts/validate_project.py."""


def new_state(name: str, mode: str, product_type: str, profile: dict, stage: str = "INTAKE",
              docs_dir: str | None = None) -> dict:
    ts = now_iso()
    engine = {"version": FORGE_VERSION, "schema_version": SCHEMA_VERSION}
    if docs_dir:
        engine["docs_dir"] = docs_dir
    return {
        "engine": engine,
        "project": {
            "name": name,
            "slug": slugify(name),
            "mode": mode,
            "stage": stage,
            "product_type": product_type,
            "profile": profile,
            "created_at": ts,
            "updated_at": ts,
        },
        "blueprint": {
            "status": "NOT_STARTED",
            **{s: "NOT_STARTED" for s in model.BLUEPRINT_SECTIONS},
            "open_founder_decisions": [],
        },
        "execution": {"current_node": None, "next_nodes": []},
        "production": {"readiness": "UNVERIFIED", "last_gate_at": None},
        "documents": {},
        "counts": {
            "requirements": 0,
            "features": 0,
            "decisions": 0,
            "risks": 0,
            "assumptions": 0,
            "debt": 0,
            "nodes": 0,
            "prompts": 0,
        },
        "learning": {"project_learnings": 0, "candidates": 0},
        "history": [{"at": ts, "event": f"Project initialised in {mode} mode"}],
    }


def recount(project: Project, state: dict) -> dict:
    state["counts"] = {
        "requirements": len(project.registry("requirements.yaml")),
        "features": len(project.records("feature")),
        "decisions": len(project.records("decision")),
        "risks": len(project.registry("risks.yaml")),
        "assumptions": len(project.registry("assumptions.yaml")),
        "debt": len(project.records("debt")),
        "nodes": len(project.registry("build-graph.yaml")),
        "prompts": len(project.prompts()),
    }
    state.setdefault("learning", {})
    state["learning"]["project_learnings"] = len(project.records("learning"))
    state["learning"]["candidates"] = len(project.records("candidate"))
    return state


def iter_dotted(data: dict, dotted: str) -> Iterable[Any]:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise ForgeError(f"no such field: {dotted}")
        cur = cur[part]
    yield cur
