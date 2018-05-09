import json
import os
import tempfile

import pytest
import requests_mock


@pytest.yield_fixture
def temp_configfile():
    cf = os.path.join(tempfile.gettempdir(), 'config.json')
    with open(cf, 'w') as f:
        json.dump({}, f)
    yield cf
    os.remove(cf)


@pytest.fixture(autouse=True)
def requestsmock():
    """Return a context where requests are all mocked.
    Usage::

        def test_something(requestsmock):
            requestsmock.get(
                'https://example.com/path'
                content=b'The content'
            )
            # Do stuff that involves requests.get('http://example.com/path')
    """
    with requests_mock.mock() as m:
        yield m
