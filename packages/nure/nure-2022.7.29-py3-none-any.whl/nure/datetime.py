import json
from datetime import datetime, date
from collections.abc import Iterable


class DatetimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def parse(obj):
    if isinstance(obj, str):
        try:
            obj = datetime.fromisoformat(obj)
        except ValueError:
            pass
    elif isinstance(obj, dict):
        obj = {key: parse(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        obj = [parse(item) for item in obj]
    elif isinstance(obj, tuple):
        obj = tuple([parse(item) for item in obj])
    elif isinstance(obj, Iterable):
        obj = map(parse, obj)

    return obj


def to_string(obj):
    if isinstance(obj, datetime) or isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        obj = {key: to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        obj = [to_string(item) for item in obj]
    elif isinstance(obj, tuple):
        obj = tuple([to_string(item) for item in obj])
    elif isinstance(obj, Iterable):
        obj = map(to_string, obj)

    return obj
