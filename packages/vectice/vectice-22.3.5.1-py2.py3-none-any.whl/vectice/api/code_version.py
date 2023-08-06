from __future__ import annotations

from typing import Optional, TYPE_CHECKING, List
from urllib.parse import urlencode

from ._auth import Auth
from ._http import HttpError
from .code import CodeApi
from .http_error_handlers import HttpErrorHandler
from .json import Page, PagedResponse, CodeVersionInput, CodeVersionOutput
from .project import ProjectApi
from .reference import InvalidReferenceError, MissingReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class CodeVersionApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def create_code_version(
        self,
        code_data: CodeVersionInput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersionOutput:
        if project is None:
            raise InvalidReferenceError("project", project)
        project_output = ProjectApi(self._auth).get_project(project, workspace)
        url = f"/metadata/project/{project_output.id}/codeversion"
        try:
            response = self._auth._post(url, code_data)
            return CodeVersionOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "code")

    def get_code_version(
        self,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersionOutput:
        if not isinstance(version, int) and not isinstance(version, str):
            raise ValueError("The code version reference is invalid. Please check the entered value.")
        if isinstance(version, int):
            try:
                url = f"/metadata/codeversion/{version}"
                response = self._auth._get(url)
                return CodeVersionOutput(**response)
            except HttpError as e:
                raise self._httpErrorhandler.handleGetHttpError(e, "code version", version)
            except IndexError:
                raise ValueError("The code version is invalid. Please check the entered value.")
        elif isinstance(version, str):
            if project is None:
                raise MissingReferenceError("project", project)
            code_version_list = self.list_code_versions(project, workspace, version)
            if len(code_version_list) == 1:
                return code_version_list[0]
            else:
                raise ValueError("The code version is invalid. Please check the entered value.")

    def list_code_versions(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> List[CodeVersionOutput]:
        if project is None:
            raise InvalidReferenceError("project", project)
        project_output = ProjectApi(self._auth).get_project(project, workspace)
        if search is not None:
            code_list = CodeApi(self._auth).list_codes(project, workspace).list
            for code in code_list:
                url = f"/metadata/project/{project_output.id}/code/{code.id}/version"
                queries = {"index": page_index, "size": page_size}
                if search:
                    queries["search"] = search
                response = self._auth._get(f"{url}?{urlencode(queries)}")
                result = PagedResponse(
                    item_cls=CodeVersionOutput, total=response["total"], page=response["page"], items=response["items"]
                )
                if len(result.list) >= 1:
                    return result.list
            else:
                raise ValueError("The code version was not found.")
        elif search is None:
            results = []
            code_list = CodeApi(self._auth).list_codes(project, workspace).list
            for code in code_list:
                url = f"/metadata/project/{project_output.id}/code/{code.id}/version"
                queries = {"index": page_index, "size": page_size}
                if search:
                    queries["search"] = search
                response = self._auth._get(f"{url}?{urlencode(queries)}")
                result = PagedResponse(
                    item_cls=CodeVersionOutput, total=response["total"], page=response["page"], items=response["items"]
                )
                if len(result.list) >= 1:
                    results += result.list
            return results

    def update_code_version(
        self,
        code_data: CodeVersionInput,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersionOutput:
        if project is None:
            raise InvalidReferenceError("project", project)
        code_version_object = self.get_code_version(version, project, workspace)
        url = f"/metadata/codeversion/{code_version_object.id}"
        try:
            response = self._auth._put(url, code_data)
            return CodeVersionOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePutHttpError(e, "version", code_version_object.id)

    def delete_code_version(
        self,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        try:
            code_version_object = self.get_code_version(version, project, workspace)
            if code_version_object is None:
                raise ValueError("The code version was not found.")
            self._auth._delete(f"/metadata/codeversion/{code_version_object.id}")
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "code_version", version)
