from __future__ import annotations

from typing import Optional, Union, List, Dict, BinaryIO, TYPE_CHECKING, Tuple, Any

from .attachment_container import AttachmentContainer
from ..api.json import ArtifactVersion, FileMetadata

if TYPE_CHECKING:
    from vectice.models import Dataset


class DatasetVersion(AttachmentContainer):
    """
    Describes a dataset version
    """

    def __init__(
        self,
        dataset: Dataset,
        id: int,
        name: str,
        version_number: int,
        properties: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        resources: Optional[Union[str, List[str]]] = None,
        attachments: Optional[Union[str, List[str]]] = None,
        auto_version: Optional[bool] = True,
        is_starred: Optional[bool] = False,
        version: Optional[ArtifactVersion] = None,
    ):
        """
        :param dataset: The parent Dataset object.
        :param id: The project identifier.
        :param name: The name of the dataset.
        :param version_number: The version number of the dataset version.
        :param properties: The dataset version properties.
        :param description: A quick description of the dataset.
        :param resources: The dataset version resources.
        :param attachments: The dataset version attachments.
        :param auto_version: Boolean for auto versioning option.
        :param is_starred: Boolean for starring the dataset version.
        :param version: The artifact version object of the dataset version.
        """
        super().__init__(name, id, dataset._client, "DatasetVersion")
        self._dataset = dataset
        self._description = description
        self._isStarred = is_starred
        self._autoVersion = auto_version
        self._properties = properties
        self._version = version  # Relevant for runs // ArtifactVersion
        self._version_number = version_number
        self._resources = resources
        self._parentId = dataset.id
        self._attachments: Optional[
            Union[Tuple[str, Tuple[str, BinaryIO]], List[Tuple[str, Tuple[str, BinaryIO]]]]
        ] = None

        if properties:
            self.properties = properties
        if version:
            if isinstance(version, str):
                self.version = ArtifactVersion(versionNumber=None, versionName=version, id=None)
            elif isinstance(version, int):
                self.version = ArtifactVersion(versionNumber=version, versionName=None, id=None)
        if attachments:
            self.add_attachments(attachments)

    def __repr__(self):
        return f"DatasetVersion(dataset={self.dataset}, id={self.id}, description={self.description}, is_starred={self.is_starred}, auto_version={self.auto_version}, name={self.name}, properties={self.properties}, version={self.version})"

    @property
    def dataset(self) -> Dataset:
        """
        Parent Dataset object.
        :return: Dataset
        """
        return self._dataset

    @property
    def id(self) -> int:
        """
        Dataset version identifier.
        :return: int
        """
        return self._id

    @id.setter
    def id(self, dataset_version_id: int):
        self._id = dataset_version_id

    @property
    def name(self) -> Optional[str]:
        """
        Dataset version name.
        :return: Optional[str]
        """
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def parent_name(self) -> Optional[str]:
        """
        Parent dataset name.
        :return: Optional[str]
        """
        return self._dataset.name

    @property
    def parent_id(self) -> Optional[int]:
        """
        Parent dataset id.
        :return: Optional[int]
        """
        return self._dataset.id

    @parent_id.setter
    def parent_id(self, dataset: int):
        self._parentId = dataset

    @property
    def version_number(self) -> int:
        """
        Version number.
        :return: int
        """
        return self._version_number

    @property
    def description(self) -> Optional[str]:
        """
        Quick description of the dataset version
        :return: Optional[str]
        """
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

    @property
    def properties(self) -> Optional[Dict]:
        """
        Dataset version properties.
        :return: Optional[Dict]
        """
        return self._properties

    @properties.setter
    def properties(self, properties: Dict[str, Any]):
        self._properties = properties

    @property
    def resources(self) -> Optional[Union[str, List[str]]]:
        """
        Dataset version resources.
        :return: Optional[Union[str, List[str]]]
        """
        return self._resources

    @resources.setter
    def resources(self, resources: Union[str, List[str]]):
        self._resources = resources

    @property
    def is_starred(self) -> Optional[bool]:
        """
        Boolean for the dataset version starring.
        :return: Optional[bool]
        """
        return self._isStarred

    @is_starred.setter
    def is_starred(self, is_starred: bool):
        self._isStarred = is_starred

    @property
    def auto_version(self) -> Optional[bool]:
        """
        Boolean for auto versioning option.
        :return: Optional[bool]
        """
        return self._autoVersion

    @auto_version.setter
    def auto_version(self, auto_version: bool):
        self._autoVersion = auto_version

    @property
    def version(self) -> Optional[ArtifactVersion]:
        """
        The artifact version.
        :return: Optional[ArtifactVersion]
        """
        return self._version

    @version.setter
    def version(self, version: ArtifactVersion):
        self._version = version

    @property
    def attachments(self) -> Optional[Union[Tuple[str, Tuple[str, BinaryIO]], List[Tuple[str, Tuple[str, BinaryIO]]]]]:
        """
        The attachments linked to the dataset version.
        """
        return self._attachments

    @attachments.setter
    def attachments(self, attachments: Union[Tuple[str, Tuple[str, BinaryIO]], List[Tuple[str, Tuple[str, BinaryIO]]]]):
        self._attachments = attachments

    def list_files_metadata(self) -> List[FileMetadata]:
        """
        Lists the dataset version files metadata.
        """
        return self._client.list_dataset_version_files_metadata(self.id)
