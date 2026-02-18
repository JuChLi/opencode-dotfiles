#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Sequence


DEFAULT_INCLUDE_GLOBS = ["**/*.md"]
DEFAULT_EXCLUDE_GLOBS = [
    ".git/**",
    ".github/**",
    ".idea/**",
    ".vscode/**",
    "node_modules/**",
    "dist/**",
    "build/**",
    "coverage/**",
    ".venv/**",
    "venv/**",
    "__pycache__/**",
]

DEFAULT_DOC_TYPE_HINTS = {
    "tutorial": ["tutorial", "教學", "入門", "quickstart"],
    "how-to": ["how-to", "howto", "操作", "指南", "runbook", "plan"],
    "reference": ["reference", "api", "spec", "schema", "規格", "參考"],
    "explanation": ["explanation", "說明", "架構", "設計", "decision", "adr"],
    "handoff": ["handoff", "交接", "移交", "on-call"],
}

HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")


def load_json(file_path: str | Path) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"JSON file not found: {path}")
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def deep_merge(base: dict, override: dict | None) -> dict:
    result = dict(base)
    for key, override_value in (override or {}).items():
        base_value = result.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, dict):
            result[key] = deep_merge(base_value, override_value)
            continue
        result[key] = override_value
    return result


def resolve_style_file(style_file: str | None, cwd: str | Path | None = None) -> Path | None:
    if not style_file:
        return None
    path = Path(style_file)
    if path.is_absolute():
        return path
    base = Path(cwd) if cwd else Path.cwd()
    return (base / path).resolve()


def resolve_builtin_style_file(style_name: str, script_dir: Path) -> Path:
    normalized = (style_name or "google-zhtw").lower()
    style_path = script_dir / ".." / "references" / "style-profiles" / f"{normalized}.json"
    style_path = style_path.resolve()
    if not style_path.exists():
        raise ValueError(f"Unknown style profile: {style_name}. Expected file: {style_path}")
    return style_path


def resolve_extends_reference(extends_value: str, current_file: Path, script_dir: Path) -> Path:
    value = extends_value.strip()
    if not value:
        raise ValueError("The extends field cannot be empty.")

    if value.endswith(".json") or "/" in value or "\\" in value:
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = (current_file.parent / candidate).resolve()
        if not candidate.exists():
            raise ValueError(f"Extended style profile not found: {candidate}")
        return candidate

    return resolve_builtin_style_file(value, script_dir)


def load_profile_tree(profile_path: Path, script_dir: Path, seen: set[Path] | None = None) -> dict:
    seen = seen or set()
    current = profile_path.resolve()
    if current in seen:
        raise ValueError(f"Circular extends detected at {current}")
    seen.add(current)

    profile = load_json(current)
    extends_value = profile.get("extends")
    if isinstance(extends_value, str) and extends_value.strip():
        base_path = resolve_extends_reference(extends_value, current, script_dir)
        base_profile = load_profile_tree(base_path, script_dir, seen)
        profile = deep_merge(base_profile, profile)

    profile["source"] = str(current)
    return profile


def apply_profile_defaults(profile: dict) -> dict:
    merged_hints = deep_merge(DEFAULT_DOC_TYPE_HINTS, profile.get("docTypeHints") or {})
    profile["docTypeHints"] = merged_hints

    include = list(profile.get("includeGlobs") or DEFAULT_INCLUDE_GLOBS)
    profile["includeGlobs"] = include

    exclude = list(DEFAULT_EXCLUDE_GLOBS)
    for pattern in profile.get("excludeGlobs") or []:
        if pattern not in exclude:
            exclude.append(pattern)
    profile["excludeGlobs"] = exclude

    profile.setdefault("name", "google-zhtw")
    profile.setdefault("language", "zh-TW")
    profile.setdefault("defaultDocType", "how-to")
    profile.setdefault("structureRules", {})
    profile.setdefault("terminologyRules", {})
    profile.setdefault("proseRules", {})
    profile.setdefault("similarityRules", {})

    profile["terminologyRules"].setdefault("preferredTerms", {})
    profile["terminologyRules"].setdefault("bannedPatterns", [])

    profile["proseRules"].setdefault("maxLineLength", 120)
    profile["proseRules"].setdefault("maxParagraphLines", 8)
    profile["proseRules"].setdefault("discouragedPhrases", [])
    profile["proseRules"].setdefault("genericHeadings", [])

    profile["similarityRules"].setdefault("similarityThreshold", 0.9)
    profile["similarityRules"].setdefault("minLineLength", 12)

    return profile


def load_style_profile(style: str, style_file: str | None, script_dir: Path) -> dict:
    builtin_path = resolve_builtin_style_file(style, script_dir)
    profile = load_profile_tree(builtin_path, script_dir)

    custom_path = resolve_style_file(style_file)
    if custom_path:
        custom_profile = load_profile_tree(custom_path, script_dir)
        profile = deep_merge(profile, custom_profile)
        profile["source"] = str(custom_path)

    return apply_profile_defaults(profile)


def _matches_any_glob(relative_path: str, patterns: Sequence[str]) -> bool:
    normalized = relative_path.replace("\\", "/")
    pure = PurePosixPath(normalized)
    return any(pure.match(pattern) for pattern in patterns)


def collect_markdown_files(
    root: Path,
    include_globs: Sequence[str] | None,
    exclude_globs: Sequence[str] | None,
) -> list[Path]:
    resolved_root = root.resolve()
    include = list(include_globs or DEFAULT_INCLUDE_GLOBS)
    exclude = list(exclude_globs or DEFAULT_EXCLUDE_GLOBS)

    discovered: dict[Path, str] = {}
    for pattern in include:
        for path in resolved_root.glob(pattern):
            if not path.is_file() or path.suffix.lower() != ".md":
                continue
            relative = path.relative_to(resolved_root).as_posix()
            if _matches_any_glob(relative, exclude):
                continue
            discovered[path.resolve()] = relative

    return sorted(discovered.keys(), key=lambda path: discovered[path].lower())


def collect_files_from_args(args, profile: dict) -> list[Path]:
    root = Path(getattr(args, "root", ".")).resolve()
    include = getattr(args, "include", None) or profile.get("includeGlobs")
    exclude = list(profile.get("excludeGlobs") or [])
    exclude.extend(getattr(args, "exclude", []) or [])
    return collect_markdown_files(root, include, exclude)


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}

    data: dict[str, str] = {}
    for raw_line in lines[1:end_index]:
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            data[key] = value
    return data


def normalize_heading(text: str) -> str:
    normalized = text.strip().lower()
    normalized = re.sub(
        r"[\s`*_~:：;；,.，。!?！？()（）\[\]{}<>《》\"'“”‘’/\\|-]+",
        "",
        normalized,
    )
    return normalized


def extract_headings(text: str) -> list[tuple[int, int, str, str]]:
    headings: list[tuple[int, int, str, str]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        match = HEADING_RE.match(raw_line)
        if not match:
            continue
        level = len(match.group(1))
        heading_text = match.group(2).strip()
        headings.append((line_number, level, heading_text, normalize_heading(heading_text)))
    return headings


def infer_doc_type(file_path: Path, text: str, profile: dict) -> str:
    frontmatter = parse_frontmatter(text)
    supported_types = set(profile.get("structureRules", {}).keys())
    for key in ("doc_type", "docType", "type"):
        value = frontmatter.get(key)
        if value and (not supported_types or value in supported_types):
            return value

    target_name = file_path.stem.lower()
    target_tokens = set(re.findall(r"[a-z0-9-]+", target_name))
    first_heading = ""
    heading_tokens: set[str] = set()
    headings = extract_headings(text)
    if headings:
        first_heading = headings[0][2].lower()
        heading_tokens = set(re.findall(r"[a-z0-9-]+", first_heading))

    for doc_type, keywords in (profile.get("docTypeHints") or {}).items():
        for keyword in keywords:
            lowered = keyword.lower()
            is_ascii_keyword = bool(re.fullmatch(r"[a-z0-9-]+", lowered))
            if is_ascii_keyword:
                if lowered in target_tokens or lowered in heading_tokens:
                    return doc_type
                continue

            if lowered in target_name or (first_heading and lowered in first_heading):
                return doc_type

    default_doc_type = profile.get("defaultDocType", "how-to")
    if isinstance(default_doc_type, str) and default_doc_type:
        return default_doc_type
    return "how-to"
