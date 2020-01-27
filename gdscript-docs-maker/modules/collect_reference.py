"""
Finds and collects docstrings from individual GDScript files
"""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class Statement:
    index: int
    line: str
    type: str


def _collect_reference_statements(gdscript: List[str]) -> List[Statement]:
    """Returns a StatementsList of the lines to process for the docs"""
    statements: List[Statement] = []
    types_map: dict = {
        "var": "properties",
        "onready": "properties",
        "export": "properties",
        "signal": "signals",
        "func": "functions",
        "class": "subclasses",
    }
    for index, line in enumerate(gdscript):
        for pattern in types_map:
            if not line.startswith(pattern):
                continue
            statements.append(Statement(index, line, types_map[pattern]))
    return statements


def _find_docstring(gdscript: List[str], statement: Statement) -> List[str]:
    """Returns the docstring found in the GDScript file for the given statement, or an empty
    string if there's no docstring."""
    docstring: List[str] = []
    index_start = statement.index - 1
    index = index_start
    while gdscript[index].startswith("#"):
        index -= 1
    if index != index_start:
        docstring = gdscript[index + 1 : index_start + 1]

    for index, line in enumerate(docstring):
        docstring[index] = docstring[index].replace("#", "", 1).strip()
    return docstring


def _get_class_data(gdscript: List[str]) -> dict:
    """Returns a dictionary that contains information about the GDScript class. The function
    only reads lines in the document up to the first line that doesn't start with #,
    tool, extends, or class_name.
    """
    data: dict = {
        "is_tool": False,
        "class_name": "",
        "extends": "",
        "docstring": [],
    }
    for line in gdscript:
        if line.startswith("tool"):
            data["is_tool"] = True
        elif line.startswith("class_name"):
            data["class_name"] = re.sub(r"(class_name)?(,.+)?", "", line).strip(" \n")
        elif line.startswith("extends"):
            data["extends"] = line.replace("extends ", "", 1).strip(" \n")
        elif line.startswith("#"):
            data["docstring"].append(line.strip(" #"))
        else:
            break
    return data


def _get_property_data(line: str) -> dict:
    """Returns a dictionary that contains information about a member variable"""
    # Groups 3, 4, and 5 respectively match the symbol, type, and value
    # Use group 6 and the setget regex to find setter and getter functions
    match = re.match(
        r"^(export|onready)?(\(.+\))? ?var (\w+) ?:? ?(\w+)? ?=? ?([\"\'].+[\"\']|([\d.\w]+))?( setget.*)?",
        line,
    )
    if not match:
        return {}

    setter, getter = "", ""
    if match[7]:
        match_setget = re.match(r"setget (set_\w+)?,? ?(get_\w+)?", line)
        if match_setget:
            setter = match_setget.group(1)
            getter = match_setget.group(2)

    return {
        "identifier": match[3],
        "type": match[4],
        "value": match[5],
        "setter": setter,
        "getter": getter,
    }


def _get_function_data(line: str) -> dict:
    """Returns a dictionary that contains information about a function"""
    data: dict = {
        "name": "",
        "arguments": "",
        "type": "",
    }
    match = re.match(r"^func (\w+)\((.*)\) ?-> ?(\w+)", line)
    if not match:
        return []

    data["name"] = match[1]
    data["type"] = match[3]
    arguments = []
    args: str = match[2].strip()
    if args:
        for arg in args.split(","):
            match_arg = re.match(r"(\w+) ?: ?(\w*)", line)
            if not match_arg:
                continue
            arguments.append(
                {"identifier": match_arg.group(1), "type": match_arg.group(2),}
            )
    data["arguments"] = arguments
    return data


def _get_signal_data(line: str) -> dict:
    """Returns a dictionary that contains information about a signal"""
    data: dict = {"name": "", "arguments": []}
    # Matches the signal name and optionally a list of arguments
    match = re.match(r"^signal (\w+)(\(.*\))?\s*$", line)
    if not match:
        return data

    data["name"] = match[1]
    if match.group(2):
        arguments = match[2].split(",")
        for argument in arguments:
            data["arguments"].append(argument.strip("() "))
    return data


def _get_subclass_data(line: str = "") -> dict:
    """Returns a dictionary that contains information about a subclass"""
    data: dict = {
        "name": "",
    }
    match = re.match(r"class (.+):$", line)
    if match:
        data["name"] = match[1]
    return data


def get_file_reference(gdscript: List[str]) -> dict:
    """Returns a dictionary with the functions, properties, and inner classes collected from
    a GDScript file, with their docstrings.

    Keyword Arguments:
    gdscript: List[str] -- (default "")
    """
    class_reference: dict = _get_class_data(gdscript)

    class_data: dict = {
        "properties": [],
        "signals": [],
        "functions": [],
        "subclasses": [],
    }
    functions_map: dict = {
        "properties": _get_property_data,
        "functions": _get_function_data,
        "signals": _get_signal_data,
        "subclasses": _get_subclass_data,
    }
    statements: List[Statement] = _collect_reference_statements(gdscript)
    for statement in statements:
        docstring: str = "\n".join(_find_docstring(gdscript, statement))
        statement_data: dict = functions_map[statement.type](statement.line)
        reference_data: dict = statement_data
        reference_data["docstring"] = docstring
        class_data[statement.type].append(reference_data)
    class_reference["data"] = class_data
    return class_reference
