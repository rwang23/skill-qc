from __future__ import annotations

import json
import unittest
from pathlib import Path


class PackageContractTests(unittest.TestCase):
    def test_public_skill_identity_and_agent_prompt_are_consistent(self) -> None:
        root = Path(__file__).resolve().parents[1]
        skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
        agent_text = (root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        eval_data = json.loads((root / "evals" / "evals.json").read_text(encoding="utf-8"))

        self.assertEqual(root.name, "skill-qc")
        self.assertIn("name: skill-qc", skill_text)
        self.assertIn('display_name: "SkillQC"', agent_text)
        self.assertIn("$skill-qc", agent_text)
        self.assertEqual(eval_data["skill_name"], "skill-qc")

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
