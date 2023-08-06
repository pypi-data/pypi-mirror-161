# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
from datetime import datetime, timezone
import os
import pathlib

from aiohttp import web
import aiohttp_jinja2
import jinja2

from ..fs.util import human_readable
from .artifact import ArtifactView
from .branch import BranchesView, BranchView
from .container import (
    BlobsUploadsView,
    BlobsView,
    CatalogView,
    ManifestReadOnlyView,
    ManifestView,
    NewBlobUploadView,
    RootView,
    TagsListView,
)
from .fmt import FormatArchiveView, FormatDigestsView, FormatDirView, FormatFileView
from .job import JobArchiveView, JobView
from .product import (
    ProductBranchView,
    ProductsView,
    ProductVariantView,
    ProductView,
    VersionArchiveView,
    VersionView,
)
from .tag import TagView
from .util import BaseView


# --------------------------------------------------------------------------------------
class HomeView(BaseView):
    @classmethod
    def urls(cls):
        yield "/"
        yield "/~{user}"
        yield "/~{user}/"

    def _get_version_dirs(self, repo):
        stamps = list(repo.path().glob("products/*/*/*/*/.stamp"))
        # prefer mtime over ctime
        # on UNIX, ctime is "the time of most recent metadata change" whereas
        # mtime is "most recent content modification"
        stamps.sort(key=lambda s: s.stat().st_mtime, reverse=True)
        versions = []
        for s in stamps:
            versions.append(s.parent)
        return versions

    async def get_latest_releases(self, repo, num=10):
        loop = asyncio.get_running_loop()
        version_dirs = await loop.run_in_executor(None, self._get_version_dirs, repo)
        versions = []
        for v in version_dirs:
            version = (
                repo.get_product(v.parent.parent.parent.name)
                .get_variant(v.parent.parent.name)
                .get_branch(v.parent.name)
                .get_version(v.name)
            )
            if self.access_granted(version.url()):
                versions.append(version)
                if len(versions) == num:
                    break
        return versions

    @aiohttp_jinja2.template("home.html")
    async def get(self):
        repo = self.repo()
        user = self.request.match_info.get("user")
        if user:
            if not repo.path().exists():
                raise web.HTTPNotFound()
            if not self.request.path.endswith("/"):
                raise web.HTTPFound(self.request.path + "/")
            return {
                "disk_usage": repo.disk_usage,
                "quota": repo.QUOTA,
                "human_readable": human_readable,
                "latest_releases": await self.get_latest_releases(repo),
                "access": {
                    "branches": self.access_granted(repo.url() + "branches/"),
                    "products": self.access_granted(repo.url() + "products/"),
                },
            }
        users = []
        for r in repo.get_user_repos():
            if self.access_granted(r.url()):
                users.append(r.user)
        return {
            "users": users,
            "latest_releases": await self.get_latest_releases(repo),
            "access": {
                "branches": self.access_granted("/branches/"),
                "products": self.access_granted("/products/"),
            },
        }


# --------------------------------------------------------------------------------------
class StaticView(BaseView):

    ROOT = pathlib.Path(__file__).parent.parent.parent
    PUBLIC_URL = os.getenv("DLREPO_PUBLIC_URL")
    CLI = b""
    for root in (ROOT, pathlib.Path("/usr/local/bin"), pathlib.Path("/usr/bin")):
        cli = root / "dlrepo-cli"
        if cli.is_file():
            CLI = cli.read_text(encoding="utf-8")
            if PUBLIC_URL:
                CLI = CLI.replace("http://127.0.0.1:1337", PUBLIC_URL)
            CLI = CLI.encode("utf-8")
            break
    CLI_HEADERS = {
        "Content-Type": "text/plain; charset=utf-8",
        "Content-Length": str(len(CLI)),
    }
    STATIC_DIRS = []
    if os.getenv("DLREPO_STATIC_DIR"):
        STATIC_DIRS.append(pathlib.Path(os.getenv("DLREPO_STATIC_DIR")))
    STATIC_DIRS.append(ROOT / "dlrepo/static")

    @classmethod
    def urls(cls):
        yield "/cli"
        yield "/static/{file}"

    def resolve_filepath(self):
        relpath = self.request.match_info["file"]
        if relpath.startswith("/") or any(x in (".", "..") for x in relpath.split("/")):
            raise web.HTTPNotFound()
        for static_dir in self.STATIC_DIRS:
            path = static_dir / relpath
            if path.is_file():
                return path
        raise web.HTTPNotFound()

    async def get(self):
        if self.request.path == "/cli":
            return web.Response(body=self.CLI, headers=self.CLI_HEADERS)
        # Do not use self.file_response to avoid X-Sendfile.
        # The static roots are dynamic and it makes complex reverse proxy configs.
        # The static files are small anyway.
        return web.FileResponse(self.resolve_filepath())

    async def head(self):
        if self.request.path == "/cli":
            return web.Response(headers=self.CLI_HEADERS)
        return await self.get()


# --------------------------------------------------------------------------------------
async def template_vars(request):
    return {
        "year": datetime.now().strftime("%Y"),
        "request": request,
        **request.match_info,
    }


# --------------------------------------------------------------------------------------
def pretty_time(timestamp: int, fmt: str = "%Y %b %d, %H:%M:%S UTC") -> str:
    if not timestamp:
        return "n/a"
    utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
    return utc_time.strftime(fmt)


# --------------------------------------------------------------------------------------
def add_routes(app):
    template_dirs = []
    if os.getenv("DLREPO_TEMPLATES_DIR"):
        template_dirs.append(os.getenv("DLREPO_TEMPLATES_DIR"))
    base_dir = os.path.dirname(os.path.dirname(__file__))
    template_dirs += [
        os.path.join(base_dir, "templates"),
        # add the parent path of the default templates dir to allow overriding
        # builtin templates in DLREPO_TEMPLATES_DIR
        # Inspired from https://github.com/ipython/ipython/commit/905835ea53d3a
        base_dir,
    ]
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(template_dirs),
        context_processors=[template_vars],
        extensions=["jinja2.ext.do"],
        trim_blocks=True,
        lstrip_blocks=True,
        filters={"pretty_time": pretty_time},
    )
    for route in (
        HomeView,
        StaticView,
        # artifacts
        BranchesView,
        BranchView,
        TagView,
        JobArchiveView,
        JobView,
        FormatArchiveView,
        FormatDigestsView,
        FormatFileView,
        FormatDirView,
        ArtifactView,
        ProductsView,
        ProductView,
        ProductVariantView,
        ProductBranchView,
        VersionArchiveView,
        VersionView,
        # docker
        RootView,
        CatalogView,
        ManifestView,
        TagsListView,
        NewBlobUploadView,
        BlobsUploadsView,
        BlobsView,
        TagsListView,
        ManifestReadOnlyView,
    ):
        for url in route.urls():
            app.add_routes([web.view(url, route)])
