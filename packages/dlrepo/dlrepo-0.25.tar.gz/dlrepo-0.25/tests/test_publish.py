# Copyright (c) 2022 Julien Floret
# Copyright (c) 2022 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import aiohttp
import pytest


reference = pathlib.Path(__file__).parent / "publish_reference"
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module", params=["1", "10"])
def dlrepo_servers(request, dlrepo_server):
    tmp = pathlib.Path(tempfile.mkdtemp())
    shutil.copytree(reference / "branches", tmp / "branches")
    shutil.copytree(reference / "products", tmp / "products", symlinks=True)
    auth = tmp / "publish.auth"
    auth.write_text("foo:bar")  # use garbage credentials, auth is disabled anyway
    public_url, _ = dlrepo_server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))
        _, portnum = sock.getsockname()

    env = {
        "DLREPO_ROOT_DIR": str(tmp),
        "DLREPO_LISTEN_ADDRESS": "127.0.0.1",
        "DLREPO_LISTEN_PORT": str(portnum),
        "DLREPO_LOG_OUTPUT": "console",
        "DLREPO_LOG_LEVEL": "DEBUG",
        "DLREPO_AUTH_DISABLED": "1",
        "DLREPO_PUBLISH_URL": public_url,
        "DLREPO_PUBLISH_AUTH": auth,
        "DLREPO_PUBLISH_MAX_REQUESTS": request.param,
    }
    with subprocess.Popen([sys.executable, "-m", "dlrepo"], env=env) as proc:
        while proc.poll() is None:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("127.0.0.1", portnum))
                break
            except socket.error:
                time.sleep(0.1)
        assert proc.poll() is None
        try:
            yield f"http://127.0.0.1:{portnum}", public_url
        finally:
            proc.terminate()

    shutil.rmtree(tmp)


async def test_publish(dlrepo_servers):  # pylint: disable=redefined-outer-name
    url, public_url = dlrepo_servers
    async with aiohttp.ClientSession(url) as sess:
        resp = await sess.put("/branches/branch/tag/", json={"tag": {"released": True}})
        assert resp.status == 200
        await asyncio.sleep(1)
        resp = await sess.get("/branches/branch/tag/")
        assert resp.status == 200
        data = await resp.json()
        assert data["tag"]["publish_status"] == f"published to {public_url}"

        async with aiohttp.ClientSession(public_url) as pub_sess:
            for job in "job1", "job2":
                for fmt in "fmt1", "fmt2":
                    sha_url = f"/branches/branch/tag/{job}/{fmt}.sha256"
                    resp = await sess.get(sha_url)
                    assert resp.status == 200
                    data = await resp.text()
                    resp = await pub_sess.get(sha_url)
                    assert resp.status == 200
                    data_pub = await resp.text()
                    assert data_pub == data
            sha_url = "/branches/branch/tag/internal_job/fmt1.sha256"
            resp = await sess.get(sha_url)
            assert resp.status == 200
            resp = await pub_sess.get(sha_url)
            assert resp.status == 404
