"""Merges JSON dumped by Godot's gdscript language server or converts it to a markdown
document.
"""
import json
import os
from argparse import Namespace
from typing import List

from .modules import command_line
from .modules.convert_to_markdown import convert_to_markdown
from .modules.merged_json import merge_into


def main():
    args: Namespace = command_line.parse()
    json_files: List[str] = [f for f in args.files if f.lower().endswith(".json")]


if __name__ == "__main__":
    main()
