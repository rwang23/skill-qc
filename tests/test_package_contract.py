from __future__ import annotations

import json
import unittest
from pathlib import Path


class PackageContractTests(unittest.TestCase):
    def test_each_routing_fixture_has_human_review_expectations(self) -> None:
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "evals" / "evals.json").read_text(encoding="utf-8"))

        for case in data["evals"]:
            with self.subTest(case=case.get("id")):
                expectations = case.get("expectations")
                self.assertIsInstance(expectations, list)
                self.assertTrue(expectations)
                self.assertTrue(all(isinstance(item, str) and item.strip() for item in expectations))

    def test_each_routing_fixture_declares_lexical_evaluation_bounds(self) -> None:
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "evals" / "evals.json").read_text(encoding="utf-8"))

        for case in data["evals"]:
            with self.subTest(case=case.get("id")):
                routing = case.get("routing")
                self.assertIsInstance(routing, dict)
                lexical = routing.get("lexical")
                self.assertIsInstance(lexical, dict)
                self.assertGreaterEqual(lexical.get("required_top_k", 1), 1)
                self.assertGreaterEqual(lexical.get("forbidden_top_k", 1), 1)


if __name__ == "__main__":
    unittest.main()
