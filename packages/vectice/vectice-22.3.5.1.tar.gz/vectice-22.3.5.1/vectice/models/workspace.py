from __future__ import annotations

import logging
from typing import List, Optional, Dict, TYPE_CHECKING, Any

from vectice.api.json import ProjectInput, ConnectionInput, ConnectionType
from .connection import Connection
from .project import Project

if TYPE_CHECKING:
    from vectice import Reference
    from vectice.api import Client
    from vectice.models.integration import AbstractIntegration


class Workspace:
    """
    Workspace is a space where you can found :py:class:`Project` and :py:class:`Connection` for a team.

    In a workspace, you can manage (create, update, delete, get and list ) projects.

    You can also lists and get connections but you can not create or delete them.

    """

    def __init__(self, id: int, name: str, description: Optional[str] = None):
        """
        :param id: the workspace identifier
        :param name: the name of the workspace
        :param description: the description of the workspace
        """
        self._id = id
        self._name = name
        self._description = description
        self._client: Client
        self._logger = logging.getLogger(self.__class__.__name__)

    def __post_init__(self, client: Client, integration_client: Optional[AbstractIntegration]):
        self._client = client
        self._integration_client = integration_client

    def __repr__(self):
        return f"Workspace(name={self.name}, id={self.id}, description={self.description})"

    @property
    def id(self) -> int:
        """
        The workspace identifier.
        :return: int
        """
        return self._id

    @property
    def name(self) -> str:
        """
        The name of the workspace.
        :return: str
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """
        The description of the workspace.
        :return: Optional[str]
        """
        return self._description

    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """
        Creates a new project in the workspace with the given attributes.
        the name is required and must be unique in the workspace.

        By default, the project is public, change `is_public` to `False`
        to make it private.
        the status can be `New`, `InProgress` or `Deployed`

        :param name: The name of the project to be created.
        :param description: The description of the project

        :return: The newly created project
        """
        data = ProjectInput(name=name, description=description)
        output = self._client.create_project(data, self.id)
        self._logger.info(f"Project with id: {output.id} successfully created.")
        return Project(output.id, self, output.name, output.description)

    def update_project(
        self,
        project: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Project:
        """
        Updates a project.

        :param project: The project name or id to update.
        :param name: The name of the project to be.
        :param description: The description of the project

        :return: The updated project
        """
        data = ProjectInput(name=name, description=description)
        item = self._client.get_project(project, self.id)
        output = self._client.update_project(data, item.id, self.id)
        self._logger.info(f"Project with id: {item.id} successfully updated.")
        return Project(output.id, self, output.name, output.description)

    def get_project(self, project: Reference) -> Project:
        """
        Gets a project.

        Gets a project instance with the specified project name or id in the current workspace.

        :param project: The project name or id to get.

        :return: Project
        """
        item = self._client.get_project(project, self.id)
        self._logger.info(f"Project with id: {item.id} successfully retrieved.")
        return Project(item.id, self, item.name, item.description)

    def delete_project(self, project: Reference) -> None:
        """
        Deletes the project specified by the user.

        :param project: The project name or id to delete.

        :return: None
        """
        project_id = self._client.get_project(project, self.id).id
        self._client.delete_project(project_id, self.id)
        self._logger.info(f"Project with id: {project_id} successfully deleted.")

    def list_projects(
        self,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[Project]:
        """
        Lists the projects in this workspace.

        :param search: The name to search
        :param page_index: The page index
        :param page_size: The page size

        :return: a list of projects
        """
        response = self._client.list_projects(self.id, search, page_index, page_size)
        return [Project(item.id, self, item.name, item.description) for item in response.list]

    def list_connections(
        self,
        connection_type: Optional[str] = None,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[Connection]:
        """
        Lists the connections defined in this workspace.

        :param connection_type: The connection type
        :param search: The name to search
        :param page_index: The page index
        :param page_size: The page size

        :return: A list of connections
        """
        response = self._client.list_connections(self.id, connection_type, search, page_index, page_size)
        return [
            Connection(item.id, item.name, self, item.type, item.parameters, item.description) for item in response.list
        ]

    def get_connection(self, connection: Reference) -> Connection:
        """
        Gets a connection.

        Gets a connection instance with the specified connection name or id in the current workspace.


        :param connection: The connection name or id to get.

        :return: Connection
        """
        item = self._client.get_connection(connection, self.id)
        self._logger.info(f"Connection with id: {item.id} successfully retrieved.")
        return Connection(item.id, item.name, self, item.type, item.parameters, item.description)

    def create_connection(
        self, name: str, type: ConnectionType, parameters: Optional[Dict[str, Any]] = None, description: str = ""
    ) -> Connection:
        """
        Creates a connection.

        Create a connection with the specified connection name, description and
        parameters. The parameters keys and values depends on each connection Type.
        Example of required parameters. {"key_value": data, "file_name": "file.json", "connection_info": data}


        :param name: The name of the connection
        :param type: The type of connection
        :param parameters: The parameters for the connection
        :param description: The description of the connection

        :return: Connection
        """
        data = ConnectionInput(
            name=name,
            parameters=parameters,
            type=type,
            description=description,
        )
        output = self._client.create_connection(data, self.id)
        self._logger.info(f"Connection with id: {output.id} successfully created.")
        return Connection(output.id, output.name, self, output.type, output.parameters, output.description)

    def delete_connection(self, connection: Reference) -> None:
        """
        Deletes the connection.
        :param connection: The connection name or id to delete.
        :return: None
        """
        connection_id = self._client.get_connection(connection, self.id).id
        self._client.delete_connection(connection, self.id)
        self._logger.info(f"Connection with id: {connection_id} successfully deleted.")

    def update_connection(
        self,
        connection: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, str]] = None,
    ) -> Connection:
        """
        Updates a connection.
        :param connection: The connection name or id to delete.
        :param name: The new connection name
        :param description: The new connection description
        :param parameters: The new connection parameters
        :return: Connection
        """
        connection_object = self.get_connection(connection)
        connection_input = ConnectionInput(
            name=name if name is not None else connection_object.name,
            type=connection_object.type,
            description=description if description is not None else connection_object.description,
            parameters=parameters,
        )
        connection_update = self._client.update_connection(connection_input, connection, self.id)
        self._logger.info(f"Connection with id: {connection_update.id} successfully updated.")
        return Connection(
            connection_update.id,
            connection_update.name,
            self,
            connection_update.type,
            connection_update.parameters,
            connection_update.description,
        )
