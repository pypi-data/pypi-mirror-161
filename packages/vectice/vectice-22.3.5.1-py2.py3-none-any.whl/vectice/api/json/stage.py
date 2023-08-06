from typing import Optional
from .project import ProjectOutput
from enum import Enum


class StageOrigin(Enum):
    """
    Indicates the Documentation Page Origin.
    """

    VecticeFile = "VecticeFile"
    """
    """
    ExternalLink = "ExternalLink"
    """
    """


class StageStatus(Enum):
    """
    Indicates the Documentation Page Status.
    """

    NotStarted = "NotStarted"
    """
    """
    InProgress = "Draft"
    """
    """
    Completed = "Completed"
    """
    """


class DocumentationPageType(Enum):
    """
    Indicates the Documentation Page Type.
    """

    Project = "Project"
    """
    """
    Dataset = "Dataset"
    """
    """
    Model = "Model"
    """
    """


class StageInput(dict):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def status(self) -> Optional[str]:
        return str(self["status"])

    @property
    def uri(self) -> str:
        return str(self["uri"])


class StageOutput(dict):
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
    def name(self) -> str:
        return str(self["name"])

    @property
    def status(self) -> str:
        return str(self["status"])

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def origin(self) -> str:
        return str(self["origin"])

    @property
    def index(self) -> int:
        return int(self["index"])

    @property
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def create_date(self) -> str:
        return str(self["createdDate"])

    @property
    def updated_date(self) -> str:
        return str(self["updatedDate"])

    @property
    def deleted_date(self) -> str:
        return str(self["deletedDate"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])

    @property
    def project(self) -> ProjectOutput:
        return self._project

    @project.setter
    def project(self, project: ProjectOutput):
        self._project = project
