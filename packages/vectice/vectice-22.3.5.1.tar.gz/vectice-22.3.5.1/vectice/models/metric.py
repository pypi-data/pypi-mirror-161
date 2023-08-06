from datetime import datetime, timezone
from typing import Optional, Union


class Metric:
    def __init__(self, key, value, name=None):
        self._key: str = key
        """"""
        self._value: str = value
        """"""
        self._timestamp: Union[datetime, str] = datetime.now(timezone.utc).isoformat()
        """"""
        self._name: Optional[str] = None
        """"""

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
