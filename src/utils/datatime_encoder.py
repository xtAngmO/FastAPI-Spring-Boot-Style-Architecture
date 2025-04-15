import json
from datetime import datetime
from typing import Self


class DateTimeEncoder(json.JSONEncoder):
    def default(self: Self, obj: object) -> str | list | dict | int | float | bool | None:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
