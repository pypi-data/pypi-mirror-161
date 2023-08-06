# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import pytest


@pytest.fixture(scope="module")
def temp_dir():
    tmp = pathlib.Path(tempfile.mkdtemp())
    yield tmp
    shutil.rmtree(tmp)


@pytest.fixture(scope="module")
def dlrepo_server(request, temp_dir):  # pylint: disable=redefined-outer-name
    data_dir = pathlib.Path(request.fspath).parent / request.module.__name__
    for d in ("branches", "products", "users"):
        folder = data_dir / d
        if folder.is_dir():
            shutil.copytree(folder, temp_dir / d)
    portnum = get_free_tcp_port()
    env = {
        "DLREPO_ROOT_DIR": str(temp_dir),
        "DLREPO_LISTEN_ADDRESS": "127.0.0.1",
        "DLREPO_LISTEN_PORT": str(portnum),
        "DLREPO_TEMPLATES_DIR": str(data_dir / "templates"),
        "DLREPO_STATIC_DIR": str(data_dir / "static"),
        "DLREPO_LOG_OUTPUT": "console",
        "DLREPO_LOG_LEVEL": "DEBUG",
    }
    acls = data_dir / "acls"
    if acls.is_dir():
        env["DLREPO_ACLS_DIR"] = str(acls)
    auth = data_dir / "auth"
    if auth.is_file():
        env["DLREPO_AUTH_FILE"] = str(auth)
    else:
        headers = data_dir / "headers"
        if headers.is_dir():
            for h in headers.iterdir():
                env[h.name] = h.read_text("utf-8").strip()
        else:
            env["DLREPO_AUTH_DISABLED"] = "1"
    settings = data_dir / "settings"
    if settings.is_dir():
        for s in settings.iterdir():
            env[s.name] = s.read_text("utf-8").strip()
    post_process = data_dir / "post-process.sh"
    if post_process.is_file():
        env["DLREPO_POST_PROCESS_CMD"] = str(post_process)
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
            yield f"http://127.0.0.1:{portnum}", temp_dir
        finally:
            proc.terminate()


def get_free_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))
        _, portnum = sock.getsockname()
        return portnum
