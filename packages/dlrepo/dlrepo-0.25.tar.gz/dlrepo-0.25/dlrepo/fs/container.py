# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple
import weakref

from .util import parse_digest


# --------------------------------------------------------------------------------------
class ContainerRegistry:
    def __init__(self, repo: "AbstractRepository"):
        self.repo = weakref.proxy(repo)

    def repositories(self) -> List[str]:
        repos = set()
        for d in self.repo.path().glob("branches/*/*/*/container"):
            if d.is_dir():
                job = d.parent.name
                branch = d.parent.parent.parent.name
                repos.add(f"{branch}/{job}")
        for d in self.repo.path().glob("products/*/*/*/*/container"):
            if d.is_dir():
                product_branch = d.parent.parent.name
                variant = d.parent.parent.parent.name
                product = d.parent.parent.parent.parent.name
                repos.add(f"{product}/{variant}/{product_branch}")
        return list(repos)

    def product_tags(self, product: str, variant: str, branch: str) -> List[str]:
        tags = set()
        glob = f"products/{product}/{variant}/{branch}/*/container"
        for d in self.repo.path().glob(glob):
            if d.is_dir():
                tags.add(d.parent.name)
        if tags:
            tags.add("latest")
        return sorted(tags)

    def job_tags(self, branch: str, job: str) -> List[str]:
        tags = set()
        glob = f"branches/{branch}/*/{job}/container"
        for d in self.repo.path().glob(glob):
            if d.is_dir():
                tags.add(d.parent.parent.name)
        if tags:
            tags.add("latest")
        return sorted(tags)

    def blob_link_path(self, parent_path: Path, digest: str):
        if not parent_path.is_dir():
            raise FileNotFoundError()
        algo, digest = parse_digest(digest.lower())
        return parent_path / f"container/blobs/{algo}/{digest[:2]}/{digest}"

    def manifest_by_digest(self, digest: str) -> Path:
        path = self.repo.blob_path(digest)
        if not path.is_file():
            raise FileNotFoundError()
        return path

    def manifest_by_parent(self, parent_path: Path) -> Tuple[Path, str]:
        if not parent_path.is_dir():
            raise FileNotFoundError()
        files = list(parent_path.glob("container/manifests/*/*/*"))
        if len(files) != 1:
            raise FileNotFoundError()
        if not files[0].is_file():
            raise FileNotFoundError()
        path = files[0]
        digest = path.name
        algo = path.parent.parent.name
        return (path, f"{algo}:{digest}")

    def _link_blob_to_job(self, digest: str, job: "Job") -> str:
        job_path = self.repo.blob_path(digest, parent=job.path() / "container/blobs")
        self.repo.link_blob(digest, job_path)
        return job_path.stat().st_size

    def new_manifest(self, job: "Job", manifest: Dict) -> str:
        # For an unknown reason, the manifest json file uploaded by "docker push"
        # does not specify a "size" field for every blob.
        # While "docker pull" can perfectly live with that and k8s/dockershim,
        # k8s/containerd on the other hand considers that the blob is of size 0
        # and issues an error like:
        #
        #   failed commit on ref "config-sha256:5b238[...]": commit failed:
        #   unexpected commit digest sha256:e3b0c[...], expected sha256:5b238[...]:
        #   failed precondition
        #
        # Indeed, e3b0c[...] is the sha256 of the empty string.
        #
        # To fix this, we add the missing 'size' fields into the manifest json
        # file right after it is uploaded. The blobs being uploaded before the
        # manifest, we can read their size on the filesystem.

        # link config blob into the job folder
        job.create()
        config = manifest.get("config", {})
        config["size"] = self._link_blob_to_job(config.get("digest"), job)

        # link layers blobs into the job folder
        for l in manifest.get("layers", []):
            l["size"] = self._link_blob_to_job(l.get("digest"), job)

        data = json.dumps(manifest).encode("utf-8")
        digest = "sha256:" + hashlib.sha256(data).hexdigest()

        manifest_path = self.repo.blob_path(digest)
        if not manifest_path.is_file():
            manifest_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            manifest_path.write_bytes(data)

        job_manifest_path = self.repo.blob_path(
            digest, parent=job.path() / "container/manifests"
        )
        if job_manifest_path.is_file():
            job_manifest_path.unlink()
        self.repo.link_blob(digest, job_manifest_path)

        return digest
