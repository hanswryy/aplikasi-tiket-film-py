from collections.abc import Mapping

from marshmallow import Schema, pre_load


class BaseSchema(Schema):
    @pre_load
    def trim_strings(self, data: object, **_: object) -> object:
        return _trim_strings(data)


def _trim_strings(value: object) -> object:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Mapping):
        return {key: _trim_strings(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_trim_strings(item) for item in value]
    return value
