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

    def test_each_readme_links_only_to_html_examples_in_its_language(self) -> None:
        root = Path(__file__).resolve().parents[1]
        english = (root / "README.md").read_text(encoding="utf-8")
        chinese = (root / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertIn("examples/self-audit.en.html", english)
        self.assertIn("examples/repository-audit.en.html", english)
        self.assertNotIn("examples/self-audit.zh-CN.html", english)
        self.assertNotIn("examples/repository-audit.zh-CN.html", english)

        self.assertIn("examples/self-audit.zh-CN.html", chinese)
        self.assertIn("examples/repository-audit.zh-CN.html", chinese)
        self.assertNotIn("examples/self-audit.en.html", chinese)
        self.assertNotIn("examples/repository-audit.en.html", chinese)


if __name__ == "__main__":
    unittest.main()
