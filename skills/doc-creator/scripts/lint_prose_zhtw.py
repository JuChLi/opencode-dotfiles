#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from style_profile_utils import collect_files_from_args, extract_headings, load_style_profile, normalize_heading


def _is_paragraph_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return False
    if stripped.startswith(">"):
        return False
    if stripped.startswith("|"):
        return False
    if re.match(r"^[-*+]\s+", stripped):
        return False
    if re.match(r"^\d+[.)]\s+", stripped):
        return False
    return True


def lint_files(files: list[Path], profile: dict) -> list[dict]:
    warnings: list[dict] = []
    prose_rules = profile.get("proseRules") or {}

    max_line_length = int(prose_rules.get("maxLineLength") or 120)
    max_paragraph_lines = int(prose_rules.get("maxParagraphLines") or 8)
    discouraged_phrases = [str(item) for item in (prose_rules.get("discouragedPhrases") or [])]
    generic_headings = {
        normalize_heading(str(item)) for item in (prose_rules.get("genericHeadings") or []) if str(item).strip()
    }

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        headings = extract_headings(text)

        previous_level = 0
        for line_number, level, heading_text, normalized in headings:
            if normalized in generic_headings:
                warnings.append(
                    {
                        "path": path,
                        "line": line_number,
                        "code": "GENERIC_HEADING",
                        "message": f"標題「{heading_text}」過於籠統，建議改為可描述內容的標題。",
                    }
                )

            if previous_level and level - previous_level > 1:
                warnings.append(
                    {
                        "path": path,
                        "line": line_number,
                        "code": "HEADING_LEVEL_JUMP",
                        "message": "標題層級跳太多（例如從 h2 直接跳到 h4），可讀性較差。",
                    }
                )
            previous_level = level

        in_code_block = False
        paragraph_start = 0
        paragraph_count = 0
        paragraph_warning_emitted = False

        def flush_paragraph() -> None:
            nonlocal paragraph_start, paragraph_count, paragraph_warning_emitted
            if paragraph_count > max_paragraph_lines and not paragraph_warning_emitted:
                warnings.append(
                    {
                        "path": path,
                        "line": paragraph_start,
                        "code": "PARAGRAPH_TOO_LONG",
                        "message": (
                            f"段落連續 {paragraph_count} 行，建議拆段。"
                            f"目前上限為 {max_paragraph_lines} 行。"
                        ),
                    }
                )
                paragraph_warning_emitted = True
            paragraph_start = 0
            paragraph_count = 0
            paragraph_warning_emitted = False

        for line_number, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if stripped.startswith("```"):
                flush_paragraph()
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            if len(line) > max_line_length and "http://" not in line and "https://" not in line:
                warnings.append(
                    {
                        "path": path,
                        "line": line_number,
                        "code": "LINE_TOO_LONG",
                        "message": f"單行長度 {len(line)}，建議不超過 {max_line_length}。",
                    }
                )

            for phrase in discouraged_phrases:
                if phrase and phrase in line:
                    warnings.append(
                        {
                            "path": path,
                            "line": line_number,
                            "code": "DISCOURAGED_PHRASE",
                            "message": f"發現建議避免的句型：「{phrase}」。",
                        }
                    )

            if _is_paragraph_line(line):
                if paragraph_count == 0:
                    paragraph_start = line_number
                paragraph_count += 1
                continue

            flush_paragraph()

        flush_paragraph()

    return warnings


def _print_warnings(warnings: list[dict]) -> None:
    for warning in warnings:
        print(
            f"WARN  {warning['path']}:{warning['line']} "
            f"[{warning['code']}] {warning['message']}"
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint zh-TW prose readability in markdown files")
    parser.add_argument("--root", default=".", help="root directory to scan")
    parser.add_argument("--style", default="google-zhtw", help="built-in style profile")
    parser.add_argument("--style-file", help="custom style profile JSON")
    parser.add_argument("--include", action="append", default=[], help="include glob (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="exclude glob (repeatable)")
    parser.add_argument("--strict", action="store_true", help="return non-zero when warnings exist")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    script_dir = Path(__file__).resolve().parent
    profile = load_style_profile(args.style, args.style_file, script_dir)

    files = collect_files_from_args(args, profile)
    if not files:
        print("No markdown files matched the current filters.")
        return 0

    warnings = lint_files(files, profile)
    if not warnings:
        print(f"PASS: prose lint passed for {len(files)} files.")
        return 0

    _print_warnings(warnings)
    print(f"WARN: prose lint found {len(warnings)} warning(s).")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
