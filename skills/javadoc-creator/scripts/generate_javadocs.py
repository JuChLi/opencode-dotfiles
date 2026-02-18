#!/usr/bin/env python3

"""
generate_javadocs 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

import json
import re
import sys
from pathlib import Path

from javadoc_utils import (
    collect_method_signature,
    detect_eol,
    extract_param_name,
    find_insertion_index,
    has_javadoc,
    is_method_declaration,
    is_method_start_line,
    is_type_declaration,
    list_java_files,
    parse_args,
    parse_method_declaration,
    parse_type_declaration,
    relative_path,
    reorder_doc_before_annotations,
    resolve_root,
)
from style_profile_utils import (
    choose_method_summary,
    choose_param_description,
    choose_return_description,
    choose_type_summary,
    load_style_profile,
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
        return "執行此方法的主要流程。"
    if summary.endswith(("。", ".", "！", "!", "？", "?")):
        return summary
    return f"{summary}。"


def leading_indent(line):
    """
    執行 leading_indent 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param line: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    match = re.match(r"^\s*", line or "")
    return match.group(0) if match else ""


def build_type_javadoc(type_info, indent, profile):
    """
    建立目標資料結構。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param type_info: 此參數會影響函式的執行行為。
    :param indent: 此參數會影響函式的執行行為。
    :param profile: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    summary = ensure_summary_sentence(choose_type_summary(profile, type_info))
    return [
        f"{indent}/**",
        f"{indent} * {summary}",
        f"{indent} */",
    ]


def build_method_javadoc(method_info, indent, profile):
    """
    建立目標資料結構。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param method_info: 此參數會影響函式的執行行為。
    :param indent: 此參數會影響函式的執行行為。
    :param profile: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    summary = ensure_summary_sentence(choose_method_summary(profile, method_info))
    lines = [
        f"{indent}/**",
        f"{indent} * {summary}",
    ]

    param_names = [extract_param_name(param) for param in method_info["params"]]
    param_names = [name for name in param_names if name]
    return_text = None if method_info["isConstructor"] else choose_return_description(profile, method_info["returnType"])
    has_throws = len(method_info["throwsList"]) > 0

    if param_names or return_text or has_throws:
        lines.append(f"{indent} *")

    for param_name in param_names:
        lines.append(f"{indent} * @param {param_name} {choose_param_description(profile, param_name)}")

    if return_text:
        lines.append(f"{indent} * @return {return_text}")

    throws_template = profile.get("throwsTemplate") or "當處理過程發生錯誤時拋出。"
    for throwable in method_info["throwsList"]:
        short_name = throwable.split(".")[-1]
        lines.append(f"{indent} * @throws {short_name} {throws_template}")

    lines.append(f"{indent} */")
    return lines


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

    changed = reorder_doc_before_annotations(lines)
    inserted = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        if is_type_declaration(line) and not has_javadoc(lines, i):
            type_info = parse_type_declaration(line)
            if type_info:
                indent = leading_indent(line)
                doc = build_type_javadoc(type_info, indent, profile)
                lines[i:i] = doc
                inserted += 1
                changed = True
                i += len(doc)
            i += 1
            continue

        if not is_method_start_line(line, include_private):
            i += 1
            continue

        collected = collect_method_signature(lines, i)
        if not is_method_declaration(collected["signature"], include_private):
            i = collected["end_index"] + 1
            continue

        insertion_index = find_insertion_index(lines, i)
        if has_javadoc(lines, insertion_index):
            i = collected["end_index"] + 1
            continue

        method_info = parse_method_declaration(collected["signature"], class_name)
        if not method_info:
            i = collected["end_index"] + 1
            continue

        indent = leading_indent(lines[i])
        doc = build_method_javadoc(method_info, indent, profile)
        lines[insertion_index:insertion_index] = doc
        inserted += 1
        changed = True
        i = collected["end_index"] + len(doc) + 1

    if changed:
        Path(file_path).write_text(eol.join(lines), encoding="utf-8")

    return {
        "file": relative_path(file_path, root),
        "inserted": inserted,
        "changed": changed,
    }


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
    inserted_total = 0
    per_file = []

    for file_path in files:
        result = process_file(file_path, root, args.include_private, profile)
        if result["changed"]:
            changed_files += 1
            inserted_total += result["inserted"]
            per_file.append(result)

    summary = {
        "root": root,
        "style": profile.get("name") or args.style,
        "styleSource": profile.get("source"),
        "includePrivate": args.include_private,
        "changedFiles": changed_files,
        "insertedTotal": inserted_total,
        "files": per_file,
    }

    if args.json:
        sys.stdout.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
        return

    sys.stdout.write("Javadoc generation completed\n")
    sys.stdout.write(f"Root: {summary['root']}\n")
    sys.stdout.write(f"Style: {summary['style']}\n")
    sys.stdout.write(f"Style source: {summary['styleSource']}\n")
    sys.stdout.write(f"Changed files: {summary['changedFiles']}\n")
    sys.stdout.write(f"Inserted Javadocs: {summary['insertedTotal']}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"[generate_javadocs] {error}\n")
        raise SystemExit(1)
