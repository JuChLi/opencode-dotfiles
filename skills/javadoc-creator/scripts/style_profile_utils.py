#!/usr/bin/env python3

"""
style_profile_utils 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

import json
import re
from pathlib import Path


DEFAULT_PREFIX_ORDER = [
    "get",
    "set",
    "is",
    "has",
    "start",
    "stop",
    "shutdown",
    "initialize",
    "init",
    "collect",
    "fetch",
    "handle",
    "parse",
    "build",
    "load",
    "save",
    "publish",
    "reset",
    "toJson",
    "to",
    "create",
]

DEFAULT_DOCLET_SPEC_SOURCE = (
    "https://docs.oracle.com/en/java/javase/21/docs/specs/javadoc/doc-comment-spec.html"
)

DEFAULT_TAG_ORDER = ["param", "return", "throws"]


def load_json(file_path):
    """
    載入目標資料或設定。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param file_path: 檔案路徑。
    :returns: 函式回傳結果。
    :raises ValueError: 當輸入不合法或處理失敗時拋出。
    """
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"Style file not found: {file_path}")
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def deep_merge(base, override):
    """
    執行 deep_merge 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param base: 此參數會影響函式的執行行為。
    :param override: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    result = dict(base)
    for key, override_value in (override or {}).items():
        base_value = result.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, dict):
            result[key] = deep_merge(base_value, override_value)
            continue
        result[key] = override_value
    return result


def resolve_style_file(style_file, cwd=None):
    """
    執行 resolve_style_file 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param style_file: 此參數會影響函式的執行行為。
    :param cwd: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    if not style_file:
        return None
    path = Path(style_file)
    if path.is_absolute():
        return str(path)
    return str((Path(cwd or Path.cwd()) / path).resolve())


def resolve_builtin_style_file(style_name, script_dir):
    """
    執行 resolve_builtin_style_file 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param style_name: 此參數會影響函式的執行行為。
    :param script_dir: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    :raises ValueError: 當輸入不合法或處理失敗時拋出。
    """
    normalized = (style_name or "vertx").lower()
    style_path = Path(script_dir) / ".." / "references" / "style-profiles" / f"{normalized}.json"
    style_path = style_path.resolve()
    if not style_path.exists():
        raise ValueError(f"Unknown style profile: {style_name}. Expected file: {style_path}")
    return str(style_path)


def load_style_profile(args, script_dir):
    """
    載入目標資料或設定。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param args: 其他位置參數。
    :param script_dir: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    style = getattr(args, "style", "vertx")
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

    if not isinstance(profile.get("methodPrefixOrder"), list):
        profile["methodPrefixOrder"] = DEFAULT_PREFIX_ORDER
    if not profile.get("paramDescriptions"):
        profile["paramDescriptions"] = {}
    if not profile.get("paramFallback"):
        profile["paramFallback"] = {}
    if not profile.get("returnDescriptions"):
        profile["returnDescriptions"] = {}
    if not profile.get("methodSummary"):
        profile["methodSummary"] = {}
    if not profile.get("typeSummary"):
        profile["typeSummary"] = {}
    if not profile.get("bannedPatterns"):
        profile["bannedPatterns"] = []

    if not isinstance(profile.get("docletSpec"), dict):
        profile["docletSpec"] = {}

    doclet_spec = profile["docletSpec"]
    doclet_spec.setdefault(
        "source",
        DEFAULT_DOCLET_SPEC_SOURCE,
    )
    doclet_spec.setdefault("enforceSummarySentence", True)
    doclet_spec.setdefault("enforceSummaryFragment", False)
    doclet_spec.setdefault("summaryDisallowPatterns", [])
    doclet_spec.setdefault("enforceTagOrder", True)
    doclet_spec.setdefault("tagOrder", list(DEFAULT_TAG_ORDER))
    doclet_spec.setdefault("requireParamTags", True)
    doclet_spec.setdefault("requireReturnTagForNonVoid", True)
    doclet_spec.setdefault("forbidReturnTagForVoidOrConstructor", True)
    doclet_spec.setdefault("requireDeclaredThrowsTags", True)
    doclet_spec.setdefault("requireNonEmptyTagDescription", True)
    doclet_spec.setdefault("requireDeprecatedDescription", False)
    doclet_spec.setdefault("requireDeprecatedReplacementLink", False)
    doclet_spec.setdefault("allowMissingJavadocForOverrides", False)

    return profile


def render_template(template, values=None):
    """
    執行 render_template 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param template: 此參數會影響函式的執行行為。
    :param values: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    if not template:
        return ""
    values = values or {}

    def repl(match):
        key = match.group(1)
        if key in values:
            return str(values[key])
        return "{" + key + "}"

    return re.sub(r"\{([A-Za-z0-9_]+)\}", repl, template)


def choose_type_summary(profile, type_info):
    """
    執行 choose_type_summary 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param profile: 此參數會影響函式的執行行為。
    :param type_info: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    kind = type_info["kind"]
    name = type_info["name"]
    suffix_rules = profile.get("typeSuffixRules", {})
    type_summary = profile.get("typeSummary", {})

    if kind == "interface" and type_summary.get("interface"):
        return render_template(type_summary["interface"], {"name": name, "kind": kind})
    if kind == "enum" and type_summary.get("enum"):
        return render_template(type_summary["enum"], {"name": name, "kind": kind})

    for suffix, template in suffix_rules.items():
        if name.endswith(suffix):
            return render_template(template, {"name": name, "kind": kind, "suffix": suffix})

    if type_summary.get("class"):
        return render_template(type_summary["class"], {"name": name, "kind": kind})
    if type_summary.get("default"):
        return render_template(type_summary["default"], {"name": name, "kind": kind})
    return f"{name} 的主要實作。"


def choose_method_summary(profile, method_info):
    """
    執行 choose_method_summary 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param profile: 此參數會影響函式的執行行為。
    :param method_info: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    method_summary = profile.get("methodSummary", {})

    if method_info.get("isConstructor") and method_summary.get("constructor"):
        return render_template(method_summary["constructor"], {"name": method_info["name"]})

    for prefix in profile.get("methodPrefixOrder", DEFAULT_PREFIX_ORDER):
        if method_info["name"].startswith(prefix) and method_summary.get(prefix):
            return render_template(method_summary[prefix], {"name": method_info["name"], "prefix": prefix})

    if method_summary.get("default"):
        return render_template(method_summary["default"], {"name": method_info["name"]})

    return "執行此方法的主要處理流程。"


def choose_param_description(profile, param_name):
    """
    執行 choose_param_description 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param profile: 此參數會影響函式的執行行為。
    :param param_name: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    direct = profile.get("paramDescriptions", {}).get(param_name)
    if direct:
        return direct

    fallback = profile.get("paramFallback", {})
    if param_name.endswith("List") or param_name.endswith("Set") or param_name.endswith("Map"):
        return fallback.get("list") or fallback.get("collection") or "參數集合。"
    if param_name.endswith("Id") or param_name.endswith("ID"):
        return fallback.get("id") or "識別值。"
    if param_name.endswith("Ms"):
        return fallback.get("ms") or "時間值（毫秒）。"
    if param_name.endswith("Seconds"):
        return fallback.get("seconds") or "時間值（秒）。"
    if param_name.endswith("Threshold"):
        return fallback.get("threshold") or "門檻值。"
    if param_name.startswith("is") or param_name.startswith("has"):
        return fallback.get("flag") or "狀態旗標。"

    return fallback.get("default") or "輸入參數。"


def choose_return_description(profile, return_type):
    """
    執行 choose_return_description 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param profile: 此參數會影響函式的執行行為。
    :param return_type: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
    """
    if not return_type or return_type == "void":
        return None

    return_descriptions = profile.get("returnDescriptions", {})
    if "Future<" in return_type or return_type == "Future":
        return return_descriptions.get("future") or "非同步處理結果。"
    if return_type in {"boolean", "Boolean"}:
        return return_descriptions.get("boolean") or "判斷結果。"
    if "List" in return_type or "Set" in return_type or "Map" in return_type:
        return return_descriptions.get("collection") or "結果集合。"
    return return_descriptions.get("default") or "方法回傳結果。"


def normalize_banned_patterns(profile):
    """
    執行 normalize_banned_patterns 的核心流程並回傳結果。
    
    說明此函式的主要流程、輸入限制與輸出語意。
    
    :param profile: 此參數會影響函式的執行行為。
    :returns: 函式回傳結果。
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
