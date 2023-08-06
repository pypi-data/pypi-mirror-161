from __future__ import annotations

import inspect
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Union, Any


class MetricInput:
    def __init__(self, key: str, value: Union[float, int], timestamp: Optional[Union[datetime, str]] = None):
        self.key: str = key
        """"""
        self.value: Union[float, int] = value
        """"""
        if timestamp is None:
            self.timestamp: str = datetime.now(timezone.utc).isoformat()
        else:
            self.timestamp = timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp


@dataclass
class MetricOutput:
    key: str
    value: float
    timestamp: datetime
    name: Optional[str] = None
    id: Optional[int] = None

    @classmethod
    def from_dict(cls, metrics):
        return cls(**{k: v for k, v in metrics.items() if k in inspect.signature(cls).parameters})

    def as_dict(self):
        return asdict(self)


def create_metrics_input(metrics: Dict[str, float]) -> List[MetricInput]:
    if len(set(metrics)) < len(metrics):
        raise ValueError("You can not use the same key value pair more than once.")
    props: List[MetricInput] = []
    for key, value in metrics.items():
        _check_empty_property(key, value)
        props.append(MetricInput(key, value))
    return props


def _check_empty_property(key: str, value: Any):
    if key.strip() == "":
        raise ValueError("Property keys and values can't be empty.")
