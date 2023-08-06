from typing import Optional
from .project import ProjectOutput
from enum import Enum


class BlockType(Enum):
    """
    Indicates the Documentation Page Origin.
    """

    EDITABLE = "EDITABLE"
    """
    """
    VECTICE_RESOURCE = "VECTICE_RESOURCE"
    """
    """
    CLOUD_FILE = "CLOUD_FILE"
    """
    """
    VERSIONED_FILE = "VERSIONED_FILE"
    """
    """
    OTHER = "OTHER"
    """
    """


class BlockVariant(Enum):
    """
    Indicates the Documentation Page Status.
    """

    TEXT = "TEXT"
    """
    """
    MODEL = "MODEL"
    """
    """
    MODEL_VERSION = "MODEL_VERSION"
    """
    """
    DATASET = "DATASET"
    """
    """
    DATASET_VERSION = "DATASET_VERSION"
    """
    """
    RUN = "RUN"
    """
    """
    IMAGE = "IMAGE"
    """
    """
    NOTEBOOK = "NOTEBOOK"
    """
    """
    FILE = "FILE"
    """
    """
    FORMULA = "FORMULA"
    """
    """
    CODE = "CODE"
    """
    """
    DIVIDER = "DIVIDER"
    """
    """


class BlockState(Enum):
    """
    Indicates the Block State.
    """

    COLLAPSE = "COLLAPSE"
    """
    """
    SMALL = "SMALL"
    """
    """
    MEDIUM = "MEDIUM"
    """
    """
    FULL = "FULL"
    """
    """


class BlockInput(dict):
    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def variant(self) -> str:
        return str(self["variant"])

    @property
    def content(self) -> Optional[str]:
        return str(self["content"])

    @property
    def name(self) -> Optional[str]:
        return str(self["name"])

    @property
    def position(self) -> Optional[int]:
        return int(self["position"])

    @property
    def searchable_content(self) -> Optional[str]:
        return str(self["searchableContent"])

    @property
    def state(self) -> Optional[str]:
        return str(self["state"])

    @property
    def resource_id(self) -> Optional[int]:
        return int(self["resourceId"])

    @property
    def entity_file_id(self) -> Optional[int]:
        return int(self["entityFileId"])

    @property
    def file_size(self) -> Optional[int]:
        return int(self["fileSize"])

    @property
    def file_path(self) -> Optional[str]:
        return str(self["filePath"])

    @property
    def url(self) -> Optional[str]:
        return str(self["url"])

    @property
    def config(self) -> Optional[str]:
        return str(self["config"])


class BlockOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "project" in self:
            self._project: ProjectOutput = ProjectOutput(**self["project"])
        else:
            self._project = None

    def items(self):
        result = []
        for key in self:
            if self[key] is not None:
                result.append((key, self[key]))
        return result

    @property
    def id(self) -> int:
        return int(self["id"])

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def variant(self) -> str:
        return str(self["variant"])

    @property
    def content(self) -> Optional[str]:
        return str(self["content"])

    @property
    def name(self) -> Optional[str]:
        return str(self["name"])

    @property
    def position(self) -> Optional[int]:
        return int(self["position"])

    @property
    def searchable_content(self) -> Optional[str]:
        return str(self["searchableContent"])

    @property
    def state(self) -> Optional[str]:
        if self.get("state", None):
            return str(self["state"])
        else:
            return None

    @property
    def resource_id(self) -> Optional[int]:
        if self.get("resourceId", None):
            return int(self["resourceId"])
        else:
            return None

    @property
    def entity_file_id(self) -> Optional[int]:
        if self.get("entityFileId", None):
            return int(self["entityFileId"])
        else:
            return None

    @property
    def file_size(self) -> Optional[int]:
        if self.get("fileSize", None):
            return int(self["fileSize"])
        else:
            return None

    @property
    def file_path(self) -> Optional[str]:
        if self.get("filePath", None):
            return str(self["filePath"])
        else:
            return None

    @property
    def url(self) -> Optional[str]:
        return str(self["url"])

    @property
    def config(self) -> Optional[str]:
        return str(self["config"])
