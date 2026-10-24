"""Export/import of a project as a zip, for hosts without a lasting repository."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from tests.helpers import ProjectCase, run


class Bundle(ProjectCase):
    def setUp(self):
        super().setUp()
        self.other = Path(tempfile.mkdtemp(prefix="skill-test-import-"))

    def tearDown(self):
        shutil.rmtree(self.other, ignore_errors=True)
        super().tearDown()

    def make_zip(self, entries: dict[str, bytes], name="p.zip", link: str | None = None) -> Path:
        path = self.tmp / name
        with zipfile.ZipFile(path, "w") as zf:
            for arc, data in entries.items():
                zf.writestr(arc, data)
            if link:
                info = zipfile.ZipInfo(link)
                info.external_attr = (0o120777 << 16)
                zf.writestr(info, "/etc/passwd")
        return path

    def import_into_other(self, archive: Path, *extra):
        return run("import", str(archive), *extra, root=self.other)

    def test_round_trip(self):
        self.init("Round Trip")
        self.forge("blueprint")
        res = self.forge("export", "--out", str(self.tmp / "out"), "--json").json()
        archive = Path(res["zip"])
        self.assertEqual(archive.name, "round-trip-raftly.zip")
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
        self.assertIn(".raftly/state.yaml", names)
        self.assertIn("artifacts/blueprint.html", names)
        imp = self.import_into_other(archive)
        self.assertEqual(imp.code, 0, imp.err)
        self.assertEqual((self.tmp / ".raftly/state.yaml").read_text(), (self.other / ".raftly/state.yaml").read_text())
        ctx = run("context", "--json", root=self.other).json()
        self.assertEqual(ctx["state"]["name"], "Round Trip")

    def test_export_requires_project(self):
        self.assertNotEqual(self.forge("export", ok=False).code, 0)

    def test_refuses_existing_project_without_force(self):
        self.init("Existing")
        archive = Path(self.forge("export", "--out", str(self.tmp / "out"), "--json").json()["zip"])
        self.assertEqual(self.import_into_other(archive).code, 0)
        again = self.import_into_other(archive)
        self.assertNotEqual(again.code, 0)
        self.assertIn("--force", again.err)
        self.assertEqual(self.import_into_other(archive, "--force").code, 0)

    def test_accepts_one_wrapping_folder(self):
        archive = self.make_zip({"my-app/.raftly/state.yaml": b"x: 1\n", "my-app/artifacts/deck.md": b"# d\n"})
        self.assertEqual(self.import_into_other(archive).code, 0)
        self.assertTrue((self.other / ".raftly/state.yaml").exists())
        self.assertTrue((self.other / "artifacts/deck.md").exists())

    def test_rejects_unsafe_archives(self):
        cases = {
            "parent": {".raftly/../../evil.txt": b"x"},
            "absolute": {"/tmp/evil.txt": b"x", ".raftly/state.yaml": b"x"},
            "other-file": {".raftly/state.yaml": b"x", "src/app.py": b"print(1)"},
            "no-state": {"artifacts/deck.md": b"x"},
        }
        for label, entries in cases.items():
            with self.subTest(label):
                res = self.import_into_other(self.make_zip(entries, name=f"{label}.zip"))
                self.assertNotEqual(res.code, 0)
                self.assertFalse((self.other / "evil.txt").exists())
        res = self.import_into_other(self.make_zip({".raftly/state.yaml": b"x"}, name="link.zip", link=".raftly/link"))
        self.assertNotEqual(res.code, 0)
        self.assertIn("links", res.err)

    def test_rejects_non_zip(self):
        bad = self.tmp / "not.zip"
        bad.write_text("hello")
        self.assertNotEqual(self.import_into_other(bad).code, 0)
