# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import hashlib
import os

from aiohttp import web

from .util import BaseView


# --------------------------------------------------------------------------------------
class ArtifactView(BaseView):
    @classmethod
    def urls(cls):
        yield "/branches/{branch}/{tag}/{job}/{format}/{artifact:.+}"
        yield "/~{user}/branches/{branch}/{tag}/{job}/{format}/{artifact:.+}"
        yield "/%7e{user}/branches/{branch}/{tag}/{job}/{format}/{artifact:.+}"
        yield "/%7E{user}/branches/{branch}/{tag}/{job}/{format}/{artifact:.+}"
        yield "/products/{product}/{variant}/{product_branch}/{version}/{format}/{artifact:.+}"
        yield "/~{user}/products/{product}/{variant}/{product_branch}/{version}/{format}/{artifact:.+}"
        yield "/%7e{user}/products/{product}/{variant}/{product_branch}/{version}/{format}/{artifact:.+}"
        yield "/%7E{user}/products/{product}/{variant}/{product_branch}/{version}/{format}/{artifact:.+}"

    def _get_format(self, create=False):
        match = self.request.match_info
        if "product" in match:
            if create:
                raise web.HTTPBadRequest(reason="Uploading products is not supported")
            fmt = (
                self.repo()
                .get_product(match["product"])
                .get_variant(match["variant"])
                .get_branch(match["product_branch"])
                .get_version(match["version"])
                .get_format(match["format"])
            )
        else:
            job = (
                self.repo()
                .get_branch(match["branch"])
                .get_tag(match["tag"])
                .get_job(match["job"])
            )
            fmt = job.get_format(match["format"])
            if create:
                if match["tag"] == "latest":
                    raise web.HTTPMethodNotAllowed(self.request.method, ["GET"])
                if match["format"] == "container":
                    agent = self.request.headers.get("User-Agent", "")
                    # allow uploading directly between dlrepo servers
                    if not agent.startswith("dlrepo-server/"):
                        raise web.HTTPBadRequest(
                            reason="Uploading container images must be done with docker push"
                        )
                if job.is_locked():
                    raise web.HTTPBadRequest(
                        reason="Cannot upload files in locked jobs"
                    )
        if not create and not fmt.exists():
            raise web.HTTPNotFound()
        return fmt

    async def head(self):
        digest = self.request.headers.get("Digest")
        if digest is not None:
            try:
                filepath = self.repo().blob_path(digest)
                if not filepath.is_file():
                    raise web.HTTPNotFound()
            except ValueError as e:
                raise web.HTTPUnprocessableEntity(reason=str(e)) from e

        else:
            fmt = self._get_format()
            artifact = self.request.match_info["artifact"]
            try:
                filepath = fmt.get_filepath(artifact)
            except PermissionError as e:
                raise web.HTTPBadRequest(reason=str(e)) from e
            except FileNotFoundError as e:
                raise web.HTTPNotFound() from e
            if filepath.is_dir():
                raise web.HTTPNotFound()
            url = fmt.url() + artifact
            if url != self.request.path:
                raise web.HTTPFound(url)
            digest = fmt.get_digests()[artifact]

        return web.Response(
            headers={"Digest": digest, "Content-Length": str(filepath.stat().st_size)}
        )

    async def get(self):
        fmt = self._get_format()
        artifact = self.request.match_info["artifact"]
        try:
            filepath = fmt.get_filepath(artifact)
        except PermissionError as e:
            raise web.HTTPBadRequest(reason=str(e)) from e
        except FileNotFoundError as e:
            if artifact.endswith(".sha256"):
                artifact = artifact[: -len(".sha256")]
                digest = fmt.get_digests().get(artifact)
                if digest is not None:
                    algo, digest = digest.split(":")
                    if algo == "sha256":
                        url = fmt.url() + artifact + ".sha256"
                        if url != self.request.path:
                            raise web.HTTPFound(url)
                        artifact = os.path.basename(artifact)
                        return web.Response(text=f"{digest}  {artifact}\n")
            raise web.HTTPNotFound() from e
        url = fmt.url() + artifact
        if filepath.is_dir():
            if "html" in self.request.headers.get("Accept", "json"):
                if not url.endswith("/"):
                    raise web.HTTPFound(url + "/")
                if url != self.request.path:
                    raise web.HTTPFound(url)
                return await self.autoindex(fmt, artifact)
            raise web.HTTPNotFound()
        if url != self.request.path:
            raise web.HTTPFound(url)
        digest = fmt.get_digests().get(artifact)
        if not digest and fmt.name == "container":
            algo = filepath.parent.parent.name
            if algo in hashlib.algorithms_guaranteed:
                digest = f"{algo}:{filepath.name}"
        headers = {}
        if digest:
            headers["Digest"] = digest
        return self.file_response(filepath, headers=headers)

    async def put(self):
        fmt = self._get_format(create=True)
        artifact = self.request.match_info["artifact"]
        digest = self.request.headers.get("Digest")
        try:
            if self.request.headers.get("X-Dlrepo-Link") == digest:
                # no content, link existing blob
                fmt.link_file(digest, artifact)
            else:
                await fmt.add_file(artifact, self.request.content.read, digest)
        except FileNotFoundError as e:
            raise web.HTTPNotFound() from e
        except PermissionError as e:
            raise web.HTTPBadRequest(reason=str(e)) from e
        except ValueError as e:
            raise web.HTTPUnprocessableEntity(reason=str(e)) from e
        return web.HTTPCreated()
