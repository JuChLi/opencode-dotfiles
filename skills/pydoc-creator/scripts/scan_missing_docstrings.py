#!/usr/bin/env python3

"""
scan_missing_docstrings 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydoc_utils import (
    collect_doc_targets,
    list_python_files,
    parse_args,
    parse_python_source,
    relative_path,
    resolve_root,
)
from style_profile_utils import load_style_profile


def target_signature(target) -> str:
    """
    執行 target_signature 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    if target.kind == "module":
        return f"module {target.name}"
    if target.kind == "class":
        return f"class {target.qualified_name}"

    prefix = "async def" if target.is_async else "def"
    params = ", ".join(target.params)
    return f"{prefix} {target.qualified_name}({params})"


def scan_file(file_path: str, root: str, include_private: bool, profile: dict) -> list[dict]:
    """
    執行 scan_file 的核心流程並回傳結果。
    
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
    targets = collect_doc_targets(raw, tree, file_path, include_private)

    missing: list[dict] = []
    rel = relative_path(file_path, root)
    module_stem = Path(file_path).stem

    for target in targets:
        if target.has_docstring:
            continue

        if (
            target.kind == "method"
            and target.is_override
            and profile.get("allowMissingDocstringForOverrides", False)
        ):
            continue

        if (
            target.kind == "module"
            and profile.get("allowMissingModuleDocstringForTests", False)
            and (module_stem.startswith("test_") or module_stem.endswith("_test"))
        ):
            continue

        missing.append(
            {
                "file": rel,
                "line": target.lineno,
                "kind": target.kind,
                "signature": target_signature(target),
            }
        )

    return missing


def main() -> None:
    """
    執行 main 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    """
    args = parse_args(sys.argv[1:])
    root = resolve_root(args.root)
    profile = load_style_profile(args, Path(__file__).resolve().parent)
    files = list_python_files(root)

    by_file = []
    all_missing = []

    for file_path in files:
        missing = scan_file(file_path, root, args.include_private, profile)
        if missing:
            by_file.append({"file": relative_path(file_path, root), "missing": len(missing)})
            all_missing.extend(missing)

    by_file.sort(key=lambda item: (-item["missing"], item["file"]))

    result = {
        "root": root,
        "style": profile.get("name") or args.style,
        "styleSource": profile.get("source"),
        "styleFile": args.style_file,
        "includePrivate": args.include_private,
        "scannedFiles": len(files),
        "filesWithMissing": len(by_file),
        "totalMissing": len(all_missing),
        "topFiles": by_file[: args.top],
        "missing": all_missing,
    }

    if args.json:
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        return

    sys.stdout.write("Python docstring coverage scan\n")
    sys.stdout.write(f"Root: {result['root']}\n")
    sys.stdout.write(f"Style: {result['style']}\n")
    sys.stdout.write(f"Style source: {result['styleSource']}\n")
    sys.stdout.write(f"Scanned files: {result['scannedFiles']}\n")
    sys.stdout.write(f"Files with missing docstring: {result['filesWithMissing']}\n")
    sys.stdout.write(f"Total missing declarations: {result['totalMissing']}\n")

    if result["topFiles"]:
        sys.stdout.write("\nTop files with missing docstring:\n")
        for entry in result["topFiles"]:
            sys.stdout.write(f"- {entry['file']}: {entry['missing']}\n")

    if result["totalMissing"] > 0:
        sys.stdout.write("\nTip: run generate_docstrings.py, then refine_docstrings.py, then lint_docstrings.py.\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"[scan_missing_docstrings] {error}\n")
        raise SystemExit(1)
