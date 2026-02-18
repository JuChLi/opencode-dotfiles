#!/usr/bin/env python3

"""
style_profile_utils 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

from __future__ import annotations

import json
import re
from pathlib import Path


DEFAULT_FUNCTION_PREFIX_ORDER = [
    "get",
    "set",
    "is",
    "has",
    "load",
    "save",
    "parse",
    "build",
    "create",
    "validate",
    "fetch",
    "update",
]


def load_json(file_path: str) -> dict:
    """
    載入所需資料。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        file_path: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    
    Raises:
        ValueError: 當輸入不合法或處理失敗時拋出例外。
    """
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"Style file not found: {file_path}")
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def deep_merge(base: dict, override: dict | None) -> dict:
    """
    執行 deep_merge 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        base: 這個參數會影響函式的執行行為。
        override: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    result = dict(base)
    for key, override_value in (override or {}).items():
        base_value = result.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, dict):
            result[key] = deep_merge(base_value, override_value)
            continue
        result[key] = override_value
    return result


def resolve_style_file(style_file: str | None, cwd: str | None = None) -> str | None:
    """
    執行 resolve_style_file 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        style_file: 這個參數會影響函式的執行行為。
        cwd: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    if not style_file:
        return None
    path = Path(style_file)
    if path.is_absolute():
        return str(path)
    return str((Path(cwd or Path.cwd()) / path).resolve())


def resolve_builtin_style_file(style_name: str, script_dir: Path) -> str:
    """
    執行 resolve_builtin_style_file 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        style_name: 這個參數會影響函式的執行行為。
        script_dir: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    
    Raises:
        ValueError: 當輸入不合法或處理失敗時拋出例外。
    """
    normalized = (style_name or "pep257").lower()
    style_path = script_dir / ".." / "references" / "style-profiles" / f"{normalized}.json"
    style_path = style_path.resolve()
    if not style_path.exists():
        raise ValueError(f"Unknown style profile: {style_name}. Expected file: {style_path}")
    return str(style_path)


def load_style_profile(args, script_dir: Path) -> dict:
    """
    載入所需資料。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        args: 其他可選的位置參數。
        script_dir: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    
    Raises:
        ValueError: 當輸入不合法或處理失敗時拋出例外。
    """
    style = getattr(args, "style", "pep257")
    style_file = getattr(args, "style_file", None)

    builtin_path = resolve_builtin_style_file(style, script_dir)
    profile = load_json(builtin_path)

    custom_path = resolve_style_file(style_file)
    if custom_path:
        custom = load_json(custom_path)
        if custom.get("extends"):
            base_path = resolve_builtin_style_file(custom["extends"], script_dir)
            base = load_json(base_path)
            profile = deep_merge(base, custom)
        else:
            profile = deep_merge(profile, custom)
        profile["source"] = custom_path
    else:
        profile["source"] = builtin_path

    if not isinstance(profile.get("functionPrefixOrder"), list):
        profile["functionPrefixOrder"] = DEFAULT_FUNCTION_PREFIX_ORDER
    if not profile.get("functionSummary"):
        profile["functionSummary"] = {}
    if not profile.get("paramDescriptions"):
        profile["paramDescriptions"] = {}
    if not profile.get("paramFallback"):
        profile["paramFallback"] = {}
    if not profile.get("returnDescriptions"):
        profile["returnDescriptions"] = {}
    if not profile.get("yieldDescriptions"):
        profile["yieldDescriptions"] = {}
    if not profile.get("bannedPatterns"):
        profile["bannedPatterns"] = []
    if not profile.get("docstringFormat"):
        profile["docstringFormat"] = "rest"

    doc_format = str(profile.get("docstringFormat") or "rest").lower()
    if doc_format not in {"rest", "google"}:
        raise ValueError(
            f"Unsupported docstringFormat: {doc_format}. Only rest/google are allowed."
        )
    profile["docstringFormat"] = doc_format

    if "allowMissingDocstringForOverrides" not in profile:
        profile["allowMissingDocstringForOverrides"] = doc_format == "google"
    if "allowMissingModuleDocstringForTests" not in profile:
        profile["allowMissingModuleDocstringForTests"] = doc_format == "google"
    if "googleAllowOmitReturnsSectionWithSummaryVerb" not in profile:
        profile["googleAllowOmitReturnsSectionWithSummaryVerb"] = True
    if "enforceSummaryLineMaxLength" not in profile:
        profile["enforceSummaryLineMaxLength"] = doc_format == "google"
    if "summaryLineMaxLength" not in profile:
        profile["summaryLineMaxLength"] = 80
    if "requireDetailDescription" not in profile:
        profile["requireDetailDescription"] = doc_format != "google"
    if "enforceGoogleSectionEntries" not in profile:
        profile["enforceGoogleSectionEntries"] = doc_format == "google"
    if "enforceYieldsSectionForGenerators" not in profile:
        profile["enforceYieldsSectionForGenerators"] = doc_format == "google"
    if "requireGoogleExamples" not in profile:
        profile["requireGoogleExamples"] = bool(profile.get("includeExamples"))

    return profile


def render_template(template: str, values: dict | None = None) -> str:
    """
    執行 render_template 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        template: 這個參數會影響函式的執行行為。
        values: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    if not template:
        return ""
    values = values or {}

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in values:
            return str(values[key])
        return "{" + key + "}"

    return re.sub(r"\{([A-Za-z0-9_]+)\}", repl, template)


def normalize_param_name(name: str) -> str:
    """
    執行 normalize_param_name 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        name: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    return name.lstrip("*")


def choose_module_summary(profile: dict, module_name: str) -> str:
    """
    執行 choose_module_summary 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        module_name: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    template = profile.get("moduleSummary") or "{module} 模組的主要功能。"
    return render_template(template, {"module": module_name})


def choose_class_summary(profile: dict, class_name: str) -> str:
    """
    執行 choose_class_summary 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        class_name: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    template = profile.get("classSummary") or "{name} 的核心行為實作。"
    return render_template(template, {"name": class_name})


def choose_function_summary(profile: dict, target) -> str:
    """
    執行 choose_function_summary 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    summary = profile.get("functionSummary", {})

    if target.name in summary:
        return render_template(summary[target.name], {"name": target.name})

    if target.is_async and summary.get("async"):
        return render_template(summary["async"], {"name": target.name})

    for prefix in profile.get("functionPrefixOrder", DEFAULT_FUNCTION_PREFIX_ORDER):
        if target.name.startswith(prefix) and summary.get(prefix):
            return render_template(summary[prefix], {"name": target.name, "prefix": prefix})

    if summary.get("default"):
        return render_template(summary["default"], {"name": target.name})

    return render_template("執行 {name} 的核心流程並回傳結果。", {"name": target.name})


def choose_param_description(profile: dict, param_name: str) -> str:
    """
    執行 choose_param_description 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        param_name: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    normalized = normalize_param_name(param_name)
    direct = profile.get("paramDescriptions", {}).get(normalized)
    if direct:
        return direct

    fallback = profile.get("paramFallback", {})
    lower = normalized.lower()

    if lower.endswith("list") or lower.endswith("set") or lower.endswith("map"):
        return fallback.get("list") or fallback.get("collection") or "參數集合。"
    if lower.endswith("id"):
        return fallback.get("id") or "識別值。"
    if lower == "ms" or lower.endswith("_ms"):
        return fallback.get("ms") or "時間值（毫秒）。"
    if lower == "seconds" or lower.endswith("_seconds") or lower == "sec" or lower.endswith("_sec"):
        return fallback.get("seconds") or "時間值（秒）。"
    if lower.startswith("is_") or lower.startswith("has_"):
        return fallback.get("flag") or "狀態旗標。"

    return fallback.get("default") or "輸入參數。"


def choose_return_description(profile: dict, target) -> str | None:
    """
    執行 choose_return_description 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    return_rules = profile.get("returnDescriptions", {})

    if target.is_generator:
        return None

    annotation = (target.returns or "").strip()
    lower = annotation.lower()
    if annotation in {"None", "NoReturn"}:
        return return_rules.get("none")

    if target.is_async and return_rules.get("async"):
        return return_rules.get("async")

    if target.name.startswith("is") or target.name.startswith("has"):
        return return_rules.get("bool") or "條件判斷結果。"

    if lower in {"bool", "optional[bool]"}:
        return return_rules.get("bool") or "條件判斷結果。"

    if any(token in lower for token in ["list", "set", "dict", "tuple", "sequence", "mapping"]):
        return return_rules.get("collection") or "結果集合。"

    return return_rules.get("default")


def choose_yield_description(profile: dict, target) -> str | None:
    """
    執行 choose_yield_description 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    if not target.is_generator:
        return None

    rules = profile.get("yieldDescriptions", {})
    annotation = (target.returns or "").strip().lower()

    if any(token in annotation for token in ["tuple", "list", "dict", "set", "sequence", "iterator"]):
        return rules.get("collection") or "每次迭代產生的資料項目。"

    return rules.get("default") or "每次迭代產生的資料項目。"


def choose_raises_description(profile: dict, exc_name: str) -> str:
    """
    執行 choose_raises_description 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        exc_name: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    template = profile.get("raisesTemplate") or "當輸入不合法或處理失敗時拋出。"
    return render_template(template, {"exception": exc_name})


def choose_detail_description(profile: dict, target) -> str:
    """
    執行 choose_detail_description 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    if target.kind == "module":
        template = profile.get("moduleDetail") or "說明此模組的主要使用情境、限制條件與注意事項。"
        return render_template(template, {"module": target.name})

    if target.kind == "class":
        template = profile.get("classDetail") or "說明此類別管理的狀態、核心流程與建議使用方式。"
        return render_template(template, {"name": target.name})

    if target.is_async:
        template = profile.get("asyncFunctionDetail") or "說明此函式的主要流程、輸入限制與非同步完成語意。"
    else:
        template = profile.get("functionDetail") or "說明此函式的主要流程、輸入限制與輸出語意。"

    return render_template(template, {"name": target.name, "qualified_name": target.qualified_name})


def guess_example_value(param_name: str) -> str:
    """
    執行 guess_example_value 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        param_name: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    lower = param_name.lower()

    if "threshold" in lower:
        return "0.5"
    if "timeout" in lower:
        return "30"
    if "path" in lower or "file" in lower:
        return '"path/to/file"'
    if "data" in lower or "values" in lower or lower.endswith("list"):
        return "[0.1, 0.9]"
    if lower.endswith("id"):
        return "1"
    if lower.startswith("is_") or lower.startswith("has_") or lower.startswith("enable"):
        return "True"

    return '"value"'


def build_example_call(target) -> str:
    """
    執行 build_example_call 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    args: list[str] = []
    max_args = 3

    for param in target.params:
        if param.startswith("*"):
            continue
        normalized = normalize_param_name(param)
        args.append(f"{normalized}={guess_example_value(normalized)}")
        if len(args) >= max_args:
            break

    return f"{target.name}({', '.join(args)})"


def choose_example_lines(profile: dict, target, return_text: str | None) -> list[str]:
    """
    執行 choose_example_lines 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        target: 這個參數會影響函式的執行行為。
        return_text: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    if target.kind not in {"function", "method"}:
        return []
    if not profile.get("includeExamples"):
        return []

    output = profile.get("exampleResultTemplate")
    if not output:
        if return_text is None:
            output = "None"
        elif "是否" in return_text or "判斷" in return_text:
            output = "True"
        else:
            output = "..."

    return [
        "Examples:",
        f"    >>> {build_example_call(target)}",
        f"    {output}",
    ]


def build_rest_body(
    summary: str,
    detail: str,
    params: list[str],
    return_text: str | None,
    raises: list[str],
    profile: dict,
) -> list[str]:
    """
    執行 build_rest_body 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        summary: 這個參數會影響函式的執行行為。
        detail: 這個參數會影響函式的執行行為。
        params: 這個參數會影響函式的執行行為。
        return_text: 這個參數會影響函式的執行行為。
        raises: 這個參數會影響函式的執行行為。
        profile: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    lines = [summary]
    if detail:
        lines.extend(["", detail])

    if params or return_text or raises:
        lines.append("")

    for param in params:
        lines.append(f":param {normalize_param_name(param)}: {choose_param_description(profile, param)}")

    if return_text:
        lines.append(f":returns: {return_text}")

    for exc in raises:
        lines.append(f":raises {exc}: {choose_raises_description(profile, exc)}")

    return lines


def build_google_body(
    summary: str,
    detail: str,
    params: list[str],
    return_text: str | None,
    yield_text: str | None,
    raises: list[str],
    profile: dict,
    target,
) -> list[str]:
    """
    執行 build_google_body 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        summary: 這個參數會影響函式的執行行為。
        detail: 這個參數會影響函式的執行行為。
        params: 這個參數會影響函式的執行行為。
        return_text: 這個參數會影響函式的執行行為。
        yield_text: 這個參數會影響函式的執行行為。
        raises: 這個參數會影響函式的執行行為。
        profile: 這個參數會影響函式的執行行為。
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    lines = [summary]
    if detail:
        lines.extend(["", detail])

    if params:
        lines.append("")
        lines.append("Args:")
        for param in params:
            lines.append(f"    {param}: {choose_param_description(profile, param)}")

    if return_text:
        lines.append("")
        lines.append("Returns:")
        lines.append(f"    {return_text}")

    if yield_text:
        lines.append("")
        lines.append("Yields:")
        lines.append(f"    {yield_text}")

    if raises:
        lines.append("")
        lines.append("Raises:")
        for exc in raises:
            lines.append(f"    {exc}: {choose_raises_description(profile, exc)}")

    example_lines = choose_example_lines(profile, target, return_text)
    if example_lines:
        lines.append("")
        lines.extend(example_lines)

    return lines


def build_function_doc_body(profile: dict, target) -> list[str]:
    """
    執行 build_function_doc_body 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    summary = choose_function_summary(profile, target)
    detail = choose_detail_description(profile, target)
    params = target.params
    return_text = choose_return_description(profile, target)
    yield_text = choose_yield_description(profile, target)
    raises = target.raises

    fmt = (profile.get("docstringFormat") or "rest").lower()
    if fmt == "google":
        return build_google_body(summary, detail, params, return_text, yield_text, raises, profile, target)
    return build_rest_body(summary, detail, params, return_text, raises, profile)


def build_docstring_body(profile: dict, target) -> list[str]:
    """
    執行 build_docstring_body 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
        target: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    if target.kind == "module":
        summary = choose_module_summary(profile, target.name)
        detail = choose_detail_description(profile, target)
        if detail:
            return [summary, "", detail]
        return [summary]
    if target.kind == "class":
        summary = choose_class_summary(profile, target.name)
        detail = choose_detail_description(profile, target)
        if detail:
            return [summary, "", detail]
        return [summary]
    return build_function_doc_body(profile, target)


def normalize_banned_patterns(profile: dict) -> list[dict]:
    """
    執行 normalize_banned_patterns 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        profile: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    normalized = []
    for entry in profile.get("bannedPatterns", []):
        if isinstance(entry, str):
            normalized.append(
                {
                    "regex": re.compile(entry),
                    "reason": "命中禁止樣式規則",
                    "pattern": entry,
                }
            )
            continue

        pattern = entry.get("pattern", "")
        normalized.append(
            {
                "regex": re.compile(pattern),
                "reason": entry.get("reason") or "命中禁止樣式規則",
                "pattern": pattern,
            }
        )
    return normalized
