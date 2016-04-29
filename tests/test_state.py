import os
import tempfile
import json

import pytest

from gg import state


@pytest.fixture()
def temp_configfile(request):
    cf = os.path.join(tempfile.gettempdir(), 'config.json')
    with open(cf, 'w') as f:
        json.dump({}, f)

    def teardown():
        os.remove(cf)
    request.addfinalizer(teardown)
    return cf


def test_save(temp_configfile):
    state.write(temp_configfile, {})
    state.save(temp_configfile, 'My description', 'branch-name', foo='bar')
    with open(temp_configfile) as f:
        saved = json.load(f)
        key = 'gg:branch-name'
        assert saved[key]['description'] == 'My description'
        assert saved[key]['foo'] == 'bar'
        assert saved[key]['date']


def test_update(temp_configfile):
    state.update(temp_configfile, {'any': 'thing'})
    with open(temp_configfile) as f:
        saved = json.load(f)
        assert saved['any'] == 'thing'


def test_remove(temp_configfile):
    state.update(temp_configfile, {'any': 'thing', 'other': 'stuff'})
    state.remove(temp_configfile, 'any')
    with open(temp_configfile) as f:
        saved = json.load(f)
        assert 'any' not in saved
        assert saved['other'] == 'stuff'
