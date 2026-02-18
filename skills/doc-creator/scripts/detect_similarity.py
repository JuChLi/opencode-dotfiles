#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from itertools import combinations
from pathlib import Path

from style_profile_utils import collect_files_from_args, load_style_profile


def _strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :])
    return text


def _build_line_set(text: str, min_line_length: int) -> set[str]:
    cleaned = _strip_frontmatter(text)
    in_code_block = False
    line_set: set[str] = set()

    for raw_line in cleaned.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not stripped or stripped.startswith("#"):
            continue

        normalized = re.sub(r"\s+", " ", stripped).strip().lower()
        if len(normalized) < min_line_length:
            continue
        line_set.add(normalized)

    return line_set


def _content_hash(text: str) -> str:
    cleaned = _strip_frontmatter(text)
    normalized_lines: list[str] = []
    in_code_block = False

    for raw_line in cleaned.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not stripped:
            continue
        normalized_lines.append(re.sub(r"\s+", " ", stripped).strip().lower())

    payload = "\n".join(normalized_lines).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def detect_similar_files(
    files: list[Path],
    profile: dict,
    threshold_override: float | None = None,
) -> list[dict]:
    rules = profile.get("similarityRules") or {}
    threshold = float(threshold_override if threshold_override is not None else rules.get("similarityThreshold", 0.9))
    min_line_length = int(rules.get("minLineLength") or 12)

    snapshots: list[dict] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        snapshots.append(
            {
                "path": path,
                "lineSet": _build_line_set(text, min_line_length),
                "hash": _content_hash(text),
            }
        )

    issues: list[dict] = []
    for left, right in combinations(snapshots, 2):
        left_set = left["lineSet"]
        right_set = right["lineSet"]
        if not left_set and not right_set:
            continue

        exact_duplicate = left["hash"] == right["hash"]
        if exact_duplicate:
            similarity = 1.0
        else:
            union_size = len(left_set | right_set)
            if union_size == 0:
                continue
            similarity = len(left_set & right_set) / union_size

        if similarity < threshold:
            continue

        issues.append(
            {
                "pathA": left["path"],
                "pathB": right["path"],
                "score": similarity,
                "exact": exact_duplicate,
                "code": "DUPLICATE" if exact_duplicate else "HIGH_SIMILARITY",
            }
        )

    return issues


def _print_issues(issues: list[dict]) -> None:
    for issue in issues:
        print(
            f"WARN  {issue['pathA']} <-> {issue['pathB']} "
            f"[{issue['code']}] score={issue['score']:.3f}"
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect duplicate or highly similar markdown files")
    parser.add_argument("--root", default=".", help="root directory to scan")
    parser.add_argument("--style", default="google-zhtw", help="built-in style profile")
    parser.add_argument("--style-file", help="custom style profile JSON")
    parser.add_argument("--include", action="append", default=[], help="include glob (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="exclude glob (repeatable)")
    parser.add_argument("--threshold", type=float, help="override similarity threshold")
    parser.add_argument("--strict", action="store_true", help="return non-zero when matches exist")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    script_dir = Path(__file__).resolve().parent
    profile = load_style_profile(args.style, args.style_file, script_dir)

    files = collect_files_from_args(args, profile)
    if not files:
        print("No markdown files matched the current filters.")
        return 0

    issues = detect_similar_files(files, profile, args.threshold)
    if not issues:
        print(f"PASS: similarity scan passed for {len(files)} files.")
        return 0

    _print_issues(issues)
    print(f"WARN: similarity scan found {len(issues)} match(es).")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
