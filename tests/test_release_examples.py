"""Examples, rendering safety, repo inspection, eval suite structure, release checks."""

import json
import shutil
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from tests.helpers import REPO, SKILL

sys.path.insert(0, str(REPO / "evals"))
from forgelib import mdhtml
from forgelib.checks import blueprint_gaps, validate
from forgelib.project import Project, parse_frontmatter

import check_release  # noqa: E402
import inspect_repo  # noqa: E402
import render_blueprint  # noqa: E402

EXAMPLES = ["calculator", "b2b-ai-saas"]
VOID = {"meta", "link", "br", "img", "input", "hr", "path", "rect", "source"}


class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.external = [], [], []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("src", "href") and v and v.startswith(("http://", "https://", "//")) and tag in ("script", "link", "img"):
                self.external.append(v)
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


class Examples(unittest.TestCase):
    def test_examples_valid_and_blueprint_complete(self):
        for ex in EXAMPLES:
            with self.subTest(ex=ex):
                proj = Project(REPO / "examples" / ex)
                res = validate(proj)
                self.assertEqual(res["errors"], [])
                self.assertEqual(res["warnings"], [])
                self.assertEqual(blueprint_gaps(proj), [])
                self.assertEqual(proj.state()["project"]["stage"], "BLUEPRINT_COMPLETE")

    def test_examples_meaningfully_different(self):
        calc, b2b = (Project(REPO / "examples" / e) for e in EXAMPLES)
        na = lambda p: sum(1 for c in p.gate()["checks"] if c["group"] == "production" and c["status"] == "NOT_APPLICABLE")  # noqa: E731
        self.assertGreater(na(calc), 25)
        self.assertLess(na(b2b), 5)
        self.assertGreater(len(b2b.registry("build-graph.yaml")), len(calc.registry("build-graph.yaml")))

    def test_deterministic_eval_grader(self):
        import grade

        spec = json.loads((REPO / "evals/evals.json").read_text())
        for s in spec["evals"]:
            if s.get("example"):
                with self.subTest(s=s["id"]):
                    results = grade.grade(s, REPO / s["example"], None)
                    failed = [r for r in results if r["result"] == "FAIL"]
                    self.assertEqual(failed, [])

    def test_rendered_blueprints_are_wellformed_and_self_contained(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for ex in EXAMPLES:
                with self.subTest(ex=ex):
                    page = render_blueprint.build(Project(REPO / "examples" / ex))
                    parser = TagBalance()
                    parser.feed(page)
                    self.assertEqual(parser.errors, [])
                    self.assertEqual(parser.external, [])
                    for section in ("overview", "product", "build", "features", "design", "architecture", "decisions", "risks", "readiness", "launch"):
                        self.assertIn(f'id="{section}"', page)
                    self.assertIn("prefers-color-scheme: dark", page)
                    self.assertIn('name="viewport"', page)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class RenderingSafety(unittest.TestCase):
    def test_markdown_is_escaped(self):
        html = mdhtml.render('<script>alert(1)</script>\n\n[x](javascript:alert(1)) [ok](https://example.com) **b** `c<d>`')
        self.assertNotIn("<script>", html)
        self.assertNotIn("javascript:", html)
        self.assertIn('href="https://example.com"', html)
        self.assertIn("<strong>b</strong>", html)
        self.assertIn("<code>c&lt;d&gt;</code>", html)

    def test_tables_lists_tasks(self):
        html = mdhtml.render("| a | b |\n|---|---|\n| 1 | 2 |\n\n- [x] done\n- [~] na\n\n1. one")
        self.assertIn("<table>", html)
        self.assertIn("task-done", html)
        self.assertIn("task-na", html)
        self.assertIn("<ol>", html)


class InspectRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_empty_is_greenfield(self):
        self.assertEqual(inspect_repo.inspect(self.tmp)["suggested_mode"], "GREENFIELD")
        (self.tmp / "README.md").write_text("# idea")
        self.assertEqual(inspect_repo.inspect(self.tmp)["suggested_mode"], "GREENFIELD")

    def test_node_stack_detection(self):
        (self.tmp / "package.json").write_text(json.dumps({"dependencies": {"next": "1", "@prisma/client": "1", "stripe": "1"},
                                                           "devDependencies": {"vitest": "1"}}))
        (self.tmp / "pnpm-lock.yaml").write_text("")
        (self.tmp / "src").mkdir()
        (self.tmp / "src/app.ts").write_text("export {}")
        (self.tmp / ".github/workflows").mkdir(parents=True)
        (self.tmp / ".github/workflows/ci.yml").write_text("on: push")
        (self.tmp / "node_modules/x").mkdir(parents=True)
        (self.tmp / "node_modules/x/index.js").write_text("")
        r = inspect_repo.inspect(self.tmp)
        self.assertIn("Next.js", r["frameworks"])
        self.assertIn("Prisma", r["data"])
        self.assertIn("Stripe", r["services"])
        self.assertIn("Vitest", r["tests"])
        self.assertIn("pnpm", r["package_managers"])
        self.assertEqual(r["ci"], [".github/workflows/ci.yml"])
        self.assertEqual(r["suggested_mode"], "REVIEW")
        self.assertEqual(r["code_files"], 1)  # node_modules skipped

    def test_python_and_firebase_signals(self):
        (self.tmp / "requirements.txt").write_text("fastapi==0.1\nsqlalchemy\npsycopg2-binary\n")
        (self.tmp / "main.py").write_text("print(1)")
        (self.tmp / "firebase.json").write_text("{}")
        r = inspect_repo.inspect(self.tmp)
        self.assertIn("FastAPI", r["frameworks"])
        self.assertIn("PostgreSQL", r["data"])
        self.assertTrue(any("migrations" in s for s in r["signals"]))
        self.assertTrue(any("Firebase" in s for s in r["signals"]))


class EvalSuite(unittest.TestCase):
    PROMPT_KEYS = {"schema_version", "name", "description", "tags", "plugins", "runs", "expected_outcome", "model", "max_turns",
                   "timeout_seconds", "allowed_tools", "append_system_prompt", "env"}
    GRADER_TYPES = {"regex", "tool_used", "tool_order", "file_exists", "llm", "baseline"}

    def test_cases_structure(self):
        spec = json.loads((REPO / "evals/evals.json").read_text())
        self.assertGreaterEqual(len(spec["evals"]), 10)
        for s in spec["evals"]:
            with self.subTest(case=s["id"]):
                d = REPO / "evals" / s["case"]
                fm, body = parse_frontmatter((d / "prompt.md").read_text())
                self.assertFalse(set(fm) - self.PROMPT_KEYS)
                self.assertTrue(body.strip())
                graders = list((d / "graders").glob("*.md"))
                self.assertTrue(graders)
                self.assertTrue(any("tool: Skill" in g.read_text() for g in graders))
                for g in graders:
                    gfm, _ = parse_frontmatter(g.read_text())
                    self.assertIn(gfm.get("type"), self.GRADER_TYPES, g.name)
                if (d / "case.yaml").exists():
                    self.assertTrue((d / "scaffold.sh").exists())


class ReleaseChecks(unittest.TestCase):
    def test_release_checks_pass(self):
        res = check_release.run()
        self.assertEqual(res["errors"], [])

    def test_skill_frontmatter(self):
        fm, body = parse_frontmatter((SKILL / "SKILL.md").read_text())
        self.assertEqual(fm["name"], SKILL.name)
        self.assertNotIn("version", fm)  # not a documented skill field; lives in metadata
        self.assertIn("${CLAUDE_SKILL_DIR}/scripts/engine.py", body)
        self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", body)  # self-contained skill


if __name__ == "__main__":
    unittest.main()
