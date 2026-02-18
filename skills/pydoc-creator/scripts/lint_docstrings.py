#!/usr/bin/env python3

"""
lint_docstrings 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

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


def is_test_module_path(rel: str) -> bool:
    """
    回傳目前是否符合條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        rel: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    normalized = rel.replace("\\", "/")
    name = normalized.split("/")[-1]
    stem = name[:-3] if name.endswith(".py") else name
    return stem.startswith("test_") or stem.endswith("_test")


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


def collect_structure_issues(target, rel: str, profile: dict) -> list[dict]:
    """
    執行 collect_structure_issues 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        target: 這個參數會影響函式的執行行為。
        rel: 這個參數會影響函式的執行行為。
        profile: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    issues = []
    docstring = target.docstring or ""
    base_line = target.doc_start_line or target.lineno

    if profile.get("requireDetailDescription") and not has_detail_description(docstring):
        issues.append(
            {
                "file": rel,
                "line": base_line,
                "kind": "missing-detail",
                "detail": "docstring 缺少摘要後的詳細描述段落。",
            }
        )

    if not has_blank_line_after_summary(docstring):
        issues.append(
            {
                "file": rel,
                "line": base_line,
                "kind": "missing-blank-line-after-summary",
                "detail": "摘要行後方應保留一個空行，再開始詳細描述或區段。",
            }
        )

    if target.kind not in {"function", "method"}:
        return issues

    doc_format = (profile.get("docstringFormat") or "rest").lower()
    return_text = choose_return_description(profile, target)
    summary = first_summary_line(docstring)

    if doc_format == "google":
        sections = parse_google_sections(docstring)
        has_args = has_google_heading(docstring, "Args:")
        has_returns = has_google_heading(docstring, "Returns:")
        has_yields = has_google_heading(docstring, "Yields:")
        has_raises = has_google_heading(docstring, "Raises:")
        has_examples = has_google_heading(docstring, "Examples:")

        if target.params and not has_args:
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "missing-args",
                    "detail": "Google style 需提供 Args 區段。",
                }
            )

        if has_args and profile.get("enforceGoogleSectionEntries", True):
            if not google_section_has_content(sections, "Args"):
                issues.append(
                    {
                        "file": rel,
                        "line": base_line,
                        "kind": "empty-args",
                        "detail": "Google style 的 Args 區段不可為空。",
                    }
                )
            documented_args = parse_google_args_entries(sections)
            for param in target.params:
                aliases = {param, normalize_param_name(param)}
                if documented_args.intersection(aliases):
                    continue
                issues.append(
                    {
                        "file": rel,
                        "line": base_line,
                        "kind": "missing-arg-item",
                        "detail": f"Args 區段缺少參數 `{param}` 的說明。",
                    }
                )

        if target.is_generator and profile.get("enforceYieldsSectionForGenerators", True):
            if not has_yields:
                issues.append(
                    {
                        "file": rel,
                        "line": base_line,
                        "kind": "missing-yields",
                        "detail": "Generator 函式應提供 Yields 區段。",
                    }
                )
            if has_returns:
                issues.append(
                    {
                        "file": rel,
                        "line": base_line,
                        "kind": "unexpected-returns-for-generator",
                        "detail": "Generator 函式應使用 Yields 區段，不應使用 Returns。",
                    }
                )
        else:
            allow_omit_returns = bool(
                profile.get("googleAllowOmitReturnsSectionWithSummaryVerb", True)
                and starts_with_return_verb(summary)
            )
            if return_text and not allow_omit_returns and not has_returns:
                issues.append(
                    {
                        "file": rel,
                        "line": base_line,
                        "kind": "missing-returns",
                        "detail": "Google style 需提供 Returns 區段。",
                    }
                )

        if has_returns and not google_section_has_content(sections, "Returns"):
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "empty-returns",
                    "detail": "Google style 的 Returns 區段不可為空。",
                }
            )

        if has_yields and not google_section_has_content(sections, "Yields"):
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "empty-yields",
                    "detail": "Google style 的 Yields 區段不可為空。",
                }
            )

        if target.raises and not has_raises:
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "missing-raises",
                    "detail": "Google style 需提供 Raises 區段。",
                }
            )

        if has_raises and not google_section_has_content(sections, "Raises"):
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "empty-raises",
                    "detail": "Google style 的 Raises 區段不可為空。",
                }
            )

        if profile.get("requireGoogleExamples") and not has_examples:
            issues.append(
                {
                    "file": rel,
                    "line": base_line,
                    "kind": "missing-examples",
                    "detail": "Google style 需提供 Examples 區段。",
                }
            )

        if has_examples and profile.get("enforceGoogleSectionEntries", True):
            if not google_section_has_content(sections, "Examples"):
                issues.append(
                    {
                        "file": rel,
                        "line": base_line,
                        "kind": "empty-examples",
                        "detail": "Google style 的 Examples 區段不可為空。",
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
    """
    執行 scan_quality 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        file_path: 這個參數會影響函式的執行行為。
        root: 這個參數會影響函式的執行行為。
        include_private: 這個參數會影響函式的執行行為。
        profile: 這個參數會影響函式的執行行為。
        banned_patterns: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    raw, tree = parse_python_source(file_path)
    lines = split_lines(raw)
    targets = collect_doc_targets(raw, tree, file_path, include_private)

    issues = []
    rel = relative_path(file_path, root)

    for target in targets:
        if not target.has_docstring:
            if (
                target.kind == "method"
                and target.is_override
                and profile.get("allowMissingDocstringForOverrides", False)
            ):
                continue
            if (
                target.kind == "module"
                and profile.get("allowMissingModuleDocstringForTests", False)
                and is_test_module_path(rel)
            ):
                continue
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

        if profile.get("enforceSummaryLineMaxLength"):
            try:
                limit = int(profile.get("summaryLineMaxLength") or 80)
            except (TypeError, ValueError):
                limit = 80
            if summary and len(summary) > limit:
                issues.append(
                    {
                        "file": rel,
                        "line": target.doc_start_line or target.lineno,
                        "kind": "summary-line-too-long",
                        "detail": f"摘要首句長度不應超過 {limit} 個字元。",
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
    """
    執行 main 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Raises:
        SystemExit: 當輸入不合法或處理失敗時拋出例外。
    """
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
