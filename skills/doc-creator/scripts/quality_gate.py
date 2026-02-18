#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from check_terminology import check_files
from detect_similarity import detect_similar_files
from lint_prose_zhtw import lint_files
from style_profile_utils import collect_files_from_args, load_style_profile
from validate_structure import validate_files


def _print_section(title: str, items: list[dict], max_details: int) -> None:
    if not items:
        return
    print(f"\n[{title}] {len(items)} issue(s)")
    for item in items[:max_details]:
        if "pathA" in item:
            print(
                f"- {item['pathA']} <-> {item['pathB']} "
                f"[{item['code']}] score={item['score']:.3f}"
            )
            continue
        print(f"- {item['path']}:{item['line']} [{item['code']}] {item['message']}")
    if len(items) > max_details:
        print(f"- ... and {len(items) - max_details} more")


def _to_serializable(items: list[dict]) -> list[dict]:
    serializable: list[dict] = []
    for item in items:
        mapped: dict = {}
        for key, value in item.items():
            if isinstance(value, Path):
                mapped[key] = str(value)
            else:
                mapped[key] = value
        serializable.append(mapped)
    return serializable


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full markdown documentation quality gate")
    parser.add_argument("--root", default=".", help="root directory to scan")
    parser.add_argument("--style", default="google-zhtw", help="built-in style profile")
    parser.add_argument("--style-file", help="custom style profile JSON")
    parser.add_argument("--include", action="append", default=[], help="include glob (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="exclude glob (repeatable)")
    parser.add_argument("--strict", action="store_true", help="promote warnings to failures")
    parser.add_argument("--threshold", type=float, help="override similarity threshold")
    parser.add_argument("--max-details", type=int, default=20, help="max items per category to print")
    parser.add_argument("--report-json", help="write summary report to JSON file")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    script_dir = Path(__file__).resolve().parent
    profile = load_style_profile(args.style, args.style_file, script_dir)

    files = collect_files_from_args(args, profile)
    if not files:
        print("No markdown files matched the current filters.")
        return 0

    structure_issues = validate_files(files, profile)
    terminology_issues = check_files(files, profile)
    prose_warnings = lint_files(files, profile)
    similarity_warnings = detect_similar_files(files, profile, args.threshold)

    hard_fail_count = len(structure_issues) + len(terminology_issues)
    warning_count = len(prose_warnings) + len(similarity_warnings)

    print("Doc Creator Quality Gate")
    print(f"- Scanned files: {len(files)}")
    print(f"- Style profile: {profile.get('name')} ({profile.get('source')})")
    print(f"- Structure errors: {len(structure_issues)}")
    print(f"- Terminology errors: {len(terminology_issues)}")
    print(f"- Prose warnings: {len(prose_warnings)}")
    print(f"- Similarity warnings: {len(similarity_warnings)}")

    _print_section("Structure", structure_issues, args.max_details)
    _print_section("Terminology", terminology_issues, args.max_details)
    _print_section("Prose", prose_warnings, args.max_details)
    _print_section("Similarity", similarity_warnings, args.max_details)

    passed = hard_fail_count == 0 and (warning_count == 0 or not args.strict)

    if args.report_json:
        report_path = Path(args.report_json)
        report = {
            "root": str(Path(args.root).resolve()),
            "style": profile.get("name"),
            "styleSource": profile.get("source"),
            "scannedFiles": len(files),
            "strict": bool(args.strict),
            "hardFailCount": hard_fail_count,
            "warningCount": warning_count,
            "passed": passed,
            "issues": {
                "structure": _to_serializable(structure_issues),
                "terminology": _to_serializable(terminology_issues),
                "prose": _to_serializable(prose_warnings),
                "similarity": _to_serializable(similarity_warnings),
            },
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"- JSON report: {report_path}")

    if passed:
        if warning_count:
            print("PASS with warnings: hard-fail checks passed.")
        else:
            print("PASS: all checks passed.")
        return 0

    if args.strict and warning_count and hard_fail_count == 0:
        print("FAIL: strict mode enabled and warnings were found.")
    else:
        print("FAIL: hard-fail checks failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
