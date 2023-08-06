from __future__ import annotations

import urllib
from typing import Optional, TYPE_CHECKING

from .reference import InvalidReferenceError, MissingReferenceError
from ._auth import Auth
from ._http import HttpError
from .json import ProjectOutput, PagedResponse, ProjectInput
from .http_error_handlers import HttpErrorHandler
from .workspace import WorkspaceApi

if TYPE_CHECKING:
    from vectice import Reference


class ProjectApi:
    def __init__(
        self,
        auth: Auth,
    ):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def create_project(self, data: ProjectInput, workspace: Reference) -> ProjectOutput:
        if isinstance(workspace, int):
            url = f"/metadata/workspace/{workspace}/project"
        elif isinstance(workspace, str):
            parent_workspace = WorkspaceApi(self._auth).get_workspace(workspace)
            url = f"/metadata/workspace/{parent_workspace.id}/project"
        else:
            raise InvalidReferenceError("workspace", workspace)
        try:
            response = self._auth._post(url, data)
            return ProjectOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "project")
        except IndexError:
            raise ValueError("The project is invalid. Please check the entered value.")

    def delete_project(self, project: Reference, workspace: Optional[Reference] = None):
        project_output = self.get_project(project, workspace)
        url = f"/metadata/project/{project_output.id}"
        try:
            response = self._auth._delete(url)
            return ProjectOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handleDeleteHttpError(e, "project", project)
        except IndexError:
            raise ValueError("The project is invalid. Please check the entered value.")

    def get_project(self, project: Reference, workspace: Optional[Reference] = None) -> ProjectOutput:
        if isinstance(project, int):
            url = f"/metadata/project/{project}"
        elif isinstance(project, str):
            if workspace is None:
                raise MissingReferenceError("workspace")
            parent_workspace = WorkspaceApi(self._auth).get_workspace(workspace)
            url = f"/metadata/workspace/{parent_workspace.id}/project/name/{urllib.parse.quote(project)}"
        else:
            raise InvalidReferenceError("project", project)
        try:
            response = self._auth._get(url)
            return ProjectOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "project", project)
        except IndexError:
            raise ValueError("The project is invalid. Please check the entered value.")

    def update_project(self, data: ProjectInput, project: Reference, workspace: Reference) -> ProjectOutput:
        if isinstance(workspace, int):
            base_url = f"/metadata/workspace/{workspace}/project"
        elif isinstance(workspace, str):
            base_url = f"/metadata/workspace/name/{urllib.parse.quote(workspace)}/project"
        else:
            raise InvalidReferenceError("workspace", workspace)
        if isinstance(project, int):
            url = f"/metadata/project/{project}"
        elif isinstance(project, str):
            url = f"{base_url}/name/{urllib.parse.quote(project)}"
        else:
            raise InvalidReferenceError("project", project)
        try:
            response = self._auth._put(url, data)
            return ProjectOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePutHttpError(e, "project", project)
        except IndexError:
            raise ValueError("The project is invalid. Please check the entered value.")

    def list_projects(
        self, workspace: Reference, search: Optional[str] = None, page_index: int = 1, page_size: int = 20
    ) -> PagedResponse[ProjectOutput]:
        if isinstance(workspace, int):
            url = f"/metadata/workspace/project?index={page_index}&size={page_size}&workspaceId={workspace}"
        elif isinstance(workspace, str):
            url = f"/metadata/workspace/project?index={page_index}&size={page_size}&workspaceName={workspace}"
        else:
            raise InvalidReferenceError("workspace", workspace)
        if search:
            url = url + f"&search={search}"
        projects = self._auth._get(url)
        return PagedResponse(
            item_cls=ProjectOutput, total=projects["total"], page=projects["page"], items=projects["items"]
        )
