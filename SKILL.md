---
name: skill-rigor
description: Audit one Agent Skill read-only and generate an explainable 100-point English or Chinese HTML report. Use when reviewing a single SKILL.md package before install, release, reuse, or revision; not for portfolio scans or general code review.
---

## Workflow

1. Bind exactly one Skill directory, its profile, intended maturity, and the read-only boundary.
2. Read [the rubric](references/rubric.md) before interpreting a score or changing a threshold.
3. Run the deterministic audit and save both JSON and HTML outputs.
4. Review context-sensitive findings with [the review protocol](references/review-protocol.md); change a rule only when a focused regression fixture proves it wrong.
5. Credit E3 or E4 only when [the evidence contract](references/evidence-schema.md) matches the current `SKILL.md` revision.
6. For an authorized improvement cycle, preserve the prior JSON as `--baseline`, rerun after each bounded change, and stop after three rounds unless asked to continue.
7. Report the quality score, safety gate, evidence grade, profile, and maturity separately. A 100-point artifact score is not proof of real-world effectiveness.

## Run an audit

```powershell
python scripts/skill_audit.py audit <SKILL_DIR> `
  --profile portable `
  --maturity library `
  --locale en `
  --json-out audit.json `
  --html-out audit.html
```

Use `--locale zh-CN` for the Chinese report. Add `--baseline previous.json` for an iteration delta or `--evidence evidence.json` for revision-bound E3/E4 evidence. The CLI redacts the target root by default; add repeatable `--redact-root SOURCE=LABEL` mappings for other private paths.

## Decision rules

- Keep the target read-only. Editing, repair, installation, registry changes, publishing, and deployment require separate authorization.
- Require a directory whose root contains one `SKILL.md`; reject portfolio roots and general code-review targets.
- Treat `BLOCKED` as independent of the numeric score.
- Treat heuristic findings as review prompts when negation, examples, local profiles, or security demonstrations may create false positives.
- Do not credit synthetic fixtures or lexical matching above E2.
- Report only a secret pattern class and location, never the matched value.

## Resources

- [Rubric](references/rubric.md): score, gates, evidence, profiles, and maturity.
- [Review protocol](references/review-protocol.md): bounded iteration and adjudication.
- [Evidence contract](references/evidence-schema.md): revision-bound E3/E4 schema.
- [Report contract](references/report-contract.md): single-Skill JSON and bilingual HTML output.
- `scripts/skill_audit.py`: deterministic auditor and renderer.
- `assets/report-template.en.html` and `assets/report-template.zh-CN.html`: self-contained responsive report templates.
