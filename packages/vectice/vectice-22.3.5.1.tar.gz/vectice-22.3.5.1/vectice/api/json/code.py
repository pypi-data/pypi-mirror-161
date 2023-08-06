from datetime import datetime
from typing import Optional

from vectice.api._utils import read_nodejs_date
from .project import ProjectOutput


class CodeInput(dict):
    @property
    def code_id(self) -> int:
        return int(self["codeId"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str:
        return str(self["description"])

    @property
    def uri(self) -> str:
        return str(self["uri"])


class CodeOutput(dict):
    _project: ProjectOutput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "project" in self:
            self._project = ProjectOutput(**self["project"])
        else:
            self._project = None

    @property
    def created_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["createdDate"]))

    @property
    def updated_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["updatedDate"]))

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
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def author_id(self) -> int:
        return int(self["authorId"])

    @property
    def deleted_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["deletedDate"]))

    @property
    def version_number(self) -> int:
        return int(self["versionNumber"])

    @property
    def project(self) -> ProjectOutput:
        return self._project

    @project.setter
    def project(self, project: ProjectOutput):
        self._project = project

    @property
    def project_id(self) -> Optional[int]:
        return int(self["projectId"])
