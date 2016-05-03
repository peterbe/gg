import json
import os
import tempfile

import pytest


@pytest.fixture()
def temp_configfile(request):
    cf = os.path.join(tempfile.gettempdir(), 'config.json')
    with open(cf, 'w') as f:
        json.dump({}, f)

    def teardown():
        os.remove(cf)
    request.addfinalizer(teardown)
    return cf


class Response:
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code

    def json(self):
        return self.content
