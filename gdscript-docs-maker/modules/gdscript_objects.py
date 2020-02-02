"""Converts the json representation of GDScript classes as dictionaries into objects
"""
from dataclasses import dataclass
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


@dataclass
class Method:
    signature: str
    name: str
    description: str
    return_type: str
    arguments: List[Argument]
    rpc_mode: int
    is_virtual: bool
    tags: List[str]

    def summarize(self) -> List[str]:
        return [self.return_type, self.signature]


@dataclass
class StaticFunction:
    signature: str
    name: str
    description: str
    return_type: str
    arguments: List[Argument]
    tags: List[str]

    def summarize(self) -> List[str]:
        return [self.return_type, self.signature]


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
    methods: List[Method]
    members: List[Member]
    static_functions: List[StaticFunction]
    signals: List[Signal]
    tags: List[str]

    @classmethod
    def from_dict(cls, data: dict):
        description, tags = get_tags(data["description"])
        return GDScriptClass(
            data["name"],
            data["extends_class"],
            description.strip(" \n"),
            data["path"],
            _get_methods(data["methods"]),
            _get_members(data["members"]),
            _get_static_functions(data["static_functions"]),
            _get_signals(data["signals"]),
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
        line = line.strip().lower()
        if not line.startswith("tags:"):
            description_trimmed.append(line)
            continue
        tags = line.replace("tags:", "", 1).split(",")
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


def _get_methods(data: List[dict]) -> List[Method]:
    methods: List[Method] = []
    for entry in data:
        name: str = entry["name"]
        if name in BUILTIN_VIRTUAL_CALLBACKS:
            continue
        if name == TYPE_CONSTRUCTOR and not entry["arguments"]:
            continue

        description, tags = get_tags(entry["description"])
        is_virtual: bool = "virtual" in tags

        is_private: bool = name.startswith("_") and not is_virtual
        if is_private:
            continue

        method: Method = Method(
            entry["signature"].replace("-> null", "-> void", 1),
            name,
            description.strip(" \n"),
            entry["return_type"].replace("null", "void", 1),
            _get_arguments(entry["arguments"]),
            entry["rpc_mode"],
            is_virtual,
            tags,
        )
        methods.append(method)
    return methods


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


def _get_static_functions(data: List[dict]) -> List[StaticFunction]:
    static_functions: List[StaticFunction] = []
    for entry in data:
        description, tags = get_tags(entry["description"])
        static_function: StaticFunction = StaticFunction(
            entry["signature"],
            entry["name"],
            description.strip(" \n"),
            entry["return_type"],
            _get_arguments(entry["arguments"]),
            tags,
        )
        static_functions.append(static_function)
    return static_functions
