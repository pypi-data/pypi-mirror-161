# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

from http import HTTPStatus
import json
import os

from aiohttp import web


# --------------------------------------------------------------------------------------
class AuthenticationRequired(web.HTTPUnauthorized):

    REALM = os.getenv("DLREPO_AUTH_REALM", "dlrepo")
    AUTH_HEADERS = {
        "WWW-Authenticate": f'Basic realm="{REALM}", charset="utf-8"',
    }

    def __init__(self):
        super().__init__(headers=self.AUTH_HEADERS)


# --------------------------------------------------------------------------------------
class ContainerRegistryError(web.HTTPError):
    docker_code = None
    message = None
    headers = None

    def __init__(self, message=None):
        body = json.dumps(
            {
                "errors": [
                    {
                        "code": self.docker_code,
                        "message": message or self.message or self.docker_code,
                    }
                ]
            }
        ).encode("utf-8")
        h = {"Docker-Distribution-Api-Version": "registry/2.0"}
        if self.headers is not None:
            h.update(self.headers)
        super().__init__(body=body, content_type="application/json", headers=h)


class NameUnknown(ContainerRegistryError):
    status_code = HTTPStatus.NOT_FOUND
    docker_code = "NAME_UNKNOWN"
    message = "Repository name not known to registry."


class ManifestUnknown(ContainerRegistryError):
    status_code = HTTPStatus.NOT_FOUND
    docker_code = "MANIFEST_UNKNOWN"
    message = "Unknown manifest in registry."


class ManifestBlobUnknown(ContainerRegistryError):
    status_code = HTTPStatus.NOT_FOUND
    docker_code = "MANIFEST_BLOB_UNKNOWN"
    message = "Unknown blob in registry."


class BlobUploadInvalid(ContainerRegistryError):
    status_code = HTTPStatus.BAD_REQUEST
    docker_code = "BLOB_UPLOAD_INVALID"
    message = "Blob upload invalid."


class BlobUploadUnknown(ContainerRegistryError):
    status_code = HTTPStatus.NOT_FOUND
    docker_code = "BLOB_UPLOAD_UNKNOWN"
    message = "Blob upload unknown to registry."


class BlobUnknown(ContainerRegistryError):
    status_code = HTTPStatus.NOT_FOUND
    docker_code = "BLOB_UNKNOWN"
    message = "Unknown blob in registry."


class Unsupported(ContainerRegistryError):
    status_code = HTTPStatus.BAD_REQUEST
    docker_code = "UNSUPPORTED"
    message = "The operation is unsupported."


class ManifestInvalid(ContainerRegistryError):
    status_code = HTTPStatus.BAD_REQUEST
    docker_code = "MANIFEST_INVALID"
    message = "Invalid manifest."


class Denied(ContainerRegistryError):
    status_code = HTTPStatus.FORBIDDEN
    docker_code = "DENIED"
    message = "Requested access to the resource is denied."


class Unauthorized(ContainerRegistryError):
    status_code = HTTPStatus.UNAUTHORIZED
    docker_code = "UNAUTHORIZED"
    message = "Authentication is required."
    headers = AuthenticationRequired.AUTH_HEADERS
