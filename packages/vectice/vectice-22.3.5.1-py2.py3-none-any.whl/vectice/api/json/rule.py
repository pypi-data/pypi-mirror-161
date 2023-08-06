from dataclasses import dataclass
from typing import List, Optional

from .artifact_reference import ArtifactReferenceInput, ArtifactReferenceOutput
from .job import JobInput
from .run import RunInput, RunOutput


class StartRunInput:
    def __init__(self, job: Optional[JobInput], run: RunInput, inputs: Optional[List[ArtifactReferenceInput]] = None):
        self._job = job
        self._jobRun = run
        self._jobRun.job = None
        if inputs is not None:
            self._inputArtifacts = [item for item in inputs if item is not None]
        else:
            self._inputArtifacts = []

    @property
    def job(self) -> Optional[JobInput]:
        return self._job

    @property
    def run(self) -> RunInput:
        return self._jobRun

    @property
    def inputs(self) -> List[ArtifactReferenceInput]:
        return self._inputArtifacts


class StopRunInput:
    def __init__(self, run: RunOutput, outputs: Optional[List[ArtifactReferenceInput]] = None):
        self._jobRun = run
        if outputs is not None:
            self._outputArtifacts = [item for item in outputs if item is not None]
        else:
            self._outputArtifacts = []

    @property
    def jobRun(self) -> RunOutput:
        return self._jobRun

    @property
    def outputArtifacts(self) -> Optional[List[ArtifactReferenceInput]]:
        return self._outputArtifacts


class StopRunOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "jobRun" in self:
            self._jobRun: RunOutput = RunOutput(**self["jobRun"])
        if "jobArtifacts" in self:
            self._outputArtifacts: Optional[List[ArtifactReferenceOutput]] = [
                ArtifactReferenceOutput(**item) for item in self["jobArtifacts"] if item is not None
            ]
        else:
            self._outputArtifacts: Optional[List[ArtifactReferenceOutput]] = None

    @property
    def jobRun(self) -> RunOutput:
        return self._jobRun

    @property
    def outputArtifacts(self) -> Optional[List[ArtifactReferenceOutput]]:
        return self._outputArtifacts


@dataclass()
class FillRunInput:
    jobRunId: int
    inputArtifacts: List[ArtifactReferenceInput]
    outputArtifacts: List[ArtifactReferenceInput]


class FillRunOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
