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
    state = read(configfile)
    repo_name = get_repo_name()
    key = '{}:{}'.format(repo_name, branch_name)
    state[key] = extra
    state[key].update({
        'description': description,
        'date': datetime.datetime.now().isoformat(),
    })
    write(configfile, state)
