#!/usr/bin/env python3

"""
generate_docstrings 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydoc_utils import (
    apply_insertions,
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
from style_profile_utils import build_docstring_body, load_style_profile


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
    insertions: list[tuple[int, list[str]]] = []

    inserted = 0
    for target in targets:
        if target.has_docstring:
            continue

        if (
            target.kind == "method"
            and target.is_override
            and profile.get("allowMissingDocstringForOverrides", False)
        ):
            continue

        if target.kind == "module" and profile.get("allowMissingModuleDocstringForTests", False):
            module_name = Path(file_path).stem
            if module_name.startswith("test_") or module_name.endswith("_test"):
                continue

        body_lines = build_docstring_body(profile, target)
        doc_lines = render_docstring_block(body_lines, target.indent)
        if target.kind == "module":
            doc_lines.append("")

        insertions.append((target.insert_line, doc_lines))
        inserted += 1

    changed = inserted > 0
    if changed:
        apply_insertions(lines, insertions)
        Path(file_path).write_text(eol.join(lines), encoding="utf-8")

    return {
        "file": relative_path(file_path, root),
        "inserted": inserted,
        "changed": changed,
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

    sys.stdout.write("Python docstring generation completed\n")
    sys.stdout.write(f"Root: {summary['root']}\n")
    sys.stdout.write(f"Style: {summary['style']}\n")
    sys.stdout.write(f"Style source: {summary['styleSource']}\n")
    sys.stdout.write(f"Changed files: {summary['changedFiles']}\n")
    sys.stdout.write(f"Inserted docstrings: {summary['insertedTotal']}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"[generate_docstrings] {error}\n")
        raise SystemExit(1)
