import json


def label_formatter(name: str):
    return " ".join(map(str.capitalize, name.split("_")))


def load_json_file(file_path: str = "../config.json"):
    # import config json file
    with open(file_path, "rb") as f:
        config_file = json.load(f)
    return config_file
