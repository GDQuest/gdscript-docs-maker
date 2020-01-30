"""Merges JSON dumped by Godot's gdscript language server or converts it to a markdown
document.
"""
import json
import os
from argparse import Namespace
from itertools import repeat
from typing import List

from .modules import command_line
from .modules.convert_to_markdown import MarkdownDocument, convert_to_markdown


def main():
    args: Namespace = command_line.parse()
    json_files: List[str] = [f for f in args.files if f.lower().endswith(".json")]
    for f in json_files:
        with open(f, "r") as json_file:
            data: dict = json.loads(json_file.read())
            documents: List[MarkdownDocument] = convert_to_markdown(data)
            if not os.path.exists(args.path):
                os.mkdir(args.path)
            list(map(save, documents, repeat(args.path)))


def save(
    document: MarkdownDocument, dirpath: str,
):
    path: str = os.path.join(dirpath, document.get_filename())
    with open(path, "w") as file_out:
        file_out.writelines("\n".join(document.content))


if __name__ == "__main__":
    main()
