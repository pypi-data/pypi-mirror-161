# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import hashlib
import os
from pathlib import Path
import re
from typing import Iterator, Tuple, Union


# --------------------------------------------------------------------------------------
class SubDir:
    def __init__(self, parent: Union["AbstractRepository", "SubDir"], name: str):
        self.parent = parent
        self.name = name.lower()
        self._path = self._resolve_path()

    def root(self) -> "AbstractRepository":
        r = self
        while r.parent is not None:
            r = r.parent
        return r

    def url_bit(self) -> str:
        return self.name

    def url(self) -> str:
        bits = [self.url_bit()]
        r = self
        while r.parent is not None:
            r = r.parent
            if r.url_bit() is not None:
                bits.insert(0, r.url_bit())
        return f"/{'/'.join(bits)}/"

    @classmethod
    def all(cls, parent) -> Iterator["SubDir"]:
        try:
            dirs = list(cls.parent_path(parent).iterdir())
            dirs.sort(key=lambda d: d.name)
            for d in dirs:
                if d.name.startswith(".") or not d.is_dir():
                    continue
                yield cls(parent, d.name)
        except FileNotFoundError:
            pass

    @classmethod
    def parent_path(cls, parent: "SubDir") -> Path:
        return parent.path()

    def _resolve_path(self) -> Path:
        path = self.parent_path(self.parent) / self.name
        if self.name.startswith(".") or "/" in self.name:
            raise FileNotFoundError(path)
        return path

    def exists(self) -> bool:
        return self.path().is_dir()

    def create(self):
        if self.parent is not None:
            self.parent.create()
        self.path().mkdir(mode=0o755, parents=True, exist_ok=True)

    def path(self) -> Path:
        return self._path


# --------------------------------------------------------------------------------------
HASH_ALGOS = "|".join(hashlib.algorithms_guaranteed)
ALGO_RE = re.compile(
    rf"""
    ^
    (?P<algo>{HASH_ALGOS})
    :
    (?P<digest>[A-Fa-f0-9]+)
    $
    """,
    re.VERBOSE,
)


def parse_digest(digest: str) -> Tuple[str, str]:
    match = ALGO_RE.match(digest)
    if not match:
        raise ValueError(f"invalid digest: {digest}")
    return match.groups()


# --------------------------------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("DLREPO_CHUNK_SIZE", str(256 * 1024)))


def file_digest(algo: str, path: Path) -> str:
    h = hashlib.new(algo)
    buf = bytearray(CHUNK_SIZE)
    view = memoryview(buf)
    with path.open("rb") as f:
        while True:
            n = f.readinto(buf)
            if not n:
                break
            h.update(view[:n])
    return h.hexdigest()


# --------------------------------------------------------------------------------------
def human_readable(value):
    if value == 0:
        return "0"
    units = ("K", "M", "G", "T")
    i = 0
    unit = ""
    while value >= 1000 and i < len(units):
        unit = units[i]
        value /= 1000
        i += 1
    if value < 100:
        return f"{value:.1f}{unit}"
    return f"{value:.0f}{unit}"
