#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pydoc_utils import (
    collect_doc_targets,
    list_python_files,
    parse_args,
    parse_python_source,
    relative_path,
    resolve_root,
    split_lines,
)
from style_profile_utils import (
    choose_return_description,
    load_style_profile,
    normalize_banned_patterns,
    normalize_param_name,
)


def first_summary_line(docstring: str) -> str:
    for line in docstring.splitlines():
        text = line.strip()
        if text:
            return text
    return ""


def has_detail_description(docstring: str) -> bool:
    summary_seen = False
    for raw in docstring.splitlines():
        text = raw.strip()
        if not text:
            continue

        if not summary_seen:
            summary_seen = True
            continue

        if text in {"Args:", "Returns:", "Raises:", "Examples:"}:
            return False
        if text.startswith(":param") or text.startswith(":return") or text.startswith(":returns") or text.startswith(":raises"):
            return False
        return True

    return False


def has_google_heading(docstring: str, heading: str) -> bool:
    return re.search(rf"(?m)^\s*{re.escape(heading)}\s*$", docstring) is not None


def has_rest_param(docstring: str, param_name: str) -> bool:
    return re.search(rf"(?m)^\s*:param\s+{re.escape(param_name)}\s*:", docstring) is not None


def has_rest_returns(docstring: str) -> bool:
    return re.search(r"(?m)^\s*:returns?\s*:", docstring) is not None


def has_rest_raises(docstring: str, exc_name: str) -> bool:
    return re.search(rf"(?m)^\s*:raises\s+{re.escape(exc_name)}\s*:", docstring) is not None


def collect_structure_issues(target, rel: str, profile: dict) -> list[dict]:
    issues = []
    docstring = target.docstring or ""
    base_line = target.doc_start_line or target.lineno

    if not has_detail_description(docstring):
        issues.append(
            {
                "file": rel,
                "line": base_line,
                "kind": "missing-detail",
                "detail": "docstring 缺少摘要後的詳細描述段落。",
            }
        )

    if target.kind not in {"function", "method"}:
        return issues

    doc_format = (profile.get("docstringFormat") or "rest").lower()
    return_text = choose_return_description(profile, target)

    if doc_format == "google":
        if target.params and not has_google_heading(docstring, "Args:"):
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "missing-args",
                    "detail": "Google style 需提供 Args 區段。",
                }
            )

        if return_text and not has_google_heading(docstring, "Returns:"):
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "missing-returns",
                    "detail": "Google style 需提供 Returns 區段。",
                }
            )

        if target.raises and not has_google_heading(docstring, "Raises:"):
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "missing-raises",
                    "detail": "Google style 需提供 Raises 區段。",
                }
            )

        if profile.get("includeExamples") and not has_google_heading(docstring, "Examples:"):
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "missing-examples",
                    "detail": "Google style 需提供 Examples 區段。",
                }
            )

        return issues

    for param in target.params:
        normalized = normalize_param_name(param)
        if has_rest_param(docstring, normalized):
            continue
        issues.append(
            {
                "file": rel,
                "line": base_line,
                "kind": "missing-param-field",
                "detail": f"PEP 257/reST 風格缺少 :param {normalized}: 欄位。",
            }
        )

    if return_text and not has_rest_returns(docstring):
        issues.append(
            {
                "file": rel,
                "line": base_line,
                "kind": "missing-returns-field",
                "detail": "PEP 257/reST 風格缺少 :returns: 欄位。",
            }
        )

    for exc in target.raises:
        if has_rest_raises(docstring, exc):
            continue
        issues.append(
            {
                "file": rel,
                "line": base_line,
                "kind": "missing-raises-field",
                "detail": f"PEP 257/reST 風格缺少 :raises {exc}: 欄位。",
            }
        )

    return issues


def scan_quality(file_path: str, root: str, include_private: bool, profile: dict, banned_patterns: list[dict]) -> list[dict]:
    raw, tree = parse_python_source(file_path)
    lines = split_lines(raw)
    targets = collect_doc_targets(raw, tree, file_path, include_private)

    issues = []
    rel = relative_path(file_path, root)

    for target in targets:
        if not target.has_docstring:
            issues.append(
                {
                    "file": rel,
                    "line": target.lineno,
                    "kind": "missing-docstring",
                    "detail": f"{target.kind} 缺少 docstring。",
                }
            )
            continue

        if not target.docstring:
            issues.append(
                {
                    "file": rel,
                    "line": target.lineno,
                    "kind": "empty-docstring",
                    "detail": "docstring 內容為空。",
                }
            )
            continue

        summary = first_summary_line(target.docstring)
        if not summary:
            issues.append(
                {
                    "file": rel,
                    "line": target.doc_start_line or target.lineno,
                    "kind": "missing-summary",
                    "detail": "docstring 缺少摘要首句。",
                }
            )
        elif not summary.endswith(("。", ".", "!", "！", "?", "？")):
            issues.append(
                {
                    "file": rel,
                    "line": target.doc_start_line or target.lineno,
                    "kind": "summary-punctuation",
                    "detail": "摘要首句建議以句號收尾。",
                }
            )

        issues.extend(collect_structure_issues(target, rel, profile))

        if target.doc_start_line is None or target.doc_end_line is None:
            continue

        for line_no in range(target.doc_start_line, target.doc_end_line + 1):
            if line_no < 1 or line_no > len(lines):
                continue
            text = lines[line_no - 1].strip()
            for rule in banned_patterns:
                if rule["regex"].search(text):
                    issues.append(
                        {
                            "file": rel,
                            "line": line_no,
                            "kind": "weak-text",
                            "detail": f"{text} ({rule['reason']})",
                            "pattern": rule["pattern"],
                        }
                    )

    return issues


def main() -> None:
    args = parse_args(sys.argv[1:])
    root = resolve_root(args.root)
    profile = load_style_profile(args, Path(__file__).resolve().parent)
    banned_patterns = normalize_banned_patterns(profile)
    files = list_python_files(root)

    issues = []
    for file_path in files:
        issues.extend(scan_quality(file_path, root, args.include_private, profile, banned_patterns))

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
        sys.stdout.write("Python docstring quality lint\n")
        sys.stdout.write(f"Root: {summary['root']}\n")
        sys.stdout.write(f"Style: {summary['style']}\n")
        sys.stdout.write(f"Style source: {summary['styleSource']}\n")
        sys.stdout.write(f"Scanned files: {summary['scannedFiles']}\n")
        sys.stdout.write(f"Issues: {summary['issueCount']}\n")

        if issues:
            sys.stdout.write("\nIssue details:\n")
            for issue in issues[:200]:
                sys.stdout.write(f"- {issue['file']}:{issue['line']} [{issue['kind']}] {issue['detail']}\n")
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
        sys.stderr.write(f"[lint_docstrings] {error}\n")
        raise SystemExit(1)
