from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Union, Dict, List, TYPE_CHECKING, BinaryIO, Any

from vectice.api.json import ModelVersionStatus, PropertyInput, ArtifactVersion, UserDeclaredVersion
from vectice.api.json.metric import create_metrics_input, MetricInput
from vectice.api.json.property import create_properties_input
from vectice.models.attachment_container import AttachmentContainer
from vectice.models.metric import Metric
from vectice.models.property import Property

if TYPE_CHECKING:
    from vectice.models import Model


class ModelVersion(AttachmentContainer):
    """
    A version of the model.

    A ModelVersion store several information that can change between 2 versions like hyper parameters or metrics.

    Noteworthy:
    1. id: Backend will return id if it doesn't exist so it should be optional. SDK doesn't assign id unless we retrieve or reuse a modelVersion.
    2. model: We need the model name or id for a scenario where we won't have the modelVersionId. Currently not in the backend modelVersion.createDTO.
    3. version: Optional as we don't always need it e.g creation of model version. Currently not in the backend modelVersion.createDTO.
    4. status: Backend will throw an error if there's no status, default to EXPERIMENTATION.
    """

    def __init__(
        self,
        model: Model,
        id: int,
        name: str,
        version_number: int,
        description: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None,
        hyper_parameters: Optional[Dict[str, str]] = None,
        algorithm_name: Optional[str] = None,
        status: ModelVersionStatus = ModelVersionStatus.EXPERIMENTATION,
        is_starred: bool = False,
        user_declared_version: Optional[UserDeclaredVersion] = None,
        created_date: Optional[datetime] = None,
        updated_date: Optional[datetime] = None,
        deleted_date: Optional[datetime] = None,
    ):
        """
        :param model: The parent model of this model version
        :param id: The model version identifier
        :param name: The model version name
        :param version_number: The model version number
        :param description: The model version description
        :param metrics: The list of timestamped key/value pair
        :param hyper_parameters: List of parameters of the model
        :param algorithm_name: The algorithm name
        :param status: The status of the version
        :param is_starred: If the model isStarred
        :param user_declared_version: user declared version
        :param created_date: Creation date of the model version
        :param updated_date: Update date of the model version
        :param deleted_date: Delete date of the model version
        """
        super().__init__(name, id, model._client, "ModelVersion")
        self._model: Model = model
        self._metrics = metrics
        self._properties = hyper_parameters
        self._description = description
        self._algorithmName = algorithm_name
        self._status = status
        self._isStarred = is_starred
        self._version_number = version_number
        self._created_date = created_date
        self._updated_date = updated_date
        self._deleted_date = deleted_date
        self._user_declared_version: Optional[UserDeclaredVersion] = user_declared_version

    def __repr__(self):
        return f"ModelVersion(model={self.model}, id={self.id}, description={self.description}, metrics={self.metrics}, hyper_parameters={self.properties}, algorithm_name={self.algorithmName}, status={self.status}, is_starred={self.is_starred}, version={self.version}, user_declared_version={self.user_declared_version})"

    @property
    def is_starred(self) -> bool:
        """
        Boolean for starring the model version.
        :return: bool
        """
        return self._isStarred

    @property
    def model(self) -> Model:
        """
        The parent Model object.
        :return: Model
        """
        return self._model

    @property
    def id(self) -> int:
        """
        The model version id.
        :return: int
        """
        return self._id

    @property
    def name(self) -> str:
        """
        The model version name.
        :return: str
        """
        return self._name

    @property
    def metrics(self) -> Optional[Dict[str, float]]:
        """
        The model version metrics.
        :return: Optional[Dict[str, float]]
        """
        return self._metrics

    @property
    def properties(self) -> Optional[Dict[str, str]]:
        """
        The model version properties.
        :return: Optional[Dict[str, str]]
        """
        return self._properties

    @property
    def description(self) -> Optional[str]:
        """
        A quick description of the model version.
        :return: Optional[str]
        """
        return self._description

    @property
    def user_declared_version(self):
        """
        The user declared version.
        """
        return self._user_declared_version

    @user_declared_version.setter
    def user_declared_version(self, version: UserDeclaredVersion):
        """
        user generated version uses an empty UserDeclaredVersion()
        """
        self._user_declared_version = version

    @property
    def algorithmName(self) -> Optional[str]:
        """
        The algorithm name used for the model version.
        :return: Optional[str]
        """
        return self._algorithmName

    @property
    def status(self) -> Optional[ModelVersionStatus]:
        """
        The model version status, it can be "EXPERIMENTATION" or "STAGING" or "PRODUCTION".
        :return: Optional[ModelVersionStatus]
        """
        return self._status

    @status.setter
    def status(self, status: ModelVersionStatus):
        self._status = status

    @property
    def parent_name(self) -> Optional[str]:
        """
        The parent model name.
        :return: Optional[str]
        """
        return self._model.name

    @property
    def parent_id(self) -> Optional[int]:
        """
        The parent model id.
        :return: Optional[int]
        """
        return self._model.id

    @property
    def version(self) -> ArtifactVersion:
        """
        The model version artifact.
        :return: ArtifactVersion
        """
        return ArtifactVersion(self._version_number, self._name, self._id)

    @property
    def version_number(self) -> int:
        """
        The model version number.
        :return: int
        """
        return self._version_number

    @property
    def created_date(self) -> Optional[datetime]:
        """
        The model version number.
        :return: int
        """
        return self._created_date

    def create_metrics(self, metrics: Union[List[Metric], Dict[str, Any]]) -> None:
        """
        Create some metrics to the existing list of metrics.

        There are 2 solution to add metrics:
        - a list of already timestamped metrics.
        - a dictionary of key/value. In this case, the timestamp used is the time this method is called.

        :param metrics: The metrics e.g metric_key: value = {'metric_key': 1}

        :return: None
        """
        if isinstance(metrics, List):
            param = [MetricInput(item.key, item.value, item.timestamp) for item in metrics]
        else:
            param = create_metrics_input(metrics)
        return self._client.create_model_version_metrics(self.id, param)

    def list_metrics(
        self,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> Optional[Dict[str, Any]]:
        """
        Lists the metrics used for the specified model version.

        :param search: The name to search
        :param page_index:
        :param page_size:

        :return: A List of Metrics
        """
        return {
            prop.key: prop.value
            for prop in self._client.list_model_version_metrics(
                self.id, search=search, page_size=page_size, page_index=page_index
            ).list
        }

    def delete_metrics(
        self,
        metrics: Union[List[int], List[str]],
    ) -> None:
        """
        Deletes a metric used for the specified model version.

        :param metrics: The metric ids or keys

        :return: None
        """
        metrics_reference = {
            metric.key: metric.id for metric in self._client.list_model_version_metrics(self.id).list if metric.id
        }
        for metric in metrics:
            if isinstance(metric, int):
                metric_id = metric
            elif isinstance(metric, str):
                metric_id = int(metrics_reference[metric])
            else:
                raise ValueError(f"{metric} could not be found. Please check the value.")
            try:
                self._client.delete_model_version_metrics(self.id, metric_id, self.model.id)
            except Exception as e:
                logging.warning(f"Metric {metric} failed to delete due to {e}")

    def create_hyper_parameters(self, hyper_parameters: Dict[str, Union[int, float, str]]):
        """
        Updates the hyper parameters used for the specified model version.

        :param hyper_parameters: A dict of hyper_parameter key : value

        :return: None
        """
        self._client.create_model_version_properties(self.id, create_properties_input(hyper_parameters))

    def update_hyper_parameters(self, hyper_parameters: Dict[str, Union[str, float, int]]) -> None:
        """
        Updates the hyper parameters used for the specified model version.

        :param hyper_parameters:  A dict of hyper_parameter key : value

        :return: None
        """
        properties = {prop.key: prop.id for prop in self._client.list_model_version_properties(self.id).list}
        for key, value in hyper_parameters.items():
            if properties.get(key):
                property_id = properties[key]
                property_values = Property(key, value)
                try:
                    self._client.update_model_version_properties(
                        self.id, property_id, [PropertyInput(property_values.key, property_values.value)]
                    )
                except Exception as e:
                    logging.warning(f"Hyper Parameter {key} failed to update due to {e}")

    def delete_hyper_parameters(
        self,
        hyper_parameters: Union[List[str], List[int]],
    ) -> None:
        """
        Deletes the hyper parameters used for the specified model.

        :param hyper_parameters: The hyper_parameter ids or keys

        :return: None
        """
        properties = {prop.key: prop.id for prop in self._client.list_model_version_properties(self.id).list}
        for parameter in hyper_parameters:
            if isinstance(parameter, int):
                parameter_id = parameter
            elif isinstance(parameter, str):
                parameter_id = properties[parameter]
            else:
                raise ValueError(f"{parameter} could not be found. Please check the value.")
            try:
                self._client.delete_model_version_properties(self.id, parameter_id, self.model.id)
            except Exception as e:
                logging.warning(f"Hyper Parameter {parameter} failed to delete due to {e}")

    def list_hyper_parameters(self) -> Dict[str, Any]:
        """
        List the model version hyper parameters.

        :return: A Dict of hyper_parameters
        """
        return {prop.key: prop.value for prop in self._client.list_model_version_properties(self.id).list}

    def update_metrics(
        self,
        metrics: Dict[str, int],
    ) -> None:
        """
        Update the metrics used for the specified model version

        :param metrics: The metrics e.g metric_key: value = {'metric_key': 1} OR metric_id: value = {12: 32}

        :return: None
        """
        metrics_reference = {
            metric.key: metric.id for metric in self._client.list_model_version_metrics(self.id).list if metric.id
        }
        for key, value in metrics.items():
            if metrics.get(key):
                try:
                    metric_id = metrics_reference[key]
                    metric_values = Metric(key, value)
                    self._client.update_model_version_metrics(
                        self.model.id, self.id, metric_id, [MetricInput(metric_values.key, metric_values.value)]
                    )
                except Exception as e:
                    logging.warning(f"Metric {key} failed to update due to {e}")

    def attach_model_files(self, model_object: BinaryIO) -> None:
        """
        Saves the specified model as an object to be reused.

        :param model_object: The model to save
        :return: None
        """
        attachment = [("file", (model_object.name, model_object))]
        self._client.create_attachments("modelversion", attachment, self.id)
