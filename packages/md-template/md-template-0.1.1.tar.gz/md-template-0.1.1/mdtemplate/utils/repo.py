import os
import re
import subprocess
from typing import List

_RE_REPO_URL = re.compile(r"https?://(?P<domain>.+)/(?P<owner>.+)/(?P<name>.+)")


class Repository:
    """Representation of a Git repository, with lazy-loaded properties."""

    _url: str = None
    _name: str = None
    _owner: str = None
    _branch: str = None
    _tracked_files: List[str] = []

    def __init__(self, path="."):
        self.path = os.path.abspath(path)

    @property
    def branch(self):
        if not self._branch:
            self._branch = (
                subprocess.check_output(
                    ["git", "-C", self.path, "branch", "--show-current"]
                )
                .strip()
                .decode()
            )
        return self._branch

    @property
    def url(self):
        self.load_url()
        return self._url

    @property
    def name(self):
        self.load_url()
        return self._name

    @property
    def owner(self):
        self.load_url()
        return self._owner

    def load_url(self):
        if self._url:
            return

        self._url = (
            subprocess.check_output(
                ["git", "-C", self.path, "remote", "get-url", "origin"]
            )
            .strip()
            .removesuffix(b".git")
            .decode()
        )

        match = _RE_REPO_URL.match(self._url)

        self._name = match.group("name")
        self._owner = match.group("owner")

    @property
    def tracked_files(self):
        if not self._tracked_files:
            self._tracked_files = (
                subprocess.check_output(["git", "-C", self.path, "ls-files"])
                .decode()
                .splitlines(keepends=False)
            )
        return self._tracked_files
