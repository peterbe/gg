import os
import tempfile
import json

from gg import state


def test_save():
    fp = os.path.join(tempfile.gettempdir(), 'config.json')
    state.write(fp, {})
    try:
        state.save(fp, 'My description', 'branch-name', foo='bar')
        with open(fp) as f:
            saved = json.load(f)
            key = 'gg:branch-name'
            assert saved[key]['description'] == 'My description'
            assert saved[key]['foo'] == 'bar'
            assert saved[key]['date']
    finally:
        os.remove(fp)
