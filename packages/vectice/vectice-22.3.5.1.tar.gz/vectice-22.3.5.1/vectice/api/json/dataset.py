from typing import Optional, List

from .artifact_version import ArtifactVersion
from .connection import ConnectionOutput
from .data_resource_schema import DataResourceSchema
from .data_resources_path import DataResourcePath
from .project import ProjectOutput


class DataResource:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        path: Optional[DataResourcePath] = None,
        schema: Optional[DataResourceSchema] = None,
        *args,
        **kwargs
    ):
        self._name = name
        self._description = description
        self._path = path
        self._schema = schema
        self._extra = kwargs

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def path(self) -> Optional[DataResourcePath]:
        return self._path

    @property
    def schema(self) -> Optional[DataResourceSchema]:
        return self._schema


class DatasetInput(dict):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def pattern(self) -> str:
        return str(self["pattern"])

    @property
    def description(self) -> Optional[str]:
        if self.get("description", None):
            return str(self["description"])
        else:
            return None

    @property
    def connection_id(self) -> int:
        return int(self["connectionId"])

    @property
    def connection_name(self) -> str:
        return str(self["connectionName"])

    @property
    def version(self) -> ArtifactVersion:
        return ArtifactVersion(**self["version"])


class DatasetOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "project" in self:
            self._project: ProjectOutput = ProjectOutput(**self["project"])
        else:
            self._project = None
        if "connection" in self:
            self._connection: ConnectionOutput = ConnectionOutput(**self["connection"])
        else:
            self._connection = None
        self._resources: List[DataResource] = []
        if "dataResources" in self:
            for item in self["dataResources"]:
                path = item.pop("path", None)
                self._resources.append(DataResource(**item, path=DataResourcePath(**path)))

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
    def description(self) -> str:
        return str(self["description"])

    @property
    def pattern(self) -> str:
        return str(self["pattern"])

    @property
    def is_pattern_base(self) -> str:
        return str(self["isPatternBase"])

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
    def connection_id(self) -> Optional[int]:
        if self.get("connectionId", None):
            return int(self["connectionId"])
        else:
            return None

    @property
    def created_by_user_id(self) -> int:
        return int(self["createdByUserId"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])

    @property
    def version(self) -> int:
        return int(self["version"])

    @property
    def connection(self) -> Optional[ConnectionOutput]:
        return self._connection

    @property
    def project(self) -> ProjectOutput:
        return self._project

    @project.setter
    def project(self, project: ProjectOutput):
        self._project = project

    @property
    def resources(self) -> List[str]:
        return [item.path.uri for item in self._resources if item.path is not None and item.path.uri is not None]
