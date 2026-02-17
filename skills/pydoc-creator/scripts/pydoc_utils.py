#!/usr/bin/env python3

from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


SPECIAL_PUBLIC_METHODS = {
    "__init__",
    "__call__",
    "__enter__",
    "__exit__",
    "__aenter__",
    "__aexit__",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
}


@dataclass
class ScriptArgs:
    root: str = "."
    include_private: bool = False
    json: bool = False
    top: int = 20
    style: str = "pep257"
    style_file: Optional[str] = None


@dataclass
class DocTarget:
    kind: str
    name: str
    qualified_name: str
    lineno: int
    insert_line: int
    indent: str
    has_docstring: bool
    docstring: Optional[str]
    doc_start_line: Optional[int]
    doc_end_line: Optional[int]
    params: list[str]
    returns: Optional[str]
    raises: list[str]
    is_async: bool


def parse_args(argv: list[str]) -> ScriptArgs:
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


def resolve_root(root_arg: str) -> str:
    root = Path(root_arg)
    if not root.is_absolute():
        root = Path.cwd() / root
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Root path does not exist or is not a directory: {root}")
    return str(root)


def list_python_files(directory: str) -> list[str]:
    root = Path(directory)
    files: list[str] = []

    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = [name for name in sorted(dir_names) if name not in SKIP_DIRS and not name.startswith(".")]
        for name in sorted(file_names):
            if name.endswith(".py"):
                files.append(str(Path(current_root) / name))

    return files


def relative_path(file_path: str, root: str) -> str:
    return os.path.relpath(file_path, root).replace("\\", "/")


def detect_eol(content: str) -> str:
    return "\r\n" if "\r\n" in content else "\n"


def split_lines(content: str) -> list[str]:
    return re.split(r"\r?\n", content)


def parse_python_source(file_path: str) -> tuple[str, ast.Module]:
    raw = Path(file_path).read_text(encoding="utf-8")
    tree = ast.parse(raw, filename=file_path)
    return raw, tree


def is_docstring_expr(node: ast.AST) -> bool:
    if not isinstance(node, ast.Expr):
        return False
    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
        return True
    if hasattr(ast, "Str") and isinstance(node.value, ast.Str):
        return True
    return False


def get_doc_node(node: ast.AST) -> Optional[ast.Expr]:
    if not hasattr(node, "body"):
        return None
    body = getattr(node, "body", None)
    if not isinstance(body, list) or not body:
        return None
    first = body[0]
    if is_docstring_expr(first):
        return first
    return None


def module_insert_line(lines: list[str]) -> int:
    line_no = 1
    if lines and lines[0].startswith("#!"):
        line_no = 2

    if len(lines) >= line_no and re.match(r"^#.*coding[:=]", lines[line_no - 1]):
        line_no += 1

    while len(lines) >= line_no and not lines[line_no - 1].strip():
        line_no += 1

    return min(line_no, len(lines) + 1)


def line_indent(lines: list[str], line_no: int, fallback_spaces: int = 0) -> str:
    if 1 <= line_no <= len(lines):
        match = re.match(r"^[ \t]*", lines[line_no - 1])
        if match:
            return match.group(0)
    return " " * fallback_spaces


def stringify_annotation(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    try:
        return ast.unparse(node).strip()
    except Exception:  # noqa: BLE001
        return None


def extract_params(node: ast.FunctionDef | ast.AsyncFunctionDef, is_method: bool) -> list[str]:
    names: list[str] = []

    ordered_args = list(node.args.posonlyargs) + list(node.args.args)
    if is_method and ordered_args and ordered_args[0].arg in {"self", "cls"}:
        ordered_args = ordered_args[1:]

    names.extend(arg.arg for arg in ordered_args)

    if node.args.vararg:
        names.append(f"*{node.args.vararg.arg}")

    names.extend(arg.arg for arg in node.args.kwonlyargs)

    if node.args.kwarg:
        names.append(f"**{node.args.kwarg.arg}")

    return names


def extract_raise_name(exc: ast.AST) -> str:
    if isinstance(exc, ast.Call):
        return extract_raise_name(exc.func)
    if isinstance(exc, ast.Name):
        return exc.id
    if isinstance(exc, ast.Attribute):
        return exc.attr
    return "Exception"


class RaiseCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Raise(self, node: ast.Raise) -> None:  # noqa: N802
        if node.exc is not None:
            self.names.add(extract_raise_name(node.exc))
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        return


def collect_raises(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    collector = RaiseCollector()
    for stmt in node.body:
        collector.visit(stmt)
    return sorted(collector.names)


def is_public_name(name: str, include_private: bool) -> bool:
    if include_private:
        return True
    if name in SPECIAL_PUBLIC_METHODS:
        return True
    return not name.startswith("_")


class TargetCollector(ast.NodeVisitor):
    def __init__(self, lines: list[str], include_private: bool, module_name: str) -> None:
        self.lines = lines
        self.include_private = include_private
        self.module_name = module_name
        self.class_stack: list[str] = []
        self.class_visibility_stack: list[bool] = []
        self.targets: list[DocTarget] = []

    def collect(self, tree: ast.Module) -> list[DocTarget]:
        self.targets.append(self._build_module_target(tree))
        for stmt in tree.body:
            self.visit(stmt)
        return self.targets

    def _build_module_target(self, node: ast.Module) -> DocTarget:
        doc_node = get_doc_node(node)
        has_doc = ast.get_docstring(node, clean=False) is not None
        return DocTarget(
            kind="module",
            name=self.module_name,
            qualified_name=self.module_name,
            lineno=1,
            insert_line=module_insert_line(self.lines),
            indent="",
            has_docstring=has_doc,
            docstring=ast.get_docstring(node, clean=False),
            doc_start_line=getattr(doc_node, "lineno", None),
            doc_end_line=getattr(doc_node, "end_lineno", None),
            params=[],
            returns=None,
            raises=[],
            is_async=False,
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        visible = is_public_name(node.name, self.include_private)
        if visible:
            doc_node = get_doc_node(node)
            has_doc = ast.get_docstring(node, clean=False) is not None
            insert_line = node.body[0].lineno if node.body else node.lineno + 1
            indent = line_indent(self.lines, insert_line, node.col_offset + 4)
            qualified = ".".join(self.class_stack + [node.name]) if self.class_stack else node.name
            self.targets.append(
                DocTarget(
                    kind="class",
                    name=node.name,
                    qualified_name=qualified,
                    lineno=node.lineno,
                    insert_line=insert_line,
                    indent=indent,
                    has_docstring=has_doc,
                    docstring=ast.get_docstring(node, clean=False),
                    doc_start_line=getattr(doc_node, "lineno", None),
                    doc_end_line=getattr(doc_node, "end_lineno", None),
                    params=[],
                    returns=None,
                    raises=[],
                    is_async=False,
                )
            )

        self.class_stack.append(node.name)
        self.class_visibility_stack.append(visible)
        for stmt in node.body:
            self.visit(stmt)
        self.class_stack.pop()
        self.class_visibility_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._visit_function_like(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._visit_function_like(node, is_async=True)

    def _visit_function_like(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool) -> None:
        in_class = len(self.class_stack) > 0
        kind = "method" if in_class else "function"

        class_visible = all(self.class_visibility_stack) if self.class_visibility_stack else True
        visible = is_public_name(node.name, self.include_private)
        if not class_visible and not self.include_private:
            visible = False

        if not visible:
            return

        doc_node = get_doc_node(node)
        has_doc = ast.get_docstring(node, clean=False) is not None
        insert_line = node.body[0].lineno if node.body else node.lineno + 1
        indent = line_indent(self.lines, insert_line, node.col_offset + 4)

        if in_class:
            qualified_name = ".".join(self.class_stack + [node.name])
        else:
            qualified_name = node.name

        self.targets.append(
            DocTarget(
                kind=kind,
                name=node.name,
                qualified_name=qualified_name,
                lineno=node.lineno,
                insert_line=insert_line,
                indent=indent,
                has_docstring=has_doc,
                docstring=ast.get_docstring(node, clean=False),
                doc_start_line=getattr(doc_node, "lineno", None),
                doc_end_line=getattr(doc_node, "end_lineno", None),
                params=extract_params(node, is_method=in_class),
                returns=stringify_annotation(node.returns),
                raises=collect_raises(node),
                is_async=is_async,
            )
        )


def collect_doc_targets(raw: str, tree: ast.Module, file_path: str, include_private: bool) -> list[DocTarget]:
    lines = split_lines(raw)
    module_name = Path(file_path).stem
    collector = TargetCollector(lines=lines, include_private=include_private, module_name=module_name)
    return collector.collect(tree)


def render_docstring_block(body_lines: list[str], indent: str) -> list[str]:
    lines = ['"""']
    lines.extend(body_lines)
    lines.append('"""')
    return [f"{indent}{line}" if line else indent for line in lines]


def apply_insertions(lines: list[str], insertions: list[tuple[int, list[str]]]) -> None:
    for line_no, new_lines in sorted(insertions, key=lambda item: item[0], reverse=True):
        index = max(0, min(line_no - 1, len(lines)))
        lines[index:index] = new_lines


def apply_replacements(lines: list[str], replacements: list[tuple[int, int, list[str]]]) -> None:
    for start_line, end_line, new_lines in sorted(replacements, key=lambda item: item[0], reverse=True):
        start_index = max(0, start_line - 1)
        end_index = max(start_index, end_line)
        lines[start_index:end_index] = new_lines
