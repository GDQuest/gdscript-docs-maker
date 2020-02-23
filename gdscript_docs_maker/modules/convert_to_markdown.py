"""Parses the JSON data from Godot as a dictionary and outputs markdown
documents"""
from argparse import Namespace
from typing import List

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
        markdown.append(write_index_page(classes, info))
    for entry in classes:
        markdown.append(as_markdown(entry, arguments))
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
    if gdscript.extends:
        content += [make_bold("Extends:") + " " + gdscript.extends_as_string()]
    content += [*MarkdownSection("Description", 2, [gdscript.description]).as_text()]

    members_summary: List[str] = summarize_members(gdscript)
    methods_summary: List[str] = summarize_methods(gdscript)
    if members_summary:
        content += MarkdownSection("Properties", 2, members_summary).as_text()
    if methods_summary:
        content += MarkdownSection("Methods", 2, methods_summary).as_text()

    content += [
        *MarkdownSection("Signals", 2, write_signals(gdscript.signals)).as_text(),
        *MarkdownSection(
            "Enumerations", 2, write_enums(gdscript.enums, output_format)
        ).as_text(),
        # Full reference for the properties and methods.
        *MarkdownSection(
            "Property Descriptions", 2, write_members(gdscript.members, output_format)
        ).as_text(),
        *MarkdownSection(
            "Method Descriptions",
            2,
            write_functions(gdscript.functions, output_format),
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
    if not gdscript.functions:
        return []
    header: List[str] = make_table_header(["Type", "Name"])
    return header + [
        make_table_row(function.summarize()) for function in gdscript.functions
    ]


def write_signals(signals: List[Signal]) -> List[str]:
    if not signals:
        return []
    return wrap_in_newlines(["- {}".format(s.signature) for s in signals])


def write_enums(enums: List[Enumeration], output_format: OutputFormats) -> List[str]:
    def write_enum(enum: Enumeration) -> List[str]:
        markdown: List[str] = []
        markdown.extend(make_heading(enum.name, 3))
        if output_format == OutputFormats.HUGO:
            markdown.extend([hugo.highlight_code(enum.signature), ""])
        else:
            markdown.extend([make_code_block(enum.signature), ""])
        markdown.append(enum.description)
        return markdown

    markdown: List[str] = []
    for enum in enums:
        markdown += write_enum(enum)
    return markdown


def write_members(members: List[Member], output_format: OutputFormats) -> List[str]:
    def write_member(member: Member) -> List[str]:
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
    for member in members:
        markdown += write_member(member)
    return markdown


def write_functions(
    functions: List[Function], output_format: OutputFormats
) -> List[str]:
    def write_function(function: Function) -> List[str]:
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
        markdown += write_function(function)
    return markdown


def write_index_page(classes: GDScriptClasses, info: ProjectInfo) -> MarkdownDocument:
    title: str = "{} ({})".format(info.name, surround_with_html(info.version, "small"))
    content: List[str] = [
        *MarkdownSection(title, 1, info.description).as_text(),
        *MarkdownSection("Contents", 2, write_table_of_contents(classes)).as_text(),
    ]
    return MarkdownDocument("index", content)


def write_table_of_contents(classes: GDScriptClasses) -> List[str]:
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
