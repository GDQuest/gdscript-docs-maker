import os
import json
from argparse import Namespace
from typing import List

from .modules import collect_reference, command_line


def main():
    args: Namespace = command_line.parse()
    reference = []
    for file_path in args.files:
        if not file_path.lower().endswith(".gd"):
            continue
        with open(file_path, "r") as gdscript_file:
            gdscript: List[str] = gdscript_file.readlines()
            file_name: str = os.path.basename(file_path)
            file_data: dict = collect_reference.get_file_reference(gdscript)
            if not file_data["class_name"]:
                file_data["class_name"] = file_name.split(".gd")[0].strip()
            reference.append(file_data)
    reference_as_json = json.dumps(reference, indent=4)
    print(reference_as_json)


if __name__ == "__main__":
    main()
