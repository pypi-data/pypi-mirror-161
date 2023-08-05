from __future__ import annotations

import argparse
import re
from functools import lru_cache
from os import PathLike
from pathlib import Path
from types import MethodType
from typing import (
    Sequence,
    Union,
    Optional,
    Iterable,
    List,
    cast,
    Pattern,
    Callable,
)

from ..utils import Repository, print_difference, escape_table_cell


class TableTemplate:
    """Base class for creating table templates."""

    table: Optional[str] = None
    """Name of the table to match, useful when templating multiple tables.

    This template will match table surrounded with:
        `<!-- table --><!-- table-end -->` or

        `<!-- table-<id> --><!-- table-<id>-end -->`
    """

    files: str
    """A glob pattern to match the files to be included in the table."""

    columns: Sequence[str]
    """The columns to include in the table."""

    source: Union[str, PathLike[str]] = "README.md"
    """The file to be used as the source for the table."""

    output: Optional[Union[str, PathLike[str]]] = None
    """The file to write the templated result to, defaults to source."""

    dry_run: bool = False
    """Prevent writing to any files."""

    use_natsort: bool = True
    """Use the external natsort library to ensure the consistent natural sorting of files between platforms."""

    only_tracked: bool = True
    """Only include files that have been checked into source control."""

    repository = Repository()
    """A class containing lazy-loaded information about the current repository."""

    paths: List[Path] = []
    """The resolved list of files to be included in the table."""

    def __init__(
        self,
        table: Optional[str] = None,
        files: Optional[str] = None,
        columns: Optional[Sequence[str]] = None,
        source: Optional[Union[str, PathLike[str]]] = None,
        output: Optional[Union[str, PathLike[str]]] = None,
        dry_run: Optional[bool] = None,
        use_natsort: Optional[bool] = None,
        only_tracked: Optional[bool] = None,
        handle_path: Callable[[TableTemplate, Path], Iterable[Iterable[str]]] = None,
    ):
        """
        Arguments:
            table: Name of the table to match, used when templating multiple tables.
            files: A glob pattern to match the files to be included in the table.
            columns: The columns to include in the table.
            source: The file to be used as the source for the table (default: README.md).
            output: The file to write the templated result to, defaults to source.
            dry_run: Prevent writing to any files.
            use_natsort: Use the external natsort library to ensure the consistent natural sorting of files between platforms.
            only_tracked: Only include files that have been checked into source control.
            handle_path: Generates a list of rows of cells for a given filepath.
                         This function can be a generator and `yield` each row.
                         Both `\\n` (new-line) and `|` (pipe) can be used inside cells and will be escaped.
        """
        if table is not None:
            self.table = table
        if files is not None:
            self.files = files
        if columns is not None:
            self.columns = columns
        if source is not None:
            self.source = source
        if output is not None:
            self.output = output
        if dry_run is not None:
            self.dry_run = dry_run
        if use_natsort is not None:
            self.use_natsort = use_natsort
        if only_tracked is not None:
            self.only_tracked = only_tracked
        if handle_path:
            self.handle_path: Callable[[Path], Iterable[Iterable[str]]] = MethodType(
                handle_path, self
            )
        self.__post_init__()

    def __post_init__(self):
        if not self.files:
            raise ValueError("`files` property is required")
        if not self.columns:
            raise ValueError("`columns` property is required")
        self.resolve_paths()

    def resolve_paths(self):
        """Resolves individual filepaths from the `files` property.

        It also optionally excludes untracked files and performs a natural sort.
        """
        paths = Path(".").glob(self.files)

        if self.only_tracked:
            self.paths = [
                path
                for path in paths
                if path.as_posix() in self.repository.tracked_files
            ]
        else:
            self.paths = list(paths)

        if self.use_natsort:
            try:
                from natsort import os_sorted

                self.paths = cast(List[Path], os_sorted(self.paths))
            except ImportError:
                print(
                    "[WARN] Missing `natsort` package; it is recommended to install it\n"
                    "       for consistent natural ordering of files between operating systems.\n"
                    "       Set `use_natsort=False` to suppress this warning."
                )

        if len(self.paths) == 0:
            print("[WARN]: no files to include in the table; resolved paths was empty")

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--dry-run", action="store_true")
        parser.add_argument("-o", "--output", default="README.md")
        args = parser.parse_args()
        if args.output:
            self.output = args.output
        if args.dry_run:
            self.dry_run = True
        return self

    def create_header(self) -> str:
        return f"| {' | '.join(self.columns)} |\n| {' | '.join('-' * len(column) for column in self.columns)} |"

    def create_rows(self) -> Iterable[str]:
        for path in self.paths:
            rows = self.handle_path(path)
            for row in rows:
                cells = (escape_table_cell(cell) for cell in row)
                yield f"| {' | '.join(cells)} |"

    def handle_path(self, path: Path) -> Iterable[Iterable[str]]:
        """Generates a list of rows of cells for a given filepath.

        This function can be a generator and `yield` each row.
        Both `\\n` (new-line) and `|` (pipe) can be used inside cells and will be escaped.
        """
        raise NotImplementedError

    def render(
        self,
        *,
        output: Optional[Union[str, PathLike[str], False]] = None,
        diff: bool = True,
    ):
        with open(self.source, encoding="UTF-8") as file:
            source_content = file.read()

        header = self.create_header()
        rows = "\n".join(self.create_rows())
        regex = self._regex_table(self.table)

        if not regex.search(source_content):
            raise ValueError(
                f"Could not find table to template{f' with id `{self.table}`' if self.table else ''} in \"{self.source}\""
            )

        content = regex.sub(f"\n{header}\n{rows}\n", source_content)

        if diff:
            print_difference(source_content, content)

        if output is not False:
            if output is None:
                output = self.source

            if not self.dry_run:
                with open(output, "w+", encoding="UTF-8") as file:
                    file.write(content)

            print(f"All done!", end="")
            if source_content == content:
                print(" \x1b[94m(up-to-date)\x1b[0m", end="")
            else:
                print(" \x1b[93m(updated)\x1b[0m", end="")
            print(" ✨")

        return content

    @staticmethod
    @lru_cache
    def _regex_table(id_=None) -> Pattern[str]:
        id_ = f"-{id_}" if id_ else ""
        return re.compile(f"(?<=<!-- table{id_} -->)[\s\S]*(?=<!-- table{id_}-end -->)")
