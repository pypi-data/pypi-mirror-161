# Copyright (c) 2022 Julien Floret
# Copyright (c) 2022 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import hashlib

import aiohttp
import pytest


pytestmark = pytest.mark.asyncio


async def test_digests(dlrepo_server):
    url, _ = dlrepo_server
    async with aiohttp.ClientSession(url) as sess:
        data2 = b"content2"
        digest2 = hashlib.sha256(data2).hexdigest()
        resp = await sess.put(
            "/branches/main/tag/job/format/file2.txt",
            data=data2,
            headers={"Digest": f"sha256:{digest2}"},
        )
        assert resp.status == 201

        data = b"content"
        digest = hashlib.sha256(data).hexdigest()
        resp = await sess.put(
            "/branches/main/tag/job/format/file.txt",
            data=data,
            headers={"Digest": f"sha256:{digest}"},
        )
        assert resp.status == 201

        resp = await sess.get("/branches/main/tag/job/format/file.txt.sha256")
        assert resp.status == 200
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"
        buf = await resp.read()
        assert buf.decode("utf-8") == f"{digest}  file.txt\n"

        resp = await sess.get("/branches/main/tag/job/format/file2.txt.sha256")
        assert resp.status == 200
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"
        buf = await resp.read()
        assert buf.decode("utf-8") == f"{digest2}  file2.txt\n"

        resp = await sess.get("/branches/main/tag/job/format.sha256")
        assert resp.status == 200
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"
        buf = await resp.read()
        assert buf.decode("utf-8") == f"{digest}  file.txt\n{digest2}  file2.txt\n"
