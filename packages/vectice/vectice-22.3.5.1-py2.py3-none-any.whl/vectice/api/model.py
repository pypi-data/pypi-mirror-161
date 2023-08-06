from __future__ import annotations

import urllib
from typing import Optional, TYPE_CHECKING
from urllib.parse import urlencode

from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import ModelOutput, ModelInput, Page, PagedResponse
from .project import ProjectApi
from .reference import InvalidReferenceError, MissingReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class ModelApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def get_model(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        if not isinstance(model, int) and not isinstance(model, str):
            raise InvalidReferenceError("model", model)
        if isinstance(model, int):
            parent_project = None
            url = f"/metadata/model/{model}"
        else:
            if project is None:
                raise MissingReferenceError("project")
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/model/name/{urllib.parse.quote(model)}"
        try:
            response = self._auth._get(url)
            result = ModelOutput(response)
            if parent_project is not None:
                result.project = parent_project
            return result
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "model", model)

    def list_models(
        self,
        project: Reference,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[ModelOutput]:
        queries = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        if isinstance(project, int):
            base_url = f"/metadata/project/{project}/model"
        else:
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            base_url = f"/metadata/project/{parent_project.id}/model"
        response = self._auth._get(f"{base_url}?{urlencode(queries)}")
        result = PagedResponse(
            item_cls=ModelOutput, total=response["total"], page=response["page"], items=response["items"]
        )
        return result

    def create_model(
        self,
        model: ModelInput,
        project: Reference,
        workspace: Optional[Reference] = None,
    ) -> ModelOutput:
        if model.get("name") is None:
            raise ValueError('"name" must be provided in model.')
        if isinstance(project, int):
            url = f"/metadata/project/{project}/model"
        elif isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/model"
        else:
            raise InvalidReferenceError("project", project)
        try:
            response = self._auth._post(url, model)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "model")
        return ModelOutput(**response)

    def update_model(
        self,
        data: ModelInput,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ModelOutput:
        if isinstance(model, int):
            url = f"/metadata/model/{model}"
        elif isinstance(model, str):
            model_object = self.get_model(model, project, workspace)
            url = f"/metadata/model/{model_object.id}"
        else:
            raise InvalidReferenceError("model", model)
        try:
            response = self._auth._put(url, data)
            return ModelOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "model")

    def delete_model(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        try:
            model_object = self.get_model(model, project, workspace)
            self._auth._delete(f"/metadata/model/{model_object.id}")
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "model", model)
