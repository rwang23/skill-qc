# Review and iteration protocol

## Pass 1: deterministic baseline

1. Bind one exact Skill directory whose root contains `SKILL.md`.
2. Select profile and maturity explicitly.
3. Save JSON and localized HTML outputs; the CLI redacts the target root by default.
4. Record the Skill revision and rubric version.
5. Do not edit the target while collecting the baseline.

The baseline answers “what did this rubric observe?” It does not prove that every heuristic finding is valid or that the Skill succeeds in real tasks.

## Pass 2: context adjudication

Review blockers and high findings first. Record one outcome for each disputed item:

- `confirmed`: direct package evidence matches the rule;
- `false-positive`: negation, quoted security material, or another explicit boundary invalidates the detector;
- `profile-exception`: the selected local profile permits the assumption;
- `needs-behavioral-evidence`: static inspection cannot settle the claim;
- `out-of-scope`: the concern is valid but not owned by this Skill package.

Do not suppress a rule merely to increase the score. Change a detector only when a minimal fixture proves the old behavior wrong for the rubric as a whole.

## Pass 3: bounded improvement

Run this pass only when the user separately authorizes edits to the audited Skill.

1. Fix blockers without combining unrelated cleanup.
2. Improve routing before expanding the body.
3. Externalize repeated code or examples through direct references.
4. Add balanced routing fixtures before claiming Library or Governed maturity.
5. Rerun with the prior JSON passed as `--baseline`.
6. Inspect `resolved_findings`, `new_findings`, and `score_delta`.
7. Repeat for at most three rounds by default.

Stop early when blockers are gone, the intended maturity contract is met, and a new round produces no material change. Report `INCONCLUSIVE` when the requested claim requires E3/E4 but target-client evidence is unavailable.

## Safety adjudication

- Never print or copy a matched secret value. Report only pattern class, file, and line.
- A destructive command is not automatically unsafe inside an explicit prohibition, dry-run, scoped confirmation, backup, or rollback contract.
- A security example that quotes an instruction-bypass phrase is acceptable only when nearby text clearly says not to follow it.
- A local-path exception does not make a package portable.

## Reporting order

Lead with the tuple: score, gate, evidence, profile, maturity. Then present:

1. per-dimension score reasons and improvements;
2. blockers and high findings;
3. strongest evidence and its revision or observation time;
4. iteration delta;
5. residual uncertainty and the next decisive test.

Never use “certified,” “secure,” “production-ready,” or “effective” from E1/E2 alone.
