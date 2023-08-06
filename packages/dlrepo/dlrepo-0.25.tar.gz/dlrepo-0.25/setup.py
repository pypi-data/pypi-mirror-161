#!/usr/bin/env python3
# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib

import setuptools
import setuptools.command.build_py


class BuildPyCommand(setuptools.command.build_py.build_py):
    def build_package_data(self):
        super().build_package_data()
        src = "scss/main.scss"
        if self.distribution.src_root is not None:
            src = os.path.join(self.distribution.src_root, src)
        dest = os.path.join(self.build_lib, "dlrepo/static/dlrepo.css")
        self.spawn(["sassc", "-t", "compact", src, dest])


setuptools.setup(
    name="dlrepo",
    description="Artifact repository",
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text("utf-8"),
    long_description_content_type="text/markdown",
    license="BSD-3-Clause",
    version="0.25",
    author="Robin Jarry",
    author_email="robin@jarry.cc",
    install_requires=[
        "aiohttp>=3.8.0",
        "aiohttp-jinja2",
        "cachetools",
        "bonsai",
    ],
    cmdclass={
        "build_py": BuildPyCommand,
    },
    url="https://sr.ht/~rjarry/dlrepo/",
    packages=setuptools.find_packages("."),
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [console_scripts]
    dlrepo = dlrepo.__main__:main
    """,
    scripts=["dlrepo-cli"],
)
