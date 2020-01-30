"""Parses the JSON data from Godot as a dictionary and outputs markdown documents"""
from dataclasses import dataclass
from typing import List

from .gdscript_objects import GDScriptClass, Member, Method, Signal


@dataclass
class MarkdownDocument:
    content: List[str]
    title: str

    def get_filename(self):
        return self.title + ".md"


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
                "Auto-generated from JSON by GDScript docs maker."
                "Do not edit this document directly."
            ),
            *make_heading(gdscript.name, 1),
            make_bold("Extends:") + " " + gdscript.extends_as_string(),
            *make_heading("Description", 2),
            gdscript.description,
            # Overview of the properties and methods
            *make_heading("Properties", 2),
            *summarize_members(gdscript),
            *make_heading("Methods", 2),
            *summarize_methods(gdscript),
            *make_heading("Signals", 2),
            *write_signals(gdscript.signals),
            # TODO
            *make_heading("Enumerations", 2),
            # Full reference for the properties and methods.
            *make_heading("Property Descriptions", 2),
            *write_members(gdscript.members),
            *make_heading("Method Descriptions", 2),
            *write_methods(gdscript.methods),
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
    return header + [make_table_row(method.summarize()) for method in gdscript.methods]


def write_signals(signals: List[Signal]) -> List[str]:
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


def write_methods(methods: List[Method]) -> List[str]:
    def write_method(method: Method) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(method.name, 3))
        markdown.append(make_code(method.signature))
        if method.description:
            markdown.extend(["", method.description])
        return markdown

    markdown: List[str] = []
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


def make_table_header(cells: List[str]) -> List[str]:
    return [make_table_row(cells), " --- |" * (len(cells) - 1) + " --- "]


def make_table_row(cells: List[str]) -> str:
    return " | ".join(cells)


def make_comment(text: str) -> str:
    return "<!-- {} -->".format(text)
