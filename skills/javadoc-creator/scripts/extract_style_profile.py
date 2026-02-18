#!/usr/bin/env python3
"""
Extract a custom Javadoc style profile from a URL or local document.

The generated JSON can be passed to:
  --style-file <profile.json>
for generate/refine/lint scripts.
"""

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
    "javadoc",
    "doc comment",
    "summary",
    "first sentence",
    "@param",
    "@return",
    "@throws",
    "@exception",
    "standard doclet",
    "doc comment specification",
    "style",
    "documentation",
    "api",
    "comment",
]


class TextExtractor(HTMLParser):
    """
    TextExtractor 的核心行為實作。
    
    說明此類別管理的狀態、核心流程與建議使用方式。
    """
    def __init__(self) -> None:
        """
        初始化 __init__ 所需的狀態。
        
        說明此函式的主要流程、輸入限制與輸出語意。
        """
        super().__init__()
        self.chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        """
        執行 handle_data 的核心流程並回傳結果。
        
        說明此函式的主要流程、輸入限制與輸出語意。
        
        :param data: 待處理資料。
        """
        if data and data.strip():
            self.chunks.append(data)

    def text(self) -> str:
        """
        執行 text 的核心流程並回傳結果。
        
        說明此函式的主要流程、輸入限制與輸出語意。
        
        :returns: 函式回傳結果。
        """
        return "\n".join(self.chunks)


def fetch_source_text(source: str, timeout: int = 20) -> str:
    """
    執行 fetch_source_text 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param source: 此參數會影響函式的執行行為。
    :param timeout: 逾時時間（秒）。
    :returns: 函式回傳結果。
    :raises FileNotFoundError: 當輸入不合法或處理失敗時拋出。
    """
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = urllib.request.Request(
            source,
            headers={"User-Agent": "javadoc-creator/1.0 (+style-extractor)"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
            charset_match = re.search(r"charset=([A-Za-z0-9_\-]+)", content_type)
            charset = charset_match.group(1) if charset_match else "utf-8"
            text = raw.decode(charset, errors="replace")

        # If likely HTML, strip tags.
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
    """
    執行 normalize_line 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param line: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    line = html.unescape(line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def score_line(line: str) -> int:
    """
    執行 score_line 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param line: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    lower = line.lower()
    score = 0
    for keyword in KEYWORDS:
        if keyword in lower:
            score += 1
    if lower.startswith(("-", "*", "1.", "2.", "3.")):
        score += 1
    if 10 <= len(line) <= 220:
        score += 1
    return score


def extract_rules(text: str, max_rules: int) -> list[str]:
    """
    執行 extract_rules 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param text: 此參數會影響函式的執行行為。
    :param max_rules: 此參數會影響函式的執行行為。
    :returns: 結果集合。
    """
    candidates: list[tuple[int, str]] = []
    seen: set[str] = set()

    for raw in text.splitlines():
        line = normalize_line(raw)
        if not line:
            continue
        if len(line) < 10 or len(line) > 240:
            continue

        line_score = score_line(line)
        if line_score < 2:
            continue

        line_key = line.lower()
        if line_key in seen:
            continue
        seen.add(line_key)
        candidates.append((line_score, line))

    # Keep stable ordering by score desc then original order.
    candidates.sort(key=lambda item: item[0], reverse=True)
    return [line for _, line in candidates[:max_rules]]


def build_profile(name: str, source: str, extends: str, rules: list[str]) -> dict:
    """
    建立目標資料結構。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param name: 此參數會影響函式的執行行為。
    :param source: 此參數會影響函式的執行行為。
    :param extends: 此參數會影響函式的執行行為。
    :param rules: 此參數會影響函式的執行行為。
    :returns: 結果集合。
    """
    return {
        "name": name,
        "extends": extends,
        "source": source,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "docletSpec": {
            "source": "https://docs.oracle.com/en/java/javase/21/docs/specs/javadoc/doc-comment-spec.html",
            "enforceSummarySentence": True,
            "enforceTagOrder": True,
            "tagOrder": ["param", "return", "throws"],
            "requireParamTags": True,
            "requireReturnTagForNonVoid": True,
            "forbidReturnTagForVoidOrConstructor": True,
            "requireDeclaredThrowsTags": True,
        },
        "methodSummary": {},
        "paramDescriptions": {},
        "returnDescriptions": {},
        "bannedPatterns": [],
        "notes": [
            "先符合 Documentation Comment Specification for the Standard Doclet。",
            "請根據 discoveredRules 補齊 methodSummary/paramDescriptions/returnDescriptions。",
            "可保留 extends=vertx，或改為 extends=apache/google。",
        ],
        "discoveredRules": rules,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    """
    解析輸入內容。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param argv: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    parser = argparse.ArgumentParser(description="Extract custom Javadoc style profile")
    parser.add_argument("--name", required=True, help="profile name")
    parser.add_argument("--source", required=True, help="style guide URL or local file path")
    parser.add_argument("--output", required=True, help="output JSON path")
    parser.add_argument("--extends", default="vertx", help="base style profile (vertx/apache/google)")
    parser.add_argument("--max-rules", type=int, default=40, help="maximum discovered rules to keep")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """
    執行 main 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param argv: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    args = parse_args(argv)

    text = fetch_source_text(args.source)
    rules = extract_rules(text, args.max_rules)
    profile = build_profile(args.name, args.source, args.extends, rules)

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Style profile extracted")
    print(f"Name: {args.name}")
    print(f"Source: {args.source}")
    print(f"Rules captured: {len(rules)}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:  # noqa: BLE001
        print(f"[extract_style_profile] {exc}", file=sys.stderr)
        raise SystemExit(1)
