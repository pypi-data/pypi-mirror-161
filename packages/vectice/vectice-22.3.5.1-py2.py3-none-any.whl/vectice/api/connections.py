from __future__ import annotations

import urllib
from typing import Optional, TYPE_CHECKING, Dict, Any
from urllib.parse import urlencode

from vectice.api._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import ConnectionOutput, Page, PagedResponse, ConnectionInput
from .reference import InvalidReferenceError
from .workspace import WorkspaceApi

if TYPE_CHECKING:
    from vectice import Reference


class ConnectionApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorHandler = HttpErrorHandler()

    def _create_base_url(self, workspace: Reference) -> str:
        if isinstance(workspace, str):
            parent_workspace = WorkspaceApi(self._auth).get_workspace(workspace)
            return f"/metadata/workspace/{parent_workspace.id}"
        elif isinstance(workspace, int):
            return f"/metadata/workspace/{workspace}"
        else:
            raise InvalidReferenceError("workspace", workspace)

    def get_connection(self, connection: Reference, workspace: Optional[Reference] = None) -> ConnectionOutput:
        if isinstance(connection, int):
            url = f"/metadata/connection/{connection}"
        elif isinstance(connection, str):
            if isinstance(workspace, str):
                parent_workspace = WorkspaceApi(self._auth).get_workspace(workspace)
                url = f"/metadata/workspace/{parent_workspace.id}/connection/name/{urllib.parse.quote(connection)}"
            elif isinstance(workspace, int):
                url = f"/metadata/workspace/{workspace}/connection/name/{urllib.parse.quote(connection)}"
            else:
                raise InvalidReferenceError("workspace", workspace)
        else:
            raise InvalidReferenceError("connection", connection)
        try:
            response = self._auth._get(url)
        except HttpError as e:
            raise self._httpErrorHandler.handleGetHttpError(e, "connection", connection)
        return ConnectionOutput(**response)

    def list_connections(
        self,
        workspace: Reference,
        connection_type: Optional[str] = None,
        search: Optional[str] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> PagedResponse[ConnectionOutput]:
        url = self._create_base_url(workspace)
        queries: Dict[str, Any] = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        if connection_type:
            queries["type"] = connection_type
        try:
            response = self._auth._get(url + "/connection" + "?" + urlencode(queries))
            return PagedResponse(
                item_cls=ConnectionOutput,
                total=response["total"],
                page=response["page"],
                items=response["items"],
            )
        except HttpError as e:
            raise self._httpErrorHandler.handleGetHttpError(e, "workspace", workspace)

    def delete_connection(self, connection: Reference, workspace: Reference) -> None:
        if not isinstance(connection, int) and not isinstance(connection, str):
            raise ValueError("Please provide a valid connection reference.")
        connection_output = self.get_connection(connection, workspace)
        try:
            self._auth._delete(f"/metadata/connection/{connection_output.id}")
        except HttpError as e:
            raise self._httpErrorHandler.handleDeleteHttpError(e, "connection", connection)

    def create_connection(self, data: ConnectionInput, workspace: Reference) -> ConnectionOutput:
        parent_workspace = WorkspaceApi(self._auth).get_workspace(workspace)
        url = f"/metadata/workspace/{parent_workspace.id}/connection"
        response = self._auth._post(url, data)
        return ConnectionOutput(**response)

    def update_connection(self, data: ConnectionInput, connection: Reference, workspace: Reference) -> ConnectionOutput:
        if not isinstance(connection, int) and not isinstance(connection, str):
            raise ValueError("Please provide a valid connection reference.")
        parent_workspace = WorkspaceApi(self._auth).get_workspace(workspace)
        if isinstance(connection, int):
            response = self._auth._put(f"/metadata/workspace/{parent_workspace.id}/connection/{connection}", data)
            return ConnectionOutput(**response)
        else:
            connection_output = self.get_connection(connection, parent_workspace.id)
            response = self._auth._put(
                f"/metadata/workspace/{parent_workspace.id}/connection/{connection_output.id}", data
            )
            return ConnectionOutput(**response)
