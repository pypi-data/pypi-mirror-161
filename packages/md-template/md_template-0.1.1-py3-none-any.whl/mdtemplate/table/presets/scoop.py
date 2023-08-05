import json
from pathlib import Path
from typing import Union, Iterable, Dict, List

from .. import TableTemplate


class ScoopTableTemplate(TableTemplate):
    """This preset expects manifests to be located in `bucket/*.json`.

    The preset will attempt to extract a friendly name from the manifest. It will do this by
    pulling the name from the shortcut if defined or the filename. A custom name can be
    defined by adding a comment in the form `:Custom Name`. It will also apply an extension to
    the name based on the end of the filename, for example, `name-np` -> `Name (Non-Portable)`.
    """

    files = "bucket/*.json"
    columns = ("Manifests",)

    def handle_path(self, path: Path) -> Iterable[Iterable[str]]:
        with open(path) as file:
            manifest = json.loads(file.read())

        name = self.get_name(path.stem, manifest)
        desc = manifest.get("description", "")
        if desc:
            desc = f"\n{manifest['description']}\n\n"

        yield [
            f"[**{name}**]({manifest['homepage']}) — [`{path.stem}`]({path.as_posix()}){desc}"
        ]

    @classmethod
    def get_name(cls, filename: str, manifest: Dict):
        try:
            name = manifest["shortcuts"][0][1]
        except (KeyError, IndexError):
            name = cls.get_name_from_comment(manifest)
            if not name:
                name = (
                    filename.replace("-portable", "")
                    .replace("-np", "")
                    .replace("-py", "")
                    .replace("-nightly", "")
                )
        if filename.endswith("-portable"):
            name += " (Portable)"
        if filename.endswith("-np"):
            name += " (Non-Portable)"
        if filename.endswith("-nightly"):
            name += " (Nightly)"
        return name

    @staticmethod
    def get_name_from_comment(manifest: Dict):
        comments: Union[str, List[str]] = manifest.get("##", [])
        if type(comments) == str:
            comments = [comments]
        for comment in comments:
            if comment.startswith(":"):
                return comment[1:]
