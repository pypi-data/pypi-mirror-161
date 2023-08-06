from __future__ import annotations

import ast
from typing import Any, Generator, Tuple, Type

ANN001 = "ANN001: Use `|` instead of `Union` or `Optional`."
ANN002 = (
    "ANN002: Use built-in generics instead of typing implementations "
    + "(e.g. list instead of `List`)."
)

VisitorError = Tuple[int, int, str]
PluginErrorInfo = Tuple[int, int, str, Type[Any]]


def get_slice_expr(node: ast.Subscript) -> ast.expr:
    """
    Get slice expression from the subscript in all versions of python.

    It was changed in ``python3.9``.

    Before: ``ast.Subscript`` -> ``ast.Index`` -> ``ast.expr``
    After: ``ast.Subscript`` -> ``ast.expr``
    """
    return (
        node.slice.value  # type: ignore
        if isinstance(node.slice, ast.Index)
        else node.slice
    )


class UnionTypingVisitor(ast.NodeVisitor):
    """AST-based visitor that checks for usage of Union and Optional."""

    _union_names = ("Union", "Optional")

    def __init__(self) -> None:
        """Initializes visitor with an empty errors list."""
        self.errors: list[VisitorError] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Checks function annotations."""
        if self._has_union_been_used(node, node.returns):
            self.errors += [(node.lineno, node.col_offset, ANN001)]
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        """Checks arguments annotations."""
        if self._has_union_been_used(node, node.annotation):
            self.errors += [(node.lineno, node.col_offset, ANN001)]
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Checks assignment annotations."""
        if self._has_union_been_used(node, node.value):
            self.errors += [(node.lineno, node.col_offset, ANN001)]
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Checks variable type annotations."""
        if self._has_union_been_used(node, node.annotation):
            self.errors += [(node.lineno, node.col_offset, ANN001)]
        self.generic_visit(node)

    def _has_union_been_used(
        self,
        node: ast.FunctionDef | ast.arg | ast.Assign | ast.AnnAssign,
        annotate_node: ast.expr | None,
    ) -> bool:
        if not isinstance(annotate_node, ast.Subscript):
            return False

        union_used_in_node_name = (
            isinstance(annotate_node.value, ast.Name)
            and annotate_node.value.id in self._union_names
        )
        if union_used_in_node_name:
            return True

        union_used_in_node_attr = (
            isinstance(annotate_node.value, ast.Attribute)
            and annotate_node.value.attr in self._union_names
        )
        if union_used_in_node_attr:
            return True

        return self._has_union_been_used(
            node,
            get_slice_expr(annotate_node),
        )


class GenericTypesVisitor(ast.NodeVisitor):
    """AST-based visitor that checks for usage of non-generic instances."""

    _non_generic_names = (
        "Dict",
        "List",
        "Tuple",
        "Type",
        "Set",
    )

    def __init__(self) -> None:
        """Initializes visitor with an empty errors list."""
        self.errors: list[VisitorError] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Checks function annotations."""
        if self._has_invalid_keyword_been_used(node, node.returns):
            self.errors += [(node.lineno, node.col_offset, ANN002)]
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        """Checks arguments annotations."""
        if self._has_invalid_keyword_been_used(node, node.annotation):
            self.errors += [(node.lineno, node.col_offset, ANN002)]
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Checks assignment annotations."""
        if self._has_invalid_keyword_been_used(node, node.value):
            self.errors += [(node.lineno, node.col_offset, ANN002)]
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Checks variable type annotations."""
        if self._has_invalid_keyword_been_used(node, node.annotation):
            self.errors += [(node.lineno, node.col_offset, ANN002)]
        self.generic_visit(node)

    def _has_invalid_keyword_been_used(
        self,
        node: ast.FunctionDef | ast.arg | ast.Assign | ast.AnnAssign,
        annotate_node: ast.expr | None,
    ) -> bool:
        if not isinstance(annotate_node, ast.Subscript):
            return False

        union_used_in_node_name = (
            isinstance(annotate_node.value, ast.Name)
            and annotate_node.value.id in self._non_generic_names
        )
        if union_used_in_node_name:
            return True

        union_used_in_node_attr = (
            isinstance(annotate_node.value, ast.Attribute)
            and annotate_node.value.attr in self._non_generic_names
        )
        if union_used_in_node_attr:
            return True

        return self._has_invalid_keyword_been_used(
            node,
            get_slice_expr(annotate_node),
        )


class TypeAnnotationsPlugin:
    """
    Plugin for flake8 checking for common type annotation mistakes.

    ANN001 - disallows `Union` and `Optional` usages and encourages usage of
             a new `|` operator syntax. The usage of the new syntax can be
             enabled in earlier versions (Python 3.7+) via the
             `from __future__ import annotations` import.

    ANN002 - disallows usage of types where built-in alternative can be used,
             e.g. `List[]` instead of `list[]`, etc. The support for usage of
             generics in typing syntax has been added in Python 3.9, and is now
             the preferred way of annotating types. The usage of the new syntax
             can be enabled in earlier versions (Python 3.7+) via the
             `from __future__ import annotations` import.
    """

    name = __name__
    version = "1.0.0"

    def __init__(self, tree: ast.AST) -> None:
        """Initializes the plugin with the AST tree."""
        self._tree = tree

    def run(self) -> Generator[PluginErrorInfo, None, None]:
        """Runs the plugin checks."""
        for visitor_cls in (UnionTypingVisitor, GenericTypesVisitor):
            visitor = visitor_cls()
            visitor.visit(self._tree)

            for line, col, msg in visitor.errors:
                yield line, col, msg, type(self)
