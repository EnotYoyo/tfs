# -*- coding: utf-8 -*-
import re
from pathlib import Path
from urllib.parse import urlparse

import httpretty
import pytest

from tfs import TFSAPI

resource_path = Path(__file__).parent.resolve() / 'resources'


def request_callback_get(request, uri, headers):
    # Map path from url to a file
    path = urlparse(uri).path.split("DefaultCollection/")[1]
    response_file = resource_path / path / "response.json"

    if response_file.exists():
        code = 200
        response = response_file.read_text(encoding="utf-8-sig")
    else:
        code = 404
        response = "Cannot find file {}".format(response_file)

    return code, headers, response


@pytest.fixture(autouse=True)
def tfs_server_mock():
    for method in (httpretty.GET, httpretty.POST, httpretty.PUT, httpretty.PATCH):
        httpretty.register_uri(
            method,
            re.compile(r"http://.*/DefaultCollection/.*"),
            body=request_callback_get,
            content_type="application/json",
        )
    yield
    httpretty.reset()


@pytest.fixture()
def tfsapi():
    httpretty.enable()
    yield TFSAPI("http://tfs.tfs.ru/tfs", "DefaultCollection/MyProject", "username", "password")
    httpretty.disable()
