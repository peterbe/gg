import datetime
import json

from .utils import get_repo_name


def read(configfile):
    with open(configfile, 'r') as f:
        return json.load(f)

def write(configfile, data):
    with open(configfile, 'w') as f:
        json.dump(data, f)


def save(configfile, description, branch_name, bugnumber):
    state = read(configfile)
    repo_name = get_repo_name()
    key = '{}:{}'.format(repo_name, branch_name)
    state[key] = {
        'description': description,
        'bugnumber': bugnumber,
        'date': datetime.datetime.now().isoformat(),
    }
    write(configfile, state)
