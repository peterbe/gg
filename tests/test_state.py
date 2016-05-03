import json

from gg import state


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
