#!/usr/bin/env python3
"""Validate the static training-game catalog before publishing."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ASSET_PATTERN = re.compile(
    r'''["']([^"'\n]+/[^"'\n]+\.(?:css|gif|jpe?g|js|json|mp3|mp4|png|svg|ttf|wav|webp|woff2?))["']''',
    re.IGNORECASE,
)
CSS_URL_PATTERN = re.compile(
    r'''(?<![A-Za-z0-9_])url\(\s*(["']?)([^\s)"']+)\1\s*\)''', re.IGNORECASE
)
RISKY_NAMES = {"credentials.json", "secrets.json"}
RISKY_SUFFIXES = {".key", ".p12", ".pem"}


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: set[str] = set()
        self.cards: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        for key in ("href", "poster", "src", "data-src"):
            if values.get(key):
                self.references.add(values[key])
        for candidate in values.get("srcset", "").split(","):
            if candidate.strip():
                self.references.add(candidate.strip().split()[0])
        if tag == "a" and "card" in values.get("class", "").split():
            self.cards.append(values.get("href", ""))


def parse_args() -> argparse.Namespace:
    default_repo = Path(__file__).resolve().parents[4]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=default_repo)
    return parser.parse_args()


def exact_case_exists(repo: Path, target: Path) -> bool:
    try:
        parts = target.resolve().relative_to(repo.resolve()).parts
    except ValueError:
        return False
    current = repo.resolve()
    for part in parts:
        if not current.is_dir() or part not in os.listdir(current):
            return False
        current /= part
    return current.exists()


def local_target(repo: Path, page: Path, reference: str) -> tuple[Path | None, str | None]:
    value = reference.strip()
    if not value or value.startswith(("#", "//")):
        return None, None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None, None
    if value.startswith("/"):
        return None, f"{page.relative_to(repo)} uses root-relative URL: {value}"
    path_text = unquote(parsed.path)
    if not path_text or any(marker in path_text for marker in ("${", "{{", "<%")):
        return None, None
    target = (page.parent / path_text).resolve()
    if path_text.endswith("/"):
        target /= "index.html"
    return target, None


def changed_published_urls(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "HEAD", "--name-status", "--find-renames"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    errors: list[str] = []
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        status = fields[0]
        old_path = fields[1] if len(fields) > 1 else ""
        if status.startswith(("D", "R")) and re.fullmatch(r"[^/]+/index\.html", old_path):
            errors.append(f"published URL removed or renamed: {old_path.removesuffix('index.html')}")
    return errors


def validate(repo: Path) -> list[str]:
    errors: list[str] = []
    root_index = repo / "index.html"
    if not root_index.is_file():
        return ["root index.html is missing"]

    root_parser = ReferenceParser()
    root_parser.feed(root_index.read_text(encoding="utf-8"))
    cards = [card for card in root_parser.cards if card]
    if not cards:
        errors.append("root index.html has no game cards")
    if len(cards) != len(set(cards)):
        errors.append("root index.html contains duplicate game links")

    card_directories: set[Path] = set()
    for card in cards:
        target, message = local_target(repo, root_index, card)
        if message:
            errors.append(message)
        elif target:
            card_directories.add(target.parent)
            if not exact_case_exists(repo, target):
                errors.append(f"catalog target missing or wrong case: {card}")

    for child in repo.iterdir():
        if child.is_dir() and not child.name.startswith(".") and (child / "index.html").is_file():
            if child.resolve() not in card_directories:
                errors.append(f"game folder missing from root catalog: {child.name}/")

    for page in repo.rglob("*.html"):
        if ".git" in page.parts or ".agents" in page.parts:
            continue
        content = page.read_text(encoding="utf-8")
        parser = ReferenceParser()
        parser.feed(content)
        css_references = {match[1] for match in CSS_URL_PATTERN.findall(content)}
        references = parser.references | set(ASSET_PATTERN.findall(content)) | css_references
        for reference in sorted(references):
            target, message = local_target(repo, page, reference)
            if message:
                errors.append(message)
            elif target and not exact_case_exists(repo, target):
                errors.append(f"{page.relative_to(repo)} references missing path: {reference}")

    total_size = 0
    for path in repo.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        name = path.name.lower()
        if (name == ".env" or name.startswith(".env.")) and name != ".env.example":
            errors.append(f"public repository contains sensitive filename: {path.relative_to(repo)}")
        if name in RISKY_NAMES or path.suffix.lower() in RISKY_SUFFIXES:
            errors.append(f"public repository contains risky file: {path.relative_to(repo)}")
        size = path.stat().st_size
        total_size += size
        if size >= 100 * 1024 * 1024:
            errors.append(f"file reaches GitHub's 100 MiB limit: {path.relative_to(repo)}")
    if total_size > 1024 * 1024 * 1024:
        errors.append("published content exceeds the 1 GiB GitHub Pages limit")

    errors.extend(changed_published_urls(repo))
    return sorted(set(errors))


def main() -> int:
    repo = parse_args().repo.resolve()
    errors = validate(repo)
    if errors:
        print(f"FAILED: {len(errors)} validation error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: catalog, game entry points, local assets, public files, and URL stability validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
