# Documentation map

## Reading order

1. [`agent-brief.md`](agent-brief.md)
2. [`../README.md`](../README.md)
3. [`../references/rubric.md`](../references/rubric.md)
4. The narrow protocol, schema, or template needed for the task

## Durable documents

- [`agent-brief.md`](agent-brief.md): project router and safety boundary.
- [`document-structure-baseline.json`](document-structure-baseline.json): provisional structure authority awaiting owner confirmation.
- [`maturity-decision.md`](maturity-decision.md): Governed classification and evidence boundary.
- [`CHANGELOG.md`](CHANGELOG.md): rubric and release history.
- [`../references/rubric.md`](../references/rubric.md): scoring authority.
- [`../references/review-protocol.md`](../references/review-protocol.md): audit and iteration workflow.
- [`../references/evidence-schema.md`](../references/evidence-schema.md): E3/E4 traceability contract.
- [`../references/report-contract.md`](../references/report-contract.md): single-Skill and repository JSON plus bilingual webpage requirements.

Public single-Skill and anonymized repository examples live in `examples/`. README screenshots live in `docs/images/`. Disposable local runs belong in ignored `.audit-work/`, not in durable documentation.

This project does not currently retain `docs/92-report/`, `docs/94-archive/`, or `context/raw/`; if introduced later, they are historical or execution-time surfaces and are not part of the default first-read path.

## Maintenance rules

- Update only the authority whose behavior changed.
- Keep reusable scoring and evidence rules in `references/`; keep release history in `CHANGELOG.md`.
- Do not commit private target reports, raw local inventory, credentials, or user-specific paths.
- Leave a changed structure baseline `provisional` until the owner reviews the post-change map.
