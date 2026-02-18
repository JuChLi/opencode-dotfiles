#!/usr/bin/env python3

"""
refine_javadocs 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

import json
import re
import sys
from pathlib import Path

from javadoc_utils import (
    collect_method_signature,
    detect_eol,
    is_method_declaration,
    is_method_start_line,
    is_type_declaration,
    list_java_files,
    parse_args,
    parse_method_declaration,
    parse_type_declaration,
    relative_path,
    resolve_root,
)
from style_profile_utils import (
    choose_method_summary,
    choose_param_description,
    choose_return_description,
    choose_type_summary,
    load_style_profile,
)


SUMMARY_END_PUNCTUATION = ("。", ".", "！", "!", "？", "?")


def find_declaration_index(lines, doc_end):
    """
    執行 find_declaration_index 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param lines: 此參數會影響函式的執行行為。
    :param doc_end: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    i = doc_end + 1
    while i < len(lines):
        trimmed = lines[i].strip()
        if not trimmed or trimmed.startswith("@"):
            i += 1
            continue
        return i
    return -1


def is_weak_summary(text):
    """
    判斷是否符合條件。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param text: 此參數會影響函式的執行行為。
    :returns: 條件判斷結果。
    """
    return bool(
        re.match(
            r"^(執行此方法的主要處理流程。|取得此方法對應的值。|判斷此方法對應的狀態。|更新此方法對應的值。|執行\s+\{@code\s+[A-Za-z0-9_]+\}\s+操作。)$",
            text,
        )
    )


def ensure_summary_sentence(text):
    """
    執行 ensure_summary_sentence 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param text: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    summary = (text or "").strip()
    if not summary:
        return ""
    if summary.endswith(SUMMARY_END_PUNCTUATION):
        return summary
    return f"{summary}。"


def refine_doc_block(lines, start, end, declaration_info, profile):
    """
    執行 refine_doc_block 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param lines: 此參數會影響函式的執行行為。
    :param start: 此參數會影響函式的執行行為。
    :param end: 此參數會影響函式的執行行為。
    :param declaration_info: 此參數會影響函式的執行行為。
    :param profile: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    changed = False
    summary_handled = False

    for i in range(start + 1, end):
        line = lines[i]
        summary_match = re.match(r"^(\s*\*\s+)([^@].*)$", line)
        if summary_match and not summary_handled:
            if declaration_info["kind"] == "type":
                expected_summary = choose_type_summary(profile, declaration_info["type"])
            else:
                expected_summary = choose_method_summary(profile, declaration_info["method"])

            expected_summary = ensure_summary_sentence(expected_summary)
            current_summary = summary_match.group(2).strip()

            if is_weak_summary(current_summary) and current_summary != expected_summary:
                lines[i] = f"{summary_match.group(1)}{expected_summary}"
                changed = True
            elif current_summary and not current_summary.endswith(SUMMARY_END_PUNCTUATION):
                lines[i] = f"{summary_match.group(1)}{ensure_summary_sentence(current_summary)}"
                changed = True

            summary_handled = True
            continue

        if declaration_info["kind"] != "method":
            continue

        param_match = re.match(r"^(\s*\*\s+@param\s+)([A-Za-z_][A-Za-z0-9_]*)(\s+).+$", line)
        if param_match:
            expected = (
                f"{param_match.group(1)}{param_match.group(2)}{param_match.group(3)}"
                f"{choose_param_description(profile, param_match.group(2))}"
            )
            if expected != line:
                lines[i] = expected
                changed = True
            continue

        return_match = re.match(r"^(\s*\*\s+@return\s+).+$", line)
        if return_match:
            return_text = choose_return_description(profile, declaration_info["method"]["returnType"])
            if return_text:
                expected = f"{return_match.group(1)}{return_text}"
                if expected != line:
                    lines[i] = expected
                    changed = True
            continue

        throws_match = re.match(r"^(\s*\*\s+@throws\s+)([A-Za-z_][A-Za-z0-9_]*)(\s+).+$", line)
        if throws_match:
            throws_template = profile.get("throwsTemplate") or "當處理過程發生錯誤時拋出。"
            expected = (
                f"{throws_match.group(1)}{throws_match.group(2)}{throws_match.group(3)}{throws_template}"
            )
            if expected != line:
                lines[i] = expected
                changed = True

    return changed


def process_file(file_path, root, include_private, profile):
    """
    執行 process_file 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param file_path: 檔案路徑。
    :param root: 此參數會影響函式的執行行為。
    :param include_private: 此參數會影響函式的執行行為。
    :param profile: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    raw = Path(file_path).read_text(encoding="utf-8")
    eol = detect_eol(raw)
    lines = re.split(r"\r?\n", raw)
    class_name = Path(file_path).stem

    changed = False

    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("/**"):
            i += 1
            continue

        doc_start = i
        doc_end = i
        while doc_end < len(lines) and "*/" not in lines[doc_end]:
            doc_end += 1
        if doc_end >= len(lines):
            break

        declaration_index = find_declaration_index(lines, doc_end)
        if declaration_index < 0:
            i = doc_end + 1
            continue

        declaration_line = lines[declaration_index]
        if is_type_declaration(declaration_line):
            type_info = parse_type_declaration(declaration_line)
            if type_info and refine_doc_block(lines, doc_start, doc_end, {"kind": "type", "type": type_info}, profile):
                changed = True
            i = doc_end + 1
            continue

        if not is_method_start_line(declaration_line, include_private):
            i = doc_end + 1
            continue

        collected = collect_method_signature(lines, declaration_index)
        if not is_method_declaration(collected["signature"], include_private):
            i = doc_end + 1
            continue

        method_info = parse_method_declaration(collected["signature"], class_name)
        if method_info and refine_doc_block(lines, doc_start, doc_end, {"kind": "method", "method": method_info}, profile):
            changed = True

        i = doc_end + 1

    if changed:
        Path(file_path).write_text(eol.join(lines), encoding="utf-8")

    return changed


def main():
    """
    執行 main 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :returns: 函式回傳結果。
    """
    args = parse_args(sys.argv[1:])
    root = resolve_root(args.root)
    profile = load_style_profile(args, Path(__file__).resolve().parent)
    files = list_java_files(root)

    changed_files = 0
    refined = []
    for file_path in files:
        if process_file(file_path, root, args.include_private, profile):
            changed_files += 1
            refined.append(relative_path(file_path, root))

    summary = {
        "root": root,
        "style": profile.get("name") or args.style,
        "styleSource": profile.get("source"),
        "includePrivate": args.include_private,
        "changedFiles": changed_files,
        "files": refined,
    }

    if args.json:
        sys.stdout.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
        return

    sys.stdout.write("Javadoc refinement completed\n")
    sys.stdout.write(f"Root: {summary['root']}\n")
    sys.stdout.write(f"Style: {summary['style']}\n")
    sys.stdout.write(f"Style source: {summary['styleSource']}\n")
    sys.stdout.write(f"Refined files: {summary['changedFiles']}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"[refine_javadocs] {error}\n")
        raise SystemExit(1)
