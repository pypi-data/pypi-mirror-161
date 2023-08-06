from __future__ import annotations

import logging
import urllib
from typing import Optional, TYPE_CHECKING, List
from urllib.parse import urlencode

from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import (
    ModelVersionOutput,
    ModelVersionInput,
    Page,
    PagedResponse,
    PropertyInput,
    PropertyOutput,
    MetricInput,
    MetricOutput,
)

from .model import ModelApi
from .reference import InvalidReferenceError, MissingReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class ModelVersionApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_model_version(
        self,
        version: Reference,
        model: Optional[Reference],
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ModelVersionOutput:
        if not isinstance(version, int) and not isinstance(version, str):
            raise ValueError("The model version reference is invalid. Please check the entered value.")

        if isinstance(version, int):
            url = f"/metadata/modelversion/{version}"
        elif isinstance(version, str):
            if model is None:
                raise MissingReferenceError("model version", "model")
            parent_model = ModelApi(self._auth).get_model(model, project, workspace)
            url = f"/metadata/project/{parent_model.project.id}/model/{parent_model.id}/version/name/{urllib.parse.quote(version)}"
        try:
            response = self._auth._get(url)
            return ModelVersionOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "model version", version)
        except IndexError:
            raise ValueError("The model version is invalid. Please check the entered value.")

    def list_model_versions(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[ModelVersionOutput]:
        parent_model = ModelApi(self._auth).get_model(model, project, workspace)
        if isinstance(model, int):
            url = f"/metadata/project/{parent_model.project.id}/model/{model}/version"
        elif isinstance(model, str):
            url = f"/metadata/project/{parent_model.project.id}/model/{parent_model.id}/version"
        else:
            raise InvalidReferenceError("model", model)
        queries = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        model_versions = self._auth._get(url + "?" + urlencode(queries))
        return PagedResponse(
            item_cls=ModelVersionOutput,
            total=model_versions["total"],
            page=model_versions["page"],
            items=model_versions["items"],
        )

    def create_model_version(
        self,
        data: ModelVersionInput,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ModelVersionOutput:
        parent_model = ModelApi(self._auth).get_model(model, project, workspace)
        if isinstance(model, int):
            url = f"/metadata/project/{parent_model.project.id}/model/{model}/version"
        elif isinstance(model, str):
            url = f"/metadata/project/{parent_model.project.id}/model/{parent_model.id}/version"
        else:
            raise InvalidReferenceError("model", model)
        response = self._auth._post(url, data)
        return ModelVersionOutput(**response)

    def update_model_version(
        self,
        data: ModelVersionInput,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ModelVersionOutput:
        model_version_object = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/modelversion/{model_version_object.id}"
        try:
            response = self._auth._put(url, data)
            return ModelVersionOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePutHttpError(e, "dataset version", version)

    def delete_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        try:
            model_version = self.get_model_version(version, model, project, workspace)
            self._auth._delete(f"/metadata/modelversion/{model_version.id}")
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "model version", version)

    def create_model_version_properties(
        self,
        version: Reference,
        properties: List[PropertyInput],
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        model_version = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/project/{model_version['model']['project']['id']}/model/{model_version['model']['id']}/version/{model_version.id}/entityProperty"
        if properties:
            for property in properties:
                self._auth._post(
                    url,
                    property,
                )
        self._logger.info(
            f"Hyperparameters with names: {[k.key for k in properties]} successfully added to ModelVersion {model_version.name}."
        )

    def update_model_version_properties(
        self,
        version: Reference,
        property_id: int,
        properties: List[PropertyInput],
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        model_version = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/project/{model_version['model']['project']['id']}/model/{model_version['model']['id']}/version/{model_version.id}/entityProperty/{property_id}"
        if properties:
            for property in properties:
                self._auth._put(
                    url,
                    property,
                )
        self._logger.info(
            f"Hyperparameters with names: {[k.key for k in properties]} successfully updated in ModelVersion {model_version.name}."
        )

    def create_model_version_metrics(
        self,
        version: Reference,
        metrics: List[MetricInput],
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        model_version = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/project/{model_version['model']['project']['id']}/model/{model_version['model']['id']}/version/{model_version.id}/entityMetric"
        if metrics:
            for metric in metrics:
                self._auth._post(
                    url,
                    metric,
                )
        self._logger.info(
            f"Metrics with names: {[k.key for k in metrics]} successfully added to ModelVersion {model_version.name}."
        )

    def update_model_version_metrics(
        self,
        version: Reference,
        metric_id: int,
        metrics: List[MetricInput],
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        model_version = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/project/{model_version['model']['project']['id']}/model/{model_version['model']['id']}/version/{model_version.id}/entityMetric/{metric_id}"
        if metrics:
            for metric in metrics:
                self._auth._put(
                    url,
                    metric,
                )
        self._logger.info(
            f"Metrics with names: {[k.key for k in metrics]} successfully updated in ModelVersion {model_version.name}."
        )

    def list_model_version_metrics(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[MetricOutput]:
        model_version = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/project/{model_version['model']['project']['id']}/model/{model_version['model']['id']}/version/{model_version.id}/entityMetric"
        queries = {"index": page_index, "size": page_size}
        if search is not None:
            queries["search"] = search
        model_version_metrics = self._auth._get(url + "?" + urlencode(queries))
        metrics = [MetricOutput.from_dict(metric).as_dict() for metric in model_version_metrics["items"]]
        return PagedResponse(
            item_cls=MetricOutput,
            total=model_version_metrics["total"],
            page=model_version_metrics["page"],
            items=metrics,
        )

    def list_model_version_properties(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[PropertyOutput]:
        model_version = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/project/{model_version['model']['project']['id']}/model/{model_version['model']['id']}/version/{model_version.id}/entityProperty"
        queries = {"index": page_index, "size": page_size}
        if search is not None:
            queries["search"] = search
        model_version_properties = self._auth._get(url + "?" + urlencode(queries))
        properties = [PropertyOutput.from_dict(property).as_dict() for property in model_version_properties["items"]]
        return PagedResponse(
            item_cls=PropertyOutput,
            total=model_version_properties["total"],
            page=model_version_properties["page"],
            items=properties,
        )

    def delete_model_version_metrics(
        self,
        version: Reference,
        metric_id: int,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        model_version = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/project/{model_version['model']['project']['id']}/model/{model_version['model']['id']}/version/{model_version.id}/entityMetric/{metric_id}"
        metric_list = self.list_model_version_metrics(model_version.id, model, project, workspace).list
        self._auth._delete(url)
        self._logger.info(
            f"Metrics with names: {[item.as_dict()['key']  for item in metric_list if item.as_dict()['id'] == metric_id]} successfully deleted from ModelVersion {model_version.name}."
        )

    def delete_model_version_properties(
        self,
        version: Reference,
        property_id: int,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        model_version = self.get_model_version(version, model, project, workspace)
        url = f"/metadata/project/{model_version['model']['project']['id']}/model/{model_version['model']['id']}/version/{model_version.id}/entityProperty/{property_id}"
        hyperparameters_list = self.list_model_version_properties(model_version.id, model, project, workspace).list
        self._auth._delete(url)
        self._logger.info(
            f"Hyperparameters with names: {[item.as_dict()['key']  for item in hyperparameters_list if item.as_dict()['id'] == property_id]} successfully deleted from ModelVersion {model_version.name}."
        )
