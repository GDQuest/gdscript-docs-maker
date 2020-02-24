"""Parses the JSON data from Godot as a dictionary and outputs markdown
documents"""
from argparse import Namespace
from typing import List
import re

from . import hugo
from .command_line import OutputFormats
from .gdscript_objects import (
    Enumeration,
    Function,
    FunctionTypes,
    GDScriptClass,
    GDScriptClasses,
    ProjectInfo,
    Member,
    Signal,
)
from .hugo import HugoFrontMatter
from .make_markdown import (
    MarkdownDocument,
    MarkdownSection,
    make_bold,
    make_code_block,
    make_heading,
    surround_with_html,
    make_table_row,
    make_table_header,
    wrap_in_newlines,
    make_comment,
    make_link,
)


def convert_to_markdown(
    classes: GDScriptClasses, arguments: Namespace, info: ProjectInfo
) -> List[MarkdownDocument]:
    """Takes a list of dictionaries that each represent one GDScript class to
    convert to markdown and returns a list of markdown documents.

    """
    markdown: List[MarkdownDocument] = []
    if arguments.make_index:
        markdown.append(_write_index_page(classes, info))
    for entry in classes:
        markdown.append(_as_markdown(entry, arguments))
    return markdown


def _as_markdown(gdscript: GDScriptClass, arguments: Namespace) -> MarkdownDocument:
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
    if gdscript.extends:
        content += [make_bold("Extends:") + " " + gdscript.extends_as_string()]
    content += [*MarkdownSection("Description", 2, [gdscript.description]).as_text()]

    members_summary: List[str] = _write_members_summary(gdscript)
    methods_summary: List[str] = _write_methods_summary(gdscript)
    if members_summary:
        content += MarkdownSection("Properties", 2, members_summary).as_text()
    if methods_summary:
        content += MarkdownSection("Methods", 2, methods_summary).as_text()

    content += [
        *MarkdownSection("Signals", 2, _write_signals(gdscript.signals)).as_text(),
        *MarkdownSection(
            "Enumerations", 2, _write_enums(gdscript.enums, output_format)
        ).as_text(),
        # Full reference for the properties and methods.
        *MarkdownSection(
            "Property Descriptions", 2, _write_members(gdscript.members, output_format)
        ).as_text(),
        *MarkdownSection(
            "Method Descriptions",
            2,
            _write_functions(gdscript.functions, output_format),
        ).as_text(),
    ]
    doc: MarkdownDocument = MarkdownDocument(
        gdscript.name, content,
    )
    return doc


def _write_members_summary(gdscript: GDScriptClass) -> List[str]:
    if not gdscript.members:
        return []
    header: List[str] = make_table_header(["Type", "Name"])
    return header + [make_table_row(member.summarize()) for member in gdscript.members]


def _write_methods_summary(gdscript: GDScriptClass) -> List[str]:
    if not gdscript.functions:
        return []
    header: List[str] = make_table_header(["Type", "Name"])
    return header + [
        make_table_row(function.summarize()) for function in gdscript.functions
    ]


def _write_signals(signals: List[Signal]) -> List[str]:
    if not signals:
        return []
    return wrap_in_newlines(["- {}".format(s.signature) for s in signals])


def _write_enums(enums: List[Enumeration], output_format: OutputFormats) -> List[str]:
    def write(enum: Enumeration) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(enum.name, 3))
        if output_format == OutputFormats.HUGO:
            markdown.extend([hugo.highlight_code(enum.signature), ""])
        else:
            markdown.extend([make_code_block(enum.signature), ""])
        markdown.append(enum.description)
        return markdown

    markdown: List[str] = []
    return [markdown.extend(write(enum)) for enum in enums]


def _write_members(members: List[Member], output_format: OutputFormats) -> List[str]:
    def write(member: Member) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(member.name, 3))
        if output_format == OutputFormats.HUGO:
            markdown.extend([hugo.highlight_code(member.signature), ""])
        else:
            markdown.extend([make_code_block(member.signature), ""])
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
    return [markdown.extend(write(member)) for member in members]


def _write_functions(
    functions: List[Function], output_format: OutputFormats
) -> List[str]:
    def write(function: Function) -> List[str]:
        markdown: List[str] = []

        heading: str = function.name
        if function.kind == FunctionTypes.VIRTUAL:
            heading += " " + surround_with_html("(virtual)", "small")
        if function.kind == FunctionTypes.STATIC:
            heading += " " + surround_with_html("(static)", "small")

        markdown.extend(make_heading(heading, 3))
        if output_format == OutputFormats.HUGO:
            markdown.extend([hugo.highlight_code(function.signature), ""])
        else:
            markdown.extend([make_code_block(function.signature), ""])
        if function.description:
            markdown.extend(["", function.description])
        return markdown

    markdown: List[str] = []
    for function in functions:
        markdown += write(function)
    return [markdown.extend(write(function)) for function in functions]


def _write_index_page(classes: GDScriptClasses, info: ProjectInfo) -> MarkdownDocument:
    title: str = "{} ({})".format(info.name, surround_with_html(info.version, "small"))
    content: List[str] = [
        *MarkdownSection(title, 1, info.description).as_text(),
        *MarkdownSection("Contents", 2, _write_table_of_contents(classes)).as_text(),
    ]
    return MarkdownDocument("index", content)


def _write_table_of_contents(classes: GDScriptClasses) -> List[str]:
    toc: List[str] = []

    by_category = classes.get_grouped_by_category()

    for group in by_category:
        indent: str = ""
        first_class: GDScriptClass = group[0]
        category: str = first_class.category
        if category:
            toc.append("- {}".format(make_bold(category)))
            indent = "  "

        for gdscript_class in group:
            link: str = indent + "- " + make_link(
                gdscript_class.name, gdscript_class.name
            )
            toc.append(link)

    return toc


def _replace_references(classes: GDScriptClasses, description: str) -> str:
    """Finds and replaces references to other classes or methods in the
`description`."""
    references: re.Match = re.findall(r"\[.+\]", description)

    pattern: str = r"([A-Z]\w*)?\.?([a-z_]+)?"
    for reference in references:
        match: re.Match = re.match(pattern, match)
        if not match:
            continue

        class_name, member = match[1], match[2]
        index: dict = classes.get_class_index()
        if class_name and class_name not in index:
            continue
        if member and member not in index[class_name]:
            continue

        display_text, path = class_name, class_name
        if class_name and member:
            display_text += "."
            path += "/#"
        if member:
            display_text += member
            path += member.replace("_", "-")
        description.replace(reference, make_link(display_text, path), 1)
    return description
