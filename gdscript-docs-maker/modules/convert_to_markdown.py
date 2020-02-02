"""Parses the JSON data from Godot as a dictionary and outputs markdown documents"""
from dataclasses import dataclass
from typing import List

from .gdscript_objects import (GDScriptClass, Member, Method, Signal,
                               StaticFunction)


@dataclass
class MarkdownDocument:
    content: List[str]
    title: str

    def get_filename(self):
        return self.title + ".md"


class MarkdownSection:
    def __init__(self, title: str, heading_level: int, content: List[str]):
        """Represents a section of a markdown document.

        Keyword Arguments:
        title: str         --
        heading_level: int --
        content: List[str] -- content of the section
        """
        self.title: List[str] = make_heading(title, heading_level)
        self.content: List[str] = content

    def is_empty(self) -> bool:
        return not self.content

    def as_text(self) -> List[str]:
        return self.title + self.content if not self.is_empty() else []


def convert_to_markdown(data: dict = {}) -> List[MarkdownDocument]:
    """Takes a dictionary that contains all the GDScript classes to convert to markdown
    and returns a list of markdown documents.
    """
    markdown: List[MarkdownDocument] = []
    for entry in data:
        markdown.append(as_markdown(GDScriptClass.from_dict(entry)))
    return markdown


def as_markdown(gdscript: GDScriptClass) -> MarkdownDocument:
    return MarkdownDocument(
        [
            make_comment(
                "Auto-generated from JSON by GDScript docs maker. "
                "Do not edit this document directly."
            ),
            *make_heading(gdscript.name, 1),
            make_bold("Extends:") + " " + gdscript.extends_as_string(),
            *MarkdownSection("Description", 2, [gdscript.description]).as_text(),
            # Overview of the properties and methods
            *MarkdownSection("Properties", 2, summarize_members(gdscript)).as_text(),
            *MarkdownSection("Methods", 2, summarize_methods(gdscript)).as_text(),
            *MarkdownSection("Signals", 2, write_signals(gdscript.signals)).as_text(),
            # TODO
            *MarkdownSection("Enumerations", 2, []).as_text(),
            # Full reference for the properties and methods.
            *MarkdownSection(
                "Property Descriptions", 2, write_members(gdscript.members)
            ).as_text(),
            *MarkdownSection(
                "Method Descriptions",
                2,
                write_functions(gdscript.methods, gdscript.static_functions),
            ).as_text(),
        ],
        gdscript.name,
    )


def summarize_members(gdscript: GDScriptClass) -> List[str]:
    if not gdscript.members:
        return []
    header: List[str] = make_table_header(["Type", "Name"])
    return header + [make_table_row(member.summarize()) for member in gdscript.members]


def summarize_methods(gdscript: GDScriptClass) -> List[str]:
    header: List[str] = make_table_header(["Type", "Name"])
    return header + [
        make_table_row(method.summarize())
        for method in gdscript.methods + gdscript.static_functions
    ]


def write_signals(signals: List[Signal]) -> List[str]:
    if not signals:
        return []
    return wrap_in_newlines(["- {}".format(s.signature) for s in signals])


def write_members(members: List[Member]) -> List[str]:
    def write_member(member: Member) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(member.name, 3))
        markdown.extend([make_code(member.signature), ""])
        if member.setter or member.setter:
            setget: List[str] = []
            if member.setter:
                setget.append(make_table_row(["Setter", member.setter]))
            if member.getter:
                setget.append(make_table_row(["Getter", member.getter]))
            setget.append("")
            markdown.extend(setget)
        markdown.append(member.description)
        return markdown

    markdown: List[str] = []
    for member in members:
        markdown += write_member(member)
    return markdown


def write_functions(
    methods: List[Method], static_functions: List[StaticFunction]
) -> List[str]:
    def write_method(method: Method) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(method.name, 3))
        signature: str = method.signature
        if method.is_virtual:
            signature = make_bold("virtual") + " " + method.signature
        markdown.append(make_code(signature))
        if method.description:
            markdown.extend(["", method.description])
        return markdown

    def write_static_function(static_function: StaticFunction) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(static_function.name, 3))
        signature: str = make_bold("static") + " " + static_function.signature
        markdown.append(make_code(signature))
        if static_function.description:
            markdown.extend(["", static_function.description])
        return markdown

    markdown: List[str] = []
    for function in static_functions:
        markdown += write_static_function(function)
    for method in methods:
        markdown += write_method(method)
    return markdown


def wrap_in_newlines(markdown: List[str] = []) -> List[str]:
    return ["", *markdown, ""]


def make_heading(line: str, level: int = 1) -> List[str]:
    """Returns the line as a markdown heading, surrounded by two empty lines."""
    hashes = "#" * level
    return ["", " ".join([hashes, escape_markdown(line), hashes]), ""]


def escape_markdown(text: str) -> str:
    """Escapes characters that have a special meaning in markdown, like *_-"""
    characters: str = "*_-+`"
    for character in characters:
        text = text.replace(character, "\\" + character)
    return text


def make_bold(text: str) -> str:
    """Returns the text surrounded by **"""
    return "**" + text + "**"


def make_italic(text: str) -> str:
    """Returns the text surrounded by *"""
    return "*" + text + "*"


def make_code(text: str) -> str:
    """Returns the text surrounded by `"""
    return "`" + text + "`"


def make_link(description: str, target: str) -> str:
    return "[{}]({})".format(description, target)


def make_table_header(cells: List[str]) -> List[str]:
    return [make_table_row(cells), " --- |" * (len(cells) - 1) + " --- "]


def make_table_row(cells: List[str]) -> str:
    return " | ".join(cells)


def make_comment(text: str) -> str:
    return "<!-- {} -->".format(text)
