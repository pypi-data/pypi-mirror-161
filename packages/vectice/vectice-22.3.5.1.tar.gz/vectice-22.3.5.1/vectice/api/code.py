from __future__ import annotations

import urllib
from typing import Optional, TYPE_CHECKING
from urllib.parse import urlencode

from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import CodeInput, CodeOutput, Page, PagedResponse
from .project import ProjectApi
from .reference import InvalidReferenceError, MissingReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class CodeApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def create_code(
        self,
        code_data: CodeInput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeOutput:
        if code_data.name is None:
            raise ValueError('"name" must be provided in code.')
        if isinstance(project, int):
            url = f"/metadata/project/{project}/code"
        elif isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/code"
        else:
            raise InvalidReferenceError("project", project)
        try:
            response = self._auth._post(url, code_data)
            return CodeOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "code")

    def get_code(
        self,
        code: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeOutput:
        if not isinstance(code, int) and not isinstance(code, str):
            raise InvalidReferenceError("code", code)
        if project is None:
            raise MissingReferenceError("code", "project")
        parent_project = ProjectApi(self._auth).get_project(project, workspace)
        if isinstance(code, int):
            url = f"/metadata/project/{parent_project.id}/code/{code}"
        else:
            url = f"/metadata/project/{parent_project.id}/code/name/{urllib.parse.quote(code)}"
        try:
            response = self._auth._get(url)
            return CodeOutput(response)
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "code", code)
        except IndexError:
            raise ValueError("The code is invalid. Please check the entered value.")

    # There is No route in the backend to list code
    # Waiting for BE implementation : https://app.shortcut.com/vectice/story/23415/list-code-rest-api
    def list_codes(
        self,
        project: Reference,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[CodeOutput]:
        if isinstance(project, int):
            url = f"/metadata/project/{project}/code"
        elif isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/code"
        else:
            raise InvalidReferenceError("project", project)
        try:
            queries = {"index": page_index, "size": page_size}
            if search:
                queries["search"] = search
            response = self._auth._get(f"{url}?{urlencode(queries)}")
            result = PagedResponse(
                item_cls=CodeOutput, total=response["total"], page=response["page"], items=response["items"]
            )
            return result
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "project", project)

    def update_code(
        self,
        code_data: CodeOutput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeOutput:
        code_output = self.get_code(code_data.id, project, workspace)
        url = f"/metadata/project/{code_output.project_id}/code/{code_data.id}"
        try:
            response = self._auth._put(url, code_data)
            return CodeOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePutHttpError(e, "code", code_data.id)

    def delete_code(
        self,
        code: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        try:
            code_object = self.get_code(code, project, workspace)
            if isinstance(code, str):
                self._auth._delete(f"/metadata/project/{code_object.project_id}/code/{code_object.id}")
            else:
                self._auth._delete(f"/metadata/project/{code_object.project_id}/code/{code}")
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "code", code)
