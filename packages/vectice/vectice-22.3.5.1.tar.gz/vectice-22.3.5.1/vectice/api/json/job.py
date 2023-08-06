from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from .project import ProjectOutput
from .._utils import read_nodejs_date


class JobType(Enum):
    """
    Indicates the type of the job.
    """

    EXTRACTION = "EXTRACTION"
    """
    """
    PREPARATION = "PREPARATION"
    """
    """
    TRAINING = "TRAINING"
    """
    """
    INFERENCE = "INFERENCE"
    """
    """
    DEPLOYMENT = "DEPLOYMENT"
    """
    """
    OTHER = "OTHER"
    """
    """


@dataclass
class JobInput:
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[JobType] = None


class JobOutput(dict):
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
    def description(self) -> Optional[str]:
        if "description" in self and self["description"] is not None:
            return str(self["description"])
        else:
            return None

    @property
    def create_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["createdDate"]))

    @property
    def updated_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["updatedDate"]))

    @property
    def deleted_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["deletedDate"]))

    @property
    def project_id(self) -> int:
        return int(self["projectId"])

    @property
    def version(self) -> int:
        return int(self["version"])

    @property
    def type(self) -> JobType:
        return JobType[str(self["type"])]

    @property
    def author_id(self) -> int:
        return int(self["authorId"])

    @property
    def metadata_source(self) -> Optional[str]:
        return str(self["metadataSource"])

    @property
    def project(self) -> ProjectOutput:
        return self._project

    @project.setter
    def project(self, project: ProjectOutput):
        self._project = project
