# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import asyncio

from aiohttp import web
import aiohttp_jinja2

from .util import BaseView


# --------------------------------------------------------------------------------------
class BranchesView(BaseView):
    @classmethod
    def urls(cls):
        yield "/branches"
        yield "/branches/"
        yield "/~{user}/branches"
        yield "/~{user}/branches/"

    async def get(self):
        """
        Get the list of branches.
        """
        if not self.request.path.endswith("/"):
            raise web.HTTPFound(self.request.path + "/")
        data = {"branches": []}
        for b in self.repo().get_branches():
            if not self.access_granted(b.url()):
                continue
            br = {
                "name": b.name,
                "daily_tags": 0,
                "released_tags": 0,
            }
            for t in b.get_tags():
                if t.is_released():
                    br["released_tags"] += 1
                else:
                    br["daily_tags"] += 1
            br.update(b.get_cleanup_policy())
            data["branches"].append(br)
        if "html" in self.request.headers.get("Accept", "json"):
            return aiohttp_jinja2.render_template("branches.html", self.request, data)
        return web.json_response(data)


# --------------------------------------------------------------------------------------
class BranchView(BaseView):
    @classmethod
    def urls(cls):
        yield "/branches/{branch}"
        yield "/branches/{branch}/"
        yield "/~{user}/branches/{branch}"
        yield "/~{user}/branches/{branch}/"

    def _get_branch(self):
        branch = self.repo().get_branch(self.request.match_info["branch"])
        if not branch.exists():
            raise web.HTTPNotFound()
        if not self.request.path.endswith("/"):
            raise web.HTTPFound(self.request.path + "/")
        return branch

    async def get(self):
        """
        Get the list of tags for a branch.
        """
        branch = self._get_branch()
        released_only = bool(self.request.query.get("released"))
        data = {
            "branch": {
                "name": self.request.match_info["branch"],
                "cleanup_policy": branch.get_cleanup_policy(),
                "tags": [],
            },
        }
        for t in branch.get_tags():
            if not self.access_granted(t.url()):
                continue
            if released_only and not t.is_released():
                continue
            data["branch"]["tags"].append(
                {
                    "name": t.name,
                    "timestamp": t.timestamp,
                    "released": t.is_released(),
                    "locked": t.is_locked(),
                    "publish_status": t.publish_status(),
                }
            )
        if "html" in self.request.headers.get("Accept", "json"):
            return aiohttp_jinja2.render_template("branch.html", self.request, data)
        return web.json_response(data)

    async def put(self):
        """
        Update the cleanup policy for a branch.
        """
        branch = self._get_branch()
        prev = branch.get_cleanup_policy()
        try:
            policy = (await self.json_body())["branch"]
            max_daily = policy.get("max_daily_tags", prev["max_daily_tags"])
            max_released = policy.get("max_released_tags", prev["max_released_tags"])
            if not (isinstance(max_daily, int) and isinstance(max_released, int)):
                raise TypeError()
            if max_daily < 0 or max_released < 0:
                raise TypeError()
        except (TypeError, KeyError) as e:
            raise web.HTTPBadRequest(reason="invalid parameters") from e
        branch.set_cleanup_policy(max_daily, max_released)
        return web.Response()

    async def delete(self):
        """
        Delete a branch and all its contents.
        """
        loop = asyncio.get_running_loop()
        branch = self._get_branch()
        try:
            force = "force" in self.request.query
            await loop.run_in_executor(None, lambda: branch.delete(force=force))
            self.repo().schedule_cleanup_orphans()
            return web.Response()
        except OSError as e:
            raise web.HTTPBadRequest(reason=str(e)) from e
