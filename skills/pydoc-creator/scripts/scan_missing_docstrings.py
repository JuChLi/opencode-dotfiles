#!/usr/bin/env python3

from __future__ import annotations

import json
import sys

from pydoc_utils import (
    collect_doc_targets,
    list_python_files,
    parse_args,
    parse_python_source,
    relative_path,
    resolve_root,
)


def target_signature(target) -> str:
    if target.kind == "module":
        return f"module {target.name}"
    if target.kind == "class":
        return f"class {target.qualified_name}"

    prefix = "async def" if target.is_async else "def"
    params = ", ".join(target.params)
    return f"{prefix} {target.qualified_name}({params})"


def scan_file(file_path: str, root: str, include_private: bool) -> list[dict]:
    raw, tree = parse_python_source(file_path)
    targets = collect_doc_targets(raw, tree, file_path, include_private)

    missing: list[dict] = []
    for target in targets:
        if target.has_docstring:
            continue
        missing.append(
            {
                "file": relative_path(file_path, root),
                "line": target.lineno,
                "kind": target.kind,
                "signature": target_signature(target),
            }
        )

    return missing


def main() -> None:
    args = parse_args(sys.argv[1:])
    root = resolve_root(args.root)
    files = list_python_files(root)

    by_file = []
    all_missing = []

    for file_path in files:
        missing = scan_file(file_path, root, args.include_private)
        if missing:
            by_file.append({"file": relative_path(file_path, root), "missing": len(missing)})
            all_missing.extend(missing)

    by_file.sort(key=lambda item: (-item["missing"], item["file"]))

    result = {
        "root": root,
        "style": args.style,
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
    style_context = result["style"]
    if result["styleFile"]:
        style_context += f" + {result['styleFile']}"
    sys.stdout.write(f"Style context: {style_context}\n")
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
