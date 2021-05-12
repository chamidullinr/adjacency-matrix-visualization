import json


def load_json(path):
    with open(path, 'rb') as f:
        return json.loads(f.read())
