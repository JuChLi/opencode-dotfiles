#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

from javadoc_utils import (
    collect_method_signature,
    find_insertion_index,
    has_javadoc,
    is_method_declaration,
    is_method_start_line,
    is_type_declaration,
    list_java_files,
    parse_args,
    relative_path,
    resolve_root,
)
from style_profile_utils import load_style_profile, normalize_banned_patterns


def scan_quality(file_path, root, include_private, banned_patterns):
    content = Path(file_path).read_text(encoding="utf-8")
    lines = re.split(r"\r?\n", content)
    issues = []

    i = 0
    while i < len(lines):
        trimmed = lines[i].strip()

        if is_type_declaration(lines[i]):
            if not has_javadoc(lines, i):
                issues.append(
                    {
                        "file": relative_path(file_path, root),
                        "line": i + 1,
                        "kind": "missing-javadoc",
                        "detail": "類別/介面/列舉缺少 Javadoc。",
                    }
                )
            i += 1
            continue

        if is_method_start_line(lines[i], include_private):
            collected = collect_method_signature(lines, i)
            if is_method_declaration(collected["signature"], include_private):
                insertion_index = find_insertion_index(lines, i)
                if not has_javadoc(lines, insertion_index):
                    issues.append(
                        {
                            "file": relative_path(file_path, root),
                            "line": i + 1,
                            "kind": "missing-javadoc",
                            "detail": "方法缺少 Javadoc。",
                        }
                    )
            i = collected["end_index"] + 1
            continue

        for rule in banned_patterns:
            if rule["regex"].search(trimmed):
                issues.append(
                    {
                        "file": relative_path(file_path, root),
                        "line": i + 1,
                        "kind": "weak-text",
                        "detail": f"{trimmed} ({rule['reason']})",
                        "pattern": rule["pattern"],
                    }
                )

        i += 1

    return issues


def main():
    args = parse_args(sys.argv[1:])
    root = resolve_root(args.root)
    profile = load_style_profile(args, Path(__file__).resolve().parent)
    banned_patterns = normalize_banned_patterns(profile)
    files = list_java_files(root)

    issues = []
    for file_path in files:
        issues.extend(scan_quality(file_path, root, args.include_private, banned_patterns))

    summary = {
        "root": root,
        "style": profile.get("name") or args.style,
        "styleSource": profile.get("source"),
        "includePrivate": args.include_private,
        "scannedFiles": len(files),
        "issueCount": len(issues),
        "issues": issues,
    }

    if args.json:
        sys.stdout.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write("Javadoc quality lint\n")
        sys.stdout.write(f"Root: {summary['root']}\n")
        sys.stdout.write(f"Style: {summary['style']}\n")
        sys.stdout.write(f"Style source: {summary['styleSource']}\n")
        sys.stdout.write(f"Scanned files: {summary['scannedFiles']}\n")
        sys.stdout.write(f"Issues: {summary['issueCount']}\n")

        if issues:
            sys.stdout.write("\nIssue details:\n")
            for issue in issues[:200]:
                sys.stdout.write(
                    f"- {issue['file']}:{issue['line']} [{issue['kind']}] {issue['detail']}\n"
                )
            if len(issues) > 200:
                sys.stdout.write(f"... {len(issues) - 200} more issues\n")

    if issues:
        raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"[lint_javadocs] {error}\n")
        raise SystemExit(1)
