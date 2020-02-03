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
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Set the verbosity level. For example, -vv sets the verbosity level to 2. Default: 0.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Run the script without actual rendering or creating files and"
            " folders. For debugging purposes"
        ),
    )
    namespace: Namespace = parser.parse_args(args)
    namespace.verbose = 99999 if namespace.dry_run else namespace.verbose
    return namespace
