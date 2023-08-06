from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from vectice.api import Client

if TYPE_CHECKING:
    from vectice.models import Project


class Code:
    """
    Describe a code


    """

    def __init__(
        self,
        name: str,
        id: int,
        project: Project,
        description: Optional[str] = None,
        uri: Optional[str] = None,
        git_version: Optional[int] = None,
    ):
        """
        :param id: the project identifier
        :param project: the project the code belong to
        :param name: the name of the code
        :param description: a quick  description of the code
        :param uri:
        """
        self._id = id
        self._name = name
        self._project: Project = project
        self._description = description
        self._uri = uri
        self._git_version = git_version
        self._client: Client = project._client

    @property
    def id(self) -> Optional[int]:
        """
        The code identifier
        :return:
        """
        return self._id

    @id.setter
    def id(self, code_id: int):
        self._id = code_id

    @property
    def project(self) -> Optional[Project]:
        """
        The project this code belong to
        """
        return self._project

    @property
    def name(self) -> str:
        """
        Name of the code
        """
        return self._name

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
        return self._uri

    @uri.setter
    def uri(self, uri: str):
        self._uri = uri

    @property
    def git_version(self) -> Optional[int]:
        return self._git_version

    @git_version.setter
    def git_version(self, git_version: int):
        self._git_version = git_version
