from dataclasses import dataclass
from datetime import datetime

from typing import Optional

from vectice.api._utils import read_nodejs_date


@dataclass
class WorkspaceInput:
    name: Optional[str]
    description: Optional[str]


class WorkspaceOutput(dict):
    def items(self):
        result = []
        for key in self:
            if self[key] is not None:
                result.append((key, self[key]))
        return result

    @property
    def organization_id(self) -> int:
        return int(self["organizationId"])

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
