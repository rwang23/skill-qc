# Skill maturity decision

- Skill: `skill-rigor`
- Decision: `governed`
- Previous mode: `library` as `audit-agent-skill`
- Triggering fact: public GitHub distribution, public scoring claims, cross-agent reuse, and safety-gate behavior now form part of the durable product boundary.
- Evidence: versioned rubric, balanced route fixtures, regression suite, bilingual report tests, exact runtime sync, self-audit, and public CI.
- Boundaries: read-only static review of one Skill; no target execution, repair, installation, registry mutation, or publication authority.
- Required gates: package validation, route-fixture checks, regression tests, self-audit, report browser review, public-safety scan, exact runtime sync, and P3 proof for remote publication.
- Checks last run: recorded in the release commit and CI for each revision.
- Missing evidence / residual risk: E2 does not prove target-client routing or task success; heuristic safety and intent checks can misclassify unusual examples.
- Owner and next review: `rwang23`; review on scoring-rule changes, a security report, or the next release boundary.

Governed maturity classifies the maintained asset. It does not grant permission for a production, destructive, authenticated, or external action.
