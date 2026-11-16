#!/usr/bin/env python3
"""Print plain text from a URL or a local file.

HTML is reduced to text. A PDF is read with pdftotext or pypdf when one of
those is available. The card wording stays with the agent. This script only
fetches and extracts.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

USER_AGENT = "generate-flashcards/1.0"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip += 1
        if tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "section"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1
        if tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "section"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip == 0:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    lines = [" ".join(part.split()) for part in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line) + "\n"


def looks_like_html(text: str, content_type: str) -> bool:
    if "html" in content_type.lower():
        return True
    start = text.lstrip()[:200].lower()
    return start.startswith("<!doctype html") or start.startswith("<html") or "<body" in start


def decode_body(raw: bytes, content_type: str) -> str:
    charset = "utf-8"
    for piece in content_type.split(";"):
        piece = piece.strip()
        if piece.lower().startswith("charset="):
            charset = piece.split("=", 1)[1].strip() or charset
    return raw.decode(charset, errors="replace")


def fetch_url(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
    except urllib.error.URLError as exc:
        raise SystemExit(f"fetch failed: {exc}") from exc
    text = decode_body(raw, content_type)
    if looks_like_html(text, content_type):
        return html_to_text(text)
    if not text.endswith("\n"):
        text += "\n"
    return text


def pdf_text(path: Path) -> str:
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        result = subprocess.run(
            [pdftotext, "-layout", str(path), "-"],
            check=False,
            capture_output=True,
        )
        if result.returncode == 0:
            text = result.stdout.decode("utf-8", errors="replace")
            return text if text.endswith("\n") else text + "\n"
    try:
        from pypdf import PdfReader
    except ImportError:
        raise SystemExit(
            "PDF text extract needs pdftotext or the pypdf package"
        ) from None
    reader = PdfReader(str(path))
    parts = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(part.strip() for part in parts if part.strip())
    return text + "\n"


def file_text(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"not a file: {path}")
    if path.suffix.lower() == ".pdf":
        return pdf_text(path)
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    if path.suffix.lower() in {".html", ".htm"} or looks_like_html(text, ""):
        return html_to_text(text)
    if not text.endswith("\n"):
        text += "\n"
    return text


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        help="http(s) URL or local file path",
    )
    args = parser.parse_args(argv)
    source = args.source
    if source.startswith("http://") or source.startswith("https://"):
        sys.stdout.write(fetch_url(source))
        return 0
    sys.stdout.write(file_text(Path(source).expanduser()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
