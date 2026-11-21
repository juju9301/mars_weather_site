import json
from typing import Any


def fixture_json(record: dict[str, Any]) -> str:
    return json.dumps([record], indent=2, ensure_ascii=False) + "\n"
