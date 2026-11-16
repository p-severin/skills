#!/usr/bin/env python3
"""Copy one fenced template from references/templates.md into a directory.

The script writes the files that section already contains. It does not invent
files that the reference only names in a tree diagram.

Running it again is safe. A file that already matches is left in place. A file
that exists with different content stops the run.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_MD = SKILL_ROOT / "references" / "templates.md"

SECTIONS = {
    "single-file": "Single-File Template",
    "router": "Single-File with Router (multiple page types)",
    "modular": "Modular Project Structure",
}

FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
FILE_BLOCK = re.compile(
    r"^### (?P<path>[^\n]+)\n+```[^\n]*\n(?P<body>.*?)```",
    re.MULTILINE | re.DOTALL,
)


def section_body(text: str, title: str) -> str:
    parts = re.split(r"(?m)^## ", text)
    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        if heading.strip() == title:
            return body
    raise SystemExit(f"section not found in {TEMPLATES_MD.name}: {title}")


def as_text(body: str) -> str:
    if body.endswith("\n"):
        return body
    return body + "\n"


def files_for(template: str, text: str) -> dict[str, str]:
    body = section_body(text, SECTIONS[template])
    if template in {"single-file", "router"}:
        match = re.search(r"```python\n(.*?)```", body, re.DOTALL)
        if match is None:
            raise SystemExit(f"{template} has no python fence")
        return {"crawler.py": as_text(match.group(1))}

    files: dict[str, str] = {}
    for match in FILE_BLOCK.finditer(body):
        rel = match.group("path").strip()
        if " " in rel or rel.startswith("/") or rel.startswith(".."):
            continue
        files[rel] = as_text(match.group("body"))
    if not files:
        raise SystemExit("modular section has no file blocks")
    return files


def destination(dest: Path, rel: str) -> Path:
    root = dest.resolve()
    path = (root / rel).resolve()
    if path != root and root not in path.parents:
        raise SystemExit(f"refusing path outside destination: {rel}")
    return path


def apply_files(dest: Path, files: dict[str, str]) -> list[str]:
    written: list[str] = []
    for rel, content in files.items():
        path = destination(dest, rel)
        if path.exists():
            current = path.read_text()
            if current != content:
                raise SystemExit(f"{path} already exists with different content")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        written.append(rel)
    return written


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template",
        required=True,
        choices=sorted(SECTIONS),
    )
    parser.add_argument("--dest", type=Path, required=True)
    args = parser.parse_args(argv)

    text = TEMPLATES_MD.read_text()
    files = files_for(args.template, text)
    args.dest.mkdir(parents=True, exist_ok=True)
    written = apply_files(args.dest, files)
    if written:
        print("\n".join(written))
    else:
        print("unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
