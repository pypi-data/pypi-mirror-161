from datetime import datetime
from typing import Optional

from .workspace import WorkspaceOutput
from .._utils import read_nodejs_date


class ProjectInput(dict):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str:
        return str(self["description"])


class ProjectOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "workspace" in self:
            self._workspace: WorkspaceOutput = WorkspaceOutput(**self["workspace"])

    def items(self):
        result = []
        for key in self:
            if self[key] is not None:
                result.append((key, self[key]))
        return result

    @property
    def workspace_id(self) -> int:
        return int(self["workspaceId"])

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
    def created_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["createdDate"]))

    @property
    def updated_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["updatedDate"]))

    @property
    def deleted_date(self) -> Optional[datetime]:
        return read_nodejs_date(str(self["deletedDate"]))

    @property
    def version(self) -> int:
        return int(self["version"])

    @property
    def workspace(self) -> WorkspaceOutput:
        return self._workspace
