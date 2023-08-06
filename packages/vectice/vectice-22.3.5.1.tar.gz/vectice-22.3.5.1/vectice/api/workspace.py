from __future__ import annotations


import urllib.parse

from typing import Optional, TYPE_CHECKING

from vectice.api._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import WorkspaceOutput, PagedResponse
from .json.workspace import WorkspaceInput
from .reference import InvalidReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class WorkspaceApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def get_workspace(self, workspace: Reference) -> WorkspaceOutput:
        if isinstance(workspace, int):
            url = f"/metadata/workspace/{workspace}"
        elif isinstance(workspace, str):
            url = f"/metadata/workspace/name/{urllib.parse.quote(workspace)}"
        else:
            raise InvalidReferenceError("workspace", workspace)
        try:
            response = self._auth._get(url)
            return WorkspaceOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "workspace", workspace)
        except TypeError:
            raise ValueError("The workspace is invalid. Please check the entered value.")

    def list_workspaces(
        self, search: Optional[str] = None, page_index: int = 1, page_size: int = 20
    ) -> PagedResponse[WorkspaceOutput]:
        if search is None or search == "":
            url = f"/metadata/workspace?index={page_index}&size={page_size}"
        else:
            url = f"/metadata/workspace?index={page_index}&size={page_size}&search={search}"
        workspaces = self._auth._get(url)
        return PagedResponse(
            item_cls=WorkspaceOutput, total=workspaces["total"], page=workspaces["page"], items=workspaces["items"]
        )

    def create_workspace(self, data: WorkspaceInput) -> WorkspaceOutput:
        url = "/metadata/workspace"
        try:
            response = self._auth._post(url, data.__dict__)
            return WorkspaceOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "workspace")
        except TypeError:
            raise ValueError("The workspace is invalid. Please check the entered value.")

    def update_workspace(self, data: WorkspaceInput, workspace: Reference) -> WorkspaceOutput:
        if isinstance(workspace, int):
            url = f"/metadata/workspace/{workspace}"
        elif isinstance(workspace, str):
            workspace_object = self.get_workspace(workspace)
            url = f"/metadata/workspace/{workspace_object.id}"
        else:
            raise InvalidReferenceError("workspace", workspace)
        try:
            response = self._auth._put(url, data)
            return WorkspaceOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePutHttpError(e, "workspace", workspace)
        except TypeError:
            raise ValueError("The workspace is invalid. Please check the entered value.")
