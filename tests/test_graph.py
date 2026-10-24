import unittest

from tests.helpers import REPO  # noqa: F401
from forgelib import graph


def n(i, deps=(), status="PLANNED"):
    return {"id": i, "name": i, "type": "feature", "depends_on": list(deps), "status": status}


class Graph(unittest.TestCase):
    def test_cycle_detection(self):
        nodes = [n("N001", ["N003"]), n("N002", ["N001"]), n("N003", ["N002"])]
        cyc = graph.find_cycle(nodes)
        self.assertIsNotNone(cyc)
        self.assertEqual(cyc[0], cyc[-1])
        self.assertTrue(any("cycle" in p for p in graph.problems(nodes)))
        with self.assertRaises(ValueError):
            graph.phases(nodes)

    def test_problems(self):
        probs = graph.problems([n("N001", ["N001"]), n("N002", ["N009"]), n("N002")])
        text = " ".join(probs)
        self.assertIn("itself", text)
        self.assertIn("unknown node N009", text)
        self.assertIn("duplicate", text)

    def test_phases(self):
        nodes = [n("N001"), n("N002", ["N001"]), n("N003", ["N001"]), n("N004", ["N002", "N003"]), n("N005")]
        self.assertEqual(graph.phases(nodes), [["N001", "N005"], ["N002", "N003"], ["N004"]])

    def test_unblocked_requires_verified_dependencies(self):
        nodes = [n("N001", status="IMPLEMENTED_UNVERIFIED"), n("N002", ["N001"]), n("N003")]
        ids = [x["id"] for x in graph.unblocked(nodes)]
        self.assertEqual(ids, ["N001", "N003"])  # verification first, N002 blocked
        self.assertIn("N002", [x["id"] for x in graph.unblocked(nodes, allow_unverified=True)])
        nodes[0]["status"] = "VERIFIED"
        ids = [x["id"] for x in graph.unblocked(nodes)]
        self.assertEqual(ids, ["N003", "N002", "N001"])  # phase order; close-out (COMPLETE) after new work

    def test_unblocked_order_in_progress_first(self):
        nodes = [n("N001", status="COMPLETE"), n("N002", ["N001"]), n("N003", ["N001"], status="IN_PROGRESS"), n("N004", status="BLOCKED")]
        ids = [x["id"] for x in graph.unblocked(nodes)]
        self.assertEqual(ids, ["N003", "N002"])

    def test_progress_and_tree(self):
        nodes = [n("N001", status="COMPLETE"), n("N002", ["N001"], status="VERIFIED"), n("N003", status="DROPPED")]
        p = graph.progress(nodes)
        self.assertEqual(p["total"], 2)
        self.assertEqual(p["complete_pct"], 50.0)
        self.assertEqual(p["verified_pct"], 100.0)
        tree = graph.ascii_tree(nodes)
        self.assertIn("[x] N001", tree)
        self.assertIn("<- N001", tree)


if __name__ == "__main__":
    unittest.main()
