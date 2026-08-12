# Contributing

Contributions should keep SkillRigor deterministic, read-only, explainable, and focused on one Skill per report.

1. Open an issue describing the false positive, false negative, report defect, or rubric change.
2. Add one behavior-focused test that fails for the current public interface.
3. Make the smallest implementation change that passes it.
4. Run `python -m unittest discover -s tests -v`.
5. Regenerate the self-audit when package behavior or report output changes.

Increment `RUBRIC_VERSION` when a weight, threshold, severity, cap, or evidence rule changes. Do not change a detector solely to increase the project’s self-score, and do not present E1/E2 evidence as target-client or real-world effectiveness.
