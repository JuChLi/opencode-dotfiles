#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser


KEYWORDS = [
    "style",
    "documentation",
    "voice",
    "tone",
    "heading",
    "paragraph",
    "terminology",
    "consistency",
    "active voice",
    "second person",
    "readability",
    "tutorial",
    "how-to",
    "reference",
    "explanation",
]


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        if data and data.strip():
            self.chunks.append(data)

    def text(self) -> str:
        return "\n".join(self.chunks)


def fetch_source_text(source: str, timeout: int = 20) -> str:
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = urllib.request.Request(
            source,
            headers={"User-Agent": "doc-creator/1.0 (+style-extractor)"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
            charset_match = re.search(r"charset=([A-Za-z0-9_\-]+)", content_type)
            charset = charset_match.group(1) if charset_match else "utf-8"
            text = raw.decode(charset, errors="replace")

        if "<html" in text.lower() or "</" in text:
            parser = TextExtractor()
            parser.feed(text)
            text = parser.text()
        return html.unescape(text)

    path = pathlib.Path(source)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"source not found: {source}")
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_line(line: str) -> str:
    line = html.unescape(line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def score_line(line: str) -> int:
    lower = line.lower()
    score = 0
    for keyword in KEYWORDS:
        if keyword in lower:
            score += 1
    if lower.startswith(("-", "*", "1.", "2.", "3.")):
        score += 1
    if 12 <= len(line) <= 240:
        score += 1
    return score


def extract_rules(text: str, max_rules: int) -> list[str]:
    candidates: list[tuple[int, str]] = []
    seen: set[str] = set()

    for raw in text.splitlines():
        line = normalize_line(raw)
        if not line:
            continue
        if len(line) < 12 or len(line) > 260:
            continue

        line_score = score_line(line)
        if line_score < 2:
            continue

        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        candidates.append((line_score, line))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [line for _, line in candidates[:max_rules]]


def build_profile(name: str, source: str, extends: str, rules: list[str]) -> dict:
    return {
        "name": name,
        "extends": extends,
        "source": source,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "defaultDocType": "how-to",
        "structureRules": {},
        "terminologyRules": {
            "preferredTerms": {},
            "bannedPatterns": [],
        },
        "proseRules": {
            "discouragedPhrases": [],
            "genericHeadings": [],
        },
        "similarityRules": {},
        "notes": [
            "先確認 style source 是否為官方來源，再套用到團隊文件。",
            "請人工整理 discoveredRules，轉成可維護的結構與術語規則。",
            "若專案已有規範，請以專案規範優先，避免衝突。",
        ],
        "discoveredRules": rules,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract custom doc style profile from URL/file")
    parser.add_argument("--name", required=True, help="profile name")
    parser.add_argument("--source", required=True, help="style guide URL or local file path")
    parser.add_argument("--output", required=True, help="output JSON path")
    parser.add_argument("--extends", default="google-zhtw", help="base style profile")
    parser.add_argument("--max-rules", type=int, default=40, help="maximum discovered rules")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    text = fetch_source_text(args.source)
    rules = extract_rules(text, args.max_rules)
    profile = build_profile(args.name, args.source, args.extends, rules)

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Generated profile: {output_path}")
    print(f"Discovered rules: {len(rules)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
