# SkillQC report contract

Every run emits one machine-readable JSON record and one self-contained HTML webpage. The report mode is either `single` or `repository`.

## Single-Skill report

The headline includes:

- artifact-quality score out of 100;
- `PASS`, `REVIEW`, or `BLOCKED` safety gate;
- E1 to E4 evidence grade;
- selected profile and maturity;
- Skill name, current `SKILL.md` revision, and iteration number.

Each of the eight dimensions includes:

- earned points and maximum weight;
- qualitative status;
- one or more reasons for the score;
- evidence-linked deductions with rule code, severity, file, and line;
- at least one concrete next improvement, including for a full-score dimension.

The webpage presents the headline, an eight-dimension overview, dimension details, prioritized findings, method and claim boundary, generation date, and target revision.

## Repository report

Repository mode audits every discoverable Skill independently and includes:

- unweighted average of all individual 100-point scores;
- number of Skills included and minimum to maximum score range;
- average earned score for each of the eight dimensions;
- `PASS`, `REVIEW`, and `BLOCKED` distribution;
- E1, E2, E3, and E4 distribution;
- a per-Skill ledger with score, gate, and evidence grade;
- recurring finding codes ordered by affected-Skill count.

The repository gate is `BLOCKED` when any included Skill is blocked. Otherwise it is `REVIEW` when any included Skill requires review, and `PASS` only when all included Skills pass. The average never replaces this gate.

With `--anonymize`, the report replaces Skill names and package paths with stable labels such as `Skill 001`. Scores, gates, evidence, and finding classes remain unchanged.

## Shared presentation rules

English and Simplified Chinese templates must present equivalent data. Reports remain responsive, printable, keyboard-independent, and self-contained. They are webpages, not slide decks.

Every report states the evaluation boundary: SkillQC measures the engineering quality of the Skill artifact. It does not judge business expertise, domain depth, commercial value, strategy, or real-world outcomes.

## Privacy and integrity

- The CLI replaces the absolute single target with `<SKILL:name>` and the repository root with `<REPOSITORY>` before saving JSON or HTML.
- Additional private prefixes require `--redact-root SOURCE=LABEL`.
- Matched secret values never enter report data.
- Embedded JSON escapes HTML-significant characters before insertion into a template.
