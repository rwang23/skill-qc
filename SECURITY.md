# Security policy

## Reporting a vulnerability

Use [GitHub Security Advisories](https://github.com/rwang23/skill-rigor/security/advisories/new) for suspected vulnerabilities. Please include the affected revision, a minimal reproduction, and the expected versus observed boundary.

Do not open a public issue containing live credentials, private Skill packages, local audit payloads, or exploit details that would put users at immediate risk.

## Scope

Security reports may cover secret-value leakage, report injection, unsafe target execution, path-redaction failures, incorrect safety-gate behavior, or a bypass of the read-only audit boundary.

SkillRigor is a static review aid, not a sandbox. It never grants authority to install or execute the audited Skill.
