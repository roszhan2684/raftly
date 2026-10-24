import unittest

from tests.helpers import SKILL  # noqa: F401  (also sets sys.path)
from forgelib import yamlio
from forgelib.yamlio import YAMLError


class YamlRoundTrip(unittest.TestCase):
    def test_roundtrip_complex(self):
        data = {
            "engine": {"version": "0.1.0", "schema_version": 1},
            "name": "Calc: the app",
            "empty_list": [],
            "empty_map": {},
            "flags": [True, False, None],
            "numbers": [0, -3, 2.5, "007", "1.0"],
            "strings": ["yes", "no", "null", "", " lead", "trail ", "a # b", "key: value", "-dash", "@at", "it's", 'say "hi"'],
            "multi": "line one\nline two\n",
            "multi_strip": "a\n\nb",
            "nested": [{"id": "N001", "depends_on": [], "dod": ["a", "b"], "meta": {"x": 1}}, {"id": "N002", "depends_on": ["N001"]}],
            "list_of_lists": [[1, 2], ["a"]],
            "unicode": "naïve — ✓",
            "date": "2026-01-15",
            "ts": "2026-01-15T10:00:00Z",
        }
        text = yamlio.dumps(data, header="hello\nworld")
        self.assertTrue(text.startswith("# hello\n# world\n"))
        self.assertEqual(yamlio.loads(text), data)

    def test_parse_human_yaml(self):
        text = """
---
# comment
title: "Quoted # not comment"  # trailing comment
plain: hello world
single: 'it''s'
flow: [a, "b, c", {k: v, n: [1, 2]}]
flowmap: {a: 1, b: null}
seq_same_indent:
- one
- two: 2
  three: 3
block: |
  first
    indented
  last
folded: >-
  joined
  words

  new para
n: 12
f: 1.5e3
t: True
dashed-key: x
url: https://example.com/a?b=c
time: 12:30
multi_flow: [
  a,
  b
]
"""
        d = yamlio.loads(text)
        self.assertEqual(d["title"], "Quoted # not comment")
        self.assertEqual(d["plain"], "hello world")
        self.assertEqual(d["single"], "it's")
        self.assertEqual(d["flow"], ["a", "b, c", {"k": "v", "n": [1, 2]}])
        self.assertEqual(d["flowmap"], {"a": 1, "b": None})
        self.assertEqual(d["seq_same_indent"], ["one", {"two": 2, "three": 3}])
        self.assertEqual(d["block"], "first\n  indented\nlast\n")
        self.assertEqual(d["folded"], "joined words\nnew para")
        self.assertEqual(d["n"], 12)
        self.assertEqual(d["f"], 1500.0)
        self.assertIs(d["t"], True)
        self.assertEqual(d["url"], "https://example.com/a?b=c")
        self.assertEqual(d["time"], "12:30")
        self.assertEqual(d["multi_flow"], ["a", "b"])

    def test_dates_stay_strings(self):
        self.assertEqual(yamlio.loads("d: 2026-01-15"), {"d": "2026-01-15"})

    def test_errors(self):
        for bad in ("a: &x 1", "a:\n\t- b", "a: 1\na: 2", "a: 1\n---\nb: 2", "a: [1, 2", 'a: "unterminated', "- - x"):
            with self.subTest(bad=bad):
                with self.assertRaises(YAMLError):
                    yamlio.loads(bad)

    def test_empty(self):
        self.assertIsNone(yamlio.loads(""))
        self.assertEqual(yamlio.loads("[]"), [])
        self.assertEqual(yamlio.dumps({}), "{}\n")

    def test_core_catalogs_parse(self):
        for name in ("production-gate.yaml", "forgotten-20.yaml", "roles.yaml"):
            data = yamlio.load_file(SKILL / "core" / name)
            self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
