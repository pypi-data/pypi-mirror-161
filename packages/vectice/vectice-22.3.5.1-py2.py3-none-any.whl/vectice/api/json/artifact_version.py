from enum import Enum
from typing import Optional


class VersionStrategy(Enum):
    """
    Enumeration of supported version strategies.
    """

    AUTOMATIC = "AUTOMATIC"
    """
    """
    MANUAL = "MANUAL"
    """
    """


class ArtifactVersion(dict):
    def __init__(
        self,
        version_number: Optional[int] = None,
        version_name: Optional[str] = None,
        version_id: Optional[int] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        if version_number is not None:
            self["versionNumber"] = version_number
        if version_name is not None:
            self["versionName"] = version_name
        if version_id is not None:
            self["id"] = version_id

    @property
    def version_number(self) -> Optional[int]:
        return self.get("versionNumber", None)

    @property
    def version_id(self) -> Optional[int]:
        return self.get("id", None)

    @property
    def version_name(self) -> Optional[int]:
        return self.get("versionName", None)
