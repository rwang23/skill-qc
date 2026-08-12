# Contributing

Contributions should keep SkillQC deterministic, read-only, and explainable. Single mode stays focused on one Skill; repository mode aggregates independently audited Skills without changing their scores.

1. Open an issue describing the false positive, false negative, report defect, or rubric change.
2. Add one behavior-focused test that fails for the current public interface.
3. Make the smallest implementation change that passes it.
4. Run `python -m unittest discover -s tests -v`.
5. Regenerate the single-Skill self-audit and anonymized repository examples when package behavior or report output changes.

Increment `RUBRIC_VERSION` when a weight, threshold, severity, cap, or evidence rule changes. Repository aggregation alone does not change the rubric version. Do not change a detector solely to increase the project's self-score, present E1/E2 as target-client effectiveness, or treat artifact quality as business expertise.
