"""Parses the JSON data from Godot as a dictionary and outputs markdown documents"""
from dataclasses import dataclass
from typing import List


@dataclass
class MarkdownDocument:
    content: List[str]
    title: str

    def get_filename(self):
        return self.title + ".md"


@dataclass
class Argument:
    name: str
    type: str


@dataclass
class Method:
    signature: str
    name: str
    description: str
    return_type: str
    arguments: List[Argument]
    rpc_mode: int

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

    def as_markdown(self) -> MarkdownDocument:
        return MarkdownDocument(
            [
                *make_heading(self.name, 1),
                make_bold("Extends:") + " " + self.extends_as_string(),
                *make_heading("Description", 2),
                self.description,
                # Overview of the properties and methods
                *make_heading("Properties", 2),
                *self.summarize_members(),
                *make_heading("Methods", 2),
                *self.summarize_methods(),
                *make_heading("Signals", 2),
                *make_heading("Enumerations", 2),
                # Full reference for the properties and methods.
                *make_heading("Property Descriptions", 2),
                *make_heading("Method Descriptions", 2),
            ],
            self.name,
        )

    def extends_as_string(self) -> str:
        return " < ".join(self.extends)

    def summarize_members(self) -> List[str]:
        if not self.members:
            return []
        header: List[str] = make_table_header(["Type", "Name"])
        return header + [make_table_row(member.summarize()) for member in self.members]

    def summarize_methods(self) -> List[str]:
        header: List[str] = make_table_header(["Type", "Name"])
        return header + [make_table_row(method.summarize()) for method in self.methods]


def _get_methods(data: List[dict]) -> List[Method]:
    methods: List[Method] = []
    for entry in data:
        method: Method = Method(
            entry["signature"],
            entry["name"],
            entry["description"].strip(" \n"),
            entry["return_type"],
            _get_arguments(entry["arguments"]),
            entry["rpc_mode"],
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


def convert_to_markdown(data: dict = {}) -> List[MarkdownDocument]:
    """Takes a dictionary that contains all the GDScript classes to convert to markdown
    and returns a list of markdown documents.
    """
    as_markdown: List[MarkdownDocument] = []
    for entry in data:
        as_markdown.append(_convert_class_to_markdown(entry))
    return as_markdown


def _convert_class_to_markdown(data: dict = {}) -> MarkdownDocument:
    gdscript_class: GDScriptClass = GDScriptClass(
        data["name"],
        data["extends_class"],
        data["description"].strip(" \n"),
        data["path"],
        _get_methods(data["methods"]),
        _get_members(data["members"]),
        _get_static_functions(data["static_functions"]),
    )
    return gdscript_class.as_markdown()


def make_heading(line: str, level: int = 1) -> List[str]:
    """Returns the line as a markdown heading, surrounded by two empty lines."""
    hashes = "#" * level
    return ["", " ".join([hashes, line, hashes]), ""]


def make_bold(text: str) -> str:
    """Returns the text surrounded by **"""
    return "**" + text + "**"


def make_italic(text: str) -> str:
    """Returns the text surrounded by *"""
    return "*" + text + "*"


def make_table_header(cells: List[str]) -> List[str]:
    return [make_table_row(cells), " --- |" * (len(cells) - 1) + " --- "]


def make_table_row(cells: List[str]) -> str:
    return " | ".join(cells)
