# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import hashlib

import aiohttp
import pytest


pytestmark = pytest.mark.asyncio


async def test_noauth(dlrepo_server):
    url, _ = dlrepo_server
    async with aiohttp.ClientSession(url) as sess:
        for u in ("/", "/not-found", "/cli"):
            resp = await sess.get(u)
            assert resp.status == 401
        resp = await sess.get("/static/logo.svg")
        assert resp.status == 200


async def test_invalid_auth(dlrepo_server):
    url, _ = dlrepo_server
    auth = aiohttp.BasicAuth("foo", "invalidpassword")
    async with aiohttp.ClientSession(url, auth=auth) as sess:
        for u in ("/", "/not-found", "/cli"):
            resp = await sess.get(u)
            assert resp.status == 401
        resp = await sess.get("/static/logo.svg")
        assert resp.status == 200


async def test_valid_auth(dlrepo_server):
    url, _ = dlrepo_server
    auth = aiohttp.BasicAuth("foo", "baz")
    async with aiohttp.ClientSession(url) as sess:
        resp = await sess.get("/", auth=auth)
        assert resp.status == 200
        resp = await sess.get("/not-found", auth=auth)
        assert resp.status == 404
        resp = await sess.get("/cli", auth=auth)
        assert resp.status == 200
        text = await resp.text()
        with open("dlrepo-cli", "r", encoding="utf-8") as f:
            assert text == f.read()
        resp = await sess.get("/static/logo.svg", auth=auth)
        assert resp.status == 200


async def test_write_denied(dlrepo_server):
    url, _ = dlrepo_server
    auth = aiohttp.BasicAuth("foo", "baz")
    async with aiohttp.ClientSession(url, auth=auth) as sess:
        resp = await sess.put("/branches/main/tag/job/format/file.txt")
        assert resp.status == 401


async def test_write_allowed(dlrepo_server):
    url, _ = dlrepo_server
    auth = aiohttp.BasicAuth("bar", "bar")
    async with aiohttp.ClientSession(url, auth=auth) as sess:
        data = b"content"
        digest = hashlib.sha256(data).hexdigest()
        resp = await sess.put(
            "/branches/main/tag/job/format/file.txt",
            data=data,
            headers={"Digest": f"sha256:{digest}"},
        )
        assert resp.status == 201
        resp = await sess.put(
            "/branches/main/tag/job/format/file2.txt",
            data=data + b"corrupt",
            headers={"Digest": f"sha256:{digest}"},
        )
        assert resp.status == 422


async def test_read_allowed(dlrepo_server):
    url, _ = dlrepo_server
    auth = aiohttp.BasicAuth("foo", "baz")
    async with aiohttp.ClientSession(url, auth=auth) as sess:
        resp = await sess.get("/branches/main/tag/job/format/file.txt")
        assert resp.status == 200
        data = await resp.read()
        assert data == b"content"


async def test_read_denied(dlrepo_server):
    url, _ = dlrepo_server
    async with aiohttp.ClientSession(url) as sess:
        resp = await sess.get("/branches/main/tag/job/format/file.txt")
        assert resp.status == 401
    auth = aiohttp.BasicAuth("coin", "coin")
    async with aiohttp.ClientSession(url, auth=auth) as sess:
        resp = await sess.get("/branches/main/tag/job/format/file.txt")
        assert resp.status == 401


async def test_acl_regexp(dlrepo_server):
    url, _ = dlrepo_server
    auth = aiohttp.BasicAuth("coin", "coin")
    async with aiohttp.ClientSession(url, auth=auth) as sess:
        data = b"content"
        digest = hashlib.sha256(data).hexdigest()
        resp = await sess.put(
            "/branches/main/tag2/job/format/file2.txt",
            data=data,
            headers={"Digest": f"sha256:{digest}"},
        )
        assert resp.status == 201
        resp = await sess.get("/branches/main/tag2/job/format/file2.txt")
        assert resp.status == 200
        data = await resp.read()
        assert data == b"content"
