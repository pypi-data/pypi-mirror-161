from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from vectice.api.json.connection_type import ConnectionType

if TYPE_CHECKING:
    from vectice.models import Workspace


class Connection:
    """
    Connection to a repository that contains datasets
    """

    def __init__(
        self,
        id: int,
        name: str,
        workspace: Workspace,
        type: ConnectionType,
        parameters: Dict[str, str],
        description: str = "",
    ):
        """
        :param id: connection identifier
        :param name: name of the connection
        :param workspace: the workspace the connection belong to
        :param type: the type of connection
        :param description: the description of the connection
        """
        self._id = id
        self._name = name
        self._workspace = workspace
        self._type = type
        self._description = description
        self._parameters = parameters

    def __repr__(self):
        return f"Connection(id={self.id}, name={self.name}, type={self.type}, description={self.description}, workspace={self.workspace})"

    @property
    def id(self) -> int:
        """
        Connection identifier.
        :return: int
        """
        return self._id

    @property
    def name(self) -> str:
        """
        Name of the connection.
        """
        return self._name

    @property
    def workspace(self) -> Workspace:
        """
        The workspace this connection belong to.
        :return: Workspace
        """
        return self._workspace

    @property
    def type(self) -> ConnectionType:
        """
        Type of the connection.
        :return: ConnectionType
        """
        return self._type

    @property
    def description(self) -> str:
        """
        Description of the connection.
        :return: str
        """
        return self._description

    @property
    def parameters(self) -> Dict[str, str]:
        """
        Parameters of the connection.
        :return: Dict[str, str]
        """
        return self._parameters.copy()
