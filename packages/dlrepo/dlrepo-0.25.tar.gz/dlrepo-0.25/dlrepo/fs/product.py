# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import logging
from pathlib import Path
from typing import Callable, Iterator

from .fmt import ArtifactFormat
from .util import SubDir


LOG = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------
class Product(SubDir):
    """
    TODO
    """

    ROOT_DIR = "products"

    @classmethod
    def parent_path(cls, parent: "ArtifactRepository") -> Path:
        return parent.path() / cls.ROOT_DIR

    def url_bit(self) -> str:
        return f"products/{self.name}"

    def get_variants(self) -> Iterator["Variant"]:
        yield from Variant.all(self)

    def get_variant(self, name: str) -> "Variant":
        return Variant(self, name)


# --------------------------------------------------------------------------------------
class Variant(SubDir):
    """
    TODO
    """

    def get_branches(self) -> Iterator["ProductBranch"]:
        yield from ProductBranch.all(self)

    def get_branch(self, name: str) -> "ProductBranch":
        return ProductBranch(self, name)


# --------------------------------------------------------------------------------------
class ProductBranch(SubDir):
    """
    TODO
    """

    def get_versions(
        self, access_cb: Callable[[str], bool] = None
    ) -> Iterator["Version"]:
        for v in Version.all(self):
            if access_cb is not None and not access_cb(v.url()):
                continue
            yield v

    def get_version(
        self, name: str, access_cb: Callable[[str], bool] = None
    ) -> "Version":
        if name in ("latest", "stable"):
            versions = list(self.get_versions(access_cb))
            versions.sort(key=Version.creation_date, reverse=True)
            for v in versions:
                if name == "latest":
                    return v
                if v.is_released():
                    return v
            raise FileNotFoundError(name)
        return Version(self, name)


# --------------------------------------------------------------------------------------
class Version(SubDir):
    """
    TODO
    """

    def create(self):
        super().create()
        stamp = self.path() / ".stamp"
        if not stamp.exists():
            stamp.touch()

    def archive_name(self) -> str:
        variant = self.parent.parent
        product = variant.parent
        return f"{product.name}-{variant.name}-v{self.name}"

    @classmethod
    def creation_date(cls, v):
        stamp = v.path() / ".stamp"
        if stamp.is_file():
            # prefer mtime over ctime
            # on UNIX, ctime is "the time of most recent metadata change" whereas
            # mtime is "most recent content modification"
            return stamp.stat().st_mtime
        return 0

    @property
    def timestamp(self) -> int:
        return Version.creation_date(self)

    def is_released(self) -> bool:
        for fmt in self.get_formats():
            released_path = fmt.path().resolve().parent / ".released"
            if released_path.is_file():
                return True
        return False

    def is_locked(self) -> bool:
        for fmt in self.get_formats():
            released_path = fmt.path().resolve().parent.parent / ".locked"
            if released_path.is_file():
                return True
        return False

    def get_formats(self) -> Iterator[ArtifactFormat]:
        yield from ArtifactFormat.all(self)

    def get_format(self, name: str) -> ArtifactFormat:
        return ArtifactFormat(self, name)
