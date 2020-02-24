"""Converts the json representation of GDScript classes as dictionaries into objects
"""
import itertools
import operator
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

from .make_markdown import make_table_row, surround_with_html

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
class Metadata:
    """Container for metadata for Elements"""

    tags: List[str]
    category: str


def extract_metadata(description: str) -> Tuple[str, Metadata]:
    """Finds metadata keys in the provided description and returns the description
without the corresponding lines, as well as the metadata. In the source text,
Metadata should be of the form key: value, e.g. category: Category Name

    """
    tags: List[str] = []
    category: str = ""

    lines: List[str] = description.split("\n")
    description_trimmed: List[str] = []
    for index, line in enumerate(lines):
        line_stripped: str = line.strip().lower()

        if line_stripped.startswith("tags:"):
            tags = line[line.find(":") + 1 :].split(",")
            tags = list(map(lambda t: t.strip(), tags))
            continue
        elif line_stripped.startswith("category:"):
            category = line[line.find(":") + 1 :].strip()
            continue
        else:
            description_trimmed.append(line.strip())

    metadata: Metadata = Metadata(tags, category)
    return "\n".join(description_trimmed), metadata


class FunctionTypes(Enum):
    METHOD = 1
    VIRTUAL = 2
    STATIC = 3


@dataclass
class ProjectInfo:
    name: str
    description: str
    version: str

    @staticmethod
    def from_dict(data: dict):
        return ProjectInfo(data["name"], data["description"], data["version"])


@dataclass
class Element:
    """Base type for all main GDScript symbol types. Contains properties common to
Signals, Functions, Member variables, etc."""

    signature: str
    name: str
    description: str

    def __post_init__(self):
        _description, self.metadata = extract_metadata(self.description)
        self.description = _description.strip("\n")

    def get_heading_as_string(self) -> str:
        """Returns an empty string. Virtual method to get a list of strings representing
the element as a markdown heading."""
        return self.name

    def get_unique_attributes_as_markdown(self) -> List[str]:
        """Returns an empty list. Virtual method to get a list of strings describing the
unique attributes of this element."""
        return []

    @staticmethod
    def from_dict(data: dict) -> "Element":
        return Element(data["signature"], data["name"], data["description"])


@dataclass
class Signal(Element):
    arguments: List[str]

    @staticmethod
    def from_dict(data: dict) -> "Signal":
        return Signal(
            data["signature"], data["name"], data["description"], data["arguments"],
        )


@dataclass
class Argument:
    """Container for function arguments."""

    name: str
    type: str


@dataclass
class Function(Element):
    kind: FunctionTypes
    return_type: str
    arguments: List[Argument]
    rpc_mode: int

    def __post_init__(self):
        super().__post_init__()
        self.signature = self.signature.replace("-> null", "-> void", 1)
        self.return_type = self.return_type.replace("null", "void", 1)

    def summarize(self) -> List[str]:
        return [self.return_type, self.signature]

    def get_heading_as_string(self) -> str:
        """Returns an empty list. Virtual method to get a list of strings representing
the element as a markdown heading."""
        heading: str = self.name
        if self.kind == FunctionTypes.VIRTUAL:
            heading += " " + surround_with_html("(virtual)", "small")
        if self.kind == FunctionTypes.STATIC:
            heading += " " + surround_with_html("(static)", "small")
        return heading

    @staticmethod
    def from_dict(data: dict) -> "Function":
        kind: FunctionTypes = FunctionTypes.METHOD
        if data["is_static"]:
            kind = FunctionTypes.STATIC
        elif data["is_virtual"]:
            kind = FunctionTypes.VIRTUAL

        return Function(
            data["signature"],
            data["name"],
            data["description"],
            kind,
            data["return_type"],
            Function._get_arguments(data["arguments"]),
            data["rpc_mode"] if "rpc_mode" in data else 0,
        )

    @staticmethod
    def _get_arguments(data: List[dict]) -> List[Argument]:
        return [Argument(entry["name"], entry["type"],) for entry in data]


@dataclass
class Enumeration(Element):
    """Represents an enum with its constants"""

    values: dict

    @staticmethod
    def from_dict(data: dict) -> "Enumeration":
        return Enumeration(
            data["signature"], data["name"], data["description"], data["value"],
        )


@dataclass
class Member(Element):
    """Represents a property or member variable"""

    type: str
    default_value: str
    is_exported: bool
    setter: str
    getter: str

    def summarize(self) -> List[str]:
        return [self.type, self.name]

    def get_unique_attributes_as_markdown(self) -> List[str]:
        setget: List[str] = []
        if self.setter or self.setter:
            if self.setter:
                setget.append(make_table_row(["Setter", self.setter]))
            if self.getter:
                setget.append(make_table_row(["Getter", self.getter]))
            setget.append("")
        return setget

    @staticmethod
    def from_dict(data: dict) -> "Member":
        return Member(
            data["signature"],
            data["name"],
            data["description"],
            data["data_type"],
            data["default_value"],
            data["export"],
            data["setter"],
            data["getter"],
        )


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

    def __post_init__(self):
        description, self.metadata = extract_metadata(self.description)
        self.description = description.strip("\n ")

        elements = self.functions + self.members + self.signals + self.enums
        self.symbols = {element.name for element in elements}

    @staticmethod
    def from_dict(data: dict):
        # the extends_class field is a list in json even though it only has one
        # class.
        extends: str = data["extends_class"][0] if data["extends_class"] else ""
        return GDScriptClass(
            data["name"],
            extends,
            data["description"],
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
        )

    def get_extends_tree(self, classes: "GDScriptClasses") -> List[str]:
        """Returns the list of ancestors for this class, starting from self.extends.

        Arguments:

        - classes: a GDScriptClasses list of GDScriptClass this object is part
          of.

        """
        extends: str = self.extends
        extends_tree: List[str] = []
        while extends != "":
            extends_tree.append(extends)
            extends = next((cls.extends for cls in classes if cls.name == extends), "")
        return extends_tree


class GDScriptClasses(list):
    """Container for a list of GDScriptClass objects

    Provides methods for filtering and grouping GDScript classes"""

    def __init__(self, *args):
        super(GDScriptClasses, self).__init__(args[0])
        self.class_index = {
            gdscript_class.name: gdscript_class.symbols for gdscript_class in self
        }

    def _get_grouped_by(self, attribute: str) -> List[List[GDScriptClass]]:
        if not self or attribute not in self[0].__dict__:
            return []

        groups = []
        get_attribute = operator.attrgetter(attribute)
        data = sorted(self, key=get_attribute)
        for key, group in itertools.groupby(data, get_attribute):
            groups.append(list(group))
        return groups

    def get_grouped_by_category(self) -> List[List[GDScriptClass]]:
        """Returns a list of lists of GDScriptClass objects, grouped by their `category`
attribute"""
        return self._get_grouped_by("category")

    @staticmethod
    def from_dict_list(data: List[dict]):
        return GDScriptClasses(
            [GDScriptClass.from_dict(entry) for entry in data if "name" in entry]
        )


def _get_signals(data: List[dict]) -> List[Signal]:
    return [Signal.from_dict(entry) for entry in data]


def _get_functions(data: List[dict], is_static: bool = False) -> List[Function]:
    """Returns a list of valid functions to put in the class reference. Skips
built-in virtual callbacks, except for constructor functions marked for
inclusion, and private methods."""
    functions: List[Function] = []
    for entry in data:
        name: str = entry["name"]
        if name in BUILTIN_VIRTUAL_CALLBACKS:
            continue
        if name == TYPE_CONSTRUCTOR and not entry["arguments"]:
            continue

        _, metadata = extract_metadata(entry["description"])

        is_virtual: bool = "virtual" in metadata.tags and not is_static
        is_private: bool = name.startswith("_") and not is_virtual
        if is_private:
            continue

        function_data: dict = entry
        function_data["is_virtual"] = is_virtual
        function_data["is_static"] = is_static

        functions.append(Function.from_dict(function_data))
    return functions


def _get_members(data: List[dict]) -> List[Member]:
    return [
        Member.from_dict(entry) for entry in data if not entry["name"].startswith("_")
    ]
