import ast
from typing import List, Tuple

from dagster_fmt.shared.insert import InsertText
from dagster_fmt.shared.read_context import get_config_field_names


def is_resource_node(node) -> bool:
    # the hastattr makes sure not to include ops with some
    # config already
    return isinstance(node, ast.FunctionDef) and any(
        [hasattr(n, "id") and "resource" == n.id for n in node.decorator_list]
    )


def get_resource_decorator_node(node: ast.FunctionDef):

    for decorator in node.decorator_list:

        if decorator.id == "resource":
            return decorator


def create_resource_config(
    config_names: List[str], config
) -> Tuple[Tuple[str, str], bool]:
    if len(config_names) == 0:
        return "", False

    desc = 'description="", ' if config.resources.add_descriptions else ""
    is_req = "is_required=True, " if config.resources.add_is_required else ""

    return (
        (
            "config_schema={"
            + ",".join(
                [
                    f'"{c}": Field(config=dagster.Any, {desc}{is_req}default_value=None)'
                    for c in config_names
                ]
            )
            + "},",
            "import dagster\nfrom dagster import Field\n",
        ),
        True,
    )


def add_resource_decorator(node: ast.FunctionDef, config, first_node):
    output = []

    decorator_node = get_resource_decorator_node(node)

    (decorator_config, imports), include = create_resource_config(
        get_config_field_names("resource_config", node), config
    )
    if include:
        output.append(InsertText.after_node(decorator_config, decorator_node))
        output.append(InsertText.before_node(imports, first_node))

    return [
        InsertText("(", decorator_node.lineno - 1, decorator_node.end_col_offset),
        *output,
        InsertText(")", decorator_node.lineno - 1, decorator_node.end_col_offset),
    ]


def add_resource_docstring(node):
    n_body = node.body[0]

    if (
        isinstance(n_body, ast.Expr)
        and isinstance(n_body.value, ast.Constant)
        and isinstance(n_body.value.value, str)
    ):
        if n_body.value.value.endswith("\n"):
            return

        return InsertText.after_node("\n", n_body)

    return InsertText.before_node('"""Resource description"""\n', n_body, newline=True)
