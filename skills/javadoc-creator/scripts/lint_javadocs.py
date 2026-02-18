#!/usr/bin/env python3

"""
lint_javadocs 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

import json
import re
import sys
from pathlib import Path

from javadoc_utils import (
    collect_method_signature,
    extract_param_name,
    find_insertion_index,
    has_javadoc,
    is_method_declaration,
    is_method_start_line,
    is_type_declaration,
    list_java_files,
    parse_args,
    parse_method_declaration,
    relative_path,
    resolve_root,
)
from style_profile_utils import load_style_profile, normalize_banned_patterns


SUMMARY_END_PUNCTUATION = ("。", ".", "！", "!", "？", "?")

DEFAULT_TAG_ORDER = ["param", "return", "throws"]
DEFAULT_SUMMARY_DISALLOW_PATTERNS = [
    r"^This\s+method\b",
    r"^A\s+\{@code\s+[^}]+\}\s+is\s+a\b",
    r"^此方法",
    r"^這個方法",
]


def normalize_exception_name(value):
    """
    執行 normalize_exception_name 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param value: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    if not value:
        return None
    return value.strip().split(".")[-1]


def extract_doc_content(line):
    """
    執行 extract_doc_content 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param line: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    text = line.strip()
    if text.startswith("/**"):
        text = text[3:]
    if text.endswith("*/"):
        text = text[:-2]
    text = text.strip()
    if text.startswith("*"):
        text = text[1:].lstrip()
    return text


def locate_javadoc_block_before(lines, insertion_index):
    """
    執行 locate_javadoc_block_before 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param lines: 此參數會影響函式的執行行為。
    :param insertion_index: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    probe = insertion_index - 1
    while probe >= 0:
        text = lines[probe].strip()
        if not text or text.startswith("@"):
            probe -= 1
            continue
        break

    if probe < 0:
        return None

    if "*/" not in lines[probe]:
        return None

    end = probe
    start = end
    while start >= 0 and "/**" not in lines[start]:
        start -= 1

    if start < 0:
        return None
    return {
        "start": start,
        "end": end,
    }


def parse_javadoc_block(lines, start, end):
    """
    解析輸入內容。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param lines: 此參數會影響函式的執行行為。
    :param start: 此參數會影響函式的執行行為。
    :param end: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    summary = None
    detail_lines = []
    tags = []
    has_blank_before_first_tag = False
    seen_text_after_first_tag = False
    first_tag_line = None

    for index in range(start, end + 1):
        content = extract_doc_content(lines[index])
        if not content:
            if summary is not None and first_tag_line is None:
                has_blank_before_first_tag = True
            continue

        if content.startswith("@"):
            if first_tag_line is None:
                first_tag_line = index + 1
            match = re.match(r"^@([A-Za-z]+)(.*)$", content)
            if match:
                tag_name = match.group(1).lower()
                rest = (match.group(2) or "").strip()
                arg = None
                text = ""

                if tag_name in {"param", "throws", "exception"}:
                    if rest:
                        parts = rest.split(None, 1)
                        arg = parts[0]
                        text = parts[1] if len(parts) > 1 else ""
                else:
                    text = rest

                tags.append(
                    {
                        "name": tag_name,
                        "arg": arg,
                        "text": text,
                        "line": index + 1,
                    }
                )
            else:
                tags.append(
                    {
                        "name": "invalid",
                        "arg": None,
                        "text": content,
                        "line": index + 1,
                    }
                )
            continue

        if first_tag_line is not None:
            seen_text_after_first_tag = True
            continue

        if summary is None:
            summary = content
            continue

        detail_lines.append(content)

    return {
        "startLine": start + 1,
        "endLine": end + 1,
        "summary": summary,
        "detailLines": detail_lines,
        "tags": tags,
        "hasBlankBeforeFirstTag": has_blank_before_first_tag,
        "hasTextAfterFirstTag": seen_text_after_first_tag,
        "firstTagLine": first_tag_line,
    }


def build_issue(file_path, line, kind, detail, extra=None):
    """
    建立目標資料結構。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param file_path: 檔案路徑。
    :param line: 此參數會影響函式的執行行為。
    :param kind: 此參數會影響函式的執行行為。
    :param detail: 此參數會影響函式的執行行為。
    :param extra: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    issue = {
        "file": file_path,
        "line": line,
        "kind": kind,
        "detail": detail,
    }
    if extra:
        issue.update(extra)
    return issue


def normalize_tag_name(tag_name):
    """
    執行 normalize_tag_name 的核心流程並回傳結果。

    說明此函式的主要流程、輸入限制與輸出語意。

    :param tag_name: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    if tag_name == "exception":
        return "throws"
    return tag_name


def build_tag_rank(tag_order):
    """
    建立目標資料結構。

    說明此函式的主要流程、輸入限制與輸出語意。

    :param tag_order: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    rank = {}
    for index, raw_name in enumerate(tag_order, start=1):
        name = normalize_tag_name(str(raw_name).lower())
        rank[name] = index

    if "throws" in rank:
        rank["exception"] = rank["throws"]

    return rank


def contains_link_reference(text):
    """
    判斷是否具備指定條件。

    說明此函式的主要流程、輸入限制與輸出語意。

    :param text: 此參數會影響函式的執行行為。
    :returns: 條件判斷結果。
    """
    if not text:
        return False
    return bool(re.search(r"\{@link\s+[^}]+\}", text))


def has_override_annotation(lines, start_index, declaration_index):
    """
    判斷是否具備指定條件。

    說明此函式的主要流程、輸入限制與輸出語意。

    :param lines: 此參數會影響函式的執行行為。
    :param start_index: 此參數會影響函式的執行行為。
    :param declaration_index: 此參數會影響函式的執行行為。
    :returns: 條件判斷結果。
    """
    for index in range(start_index, declaration_index):
        text = lines[index].strip()
        if not text or not text.startswith("@"):
            continue
        if re.match(r"^@Override\b", text):
            return True
    return False


def validate_doclet_structure(file_path, block, declaration_kind, method_info, doclet_spec):
    """
    驗證輸入資料是否符合規範。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param file_path: 檔案路徑。
    :param block: 此參數會影響函式的執行行為。
    :param declaration_kind: 此參數會影響函式的執行行為。
    :param method_info: 此參數會影響函式的執行行為。
    :param doclet_spec: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    issues = []
    summary = block.get("summary")
    tags = block.get("tags", [])
    block_start_line = block.get("startLine") or (tags[0]["line"] if tags else 1)

    if doclet_spec.get("enforceSummarySentence", True):
        if not summary:
            issues.append(
                build_issue(
                    file_path,
                    block_start_line,
                    "missing-summary",
                    "Javadoc 缺少摘要句（summary sentence）。",
                )
            )
        elif not summary.endswith(SUMMARY_END_PUNCTUATION):
            issues.append(
                build_issue(
                    file_path,
                    block_start_line,
                    "summary-punctuation",
                    "摘要句建議以句號結尾，符合 Standard Doclet 可讀性慣例。",
                )
            )

    if doclet_spec.get("enforceSummaryFragment", False) and summary:
        configured_patterns = doclet_spec.get("summaryDisallowPatterns")
        if isinstance(configured_patterns, list) and configured_patterns:
            summary_patterns = configured_patterns
        else:
            summary_patterns = DEFAULT_SUMMARY_DISALLOW_PATTERNS

        for pattern in summary_patterns:
            try:
                regex = re.compile(pattern)
            except re.error:
                continue

            if regex.search(summary):
                issues.append(
                    build_issue(
                        file_path,
                        block_start_line,
                        "summary-fragment",
                        "摘要句型不符合 Google Javadoc summary fragment 建議，請避免模板開頭。",
                        extra={"pattern": pattern},
                    )
                )
                break

    if tags and not block.get("hasBlankBeforeFirstTag"):
        issues.append(
            build_issue(
                file_path,
                block.get("firstTagLine") or block_start_line,
                "missing-blank-before-tags",
                "主描述與 block tags 之間應有空行。",
            )
        )

    if block.get("hasTextAfterFirstTag"):
        issues.append(
            build_issue(
                file_path,
                block.get("firstTagLine") or block_start_line,
                "text-after-tags",
                "發現 block tags 後仍有主描述文字，請將描述移至 tags 之前。",
            )
        )

    raw_tag_order = doclet_spec.get("tagOrder")
    if isinstance(raw_tag_order, list) and raw_tag_order:
        tag_order = [normalize_tag_name(str(name).lower()) for name in raw_tag_order]
    else:
        tag_order = list(DEFAULT_TAG_ORDER)

    tag_rank = build_tag_rank(tag_order)
    order_display = []
    for name in tag_order:
        if name not in order_display:
            order_display.append(name)
    expected_tag_order = " -> ".join(f"@{name}" for name in order_display)

    if doclet_spec.get("enforceTagOrder", True):
        previous_rank = 0
        for tag in tags:
            normalized_name = normalize_tag_name(tag["name"])
            rank = tag_rank.get(normalized_name)
            if rank is None:
                continue
            if rank < previous_rank:
                issues.append(
                    build_issue(
                        file_path,
                        tag["line"],
                        "tag-order",
                        f"核心 tags 順序需為 {expected_tag_order}。",
                    )
                )
                break
            previous_rank = rank

    if doclet_spec.get("requireNonEmptyTagDescription", True):
        for tag in tags:
            normalized_name = normalize_tag_name(tag["name"])
            if normalized_name not in {"param", "return", "throws"}:
                continue

            if normalized_name in {"param", "throws"} and not (tag.get("arg") or "").strip():
                issues.append(
                    build_issue(
                        file_path,
                        tag["line"],
                        "missing-tag-argument",
                        f"@{normalized_name} 缺少必要目標名稱。",
                    )
                )

            if not (tag.get("text") or "").strip():
                issues.append(
                    build_issue(
                        file_path,
                        tag["line"],
                        "empty-tag-description",
                        f"@{normalized_name} 不可使用空白描述。",
                    )
                )

    deprecated_tags = [tag for tag in tags if tag["name"] == "deprecated"]
    if len(deprecated_tags) > 1:
        issues.append(
            build_issue(
                file_path,
                deprecated_tags[1]["line"],
                "duplicate-deprecated-tag",
                "@deprecated 不可重複出現。",
            )
        )

    if doclet_spec.get("requireDeprecatedDescription", False):
        for tag in deprecated_tags:
            if not (tag.get("text") or "").strip():
                issues.append(
                    build_issue(
                        file_path,
                        tag["line"],
                        "missing-deprecated-description",
                        "@deprecated 需包含棄用原因與替代方案。",
                    )
                )

    if doclet_spec.get("requireDeprecatedReplacementLink", False):
        for tag in deprecated_tags:
            text = (tag.get("text") or "").strip()
            if not text:
                continue
            if not contains_link_reference(text):
                issues.append(
                    build_issue(
                        file_path,
                        tag["line"],
                        "missing-deprecated-link",
                        "@deprecated 建議包含 {@link ...} 指向替代 API。",
                    )
                )

    if declaration_kind != "method" or not method_info:
        return issues

    expected_param_names = [extract_param_name(raw) for raw in method_info.get("params", [])]
    expected_param_names = [name for name in expected_param_names if name]

    param_tags = [tag for tag in tags if tag["name"] == "param" and tag.get("arg")]
    method_param_tags = [tag for tag in param_tags if not tag["arg"].startswith("<")]
    actual_param_names = [tag["arg"] for tag in method_param_tags]

    if doclet_spec.get("requireParamTags", True):
        missing_params = [name for name in expected_param_names if name not in actual_param_names]
        for name in missing_params:
            issues.append(
                build_issue(
                    file_path,
                    method_info.get("line") or block_start_line,
                    "missing-param-tag",
                    f"參數 `{name}` 缺少對應的 @param 說明。",
                )
            )

        for name in sorted(set(actual_param_names)):
            if actual_param_names.count(name) > 1:
                issues.append(
                    build_issue(
                        file_path,
                        method_info.get("line") or block_start_line,
                        "duplicate-param-tag",
                        f"參數 `{name}` 出現重複 @param。",
                    )
                )

        unexpected_params = [name for name in actual_param_names if name not in expected_param_names]
        for name in sorted(set(unexpected_params)):
            issues.append(
                build_issue(
                    file_path,
                    method_info.get("line") or block_start_line,
                    "unexpected-param-tag",
                    f"@param `{name}` 找不到對應的方法參數。",
                )
            )

    return_tags = [tag for tag in tags if tag["name"] == "return"]
    expected_return = (not method_info.get("isConstructor")) and method_info.get("returnType") != "void"

    if doclet_spec.get("requireReturnTagForNonVoid", True) and expected_return and not return_tags:
        issues.append(
            build_issue(
                file_path,
                method_info.get("line") or block_start_line,
                "missing-return-tag",
                "非 void 且非建構子方法需提供 @return。",
            )
        )

    if doclet_spec.get("forbidReturnTagForVoidOrConstructor", True) and (not expected_return) and return_tags:
        issues.append(
            build_issue(
                file_path,
                return_tags[0]["line"],
                "unexpected-return-tag",
                "void 或建構子方法不應出現 @return。",
            )
        )

    if len(return_tags) > 1:
        issues.append(
            build_issue(
                file_path,
                return_tags[1]["line"],
                "duplicate-return-tag",
                "@return 不可重複出現。",
            )
        )

    throws_tags = [tag for tag in tags if tag["name"] in {"throws", "exception"} and tag.get("arg")]
    declared_throws = [normalize_exception_name(value) for value in method_info.get("throwsList", [])]
    declared_throws = [name for name in declared_throws if name]
    actual_throws = [normalize_exception_name(tag["arg"]) for tag in throws_tags]
    actual_throws = [name for name in actual_throws if name]

    for name in sorted(set(actual_throws)):
        if actual_throws.count(name) > 1:
            issues.append(
                build_issue(
                    file_path,
                    method_info.get("line") or block_start_line,
                    "duplicate-throws-tag",
                    f"例外 `{name}` 出現重複 @throws/@exception。",
                )
            )

    if doclet_spec.get("requireDeclaredThrowsTags", True):
        missing_throws = [name for name in declared_throws if name not in actual_throws]
        for name in missing_throws:
            issues.append(
                build_issue(
                    file_path,
                    method_info.get("line") or block_start_line,
                    "missing-throws-tag",
                    f"宣告 throws `{name}` 但缺少對應的 @throws。",
                )
            )

    return issues


def scan_quality(file_path, root, include_private, profile, banned_patterns):
    """
    執行 scan_quality 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param file_path: 檔案路徑。
    :param root: 此參數會影響函式的執行行為。
    :param include_private: 此參數會影響函式的執行行為。
    :param profile: 此參數會影響函式的執行行為。
    :param banned_patterns: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    content = Path(file_path).read_text(encoding="utf-8")
    lines = re.split(r"\r?\n", content)
    issues = []
    rel_file = relative_path(file_path, root)

    doclet_spec = profile.get("docletSpec") or {}
    class_name = Path(file_path).stem

    i = 0
    while i < len(lines):
        trimmed = lines[i].strip()

        if is_type_declaration(lines[i]):
            if not has_javadoc(lines, i):
                issues.append(
                    build_issue(
                        rel_file,
                        i + 1,
                        "missing-javadoc",
                        "類別/介面/列舉缺少 Javadoc。",
                    )
                )
            else:
                block_loc = locate_javadoc_block_before(lines, i)
                if block_loc:
                    block = parse_javadoc_block(lines, block_loc["start"], block_loc["end"])
                    issues.extend(
                        validate_doclet_structure(
                            rel_file,
                            block,
                            declaration_kind="type",
                            method_info=None,
                            doclet_spec=doclet_spec,
                        )
                    )

            i += 1
            continue

        if is_method_start_line(lines[i], include_private):
            collected = collect_method_signature(lines, i)
            if is_method_declaration(collected["signature"], include_private):
                insertion_index = find_insertion_index(lines, i)
                method_info = parse_method_declaration(collected["signature"], class_name)
                if method_info:
                    method_info["line"] = i + 1

                if not has_javadoc(lines, insertion_index):
                    is_override = has_override_annotation(lines, insertion_index, i)
                    if not (doclet_spec.get("allowMissingJavadocForOverrides", False) and is_override):
                        issues.append(
                            build_issue(
                                rel_file,
                                i + 1,
                                "missing-javadoc",
                                "方法缺少 Javadoc。",
                            )
                        )
                else:
                    block_loc = locate_javadoc_block_before(lines, insertion_index)
                    if block_loc:
                        block = parse_javadoc_block(lines, block_loc["start"], block_loc["end"])
                        issues.extend(
                            validate_doclet_structure(
                                rel_file,
                                block,
                                declaration_kind="method",
                                method_info=method_info,
                                doclet_spec=doclet_spec,
                            )
                        )

            i = collected["end_index"] + 1
            continue

        for rule in banned_patterns:
            if rule["regex"].search(trimmed):
                issues.append(
                    build_issue(
                        rel_file,
                        i + 1,
                        "weak-text",
                        f"{trimmed} ({rule['reason']})",
                        extra={"pattern": rule["pattern"]},
                    )
                )

        i += 1

    return issues


def main():
    """
    執行 main 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :returns: 函式回傳結果。
    :raises SystemExit: 當輸入不合法或處理失敗時拋出。
    """
    args = parse_args(sys.argv[1:])
    root = resolve_root(args.root)
    profile = load_style_profile(args, Path(__file__).resolve().parent)
    banned_patterns = normalize_banned_patterns(profile)
    files = list_java_files(root)

    issues = []
    for file_path in files:
        issues.extend(scan_quality(file_path, root, args.include_private, profile, banned_patterns))

    summary = {
        "root": root,
        "style": profile.get("name") or args.style,
        "styleSource": profile.get("source"),
        "docletSpec": (profile.get("docletSpec") or {}).get("source"),
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
        sys.stdout.write(f"Doclet spec: {summary['docletSpec']}\n")
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
