#!/usr/bin/env python3

"""
pydoc_utils 模組的主要功能。

說明此模組的主要使用情境、限制條件與注意事項。
"""

from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


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
    """
    ScriptArgs 的核心行為實作。
    
    說明此類別管理的狀態、核心流程與建議使用方式。
    """
    root: str = "."
    include_private: bool = False
    json: bool = False
    top: int = 20
    style: str = "pep257"
    style_file: Optional[str] = None


@dataclass
class DocTarget:
    """
    DocTarget 的核心行為實作。
    
    說明此類別管理的狀態、核心流程與建議使用方式。
    """
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
    decorators: list[str] = field(default_factory=list)
    is_generator: bool = False
    is_override: bool = False


def parse_args(argv: list[str]) -> ScriptArgs:
    """
    將輸入內容解析為可用資料。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        argv: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
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


def resolve_root(root_arg: str) -> str:
    """
    執行 resolve_root 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        root_arg: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    
    Raises:
        ValueError: 當輸入不合法或處理失敗時拋出例外。
    """
    root = Path(root_arg)
    if not root.is_absolute():
        root = Path.cwd() / root
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Root path does not exist or is not a directory: {root}")
    return str(root)


def list_python_files(directory: str) -> list[str]:
    """
    執行 list_python_files 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        directory: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    root = Path(directory)
    files: list[str] = []

    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = [name for name in sorted(dir_names) if name not in SKIP_DIRS and not name.startswith(".")]
        for name in sorted(file_names):
            if name.endswith(".py"):
                files.append(str(Path(current_root) / name))

    return files


def relative_path(file_path: str, root: str) -> str:
    """
    執行 relative_path 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        file_path: 這個參數會影響函式的執行行為。
        root: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    return os.path.relpath(file_path, root).replace("\\", "/")


def detect_eol(content: str) -> str:
    """
    執行 detect_eol 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        content: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    return "\r\n" if "\r\n" in content else "\n"


def split_lines(content: str) -> list[str]:
    """
    執行 split_lines 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        content: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    return re.split(r"\r?\n", content)


def parse_python_source(file_path: str) -> tuple[str, ast.Module]:
    """
    將輸入內容解析為可用資料。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        file_path: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    raw = Path(file_path).read_text(encoding="utf-8")
    tree = ast.parse(raw, filename=file_path)
    return raw, tree


def is_docstring_expr(node: ast.AST) -> bool:
    """
    回傳目前是否符合條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        node: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    if not isinstance(node, ast.Expr):
        return False
    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
        return True
    ast_module: Any = ast
    ast_str = getattr(ast_module, "Str", None)
    if ast_str is not None and isinstance(node.value, ast_str):
        return True
    return False


def get_doc_node(node: ast.AST) -> Optional[ast.Expr]:
    """
    回傳目前值或狀態。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        node: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
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
    """
    執行 module_insert_line 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        lines: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    line_no = 1
    if lines and lines[0].startswith("#!"):
        line_no = 2

    if len(lines) >= line_no and re.match(r"^#.*coding[:=]", lines[line_no - 1]):
        line_no += 1

    while len(lines) >= line_no and not lines[line_no - 1].strip():
        line_no += 1

    return min(line_no, len(lines) + 1)


def line_indent(lines: list[str], line_no: int, fallback_spaces: int = 0) -> str:
    """
    執行 line_indent 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        lines: 這個參數會影響函式的執行行為。
        line_no: 這個參數會影響函式的執行行為。
        fallback_spaces: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    if 1 <= line_no <= len(lines):
        match = re.match(r"^[ \t]*", lines[line_no - 1])
        if match:
            return match.group(0)
    return " " * fallback_spaces


def stringify_annotation(node: Optional[ast.AST]) -> Optional[str]:
    """
    執行 stringify_annotation 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        node: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    if node is None:
        return None
    try:
        return ast.unparse(node).strip()
    except Exception:  # noqa: BLE001
        return None


def extract_params(node: ast.FunctionDef | ast.AsyncFunctionDef, is_method: bool) -> list[str]:
    """
    執行 extract_params 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        node: 這個參數會影響函式的執行行為。
        is_method: 狀態旗標。
    
    Returns:
        符合條件的結果集合。
    """
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
    """
    執行 extract_raise_name 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        exc: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    if isinstance(exc, ast.Call):
        return extract_raise_name(exc.func)
    if isinstance(exc, ast.Name):
        return exc.id
    if isinstance(exc, ast.Attribute):
        return exc.attr
    return "Exception"


def decorator_name(node: ast.AST) -> Optional[str]:
    """
    執行 decorator_name 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        node: 這個參數會影響函式的執行行為。
    
    Returns:
        函式執行後回傳的結果。
    """
    current = node
    if isinstance(current, ast.Call):
        current = current.func

    if isinstance(current, ast.Name):
        return current.id

    if isinstance(current, ast.Attribute):
        parts = [current.attr]
        value = current.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        parts.reverse()
        return ".".join(parts)

    return None


def collect_decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """
    執行 collect_decorator_names 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        node: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    names = []
    for decorator in node.decorator_list:
        name = decorator_name(decorator)
        if name:
            names.append(name)
    return names


def has_override_decorator(decorators: list[str]) -> bool:
    """
    回傳目前是否具備指定條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        decorators: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    for name in decorators:
        lower = name.lower()
        if lower == "override" or lower.endswith(".override"):
            return True
    return False


class YieldCollector(ast.NodeVisitor):
    """
    YieldCollector 的核心行為實作。

    說明此類別管理的狀態、核心流程與建議使用方式。
    """

    def __init__(self) -> None:
        """
        初始化 __init__ 所需的狀態。

        說明此函式的主要流程、輸入限制與輸出語意。
        """
        self.found = False

    def visit_Yield(self, node: ast.Yield) -> None:  # noqa: N802
        """
        執行 visit_Yield 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        self.found = True

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:  # noqa: N802
        """
        執行 visit_YieldFrom 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        self.found = True

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        """
        執行 visit_FunctionDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        """
        執行 visit_AsyncFunctionDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        """
        執行 visit_ClassDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        return


def is_generator_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    回傳目前是否符合條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        node: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    collector = YieldCollector()
    for stmt in node.body:
        collector.visit(stmt)
        if collector.found:
            return True
    return False


class RaiseCollector(ast.NodeVisitor):
    """
    RaiseCollector 的核心行為實作。
    
    說明此類別管理的狀態、核心流程與建議使用方式。
    """
    def __init__(self) -> None:
        """
        初始化 __init__ 所需的狀態。
        
        說明此函式的主要流程、輸入限制與輸出語意。
        """
        self.names: set[str] = set()

    def visit_Raise(self, node: ast.Raise) -> None:  # noqa: N802
        """
        執行 visit_Raise 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        if node.exc is not None:
            self.names.add(extract_raise_name(node.exc))
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        """
        執行 visit_FunctionDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        """
        執行 visit_AsyncFunctionDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        """
        執行 visit_ClassDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        return


def collect_raises(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """
    執行 collect_raises 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        node: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    collector = RaiseCollector()
    for stmt in node.body:
        collector.visit(stmt)
    return sorted(collector.names)


def is_public_name(name: str, include_private: bool) -> bool:
    """
    回傳目前是否符合條件。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        name: 這個參數會影響函式的執行行為。
        include_private: 這個參數會影響函式的執行行為。
    
    Returns:
        是否符合條件。
    """
    if include_private:
        return True
    if name in SPECIAL_PUBLIC_METHODS:
        return True
    return not name.startswith("_")


class TargetCollector(ast.NodeVisitor):
    """
    TargetCollector 的核心行為實作。
    
    說明此類別管理的狀態、核心流程與建議使用方式。
    """
    def __init__(self, lines: list[str], include_private: bool, module_name: str) -> None:
        """
        建立物件並初始化必要狀態。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            lines: 這個參數會影響函式的執行行為。
            include_private: 這個參數會影響函式的執行行為。
            module_name: 這個參數會影響函式的執行行為。
        """
        self.lines = lines
        self.include_private = include_private
        self.module_name = module_name
        self.class_stack: list[str] = []
        self.class_visibility_stack: list[bool] = []
        self.targets: list[DocTarget] = []

    def collect(self, tree: ast.Module) -> list[DocTarget]:
        """
        執行 collect 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            tree: 這個參數會影響函式的執行行為。
        
        Returns:
            符合條件的結果集合。
        """
        self.targets.append(self._build_module_target(tree))
        for stmt in tree.body:
            self.visit(stmt)
        return self.targets

    def _build_module_target(self, node: ast.Module) -> DocTarget:
        """
        執行 _build_module_target 的核心流程並回傳結果。
        
        說明此函式的主要流程、輸入限制與輸出語意。
        
        :param node: 此參數會影響函式的執行行為。
        :returns: 函式回傳結果。
        """
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
        """
        執行 visit_ClassDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
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
        """
        執行 visit_FunctionDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        self._visit_function_like(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        """
        執行 visit_AsyncFunctionDef 的核心流程並回傳結果。
        
        說明函式處理流程、輸入限制與輸出語意。
        
        Args:
            node: 這個參數會影響函式的執行行為。
        """
        self._visit_function_like(node, is_async=True)

    def _visit_function_like(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool) -> None:
        """
        執行 _visit_function_like 的核心流程並回傳結果。
        
        說明此函式的主要流程、輸入限制與輸出語意。
        
        :param node: 此參數會影響函式的執行行為。
        :param is_async: 狀態旗標。
        """
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
        decorators = collect_decorator_names(node)
        is_generator = is_generator_function(node)
        is_override = in_class and has_override_decorator(decorators)

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
                decorators=decorators,
                is_generator=is_generator,
                is_override=is_override,
            )
        )


def collect_doc_targets(raw: str, tree: ast.Module, file_path: str, include_private: bool) -> list[DocTarget]:
    """
    執行 collect_doc_targets 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        raw: 這個參數會影響函式的執行行為。
        tree: 這個參數會影響函式的執行行為。
        file_path: 這個參數會影響函式的執行行為。
        include_private: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    lines = split_lines(raw)
    module_name = Path(file_path).stem
    collector = TargetCollector(lines=lines, include_private=include_private, module_name=module_name)
    return collector.collect(tree)


def render_docstring_block(body_lines: list[str], indent: str) -> list[str]:
    """
    執行 render_docstring_block 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        body_lines: 這個參數會影響函式的執行行為。
        indent: 這個參數會影響函式的執行行為。
    
    Returns:
        符合條件的結果集合。
    """
    lines = ['"""']
    lines.extend(body_lines)
    lines.append('"""')
    return [f"{indent}{line}" if line else indent for line in lines]


def apply_insertions(lines: list[str], insertions: list[tuple[int, list[str]]]) -> None:
    """
    執行 apply_insertions 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        lines: 這個參數會影響函式的執行行為。
        insertions: 這個參數會影響函式的執行行為。
    """
    for line_no, new_lines in sorted(insertions, key=lambda item: item[0], reverse=True):
        index = max(0, min(line_no - 1, len(lines)))
        lines[index:index] = new_lines


def apply_replacements(lines: list[str], replacements: list[tuple[int, int, list[str]]]) -> None:
    """
    執行 apply_replacements 的核心流程並回傳結果。
    
    說明函式處理流程、輸入限制與輸出語意。
    
    Args:
        lines: 這個參數會影響函式的執行行為。
        replacements: 這個參數會影響函式的執行行為。
    """
    for start_line, end_line, new_lines in sorted(replacements, key=lambda item: item[0], reverse=True):
        start_index = max(0, start_line - 1)
        end_index = max(start_index, end_line)
        lines[start_index:end_index] = new_lines
