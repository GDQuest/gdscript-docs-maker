"""Parses the JSON data from Godot as a dictionary and outputs markdown documents"""
from dataclasses import dataclass
from typing import List

from .gdscript_objects import GDScriptClass


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
    as_markdown: List[MarkdownDocument] = []
    for entry in data:
        as_markdown.append(_convert_class_to_markdown(entry))
    return as_markdown


def _convert_class_to_markdown(data: dict = {}) -> MarkdownDocument:
    return as_markdown(GDScriptClass.from_dict(data))


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
            *make_heading("Enumerations", 2),
            # Full reference for the properties and methods.
            *make_heading("Property Descriptions", 2),
            *make_heading("Method Descriptions", 2),
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


def make_comment(text: str) -> str:
    return "<!-- {} -->".format(text)
