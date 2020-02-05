"""Functions to format the markdown output for the static website engine hugo.
"""
from typing import Any, List


def highlight_code(content: str, language: str = "gdscript") -> str:
    return make_shortcode(content, "highlight", language)


def make_shortcode(content: str, shortcode: str, *args: str, **kwargs: str) -> str:
    key_value_pairs: str = " ".join(["{}={}" for key, value in kwargs.items()])
    return "{{{{< {0} {1} {2} >}}}}{3}{{{{< / {0} >}}}}".format(
        shortcode, " ".join(args), key_value_pairs, content
    )
