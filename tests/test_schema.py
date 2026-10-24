import json
import unittest

from tests.helpers import SKILL
from forgelib import model
from forgelib.schema import load_schema, schema_files, validate


class SchemaValidator(unittest.TestCase):
    def test_keywords(self):
        s = {"type": "object", "required": ["a"], "additionalProperties": False,
             "properties": {"a": {"type": "integer", "minimum": 1}, "b": {"enum": ["x"]},
                            "c": {"type": "array", "items": {"type": "string", "pattern": "^N"}, "uniqueItems": True},
                            "d": {"$ref": "#/$defs/d"}, "e": {"type": "string", "format": "date"}},
             "$defs": {"d": {"type": ["string", "null"]}}}
        self.assertEqual(validate({"a": 1, "c": ["N1"], "d": None, "e": "2026-01-01"}, s), [])
        errs = validate({"a": 0, "b": "y", "c": ["Q", "Q"], "d": 3, "e": "01/01/2026", "z": 1}, s)
        joined = "\n".join(errs)
        for frag in ("minimum", "not one of", "does not match", "duplicate", "expected string or null", "YYYY-MM-DD", "unexpected field 'z'"):
            self.assertIn(frag, joined)
        self.assertIn("missing required field 'a'", "\n".join(validate({}, s)))

    def test_combinators(self):
        s = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        self.assertEqual(validate(3, s), [])
        self.assertTrue(validate(3.5, s))
        one = {"oneOf": [{"type": "number"}, {"type": "integer"}]}
        self.assertTrue(validate(3, one))  # matches both

    def test_all_schema_files_are_valid_json_with_ids(self):
        files = schema_files()
        self.assertGreaterEqual(len(files), 14)
        for f in files:
            data = json.loads(f.read_text())
            self.assertIn("$schema", data)
            self.assertIn("title", data)

    def test_model_schema_enum_sync(self):
        st = load_schema("state")
        self.assertEqual(st["properties"]["project"]["properties"]["mode"]["enum"], model.MODES)
        self.assertEqual(st["properties"]["project"]["properties"]["stage"]["enum"], model.STAGES)
        bg = load_schema("build-graph")
        self.assertEqual(bg["properties"]["nodes"]["items"]["properties"]["status"]["enum"], model.WORK_STATUSES)
        gate = load_schema("gate")
        self.assertEqual(gate["properties"]["checks"]["items"]["properties"]["status"]["enum"], model.GATE_STATUSES)
        ev = load_schema("evidence")
        self.assertEqual(ev["properties"]["links"]["items"]["properties"]["relation"]["enum"], model.LINK_RELATIONS)
        self.assertEqual(ev["properties"]["records"]["items"]["properties"]["kind"]["enum"], model.EVIDENCE_KINDS)
        risks = load_schema("risks")
        self.assertEqual(risks["properties"]["risks"]["items"]["properties"]["category"]["enum"], model.RISK_CATEGORIES)
        dec = load_schema("decision")
        self.assertEqual(dec["properties"]["decision_type"]["enum"], model.DECISION_TYPES)
        self.assertEqual(load_schema("learning")["properties"]["outcome"]["enum"], model.LEARNING_OUTCOMES)

    def test_gate_catalog_matches_schema(self):
        from forgelib import yamlio

        for name in ("production-gate.yaml", "forgotten-20.yaml"):
            for c in yamlio.load_file(SKILL / "core" / name)["checks"]:
                self.assertRegex(c["id"], r"^G-[A-Z0-9-]+$")
                self.assertIn(c["severity"], model.GATE_SEVERITIES)


if __name__ == "__main__":
    unittest.main()
