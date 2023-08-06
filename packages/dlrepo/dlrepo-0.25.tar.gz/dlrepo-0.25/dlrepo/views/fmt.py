# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import logging

from aiohttp import web

from .util import BaseView, TarResponse


LOG = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------
class FormatDirView(BaseView):
    @classmethod
    def urls(cls):
        yield "/branches/{branch}/{tag}/{job}/{format}/"
        yield "/~{user}/branches/{branch}/{tag}/{job}/{format}/"
        yield "/products/{product}/{variant}/{product_branch}/{version}/{format}/"
        yield "/~{user}/products/{product}/{variant}/{product_branch}/{version}/{format}/"

    async def head(self):
        fmt = _get_format(self.repo(), self.request.match_info)
        if fmt.is_dirty():
            raise web.HTTPNotFound()
        if fmt.url() != self.request.path:
            raise web.HTTPFound(fmt.url())
        return web.Response()

    async def get(self):
        """
        Get the list of files of a job for the specified format.
        """
        fmt = _get_format(self.repo(), self.request.match_info)
        if fmt.url() != self.request.path:
            raise web.HTTPFound(fmt.url())
        if "html" in self.request.headers.get("Accept", "json"):
            return await self.autoindex(fmt, "")
        data = {
            "artifact_format": {
                "name": fmt.name,
                "dirty": fmt.is_dirty(),
                "files": list(fmt.get_digests().keys()),
            },
        }
        return web.json_response(data)

    async def patch(self):
        """
        Remove the dirty flag from a format.
        """
        version = self.request.match_info.get(
            "tag", self.request.match_info.get("version")
        )
        if "product" in self.request.match_info or version in ("latest", "stable"):
            raise web.HTTPMethodNotAllowed("PATCH", ["GET"])
        fmt = _get_format(self.repo(), self.request.match_info)
        try:
            await fmt.post_process()
            fmt.set_dirty(False)
        except OSError as e:
            LOG.error("post process failed: %s", e)
            raise web.HTTPInternalServerError(reason="post process failed") from e
        return web.Response()


# --------------------------------------------------------------------------------------
class FormatArchiveView(BaseView):
    @classmethod
    def urls(cls):
        yield "/branches/{branch}/{tag}/{job}/{format}.tar"
        yield "/~{user}/branches/{branch}/{tag}/{job}/{format}.tar"
        yield "/products/{product}/{variant}/{product_branch}/{version}/{format}.tar"
        yield "/~{user}/products/{product}/{variant}/{product_branch}/{version}/{format}.tar"

    async def head(self):
        fmt = _get_format(self.repo(), self.request.match_info)
        if fmt.is_dirty():
            raise web.HTTPNotFound()
        url = fmt.url().rstrip("/") + ".tar"
        if url != self.request.path:
            raise web.HTTPFound(url)
        return web.Response()

    async def get(self):
        fmt = _get_format(self.repo(), self.request.match_info)
        url = fmt.url().rstrip("/") + ".tar"
        if url != self.request.path:
            raise web.HTTPFound(url)
        return TarResponse(fmt.get_digests(), fmt.path(), fmt.archive_name())


# --------------------------------------------------------------------------------------
class FormatDigestsView(BaseView):
    @classmethod
    def urls(cls):
        yield "/branches/{branch}/{tag}/{job}/{format}.sha256"
        yield "/~{user}/branches/{branch}/{tag}/{job}/{format}.sha256"
        yield "/products/{product}/{variant}/{product_branch}/{version}/{format}.sha256"
        yield "/~{user}/products/{product}/{variant}/{product_branch}/{version}/{format}.sha256"

    async def get(self):
        fmt = _get_format(self.repo(), self.request.match_info)
        url = fmt.url().rstrip("/") + ".sha256"
        if url != self.request.path:
            raise web.HTTPFound(url)
        sha256sums = []
        for artifact, digest in sorted(fmt.get_digests().items()):
            algo, digest = digest.split(":")
            if algo == "sha256":
                sha256sums.append(f"{digest}  {artifact}\n")
        return web.Response(text="".join(sha256sums))


# --------------------------------------------------------------------------------------
class FormatFileView(BaseView):
    @classmethod
    def urls(cls):
        yield "/branches/{branch}/{tag}/{job}/{format}"
        yield "/~{user}/branches/{branch}/{tag}/{job}/{format}"
        yield "/products/{product}/{variant}/{product_branch}/{version}/{format}"
        yield "/~{user}/products/{product}/{variant}/{product_branch}/{version}/{format}"

    async def head(self):
        fmt = _get_format(self.repo(), self.request.match_info)
        if fmt.is_dirty():
            raise web.HTTPNotFound()
        url = fmt.url()
        files = list(fmt.get_digests().keys())
        if len(files) == 1:
            url += files[0]
        if url != self.request.path:
            raise web.HTTPFound(url)
        return web.Response()

    async def get(self):
        """
        If only one file in $format:
            redirect to /branches/$branch/$tag/$job/$format/$file
        else:
            redirect to /branches/$branch/$tag/$job/$format/
        """
        fmt = _get_format(self.repo(), self.request.match_info)
        files = list(fmt.get_digests().keys())
        if len(files) == 1 and files[0] != "index.html":
            return web.HTTPFound(fmt.url() + files[0])
        return web.HTTPFound(fmt.url())


# --------------------------------------------------------------------------------------
def _get_format(repo, match_info):
    try:
        if "product" in match_info:
            fmt = (
                repo.get_product(match_info["product"])
                .get_variant(match_info["variant"])
                .get_branch(match_info["product_branch"])
                .get_version(match_info["version"])
                .get_format(match_info["format"])
            )
        else:
            fmt = (
                repo.get_branch(match_info["branch"])
                .get_tag(match_info["tag"])
                .get_job(match_info["job"])
                .get_format(match_info["format"])
            )
    except FileNotFoundError as e:
        raise web.HTTPNotFound() from e
    if not fmt.exists():
        raise web.HTTPNotFound()
    return fmt
