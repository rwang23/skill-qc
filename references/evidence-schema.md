# Behavioral evidence contract

SkillRigor accepts evidence for one Skill only.

```json
{
  "grade": "E3",
  "target_revision": "<sha256-of-current-SKILL.md>",
  "observed_at": "2026-08-11T16:00:00Z",
  "source": "trace://target-client/run-001",
  "claims": [
    "routing-selection",
    "representative-task-output"
  ]
}
```

`grade` must be `E3` or `E4`. `target_revision`, `observed_at`, and `source` are mandatory. The source should resolve to an internally reviewable trace, test artifact, or accountable record; the auditor records the reference but does not fetch it.

## Acceptance rules

- Revision must equal the SHA-256 of the current UTF-8 `SKILL.md` content.
- E3 requires a named target client or representative task trace.
- E4 requires a real operating trace plus accountable human or governance review.
- Synthetic prompts, lexical overlap, static lint, and unexecuted test definitions stop at E2.
- Evidence does not override a safety blocker or maturity requirement.
- Stale or incomplete evidence produces a high-severity finding and receives no credit.
