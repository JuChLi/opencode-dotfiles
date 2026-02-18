#!/usr/bin/env python3
"""
Extract a custom Python docstring style profile from a URL or local document.

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
    "docstring",
    "documentation",
    "summary",
    "first line",
    "parameters",
    "returns",
    "raises",
    "examples",
    "pep 257",
    "google style",
    "python",
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
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            data: 要處理的資料內容。
        """
        if data and data.strip():
            self.chunks.append(data)

    def text(self) -> str:
        """
        執行 text 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Returns:
            函式執行後回傳的結果。
        """
        return "\n".join(self.chunks)


def fetch_source_text(source: str, timeout: int = 20) -> str:
    """
    執行 fetch_source_text 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        source: 這個參數會影響函式的執行行為。
        timeout: 可接受的最長等待時間（秒）。
    
    Returns:
        函式執行後回傳的結果。
    
    Raises:
        FileNotFoundError: 當輸入不合法或處理失敗時拋出例外。
    """
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = urllib.request.Request(
            source,
            headers={"User-Agent": "pydoc-creator/1.0 (+style-extractor)"},
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
    """
    執行 normalize_line 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        line: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    line = html.unescape(line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def score_line(line: str) -> int:
    """
    執行 score_line 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        line: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    lower = line.lower()
    score = 0
    for keyword in KEYWORDS:
        if keyword in lower:
            score += 1
    if lower.startswith(("-", "*", "1.", "2.", "3.")):
        score += 1
    if 10 <= len(line) <= 240:
        score += 1
    return score


def extract_rules(text: str, max_rules: int) -> list[str]:
    """
    執行 extract_rules 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        text: 這個參數會影響函式的執行行為。
        max_rules: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    candidates: list[tuple[int, str]] = []
    seen: set[str] = set()

    for raw in text.splitlines():
        line = normalize_line(raw)
        if not line:
            continue
        if len(line) < 10 or len(line) > 260:
            continue

        line_score = score_line(line)
        if line_score < 2:
            continue

        line_key = line.lower()
        if line_key in seen:
            continue
        seen.add(line_key)
        candidates.append((line_score, line))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [line for _, line in candidates[:max_rules]]


def build_profile(name: str, source: str, extends: str, rules: list[str]) -> dict:
    """
    執行 build_profile 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        name: 這個參數會影響函式的執行行為。
        source: 這個參數會影響函式的執行行為。
        extends: 這個參數會影響函式的執行行為。
        rules: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    base = (extends or "pep257").lower()
    is_google = base == "google"

    return {
        "name": name,
        "extends": extends,
        "source": source,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "docstringFormat": "google" if is_google else "rest",
        "allowMissingDocstringForOverrides": is_google,
        "allowMissingModuleDocstringForTests": is_google,
        "enforceSummaryLineMaxLength": is_google,
        "summaryLineMaxLength": 80,
        "enforceGoogleSectionEntries": is_google,
        "enforceYieldsSectionForGenerators": is_google,
        "functionDetail": "說明此函式的主要流程、輸入限制與輸出語意。",
        "includeExamples": False,
        "requireGoogleExamples": False,
        "moduleSummary": "{module} 模組的主要功能。",
        "classSummary": "{name} 的核心行為實作。",
        "functionSummary": {
            "default": "執行 {name} 的核心流程並回傳結果。"
        },
        "paramDescriptions": {},
        "returnDescriptions": {
            "default": "函式回傳結果。"
        },
        "bannedPatterns": [],
        "notes": [
            "請根據 discoveredRules 補齊 functionSummary/paramDescriptions/returnDescriptions。",
            "可保留 extends=pep257，或改為 extends=google。",
            "若為 Google 風格，請確認 Returns/Yields/override 例外是否符合專案規範。",
        ],
        "discoveredRules": rules,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    """
    將輸入內容解析為可用資料。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        argv: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    parser = argparse.ArgumentParser(description="Extract custom Python docstring style profile")
    parser.add_argument("--name", required=True, help="profile name")
    parser.add_argument("--source", required=True, help="style guide URL or local file path")
    parser.add_argument("--output", required=True, help="output JSON path")
    parser.add_argument("--extends", default="pep257", help="base style profile (pep257/google)")
    parser.add_argument("--max-rules", type=int, default=40, help="maximum discovered rules to keep")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """
    執行 main 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        argv: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
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
