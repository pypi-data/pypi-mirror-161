# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
from http import HTTPStatus
import json
import os
from pathlib import Path
import tarfile
from typing import Dict, Tuple

from aiohttp import web
from aiohttp.abc import AbstractStreamWriter
import aiohttp_jinja2

from . import auth


# --------------------------------------------------------------------------------------
class BaseView(web.View):
    @classmethod
    def urls(cls):
        raise NotImplementedError()

    def repo(self):
        r = self.request.app["dlrepo_artifact_repository"]
        if "user" in self.request.match_info:
            r = r.get_user_repo(self.request.match_info["user"])
        return r

    def access_granted(self, url: str) -> bool:
        if auth.AuthBackend.AUTH_DISABLED:
            return True
        auth_backend = self.request.app[auth.AuthBackend.KEY]
        acls = self.request["dlrepo_user_acls"]
        return auth_backend.access_granted(acls, False, url)

    X_SENDFILE_HEADER = os.getenv("DLREPO_X_SENDFILE_HEADER", None)

    def file_response(self, path, status=HTTPStatus.OK, headers=None):
        if self.X_SENDFILE_HEADER:
            if headers is None:
                headers = {}
            headers[self.X_SENDFILE_HEADER] = str(path)
            if "Content-Type" not in headers:
                # Force empty Content-Type to prevent aiohttp from adding the
                # application/octet-stream default value.
                # The reverse proxy will guess the content type based on the file name.
                headers["Content-Type"] = ""
            return web.Response(status=status, headers=headers)
        return web.FileResponse(path, status=status, headers=headers)

    async def json_body(self):
        try:
            return await self.request.json()
        except json.JSONDecodeError as e:
            raise web.HTTPBadRequest(reason=f"invalid JSON data: {e}") from e

    async def autoindex(self, fmt, relpath):
        dirs, files = fmt.list_dir(relpath)
        if "index.html" in files:
            return self.file_response(
                fmt.get_filepath(os.path.join(relpath, "index.html"))
            )
        data = {
            "artifact_format": {
                "name": fmt.name,
                "relpath": relpath.rstrip("/"),
                "dirs": dirs,
                "files": files,
            },
        }
        return aiohttp_jinja2.render_template("autoindex.html", self.request, data)


# --------------------------------------------------------------------------------------
class TarResponse(web.StreamResponse):
    def __init__(self, members: Dict[str, str], root_dir: Path, tar_prefix: str = None):
        self._members = members
        self._root_dir = root_dir
        self._tar_prefix = tar_prefix
        super().__init__()
        self.content_type = "application/x-tar"
        if self._tar_prefix is not None:
            filename = self._tar_prefix + ".tar"
            self.headers.add("Content-Disposition", f"attachment; filename={filename}")

    async def prepare(self, request: web.Request) -> AbstractStreamWriter:
        # pylint: disable=too-many-locals
        writer = await super().prepare(request)
        transport = request.transport
        loop = asyncio.get_running_loop()

        tar_offset = 0
        sha256sums = []

        for member, digest in sorted(self._members.items()):
            info, path = await self._get_tar_info(member)
            algo, digest = digest.split(":")
            if algo == "sha256":
                sha256sums.append(f"{digest}  {member}\n")

            buf = info.tobuf(tarfile.PAX_FORMAT, "utf-8")
            await self.write(buf)  # includes http chunk header & trailer
            tar_offset += len(buf)

            fobj = await loop.run_in_executor(None, path.open, "rb")
            try:
                # loop.sendfile works on the raw transport class and does not include
                # http chunk headers/trailers. Manually insert them.
                transport.write(self.CHUNK_HEADER % info.size)
                await loop.sendfile(transport, fobj, count=info.size)
                transport.write(self.CHUNK_TRAILER)

                blocks, remainder = divmod(info.size, tarfile.BLOCKSIZE)
                if remainder > 0:
                    # add tar member padding (includes http chunk header & trailer)
                    await self.write(self._padding(tarfile.BLOCKSIZE - remainder))
                    blocks += 1
                tar_offset += blocks * tarfile.BLOCKSIZE
            finally:
                await loop.run_in_executor(None, fobj.close)

        if sha256sums:
            tar_offset += await self._write_sha256sums(sha256sums)

        # add tar format trailer
        tar_trailer = self._padding(2 * tarfile.BLOCKSIZE)
        tar_offset += 2 * tarfile.BLOCKSIZE
        remainder = tar_offset % tarfile.RECORDSIZE
        if remainder > 0:
            tar_trailer += self._padding(tarfile.RECORDSIZE - remainder)

        await self.write_eof(tar_trailer)  # includes http chunk header & trailer

        return writer

    CHUNK_HEADER = b"%x\r\n"
    CHUNK_TRAILER = b"\r\n"

    @staticmethod
    def _padding(size):
        return b"\x00" * size

    async def _get_tar_info(self, name: str) -> Tuple[tarfile.TarInfo, Path]:
        path = self._root_dir / name
        if self._tar_prefix is not None:
            name = f"{self._tar_prefix}/{name}"

        loop = asyncio.get_running_loop()
        st = await loop.run_in_executor(None, path.lstat)

        info = tarfile.TarInfo(name)
        info.mode = st.st_mode
        info.size = st.st_size

        return info, path

    async def _write_sha256sums(self, sha256sums):
        name = "SHA256SUMS.txt"
        if self._tar_prefix is not None:
            name = f"{self._tar_prefix}/{name}"

        data = "".join(sha256sums).encode("utf-8")

        info = tarfile.TarInfo(name)
        info.mode = 0o0644
        info.size = len(data)

        buf = info.tobuf(tarfile.PAX_FORMAT, "utf-8") + data
        offset = len(buf)
        blocks, remainder = divmod(info.size, tarfile.BLOCKSIZE)
        if remainder > 0:
            # add tar member padding
            buf += self._padding(tarfile.BLOCKSIZE - remainder)
            blocks += 1
        offset += blocks * tarfile.BLOCKSIZE

        await self.write(buf)  # includes http chunk header & trailer

        return offset
