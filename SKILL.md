---
name: skill-qc
description: Audit one Agent Skill or a Skill repository read-only and generate an explainable English or Chinese HTML report. Use when reviewing a Skill before release or reuse, or a Skill library; not for business expertise or general code review.
---

## Workflow

1. Select `single` mode for one Skill directory or `repository` mode for every discoverable Skill below one repository root. Bind the profile, intended maturity, and read-only boundary.
2. Read [the rubric](references/rubric.md) before interpreting a score or changing a threshold.
3. Run the deterministic audit and save both JSON and HTML outputs.
4. Review context-sensitive findings with [the review protocol](references/review-protocol.md); change a rule only when a focused regression fixture proves it wrong.
5. In single mode, credit E3 or E4 only when [the evidence contract](references/evidence-schema.md) matches the current `SKILL.md` revision. Repository mode summarizes the evidence available inside each package.
6. For an authorized improvement cycle, preserve the prior JSON as `--baseline`, rerun after each bounded change, and stop after three rounds unless asked to continue.
7. Report score, safety gate, evidence grade, profile, and maturity separately. For a repository, report the average plus per-Skill results and distributions.
8. State the scope boundary: SkillQC evaluates Skill-package engineering quality, not the business expertise, strategy, or real-world result of the capability.

## Run a single-Skill audit

```powershell
python scripts/skill_audit.py audit <SKILL_DIR> `
  --profile portable `
  --maturity library `
  --locale en `
  --json-out audit.json `
  --html-out audit.html
```

Use `--locale zh-CN` for the Chinese report. Add `--baseline previous.json` for an iteration delta or `--evidence evidence.json` for revision-bound E3/E4 evidence. The CLI redacts the target root by default; add repeatable `--redact-root SOURCE=LABEL` mappings for other private paths.

## Run a repository audit

```powershell
python scripts/skill_audit.py audit-repository <REPOSITORY_DIR> `
  --profile portable `
  --maturity library `
  --locale en `
  --json-out repository-audit.json `
  --html-out repository-audit.html
```

Add `--anonymize` before sharing a report. It replaces Skill names and package paths with stable report-local labels. Repository mode ignores common generated, vendor, fixture, test, and worktree directories.

## Decision rules

- Keep the target read-only. Editing, repair, installation, registry changes, publishing, and deployment require separate authorization.
- In single mode, require a directory whose root contains one `SKILL.md`. In repository mode, require at least one discoverable `SKILL.md` below the target.
- Treat `BLOCKED` as independent of the numeric score.
- Treat the repository score as an unweighted average of individual Skill scores. Never use it to hide the gate or evidence distribution.
- Treat heuristic findings as review prompts when negation, examples, local profiles, or security demonstrations may create false positives.
- Do not credit synthetic fixtures or lexical matching above E2.
- Report only a secret pattern class and location, never the matched value.
- Do not score domain knowledge, business strategy, commercial value, or task outcomes unless a separate domain evaluation is explicitly requested.

## Resources

- [Rubric](references/rubric.md): score, gates, evidence, profiles, and maturity.
- [Review protocol](references/review-protocol.md): bounded iteration and adjudication.
- [Evidence contract](references/evidence-schema.md): revision-bound E3/E4 schema.
- [Report contract](references/report-contract.md): single-Skill and repository JSON plus bilingual HTML output.
- `scripts/skill_audit.py`: deterministic auditor and renderer.
- `assets/report-template.*.html` and `assets/repository-template.*.html`: self-contained responsive report templates.
