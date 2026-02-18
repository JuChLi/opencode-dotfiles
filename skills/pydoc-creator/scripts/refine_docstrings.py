#!/usr/bin/env python3

"""
refine_docstrings 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

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

GOOGLE_HEADINGS = ("Args", "Returns", "Yields", "Raises", "Examples")
SUMMARY_RETURN_VERBS = ("return", "returns", "yield", "yields")


def first_summary_line(docstring: str) -> str:
    """
    執行 first_summary_line 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        docstring: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    for line in docstring.splitlines():
        text = line.strip()
        if text:
            return text
    return ""


def has_detail_description(docstring: str) -> bool:
    """
    回傳目前是否具備指定條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        docstring: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
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
    """
    回傳目前是否具備指定條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        docstring: 這個參數會影響函式的執行行為。
        heading: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    return re.search(rf"(?m)^\s*{re.escape(heading)}\s*$", docstring) is not None


def starts_with_return_verb(summary: str) -> bool:
    """
    執行 starts_with_return_verb 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        summary: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    text = (summary or "").strip().lower()
    return any(text.startswith(f"{verb} ") or text.startswith(f"{verb}:") for verb in SUMMARY_RETURN_VERBS)


def parse_google_sections(docstring: str) -> dict[str, list[str]]:
    """
    將輸入內容解析為可用資料。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        docstring: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    sections = {name: [] for name in GOOGLE_HEADINGS}
    current = None

    for raw in docstring.splitlines():
        text = raw.strip()
        matched_heading = None
        for heading in GOOGLE_HEADINGS:
            if text == f"{heading}:":
                matched_heading = heading
                break

        if matched_heading:
            current = matched_heading
            continue

        if current is not None:
            sections[current].append(raw)

    return sections


def google_section_has_content(sections: dict[str, list[str]], heading: str) -> bool:
    """
    執行 google_section_has_content 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        sections: 這個參數會影響函式的執行行為。
        heading: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    return any(line.strip() for line in sections.get(heading, []))


def parse_google_args_entries(sections: dict[str, list[str]]) -> set[str]:
    """
    將輸入內容解析為可用資料。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        sections: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    names = set()
    pattern = re.compile(r"^\s{2,}(\*{0,2}[A-Za-z_][A-Za-z0-9_]*)\s*:")
    for raw in sections.get("Args", []):
        match = pattern.match(raw)
        if not match:
            continue
        names.add(match.group(1))
    return names


def has_blank_line_after_summary(docstring: str) -> bool:
    """
    回傳目前是否具備指定條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        docstring: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    lines = docstring.splitlines()
    first_index = None
    for index, raw in enumerate(lines):
        if raw.strip():
            first_index = index
            break

    if first_index is None:
        return True
    if first_index + 1 >= len(lines):
        return True

    has_more_content = any(line.strip() for line in lines[first_index + 1 :])
    if not has_more_content:
        return True

    return lines[first_index + 1].strip() == ""


def has_rest_param(docstring: str, param_name: str) -> bool:
    """
    回傳目前是否具備指定條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        docstring: 這個參數會影響函式的執行行為。
        param_name: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    return re.search(rf"(?m)^\s*:param\s+{re.escape(param_name)}\s*:", docstring) is not None


def has_rest_returns(docstring: str) -> bool:
    """
    回傳目前是否具備指定條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        docstring: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    return re.search(r"(?m)^\s*:returns?\s*:", docstring) is not None


def has_rest_raises(docstring: str, exc_name: str) -> bool:
    """
    回傳目前是否具備指定條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        docstring: 這個參數會影響函式的執行行為。
        exc_name: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    return re.search(rf"(?m)^\s*:raises\s+{re.escape(exc_name)}\s*:", docstring) is not None


def has_structure_gap(target, profile: dict) -> bool:
    """
    回傳目前是否具備指定條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        target: 這個參數會影響函式的執行行為。
        profile: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    if not target.docstring:
        return True
    if profile.get("requireDetailDescription") and not has_detail_description(target.docstring):
        return True
    if not has_blank_line_after_summary(target.docstring):
        return True

    if target.kind not in {"function", "method"}:
        return False

    doc_format = (profile.get("docstringFormat") or "rest").lower()
    return_text = choose_return_description(profile, target)
    summary = first_summary_line(target.docstring)

    if doc_format == "google":
        sections = parse_google_sections(target.docstring)
        has_args = has_google_heading(target.docstring, "Args:")
        has_returns = has_google_heading(target.docstring, "Returns:")
        has_yields = has_google_heading(target.docstring, "Yields:")
        has_raises = has_google_heading(target.docstring, "Raises:")
        has_examples = has_google_heading(target.docstring, "Examples:")

        if target.params and not has_args:
            return True

        if has_args and profile.get("enforceGoogleSectionEntries", True):
            if not google_section_has_content(sections, "Args"):
                return True
            documented_args = parse_google_args_entries(sections)
            for param in target.params:
                aliases = {param, normalize_param_name(param)}
                if not documented_args.intersection(aliases):
                    return True

        if target.is_generator and profile.get("enforceYieldsSectionForGenerators", True):
            if not has_yields:
                return True
            if has_returns:
                return True
        else:
            allow_omit_returns = bool(
                profile.get("googleAllowOmitReturnsSectionWithSummaryVerb", True)
                and starts_with_return_verb(summary)
            )
            if return_text and not allow_omit_returns and not has_returns:
                return True

        if has_returns and not google_section_has_content(sections, "Returns"):
            return True
        if has_yields and not google_section_has_content(sections, "Yields"):
            return True

        if target.raises and not has_raises:
            return True
        if has_raises and not google_section_has_content(sections, "Raises"):
            return True

        if profile.get("requireGoogleExamples") and not has_examples:
            return True
        if has_examples and profile.get("enforceGoogleSectionEntries", True):
            if not google_section_has_content(sections, "Examples"):
                return True

        if profile.get("enforceSummaryLineMaxLength"):
            try:
                limit = int(profile.get("summaryLineMaxLength") or 80)
            except (TypeError, ValueError):
                limit = 80
            if summary and len(summary) > limit:
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
    """
    執行 should_refine 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        target: 這個參數會影響函式的執行行為。
        weak_patterns: 這個參數會影響函式的執行行為。
        banned_patterns: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
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
    """
    執行 should_refine_with_profile 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        target: 這個參數會影響函式的執行行為。
        profile: 這個參數會影響函式的執行行為。
        weak_patterns: 這個參數會影響函式的執行行為。
        banned_patterns: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    if should_refine(target, weak_patterns, banned_patterns):
        return True
    return has_structure_gap(target, profile)


def process_file(file_path: str, root: str, include_private: bool, profile: dict) -> dict:
    """
    執行 process_file 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        file_path: 這個參數會影響函式的執行行為。
        root: 這個參數會影響函式的執行行為。
        include_private: 這個參數會影響函式的執行行為。
        profile: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
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
    """
    執行 main 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    """
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
