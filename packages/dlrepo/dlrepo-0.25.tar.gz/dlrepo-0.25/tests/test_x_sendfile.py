# Copyright (c) 2022 Julien Floret
# Copyright (c) 2022 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import hashlib

import aiohttp
import pytest


pytestmark = pytest.mark.asyncio
X_SENDFILE_HEADER = "X-Sendfile-Foobar"


async def test_x_sendfile(dlrepo_server):
    url, data_dir = dlrepo_server
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

        for f in ("file.txt", "file2.txt"):
            resp = await sess.get(f"/branches/main/tag/job/format/{f}")
            assert resp.status == 200
            assert X_SENDFILE_HEADER in resp.headers
            path = data_dir / "branches/main/tag/job/format" / f
            assert resp.headers[X_SENDFILE_HEADER] == str(path)
