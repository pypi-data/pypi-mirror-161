from typing import Optional

from vectice.api import Reference
from vectice.api.json import ArtifactType, VersionStrategy


class ArtifactReference:
    def __init__(
        self,
        code: Optional[Reference] = None,
        dataset: Optional[Reference] = None,
        model: Optional[Reference] = None,
        version_number: Optional[int] = None,
        version_id: Optional[int] = None,
        version_name: Optional[str] = None,
        version_strategy: VersionStrategy = VersionStrategy.MANUAL,
        description: Optional[str] = None,
    ):
        self.dataset = dataset
        self.model = model
        self.code = code
        self.version_number = version_number
        self.version_name = version_name
        self.version_id = version_id
        self.version_strategy = version_strategy
        self.description = description

    def __repr__(self):
        return (
            "ArtifactReference("
            + f"code={self.code}, "
            + f"dataset={self.dataset}, "
            + f"model={self.model}, "
            + f"version_number={self.version_number}, "
            + f"version_id={self.version_id}, "
            + f"version_name={self.version_name}, "
            + f"version_strategy={self.version_strategy}, "
            + f"description={self.description}, "
            + ")"
        )

    def __eq__(self, other):
        return (
            isinstance(other, ArtifactReference)
            and self.code == other.code
            and self.dataset == other.dataset
            and self.model == other.model
            and self.version_number == other.version_number
            and self.version_id == other.version_id
            and self.version_name == other.version_name
            and self.version_strategy == other.version_strategy
            and self.description == other.description
        )

    @property
    def artifact_type(self) -> ArtifactType:
        if self.dataset is not None:
            return ArtifactType.DATASET
        if self.model is not None:
            return ArtifactType.MODEL
        if self.code is not None:
            return ArtifactType.CODE
        raise RuntimeError("empty artifact")
