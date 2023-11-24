# Standard Library
import json
from collections import OrderedDict
from datetime import datetime

# Third Party
import dateutil.parser
from pydantic import AnyUrl, BaseModel


def load_paper_json(file_path):
    with open(file_path, "r") as file:
        # Load data preserving the order of keys
        data = json.load(file, object_pairs_hook=OrderedDict)

    # Convert datetime strings back to datetime objects
    for key in ["published", "updated"]:
        if data.get(key):
            data[key] = dateutil.parser.isoparse(data[key])

    return data


def custom_serialize(model: BaseModel,
                     json_dump: bool = False,
                     ignore_none: bool = False):
    if json_dump:
        serialized_data = model.model_dump_json(by_alias=True)
    else:
        serialized_data = model.model_dump(by_alias=True)

    # Manually handle specific types
    for key, value in serialized_data.items():
        if ignore_none and value is None:
            #logger.info(f"Skipping serialization of {key} as it is None")
            continue
        if isinstance(value, datetime):
            serialized_data[key] = value.isoformat().replace("+00:00", "Z")
        elif isinstance(value, AnyUrl):
            serialized_data[key] = str(value)
        # Add more conditions for other special types if needed

    return serialized_data
