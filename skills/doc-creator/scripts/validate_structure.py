#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from style_profile_utils import (
    collect_files_from_args,
    extract_headings,
    infer_doc_type,
    load_style_profile,
    normalize_heading,
)


def _matches_heading_group(heading_set: set[str], candidates: list[str]) -> bool:
    for candidate in candidates:
        for heading in heading_set:
            if heading == candidate or heading.startswith(candidate) or candidate in heading:
                return True
    return False


def validate_files(files: list[Path], profile: dict) -> list[dict]:
    issues: list[dict] = []
    structure_rules = profile.get("structureRules") or {}

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        headings = extract_headings(text)
        heading_set = {heading[3] for heading in headings}

        doc_type = infer_doc_type(path, text, profile)
        rule = structure_rules.get(doc_type) or {}

        for group in rule.get("requiredHeadingGroups") or []:
            normalized_group = [normalize_heading(str(item)) for item in group if str(item).strip()]
            if not normalized_group:
                continue
            if _matches_heading_group(heading_set, normalized_group):
                continue

            expected = " / ".join(str(item) for item in group)
            issues.append(
                {
                    "path": path,
                    "line": 1,
                    "code": "MISSING_HEADING",
                    "message": f"文件類型 {doc_type} 缺少必要章節：{expected}",
                }
            )

        min_heading_count = int(rule.get("minHeadingCount") or 0)
        if min_heading_count and len(headings) < min_heading_count:
            issues.append(
                {
                    "path": path,
                    "line": 1,
                    "code": "HEADING_COUNT",
                    "message": (
                        f"文件類型 {doc_type} 的標題數不足。"
                        f"目前 {len(headings)}，至少需要 {min_heading_count}。"
                    ),
                }
            )

    return issues


def _print_issues(issues: list[dict]) -> None:
    for issue in issues:
        print(
            f"ERROR {issue['path']}:{issue['line']} "
            f"[{issue['code']}] {issue['message']}"
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate markdown document structure")
    parser.add_argument("--root", default=".", help="root directory to scan")
    parser.add_argument("--style", default="google-zhtw", help="built-in style profile")
    parser.add_argument("--style-file", help="custom style profile JSON")
    parser.add_argument("--include", action="append", default=[], help="include glob (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="exclude glob (repeatable)")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    script_dir = Path(__file__).resolve().parent
    profile = load_style_profile(args.style, args.style_file, script_dir)

    files = collect_files_from_args(args, profile)
    if not files:
        print("No markdown files matched the current filters.")
        return 0

    issues = validate_files(files, profile)
    if not issues:
        print(f"PASS: structure validation passed for {len(files)} files.")
        return 0

    _print_issues(issues)
    print(f"FAIL: structure validation found {len(issues)} issue(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
