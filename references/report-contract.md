# Single-Skill report contract

Every run emits one JSON record and one self-contained HTML webpage for exactly one Skill package.

## Required headline

- artifact quality score out of 100;
- `PASS`, `REVIEW`, or `BLOCKED` gate;
- E1–E4 evidence grade;
- selected profile and maturity;
- Skill name, current `SKILL.md` revision, and iteration number.

## Required dimension detail

Each of the eight dimensions includes:

- earned points and maximum weight;
- a qualitative status;
- one or more reasons for the score;
- evidence-linked deductions with rule code, severity, file, and line;
- at least one concrete next improvement, including for a full-score dimension.

## Required report sections

1. headline score and independent evidence/safety signals;
2. dimension overview;
3. per-dimension reasons and improvements;
4. prioritized findings;
5. method and claim boundary;
6. generation date and target revision.

The English and Simplified Chinese templates must present the same report data and remain responsive, printable, keyboard-independent, and self-contained. They are webpages, not slide decks.

## Privacy and integrity

- The CLI replaces the absolute target root with `<SKILL:name>` before saving JSON or HTML.
- Additional private prefixes require `--redact-root SOURCE=LABEL`.
- Matched secret values never enter the report data.
- Embedded JSON escapes HTML-significant characters before insertion into the template.
