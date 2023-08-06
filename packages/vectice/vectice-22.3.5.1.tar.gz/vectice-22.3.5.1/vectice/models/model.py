from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Dict, List, TYPE_CHECKING

from vectice.api import Reference, Client
from vectice.api.json import (
    ModelType,
    ModelVersionInput,
    ModelVersionStatus,
    Page,
    PropertyInput,
)
from vectice.api.json.metric import create_metrics_input
from vectice.api.json.property import create_properties_input
from .model_version import ModelVersion
from .property import create_properties

if TYPE_CHECKING:
    from vectice.models import Project


class Model:
    """
    Describes a model

    Noteworthy:
    1. id: Backend will return id if it doesn't exist so it should be optional. SDK doesn't assign id unless we retrieve or resuse a model

    """

    def __init__(
        self,
        name: str,
        id: int,
        project: Project,
        description: Optional[str] = None,
        type: Optional[ModelType] = None,
    ):
        """
        :param name: The name of the model
        :param id: The model id
        :param project: The project this model belongs to
        :param description: The quick description of the model
        :param type: Type of the model
        """
        self._id = id
        self._project = project
        self._name = name
        self._type = type
        self._description = description
        self._client: Client = project._client
        self._logger = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        return f"Model(name={self.name}, id={self.id}, description={self.description}, type={self._type})"

    @property
    def id(self) -> int:
        """
        Model identifier.
        :return: int
        """
        return self._id

    @property
    def project(self) -> Project:
        """
        The project this model belong to.
        :return: Project
        """
        return self._project

    @property
    def name(self) -> str:
        """
        Name of the model.
        :return: str
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """
        Quick description of the model.
        :return: Optional[str]
        """
        return self._description

    @property
    def type(self) -> Optional[ModelType]:
        """
        Type of the model.
        :return: Optional[ModelType]
        """
        return self._type

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Model)
            and self.id == o.id
            and self.name == o.name
            and o.description == self.description
            and self.type == o.type
        )

    def create_model_version(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: ModelVersionStatus = ModelVersionStatus.EXPERIMENTATION,
        algorithm_name: Optional[str] = None,
        is_starred: Optional[bool] = False,
        metrics: Optional[Dict] = None,
        hyper_parameters: Optional[Dict] = None,
        attachments: Optional[List[str]] = None,
        runId: Optional[int] = None,
    ) -> ModelVersion:
        """
        Creates a new model version with all the existing params in Vectice.

        :param name: The name of the model version
        :param description: The description of the model
        :param status: The status of the model e.g 'OTHER'/'CLASSIFICATION'/'REGRESSION'
        :param algorithm_name: The algorithm the model version uses
        :param is_starred: Whether the model is starred or not
        :param metrics: The model version metrics
        :param hyper_parameters: The model version hyper parameters
        :param attachments: Attach file/s to the model version
        :param runId: Link the model version to a run

        :return: A ModelVersion
        """
        self._logger.propagate = True
        data = ModelVersionInput(
            name=name,
            description=description,
            algorithmName=algorithm_name,
            status=status.value,
            isStarred=is_starred,
        )
        if runId is not None:
            data["jobRunId"] = runId
        model_version_output = self._client.create_model_version(data, self._id)
        if hyper_parameters:
            self._client.create_model_version_properties(
                model_version_output.id, create_properties_input(hyper_parameters)
            )
        if metrics:
            self._client.create_model_version_metrics(model_version_output.id, create_metrics_input(metrics))

        model_version = ModelVersion(
            self,
            model_version_output.id,
            model_version_output.name,
            model_version_output.version_number,
            model_version_output.description,
            metrics,
            hyper_parameters,
            model_version_output.algorithm_name,
            model_version_output.status,
            model_version_output.is_starred,
            created_date=model_version_output.created_date if model_version_output.created_date else datetime.now(),
            updated_date=model_version_output.updated_date,
            deleted_date=model_version_output.deleted_date,
        )
        if attachments:
            model_version.add_attachments(attachments)
        self._logger.info(f"ModelVersion with id: {model_version.id} successfully created in Model {self.name}.")
        return model_version

    def update_model_version(
        self,
        version: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = "EXPERIMENTATION",
        algorithm: Optional[str] = None,
        is_starred: Optional[bool] = False,
        metrics: Optional[Dict] = None,
        hyper_parameters: Optional[Dict] = None,
    ) -> ModelVersion:
        """
        Update a model version.
        Updates the specified model version with the new params passed to this function.
        :param version: The model version name or id
        :param name: The name of the model version
        :param description: The description of the model
        :param status: The status of the model e.g 'EXPERIMENTATION'/'STAGING'/'PRODUCTION'
        :param algorithm: The algorithm the model version uses
        :param is_starred: Whether the model is starred or not
        :param metrics: The model version metrics
        :param hyper_parameters: The model version hyper parameters
        :return: ModelVersion
        """
        self._logger.propagate = True
        model_version_input = ModelVersionInput(
            name=name,
            description=description,
            isStarred=is_starred,
            status=status,
            algorithmName=algorithm,
            metrics=metrics,
            hyper_parameters=hyper_parameters,
        )
        model_version_output = self._client.update_model_version(model_version_input, version, self._id)
        if hyper_parameters:
            new_parameters = create_properties(hyper_parameters)
            parameters = {
                prop.key: prop.id
                for prop in self._client.list_model_version_properties(model_version_output.id, self._id).list
            }
            for param in new_parameters:
                if parameters.get(param.key):
                    self._client.update_model_version_properties(
                        model_version_output.id, parameters[param.key], [PropertyInput(param.key, param.value)]
                    )
        if metrics:
            new_metrics = create_metrics_input(metrics)
            metrics_list = {
                metric.key: metric.id
                for metric in self._client.list_model_version_metrics(model_version_output.id, self._id).list
            }
            for metric in new_metrics:
                temp = metrics_list.get(metric.key)
                if temp is not None:
                    self._client.update_model_version_metrics(self.id, model_version_output.id, temp, [metric])
        self._logger.info(f"ModelVersion with id: {model_version_output.id} successfully updated in Model {self.name}.")
        return ModelVersion(
            self,
            model_version_output.id,
            model_version_output.name,
            model_version_output.version_number,
            model_version_output.description,
            metrics,
            hyper_parameters,
            model_version_output.algorithm_name,
            model_version_output.status,
            model_version_output.is_starred,
            model_version_output.user_declared_version,
            model_version_output.created_date if model_version_output.created_date else datetime.now(),
            model_version_output.updated_date,
            model_version_output.deleted_date,
        )

    def list_model_versions(
        self, search: Optional[str] = None, page_index: int = Page.index, page_size: int = Page.size
    ) -> List[ModelVersion]:
        """
        Lists all the versions created out of the specified model.

        :param search: The name to search
        :param page_index:
        :param page_size:

        :return: List of ModelVersions
        """

        def get_parameters(id: int):
            properties_output = self._client.list_model_version_properties(id, self._id)
            parameters = {item.key: item.value for item in properties_output.list}
            return parameters

        model_versions = self._client.list_model_versions(self.id, None, None, search, page_index, page_size)
        return [
            ModelVersion(
                self,
                model_version.id,
                model_version.name,
                model_version.version_number,
                model_version.description,
                model_version.metrics,
                get_parameters(model_version.id),
                model_version.algorithm_name,
                model_version.status,
                model_version.is_starred,
                model_version.user_declared_version,
                model_version.created_date if model_version.created_date else datetime.now(),
                model_version.updated_date,
                model_version.deleted_date,
            )
            for model_version in model_versions.list
        ]

    def list_model_versions_dataframe(
        self,
        search: Optional[str] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> "pandas.DataFrame":  # type: ignore # noqa F821
        """
        Lists model versions in a pandas DataFrame and sorts by update date. Requires the pandas module to be installed,
        which can be done with ```pip install pandas``` or ```pip install vectice[pandas]```

        :param search: filter on name
        :param page_index: The page index. For example 1/20 would return page 1
        :param page_size: The number of versions on a page
        :return: pd.DataFrame
        """
        import pandas as pd  # type: ignore

        model_versions = self._client.list_model_versions(self.id, None, None, search, page_index, page_size)
        metric_dataframes = []
        property_dataframes = []
        for idx, model_version in enumerate(model_versions.list, start=0):
            model_metrics = self._client.list_model_version_metrics(model_version.id, 1, 1000).list
            temp_df_metrics = pd.DataFrame(
                data={metrics.key: [metrics.value] for metrics in model_metrics}, index=[idx]
            )
            metric_dataframes += [temp_df_metrics]

        for idx, model_version in enumerate(model_versions.list, start=0):
            models_properties = self._client.list_model_version_properties(model_version.id, 1, 1000).list
            temp_df_metrics = pd.DataFrame(
                data={metrics.key: [metrics.value] for metrics in models_properties}, index=[idx]
            )
            property_dataframes += [temp_df_metrics]

        metric_dataframes = pd.concat(metric_dataframes)
        property_dataframes = pd.concat(property_dataframes)
        merged_entities = pd.merge(metric_dataframes, property_dataframes, left_index=True, right_index=True)
        df_model = pd.DataFrame(
            data=model_versions.list,
            # "created_date", "name", "version_number", "status", "algorithm_name", "is_starred"
            columns=["createdDate", "name", "versionNumber", "status", "algorithmName", "isStarred"],
        )
        return pd.merge(df_model, merged_entities, left_index=True, right_index=True).sort_values(
            by=["versionNumber"], ascending=False
        )

    def get_model_version(
        self,
        version: Reference,
    ) -> ModelVersion:
        """
        Gets a specific version of a model.

        :param version: The model version name or id
        :return: A ModelVersion
        """
        self._logger.propagate = True
        model_version_output = self._client.get_model_version(version=version, model=self._id)
        properties_output = self._client.list_model_version_properties(model_version_output.id, self.id)
        parameters = {item.key: item.value for item in properties_output.list}
        metrics_output = self._client.list_model_version_metrics(model_version_output.id, self.id)
        metrics = {item.key: item.value for item in metrics_output.list}
        self._logger.info(
            f"ModelVersion with id: {model_version_output.id} successfully retrieved from Model {self.name}."
        )
        return ModelVersion(
            self,
            model_version_output.id,
            model_version_output.name,
            model_version_output.version_number,
            model_version_output.description,
            metrics,
            parameters,
            model_version_output.algorithm_name,
            model_version_output.status,
            model_version_output.is_starred,
            model_version_output.user_declared_version,
            model_version_output.created_date if model_version_output.created_date else datetime.now(),
            model_version_output.updated_date,
            model_version_output.deleted_date,
        )

    def delete_model_version(
        self,
        version: Reference,
    ) -> None:
        """
        Deletes the specified version of a model.

        :param version: The model version name or id
        :return: None
        """
        self._logger.propagate = True
        model_version = self._client.get_model_version(version, self._id)
        self._client.delete_model_version(version, self._id)
        self._logger.info(f"ModelVersion with id: {model_version.id} successfully deleted from Model {self.name}.")

    def delete_model_version_properties(self, version: Reference, properties: List[str]):
        """
        Deletes the specified properties of a model version.

        :param version: The model version name or id
        :param properties: List of property names to delete.
        :return: None
        """
        property_ids = {item.key: item.id for item in self._client.list_model_version_properties(version, self.id).list}
        for prop in properties:
            if property_ids.get(prop):
                self._client.delete_model_version_properties(version, property_ids[prop], self.id)
            else:
                logging.warning(f"Hyper Parameter {prop} was not be found.")

    def delete_model_version_metrics(self, version: Reference, metrics: List[str]):
        """
        Deletes the specified metrics of a model version.

        :param version: The model version name or id
        :param metrics: List of metric names to delete.
        :return: None
        """
        metric_ids = {item.key: item.id for item in self._client.list_model_version_metrics(version, self.id).list}
        for metric in metrics:
            temp = metric_ids.get(metric)
            if temp is not None:
                self._client.delete_model_version_metrics(version, temp, self.id)
            else:
                logging.warning(f"Metric {metric} was not be found.")
