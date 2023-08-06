from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List

from .artifact_version import ArtifactVersion
from .artifact import ArtifactInput
from .artifact_reference import (
    ArtifactReferenceInput,
    RulesModelVersionInput,
    RulesDatasetVersionInput,
    RulesCodeVersionInput,
)
from .job import JobInput, JobOutput
from .._utils import read_nodejs_date


class RunStatus(Enum):

    """
    Status of a Run.
    """

    SCHEDULED = "SCHEDULED"
    """"""
    STARTED = "STARTED"
    """"""
    COMPLETED = "COMPLETED"
    """"""
    FAILED = "FAILED"
    """"""
    ABORTED = "ABORTED"
    """"""


@dataclass
class RunInput:
    name: Optional[str]
    job: Optional[JobInput] = None
    systemName: Optional[str] = ""
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    status: RunStatus = RunStatus.SCHEDULED
    inputs: Optional[List[ArtifactInput]] = None
    properties: Optional[dict] = None
    description: Optional[str] = None


class RunOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "job" in self:
            self._job: JobOutput = JobOutput(**self["job"])
        if "jobArtifacts" in self:
            self._inputs = [
                ArtifactReferenceInput(
                    item["artifactType"],
                    item.get("description", None),
                    dataset=RulesDatasetVersionInput(
                        parentId=item["dataSetVersion"]["dataSetId"],
                        version=ArtifactVersion(
                            version_number=item["dataSetVersion"]["versionNumber"],
                            version_id=item["dataSetVersion"]["id"],
                            version_name=item["dataSetVersion"]["name"],
                        ),
                    )
                    if item["artifactType"] == "DATASET"
                    else None,
                    model=RulesModelVersionInput(
                        parentId=item["modelVersion"]["modelId"],
                        version=ArtifactVersion(
                            version_number=item["modelVersion"]["versionNumber"],
                            version_id=item["modelVersion"]["id"],
                            version_name=item["modelVersion"]["name"],
                        ),
                    )
                    if item["artifactType"] == "MODEL"
                    else None,
                    code=RulesCodeVersionInput(
                        parentId=item["codeVersion"]["codeId"],
                        version=ArtifactVersion(
                            version_number=item["codeVersion"]["versionNumber"],
                            version_id=item["codeVersion"]["id"],
                            version_name=item["codeVersion"]["name"],
                        ),
                    )
                    if item["artifactType"] == "CODE"
                    else None,
                )
                for item in self["jobArtifacts"]
                if item["jobArtifactType"] == "INPUT"
            ]

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
    def status(self) -> RunStatus:
        return RunStatus[self["status"]]

    @property
    def job_id(self) -> int:
        return int(self["jobId"])

    @property
    def start_date(self) -> Optional[datetime]:
        if "startDate" in self and self["startDate"] is not None:
            return read_nodejs_date(str(self["startDate"]))
        else:
            return None

    @property
    def end_date(self) -> Optional[datetime]:
        if "endDate" in self and self["endDate"] is not None:
            return read_nodejs_date(str(self["endDate"]))
        else:
            return None

    @property
    def created_date(self) -> Optional[datetime]:
        if "createdDate" in self and self["createdDate"] is not None:
            return read_nodejs_date(str(self["createdDate"]))
        else:
            return None

    @property
    def duration(self) -> int:
        return int(self["duration"])

    @property
    def system_name(self) -> str:
        return str(self["systemName"])

    @property
    def metadata_source(self) -> str:
        return str(self["metadataSource"])

    @property
    def properties(self) -> Optional[List[str]]:
        if "properties" in self and self["properties"] is not None:
            return list(self["properties"])
        else:
            return None

    @property
    def description(self) -> Optional[str]:
        if "description" in self and self["description"] is not None:
            return str(self["description"])
        else:
            return None

    @property
    def job(self) -> JobOutput:
        return self._job
