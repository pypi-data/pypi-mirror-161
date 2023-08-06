from __future__ import annotations

from typing import Optional, List, Union, BinaryIO, TYPE_CHECKING, Tuple

from .attachment_container import AttachmentContainer
from .git_version import GitVersion

if TYPE_CHECKING:
    from vectice import Reference
    from vectice.models.project import Project


# @dataclass
# class __CodeData:
#     gitVersion: GitVersion
#     """
#     git information structure extracted automatically by the SDK.
#     """


class CodeVersion(AttachmentContainer):
    """
    Code version class
    """

    def __init__(
        self,
        project: Project,
        id: int,
        name: str,
        version_number: Optional[int] = None,  # for rule API
        code_id: Optional[int] = None,
        description: Optional[str] = None,
        uri: Optional[str] = None,
        is_starred: Optional[bool] = False,
        attachments: Optional[Union[str, List[str]]] = None,
        git_version_id: Optional[int] = None,
        git_version: Optional[GitVersion] = None,
        version: Optional[Reference] = None,
    ):
        super().__init__(name, id, project._client, "CodeVersion")
        self._project = project
        self._description = description
        self._uri = uri
        self._isStarred = is_starred
        self._attachments: Optional[
            Union[Tuple[str, Tuple[str, BinaryIO]], List[Tuple[str, Tuple[str, BinaryIO]]]]
        ] = None
        self._version = version
        self._git_version_id = git_version_id
        self._git_version = git_version
        self._code_id = code_id
        self._version_number = version_number

        if git_version is None:
            pass
        if attachments:
            self.add_attachments(attachments)

    def __repr__(self):
        return f"CodeVersion(id={self.id}, name={self.name}, description={self.description}, uri={self.uri}, gitVersion={self.git_version}, project={self.project})"

    @property
    def project(self) -> Project:
        return self._project

    @property
    def id(self) -> int:
        """
        The code identifier
        :return: int
        """
        if self._id is None:
            raise RuntimeError("can not use id as the code version is not saved")
        return self._id

    @property
    def code_id(self) -> Optional[int]:
        """
        The code identifier
        :return: Optional[int]
        """
        return self._code_id

    @property
    def name(self) -> Optional[str]:
        """
        Name of the code
        :return: Optional[str]
        """
        return self._name

    @property
    def version(self) -> Optional[Reference]:
        """
        The version of the code
        :return: Optional[Reference]
        """
        return self._version

    @property
    def description(self) -> Optional[str]:
        """
        Quick description of the code
        """
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

    @property
    def uri(self) -> Optional[str]:
        """
        The uri to the code
        :return: Optional[str]
        """
        return self._uri

    @uri.setter
    def uri(self, uri: str):
        self._uri = uri

    @property
    def is_starred(self) -> Optional[bool]:
        """
        A boolean to star the code
        :return: Optional[bool]
        """
        return self._isStarred

    @is_starred.setter
    def is_starred(self, is_starred: bool):
        self._isStarred = is_starred

    @property
    def version_number(self) -> Optional[int]:
        """
        The version number the code
        :return: Optional[int]
        """
        return self._version_number

    @property
    def attachments(self) -> Optional[Union[Tuple[str, Tuple[str, BinaryIO]], List[Tuple[str, Tuple[str, BinaryIO]]]]]:
        """
        The attachments linked to the code
        """
        return self._attachments

    @attachments.setter
    def attachments(self, attachments: Union[Tuple[str, Tuple[str, BinaryIO]], List[Tuple[str, Tuple[str, BinaryIO]]]]):
        self._attachments = attachments

    @property
    def git_version_id(self) -> Optional[int]:
        """
        The git version id of the code
        :return: Optional[int]
        """
        return self._git_version_id

    @property
    def git_version(self) -> Optional[GitVersion]:
        """
        The GitVersion of the code
        :return: Optional[GitVersion]
        """
        return self._git_version
