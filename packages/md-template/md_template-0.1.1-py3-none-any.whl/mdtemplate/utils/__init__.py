import difflib
import sys

from .repo import Repository


def escape_table_cell(content: str):
    return content.replace("\n", "<br>").replace("|", "\\|")


def print_difference(source: str, output: str):
    def color_diff(diff):
        for line in diff:
            if line.startswith("+"):
                yield "\x1b[32m" + line + "\x1b[0m"
            elif line.startswith("-"):
                yield "\x1b[31m" + line + "\x1b[0m"
            elif line.startswith("^"):
                yield "\x1b[34m" + line + "\x1b[0m"
            else:
                yield line

    sys.stdout.writelines(
        color_diff(
            difflib.unified_diff(
                source.splitlines(keepends=True), output.splitlines(keepends=True)
            )
        )
    )
