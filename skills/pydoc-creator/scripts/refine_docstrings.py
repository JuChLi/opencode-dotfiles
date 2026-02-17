#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pydoc_utils import (
    apply_replacements,
    collect_doc_targets,
    detect_eol,
    list_python_files,
    parse_args,
    parse_python_source,
    relative_path,
    render_docstring_block,
    resolve_root,
    split_lines,
)
from style_profile_utils import (
    build_docstring_body,
    choose_return_description,
    load_style_profile,
    normalize_banned_patterns,
    normalize_param_name,
)


DEFAULT_WEAK_SUMMARY_PATTERNS = [
    r"^執行此函式的主要流程。$",
    r"^執行此方法的主要流程。$",
    r"^待補充說明。$",
    r"^TODO",
]


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


def has_structure_gap(target, profile: dict) -> bool:
    if not target.docstring:
        return True
    if not has_detail_description(target.docstring):
        return True

    if target.kind not in {"function", "method"}:
        return False

    doc_format = (profile.get("docstringFormat") or "rest").lower()
    return_text = choose_return_description(profile, target)

    if doc_format == "google":
        if target.params and not has_google_heading(target.docstring, "Args:"):
            return True
        if return_text and not has_google_heading(target.docstring, "Returns:"):
            return True
        if target.raises and not has_google_heading(target.docstring, "Raises:"):
            return True
        if profile.get("includeExamples") and not has_google_heading(target.docstring, "Examples:"):
            return True
        return False

    for param in target.params:
        if not has_rest_param(target.docstring, normalize_param_name(param)):
            return True
    if return_text and not has_rest_returns(target.docstring):
        return True
    for exc in target.raises:
        if not has_rest_raises(target.docstring, exc):
            return True
    return False


def should_refine(target, weak_patterns: list[re.Pattern[str]], banned_patterns: list[dict]) -> bool:
    if not target.docstring:
        return False

    summary = first_summary_line(target.docstring)
    if not summary:
        return True

    if any(pattern.search(summary) for pattern in weak_patterns):
        return True

    if "TODO" in target.docstring or "待補" in target.docstring:
        return True

    for rule in banned_patterns:
        if rule["regex"].search(target.docstring):
            return True

    return False


def should_refine_with_profile(target, profile: dict, weak_patterns: list[re.Pattern[str]], banned_patterns: list[dict]) -> bool:
    if should_refine(target, weak_patterns, banned_patterns):
        return True
    return has_structure_gap(target, profile)


def process_file(file_path: str, root: str, include_private: bool, profile: dict) -> dict:
    raw, tree = parse_python_source(file_path)
    eol = detect_eol(raw)
    lines = split_lines(raw)

    targets = collect_doc_targets(raw, tree, file_path, include_private)
    weak_patterns = [re.compile(item) for item in profile.get("weakSummaryPatterns", DEFAULT_WEAK_SUMMARY_PATTERNS)]
    banned_patterns = normalize_banned_patterns(profile)

    replacements: list[tuple[int, int, list[str]]] = []

    for target in targets:
        if not target.has_docstring:
            continue
        if target.doc_start_line is None or target.doc_end_line is None:
            continue
        if not should_refine_with_profile(target, profile, weak_patterns, banned_patterns):
            continue

        body_lines = build_docstring_body(profile, target)
        doc_lines = render_docstring_block(body_lines, target.indent)
        replacements.append((target.doc_start_line, target.doc_end_line, doc_lines))

    changed = len(replacements) > 0
    if changed:
        apply_replacements(lines, replacements)
        Path(file_path).write_text(eol.join(lines), encoding="utf-8")

    return {
        "file": relative_path(file_path, root),
        "changed": changed,
        "refined": len(replacements),
    }


def main() -> None:
    args = parse_args(sys.argv[1:])
    root = resolve_root(args.root)
    profile = load_style_profile(args, Path(__file__).resolve().parent)
    files = list_python_files(root)

    changed_files = 0
    refined_total = 0
    refined_files = []

    for file_path in files:
        result = process_file(file_path, root, args.include_private, profile)
        if result["changed"]:
            changed_files += 1
            refined_total += result["refined"]
            refined_files.append(result["file"])

    summary = {
        "root": root,
        "style": profile.get("name") or args.style,
        "styleSource": profile.get("source"),
        "includePrivate": args.include_private,
        "changedFiles": changed_files,
        "refinedTotal": refined_total,
        "files": refined_files,
    }

    if args.json:
        sys.stdout.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
        return

    sys.stdout.write("Python docstring refinement completed\n")
    sys.stdout.write(f"Root: {summary['root']}\n")
    sys.stdout.write(f"Style: {summary['style']}\n")
    sys.stdout.write(f"Style source: {summary['styleSource']}\n")
    sys.stdout.write(f"Refined files: {summary['changedFiles']}\n")
    sys.stdout.write(f"Refined blocks: {summary['refinedTotal']}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"[refine_docstrings] {error}\n")
        raise SystemExit(1)
