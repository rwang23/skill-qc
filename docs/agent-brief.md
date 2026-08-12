# Agent brief

## Project snapshot

- Last reviewed: 2026-08-11
- Project: `skill-rigor`
- Purpose: read-only evaluation of exactly one Agent Skill package with explainable JSON and bilingual HTML output.
- Stack: Python standard library, HTML/CSS/JavaScript, and `unittest`.
- Package manager: none.
- Public source: `https://github.com/rwang23/skill-rigor`.
- Sensitivity: audit inputs may contain private paths, unsafe commands, or credential-shaped strings; never reproduce matched secret values or treat an audit as execution authority.

## Current contract

- Scoring authority: [`references/rubric.md`](../references/rubric.md).
- Workflow: [`SKILL.md`](../SKILL.md).
- Report contract: [`references/report-contract.md`](../references/report-contract.md).
- Renderers: [`assets/report-template.en.html`](../assets/report-template.en.html) and [`assets/report-template.zh-CN.html`](../assets/report-template.zh-CN.html).
- The audited Skill stays read-only unless a separate request authorizes changes.
- Score, gate, evidence, maturity, and action permission remain separate.

## Read first

1. [`README.md`](../README.md)
2. [`references/rubric.md`](../references/rubric.md)
3. [`references/review-protocol.md`](../references/review-protocol.md)
4. The narrow schema or template needed for the task

## Verification

```powershell
python -m unittest discover -s tests -v
python scripts/skill_audit.py audit . --profile portable --maturity governed --locale en --json-out .audit-work/self.json --html-out .audit-work/self.html
```

The audit command exits `1` for `REVIEW` or `2` for `BLOCKED`; inspect the saved report rather than treating every nonzero result as a runtime crash.

## Tooling map

- Auditor and renderer: `scripts/skill_audit.py`
- Report templates: `assets/report-template.*.html`
- Behavior tests: `tests/test_skill_audit.py`
- Rendering tests: `tests/test_report_rendering.py`
- Route fixtures: `evals/evals.json`
- Runtime mirror sync: `tools/Sync-ActiveSkill.ps1`
- Public self-audit examples: `examples/self-audit.*`

## Change boundaries

- Change a detector only with a focused failing fixture and passing regression test.
- Increment `RUBRIC_VERSION` for a weight, threshold, severity, cap, or evidence-rule change.
- Keep both HTML reports self-contained, responsive, printable, and semantically equivalent.
- Keep public history free of private audit targets, absolute user paths, credentials, and local system inventory.
- Installing, publishing, pushing, or acting on live state requires its own authority and same-target readback.
