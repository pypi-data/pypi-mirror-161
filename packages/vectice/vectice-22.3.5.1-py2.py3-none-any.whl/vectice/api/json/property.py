from __future__ import annotations

import inspect
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Union, List, Dict


class PropertyInput:
    def __init__(self, key: str, value: Union[str, int, float], timestamp: Optional[Union[datetime, str]] = None):
        self.key: str = key
        """"""
        self.value: Union[str, int, float] = str(value)
        if timestamp is None:
            self.timestamp: str = datetime.now(timezone.utc).isoformat()
        else:
            self.timestamp = timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp)


@dataclass
class PropertyOutput:
    id: int
    dataSetVersionId: int
    key: str
    value: str
    timestamp: datetime
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, properties):
        return cls(**{k: v for k, v in properties.items() if k in inspect.signature(cls).parameters})

    def as_dict(self):
        return asdict(self)


def create_properties_input(properties: Dict[str, Union[int, float, str]]) -> List[PropertyInput]:
    if len(set(properties)) < len(properties):
        raise ValueError("You can not use the same key value pair more than once.")
    props: List[PropertyInput] = []
    for key, value in properties.items():
        _check_empty_property(key, value)
        props.append(PropertyInput(key, str(value)))
    return props


def _check_empty_property(key: str, value: Union[str, int, float]):
    if key.strip() == "" or (isinstance(value, str) and value.strip() == ""):
        raise ValueError("Property keys and values can't be empty.")
