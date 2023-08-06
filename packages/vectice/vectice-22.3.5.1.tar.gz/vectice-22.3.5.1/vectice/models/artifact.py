from __future__ import annotations

from typing import Optional, List, Union, TYPE_CHECKING

from vectice.api.json import JobArtifactType, ArtifactType

from .dataset_version import DatasetVersion
from .model_version import ModelVersion
from .code_version import CodeVersion
from vectice.api.reference import MissingReferenceError

if TYPE_CHECKING:
    from vectice.models import Dataset, Model


class Artifact:
    """
    Class for all type of artifact.

    This class links a Run to a Model version/Code version/Dataset version
    and allow to attach data to it (files/data).

    You can create artifact by using the factory class :class:`Artifacts`.
    You can create artifact by using the factory class :class:`Integrations`
    or simply using the :func:`~Run.add_artifact` method of a :class:`Run`.
    """

    def __init__(
        self,
        artifact: Optional[Union[Dataset, DatasetVersion, Model, ModelVersion, CodeVersion]] = None,
        type: Optional[JobArtifactType] = None,
        description: Optional[str] = None,
    ):
        self._artifact = artifact
        self._jobArtifactType = type
        self._description = description

    @property
    def artifactType(self) -> ArtifactType:
        """
        The artifact type: `MODEL`, `DATASET` or `CODEVERSION`.
        :return: Optional[JobArtifactType]
        """
        from vectice.models import Dataset, DatasetVersion, Model, ModelVersion, CodeVersion

        if isinstance(self._artifact, Model) or isinstance(self._artifact, ModelVersion):
            return ArtifactType.MODEL
        elif isinstance(self._artifact, Dataset) or isinstance(self._artifact, DatasetVersion):
            return ArtifactType.DATASET
        elif isinstance(self._artifact, CodeVersion):
            return ArtifactType.CODE
        else:
            raise RuntimeError(f"unexpected artifact type: {type(self._artifact)}")

    @property
    def artifact(self) -> Optional[Union[Dataset, DatasetVersion, Model, ModelVersion, CodeVersion]]:
        """
        The artifact object.
        :return: Optional[Union[Dataset, DatasetVersion, Model, ModelVersion, CodeVersion]]
        """
        return self._artifact

    @property
    def jobArtifactType(self) -> Optional[JobArtifactType]:
        """
        The artifact type for the job : `INPUT` or `OUTPUT`.
        :return: Optional[JobArtifactType]
        """
        return self._jobArtifactType

    @jobArtifactType.setter
    def jobArtifactType(self, value: JobArtifactType):
        self._jobArtifactType = value

    @property
    def description(self) -> Optional[str]:
        """
        The artifact description.
        :return: Optional[str]
        """
        return self._description

    @description.setter
    def description(self, description: Optional[str] = None):
        self._description = description

    def set_version(self, asset_version: Union[Dataset, DatasetVersion, Model, ModelVersion, CodeVersion]):
        """
        set the (Model or Dataset or Code) Version as the main content of the artifact.

        :param asset_version:
        """
        self._artifact = asset_version

    def add_attachments(self, file_path: Union[str, List[str]]) -> None:
        """
        Add some attachment/s to the artifact.

        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation.

        :param file_path: File path/s
        """
        if self.artifact is not None and (
            isinstance(self.artifact, DatasetVersion)
            or isinstance(self.artifact, ModelVersion)
            or isinstance(self.artifact, CodeVersion)
        ):
            self.artifact.add_attachments(file_path)
        else:
            raise MissingReferenceError("artifact")
