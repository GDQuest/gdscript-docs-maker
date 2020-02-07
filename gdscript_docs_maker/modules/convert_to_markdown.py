"""Parses the JSON data from Godot as a dictionary and outputs markdown documents"""
import re
from argparse import Namespace
from dataclasses import dataclass
from typing import List

from . import hugo
from .command_line import OutputFormats
from .gdscript_objects import (Enumeration, Function, FunctionTypes,
                               GDScriptClass, Member, Signal)
from .hugo import HugoFrontMatter


@dataclass
class MarkdownDocument:
    title: str
    content: List[str]

    def get_filename(self):
        return self.title + ".md"

    def as_string(self) -> str:
        """Removes duplicate empty lines from the document and returns it as a string."""
        text: str = "\n".join(self.content)
        return re.sub(r"\n\n+", "\n\n", text)

    def __repr__(self):
        return "MarkdownDocument(title={}, content={})".format(
            self.title, "\\n".join(self.content)[:120] + "..."
        )


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


def convert_to_markdown(data: dict, arguments: Namespace,) -> List[MarkdownDocument]:
    """Takes a dictionary that contains all the GDScript classes to convert to markdown
    and returns a list of markdown documents.
    """
    markdown: List[MarkdownDocument] = []
    for entry in data:
        markdown.append(as_markdown(GDScriptClass.from_dict(entry), arguments))
    return markdown


def as_markdown(gdscript: GDScriptClass, arguments: Namespace) -> MarkdownDocument:
    """Converts the data for a GDScript class to a markdown document, using the command line
    options."""

    content: List[str] = []

    output_format: OutputFormats = arguments.format

    name: str = gdscript.name
    if "abstract" in gdscript.tags:
        name += " " + surround_with_html("(abstract)", "small")

    if output_format == OutputFormats.HUGO:
        front_matter: HugoFrontMatter = HugoFrontMatter.from_data(gdscript, arguments)
        content += front_matter.as_string_list()

    content += [
        make_comment(
            "Auto-generated from JSON by GDScript docs maker. "
            "Do not edit this document directly."
        )
        + "\n"
    ]

    if output_format == OutputFormats.MARDKOWN:
        content += [*make_heading(name, 1)]
    content += [
        make_bold("Extends:") + " " + gdscript.extends_as_string(),
        *MarkdownSection("Description", 2, [gdscript.description]).as_text(),
        # Overview of the properties and methods
        *MarkdownSection("Properties", 2, summarize_members(gdscript)).as_text(),
        *MarkdownSection("Methods", 2, summarize_methods(gdscript)).as_text(),
        *MarkdownSection("Signals", 2, write_signals(gdscript.signals)).as_text(),
        *MarkdownSection("Enumerations", 2, write_enums(gdscript.enums)).as_text(),
        # Full reference for the properties and methods.
        *MarkdownSection(
            "Property Descriptions", 2, write_members(gdscript.members)
        ).as_text(),
        *MarkdownSection(
            "Method Descriptions", 2, write_functions(gdscript.functions),
        ).as_text(),
    ]
    doc: MarkdownDocument = MarkdownDocument(
        gdscript.name, content,
    )
    return doc


def summarize_members(gdscript: GDScriptClass) -> List[str]:
    if not gdscript.members:
        return []
    header: List[str] = make_table_header(["Type", "Name"])
    return header + [make_table_row(member.summarize()) for member in gdscript.members]


def summarize_methods(gdscript: GDScriptClass) -> List[str]:
    header: List[str] = make_table_header(["Type", "Name"])
    return header + [
        make_table_row(function.summarize()) for function in gdscript.functions
    ]


def write_signals(signals: List[Signal]) -> List[str]:
    if not signals:
        return []
    return wrap_in_newlines(["- {}".format(s.signature) for s in signals])


def write_enums(enums: List[Enumeration]) -> List[str]:
    def write_enum(enum: Enumeration) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(enum.name, 3))
        markdown.extend([hugo.highlight_code(enum.signature), ""])
        markdown.append(enum.description)
        return markdown

    markdown: List[str] = []
    for enum in enums:
        markdown += write_enum(enum)
    return markdown


def write_members(members: List[Member]) -> List[str]:
    def write_member(member: Member) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(member.name, 3))
        markdown.extend([hugo.highlight_code(member.signature), ""])
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


def write_functions(functions: List[Function]) -> List[str]:
    def write_function(function: Function) -> List[str]:
        markdown: List[str] = []

        heading: str = function.name
        if function.kind == FunctionTypes.VIRTUAL:
            heading += " " + surround_with_html("(virtual)", "small")
        if function.kind == FunctionTypes.STATIC:
            heading += " " + surround_with_html("(static)", "small")

        markdown.extend(make_heading(heading, 3))
        markdown.append(hugo.highlight_code(function.signature))
        if function.description:
            markdown.extend(["", function.description])
        return markdown

    markdown: List[str] = []
    for function in functions:
        markdown += write_function(function)
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


def make_code_inline(text: str) -> str:
    """Returns the text surrounded by `"""
    return "`" + text + "`"


def make_code_block(text: str, language: str = "") -> str:
    """Returns the text surrounded by `"""
    return "```{}\n{}\n```".format(language, text)


def make_link(description: str, target: str) -> str:
    return "[{}]({})".format(description, target)


def make_table_header(cells: List[str]) -> List[str]:
    return [make_table_row(cells), " --- |" * (len(cells) - 1) + " --- "]


def make_table_row(cells: List[str]) -> str:
    return " | ".join(cells)


def make_comment(text: str) -> str:
    return "<!-- {} -->".format(text)


def surround_with_html(text: str, tag: str) -> str:
    return "<{}>{}</{}>".format(tag, text, tag)
