from __future__ import annotations

import urllib
from typing import Optional
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import DatasetOutput, DatasetInput, Page, PagedResponse
from .project import ProjectApi
from .reference import InvalidReferenceError, MissingReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class DatasetApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def get_dataset(
        self, dataset: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> DatasetOutput:
        if not isinstance(dataset, int) and not isinstance(dataset, str):
            raise InvalidReferenceError("dataset", dataset)
        if isinstance(dataset, int):
            parent_project = None
            url = f"/metadata/dataset/{dataset}"
        else:
            if project is None:
                raise MissingReferenceError("dataset", "project")
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/dataset/name/{urllib.parse.quote(dataset)}"
        try:
            response = self._auth._get(url)
            result = DatasetOutput(**response)
            if parent_project is not None:
                result.project = parent_project
            return result
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "dataset", dataset)
        except IndexError:
            raise ValueError("The dataset is invalid. Please check the entered value.")

    def delete_dataset(
        self, dataset: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ):
        try:
            if isinstance(dataset, str):
                dataset_object = self.get_dataset(dataset, project, workspace)
                self._auth._delete(f"/metadata/dataset/{dataset_object.id}")
            else:
                self._auth._delete(f"/metadata/dataset/{dataset}")
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "dataset", dataset)

    def list_datasets(
        self,
        project: Reference,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[DatasetOutput]:
        if isinstance(project, int):
            base_url = f"/metadata/project/{project}/dataset"
        elif isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            base_url = f"/metadata/project/{parent_project.id}/dataset"
        else:
            raise InvalidReferenceError("project", project)
        try:
            queries = {"index": page_index, "size": page_size}
            if search:
                queries["search"] = search
            response = self._auth._get(f"{base_url}?{urlencode(queries)}")
            result = PagedResponse(
                item_cls=DatasetOutput, total=response["total"], page=response["page"], items=response["items"]
            )
            return result
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "project", project)

    def create_dataset(
        self, data: DatasetInput, project: Reference, workspace: Optional[Reference] = None
    ) -> DatasetOutput:
        if data.name is None:
            raise ValueError('"name" must be provided in dataset.')
        if isinstance(project, int):
            url = f"/metadata/project/{project}/dataset"
        elif isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/dataset"
        else:
            raise InvalidReferenceError("project", project)
        try:
            response = self._auth._post(url, data)
            return DatasetOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "dataset")

    def update_dataset(
        self,
        data: DatasetOutput,
        dataset: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> DatasetOutput:
        if data.name is None:
            raise ValueError('"name" must be provided in dataset.')
        if isinstance(dataset, int):
            url = f"/metadata/dataset/{dataset}"
        elif isinstance(dataset, str):
            dataset_object = self.get_dataset(dataset, project, workspace)
            url = f"/metadata/dataset/{dataset_object.id}"
        else:
            raise InvalidReferenceError("dataset", dataset)
        try:
            response = self._auth._put(url, data)
            return DatasetOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePutHttpError(e, "dataset", dataset)
