# SkillQC rubric

## Read the whole result

Read every audit as this tuple:

```text
artifact quality score / safety gate / evidence grade / profile / maturity
```

The 100-point score measures observable package quality under this rubric. It does not score the professional depth, business strategy, commercial value, or task result of the capability. The gate preserves non-compensable risk. The evidence grade states how much real behavior has been observed. Profile and maturity decide which constraints apply.

A Skill can therefore score `100 / PASS / E2`: its package meets every scored contract and its balanced routing fixtures are present, while target-client or real-world behavior remains unproved. This separation prevents evidence from being counted twice and makes a perfect artifact score narrower than an effectiveness claim.

## Weighted dimensions

| Dimension | Weight | Full-credit contract |
|---|---:|---|
| Routing | 18 | Valid name and frontmatter; concise capability plus explicit trigger; folder-name alignment |
| Executability | 16 | Short imperative workflow, decisive steps, explicit output, and bounded stop conditions |
| Context | 10 | Main body stays focused and below 500 lines; no redundant title or bulk reference material |
| Resources | 9 | Repeated examples and code are externalized; linked resources resolve; loading is progressive |
| Safety | 20 | Runtime text contains no exposed secret, policy bypass, or unguarded destructive action; authority boundaries are explicit |
| Portability | 8 | No undeclared user path, concrete model dependency, or machine-specific assumption for the selected profile |
| Effectiveness readiness | 12 | The routing and regression artifacts required by the declared maturity are present, valid, balanced, and revision-aware |
| Maintainability | 7 | No unfinished executable instructions; metadata, tests, and lifecycle declarations agree |

Findings deduct points from their owning dimension, floored at zero. The total is the rounded sum. Every dimension in JSON and HTML includes its score, reasons, deductions, and next improvements.

## Gate status

- `PASS`: no blocker or high-severity finding was detected.
- `REVIEW`: at least one high-severity finding requires human adjudication.
- `BLOCKED`: at least one blocker exists. Do not install, publish, or depend on the Skill until it is resolved or shown to be a false positive.

Critical caps prevent a high average from hiding severe defects:

- exposed secret pattern or unguarded instruction bypass: maximum score 39;
- unguarded destructive action: maximum score 49.

## Evidence grades

Evidence grades do not add score points.

| Grade | Required evidence | Permitted claim |
|---|---|---|
| E1 | Static package scan | Structural conformance only |
| E2 | Balanced routing fixtures covering positive, negative, near-neighbor, held-out, and pressure cases | Regression-fixture coverage |
| E3 | Same-revision target-client routing or representative task trace | Observed behavior on the named client or task set |
| E4 | Same-revision real operating trace plus accountable review | Observed behavior within the recorded operating scope |

Lexical matching, synthetic prompts, and fixture presence never count as E3. External E3/E4 evidence must include `target_revision`, `observed_at`, and `source`; stale evidence is rejected.

## Profiles

- `portable`: for a distributable package. User-specific paths are high-severity defects.
- `agent-skills`: centers the public Agent Skills specification.
- `codex-local`: permits declared machine-local paths without a point deduction, while retaining an informational finding.

## Maturity

- `unclassified`: no lifecycle requirements are inferred.
- `scaffold`: structural validation is enough to start iteration.
- `production`: a user-facing reusable workflow; a missing routing suite remains visible as an evidence gap.
- `library`: broad reuse or distribution; balanced routing fixtures are required.
- `governed`: Library requirements plus accountable ownership, review, release, and claim boundaries.

Maturity never grants permission to perform a risky action.

## Research inspiration

SkillQC was inspired in part by [*What Keeps Agent Skills from Being Reusable? Evidence from 138K SKILL.md Files*](https://arxiv.org/abs/2608.08453). The mapping below records how broad research themes informed this independent rubric; SkillQC does not reproduce the paper's detector.

| Research theme | SkillQC dimensions |
|---|---|
| R1 routing metadata | Routing |
| R2 instruction body | Executability and Context |
| R3 resource organization | Resources and Context |
| R4 prohibited content | Executability and Maintainability |
| R5 safety and security | Safety |
| R6 environment and portability | Portability |
| R7 persona and scope | Executability, Safety, and Maintainability |

Static heuristics can misclassify negated examples, legitimate security material, local-only contracts, and unusual workflows. A score records what this version of the rubric observed; it is not a certification.

## Repository aggregation

Repository mode applies this same rubric independently to every discoverable Skill, then reports the unweighted arithmetic mean of the individual 100-point scores. Each dimension is also averaged against its own maximum weight. The report keeps per-Skill scores, safety-gate distribution, evidence distribution, and recurring findings visible.

The repository average is a portfolio summary, not a new scoring rule. One blocked Skill keeps the repository gate at `BLOCKED`; one review Skill keeps it at `REVIEW` when none is blocked. Names and package paths may be anonymized for a shareable report, but the underlying scores do not change.

## Versioning

Every report records `rubric_version`. Increment it whenever a weight, threshold, severity, cap, or evidence rule changes, and add a focused regression test. Compare iteration deltas only when the rubric version is unchanged; otherwise label the comparison as a rubric migration.
