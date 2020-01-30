import sys
from argparse import ArgumentParser, Namespace


def parse(args=sys.argv) -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        prog="GDScript Docs Maker",
        description="Merges or converts json data dumped by Godot's GDScript language server to create a code reference.",
    )
    parser.add_argument(
        "files", type=str, nargs="+", default="", help="A list of paths to JSON files."
    )
    parser.add_argument(
        "-p", "--path", type=str, default="dist", help="Path to the output directory"
    )
    return parser.parse_args(args)
