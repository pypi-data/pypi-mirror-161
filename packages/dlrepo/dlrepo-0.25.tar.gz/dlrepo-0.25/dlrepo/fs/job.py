# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import errno
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Dict, Iterator

from .fmt import ArtifactFormat
from .product import Version
from .util import SubDir, file_digest


LOG = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------
class Job(SubDir):
    """
    TODO
    """

    def create(self):
        super().create()
        stamp = self._path / ".stamp"
        if not stamp.exists():
            stamp.touch()

    @classmethod
    def creation_date(cls, j):
        stamp = j.path() / ".stamp"
        if stamp.is_file():
            # prefer mtime over ctime
            # on UNIX, ctime is "the time of most recent metadata change" whereas
            # mtime is "most recent content modification"
            return stamp.stat().st_mtime
        return 0

    @property
    def timestamp(self) -> int:
        return Job.creation_date(self)

    def get_formats(self) -> Iterator[ArtifactFormat]:
        yield from ArtifactFormat.all(self)

    def get_format(self, name: str) -> ArtifactFormat:
        return ArtifactFormat(self, name)

    def archive_name(self) -> str:
        data = self.get_metadata()
        if {"product", "product_variant", "version"} <= set(data):
            return f"{data['product']}-{data['product_variant']}-v{data['version']}"
        return f"{self.name}-{self.parent.name}"

    def _metadata_path(self):
        return self._path / ".metadata"

    def _product_link_path(self):
        return self._path / ".product"

    def _released_path(self) -> Path:
        return self._path / ".released"

    def is_released(self) -> bool:
        return self._released_path().is_file()

    def set_released(self, released: bool):
        path = self._released_path()
        if released:
            path.touch()
        elif path.is_file():
            path.unlink()

    @staticmethod
    def update_symlink(dst, link):
        if link.exists():
            if link.is_symlink():
                link.unlink()
            else:
                raise OSError(errno.ENOTEMPTY, f"{link} exists and is not a symlink")
        link.symlink_to(os.path.relpath(dst, link.parent))

    def _link_to_product(self, version: Version):
        """
        Link the job to its product, according to the job metadata.
        Create the product fs if needed.
        The links are created in both ways:

        - From the job to its product version:
            $ROOT/branches/<branch>/<tag>/<job>/.product ->
                $ROOT/products/<product>/<variant>/<branch>/<version>

        - From the product version to the job(s), for each format:
            $ROOT/products/<product>/<variant>/<branch>/<version>/<format> ->
                $ROOT/branches/<branch>/<tag>/<job>/<format>

        The formats in a product version are not necessarily linked to the same job.
        """
        version.create()
        self.update_symlink(version.path(), self._product_link_path())
        for fmt in self.get_formats():
            self.update_symlink(fmt.path(), version.path() / fmt.name)
        container = self.path() / "container"
        if container.is_dir():
            self.update_symlink(container, version.path() / "container")

    def _cleanup_product_tree(self):
        link = self._product_link_path()
        if not link.is_symlink():
            return
        if not link.is_dir():
            link.unlink()
            return
        product = link.resolve()
        for d in product.iterdir():
            if not d.is_symlink():
                continue
            if not d.is_dir():
                continue
            try:
                if d.resolve().samefile(self.path() / d.name):
                    d.unlink()
            except FileNotFoundError:
                # same product, different jobs (e.g. doc + binaries)
                pass
        try:
            if os.listdir(product) == [".stamp"]:
                (product / ".stamp").unlink()
            # cleanup empty dirs
            os.removedirs(product)
        except OSError:
            # directory not empty, abort
            pass
        link.unlink()

    def get_metadata(self) -> Dict:
        try:
            data = json.loads(self._metadata_path().read_text())
        except (OSError, ValueError):
            data = {}
        data["locked"] = self.is_locked()
        data["name"] = self.name
        data["released"] = self.is_released()
        return data

    def _lock_path(self):
        return self.path() / ".locked"

    def is_locked(self) -> bool:
        return self._lock_path().is_file()

    def _digest_path(self) -> Path:
        return self._path / ".digest"

    def get_digest(self):
        try:
            return self._digest_path().read_text()
        except OSError:
            return ""

    async def set_digest(self):
        loop = asyncio.get_running_loop()
        digests = {}
        for fmt in self.get_formats():
            if fmt.name == "container":
                _, digest = self.root().container_registry.manifest_by_parent(
                    self._path
                )
                digests["container"] = digest
            else:
                digest = await loop.run_in_executor(
                    None, file_digest, "sha256", fmt.digest_path()
                )
                digests[fmt.name] = f"sha256:{digest}"
        digest = await loop.run_in_executor(
            None, file_digest, "sha256", self._metadata_path()
        )
        digests[".metadata"] = f"sha256:{digest}"
        data = json.dumps(digests, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(data).hexdigest()
        self._digest_path().write_text(digest)

    async def set_locked(self, locked: bool):
        if not self.exists():
            raise FileNotFoundError()
        self.create()
        path = self._lock_path()
        if locked:
            if self.is_locked():
                return
            if any(fmt.is_dirty() for fmt in self.get_formats()):
                raise OSError("Job has dirty formats")
            self.add_metadata({})
            await self.set_digest()
            path.touch()
        elif path.is_file():
            path.unlink()

    def _internal_path(self) -> Path:
        return self._path / ".internal"

    def is_internal(self) -> bool:
        return self._internal_path().is_file()

    def set_internal(self, internal: bool):
        path = self._internal_path()
        if internal:
            path.touch()
        elif path.is_file():
            path.unlink()

    def add_metadata(self, new_data: Dict):
        if self.is_locked():
            raise FileExistsError("Job is locked")
        self._cleanup_product_tree()
        metadata_path = self._metadata_path()
        try:
            data = json.loads(metadata_path.read_text())
        except (OSError, ValueError):
            data = {}
        for k, v in new_data.items():
            v = str(v or "").lower()
            if v == "":
                data.pop(k, None)
            else:
                data[k] = v
        self.create()
        metadata_path.write_text(json.dumps(data, sort_keys=True))
        if {"product", "version", "product_branch", "product_variant"} <= set(data):
            self._link_to_product(
                self.root()
                .get_product(str(data["product"]))
                .get_variant(str(data["product_variant"]))
                .get_branch(str(data["product_branch"]))
                .get_version(str(data["version"]))
            )

    def delete(self):
        if not self.exists():
            raise FileNotFoundError()
        self._cleanup_product_tree()
        self.root().rmtree(self._path)
