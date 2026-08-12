# SkillRigor

[简体中文](README.zh-CN.md)

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-0b5b4b)
![Self audit 100/100](https://img.shields.io/badge/self--audit-100%2F100-0b5b4b)
![Gate PASS](https://img.shields.io/badge/gate-PASS-0b5b4b)
![Evidence E2](https://img.shields.io/badge/evidence-E2-d7ad53)
![MIT License](https://img.shields.io/badge/license-MIT-d7684e)

SkillRigor audits one Agent Skill at a time and turns the result into an explainable 100-point score, an independent safety gate, an evidence grade, and a polished English or Chinese HTML webpage.

It is intentionally read-only. It does not repair, install, publish, or execute the Skill being reviewed.

## Why this exists

The paper [*What Keeps Agent Skills from Being Reusable? Evidence from 138K SKILL.md Files*](https://arxiv.org/abs/2608.08453) found that the common failures are ordinary packaging defects: weak routing metadata, non-actionable or bloated bodies, and poor resource organization. Its routing experiment also showed that Skills with clean metadata were retrieved more reliably.

SkillRigor turns those findings, the public Agent Skills specification, and practical release controls into a repeatable single-Skill review. It treats a Skill as a routed software artifact, not a long prompt saved in Markdown.

## What the report answers

- What is the total artifact-quality score?
- Which of the eight dimensions earned or lost points, and why?
- Is the Skill `PASS`, `REVIEW`, or `BLOCKED`?
- What evidence supports the result: E1, E2, E3, or E4?
- What is the smallest concrete improvement for each dimension?
- What changed since the previous audit round?

Open the bundled examples:

- [English self-audit report](examples/self-audit.en.html)
- [中文自审报告](examples/self-audit.zh-CN.html)
- [Machine-readable JSON](examples/self-audit.json)

## The scoring model

| Dimension | Weight | What it measures |
|---|---:|---|
| Routing | 18 | Name, Description, Trigger, and discovery contract |
| Executability | 16 | Actionable workflow, explicit output, and stop conditions |
| Context | 10 | Activated-body focus and progressive disclosure |
| Resources | 9 | Scripts, references, assets, and link integrity |
| Safety | 20 | Secrets, policy bypass, destructive actions, and authority boundaries |
| Portability | 8 | User paths, hardcoded models, and environment assumptions |
| Effectiveness readiness | 12 | Routing and regression artifacts required by the declared maturity |
| Maintainability | 7 | Unfinished instructions, metadata alignment, and lifecycle consistency |

The score, gate, and evidence grade are separate on purpose. `100 / PASS / E2` means the package meets every scored artifact contract and has balanced routing fixtures. It does **not** mean real-world effectiveness has been proved. E3 requires a same-revision target-client trace; E4 adds a real operating trace and accountable review.

See the complete [rubric](references/rubric.md), [evidence contract](references/evidence-schema.md), and [report contract](references/report-contract.md).

## Quick start

SkillRigor uses only the Python standard library. Python 3.11 or newer is recommended.

```bash
git clone https://github.com/rwang23/skill-rigor.git
cd skill-rigor
python scripts/skill_audit.py audit /path/to/one-skill \
  --profile portable \
  --maturity library \
  --locale en \
  --json-out audit.json \
  --html-out audit.html
```

For a Simplified Chinese report:

```bash
python scripts/skill_audit.py audit /path/to/one-skill \
  --profile portable \
  --maturity library \
  --locale zh-CN \
  --json-out audit.zh-CN.json \
  --html-out audit.zh-CN.html
```

The target must be one directory with `SKILL.md` at its root. A portfolio root is rejected so the total and every explanation always refer to one Skill.

### Iterate against a baseline

```bash
python scripts/skill_audit.py audit /path/to/one-skill \
  --profile portable \
  --maturity library \
  --baseline round-1.json \
  --json-out round-2.json \
  --html-out round-2.html
```

The second report records the score delta, resolved findings, and newly introduced findings. Compare deltas only when the rubric version is unchanged.

### Add E3 or E4 evidence

```bash
python scripts/skill_audit.py audit /path/to/one-skill \
  --profile portable \
  --maturity governed \
  --evidence evidence.json \
  --json-out audit.json \
  --html-out audit.html
```

Evidence is credited only when its `target_revision` matches the SHA-256 of the current `SKILL.md`.

### Render an existing JSON report

```bash
python scripts/skill_audit.py render audit.json audit.zh-CN.html --locale zh-CN
```

### Exit codes

| Code | Meaning |
|---:|---|
| 0 | `PASS` |
| 1 | `REVIEW` |
| 2 | `BLOCKED` |
| 3 | Invalid input or execution error |

## Privacy by default

The CLI replaces the absolute target root with `<SKILL:name>` before saving JSON or HTML. Add repeatable mappings for any other private prefix:

```bash
--redact-root "/private/workspace=<WORKSPACE>"
```

Credential-shaped values are never written to the report. Only the pattern class, file, and line are recorded.

## Use it as an Agent Skill

The repository root is a valid Skill package. Place or clone it into the Skill discovery directory used by your agent, keeping the folder name `skill-rigor`. The routing Description is deliberately narrow: it activates for a read-only audit of one Agent Skill, not for general code review, Skill creation, or portfolio scanning.

The active workflow is in [SKILL.md](SKILL.md). Detailed rules stay in `references/`, the deterministic implementation stays in `scripts/`, and the two report templates stay in `assets/` so startup context remains small.

## Development

Run the complete regression suite:

```bash
python -m unittest discover -s tests -v
```

Generate the self-audit:

```bash
python scripts/skill_audit.py audit . \
  --profile portable \
  --maturity governed \
  --locale en \
  --observed-at 2026-08-11T23:21:19-04:00 \
  --json-out examples/self-audit.json \
  --html-out examples/self-audit.en.html

python scripts/skill_audit.py render \
  examples/self-audit.json \
  examples/self-audit.zh-CN.html \
  --locale zh-CN
```

Any detector or scoring change needs a focused failing fixture, a passing regression test, and a rubric-version review. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Limits

- Static rules can produce false positives or false negatives, especially for security examples, negation, persona language, and unusual local contracts.
- E1/E2 results do not prove target-client routing or task success.
- The auditor does not execute scripts from the target package.
- The paper studies public Skills; private enterprise Skills may follow a different distribution.
- A clean report is not permission to install, publish, or run a Skill.

## Security

Please report suspected vulnerabilities through [GitHub Security Advisories](https://github.com/rwang23/skill-rigor/security/advisories/new). Do not put live credentials or private audit payloads in a public issue. See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
