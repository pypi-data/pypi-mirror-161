import ast
import os
import subprocess
from pathlib import Path

from dagster_fmt.ops import add_op_decorator, is_op_node
from dagster_fmt.ops.run_function import add_context_type_annotation, add_op_docstring
from dagster_fmt.resources import (
    add_resource_decorator,
    add_resource_docstring,
    is_resource_node,
)
from dagster_fmt.shared.insert import write_file
from dagster_fmt.tool.schema import Configuration


def run_on_file(file_name, config):
    with open(file_name, "r") as file:
        file_contents = file.read()

    tree = ast.parse(file_contents)

    inserts = []

    first_node = tree.body[0]

    for node in ast.walk(tree):

        if is_op_node(node):
            output = add_context_type_annotation(node, first_node)

            if output is not None:
                inserts.extend(output)

            if config.ops.add_docstrings:
                output = add_op_docstring(node)

                if output is not None:
                    inserts.append(output)

            inserts.extend(add_op_decorator(node, config, first_node))

        elif is_resource_node(node):
            output = add_context_type_annotation(
                node, first_node, type_name="InitResourceContext"
            )

            if output is not None:
                inserts.extend(output)

            if config.resources.add_docstrings:
                output = add_resource_docstring(node)

                if output is not None:
                    inserts.append(output)

            inserts.extend(add_resource_decorator(node, config, first_node))

    write_file(file_name, file_contents, inserts)
    subprocess.run(["isort", file_name])
    subprocess.run(["black", file_name])

    # write_file("fmt_res." + file_name, file_contents, inserts)
    # subprocess.run(["isort", "fmt_res." + file_name])
    # subprocess.run(["black", "fmt_res." + file_name])


def run(file_name):
    config = Configuration.from_pyproject()

    if os.path.isdir(file_name):

        sub_dir = ""

        if config.ops.dir != "*":
            sub_dir = config.ops.dir + "/"

        for path_to_file in Path(file_name).rglob(f"**/{sub_dir}*.py"):
            run_on_file(path_to_file, config)
    else:
        run_on_file(file_name, config)
