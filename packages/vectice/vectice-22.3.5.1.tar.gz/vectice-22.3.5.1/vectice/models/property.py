from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Union, List


def create_properties(properties: Dict[str, Union[int, float, str]]) -> List[Property]:
    if len(set(properties)) < len(properties):
        raise ValueError("You can not use the same key value pair more than once.")
    props: List[Property] = []
    for key, value in properties.items():
        _check_empty_property(key, value)
        props.append(Property(key, value))
    return props


def _check_empty_property(key: Optional[str], value: Union[str, int, float, None]):
    if key is None or key.strip() == "" or value is None or (isinstance(value, str) and value.strip() == ""):
        raise ValueError("Property keys and values can't be empty.")


class Property:
    def __init__(self, key, value, name=None):
        self._key: str = key
        """"""
        self._value: str = value
        """"""
        self._timestamp: Union[datetime, str] = datetime.now(timezone.utc).isoformat()
        """"""
        self._name: Optional[str] = None
        """"""

    def __repr__(self):
        return f"Property(key={self.key}, value={self.value}, timestamp={self.timestamp}, name={self.name})"

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def name(self):
        return self._name
