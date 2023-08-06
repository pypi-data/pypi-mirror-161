# Copyright (c) 2022 Julien Floret
# Copyright (c) 2022 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import hashlib

import aiohttp
import pytest


pytestmark = pytest.mark.asyncio


async def test_ok(dlrepo_server):
    url, _ = dlrepo_server
    async with aiohttp.ClientSession(url) as sess:
        resp = await sess.get("/branches/branch/tag/job/fmt/file.txt")
        assert resp.status == 200
        data = await resp.read()
        assert data == b"foo\n"
        resp = await sess.head("/branches/branch/tag/job/fmt/finalized")
        assert resp.status == 404
        resp = await sess.patch("/branches/branch/tag/job/fmt/")
        assert resp.status == 200
        resp = await sess.get("/branches/branch/tag/job/fmt/file.txt")
        assert resp.status == 200
        data = await resp.read()
        assert data == b"foo\nfinalized\n"
        resp = await sess.get("/branches/branch/tag/job/fmt/finalized")
        assert resp.status == 200


async def test_ignored(dlrepo_server):
    url, _ = dlrepo_server
    async with aiohttp.ClientSession(url) as sess:
        resp = await sess.get("/branches/branch/tag/job/fmt-ignored/foo.txt")
        assert "Digest" not in resp.headers
        assert resp.status == 200
        data = await resp.read()
        assert data == b"foobar\n"
        resp = await sess.patch("/branches/branch/tag/job/fmt-ignored/")
        assert resp.status == 200
        resp = await sess.get("/branches/branch/tag/job/fmt-ignored/foo.txt")
        assert resp.status == 200
        data = await resp.read()
        assert data == b"foobar\n"
        digest = hashlib.sha256(data).hexdigest()
        assert "Digest" in resp.headers
        assert resp.headers["Digest"] == f"sha256:{digest}"


async def test_error(dlrepo_server):
    url, _ = dlrepo_server
    async with aiohttp.ClientSession(url) as sess:
        resp = await sess.get("/branches/branch/tag/job/fmt-error/file3.txt")
        assert resp.status == 200
        data = await resp.read()
        assert data == b"foobar\n"
        resp = await sess.patch("/branches/branch/tag/job/fmt-error/")
        assert resp.status == 500
        resp = await sess.get("/branches/branch/tag/job/fmt-error/file3.txt")
        assert resp.status == 200
        data = await resp.read()
        assert data == b"foobar\n"
