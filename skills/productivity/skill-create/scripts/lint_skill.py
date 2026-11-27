#!/usr/bin/env python3
"""Deterministic structural and quality linter for Agent Skills directories."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FENCE_RE = re.compile(r"(?ms)^```.*?^```\n?")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
MD_LINK_RE = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")
CODE_PATH_RE = re.compile(r"`([^`\n]+)`")
GOAL_HEADING_RE = re.compile(r"(?m)^##\s+Goal\s*$")
HEADING_RE = re.compile(r"(?m)^#{1,6}\s+.+$")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "#")
SUBDIRS = ("references", "scripts", "assets")

VAGUE_PHRASES = (
    (re.compile(r"\breasonably\b", re.IGNORECASE), "vague modifier 'reasonably' — replace with a concrete threshold"),
    (re.compile(r"\btasteful(?:ly)?\b", re.IGNORECASE), "vague modifier 'tasteful' — replace with concrete criteria"),
    (re.compile(r"\bwhere appropriate\b", re.IGNORECASE), "vague condition 'where appropriate' — state the exact condition"),
    (re.compile(r"\bas appropriate\b", re.IGNORECASE), "vague condition 'as appropriate' — state the exact condition"),
    (re.compile(r"\bhandle errors appropriately\b", re.IGNORECASE), "generic instruction — specify exact error handling"),
    (re.compile(r"\bfollow best practices\b", re.IGNORECASE), "generic instruction — name the exact rules"),
    (re.compile(r"\bbest practices\b", re.IGNORECASE), "vague phrase 'best practices' — replace with specific rules"),
    (re.compile(r"\btry to\b", re.IGNORECASE), "soft directive 'try to' — use a direct imperative"),
    (re.compile(r"\bif possible\b", re.IGNORECASE), "soft directive 'if possible' — state fallback condition explicitly"),
    (re.compile(r"\bas needed\b", re.IGNORECASE), "vague trigger 'as needed' — specify exact trigger condition"),
    (re.compile(r"\bbe thorough\b", re.IGNORECASE), "weak no-op 'be thorough' — state a checkable completion bound"),
)

BARE_POINTER_RE = re.compile(
    r"\b(?:see|check|read|consult)\s+(?:`?references/`?(?![A-Za-z0-9_.-])|the\s+references\s+(?:folder|directory)\b)",
    re.IGNORECASE,
)


@dataclass
class Finding:
    severity: str
    location: str
    message: str


def token_count(text: str) -> int:
    return len(TOKEN_RE.findall(text))


def parse_frontmatter_fallback(raw: str) -> dict:
    data: dict = {}
    current_parent: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  ") and current_parent is not None and ":" in line:
            k, v = line.strip().split(":", 1)
            val = v.strip().strip('"').strip("'")
            if isinstance(data.get(current_parent), dict):
                data[current_parent][k.strip()] = val
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            data[key] = {}
            current_parent = key
        else:
            current_parent = None
            if value == "true":
                data[key] = True
            elif value == "false":
                data[key] = False
            else:
                data[key] = value.strip('"').strip("'")
    return data


def load_frontmatter(text: str) -> tuple[dict | None, str | None]:
    match = FRONTMATTER_RE.match(text)
    if match is None:
        return None, "missing YAML frontmatter block (--- ... ---)"
    raw = match.group(1)
    if yaml is not None:
        try:
            parsed = yaml.safe_load(raw)
        except Exception as exc:  # noqa: BLE001
            return None, f"invalid YAML frontmatter: {exc}"
        if not isinstance(parsed, dict):
            return None, "frontmatter must be a YAML mapping"
        return parsed, None
    return parse_frontmatter_fallback(raw), None


def strip_fenced_blocks_preserving_lines(text: str) -> str:
    def _blank(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    return FENCE_RE.sub(_blank, text)


def check_frontmatter(skill_dir: Path, text: str, findings: list[Finding]) -> dict | None:
    meta, err = load_frontmatter(text)
    if err is not None or meta is None:
        findings.append(Finding("ERROR", "SKILL.md:1", err or "invalid frontmatter"))
        return None

    name = meta.get("name")
    if not isinstance(name, str) or not name:
        findings.append(Finding("ERROR", "SKILL.md", "frontmatter missing 'name'"))
    else:
        if not NAME_RE.match(name):
            findings.append(Finding("ERROR", "SKILL.md", f"invalid skill name '{name}' (use lowercase hyphen-case)"))
        if name != skill_dir.name:
            findings.append(Finding("ERROR", "SKILL.md", f"frontmatter name '{name}' != directory '{skill_dir.name}'"))

    description = meta.get("description")
    if not isinstance(description, str) or not description.strip():
        findings.append(Finding("ERROR", "SKILL.md", "frontmatter missing non-empty 'description'"))
    else:
        if len(description) > 1024:
            findings.append(Finding("ERROR", "SKILL.md", f"description has {len(description)} chars (max 1024)"))
        if meta.get("disable-model-invocation") is True and len(description) > 220:
            findings.append(
                Finding(
                    "WARN",
                    "SKILL.md",
                    f"user-invoked description is {len(description)} chars; trim to one concise human-facing sentence",
                )
            )
    return meta


def check_budgets_and_goal(skill_dir: Path, text: str, findings: list[Finding]) -> None:
    lines = text.splitlines()
    if len(lines) >= 500:
        findings.append(Finding("ERROR", "SKILL.md", f"{len(lines)} lines (must be < 500)"))

    tokens = token_count(text)
    if tokens > 5000:
        findings.append(Finding("ERROR", "SKILL.md", f"~{tokens} tokens (must be <= 5000)"))

    goal_match = GOAL_HEADING_RE.search(text)
    if goal_match is None:
        findings.append(Finding("ERROR", "SKILL.md", "missing '## Goal' section stating the single problem and outcome"))
    else:
        after_goal = text[goal_match.end() :]
        next_heading = HEADING_RE.search(after_goal)
        goal_body = after_goal[: next_heading.start()] if next_heading else after_goal
        non_empty = [ln for ln in goal_body.splitlines() if ln.strip()]
        if not non_empty:
            findings.append(Finding("ERROR", "SKILL.md", "'## Goal' section is empty"))
        elif len(non_empty) > 6:
            findings.append(
                Finding("WARN", "SKILL.md", f"'## Goal' has {len(non_empty)} lines; tighten to 1-2 sentences")
            )

    for md_path in sorted(skill_dir.rglob("*.md")):
        if md_path.name == "SKILL.md":
            continue
        rel = md_path.relative_to(skill_dir)
        sub_tokens = token_count(md_path.read_text(encoding="utf-8"))
        if sub_tokens > 5000:
            findings.append(Finding("WARN", str(rel), f"~{sub_tokens} tokens (consider splitting; limit is 5000)"))


def find_repo_root(start: Path) -> Path | None:
    for parent in (start, *start.parents):
        if (parent / ".git").exists():
            return parent
    return None


def extract_relative_refs(prose: str) -> tuple[list[str], list[str]]:
    md_links: list[str] = []
    code_refs: list[str] = []
    for url in MD_LINK_RE.findall(prose):
        if url.startswith(EXTERNAL_PREFIXES) or url.startswith("//"):
            continue
        cleaned = url.split("#", 1)[0].split("?", 1)[0]
        if cleaned:
            md_links.append(cleaned)
    for token in CODE_PATH_RE.findall(prose):
        cleaned = token.split("#", 1)[0].split("?", 1)[0]
        if not cleaned or cleaned.endswith("/"):
            continue
        if any(ch in cleaned for ch in " <>*|"):
            continue
        if cleaned.startswith(("references/", "scripts/", "assets/", "../")):
            code_refs.append(cleaned)
    return md_links, code_refs


def check_links_and_orphans(skill_dir: Path, findings: list[Finding]) -> None:
    md_files = sorted(skill_dir.rglob("*.md"))
    referenced: set[Path] = set()
    repo_root = find_repo_root(skill_dir)

    for md_file in md_files:
        rel_src = md_file.relative_to(skill_dir)
        text = md_file.read_text(encoding="utf-8")
        prose = strip_fenced_blocks_preserving_lines(text)
        md_links, code_refs = extract_relative_refs(prose)

        for target in md_links:
            dest = (md_file.parent / target).resolve()
            if not dest.exists():
                findings.append(Finding("ERROR", str(rel_src), f"broken relative link: {target}"))
            else:
                referenced.add(dest)

        for target in code_refs:
            candidates = [(md_file.parent / target).resolve(), (skill_dir / target).resolve()]
            if repo_root is not None and not target.startswith("../"):
                candidates.append((repo_root / target).resolve())
            existing = next((c for c in candidates if c.exists()), None)
            if existing is None:
                findings.append(Finding("ERROR", str(rel_src), f"broken relative reference: {target}"))
            else:
                referenced.add(existing)

    for sub in SUBDIRS:
        sub_dir = skill_dir / sub
        if not sub_dir.is_dir():
            continue
        for asset in sorted(sub_dir.rglob("*")):
            if not asset.is_file():
                continue
            if asset.resolve() not in referenced:
                rel = asset.relative_to(skill_dir)
                findings.append(
                    Finding(
                        "WARN",
                        str(rel),
                        "unreferenced file (add a conditional pointer in SKILL.md or delete sediment)",
                    )
                )


def check_prose_strictness(skill_dir: Path, findings: list[Finding]) -> None:
    md_files = [skill_dir / "SKILL.md"]
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        md_files.extend(sorted(refs_dir.glob("*.md")))

    for md_file in md_files:
        if not md_file.is_file():
            continue
        rel = md_file.relative_to(skill_dir)
        text = md_file.read_text(encoding="utf-8")
        prose = strip_fenced_blocks_preserving_lines(text)
        for idx, line in enumerate(prose.splitlines(), start=1):
            if not line.strip():
                continue
            cleaned = INLINE_CODE_RE.sub("", line)
            for pattern, reason in VAGUE_PHRASES:
                if pattern.search(cleaned):
                    findings.append(Finding("WARN", f"{rel}:{idx}", reason))
            line_without_quoted_phrases = INLINE_CODE_RE.sub(
                lambda m: "" if " " in m.group(0) else m.group(0), line
            )
            if BARE_POINTER_RE.search(line_without_quoted_phrases):
                findings.append(
                    Finding(
                        "WARN",
                        f"{rel}:{idx}",
                        "bare 'references/' pointer — name the exact file and the condition for loading it",
                    )
                )


def check_skills_ref(skill_dir: Path, findings: list[Finding]) -> None:
    if shutil.which("skills-ref") is None:
        findings.append(Finding("INFO", "skills-ref", "skills-ref not on PATH; skipped spec validator"))
        return
    raw = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    stripped = re.sub(r"(?m)^disable-model-invocation:.*\n", "", raw)
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / skill_dir.name
        dest.mkdir()
        (dest / "SKILL.md").write_text(stripped, encoding="utf-8")
        proc = subprocess.run(
            ["skills-ref", "validate", str(dest)],
            check=False,
            capture_output=True,
            text=True,
        )
    if proc.returncode != 0:
        detail = (proc.stdout + proc.stderr).strip()
        findings.append(Finding("ERROR", "skills-ref", f"spec validation failed: {detail}"))


def lint_skill(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [Finding("ERROR", str(skill_dir), "missing SKILL.md")]

    text = skill_md.read_text(encoding="utf-8")
    check_frontmatter(skill_dir, text, findings)
    check_budgets_and_goal(skill_dir, text, findings)
    check_links_and_orphans(skill_dir, findings)
    check_prose_strictness(skill_dir, findings)
    check_skills_ref(skill_dir, findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint an Agent Skills directory against structural and strictness rules.")
    parser.add_argument("skill_dir", type=Path, help="Path to the skill directory containing SKILL.md")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on WARN findings as well as ERROR")
    args = parser.parse_args()

    skill_dir = args.skill_dir.resolve()
    if not skill_dir.is_dir():
        print(f"ERROR {args.skill_dir}: directory does not exist", file=sys.stderr)
        return 1

    findings = lint_skill(skill_dir)
    errors = [f for f in findings if f.severity == "ERROR"]
    warns = [f for f in findings if f.severity == "WARN"]

    for item in findings:
        print(f"{item.severity:5s} {item.location}: {item.message}")

    summary = f"lint {skill_dir.name}: {len(errors)} errors, {len(warns)} warnings"
    print(summary)

    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
