#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from style_profile_utils import collect_files_from_args, load_style_profile


def _compile_banned_patterns(raw_patterns: list) -> list[tuple[re.Pattern[str], str, str]]:
    compiled: list[tuple[re.Pattern[str], str, str]] = []
    for item in raw_patterns:
        if isinstance(item, dict):
            pattern = str(item.get("pattern") or "").strip()
            reason = str(item.get("reason") or "").strip()
        else:
            pattern = str(item).strip()
            reason = ""

        if not pattern:
            continue

        try:
            compiled.append((re.compile(pattern), reason, pattern))
        except re.error:
            compiled.append((re.compile(re.escape(pattern)), reason, pattern))
    return compiled


def check_files(files: list[Path], profile: dict) -> list[dict]:
    issues: list[dict] = []
    terminology_rules = profile.get("terminologyRules") or {}
    preferred_terms = terminology_rules.get("preferredTerms") or {}
    banned_patterns = _compile_banned_patterns(terminology_rules.get("bannedPatterns") or [])

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        in_code_block = False

        for line_number, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            for preferred, alternatives in preferred_terms.items():
                for alternative in alternatives or []:
                    alt = str(alternative)
                    if not alt or alt == preferred:
                        continue
                    if alt in line:
                        issues.append(
                            {
                                "path": path,
                                "line": line_number,
                                "code": "TERM_PREFERRED",
                                "message": (
                                    f"發現詞彙「{alt}」，建議改用「{preferred}」以維持一致性。"
                                ),
                            }
                        )

            for regex, reason, pattern in banned_patterns:
                if not regex.search(line):
                    continue
                reason_suffix = f" 原因：{reason}" if reason else ""
                issues.append(
                    {
                        "path": path,
                        "line": line_number,
                        "code": "TERM_BANNED",
                        "message": f"符合禁用模式 `{pattern}`。{reason_suffix}".strip(),
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
    parser = argparse.ArgumentParser(description="Check terminology consistency in markdown files")
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

    issues = check_files(files, profile)
    if not issues:
        print(f"PASS: terminology validation passed for {len(files)} files.")
        return 0

    _print_issues(issues)
    print(f"FAIL: terminology validation found {len(issues)} issue(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
