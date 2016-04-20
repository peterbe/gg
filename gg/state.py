import json


def read(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

def write(config_file, data):
    with open(config_file, 'w') as f:
        json.dump(data, f)


def save(config_file, description, branchname, bugnumber):
    state = read(config_file)
    state[key] = {
        'description': description,
        'bugnumber': bugnumber,
        'date': datetime.datetime.now().isoformat(),
    }
    write(config_file, state)
