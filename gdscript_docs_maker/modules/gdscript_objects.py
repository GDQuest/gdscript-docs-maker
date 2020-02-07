"""Converts the json representation of GDScript classes as dictionaries into objects
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

BUILTIN_VIRTUAL_CALLBACKS = [
    "_process",
    "_physics_process",
    "_input",
    "_unhandled_input",
    "_gui_input",
    "_draw",
    "_get_configuration_warning",
    "_ready",
    "_enter_tree",
    "_exit_tree",
    "_get",
    "_get_property_list",
    "_notification",
    "_set",
    "_to_string",
    "_clips_input",
    "_get_minimum_size",
    "_gui_input",
    "_make_custom_tooltip",
]

TYPE_CONSTRUCTOR = "_init"


@dataclass
class Argument:
    name: str
    type: str


@dataclass
class Signal:
    signature: str
    name: str
    description: str
    arguments: List[str]


class FunctionTypes(Enum):
    METHOD = 1
    VIRTUAL = 2
    STATIC = 3


@dataclass
class Function:
    signature: str
    kind: FunctionTypes
    name: str
    description: str
    return_type: str
    arguments: List[Argument]
    rpc_mode: int
    tags: List[str]

    def summarize(self) -> List[str]:
        return [self.return_type, self.signature]


@dataclass
class Enumeration:
    """Represents an enum with its constants"""

    signature: str
    name: str
    description: str
    values: dict

    @classmethod
    def from_dict(cls, data: dict):
        return Enumeration(
            data["signature"], data["name"], data["description"], data["value"]
        )


@dataclass
class Member:
    """Represents a property or member variable"""

    signature: str
    name: str
    description: str
    type: str
    default_value: str
    is_exported: bool
    setter: str
    getter: str
    tags: List[str]

    def summarize(self) -> List[str]:
        return [self.type, self.name]


@dataclass
class GDScriptClass:
    name: str
    extends: str
    description: str
    path: str
    functions: List[Function]
    members: List[Member]
    signals: List[Signal]
    enums: List[Enumeration]
    tags: List[str]

    @classmethod
    def from_dict(cls, data: dict):
        description, tags = get_tags(data["description"])
        return GDScriptClass(
            data["name"],
            data["extends_class"],
            description.strip(" \n"),
            data["path"],
            _get_functions(data["methods"])
            + _get_functions(data["static_functions"], is_static=True),
            _get_members(data["members"]),
            _get_signals(data["signals"]),
            [
                Enumeration.from_dict(entry)
                for entry in data["constants"]
                if entry["data_type"] == "Dictionary"
            ],
            tags,
        )

    def extends_as_string(self) -> str:
        return " < ".join(self.extends)


def get_tags(description: str) -> Tuple[str, List[str]]:
    """Collect the tags from the description as a list of strings.
    Returns the description without the tags and the tags as a list of strings."""
    tags: List[str] = []
    lines: List[str] = description.split("\n")
    description_trimmed = []
    for index, line in enumerate(lines):
        tag_line: str = line.strip().lower()
        if not tag_line.startswith("tags:"):
            description_trimmed.append(line)
            continue
        tags = tag_line.replace("tags:", "", 1).split(",")
        tags = list(map(lambda t: t.strip(), tags))
    return "\n".join(description_trimmed), tags


def _get_signals(data: List[dict]) -> List[Signal]:
    signals: List[Signal] = []
    for entry in data:
        signal: Signal = Signal(
            entry["signature"], entry["name"], entry["description"], entry["arguments"],
        )
        signals.append(signal)
    return signals


def _get_functions(data: List[dict], is_static: bool = False) -> List[Function]:
    functions: List[Function] = []
    for entry in data:
        name: str = entry["name"]
        if name in BUILTIN_VIRTUAL_CALLBACKS:
            continue
        if name == TYPE_CONSTRUCTOR and not entry["arguments"]:
            continue

        description, tags = get_tags(entry["description"])
        is_virtual: bool = "virtual" in tags and not is_static
        is_private: bool = name.startswith("_") and not is_virtual
        if is_private:
            continue

        kind: FunctionTypes = FunctionTypes.METHOD
        if is_static:
            kind = FunctionTypes.STATIC
        elif is_virtual:
            kind = FunctionTypes.VIRTUAL

        function: Function = Function(
            entry["signature"].replace("-> null", "-> void", 1),
            kind,
            name,
            description.strip(" \n"),
            entry["return_type"].replace("null", "void", 1),
            _get_arguments(entry["arguments"]),
            entry["rpc_mode"] if "rpc_mode" in entry else 0,
            tags,
        )
        functions.append(function)
    return functions


def _get_arguments(data: List[dict]) -> List[Argument]:
    arguments: List[Argument] = []
    for entry in data:
        argument: Argument = Argument(
            entry["name"], entry["type"],
        )
        arguments.append(argument)
    return arguments


def _get_members(data: List[dict]) -> List[Member]:
    members: List[Member] = []
    for entry in data:
        # Skip private members
        if entry["name"].startswith("_"):
            continue
        description, tags = get_tags(entry["description"])
        member: Member = Member(
            entry["signature"],
            entry["name"],
            description.strip(" \n"),
            entry["data_type"],
            entry["default_value"],
            entry["export"],
            entry["setter"],
            entry["getter"],
            tags,
        )
        members.append(member)
    return members
