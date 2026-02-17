#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

from javadoc_utils import (
    collect_method_signature,
    find_insertion_index,
    has_javadoc,
    is_method_declaration,
    is_method_start_line,
    is_type_declaration,
    list_java_files,
    parse_args,
    relative_path,
    resolve_root,
)


def scan_file(file_path, root, include_private):
    content = Path(file_path).read_text(encoding="utf-8")
    lines = re.split(r"\r?\n", content)
    missing = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if is_type_declaration(line):
            if not has_javadoc(lines, i):
                missing.append(
                    {
                        "file": relative_path(file_path, root),
                        "line": i + 1,
                        "kind": "type",
                        "signature": line.strip(),
                    }
                )
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
        if not has_javadoc(lines, insertion_index):
            missing.append(
                {
                    "file": relative_path(file_path, root),
                    "line": i + 1,
                    "kind": "method",
                    "signature": collected["signature"].strip(),
                }
            )

        i = collected["end_index"] + 1

    return missing


def main():
    args = parse_args(sys.argv[1:])
    root = resolve_root(args.root)
    files = list_java_files(root)

    by_file = []
    all_missing = []

    for file_path in files:
        missing = scan_file(file_path, root, args.include_private)
        if missing:
            by_file.append(
                {
                    "file": relative_path(file_path, root),
                    "missing": len(missing),
                }
            )
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

    sys.stdout.write("Java Javadoc coverage scan\n")
    sys.stdout.write(f"Root: {result['root']}\n")
    style_context = result["style"]
    if result["styleFile"]:
        style_context += f" + {result['styleFile']}"
    sys.stdout.write(f"Style context: {style_context}\n")
    sys.stdout.write(f"Scanned files: {result['scannedFiles']}\n")
    sys.stdout.write(f"Files with missing Javadoc: {result['filesWithMissing']}\n")
    sys.stdout.write(f"Total missing declarations: {result['totalMissing']}\n")

    if result["topFiles"]:
        sys.stdout.write("\nTop files with missing Javadoc:\n")
        for entry in result["topFiles"]:
            sys.stdout.write(f"- {entry['file']}: {entry['missing']}\n")

    if result["totalMissing"] > 0:
        sys.stdout.write("\nTip: run generate_javadocs.py, then refine_javadocs.py, then lint_javadocs.py.\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        sys.stderr.write(f"[scan_missing_javadocs] {error}\n")
        raise SystemExit(1)
