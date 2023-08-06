import json
from typing import Dict, Any


def dump_dataclass_to_json(data_class_instance, out_file_path, overwrite_if_exist: bool = True):
    with open(out_file_path, 'w') as json_file:
        json.dump(data_class_instance.__dict__, json_file, indent=4)


def json_path_as_dict(path) -> Dict[Any, Any]:
    with open(path) as f:
        return json.load(f)
