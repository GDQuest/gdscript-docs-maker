"""Converts the json representation of GDScript classes as dictionaries into objects
"""
from dataclasses import dataclass
from typing import List

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
    "_init",
    "_notification",
    "_set",
    "_to_string",
    "_clips_input",
    "_get_minimum_size",
    "_gui_input",
    "_make_custom_tooltip",
]


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

    def summarize(self) -> List[str]:
        return [self.return_type, self.signature]


@dataclass
class StaticFunction:
    signature: str
    name: str
    description: str
    return_type: str
    arguments: List[Argument]

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

    @classmethod
    def from_dict(cls, data: dict):
        return GDScriptClass(
            data["name"],
            data["extends_class"],
            data["description"].strip(" \n"),
            data["path"],
            _get_methods(data["methods"]),
            _get_members(data["members"]),
            _get_static_functions(data["static_functions"]),
            _get_signals(data["signals"]),
        )

    def extends_as_string(self) -> str:
        return " < ".join(self.extends)


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
        # Skip buit-ins and private methods
        name: str = entry["name"]
        description: str = entry["description"]
        if name in BUILTIN_VIRTUAL_CALLBACKS:
            continue

        line_last: str = description.split("\n")[-1].strip()
        is_virtual: bool = name.startswith("_") and line_last.lower() == "virtual"
        if not is_virtual:
            continue

        method: Method = Method(
            entry["signature"],
            name,
            description.strip(" \n"),
            entry["return_type"],
            _get_arguments(entry["arguments"]),
            entry["rpc_mode"],
            is_virtual,
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
        member: Member = Member(
            entry["signature"],
            entry["name"],
            entry["description"].strip(" \n"),
            entry["data_type"],
            entry["default_value"],
            entry["export"],
            entry["setter"],
            entry["getter"],
        )
        members.append(member)
    return members


def _get_static_functions(data: List[dict]) -> List[StaticFunction]:
    static_functions: List[StaticFunction] = []
    for entry in data:
        static_function: StaticFunction = StaticFunction(
            entry["signature"],
            entry["name"],
            entry["description"].strip(" \n"),
            entry["return_type"],
            _get_arguments(entry["arguments"]),
        )
        static_functions.append(static_function)
    return static_functions
