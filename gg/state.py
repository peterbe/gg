import datetime
import json

from .utils import get_repo_name


def read(configfile):
    with open(configfile, 'r') as f:
        return json.load(f)


def write(configfile, data):
    with open(configfile, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)


def save(configfile, description, branch_name, **extra):
    # state = read(configfile)
    repo_name = get_repo_name()
    key = '{}:{}'.format(repo_name, branch_name)
    new = {key: extra}
    new[key].update({
        'description': description,
        'date': datetime.datetime.now().isoformat(),
    })
    update(configfile, new)


def update(configfile, data):
    state = read(configfile)
    state.update(data)
    write(configfile, state)


def remove(configfile, key):
    state = read(configfile)
    del state[key]
    write(configfile, state)
