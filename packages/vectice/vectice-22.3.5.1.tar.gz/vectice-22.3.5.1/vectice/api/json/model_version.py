from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, cast

from .artifact_version import ArtifactVersion
from .model import ModelOutput
from .user_declared_version import UserDeclaredVersion
from .._utils import read_nodejs_date


class ModelVersionStatus(Enum):
    """
    Status of model.
    """

    EXPERIMENTATION = "EXPERIMENTATION"
    """"""
    STAGING = "STAGING"
    """"""
    PRODUCTION = "PRODUCTION"
    """"""


class ModelVersionInput(dict):
    def items(self):
        result = []
        for key in self:
            if self[key] is not None:
                result.append((key, self[key]))
        return result

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str:
        return str(self["description"])

    @property
    def repository(self) -> str:
        return str(self["repository"])

    @property
    def algorithm_name(self) -> str:
        return str(self["algorithmName"])

    @property
    def status(self) -> ModelVersionStatus:
        return ModelVersionStatus[str(self["status"])]

    @property
    def framework(self) -> str:
        return str(self["framework"])

    @property
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def is_starred(self) -> str:
        return str(self["isStarred"])

    @property
    def version(self) -> int:
        return int(self["version"])


class ModelVersionOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "model" in self:
            self._model: ModelOutput = ModelOutput(**self["model"])
        else:
            self._model = None

    def items(self):
        result = []
        for key in self:
            if self[key] is not None:
                result.append((key, self[key]))
        return result

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> Optional[str]:
        if self.get("description", None):
            return str(self["description"])
        else:
            return None

    @property
    def created_date(self) -> Optional[datetime]:
        return read_nodejs_date(self["createdDate"])

    @property
    def updated_date(self) -> Optional[datetime]:
        if "updatedDate" in self:
            return read_nodejs_date(self["updatedDate"])
        else:
            return None

    @property
    def version(self) -> ArtifactVersion:
        return ArtifactVersion(version_number=self.version_number, version_name=self.name, version_id=self.id)

    @property
    def version_number(self) -> int:
        return int(self["versionNumber"])

    @property
    def id(self) -> int:
        return int(self["id"])

    @property
    def author_id(self) -> int:
        return int(self["authorId"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])

    @property
    def deleted_date(self) -> Optional[datetime]:
        if "deletedDate" in self:
            return read_nodejs_date(self["deletedDate"])
        else:
            return None

    @property
    def project(self) -> str:
        return str(self["project"])

    @property
    def algorithm_name(self) -> str:
        return str(self["algorithmName"])

    @property
    def status(self) -> ModelVersionStatus:
        return ModelVersionStatus[str(self["status"])]

    @property
    def resources(self):
        return self.get("resources", None)

    @property
    def framework(self) -> str:
        return str(self["framework"])

    @property
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def is_starred(self) -> bool:
        return bool(self["isStarred"])

    @property
    def model_id(self) -> int:
        return int(self["modelId"])

    @property
    def model(self) -> ModelOutput:
        return self._model

    @property
    def metrics(self) -> Dict[str, Any]:
        if "metrics" in self and self["metrics"] is not None:
            return cast(dict, self["metrics"])
        else:
            return {}

    @property
    def user_declared_version(self) -> Optional[UserDeclaredVersion]:
        if "userDeclaredVersion" in self:
            return UserDeclaredVersion(self.name, self.uri, self.description)
        return None
