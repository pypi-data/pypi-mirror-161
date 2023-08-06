from dataclasses import dataclass
from typing import Optional, List

from .artifact_type import ArtifactType
from .artifact_version import ArtifactVersion
from .code_version import GitVersionInput
from .files_metadata import FileMetadata
from .metric import MetricInput
from .model import ModelType
from .model_version import ModelVersionStatus
from .property import PropertyInput, PropertyOutput
from .user_declared_version import UserDeclaredVersion


@dataclass
class RulesDatasetVersionInput:
    parentName: Optional[str] = None
    parentId: Optional[int] = None
    autoVersion: Optional[bool] = None
    version: Optional[ArtifactVersion] = None
    userDeclaredVersion: Optional[UserDeclaredVersion] = None
    properties: Optional[List[PropertyInput]] = None
    dataResources: Optional[List[PropertyInput]] = None
    filesMetadata: Optional[List[FileMetadata]] = None
    description: Optional[str] = None


class ArtifactVersionOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "version" in self:
            self._version = ArtifactVersion(self["version"])
        if "properties" in self:
            self._properties = PropertyOutput.from_dict(self["properties"])


@dataclass
class RulesModelVersionInput:
    parentName: Optional[str] = None
    parentId: Optional[int] = None
    algorithmName: Optional[str] = None
    version: Optional[ArtifactVersion] = None
    userDeclaredVersion: Optional[UserDeclaredVersion] = None
    metrics: Optional[List[MetricInput]] = None
    properties: Optional[List[PropertyInput]] = None
    type: Optional[ModelType] = None
    status: Optional[ModelVersionStatus] = None
    description: Optional[str] = None


@dataclass
class RulesCodeVersionInput:
    parentName: Optional[str] = None
    parentId: Optional[int] = None
    version: Optional[ArtifactVersion] = None
    gitVersion: Optional[GitVersionInput] = None
    userDeclaredVersion: Optional[UserDeclaredVersion] = None


@dataclass
class ArtifactReferenceInput:
    artifactType: ArtifactType
    description: Optional[str] = None
    dataset: Optional[RulesDatasetVersionInput] = None
    model: Optional[RulesModelVersionInput] = None
    code: Optional[RulesCodeVersionInput] = None


class ArtifactReferenceOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "dataset" in self:
            self._dataset = RulesDatasetVersionInput(**self["dataset"])
        else:
            self._dataset = None
        if "model" in self:
            self._model = RulesModelVersionInput(**self["model"])
        else:
            self._model = None
        if "code" in self:
            self._code = RulesCodeVersionInput(**self["code"])
        else:
            self._code = None
