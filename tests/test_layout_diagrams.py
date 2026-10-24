"""Docs layout for new projects, not-a-project detection, and DIAGRAMS.md checks."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from tests.helpers import REPO, ProjectCase, run
from forgelib import diagrams

COMPLETE_DIAGRAMS = """# Product Diagrams — Test

## 1. System architecture
Client only (ADR-001).

```mermaid
flowchart LR
  user([User]) --> ui[UI]
  ui --> engine[Engine]
```

## 2. User flow
Main journey.

```mermaid
flowchart TD
  start([Open]) --> type[Type]
  type --> done([Result])
```

## 3. Screen map and navigation
Not applicable: a single screen with no navigation.

## 4. Data model
Client state only.

```mermaid
classDiagram
  class State {
    tokens
  }
```

## 5. Critical path sequence
Press equals.

```mermaid
sequenceDiagram
  actor U as User
  participant E as Engine
  U->>E: evaluate
```
"""


class DocsLayout(ProjectCase):
    layout = "auto"

    def test_new_empty_folder_gets_docs_layout(self):
        res = self.init("Fresh").out
        self.assertIn("docs layout", res)
        self.assertTrue((self.tmp / "docs" / "PROJECT.md").exists())
        self.assertFalse((self.tmp / ".raftly" / "PROJECT.md").exists())
        self.assertTrue((self.tmp / ".raftly" / "state.yaml").exists())
        self.assertEqual(self.project().docs_dir_name(), "docs")

    def test_documents_records_and_outputs_go_to_docs(self):
        self.init("Fresh")
        self.forge("records", "add", "requirement", "--statement", "Evaluate expressions", "--priority", "MUST")
        self.forge("graph", "add", "--name", "Engine", "--type", "foundation")
        self.forge("records", "new", "feature", "--name", "Engine", "--node", "N001", "--requirements", "REQ-001")
        self.forge("records", "new", "prompt", "--title", "Engine", "--node", "N001")
        self.forge("decisions", "new", "--title", "Client only", "--owner", "architect", "--type", "AUTO",
                   "--impact", "low", "--reversibility", "high", "--confidence", "90")
        self.forge("decisions", "book")
        self.forge("blueprint")
        self.forge("deck")
        docs = self.tmp / "docs"
        self.assertTrue(list((docs / "features").glob("F001-*.md")))
        self.assertTrue((docs / "prompts" / "001-engine.md").exists())
        self.assertTrue(list((docs / "decisions").glob("ADR-001-*.md")))
        self.assertTrue((docs / "DECISIONS.md").exists())
        self.assertTrue((docs / "blueprint.html").exists())
        self.assertTrue((docs / "deck.md").exists())
        self.assertFalse((self.tmp / "artifacts").exists())
        self.assertFalse((self.tmp / ".raftly" / "features").exists())
        self.assertTrue((self.tmp / ".raftly" / "requirements.yaml").exists())
        ctx = run("context", "--json", root=self.tmp).json()
        self.assertEqual(ctx["state"]["documents_dir"], "docs")
        self.assertEqual(ctx["state"]["validation_errors"], [])

    def test_folder_with_code_keeps_classic_layout(self):
        (self.tmp / "app.py").write_text("print('hi')\n")
        self.assertIn("classic layout", self.init("Existing").out)
        self.assertTrue((self.tmp / ".raftly" / "PROJECT.md").exists())
        self.assertFalse((self.tmp / "docs").exists())

    def test_existing_docs_folder_is_never_mixed_into(self):
        (self.tmp / "docs").mkdir()
        (self.tmp / "docs" / "notes.md").write_text("# team notes\n")
        self.assertIn("classic layout", self.init("Docs exist").out)
        self.assertEqual(sorted(p.name for p in (self.tmp / "docs").iterdir()), ["notes.md"])

    def test_layout_flag_overrides(self):
        (self.tmp / "app.py").write_text("print('hi')\n")
        self.forge("init", "--name", "Forced", "--layout", "docs")
        self.assertTrue((self.tmp / "docs" / "PROJECT.md").exists())

    def test_init_creates_a_missing_project_folder(self):
        target = self.tmp / "my-product"
        res = run("init", "--root", str(target), "--name", "My Product", root=self.tmp)
        self.assertEqual(res.code, 0, res.err)
        self.assertTrue((target / "docs" / "PROJECT.md").exists())
        self.assertTrue((target / ".raftly" / "state.yaml").exists())

    def test_export_import_carries_docs(self):
        self.init("Zip Me")
        self.forge("blueprint")
        archive = Path(self.forge("export", "--out", str(self.tmp / "out"), "--json").json()["zip"])
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
        self.assertIn("docs/PROJECT.md", names)
        self.assertIn("docs/blueprint.html", names)
        other = Path(tempfile.mkdtemp(prefix="skill-test-docs-"))
        try:
            self.assertEqual(run("import", str(archive), root=other).code, 0)
            self.assertTrue((other / "docs" / "PROJECT.md").exists())
            self.assertEqual(run("context", "--json", root=other).json()["state"]["documents_dir"], "docs")
        finally:
            shutil.rmtree(other, ignore_errors=True)


class NotAProjectFolder(ProjectCase):
    def test_folder_of_projects_is_flagged(self):
        (self.tmp / "a" / ".git").mkdir(parents=True)
        (self.tmp / "b").mkdir()
        (self.tmp / "b" / "package.json").write_text("{}")
        ctx = run("context", "--json", root=self.tmp).json()
        self.assertIn("2 separate projects", ctx["repo"]["not_a_project"])
        self.assertIn("create a new folder", ctx["recommendation"])

    def test_project_folder_is_not_flagged(self):
        (self.tmp / ".git").mkdir()
        (self.tmp / "a" / ".git").mkdir(parents=True)
        (self.tmp / "b" / ".git").mkdir(parents=True)
        ctx = run("context", "--json", root=self.tmp).json()
        self.assertNotIn("not_a_project", ctx["repo"])

    def test_empty_folder_is_not_flagged(self):
        self.assertNotIn("not_a_project", run("context", "--json", root=self.tmp).json()["repo"])


class Diagrams(ProjectCase):
    def test_complete_document_passes(self):
        self.assertEqual(diagrams.problems(COMPLETE_DIAGRAMS), [])
        statuses = {d["key"]: d["status"] for d in diagrams.parse(COMPLETE_DIAGRAMS)}
        self.assertEqual(statuses["screens"], "not-applicable")
        self.assertEqual(statuses["sequence"], "ok")

    def test_missing_wrong_type_and_empty(self):
        text = COMPLETE_DIAGRAMS.replace("sequenceDiagram", "flowchart LR")
        text = text.replace("## 2. User flow\nMain journey.\n", "## 2. User flow\nMain journey, no diagram yet.\n\n")
        text = text.replace("""```mermaid
flowchart TD
  start([Open]) --> type[Type]
  type --> done([Result])
```""", "")
        text = text.replace("## 4. Data model", "## 4. Storage")
        probs = " | ".join(diagrams.problems(text))
        self.assertIn("'Critical path sequence' is a flowchart diagram", probs)
        self.assertIn("'User flow' needs a ```mermaid block", probs)
        self.assertIn("no 'Data model' section", probs)

    def test_everything_not_applicable_is_refused(self):
        text = "\n".join(f"## {i}. {t}\nNot applicable: nothing to draw here at all.\n"
                         for i, t in enumerate(["System architecture", "User flow", "Screen map", "Data model",
                                                "Critical path sequence"], 1))
        self.assertIn("marks every diagram not applicable", " ".join(diagrams.problems(text)))

    def test_template_is_not_accepted_as_finished(self):
        self.init()
        template = (REPO / "skills/raftly/templates/docs/DIAGRAMS.md").read_text()
        self.project().write_text("DIAGRAMS.md", template)
        from forgelib.checks import blueprint_gaps

        gaps = " | ".join(blueprint_gaps(self.project()))
        self.assertIn("DIAGRAMS.md still has template placeholders", gaps)

    def test_blueprint_gate_requires_diagrams(self):
        self.init()
        from forgelib.checks import blueprint_gaps

        self.assertIn("missing document DIAGRAMS.md", blueprint_gaps(self.project()))
        self.project().write_text("DIAGRAMS.md", COMPLETE_DIAGRAMS)
        self.assertNotIn("missing document DIAGRAMS.md", blueprint_gaps(self.project()))
        self.assertFalse([g for g in blueprint_gaps(self.project()) if g.startswith("DIAGRAMS.md")])

    def test_blueprint_html_shows_diagrams(self):
        self.init()
        self.project().write_text("DIAGRAMS.md", COMPLETE_DIAGRAMS)
        self.forge("blueprint")
        html = (self.tmp / "artifacts" / "blueprint.html").read_text()
        self.assertIn('id="diagrams"', html)
        self.assertIn("sequenceDiagram", html)
        self.assertIn("Not applicable:</strong> a single screen", html)

    def test_examples_have_complete_diagrams(self):
        for ex in ("calculator", "b2b-ai-saas"):
            with self.subTest(ex):
                text = (REPO / "examples" / ex / ".raftly" / "DIAGRAMS.md").read_text()
                self.assertEqual(diagrams.problems(text), [])
                self.assertTrue(all(d["status"] == "ok" for d in diagrams.parse(text)))
