from __future__ import annotations

import urllib
from typing import Optional, List
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import StageInput, StageOutput, Page
from .project import ProjectApi
from .reference import InvalidReferenceError, MissingReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class StageApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def create_stage(self, data: StageInput, project: Reference, workspace: Optional[Reference] = None) -> StageOutput:
        if isinstance(project, int):
            url = f"/metadata/project/{project}/stages"
        elif isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/stages"
        else:
            raise InvalidReferenceError("project", project)
        try:
            response = self._auth._post(url, data)
            return StageOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "stage")

    def update_stage(
        self,
        data: StageInput,
        stage: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> StageOutput:
        if data.name is None:
            raise ValueError('"name" must be provided in dataset.')
        if isinstance(stage, int):
            url = f"/metadata/stages/{stage}"
        elif isinstance(stage, str):
            stage_object = self.get_stage(stage, project, workspace)
            url = f"/metadata/stages/{stage_object.id}"
        else:
            raise InvalidReferenceError("stage", stage)
        try:
            response = self._auth._put(url, data)
            return StageOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePutHttpError(e, "stage", stage)

    def get_stage(
        self, stage: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> StageOutput:
        if not isinstance(stage, int) and not isinstance(stage, str):
            raise InvalidReferenceError("stage", stage)
        if isinstance(stage, int):
            url = f"/metadata/stages/{stage}"
        else:
            if project is None:
                raise MissingReferenceError("project")
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/stages/{urllib.parse.quote(stage)}"
        try:
            response = self._auth._get(url)
            result = StageOutput(response)
            return result
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "stage", stage)
        except IndexError:
            raise ValueError("The stage is invalid. Please check the entered value.")

    def list_stages(
        self,
        project: Reference,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> List[StageOutput]:
        if isinstance(project, int):
            base_url = f"/metadata/project/{project}/stages"
        elif isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            base_url = f"/metadata/project/{parent_project.id}/stages"
        else:
            raise InvalidReferenceError("project", project)
        try:
            queries = {"index": page_index, "size": page_size}
            if search:
                queries["search"] = search
            response = self._auth._get(f"{base_url}?{urlencode(queries)}")
            result = [StageOutput(item) for item in response]
            return result
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "project", project)

    def delete_stage(
        self, stage: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> None:
        try:
            if isinstance(stage, str):
                stage_object = self.get_stage(stage, project, workspace)
                self._auth._delete(f"/metadata/stages/{stage_object.id}")
            else:
                self._auth._delete(f"/metadata/stages/{stage}")
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "stage", stage)
