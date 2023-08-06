from typing import Callable

plain = lambda s: "\u001b[0m" + s + "\u001b[0m"
red = lambda s: "\u001b[31m" + s + "\u001b[0m"
green = lambda s: "\u001b[32m" + s + "\u001b[0m"
green_background = lambda s: "\u001b[42m" + s + "\u001b[0m"
yellow = lambda s: "\u001b[33m" + s + "\u001b[0m"
blue = lambda s: "\u001b[34m" + s + "\u001b[0m"
cyan = lambda s: "\u001b[36m" + s + "\u001b[0m"
grey = lambda s: "\u001b[38;5;240m" + s + "\u001b[0m"
underline = lambda s: "\u001b[4m" + s + "\u001b[0m"

def string_differences(old: str, new: str) -> str:
    """Adds color to the lines in new that were not in old.

    Args:
        old (str): the old string.
        new (str): the new string.

    Returns:
        str: The new string with
    """
    result = ""

    for line in new.splitlines():
        if line in old:
            result += grey(line) + "\n"
        else:
            result += plain(line) + "\n"

    return result


def color_feedback(
    interpretation_feedback: list[tuple[str, str]], coloring: dict[str, Callable] = None
) -> str:
    if coloring is None:
        coloring = {
            "keyword": green_background,
            "parameter": green,
            "ignored": plain,
        }
    
    result = ""
    
    for type, text in interpretation_feedback:
        if text.strip() == "":
            continue
        result += coloring[type](text.strip()) + " "

    return result