#!/usr/bin/env python3
"""SkillQC: evidence-qualified static audits for Agent Skill packages."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from typing import Any


RUBRIC_VERSION = "1.0.0"
DIMENSION_WEIGHTS = {
    "routing": 18,
    "executability": 16,
    "context": 10,
    "resources": 9,
    "safety": 20,
    "portability": 8,
    "effectiveness": 12,
    "maintainability": 7,
}
DIMENSION_DEFAULT_REASONS = {
    "routing": "Name, description, trigger conditions, and folder alignment passed every scored routing check.",
    "executability": "The activated body exposes an actionable workflow with explicit execution steps.",
    "context": "The main SKILL.md stays focused and within the progressive-disclosure context budget.",
    "resources": "Local resources are organized for progressive loading and every referenced path resolves.",
    "safety": "No exposed secret, instruction bypass, or unguarded destructive action was detected.",
    "portability": "No undeclared user path, concrete model dependency, or machine-specific assumption was detected.",
    "effectiveness": "The package includes the routing and regression artifacts required for its declared maturity.",
    "maintainability": "The package contains no unfinished executable instructions or lifecycle mismatch detected by the rubric.",
}
DIMENSION_DEFAULT_IMPROVEMENTS = {
    "routing": "Revalidate the description with fresh positive, negative, and near-neighbor prompts before each release.",
    "executability": "Run one representative task and tighten any workflow step that requires unstated judgment.",
    "context": "Keep SKILL.md below 500 lines and move new detail into directly linked references.",
    "resources": "Recheck every linked resource and load it only at the workflow step that needs it.",
    "safety": "Repeat the permission and destructive-action review whenever the Skill gains a new capability.",
    "portability": "Test the package on another supported client or environment before claiming broader compatibility.",
    "effectiveness": "Advance the separate evidence grade with a same-revision target-client trace; use accountable operating review for E4.",
    "maintainability": "Rerun package, routing, and report checks on every tagged release.",
}
FINDING_RECOMMENDATIONS = {
    "routing.frontmatter-invalid": "Add valid YAML frontmatter at the beginning of SKILL.md.",
    "routing.name-missing": "Declare a lowercase hyphenated name in frontmatter.",
    "routing.name-invalid": "Rename the Skill with lowercase letters, digits, and single hyphens only.",
    "routing.name-folder-mismatch": "Make the frontmatter name and containing folder name identical.",
    "routing.description-missing": "Write a concise description that states both capability and activation conditions.",
    "routing.description-over-spec-limit": "Compress the description below 1,024 characters and move detail into the body.",
    "routing.description-too-thin": "State what the Skill does and the concrete requests or conditions that should trigger it.",
    "routing.trigger-missing": "Add an explicit use-when trigger and an important near-neighbor exclusion.",
    "routing.description-over-250": "Front-load capability and trigger language, then remove non-routing detail.",
    "executability.workflow-missing": "Replace background prose with a short imperative workflow and an explicit output.",
    "executability.package-maintenance-in-body": "Move installation, license, changelog, and release material outside activated instructions.",
    "context.body-over-500-lines": "Externalize detailed examples and reference material while keeping the main workflow executable.",
    "context.name-as-heading": "Remove the repeated title and begin with the workflow or decision boundary.",
    "resources.inline-examples-excessive": "Move repeated examples or code into directly linked resource files.",
    "resources.monolithic-body": "Split reusable code, references, or assets into progressively loaded package resources.",
    "resources.reference-missing": "Restore the linked file or update the link to a package-relative path that resolves.",
    "maintainability.unfinished-marker": "Resolve or remove unfinished executable instructions before release.",
    "portability.user-path": "Replace the user-specific path with a relative path, parameter, or declared configuration input.",
    "portability.user-path-local-profile": "Keep the local-only contract explicit and exclude this path from portable releases.",
    "portability.hardcoded-model": "Route by capability or expose the model as configuration.",
    "verification.eval-suite-missing": "Add positive, negative, near-neighbor, held-out, and pressure routing fixtures.",
    "verification.eval-suite-absent": "Add a focused routing suite if this Skill can be confused with a near neighbor.",
    "verification.routing-case-coverage": "Add every missing routing case type and record its expected selection boundary.",
    "verification.pressure-case-missing": "Add one adversarial or deadline-pressure case that must preserve safety and evidence boundaries.",
    "verification.eval-suite-invalid": "Repair evals/evals.json and validate its case schema.",
    "effectiveness.evidence-invalid": "Provide a complete revision-bound E3 or E4 evidence record.",
    "effectiveness.evidence-revision-mismatch": "Rerun the behavioral check against the current SKILL.md revision.",
    "safety.secret-pattern": "Remove and rotate the credential, then reference a secure runtime configuration source.",
    "safety.destructive-unguarded": "Require exact scope, explicit confirmation, backup or dry-run, and rollback before the action.",
    "safety.instruction-bypass": "Remove the bypass directive and preserve higher-priority policy and approval boundaries.",
}
# Detector examples only: never execute, expose, or reuse matched sensitive material.
SECRET_PATTERNS = (
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
# Detector examples only: destructive actions require confirmation, exact scope, backup, and rollback.
DESTRUCTIVE_PATTERN = re.compile(
    r"\brm\s+-rf\b|\bRemove-Item\b[^\n]*(?:-Recurse|-Force)|\bgit\s+reset\s+--hard\b|\bdocker\s+system\s+prune\b|\bDROP\s+(?:TABLE|DATABASE)\b",
    re.I,
)
GUARD_PATTERN = re.compile(
    r"\b(?:do not|never|must not|forbid|prohibit|confirm|approval|explicit(?:ly)? authori[sz]|dry[- ]run|allowlist|whitelist|backup|rollback)\b|禁止|不得|不要|确认|明确授权|白名单|备份|回滚",
    re.I,
)
# Detector examples only: do not copy user-specific paths or concrete model names into a portable Skill.
USER_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:\\Users\\[^<\\\s`]+|/Users/[^</\s`]+|/home/[^</\s`]+)",
    re.I,
)
MODEL_PATTERN = re.compile(
    r"\b(?:gpt-4(?:o|\.\d+)?|claude-(?:3|sonnet|opus|haiku)|gemini-(?:1|2)(?:\.\d+)?|o[134]-mini)\b",
    re.I,
)
INSTRUCTION_BYPASS_PATTERN = re.compile(
    r"\b(?:ignore (?:all|any|the) previous instructions|bypass (?:safety|policy|approval|guardrails?)|disable (?:safety|policy|guardrails?)|do not ask for (?:confirmation|approval))\b|忽略(?:所有|任何)?(?:先前|之前)指令|绕过(?:安全|政策|审批|确认)",
    re.I,
)
ACTION_LINE_PATTERN = re.compile(
    r"(?im)^\s*(?:(?:\d+[.)]|[-*])\s+)?(?:read|inspect|identify|select|compare|run|execute|write|create|generate|return|report|verify|validate|ask|require|stop|open|load|parse|render|record|check|review|summari[sz]e|audit|score|评估|检查|读取|运行|生成|验证|报告|停止|确认|选择|比较)\b"
)
WORKFLOW_HEADING_PATTERN = re.compile(
    r"(?im)^#{1,4}\s+(?:workflow|procedure|steps?|instructions?|execution|工作流|流程|步骤|执行)\b"
)
NUMBERED_STEP_PATTERN = re.compile(r"(?m)^\s*\d+[.)]\s+\S+")
VALID_SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RUNTIME_TEXT_ROOTS = ("agents", "assets", "evals", "references", "scripts")
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
REPOSITORY_IGNORED_PARTS = {
    ".audit-work",
    ".git",
    ".worktrees",
    "__pycache__",
    "build",
    "dist",
    "fixtures",
    "node_modules",
    "test",
    "tests",
    "vendor_imports",
}


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|\Z)", text, re.S)
    if not match:
        return {}, text
    raw, body = match.group(1), text[match.end() :]
    values: dict[str, str] = {}
    lines = raw.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        field = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not field:
            index += 1
            continue
        key, value = field.group(1), field.group(2).strip()
        if value in {"|", ">", "|-", ">-", "|+", ">+"}:
            block: list[str] = []
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index][:1].isspace()):
                block.append(lines[index].strip())
                index += 1
            values[key] = " ".join(part for part in block if part).strip()
            continue
        if not value and key in {"description", "compatibility", "license"}:
            block = []
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index][:1].isspace()):
                block.append(lines[index].strip())
                index += 1
            values[key] = " ".join(part for part in block if part).strip()
            continue
        values[key] = value.strip('"\'')
        index += 1
    return values, body


def _finding(
    code: str,
    dimension: str,
    severity: str,
    message: str,
    points_lost: float,
    path: Path,
    line: int = 1,
    confidence: str = "high",
) -> dict[str, Any]:
    return {
        "code": code,
        "dimension": dimension,
        "severity": severity,
        "confidence": confidence,
        "message": message,
        "points_lost": points_lost,
        "file": str(path),
        "line": line,
    }


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _has_nearby_guard(text: str, match: re.Match[str]) -> bool:
    lines = text.splitlines()
    line_index = _line_number(text, match.start()) - 1
    start = max(0, line_index - 7)
    end = min(len(lines), line_index + 4)
    return bool(GUARD_PATTERN.search("\n".join(lines[start:end])))


def _strip_code(text: str) -> str:
    without_fences = re.sub(r"```.*?```", "", text, flags=re.S)
    without_inline = re.sub(r"`[^`\n]+`", "", without_fences)
    return re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", without_inline)


def _normalise_heading(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _runtime_texts(skill_dir: Path) -> list[tuple[Path, str]]:
    files = [skill_dir / "SKILL.md"]
    for directory in RUNTIME_TEXT_ROOTS:
        root = skill_dir / directory
        if root.is_dir():
            files.extend(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
            )
    results: list[tuple[Path, str]] = []
    for path in sorted(set(files), key=lambda item: str(item).lower()):
        if path.stat().st_size <= 2_000_000:
            results.append((path, path.read_text(encoding="utf-8-sig", errors="replace")))
    return results


def _dimension_result(
    dimension: str,
    weight: int,
    score: float,
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    relevant = [item for item in findings if item["dimension"] == dimension]
    deductions = [item for item in relevant if float(item["points_lost"]) > 0]
    reasons = [
        f"Lost {item['points_lost']:g} point(s): {item['message']}"
        for item in deductions
    ]
    if not reasons:
        reasons = [DIMENSION_DEFAULT_REASONS[dimension]]
    improvements = list(
        dict.fromkeys(
            FINDING_RECOMMENDATIONS.get(
                item["code"], DIMENSION_DEFAULT_IMPROVEMENTS[dimension]
            )
            for item in relevant
        )
    )
    if not improvements:
        improvements = [DIMENSION_DEFAULT_IMPROVEMENTS[dimension]]
    ratio = score / weight if weight else 0
    if ratio >= 0.9:
        status = "excellent"
    elif ratio >= 0.75:
        status = "good"
    elif ratio >= 0.5:
        status = "review"
    else:
        status = "critical"
    return {
        "id": dimension,
        "weight": weight,
        "score": score,
        "status": status,
        "reasons": reasons,
        "improvements": improvements,
        "deductions": [
            {
                "code": item["code"],
                "severity": item["severity"],
                "points_lost": item["points_lost"],
                "message": item["message"],
                "file": item["file"],
                "line": item["line"],
            }
            for item in deductions
        ],
    }


def _audit_skill(
    skill_dir: Path,
    profile: str,
    maturity: str,
    external_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    skill_file = skill_dir / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8-sig", errors="replace")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    frontmatter, body = _parse_frontmatter(text)
    declared_name = frontmatter.get("name", "").strip()
    name = declared_name or skill_dir.name
    description = frontmatter.get("description", "").strip()
    findings: list[dict[str, Any]] = []
    runtime_texts = _runtime_texts(skill_dir)

    if not frontmatter:
        findings.append(
            _finding(
                "routing.frontmatter-invalid",
                "routing",
                "blocker",
                "SKILL.md must begin with valid YAML frontmatter.",
                18,
                skill_file,
            )
        )
    if not declared_name:
        findings.append(
            _finding(
                "routing.name-missing",
                "routing",
                "blocker",
                "Frontmatter name is required for portable discovery.",
                10,
                skill_file,
            )
        )
    elif len(declared_name) > 64 or not VALID_SKILL_NAME_PATTERN.fullmatch(declared_name):
        findings.append(
            _finding(
                "routing.name-invalid",
                "routing",
                "high",
                "Name must be at most 64 characters and use lowercase letters, digits, and single hyphens.",
                5,
                skill_file,
            )
        )
    if declared_name and declared_name != skill_dir.name:
        findings.append(
            _finding(
                "routing.name-folder-mismatch",
                "routing",
                "high",
                "Frontmatter name does not match the containing directory name.",
                3,
                skill_file,
            )
        )
    if not description:
        findings.append(
            _finding(
                "routing.description-missing",
                "routing",
                "blocker",
                "Description is required for discovery.",
                12,
                skill_file,
            )
        )
    elif len(description) > 1024:
        findings.append(
            _finding(
                "routing.description-over-spec-limit",
                "routing",
                "blocker",
                "Description exceeds the 1,024-character Agent Skills specification limit.",
                12,
                skill_file,
            )
        )
    elif len(description) < 40 or (
        not re.search(r"[\u3400-\u9fff]", description) and len(description.split()) < 7
    ):
        findings.append(
            _finding(
                "routing.description-too-thin",
                "routing",
                "high",
                "Description is too thin to reliably communicate both capability and trigger conditions.",
                5,
                skill_file,
            )
        )
    trigger_pattern = re.compile(
        r"\b(use when|use for|when (?:the |a |an |users? |asked|working|handling)|whenever|trigger)\b|适用于|当.{0,40}时|用户明确要求.{0,120}时使用|触发",
        re.I | re.S,
    )
    if description and not trigger_pattern.search(description):
        findings.append(
            _finding(
                "routing.trigger-missing",
                "routing",
                "high",
                "Description says too little about when the skill should activate.",
                7,
                skill_file,
            )
        )
    if len(description) > 250:
        findings.append(
            _finding(
                "routing.description-over-250",
                "routing",
                "medium",
                f"Description has {len(description)} characters; front-load and compress the routing contract.",
                3,
                skill_file,
            )
        )

    actionable_lines = len(ACTION_LINE_PATTERN.findall(body))
    numbered_steps = len(NUMBERED_STEP_PATTERN.findall(body))
    if actionable_lines < 2 and numbered_steps < 2 and not WORKFLOW_HEADING_PATTERN.search(body):
        findings.append(
            _finding(
                "executability.workflow-missing",
                "executability",
                "high",
                "The activated body is mostly background prose and lacks a short executable workflow.",
                8,
                skill_file,
                confidence="medium",
            )
        )

    setup_heading = re.search(
        r"(?im)^#{1,4}\s+(?:installation|install|changelog|license|release notes?)\s*$",
        body,
    )
    if setup_heading:
        findings.append(
            _finding(
                "executability.package-maintenance-in-body",
                "executability",
                "medium",
                "Package installation, license, or changelog material belongs outside the activated workflow.",
                3,
                skill_file,
                _line_number(body, setup_heading.start()),
            )
        )

    line_count = len(text.splitlines())
    if line_count > 500:
        findings.append(
            _finding(
                "context.body-over-500-lines",
                "context",
                "medium",
                f"SKILL.md has {line_count} lines; move detailed material into direct references.",
                5,
                skill_file,
            )
        )

    h1_headings = re.findall(r"^#\s+(.+?)\s*$", body, flags=re.M)
    if any(_normalise_heading(item) == _normalise_heading(name) for item in h1_headings):
        findings.append(
            _finding(
                "context.name-as-heading",
                "context",
                "low",
                "The first-level heading repeats the skill name and consumes activated context.",
                1,
                skill_file,
            )
        )

    code_block_count = len(re.findall(r"^```", body, flags=re.M)) // 2
    if code_block_count > 8:
        findings.append(
            _finding(
                "resources.inline-examples-excessive",
                "resources",
                "medium",
                f"SKILL.md contains {code_block_count} fenced blocks; externalize repeated examples or code.",
                3,
                skill_file,
            )
        )

    resource_directories = [
        name for name in ("scripts", "references", "assets") if (skill_dir / name).is_dir()
    ]
    if line_count > 200 and not resource_directories:
        findings.append(
            _finding(
                "resources.monolithic-body",
                "resources",
                "medium",
                "A long body has no scripts, references, or assets for progressive disclosure.",
                4,
                skill_file,
            )
        )

    link_source = re.sub(r"```.*?```", "", body, flags=re.S)
    link_source = re.sub(r"`[^`\n]+`", "", link_source)
    for link_match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", link_source):
        reference = link_match.group(1).split("#", 1)[0].strip().strip("<>")
        if (
            not reference
            or "://" in reference
            or reference.startswith(("#", "/", "\\"))
        ):
            continue
        if not (skill_dir / reference).exists():
            findings.append(
                _finding(
                    "resources.reference-missing",
                    "resources",
                    "high",
                    "A relative resource link does not resolve inside the skill package.",
                    0,
                    skill_file,
                    _line_number(link_source, link_match.start()),
                )
            )

    prose_without_code = _strip_code(body)
    unfinished_match = re.search(
        r"(?im)^\s*(?:[-*]\s*)?(?:TODO|FIXME|TBD)\b(?:\s*:|\s*$)",
        prose_without_code,
    )
    if unfinished_match:
        findings.append(
            _finding(
                "maintainability.unfinished-marker",
                "maintainability",
                "medium",
                "An unfinished-work marker remains in executable instructions.",
                2,
                skill_file,
                _line_number(prose_without_code, unfinished_match.start()),
            )
        )

    user_path_source = next(
        (
            (path, content, match)
            for path, content in runtime_texts
            for match in USER_PATH_PATTERN.finditer(content)
            if not _has_nearby_guard(content, match)
        ),
        None,
    )
    if user_path_source:
        user_path_file, user_path_text, user_path_match = user_path_source
        if profile == "codex-local":
            findings.append(
                _finding(
                    "portability.user-path-local-profile",
                    "portability",
                    "info",
                    "A user-specific path is intentional only for this declared local profile; keep it out of portable distribution.",
                    0,
                    user_path_file,
                    _line_number(user_path_text, user_path_match.start()),
                    confidence="medium",
                )
            )
        else:
            findings.append(
                _finding(
                    "portability.user-path",
                    "portability",
                    "high",
                    "A user-specific absolute path prevents portable reuse; the path value is withheld.",
                    4,
                    user_path_file,
                    _line_number(user_path_text, user_path_match.start()),
                )
            )

    model_source = next(
        (
            (path, content, match)
            for path, content in runtime_texts
            for match in MODEL_PATTERN.finditer(content)
            if not _has_nearby_guard(content, match)
        ),
        None,
    )
    if model_source:
        model_file, model_text, model_match = model_source
        findings.append(
            _finding(
                "portability.hardcoded-model",
                "portability",
                "medium",
                "A concrete model name is hardcoded; prefer a capability or configurable model route.",
                3,
                model_file,
                _line_number(model_text, model_match.start()),
                confidence="medium",
            )
        )

    evidence_grade = "E1"
    eval_path = skill_dir / "evals" / "evals.json"
    if not eval_path.is_file():
        if maturity in {"library", "governed"}:
            findings.append(
                _finding(
                    "verification.eval-suite-missing",
                    "effectiveness",
                    "high",
                    f"{maturity.title()} maturity requires routing regression evidence.",
                    6,
                    skill_file,
                    confidence="high",
                )
            )
        elif maturity == "production":
            findings.append(
                _finding(
                    "verification.eval-suite-absent",
                    "effectiveness",
                    "info",
                    "No routing eval suite is present; add one if route confusion is plausible.",
                    0,
                    skill_file,
                    confidence="medium",
                )
            )
    else:
        try:
            eval_data = json.loads(eval_path.read_text(encoding="utf-8-sig"))
            eval_cases = eval_data.get("evals", eval_data.get("cases", []))
            if not isinstance(eval_cases, list):
                raise ValueError("evals/cases must be a list")
            case_types = {
                str(case.get("routing", {}).get("case_type", case.get("type", ""))).strip()
                for case in eval_cases
                if isinstance(case, dict)
            }
            pressure_present = any(
                isinstance(case, dict) and bool(case.get("pressure")) for case in eval_cases
            )
            required_types = {"positive", "negative", "near-neighbor", "held-out"}
            missing_types = sorted(required_types - case_types)
            if maturity in {"library", "governed"} and missing_types:
                findings.append(
                    _finding(
                        "verification.routing-case-coverage",
                        "effectiveness",
                        "high",
                        "Routing evals lack required case types: " + ", ".join(missing_types) + ".",
                        min(5, len(missing_types) * 1.5),
                        eval_path,
                    )
                )
            if maturity in {"library", "governed"} and not pressure_present:
                findings.append(
                    _finding(
                        "verification.pressure-case-missing",
                        "effectiveness",
                        "medium",
                        "Routing evals lack a pressure or adversarial case.",
                        2,
                        eval_path,
                    )
                )
            if not missing_types and pressure_present:
                evidence_grade = "E2"
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            findings.append(
                _finding(
                    "verification.eval-suite-invalid",
                    "effectiveness",
                    "high",
                    f"Routing eval suite is unreadable or invalid: {type(exc).__name__}.",
                    6,
                    eval_path,
                )
            )

    if external_evidence:
        requested_grade = str(external_evidence.get("grade", "")).upper()
        required_fields = ("target_revision", "observed_at", "source")
        missing_fields = [field for field in required_fields if not external_evidence.get(field)]
        if requested_grade not in {"E3", "E4"} or missing_fields:
            findings.append(
                _finding(
                    "effectiveness.evidence-invalid",
                    "effectiveness",
                    "high",
                    "External evidence requires grade E3/E4 plus target_revision, observed_at, and source.",
                    0,
                    skill_file,
                )
            )
        elif external_evidence.get("target_revision") != digest:
            findings.append(
                _finding(
                    "effectiveness.evidence-revision-mismatch",
                    "effectiveness",
                    "high",
                    "Behavioral evidence targets a different Skill revision and is not credited.",
                    0,
                    skill_file,
                )
            )
        else:
            evidence_grade = requested_grade

    secret_source = next(
        (
            (path, content, match)
            for path, content in runtime_texts
            for pattern in SECRET_PATTERNS
            if (match := pattern.search(content))
        ),
        None,
    )
    if secret_source:
        secret_file, secret_text, secret_match = secret_source
        findings.append(
            _finding(
                "safety.secret-pattern",
                "safety",
                "blocker",
                "Possible hardcoded credential detected; value withheld from the report.",
                20,
                secret_file,
                _line_number(secret_text, secret_match.start()),
            )
        )

    destructive_source = next(
        (
            (path, content, match)
            for path, content in runtime_texts
            for match in DESTRUCTIVE_PATTERN.finditer(content)
            if not _has_nearby_guard(content, match)
        ),
        None,
    )
    if destructive_source:
        destructive_file, destructive_text, first = destructive_source
        findings.append(
            _finding(
                "safety.destructive-unguarded",
                "safety",
                "blocker",
                "A destructive command lacks a nearby prohibition, confirmation, scope, or rollback guard.",
                16,
                destructive_file,
                _line_number(destructive_text, first.start()),
            )
        )

    bypass_source = next(
        (
            (path, content, match)
            for path, content in runtime_texts
            for match in INSTRUCTION_BYPASS_PATTERN.finditer(content)
            if not _has_nearby_guard(content, match)
        ),
        None,
    )
    if bypass_source:
        bypass_file, bypass_text, first = bypass_source
        findings.append(
            _finding(
                "safety.instruction-bypass",
                "safety",
                "blocker",
                "An instruction attempts to override policy, approval, or higher-priority instructions.",
                18,
                bypass_file,
                _line_number(bypass_text, first.start()),
            )
        )

    dimension_scores = []
    for dimension, weight in DIMENSION_WEIGHTS.items():
        lost = sum(
            float(item["points_lost"])
            for item in findings
            if item["dimension"] == dimension
        )
        dimension_score = max(0, round(weight - lost, 1))
        dimension_scores.append(
            _dimension_result(dimension, weight, dimension_score, findings)
        )
    score = round(sum(item["score"] for item in dimension_scores))
    if any(item["severity"] == "blocker" for item in findings):
        gate = "BLOCKED"
    elif any(item["severity"] == "high" for item in findings):
        gate = "REVIEW"
    else:
        gate = "PASS"
    if any(
        item["code"] in {"safety.secret-pattern", "safety.instruction-bypass"}
        for item in findings
    ):
        score = min(score, 39)
    elif any(item["code"] == "safety.destructive-unguarded" for item in findings):
        score = min(score, 49)
    for item in findings:
        item["skill_name"] = name
    return {
        "name": name,
        "path": str(skill_dir),
        "revision": digest,
        "profile": profile,
        "maturity": maturity,
        "line_count": line_count,
        "description_length": len(description),
        "quality_score": score,
        "gate_status": gate,
        "evidence": {
            "grade": evidence_grade,
            "coverage": {"E1": 35, "E2": 60, "E3": 85, "E4": 100}[evidence_grade],
            "claim": {
                "E1": "static artifact scan",
                "E2": "balanced routing regression fixtures",
                "E3": "target-client routing or representative task run",
                "E4": "real-world trace plus accountable review",
            }[evidence_grade],
            "source": external_evidence.get("source") if external_evidence and evidence_grade in {"E3", "E4"} else None,
            "observed_at": external_evidence.get("observed_at") if external_evidence and evidence_grade in {"E3", "E4"} else None,
        },
        "dimensions": dimension_scores,
        "findings": findings,
    }


def _apply_iteration(
    report: dict[str, Any], baseline: dict[str, Any] | str | Path | None
) -> dict[str, Any]:
    if baseline is None:
        report["iteration"] = {
            "number": 1,
            "score_delta": None,
            "resolved_findings": [],
            "new_findings": [],
        }
        return report

    if isinstance(baseline, (str, Path)):
        baseline_report = json.loads(Path(baseline).read_text(encoding="utf-8-sig"))
    else:
        baseline_report = baseline
    previous_codes = {item["code"] for item in baseline_report.get("findings", [])}
    current_codes = {item["code"] for item in report["findings"]}
    previous_iteration = int(baseline_report.get("iteration", {}).get("number", 1))
    report["iteration"] = {
        "number": previous_iteration + 1,
        "score_delta": report["summary"]["quality_score"]
        - int(baseline_report.get("summary", {}).get("quality_score", 0)),
        "resolved_findings": sorted(previous_codes - current_codes),
        "new_findings": sorted(current_codes - previous_codes),
        "baseline_target": baseline_report.get("target"),
    }
    return report


def audit_target(
    target: str | Path,
    *,
    profile: str = "portable",
    maturity: str = "unclassified",
    baseline: dict[str, Any] | str | Path | None = None,
    evidence: dict[str, Any] | str | Path | None = None,
) -> dict[str, Any]:
    """Audit exactly one Skill package."""
    target_path = Path(target).resolve()
    if not (target_path / "SKILL.md").is_file():
        raise FileNotFoundError(
            f"Target must be one Skill directory containing SKILL.md: {target_path}"
        )
    if isinstance(evidence, (str, Path)):
        evidence_data = json.loads(Path(evidence).read_text(encoding="utf-8-sig"))
    else:
        evidence_data = evidence
    skill = _audit_skill(target_path, profile, maturity, evidence_data)
    findings = skill["findings"]
    report = {
        "schema_version": 2,
        "rubric_version": RUBRIC_VERSION,
        "mode": "single",
        "target": str(target_path),
        "summary": {
            "quality_score": skill["quality_score"],
            "score_scope": "artifact-quality",
            "gate_status": skill["gate_status"],
            "finding_count": len(findings),
        },
        "dimensions": skill["dimensions"],
        "findings": findings,
        "skill": skill,
        "evidence": dict(skill["evidence"]),
    }
    return _apply_iteration(report, baseline)


def _repository_skill_directories(root: Path) -> list[Path]:
    skill_dirs: list[Path] = []
    for skill_file in root.rglob("SKILL.md"):
        relative_parts = skill_file.relative_to(root).parts[:-1]
        if any(part.lower() in REPOSITORY_IGNORED_PARTS for part in relative_parts):
            continue
        skill_dirs.append(skill_file.parent)
    return sorted(set(skill_dirs), key=lambda path: path.as_posix().lower())


def _repository_optimization_queue(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    severity_order = {"blocker": 0, "high": 1, "medium": 2, "low": 3}
    gate_order = {"BLOCKED": 0, "REVIEW": 1, "PASS": 2}
    evidence_order = {"E1": 0, "E2": 1, "E3": 2, "E4": 3}
    queue: list[dict[str, Any]] = []

    for skill in skills:
        if (
            skill["quality_score"] >= 100
            and skill["gate_status"] == "PASS"
            and not skill["findings"]
        ):
            continue

        ranked_findings = sorted(
            skill["findings"],
            key=lambda item: (
                severity_order.get(item["severity"], 4),
                -float(item["points_lost"]),
                item["code"],
            ),
        )
        affected_dimensions = {
            finding["dimension"] for finding in ranked_findings
        }
        ranked_dimensions = sorted(
            (
                dimension
                for dimension in skill["dimensions"]
                if dimension["id"] in affected_dimensions
            ),
            key=lambda item: (
                item["score"] / item["weight"] if item["weight"] else 0,
                item["id"],
            ),
        )
        improvements = list(
            dict.fromkeys(
                improvement
                for dimension in ranked_dimensions
                for improvement in dimension["improvements"]
            )
        )[:3]
        priority = {
            "BLOCKED": "critical",
            "REVIEW": "high",
            "PASS": "medium",
        }[skill["gate_status"]]
        queue.append(
            {
                "name": skill["name"],
                "path": skill["path"],
                "quality_score": skill["quality_score"],
                "gate_status": skill["gate_status"],
                "evidence_grade": skill["evidence"]["grade"],
                "priority": priority,
                "finding_count": len(skill["findings"]),
                "top_findings": [
                    {
                        "code": finding["code"],
                        "dimension": finding["dimension"],
                        "severity": finding["severity"],
                        "points_lost": finding["points_lost"],
                        "message": finding["message"],
                        "file": finding["file"],
                        "line": finding["line"],
                    }
                    for finding in ranked_findings[:3]
                ],
                "improvements": improvements,
            }
        )

    return sorted(
        queue,
        key=lambda item: (
            gate_order[item["gate_status"]],
            item["quality_score"],
            evidence_order.get(item["evidence_grade"], 4),
            item["name"].lower(),
        ),
    )


def _audit_repository_with_mapping(
    target: str | Path,
    *,
    profile: str = "portable",
    maturity: str = "unclassified",
    anonymize: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    target_path = Path(target).resolve()
    if not target_path.is_dir():
        raise FileNotFoundError(f"Repository target must be a directory: {target_path}")
    skill_dirs = _repository_skill_directories(target_path)
    if not skill_dirs:
        raise FileNotFoundError(
            f"Repository contains no discoverable Skill package: {target_path}"
        )

    skills = [
        _audit_skill(skill_dir, profile, maturity, None) for skill_dir in skill_dirs
    ]
    mapping_entries: list[dict[str, Any]] = []
    if anonymize:
        for index, skill in enumerate(skills, start=1):
            label = f"Skill {index:03d}"
            private_path = str(skill["path"])
            public_path = f"<REPOSITORY>/skill-{index:03d}"
            mapping_entries.append(
                {
                    "anonymous_name": label,
                    "skill_name": skill["name"],
                    "path": private_path,
                    "relative_path": Path(private_path).relative_to(target_path).as_posix(),
                    "revision": skill["revision"],
                    "quality_score": skill["quality_score"],
                    "gate_status": skill["gate_status"],
                    "evidence_grade": skill["evidence"]["grade"],
                }
            )
            skill = _redact_report_paths(skill, [(private_path, public_path)])
            skill["name"] = label
            skill["path"] = public_path
            skill["revision"] = "<ANONYMIZED>"
            for finding in skill["findings"]:
                finding["skill_name"] = label
            skills[index - 1] = skill
    gate_counts = {gate: 0 for gate in ("PASS", "REVIEW", "BLOCKED")}
    evidence_counts = {grade: 0 for grade in ("E1", "E2", "E3", "E4")}
    finding_frequency_map: dict[str, dict[str, Any]] = {}
    for skill in skills:
        gate_counts[skill["gate_status"]] += 1
        evidence_counts[skill["evidence"]["grade"]] += 1
        for finding in skill["findings"]:
            entry = finding_frequency_map.setdefault(
                finding["code"],
                {
                    "code": finding["code"],
                    "dimension": finding["dimension"],
                    "severity": finding["severity"],
                    "skill_count": 0,
                },
            )
            entry["skill_count"] += 1
    if gate_counts["BLOCKED"]:
        gate_status = "BLOCKED"
    elif gate_counts["REVIEW"]:
        gate_status = "REVIEW"
    else:
        gate_status = "PASS"

    dimensions = []
    for dimension_id, weight in DIMENSION_WEIGHTS.items():
        values = [
            next(
                item["score"]
                for item in skill["dimensions"]
                if item["id"] == dimension_id
            )
            for skill in skills
        ]
        average_score = round(sum(values) / len(values), 1)
        ratio = average_score / weight if weight else 0
        if ratio >= 0.9:
            status = "excellent"
        elif ratio >= 0.75:
            status = "good"
        elif ratio >= 0.5:
            status = "review"
        else:
            status = "critical"
        dimensions.append(
            {
                "id": dimension_id,
                "weight": weight,
                "average_score": average_score,
                "average_percent": round(ratio * 100),
                "status": status,
                "full_score_count": sum(value == weight for value in values),
                "skill_count": len(skills),
            }
        )

    average_quality_score = round(
        sum(skill["quality_score"] for skill in skills) / len(skills), 1
    )
    skill_scores = [skill["quality_score"] for skill in skills]
    optimization_queue = _repository_optimization_queue(skills)
    finding_frequencies = sorted(
        finding_frequency_map.values(),
        key=lambda item: (-item["skill_count"], item["code"]),
    )
    report = {
        "schema_version": 2,
        "rubric_version": RUBRIC_VERSION,
        "mode": "repository",
        "target": "<REPOSITORY>" if anonymize else str(target_path),
        "profile": profile,
        "maturity": maturity,
        "summary": {
            "average_quality_score": average_quality_score,
            "score_scope": "artifact-quality-average",
            "skill_count": len(skills),
            "gate_status": gate_status,
            "gate_counts": gate_counts,
            "evidence_counts": evidence_counts,
            "score_range": {
                "minimum": min(skill_scores),
                "maximum": max(skill_scores),
            },
            "finding_count": sum(len(skill["findings"]) for skill in skills),
            "optimization_candidate_count": len(optimization_queue),
        },
        "dimensions": dimensions,
        "finding_frequencies": finding_frequencies,
        "optimization_queue": optimization_queue,
        "skills": skills,
    }
    return report, mapping_entries


def audit_repository(
    target: str | Path,
    *,
    profile: str = "portable",
    maturity: str = "unclassified",
    anonymize: bool = False,
) -> dict[str, Any]:
    """Audit every discoverable Skill package below one repository root."""
    report, _ = _audit_repository_with_mapping(
        target,
        profile=profile,
        maturity=maturity,
        anonymize=anonymize,
    )
    return report


def render_report(
    report: dict[str, Any],
    output_path: str | Path,
    *,
    title: str | None = None,
    locale: str = "en",
    template_path: str | Path | None = None,
) -> Path:
    """Render a single-Skill or repository audit as a responsive webpage."""
    if locale not in {"en", "zh-CN"}:
        raise ValueError("locale must be 'en' or 'zh-CN'")
    report_mode = report.get("mode", "single")
    if report_mode not in {"single", "repository"}:
        raise ValueError("report mode must be 'single' or 'repository'")
    if report_mode == "repository":
        default_title = (
            "SkillQC Repository Quality Report" if locale == "en" else "SkillQC 仓库质量报告"
        )
        template_name = f"repository-template.{locale}.html"
    else:
        default_title = (
            "SkillQC Quality Report" if locale == "en" else "SkillQC 单 Skill 质量报告"
        )
        template_name = f"report-template.{locale}.html"
    generated_at = str(report.get("generated_at") or "not-recorded")
    template = (
        Path(template_path)
        if template_path is not None
        else Path(__file__).resolve().parents[1] / "assets" / template_name
    )
    template_text = template.read_text(encoding="utf-8-sig")
    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":"))
    payload = (
        payload.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    rendered = template_text.replace("__AUDIT_DATA__", payload).replace(
        "__REPORT_TITLE__", html.escape(title or default_title, quote=True)
    ).replace("__GENERATED_AT__", html.escape(generated_at, quote=True))
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8", newline="\n")
    return output


def _redact_report_paths(value: Any, mappings: list[tuple[str, str]]) -> Any:
    if isinstance(value, dict):
        return {key: _redact_report_paths(item, mappings) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_report_paths(item, mappings) for item in value]
    if isinstance(value, str):
        result = value
        for source, label in mappings:
            result = result.replace(source, label)
            result = result.replace(source.replace("\\", "/"), label)
        return result
    return value


def _parse_redactions(values: list[str]) -> list[tuple[str, str]]:
    mappings = []
    for value in values:
        if "=" not in value:
            raise ValueError("--redact-root must use SOURCE=LABEL")
        source, label = value.split("=", 1)
        if not source or not label:
            raise ValueError("--redact-root requires non-empty SOURCE and LABEL")
        mappings.append((source, label))
    return mappings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit one Agent Skill or a repository of Skills with explainable scoring and safety gates."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit", help="Audit exactly one Skill package.")
    audit.add_argument("target")
    audit.add_argument(
        "--profile", choices=("portable", "agent-skills", "codex-local"), default="portable"
    )
    audit.add_argument(
        "--maturity",
        choices=("unclassified", "scaffold", "production", "library", "governed"),
        default="unclassified",
    )
    audit.add_argument("--baseline", help="Prior JSON report for an iteration delta.")
    audit.add_argument(
        "--evidence",
        help="Revision-bound E3/E4 evidence JSON for this Skill.",
    )
    audit.add_argument("--json-out", required=True)
    audit.add_argument("--html-out", required=True)
    audit.add_argument("--title")
    audit.add_argument(
        "--observed-at",
        help="Optional ISO-8601 audit timestamp recorded in JSON and HTML.",
    )
    audit.add_argument(
        "--locale", choices=("en", "zh-CN"), default="en", help="HTML report language."
    )
    audit.add_argument(
        "--redact-root",
        action="append",
        default=[],
        metavar="SOURCE=LABEL",
        help="Replace a local path prefix in saved JSON/HTML; repeatable.",
    )
    audit.add_argument("--stdout-json", action="store_true")

    repository = subparsers.add_parser(
        "audit-repository", help="Audit every discoverable Skill below one repository root."
    )
    repository.add_argument("target")
    repository.add_argument(
        "--profile", choices=("portable", "agent-skills", "codex-local"), default="portable"
    )
    repository.add_argument(
        "--maturity",
        choices=("unclassified", "scaffold", "production", "library", "governed"),
        default="unclassified",
    )
    repository.add_argument(
        "--anonymize",
        action="store_true",
        help="Replace Skill names and package paths with stable report-local labels.",
    )
    repository.add_argument(
        "--mapping-out",
        help="Write a separate private JSON map from anonymous labels to real Skill names and paths; requires --anonymize.",
    )
    repository.add_argument("--json-out", required=True)
    repository.add_argument("--html-out", required=True)
    repository.add_argument("--title")
    repository.add_argument(
        "--observed-at",
        help="Optional ISO-8601 audit timestamp recorded in JSON and HTML.",
    )
    repository.add_argument(
        "--locale", choices=("en", "zh-CN"), default="en", help="HTML report language."
    )
    repository.add_argument(
        "--redact-root",
        action="append",
        default=[],
        metavar="SOURCE=LABEL",
        help="Replace a local path prefix in saved JSON/HTML; repeatable.",
    )
    repository.add_argument("--stdout-json", action="store_true")

    render = subparsers.add_parser("render", help="Render an existing JSON report as HTML.")
    render.add_argument("json_report")
    render.add_argument("html_out")
    render.add_argument("--title")
    render.add_argument("--locale", choices=("en", "zh-CN"), default="en")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "render":
        report = json.loads(Path(args.json_report).read_text(encoding="utf-8-sig"))
        render_report(report, args.html_out, title=args.title, locale=args.locale)
        print(f"rendered={Path(args.html_out).resolve()}")
        return 0

    try:
        mappings = _parse_redactions(args.redact_root)
        if args.command == "audit-repository":
            if args.mapping_out and not args.anonymize:
                raise ValueError("--mapping-out requires --anonymize")
            report, mapping_entries = _audit_repository_with_mapping(
                args.target,
                profile=args.profile,
                maturity=args.maturity,
                anonymize=args.anonymize,
            )
            mappings.insert(0, (str(Path(args.target).resolve()), "<REPOSITORY>"))
        else:
            report = audit_target(
                args.target,
                profile=args.profile,
                maturity=args.maturity,
                baseline=args.baseline,
                evidence=args.evidence,
            )
            mappings.insert(
                0,
                (
                    str(Path(args.target).resolve()),
                    f"<SKILL:{report['skill']['name']}>",
                ),
            )
        saved_report = _redact_report_paths(report, mappings)
        if args.observed_at:
            saved_report["generated_at"] = args.observed_at
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(saved_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
        render_report(saved_report, args.html_out, title=args.title, locale=args.locale)
        if args.command == "audit-repository" and args.mapping_out:
            mapping_path = Path(args.mapping_out)
            mapping_path.parent.mkdir(parents=True, exist_ok=True)
            mapping_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "rubric_version": RUBRIC_VERSION,
                        "generated_at": args.observed_at or "not-recorded",
                        "target": str(Path(args.target).resolve()),
                        "entries": mapping_entries,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
                newline="\n",
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit-error={type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    summary = saved_report["summary"]
    if saved_report["mode"] == "repository":
        print(
            f"average={summary['average_quality_score']} gate={summary['gate_status']} "
            f"skills={summary['skill_count']} findings={summary['finding_count']}"
        )
    else:
        print(
            f"score={summary['quality_score']} gate={summary['gate_status']} "
            f"evidence={saved_report['evidence']['grade']} skill={saved_report['skill']['name']} "
            f"findings={summary['finding_count']}"
        )
    print(f"json={Path(args.json_out).resolve()}")
    print(f"html={Path(args.html_out).resolve()}")
    if saved_report["mode"] == "repository" and args.mapping_out:
        print(f"mapping={Path(args.mapping_out).resolve()}")
    if args.stdout_json:
        print(json.dumps(saved_report, ensure_ascii=False, indent=2))
    return {"PASS": 0, "REVIEW": 1, "BLOCKED": 2}[summary["gate_status"]]


if __name__ == "__main__":
    raise SystemExit(main())
