"""Test helpers: temp projects, CLI runner, deterministic clock."""

from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = next(iter(sorted((REPO / "skills").glob("*/core/brand.yaml")))).parents[1]
SCRIPTS = SKILL / "scripts"
for _p in (REPO / "scripts", SCRIPTS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

os.environ.setdefault("FORGE_NOW", "2026-01-15T10:00:00Z")

import engine  # noqa: E402


class CLIResult:
    def __init__(self, code: int, out: str, err: str):
        self.code, self.out, self.err = code, out, err

    def json(self):
        return json.loads(self.out)


def run(*argv: str, root: str | Path | None = None) -> CLIResult:
    """Run engine.py in-process. Returns exit code, stdout, stderr."""
    args = list(argv)
    if root is not None and args and args[0] not in ("inspect",):
        args = [args[0], "--root", str(root), *args[1:]] if args[0] in ("context", "doctor") else args
    out, err = io.StringIO(), io.StringIO()
    code = 0
    cwd = os.getcwd()
    try:
        if root is not None:
            os.chdir(root)
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = engine.main(args) or 0
            except SystemExit as exc:  # argparse errors
                code = exc.code if isinstance(exc.code, int) else 1
            except Exception as exc:  # ForgeError etc. -> mimic cli.run
                from forgelib.fsutil import ForgePathError
                from forgelib.project import ForgeError
                from forgelib.yamlio import YAMLError

                if isinstance(exc, (ForgeError, YAMLError, ForgePathError)):
                    from forgelib.brand import brand

                    print(f"{brand()['skill_command']}: error: {exc}", file=sys.stderr)
                    code = 2
                else:
                    raise
    finally:
        os.chdir(cwd)
    return CLIResult(code, out.getvalue(), err.getvalue())


class ProjectCase(unittest.TestCase):
    """A test case with a fresh temp directory as project root."""

    profile = ("surfaces=[web]", "backend=false")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="skill-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def forge(self, *argv, ok=True) -> CLIResult:
        res = run(*argv, root=self.tmp)
        if ok and res.code != 0:
            self.fail(f"forge {' '.join(argv)} failed ({res.code}):\n{res.out}\n{res.err}")
        return res

    def init(self, name="Test Product", *profile):
        return self.forge("init", "--name", name, "--product-type", "test", "--profile", *(profile or self.profile))

    def project(self):
        from forgelib.project import Project

        return Project(self.tmp)
