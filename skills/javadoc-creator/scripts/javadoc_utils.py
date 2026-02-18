#!/usr/bin/env python3

"""
javadoc_utils 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ScriptArgs:
    """
    ScriptArgs 的核心行為實作。
    
    說明此類別管理的狀態、核心流程與建議使用方式。
    """
    root: str = "src/main/java"
    include_private: bool = False
    json: bool = False
    top: int = 20
    style: str = "vertx"
    style_file: Optional[str] = None


def parse_args(argv):
    """
    解析輸入內容。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param argv: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    args = ScriptArgs()
    i = 0
    while i < len(argv):
        token = argv[i]
        if token == "--root" and i + 1 < len(argv):
            args.root = argv[i + 1]
            i += 2
            continue
        if token == "--include-private":
            args.include_private = True
            i += 1
            continue
        if token == "--json":
            args.json = True
            i += 1
            continue
        if token == "--top" and i + 1 < len(argv):
            try:
                value = int(argv[i + 1])
                if value > 0:
                    args.top = value
            except ValueError:
                pass
            i += 2
            continue
        if token == "--style" and i + 1 < len(argv):
            args.style = argv[i + 1]
            i += 2
            continue
        if token == "--style-file" and i + 1 < len(argv):
            args.style_file = argv[i + 1]
            i += 2
            continue
        i += 1
    return args


def resolve_root(root_arg):
    """
    執行 resolve_root 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param root_arg: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    :raises ValueError: 當輸入不合法或處理失敗時拋出。
    """
    root = Path(root_arg)
    if not root.is_absolute():
        root = Path.cwd() / root
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Root path does not exist or is not a directory: {root}")
    return str(root)


def list_java_files(directory):
    """
    執行 list_java_files 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param directory: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    root = Path(directory)
    files = []
    for current_root, dir_names, file_names in os.walk(root):
        dir_names.sort()
        for name in sorted(file_names):
            if name.endswith(".java"):
                files.append(str(Path(current_root) / name))
    return files


def relative_path(file_path, root):
    """
    執行 relative_path 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param file_path: 檔案路徑。
    :param root: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    return os.path.relpath(file_path, root).replace("\\", "/")


def detect_eol(content):
    """
    執行 detect_eol 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param content: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    return "\r\n" if "\r\n" in content else "\n"


def has_javadoc(lines, index):
    """
    判斷是否具備指定條件。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param lines: 此參數會影響函式的執行行為。
    :param index: 此參數會影響函式的執行行為。
    :returns: 條件判斷結果。
    """
    i = index - 1
    while i >= 0:
        line = lines[i].strip()
        if not line or line.startswith("@"):
            i -= 1
            continue

        if line.startswith("/**"):
            return True

        if line.endswith("*/"):
            j = i - 1
            while j >= 0:
                current = lines[j].strip()
                if not current:
                    j -= 1
                    continue
                if current.startswith("/**"):
                    return True
                if current.startswith("*") or current.startswith("/*"):
                    j -= 1
                    continue
                return False

        return False

    return False


def is_type_declaration(line):
    """
    判斷是否符合條件。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param line: 此參數會影響函式的執行行為。
    :returns: 條件判斷結果。
    """
    trimmed = line.strip()
    return bool(
        re.match(
            r"^(?:public\s+)?(?:abstract\s+|final\s+)?(?:class|interface|enum)\s+[A-Za-z_]\w*",
            trimmed,
        )
    )


def parse_type_declaration(line):
    """
    解析輸入內容。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param line: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    trimmed = line.strip()
    match = re.match(
        r"^(?:public\s+)?(?:abstract\s+|final\s+)?(class|interface|enum)\s+([A-Za-z_]\w*)",
        trimmed,
    )
    if not match:
        return None

    return {
        "kind": match.group(1),
        "name": match.group(2),
    }


def split_params(raw):
    """
    執行 split_params 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param raw: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    result = []
    current = []
    angle_depth = 0

    for ch in raw:
        if ch == "<":
            angle_depth += 1
        elif ch == ">":
            angle_depth = max(0, angle_depth - 1)

        if ch == "," and angle_depth == 0:
            value = "".join(current).strip()
            if value:
                result.append(value)
            current = []
            continue

        current.append(ch)

    tail = "".join(current).strip()
    if tail:
        result.append(tail)

    return result


def extract_param_name(param):
    """
    執行 extract_param_name 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param param: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    if not param:
        return None

    cleaned = re.sub(r"@[A-Za-z_]\w*(?:\([^)]*\))?\s*", "", param)
    cleaned = re.sub(r"\bfinal\s+", "", cleaned).strip()
    if not cleaned:
        return None

    parts = re.split(r"\s+", cleaned)
    if not parts:
        return None

    name = re.sub(r"\[\]$", "", parts[-1])
    name = re.sub(r"\.{3}", "", name, count=1)
    return name


def is_method_start_line(line, include_private=False):
    """
    判斷是否符合條件。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param line: 此參數會影響函式的執行行為。
    :param include_private: 此參數會影響函式的執行行為。
    :returns: 條件判斷結果。
    """
    trimmed = line.strip()
    visibility = r"(public|protected|private)" if include_private else r"(public|protected)"
    if not re.match(rf"^{visibility}\s+", trimmed):
        return False
    if re.search(r"\b(class|interface|enum)\b", trimmed):
        return False
    return "(" in trimmed


def collect_method_signature(lines, start_index):
    """
    執行 collect_method_signature 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param lines: 此參數會影響函式的執行行為。
    :param start_index: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    end_index = start_index
    signature = lines[start_index].strip()

    while (
        end_index + 1 < len(lines)
        and not (
            lines[end_index].strip().endswith("{")
            or lines[end_index].strip().endswith(";")
        )
    ):
        end_index += 1
        signature += f" {lines[end_index].strip()}"
        if end_index - start_index > 30:
            break

    return {
        "signature": signature,
        "end_index": end_index,
    }


def is_method_declaration(signature, include_private=False):
    """
    判斷是否符合條件。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param signature: 此參數會影響函式的執行行為。
    :param include_private: 此參數會影響函式的執行行為。
    :returns: 條件判斷結果。
    """
    trimmed = signature.strip()
    visibility = r"(public|protected|private)" if include_private else r"(public|protected)"
    if not re.match(rf"^{visibility}\s+", trimmed):
        return False
    if "(" not in trimmed or ")" not in trimmed:
        return False
    if not (trimmed.endswith("{") or trimmed.endswith(";")):
        return False
    if re.search(r"\b(class|interface|enum)\b", trimmed):
        return False
    return True


def parse_method_declaration(signature, class_name):
    """
    解析輸入內容。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param signature: 此參數會影響函式的執行行為。
    :param class_name: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    trimmed = re.sub(r"[;{]\s*$", "", signature.strip()).strip()
    open_index = trimmed.find("(")
    close_index = trimmed.rfind(")")
    if open_index < 0 or close_index < 0 or close_index < open_index:
        return None

    before = trimmed[:open_index].strip()
    params_raw = trimmed[open_index + 1 : close_index].strip()
    after = trimmed[close_index + 1 :].strip()

    throws_list = []
    if after.startswith("throws "):
        throws_list = [item.strip() for item in after[len("throws ") :].split(",") if item.strip()]

    modifier_set = {
        "public",
        "protected",
        "private",
        "static",
        "final",
        "abstract",
        "synchronized",
        "native",
        "default",
        "strictfp",
    }

    tokens = [token for token in before.split() if token]
    while tokens and tokens[0] in modifier_set:
        tokens.pop(0)
    while tokens and tokens[0].startswith("<"):
        tokens.pop(0)
    if not tokens:
        return None

    name = tokens[-1]
    return_type = " ".join(tokens[:-1]) if len(tokens) > 1 else None
    is_constructor = (not return_type) or name == class_name

    return {
        "name": name,
        "returnType": return_type,
        "params": split_params(params_raw),
        "throwsList": throws_list,
        "isConstructor": is_constructor,
    }


def find_insertion_index(lines, method_start):
    """
    執行 find_insertion_index 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param lines: 此參數會影響函式的執行行為。
    :param method_start: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    insertion_index = method_start
    while insertion_index > 0 and lines[insertion_index - 1].strip().startswith("@"):
        insertion_index -= 1
    return insertion_index


def reorder_doc_before_annotations(lines):
    """
    執行 reorder_doc_before_annotations 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param lines: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    changed = False
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("@"):
            i += 1
            continue

        annotation_start = i
        annotation_end = i
        while annotation_end + 1 < len(lines) and lines[annotation_end + 1].strip().startswith("@"):
            annotation_end += 1

        probe = annotation_end + 1
        while probe < len(lines) and not lines[probe].strip():
            probe += 1

        if probe >= len(lines) or not lines[probe].strip().startswith("/**"):
            i = annotation_end + 1
            continue

        doc_end = probe
        while doc_end < len(lines) and "*/" not in lines[doc_end]:
            doc_end += 1
        if doc_end >= len(lines):
            i = annotation_end + 1
            continue

        annotations = lines[annotation_start : annotation_end + 1]
        spacing = lines[annotation_end + 1 : probe]
        javadoc = lines[probe : doc_end + 1]
        lines[annotation_start : doc_end + 1] = javadoc + spacing + annotations
        changed = True
        i = annotation_start + len(javadoc) + len(spacing) + len(annotations)

    return changed
