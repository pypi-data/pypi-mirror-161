# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import json
import logging
import os
from pathlib import Path
import re
from typing import Awaitable, Callable, Dict, Iterator, List, Tuple

from cachetools import LRUCache, cachedmethod

from .util import SubDir, file_digest


LOG = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------
class ArtifactFormat(SubDir):
    """
    TODO
    """

    def url_bit(self) -> str:
        return self.name

    def get_files(self) -> Iterator[str]:
        for root, dirs, files in os.walk(self._path):
            dirs.sort()
            files.sort()
            for f in files:
                f = Path(root, f)
                if self._is_reserved_file(f):
                    continue
                if f.is_file():
                    yield str(f.relative_to(self._path))

    def archive_name(self) -> str:
        return f"{self.parent.archive_name()}-{self.name}"

    _is_reserved_cache = LRUCache(4096)

    @cachedmethod(lambda self: self._is_reserved_cache)
    def _is_reserved_file(self, path, *, resolve=False):
        digests = self.digest_path()
        dirty = self._dirty_path()
        if resolve:
            digests = digests.resolve()
            dirty = dirty.resolve()
        return path in (digests, dirty)

    def list_dir(self, relpath: str) -> Tuple[List[str], List[str]]:
        path = self.get_filepath(relpath)
        if not path.is_dir():
            raise NotADirectoryError(relpath)
        dirs = []
        files = []
        for e in path.iterdir():
            if self._is_reserved_file(e, resolve=True):
                continue
            if e.is_dir():
                dirs.append(e.name)
            elif e.is_file():
                files.append(e.name)
        return dirs, files

    def _check_filepath(self, relpath: str) -> Path:
        if relpath.startswith("/") or any(x in (".", "..") for x in relpath.split("/")):
            raise PermissionError(relpath)
        path = self._path / relpath
        if self._is_reserved_file(path):
            raise PermissionError(relpath)
        return path

    def get_filepath(self, relpath: str) -> Path:
        return self._check_filepath(relpath).resolve(strict=True)

    def get_digests(self) -> Dict[str, str]:
        try:
            return json.loads(self.digest_path().read_text())
        except FileNotFoundError:
            if self.name != "container":
                return {}
            try:
                return {f: f"sha256:{os.path.basename(f)}" for f in self.get_files()}
            except OSError:
                return {}
        except (OSError, ValueError):
            return {}

    def digest_path(self) -> Path:
        return self._path / ".digests"

    async def add_file(
        self,
        relpath: str,
        read: Callable[[int], Awaitable[bytes]],
        digest: str,
    ):
        self._check_filepath(relpath)
        uuid = self.root().next_upload()
        await self.root().update_upload(uuid, read)
        await self.root().finalize_upload(uuid, digest)
        # avoid counting disk usage twice (already counted in update_upload()
        self.link_file(digest, relpath, ignore_quota=True)

    def link_file(self, digest: str, relpath: str, ignore_quota: bool = False):
        was_dirty = self.is_dirty()
        self.set_dirty(True)
        try:
            path = self._check_filepath(relpath)
            if ignore_quota:
                self.root().link_blob_ignore_quota(digest, path)
            else:
                self.root().link_blob(digest, path)
        except:
            if not was_dirty:
                self.set_dirty(False)
            raise
        # update digests file
        digests = self.get_digests()
        digests[relpath] = digest
        self.digest_path().write_text(json.dumps(digests, sort_keys=True))

    def _dirty_path(self) -> Path:
        return self._path / ".dirty"

    def is_dirty(self) -> bool:
        return self._dirty_path().is_file()

    def set_dirty(self, dirty: bool):
        path = self._dirty_path()
        if dirty:
            self.create()
            path.touch()
        elif path.is_file():
            path.unlink()
            try:
                os.removedirs(path.parent)
            except OSError:
                pass

    POST_PROCESS_CMD = os.getenv("DLREPO_POST_PROCESS_CMD")
    POST_PROCESS_FILTER = os.getenv("DLREPO_POST_PROCESS_FILTER")

    async def post_process(self):
        if not self.POST_PROCESS_CMD:
            return

        digests = self.get_digests()
        if self.POST_PROCESS_FILTER and not any(
            re.match(self.POST_PROCESS_FILTER, f) for f in digests.keys()
        ):
            return

        LOG.debug(
            "running post process command: %s (cwd %s)",
            self.POST_PROCESS_CMD,
            self._path,
        )

        ctimes = {}
        for f in digests.keys():
            # make a temporary copy of all hardlinked files so that post-process can
            # safely modify them
            self.root().copy_blob(digests[f], self._path / f)
            # record content modification time to only recalculate digest if needed
            ctimes[f] = (self._path / f).stat().st_ctime

        try:
            proc = await asyncio.create_subprocess_exec(
                self.POST_PROCESS_CMD, cwd=self._path
            )
            ret = await proc.wait()
            if ret != 0:
                raise OSError(
                    f"command {self.POST_PROCESS_CMD} exited {ret} (cwd {self._path})"
                )
        finally:
            # always refresh digests even on error to ensure consistency
            await self._refresh_digests(digests, ctimes)

    async def _refresh_digests(self, digests, ctimes):
        new_digests = {}
        loop = asyncio.get_running_loop()

        for f in self.get_files():
            fpath = self._path / f
            if f in ctimes and f in digests and ctimes[f] == fpath.stat().st_ctime:
                # file was not modified by post processing, avoid recalculating digest
                digest = new_digests[f] = digests[f]
            else:
                # new or modified file
                digest = await loop.run_in_executor(None, file_digest, "sha256", fpath)
                digest = f"sha256:{digest}"
                new_digests[f] = digest

            # deduplicate files, remove temporary copies
            blob = self.root().blob_path(digest)
            if blob.is_file():
                # replace file with hardlink to existing blob
                fpath.unlink()
                os.link(blob, fpath)
            else:
                # add hardlink to new blob
                blob.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
                os.link(fpath, blob)

        self.digest_path().write_text(json.dumps(new_digests, sort_keys=True))
