import ast
from typing import List


def get_config_field_names(
    config_name: str, function_node: ast.FunctionDef
) -> List[str]:
    output = []

    for possible_dict_access in ast.walk(function_node):

        if (
            isinstance(possible_dict_access, ast.Subscript)
            and possible_dict_access.value.value.id == "context"
            and possible_dict_access.value.attr == config_name
        ):
            output.append(possible_dict_access.slice.value.value)

    return output


def get_resource_names(function_node: ast.FunctionDef) -> List[str]:
    output = []

    for possible_resource_access in ast.walk(function_node):

        if (
            isinstance(possible_resource_access, ast.Attribute)
            and hasattr(possible_resource_access, "value")
            and hasattr(possible_resource_access.value, "attr")
            and possible_resource_access.value.attr == "resources"
            and possible_resource_access.value.value.id == "context"
        ):

            output.append(possible_resource_access.attr)

    return output
