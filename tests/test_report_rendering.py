from __future__ import annotations

import tempfile
import unittest
import subprocess
import sys
import json
from pathlib import Path

from scripts.skill_audit import audit_repository, audit_target, render_report


class ReportRenderingTests(unittest.TestCase):
    def test_english_repository_report_is_a_responsive_webpage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for name, description in (
                (
                    "alpha-skill",
                    "Inspect supplied evidence. Use when a user requests a bounded evidence review.",
                ),
                ("beta-skill", "Summarize supplied notes."),
            ):
                skill_dir = root / name
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(
                    f"""---
name: {name}
description: {description}
---

1. Inspect the supplied input.
2. Report the result and limits.
""",
                    encoding="utf-8",
                )
            report = audit_repository(root, profile="portable", maturity="scaffold")
            output = root / "repository-report.html"

            render_report(report, output, locale="en")

            rendered = output.read_text(encoding="utf-8")
            self.assertIn('<html lang="en">', rendered)
            self.assertIn('class="repository-page"', rendered)
            self.assertIn("Repository Quality Report", rendered)
            self.assertIn("Average Skill Score", rendered)
            self.assertIn("What to fix first", rendered)
            self.assertIn("Recommended actions", rendered)
            self.assertIn("beta-skill", rendered)
            self.assertIn("SkillQC", rendered)
            self.assertNotIn('class="deck-stage"', rendered)
            self.assertNotIn("__AUDIT_DATA__", rendered)

    def test_english_report_is_a_responsive_single_skill_webpage(self) -> None:
        leaked_value = "sk-proj-" + "1234567890abcdefghijklmnopqrstuvwxyz"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "unsafe-reporter"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"""---
name: unsafe-reporter
description: Review generated reports. Use when a user asks for a local report audit.
---

```bash
export API_KEY={leaked_value}
```
""",
                encoding="utf-8",
            )
            report = audit_target(skill_dir, profile="portable", maturity="production")
            output = root / "report.html"

            render_report(report, output, locale="en")

            html = output.read_text(encoding="utf-8")
            self.assertIn('<html lang="en">', html)
            self.assertIn('class="audit-page"', html)
            self.assertIn("Skill Quality Report", html)
            self.assertIn("Why this score", html)
            self.assertIn("How to improve", html)
            self.assertIn('role="progressbar"', html)
            self.assertIn(str(report["summary"]["quality_score"]), html)
            self.assertNotIn("width: 1920px", html)
            self.assertNotIn('class="deck-stage"', html)
            self.assertNotIn("__AUDIT_DATA__", html)
            self.assertNotIn("__GENERATED_AT__", html)
            self.assertNotIn(leaked_value, html)

    def test_cli_writes_json_and_html_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "route-request"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                """---
name: route-request
description: Route a request to the narrowest matching workflow. Use when comparing several candidate Agent Skills.
---

1. Read candidate descriptions.
2. Select the narrowest matching trigger and explain exclusions.
""",
                encoding="utf-8",
            )
            json_output = root / "audit.json"
            html_output = root / "audit.html"
            script = Path(__file__).resolve().parents[1] / "scripts" / "skill_audit.py"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "audit",
                    str(skill_dir),
                    "--profile",
                    "portable",
                    "--maturity",
                    "scaffold",
                    "--json-out",
                    str(json_output),
                    "--html-out",
                    str(html_output),
                    "--locale",
                    "zh-CN",
                    "--observed-at",
                    "2026-08-11T20:00:00Z",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(json_output.is_file())
            self.assertTrue(html_output.is_file())
            self.assertIn("gate=PASS", completed.stdout)
            saved_json = json_output.read_text(encoding="utf-8")
            saved_html = html_output.read_text(encoding="utf-8")
            self.assertIn("<SKILL:route-request>", saved_json)
            self.assertIn('"generated_at": "2026-08-11T20:00:00Z"', saved_json)
            self.assertIn("2026-08-11T20:00:00Z", saved_html)
            self.assertNotIn(str(skill_dir), saved_json)
            self.assertNotIn(str(skill_dir), saved_html)
            self.assertIn(
                '<html lang="zh-CN">', saved_html
            )

    def test_cli_writes_anonymized_repository_json_and_html_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repository = root / "private-skill-library"
            for name in ("private-orders", "internal-routing"):
                skill_dir = repository / name
                skill_dir.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text(
                    f"""---
name: {name}
description: Inspect supplied evidence. Use when a user requests a bounded evidence review.
---

1. Inspect the supplied input.
2. Report the result and limits.
""",
                    encoding="utf-8",
                )
            json_output = root / "repository.json"
            html_output = root / "repository.html"
            script = Path(__file__).resolve().parents[1] / "scripts" / "skill_audit.py"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "audit-repository",
                    str(repository),
                    "--profile",
                    "portable",
                    "--maturity",
                    "scaffold",
                    "--anonymize",
                    "--json-out",
                    str(json_output),
                    "--html-out",
                    str(html_output),
                    "--locale",
                    "en",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            saved = json.loads(json_output.read_text(encoding="utf-8"))
            rendered = html_output.read_text(encoding="utf-8")
            self.assertEqual(saved["mode"], "repository")
            self.assertEqual([skill["name"] for skill in saved["skills"]], ["Skill 001", "Skill 002"])
            self.assertIn("average=100.0", completed.stdout)
            self.assertIn("Repository Quality Report", rendered)
            self.assertNotIn("private-orders", rendered)
            self.assertNotIn("internal-routing", rendered)
            self.assertNotIn(str(repository), rendered)

    def test_cli_can_write_a_separate_private_anonymization_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repository = root / "private-skill-library"
            for name in ("private-orders", "internal-routing"):
                skill_dir = repository / name
                skill_dir.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text(
                    f"""---
name: {name}
description: Inspect supplied evidence. Use when a user requests a bounded evidence review.
---

1. Inspect the supplied input.
2. Report the result and limits.
""",
                    encoding="utf-8",
                )
            json_output = root / "repository.json"
            html_output = root / "repository.html"
            mapping_output = root / "repository.private-map.json"
            script = Path(__file__).resolve().parents[1] / "scripts" / "skill_audit.py"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "audit-repository",
                    str(repository),
                    "--profile",
                    "portable",
                    "--maturity",
                    "scaffold",
                    "--anonymize",
                    "--mapping-out",
                    str(mapping_output),
                    "--json-out",
                    str(json_output),
                    "--html-out",
                    str(html_output),
                    "--locale",
                    "en",
                    "--observed-at",
                    "2026-08-12T12:00:00Z",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            mapping = json.loads(mapping_output.read_text(encoding="utf-8"))
            public_json = json_output.read_text(encoding="utf-8")
            public_html = html_output.read_text(encoding="utf-8")
            self.assertEqual(mapping["generated_at"], "2026-08-12T12:00:00Z")
            self.assertEqual(mapping["target"], str(repository.resolve()))
            self.assertEqual(
                [entry["anonymous_name"] for entry in mapping["entries"]],
                ["Skill 001", "Skill 002"],
            )
            self.assertEqual(
                [entry["skill_name"] for entry in mapping["entries"]],
                ["internal-routing", "private-orders"],
            )
            self.assertTrue(all(Path(entry["path"]).is_absolute() for entry in mapping["entries"]))
            self.assertIn(f"mapping={mapping_output.resolve()}", completed.stdout)
            for private_name in ("private-orders", "internal-routing"):
                self.assertNotIn(private_name, public_json)
                self.assertNotIn(private_name, public_html)

    def test_chinese_report_uses_the_chinese_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "route-request"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                """---
name: route-request
description: 评估单个 Agent Skill 的质量并解释评分。适用于发布前审计或迭代复核。
---

1. 检查当前 Skill 包和评分证据。
2. 输出总分、分维度理由和改进建议。
""",
                encoding="utf-8",
            )
            report = audit_target(skill_dir, profile="portable", maturity="scaffold")
            output = root / "audit.zh-CN.html"

            render_report(report, output, locale="zh-CN")

            rendered = output.read_text(encoding="utf-8")
            self.assertIn('<html lang="zh-CN">', rendered)
            self.assertIn("Agent Skill 质量审计报告", rendered)
            self.assertIn("评分理由", rendered)
            self.assertIn("如何改进", rendered)

    def test_chinese_repository_report_uses_the_chinese_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "route-request"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                """---
name: route-request
description: 检查 Agent Skill。
---

1. 检查 Skill 包。
2. 输出评分和边界。
""",
                encoding="utf-8",
            )
            report = audit_repository(root, profile="portable", maturity="scaffold")
            output = root / "repository.zh-CN.html"

            render_report(report, output, locale="zh-CN")

            rendered = output.read_text(encoding="utf-8")
            self.assertIn('<html lang="zh-CN">', rendered)
            self.assertIn("Skill 仓库质量报告", rendered)
            self.assertIn("Skill 平均分", rendered)
            self.assertIn("先处理哪些 Skill", rendered)
            self.assertIn("建议动作", rendered)
            self.assertIn("评判 Skill，不评判业务深度", rendered)


if __name__ == "__main__":
    unittest.main()
