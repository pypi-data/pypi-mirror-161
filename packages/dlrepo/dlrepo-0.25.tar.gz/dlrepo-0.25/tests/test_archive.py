# Copyright (c) 2022 Julien Floret
# Copyright (c) 2022 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import hashlib
import io
import tarfile

import aiohttp
import pytest


pytestmark = pytest.mark.asyncio


async def test_archive(dlrepo_server):
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

        resp = await sess.get("/branches/main/tag/job/format.tar")
        assert resp.status == 200
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/x-tar"
        tar = await resp.read()
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            assert t.getnames() == [
                "job-tag-format/file.txt",
                "job-tag-format/file2.txt",
                "job-tag-format/SHA256SUMS.txt",
            ]
            with t.extractfile("job-tag-format/file.txt") as f:
                assert f.read() == data
            with t.extractfile("job-tag-format/file2.txt") as f:
                assert f.read() == data2
            with t.extractfile("job-tag-format/SHA256SUMS.txt") as f:
                txt = f.read().decode("utf-8")
                assert txt == f"{digest}  file.txt\n{digest2}  file2.txt\n"
