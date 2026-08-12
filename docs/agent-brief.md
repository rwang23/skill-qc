# Agent brief

## Project snapshot

- Last reviewed: 2026-08-12
- Project root: `<PROJECT_ROOT>`
- Project: `skill-qc`
- Purpose: read-only evaluation of one Agent Skill or every discoverable Skill in a repository, with explainable JSON, bilingual HTML output, and a prioritized per-Skill optimization queue.
- Stack: Python standard library, HTML/CSS/JavaScript, and `unittest`.
- Canonical package manager: none; Python standard library only.
- Production/live-data sensitivity: no live-data access; input packages and generated reports may contain private paths or security-sensitive text and must be redacted before sharing.
- Public source: `https://github.com/rwang23/skill-qc`.
- Sensitivity: audit inputs may contain private paths, unsafe commands, or credential-shaped strings; never reproduce matched secret values or treat an audit as execution authority.

## Current contract

- Scoring authority: [`references/rubric.md`](../references/rubric.md).
- Workflow: [`SKILL.md`](../SKILL.md).
- Report contract: [`references/report-contract.md`](../references/report-contract.md).
- Single-Skill renderers: [`assets/report-template.en.html`](../assets/report-template.en.html) and [`assets/report-template.zh-CN.html`](../assets/report-template.zh-CN.html).
- Repository renderers: [`assets/repository-template.en.html`](../assets/repository-template.en.html) and [`assets/repository-template.zh-CN.html`](../assets/repository-template.zh-CN.html).
- The audited Skill stays read-only unless a separate request authorizes changes.
- Score, gate, evidence, maturity, and action permission remain separate. Repository averages never replace per-Skill gates or evidence grades.
- Product scope is Skill-package engineering quality. Business expertise, domain depth, strategy, commercial value, and real-world outcomes are outside the rubric.

## Read first

1. [`README.md`](../README.md)
2. [`references/rubric.md`](../references/rubric.md)
3. [`references/review-protocol.md`](../references/review-protocol.md)
4. The narrow schema or template needed for the task

## Verification Bundles

```powershell
python -m unittest discover -s tests -v
python scripts/skill_audit.py audit . --profile portable --maturity governed --locale en --json-out .audit-work/self.json --html-out .audit-work/self.html
```

The audit command exits `1` for `REVIEW` or `2` for `BLOCKED`; inspect the saved report rather than treating every nonzero result as a runtime crash.

## Live Operation Gates

- SkillQC itself is read-only and does not execute target code.
- Installation, external publication, registry mutation, or any action suggested by a target Skill requires separate authorization and same-target verification.
- A clean audit is quality evidence, not permission to run a target Skill or change live state.

## Tooling map

- Auditor and renderer: `scripts/skill_audit.py`
- Report templates: `assets/report-template.*.html`
- Repository templates: `assets/repository-template.*.html`
- Behavior tests: `tests/test_skill_audit.py`
- Rendering tests: `tests/test_report_rendering.py`
- Route fixtures: `evals/evals.json`
- Runtime mirror sync: `tools/Sync-ActiveSkill.ps1`
- Public self-audit and anonymized repository examples: `examples/`

## Change boundaries

- Change a detector only with a focused failing fixture and passing regression test.
- Increment `RUBRIC_VERSION` for a weight, threshold, severity, cap, or evidence-rule change.
- Keep all four HTML reports self-contained, responsive, printable, and semantically equivalent within each mode.
- Keep single-Skill and repository modes behaviorally separate while using the same scoring authority.
- Keep public history free of private audit targets, absolute user paths, credentials, and local system inventory.
- Keep opt-in anonymization mappings in ignored local work areas; never sync or publish them.
- Installing, publishing, pushing, or acting on live state requires its own authority and same-target readback.
