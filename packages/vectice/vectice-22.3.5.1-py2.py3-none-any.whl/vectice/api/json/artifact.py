from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .artifact_reference import RulesDatasetVersionInput, RulesModelVersionInput, RulesCodeVersionInput
from .artifact_type import ArtifactType, JobArtifactType
from .dataset_version import DatasetVersionInput
from .model_version import ModelVersionInput


@dataclass
class ArtifactInput:
    artifactType: ArtifactType
    jobArtifactType: JobArtifactType
    dataset: Optional[RulesDatasetVersionInput] = None
    dataSetVersion: Optional[DatasetVersionInput] = None
    dataSetVersionId: Optional[int] = None
    model: Optional[RulesModelVersionInput] = None
    modelVersion: Optional[ModelVersionInput] = None
    modelVersionId: Optional[int] = None
    codeVersionId: Optional[int] = None
    description: Optional[str] = None
    metadataSource: Optional[str] = None
    authorId: Optional[int] = None
    jobRunId: Optional[int] = None
    deletedDate: Optional[datetime] = None
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None
    version: Optional[str] = None
    id: Optional[int] = None
    code: Optional[RulesCodeVersionInput] = None


class ArtifactOutput(dict):
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
    def artifact_id(self) -> int:
        if self.artifact_type == ArtifactType.DATASET:
            return int(self["dataSetVersionId"])
        elif self.artifact_type == ArtifactType.MODEL:
            return int(self["modelVersionId"])
        else:
            return int(self["codeVersionId"])

    @property
    def job_artifact_type(self) -> JobArtifactType:
        return JobArtifactType[self["jobArtifactType"]]

    @property
    def artifact_type(self) -> ArtifactType:
        return ArtifactType[self["artifactType"]]
