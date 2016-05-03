import json
import os
import tempfile

import pytest


@pytest.yield_fixture
def temp_configfile():
    cf = os.path.join(tempfile.gettempdir(), 'config.json')
    with open(cf, 'w') as f:
        json.dump({}, f)
    yield cf
    os.remove(cf)
