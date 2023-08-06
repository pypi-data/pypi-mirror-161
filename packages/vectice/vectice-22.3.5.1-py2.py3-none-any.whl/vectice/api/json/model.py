from datetime import datetime
from enum import Enum
from typing import Optional

from .project import ProjectOutput
from .._utils import read_nodejs_date


class ModelType(Enum):
    """
    Indicates the Model Type.
    """

    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    """
    """
    CLASSIFICATION = "CLASSIFICATION"
    """
    """
    CLUSTERING = "CLUSTERING"
    """
    """
    OTHER = "OTHER"
    """
    """
    RECOMMENDATION_MODELS = "RECOMMENDATION_MODELS"
    """
    """
    REGRESSION = "REGRESSION"
    """
    """
    TIME_SERIES = "TIME_SERIES"
    """
    """


class ModelInput(dict):
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
    def type(self) -> ModelType:
        return ModelType(self["type"])

    @property
    def description(self) -> str:
        return str(self["description"])

    @property
    def repository(self) -> str:
        return str(self["repository"])


class ModelOutput(dict):
    _project: ProjectOutput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "project" in self:
            self._project = ProjectOutput(**self["project"])
        else:
            self._project = None

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
    def type(self) -> str:
        return str(self["type"])

    @property
    def description(self) -> Optional[str]:
        if "description" in self and self["description"] is not None:
            return str(self["description"])
        else:
            return None

    @property
    def created_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["createdDate"]))

    @property
    def updated_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["updatedDate"]))

    @property
    def version(self) -> int:
        return int(self["version"])

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
    def repository(self) -> str:
        return str(self["repository"])

    @property
    def deleted_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["deletedDate"]))

    @property
    def project(self) -> ProjectOutput:
        return self._project

    @project.setter
    def project(self, project: ProjectOutput):
        self._project = project
