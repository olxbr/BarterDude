import json


def load_fixture(path: str):
    with open(f"tests_unit/fixtures/{path}") as json_file:
        return json.load(json_file)
