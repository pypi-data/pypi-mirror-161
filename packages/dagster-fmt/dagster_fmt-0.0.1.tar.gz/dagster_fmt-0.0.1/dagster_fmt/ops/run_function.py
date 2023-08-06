import ast
from typing import Any, Optional

from shared.insert import InsertText


def add_context_type_annotation(
    function_node: ast.FunctionDef, first_node, type_name: str = "OpExecutionContext"
) -> Optional[Any]:
    """Add the type annotation to optional context param in the op's execution function.

    For example,

    >>> @op
    >>> def my_op(context: OpExecutionContext):
    ...    ...

    Params
    ------
    function_node: ast.FunctionDef
        AST node for the op execution function

    Returns
    -------
    dagster_import_name: Optional[Any]
        If an annotation is added, the name of the module and name of the class to
        add an import for. In this case: ('dagster', 'OpExecutionContext')
    """
    if len(function_node.args.args) == 0:
        return

    possible_context_arg = function_node.args.args[0]

    if (
        possible_context_arg.arg == "context"
        and possible_context_arg.annotation is None
    ):
        return (
            InsertText.after_node(f": {type_name}", possible_context_arg),
            InsertText.before_node(f"from dagster import {type_name}\n", first_node),
        )


def type_out_resources():
    """
    convert
    -------

    context.resources.redshift.method(a, b, c)

    to
    --

    redshift: Any = context.resources.redshift

    redshift.method(a, b c)
    """


# if no return type in function signature, then add? or add to the `out` section?


def add_op_docstring(node):
    n_body = node.body[0]

    if (
        isinstance(n_body, ast.Expr)
        and isinstance(n_body.value, ast.Constant)
        and isinstance(n_body.value.value, str)
    ):
        if n_body.value.value.endswith("\n"):
            return

        return InsertText.after_node("\n", n_body)

    return InsertText.before_node('"""Op description"""\n', n_body, newline=True)
