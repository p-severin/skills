#!/usr/bin/env python3
"""Check skill layout, catalog, changelogs, relative links, and the Agent Skills spec.

skills-ref rejects the Claude Code field disable-model-invocation. The runtime
only reads that field at the top of SKILL.md, so this check removes that one
line in a temporary copy and runs skills-ref there. The real file keeps the
field. Any other non-spec field still fails.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}
ALLOWED_DIRS = {"references", "scripts", "assets"}
MODEL_INVOKED = {
    "plain-talk",
    "show-the-change",
    "web-scraping-references",
}
GROUPS = {
    "scraping": (
        "web-scraping-scout",
        "web-scraping-simple",
        "web-scraping-pipeline-design",
        "web-scraping-ops",
        "web-scraping-references",
        "scrapy-build",
        "scrapy-deploy",
        "crawlee-build",
    ),
    "engineering": (
        "hook-setup",
        "show-the-change",
        "project-statement",
        "mlflow-analyzer",
        "write-digica-readme",
    ),
    "learning": (
        "generate-flashcards",
        "anki-export",
        "kolbs-reflection",
    ),
    "productivity": (
        "obsidian-notes",
        "plain-talk",
    ),
}
GROUP_OF = {name: group for group, names in GROUPS.items() for name in names}
EXPECTED = [name for names in GROUPS.values() for name in names]
ROOT_DIRS = {".github", "docs", "scripts", "skills"}
ROOT_FILES = {"CHANGELOG.md", "LICENSE", "README.md", "decisions.tsv"}
TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
VERSION = re.compile(r"^## (\d+\.\d+\.\d+)\s*$", re.MULTILINE)
ROW = re.compile(
    r"^\| \[([a-z0-9-]+)\]\(skills/([a-z0-9-]+)/\1/SKILL\.md\) \| (\d+\.\d+\.\d+) \| (.+) \|$"
)


def token_count(text: str) -> int:
    return len(TOKEN.findall(text))


def skill_dirs() -> list[Path]:
    return [ROOT / "skills" / GROUP_OF[name] / name for name in EXPECTED]


def load_frontmatter(text: str) -> dict:
    match = FRONTMATTER.match(text)
    if match is None:
        raise ValueError("missing frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def check_layout(skill: Path, errors: list[str]) -> None:
    for path in skill.rglob("*"):
        rel = path.relative_to(skill)
        parts = rel.parts
        if path.is_dir():
            if len(parts) != 1 or parts[0] not in ALLOWED_DIRS:
                errors.append(f"{skill.name}: directory {rel} is outside references, scripts, and assets")
            continue
        if len(parts) == 1 and parts[0] not in {"SKILL.md", "CHANGELOG.md"}:
            errors.append(f"{skill.name}: loose file {rel}")
        elif len(parts) == 2 and parts[0] not in ALLOWED_DIRS:
            errors.append(f"{skill.name}: file {rel} is in the wrong directory")
        elif len(parts) > 2:
            errors.append(f"{skill.name}: nested file {rel}")


def check_skill(skill: Path, errors: list[str]) -> tuple[str, str]:
    text = (skill / "SKILL.md").read_text()
    lines = text.splitlines()
    if len(lines) >= 500:
        errors.append(f"{skill.name}: SKILL.md has {len(lines)} lines")
    try:
        meta = load_frontmatter(text)
    except ValueError as exc:
        errors.append(f"{skill.name}: {exc}")
        return "", ""

    extra = set(meta) - SPEC_FIELDS - {"disable-model-invocation"}
    if extra:
        errors.append(f"{skill.name}: unexpected frontmatter {sorted(extra)}")
    if meta.get("name") != skill.name:
        errors.append(f"{skill.name}: frontmatter name is {meta.get('name')!r}")

    description = meta.get("description")
    if not isinstance(description, str) or not description.startswith("Use when"):
        errors.append(f"{skill.name}: description must start with 'Use when'")

    disabled = meta.get("disable-model-invocation")
    if skill.name in MODEL_INVOKED:
        if "disable-model-invocation" in meta:
            errors.append(f"{skill.name}: model-invoked skill must not set disable-model-invocation")
    elif disabled is not True:
        errors.append(f"{skill.name}: disable-model-invocation must be true")

    metadata = meta.get("metadata")
    version = metadata.get("version") if isinstance(metadata, dict) else None
    if not isinstance(version, str):
        errors.append(f"{skill.name}: metadata.version must be a string")
        version = ""

    changelog = skill / "CHANGELOG.md"
    if not changelog.is_file():
        errors.append(f"{skill.name}: missing CHANGELOG.md")
        changelog_version = ""
    else:
        found = VERSION.search(changelog.read_text())
        changelog_version = found.group(1) if found else ""
        if changelog_version != version:
            errors.append(
                f"{skill.name}: changelog {changelog_version or 'missing'} != metadata.version {version}"
            )
    return version, description if isinstance(description, str) else ""


def check_tokens(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        count = token_count(text)
        if count > 5000:
            errors.append(f"{path.relative_to(ROOT)}: about {count} tokens")


def check_skills_ref(skill: Path, errors: list[str]) -> None:
    if shutil.which("skills-ref") is None:
        errors.append("skills-ref is not on PATH")
        return
    raw = (skill / "SKILL.md").read_text()
    stripped = re.sub(r"(?m)^disable-model-invocation:.*\n", "", raw)
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / skill.name
        dest.mkdir()
        (dest / "SKILL.md").write_text(stripped)
        proc = subprocess.run(
            ["skills-ref", "validate", str(dest)],
            check=False,
            capture_output=True,
            text=True,
        )
    if proc.returncode != 0:
        detail = (proc.stdout + proc.stderr).strip()
        errors.append(f"{skill.name}: skills-ref validate failed: {detail}")


def check_readme(versions: dict[str, str], descriptions: dict[str, str], errors: list[str]) -> None:
    current = None
    seen_groups: list[str] = []
    rows: list[tuple[str, str, str, str]] = []
    for line in (ROOT / "README.md").read_text().splitlines():
        heading = re.match(r"^## ([A-Za-z]+)\s*$", line)
        if heading:
            current = heading.group(1).lower()
            seen_groups.append(current)
            continue
        match = ROW.match(line)
        if match is None:
            continue
        name, group, version, description = match.groups()
        rows.append((name, group, version, description))
        if current != group:
            errors.append(f"README lists {name} under {current}, expected {group}")
    found = [name for name, _, _, _ in rows]
    if seen_groups != list(GROUPS):
        errors.append(f"README groups {seen_groups} != {list(GROUPS)}")
    if found != EXPECTED:
        errors.append(f"README skills {found} != catalog {EXPECTED}")
        return
    for name, group, version, description in rows:
        if group != GROUP_OF[name]:
            errors.append(f"README path for {name} uses group {group}")
        if version != versions.get(name):
            errors.append(f"README version for {name} is {version}, metadata is {versions.get(name)}")
        if description != descriptions.get(name):
            errors.append(f"README description for {name} does not match SKILL.md")


PORTABILITY_BANS = (
    (re.compile(r"declare\s+-A\b"), "associative arrays need bash 4"),
    (re.compile(r"\b(?:mapfile|readarray)\b"), "mapfile needs bash 4"),
    (re.compile(r"\$\{[^}\n]+,,\}|\$\{[^}\n]+\^\^\}"), "case modification needs bash 4"),
    (re.compile(r"\breadlink\b[^\n]*\s-f\b"), "readlink -f is not on BSD"),
    (re.compile(r"\bsed\b[^\n]*\s-i(?:\s|$)"), "sed -i without a BSD suffix"),
    (re.compile(r"\bfind\b[^\n]*\s-printf\b"), "find -printf is GNU only"),
    (re.compile(r"\bgrep\b[^\n]*\s(?:-P|--perl-regexp)\b"), "grep -P is GNU only"),
)


def portable_script_paths() -> list[Path]:
    paths = [path for path in ROOT.rglob("*.sh") if path.is_file() and ".git" not in path.parts]
    for skill in skill_dirs():
        scripts = skill / "scripts"
        if scripts.is_dir():
            paths.extend(path for path in scripts.rglob("*.py") if path.is_file())
    return paths


def check_portable_scripts(errors: list[str]) -> None:
    scripts = portable_script_paths()
    if not any(path.suffix == ".sh" for path in scripts):
        errors.append("expected at least one shell script for shellcheck")
        return
    for path in scripts:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for pattern, reason in PORTABILITY_BANS:
            if pattern.search(text):
                errors.append(f"{rel}: {reason}")


def check_ci(errors: list[str]) -> None:
    path = ROOT / ".github" / "workflows" / "validate-skills.yml"
    text = path.read_text()
    runs = re.findall(r"(?m)^    runs-on:\s*(\S+)\s*$", text)
    if runs != ["ubuntu-latest"]:
        errors.append(f"workflow runs-on must be ubuntu-latest only, found {runs}")
    if re.search(r"macos|windows", text, re.IGNORECASE):
        errors.append("workflow must not name macOS or Windows runners")
    if re.search(r"(?m)^strategy:\s*$|matrix:", text):
        errors.append("workflow must not use a matrix")


def check_tree(errors: list[str]) -> None:
    for child in ROOT.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir() and child.name not in ROOT_DIRS:
            errors.append(f"unexpected root directory {child.name}")
        elif child.is_file() and child.name not in ROOT_FILES:
            errors.append(f"unexpected root file {child.name}")
    for name in sorted(ROOT_FILES):
        if not (ROOT / name).is_file():
            errors.append(f"missing root file {name}")
    for name in (".github", "scripts", "skills"):
        if not (ROOT / name).is_dir():
            errors.append(f"missing root directory {name}")

    skills_root = ROOT / "skills"
    if not skills_root.is_dir():
        return
    found_groups = sorted(path.name for path in skills_root.iterdir() if path.is_dir())
    loose = sorted(path.name for path in skills_root.iterdir() if not path.is_dir())
    if loose:
        errors.append(f"unexpected files in skills/: {loose}")
    if found_groups != sorted(GROUPS):
        errors.append(f"skill groups {found_groups} != {sorted(GROUPS)}")
    for group, names in GROUPS.items():
        group_dir = skills_root / group
        if not group_dir.is_dir():
            continue
        found = sorted(path.name for path in group_dir.iterdir() if path.is_dir())
        group_loose = sorted(path.name for path in group_dir.iterdir() if not path.is_dir())
        if group_loose:
            errors.append(f"{group}: unexpected files {group_loose}")
        if found != sorted(names):
            errors.append(f"{group} skills {found} != {sorted(names)}")


def check_changelog(errors: list[str]) -> None:
    text = (ROOT / "CHANGELOG.md").read_text()
    if VERSION.search(text) is None:
        errors.append("CHANGELOG.md needs a ## x.y.z heading")


def check_license(errors: list[str]) -> None:
    text = (ROOT / "LICENSE").read_text()
    if not text.startswith("MIT License\n") or "Copyright (c) 2026 Patryk\n" not in text:
        errors.append("LICENSE is not the existing MIT license")


FENCE = re.compile(r"(?ms)^```.*?^```\n?")
MD_LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)")
CODE_PATH = re.compile(r"`([^`\n]+)`")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
EXTERNAL = ("http://", "https://", "mailto:", "ftp://")


def markdown_prose(text: str) -> str:
    return FENCE.sub("", text)


def heading_slugs(text: str) -> set[str]:
    counts: dict[str, int] = {}
    slugs: set[str] = set()
    for line in markdown_prose(text).splitlines():
        match = HEADING.match(line)
        if match is None:
            continue
        raw = re.sub(r"`+", "", match.group(2)).lower()
        slug = re.sub(r"[^\w\s-]", "", raw, flags=re.UNICODE)
        slug = re.sub(r"\s+", "-", slug).strip("-")
        if not slug:
            continue
        seen = counts.get(slug, 0)
        counts[slug] = seen + 1
        slugs.add(slug if seen == 0 else f"{slug}-{seen}")
    return slugs


CROSS_SKILL_PREFIXES = ("../", "references/")


def skill_path(token: str) -> str | None:
    path = token.split("#", 1)[0].split("?", 1)[0]
    if not path.endswith(".md"):
        return None
    if any(char in path for char in " <>*|"):
        return None
    if path.startswith(CROSS_SKILL_PREFIXES):
        return token
    return None


def check_one_link(source: Path, url: str, slugs: dict[Path, set[str]], errors: list[str]) -> None:
    root = ROOT.resolve()
    target_url, _, fragment = url.partition("#")
    if not target_url:
        destination = source.resolve()
    else:
        destination = (source.parent / target_url.split("?", 1)[0]).resolve()
        if root != destination and root not in destination.parents:
            errors.append(f"{source.relative_to(ROOT)}: link leaves the repo: {url}")
            return
        if not destination.is_file():
            errors.append(f"{source.relative_to(ROOT)}: link does not resolve: {url}")
            return
    if fragment and fragment not in slugs.get(destination, set()):
        errors.append(f"{source.relative_to(ROOT)}: missing heading #{fragment} in {url}")


def check_links(errors: list[str]) -> None:
    markdown = [
        path
        for path in ROOT.rglob("*.md")
        if path.is_file() and ".git" not in path.parts
    ]
    slugs = {
        path.resolve(): heading_slugs(path.read_text(encoding="utf-8")) for path in markdown
    }
    for path in markdown:
        prose = markdown_prose(path.read_text(encoding="utf-8"))
        for url in MD_LINK.findall(prose):
            if url.startswith(EXTERNAL) or url.startswith("//"):
                continue
            check_one_link(path, url, slugs, errors)
        for token in CODE_PATH.findall(prose):
            url = skill_path(token)
            if url is None or url.startswith(EXTERNAL):
                continue
            check_one_link(path, url, slugs, errors)


def main() -> int:
    errors: list[str] = []
    if (ROOT / ".claude-plugin").exists() or (ROOT / ".cursor-plugin").exists():
        errors.append("plugin manifest is not allowed")

    check_tree(errors)

    versions: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    for skill in skill_dirs():
        if not (skill / "SKILL.md").is_file():
            errors.append(f"{skill.name}: missing SKILL.md")
            continue
        check_layout(skill, errors)
        version, description = check_skill(skill, errors)
        versions[skill.name] = version
        descriptions[skill.name] = description
        check_skills_ref(skill, errors)

    check_tokens(errors)
    check_readme(versions, descriptions, errors)
    check_changelog(errors)
    check_license(errors)
    check_ci(errors)
    check_portable_scripts(errors)
    check_links(errors)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"ok {len(EXPECTED)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
