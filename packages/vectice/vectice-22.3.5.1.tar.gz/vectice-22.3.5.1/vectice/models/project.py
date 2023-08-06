from __future__ import annotations

import logging
from typing import Optional, List, TYPE_CHECKING

from vectice.api.json import (
    JobType,
    ModelType,
    DatasetInput,
    ModelInput,
    JobInput,
    CodeVersionInput,
    Page,
    StageInput,
    StageStatus,
    StageOrigin,
)
from .code_version import CodeVersion
from .connection import Connection
from .data_resource import DataResource
from .dataset import Dataset
from .git_version import GitVersion
from .integration import AbstractIntegration
from .job import Job
from .model import Model
from .stage import Stage

if TYPE_CHECKING:
    from vectice import Reference
    from vectice.models import Workspace


class Project:
    """
    A project contains resources relative to a specific project.

    A project can contain :

    + documentation describing the project (goals, status, ...)
    + several datasets,
    + several models
    + several jobs

    A project can contains several datasets. Each datasets contains its own history.
    This is the same for models and jobs.

    """

    def __init__(
        self,
        id: int,
        workspace: Workspace,
        name: str,
        description: Optional[str] = None,
    ):
        """

        :param id: Project identifier
        :param workspace: the workspace reference this project belong to
        :param name: Name of the project
        :param description: Quick description of the project
        """
        self._id = id
        self._workspace = workspace
        self._name = name
        self._description = description
        self._client = workspace._client
        self._integration_client: Optional[AbstractIntegration] = workspace._integration_client
        self._logger = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        return f"Project(name={self.name}, id={self.id}, description={self.description}, workspace={self.workspace})"

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Updates the information of the project.

        :param name: The name of the project.
        :param description: the description of the project

        :return: None
        """
        pass

    @property
    def id(self) -> int:
        """
        Project identifier.
        :return: int
        """
        return self._id

    @property
    def workspace(self) -> Workspace:
        """
        The workspace object this project belong to.
        :return: Workspace
        """
        return self._workspace

    @property
    def name(self) -> str:
        """
        Name of the project.
        :return: str
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """
        Quick description of the project.
        :return: Optional[str]
        """
        return self._description

    def delete(self) -> None:
        """
        Indicates if the current project is deleted

        :return: None
        """
        pass

    def list_jobs(
        self,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[Job]:
        """
        Lists the jobs in this project

        The search parm helps filter the jobs depending on the name given.

        :param search: The name to search
        :param page_index: The page index
        :param page_size: The page size

        :return: List of Jobs
        """
        outputs = self._client.list_jobs(self.id, None, search, page_index, page_size)
        return [Job(item.name, item.id, self, item.description, item.type) for item in outputs.list]

    def delete_job(self, job: Reference) -> None:
        """
        Deletes the specified job in the current project.

        :param job: The job name or id

        :return: None
        """
        item = self._client.get_job(job, self.id)
        self._logger.info(f"Job with id: {item.id} successfully deleted.")
        self._client.delete_job(job, self.id)

    def get_job(self, job: Reference) -> Job:
        """
        Gets a job.

        :param job: The job name or id

        :return: A Job or None if not found
        """
        item = self._client.get_job(job, self.id)
        self._logger.info(f"Job with id: {item.id} successfully retrieved.")
        return Job(item.name, item.id, self, item.description, item.type)

    def create_job(
        self,
        name: str,
        description: Optional[str] = None,
        type: JobType = JobType.OTHER,
    ) -> Job:
        """
        Create a new job in the project with the given attributes.

        The name is required and must be unique in the project.

        The default job type is `OTHER`. check the :class:`JobType` for other possible values.

        :param name: name of the job
        :param description: quick description of the job
        :param type: the type of the job

        :return: the newly created Job
        """
        data = JobInput(name, description, type)
        output = self._client.create_job(data, self.id)
        self._logger.info(f"Job with id: {output.id} successfully created.")
        return Job(output.name, output.id, self, output.description, output.type)

    def update_job(
        self,
        job: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[JobType] = None,
    ) -> Job:
        """
        Update the specified job with the new attribute values.

        :param job: The name or identifier of the job to update
        :param name: The name of the job
        :param description: The description of the job
        :param type: The job type

        :return: Job
        """
        data = self._client.get_job(job, self.id)
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if type is not None:
            data["type"] = type
        output = self._client.update_job(data, self.id)
        self._logger.info(f"Job with id: {output.id} successfully updated.")
        return Job(output.name, output.id, self, output.description, output.type)

    def list_datasets(self, search: Optional[str] = None, page_index: int = 1, page_size: int = 20) -> List[Dataset]:
        """
        Lists the datasets of this project.

        The search param filter the datasets with the specified name.

        :param search: The dataset to search
        :param page_index:
        :param page_size:

        :return: List of Datasets
        """
        outputs = self._client.list_datasets(self.id, None, search, page_index, page_size)
        return [
            Dataset(
                item.name,
                item.id,
                self,
                item.description,
                Connection(
                    item.connection.id,
                    item.connection.name,
                    self.workspace,
                    item.connection.type,
                    item.connection.parameters,
                    item.connection.description,
                )
                if item.connection is not None
                else None,
            )
            for item in outputs.list
        ]

    def get_dataset(self, dataset: Reference) -> Dataset:
        """
        Gets a dataset.

        :param dataset: dataset name or id

        :return: A Dataset or None if not found
        """
        dataset_output = self._client.get_dataset(dataset, self.id, self.workspace.id)
        if dataset_output.connection_id is not None:
            connection_output = self._client.get_connection(dataset_output.connection_id, self.workspace.id)
            connection = Connection(
                id=connection_output.id,
                name=connection_output.name,
                workspace=self.workspace,
                type=connection_output.type,
                parameters=connection_output.parameters,
                description=connection_output.description,
            )
        else:
            connection = None
        self._logger.info(f"Dataset with id: {dataset_output.id} successfully retrieved.")
        return Dataset(
            dataset_output.name,
            dataset_output.id,
            project=self,
            description=dataset_output.description,
            connection=connection,
        )

    def create_dataset(
        self,
        name: str,
        pattern: str = "*",
        description: Optional[str] = None,
        connection: Optional[Reference] = None,
        resources: Optional[List[str]] = None,
    ) -> Dataset:
        """
        Create a new dataset in a specific project.

        :param name: The name of the dataset
        :param pattern: The dataset pattern
        :param description: The description of the dataset
        :param connection: The connection name or id the dataset belong to
        :param resources: The file/s of the dataset version

        :return: Dataset
        """
        data = DatasetInput(
            name=name,
            pattern=pattern,
            description=description,
            connectionId=connection if isinstance(connection, int) else None,
            connectionName=connection if isinstance(connection, str) else None,
        )
        if resources is not None and len(resources) > 0:
            data["dataResources"] = [DataResource.create_resource(item) for item in resources]
        dataset_output = self._client.create_dataset(data, self.id)
        if connection is not None:
            connection_output = self._client.get_connection(connection, self.workspace.id)
            connection_object = Connection(
                id=connection_output.id,
                name=connection_output.name,
                workspace=self.workspace,
                type=connection_output.type,
                parameters=connection_output.parameters,
                description=connection_output.description,
            )
        else:
            connection_object = None
        self._logger.info(f"Dataset with id: {dataset_output.id} successfully created.")
        return Dataset(
            dataset_output.name,
            dataset_output.id,
            project=self,
            description=dataset_output.description,
            connection=connection_object,
            resources=dataset_output.resources,
        )

    def update_dataset(
        self,
        dataset: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
        connection: Optional[Reference] = None,
    ) -> Dataset:
        """
        Updates a dataset. The connection is associated with the resources, e.g gcs connection for a gcs resource.

        :param dataset: dataset name or id
        :param name: The name of the dataset version e.g Changes 'Version 1' to 'name'
        :param description: The description of the dataset version
        :param connection: The connection name or id

        :return: Dataset
        """
        dataset_output = self._client.get_dataset(dataset, self.id, self.workspace.id)
        if name is not None:
            dataset_output["name"] = name
        if description is not None:
            dataset_output["description"] = description
        if connection is not None:
            connection_output = self._client.get_connection(connection, self.workspace.id)
            dataset_output["connectionId"] = connection_output.id
            connection_object = Connection(
                id=connection_output.id,
                name=connection_output.name,
                workspace=self.workspace,
                type=connection_output.type,
                parameters=connection_output.parameters,
                description=connection_output.description,
            )
        else:
            connection_object = None
        dataset_output = self._client.update_dataset(dataset_output, dataset, self.id, self.workspace.id)
        self._logger.info(f"Dataset with id: {dataset_output.id} successfully updated.")
        return Dataset(
            dataset_output.name,
            dataset_output.id,
            project=self,
            description=dataset_output.description,
            connection=connection_object,
        )

    def delete_dataset(self, dataset: Reference) -> None:
        """
        Deletes the dataset with the specified reference.

        :param dataset: The dataset name or id

        :return: None
        """
        dataset_id = self._client.get_dataset(dataset, self.id, self.workspace.id).id
        self._logger.info(f"Dataset with id: {dataset_id} successfully deleted.")
        self._client.delete_dataset(dataset, self.id, self.workspace.id)

    def create_model(
        self,
        name: str,
        description: Optional[str] = None,
        type: Optional[ModelType] = ModelType.OTHER,
    ) -> Model:
        """
        Creates a new model in the specified project.
        :param name: The name of the model
        :param description: The description of the model
        :param type: The model type e.g

        :return: A Model
        """
        data = ModelInput(name=name, description=description, type=type)
        model_output = self._client.create_model(data, self.id)
        self._logger.info(f"Model with id: {model_output.id} successfully created.")
        return Model(model_output.name, model_output.id, self, model_output.description, ModelType[model_output.type])

    def update_model(
        self,
        model: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[ModelType] = ModelType.OTHER,
    ) -> Model:
        """
        Updates a model with the new attribute values.

        :param model: the name or identifier of the model to update
        :param name: The name of the model
        :param description: The description of the model
        :param type: The model type

        :return: Model
        """
        data = ModelInput(name=name, description=description, type=type)
        model_output = self._client.update_model(data, model, self.id)
        self._logger.info(f"Model with id: {model_output.id} successfully updated.")
        return Model(model_output.name, model_output.id, self, model_output.description, ModelType[model_output.type])

    def list_models(
        self, search: Optional[str] = None, page_index: int = Page.index, page_size: int = Page.size
    ) -> List[Model]:
        """
        Lists the models of the project

        The search param helps find the models with the specified name.

        :param search: The model to search
        :param page_index: The page index
        :param page_size:The page size

        :return: List of Models
        """
        outputs = self._client.list_models(self.id, None, search, page_index, page_size)
        return [Model(item.name, item.id, self, item.description, ModelType[item.type]) for item in outputs.list]

    def get_model(self, model: Reference) -> Model:
        """
        Gets a model from the specified project.

        :param model: The model name or id
        :return: A Model or None if not found
        """
        model_output = self._client.get_model(model, self.id)
        self._logger.info(f"Model with id: {model_output.id} successfully retrieved.")
        return Model(model_output.name, model_output.id, self, model_output.description, ModelType[model_output.type])

    def delete_model(self, model: Reference) -> None:
        """
        Deletes the model with the specified reference.

        :param model: The model name or id
        :return: None
        """
        model_id = self._client.get_model(model, self.id).id
        self._logger.info(f"Model with id: {model_id} successfully deleted.")
        self._client.delete_model(model, self.id)

    def create_code_version(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        uri: Optional[str] = None,
        is_starred: Optional[bool] = None,
        git_version: Optional[GitVersion] = None,
    ) -> CodeVersion:
        """
        Gets a specific version of this code.

        :param name: The version name or id
        :param description: A quick description of the code version
        :param uri: The uri of the code
        :param is_starred: If the code version is starred
        :param git_version: The git version of the code version

        :return: A CodeVersion or None if the version does not exist
        """
        logging.getLogger("Client").propagate = False
        code_version_input = CodeVersionInput(
            name=name,
            description=description,
            uri=uri,
            is_starred=is_starred,
            gitVersion=git_version,
        )
        code_version_output = self._client.create_code_version(code_version_input, self.id)
        code_name = self._client.get_code(code_version_output.code_id).name
        logging.getLogger("Client").propagate = True
        self._logger.info(f"CodeVersion with id: {code_version_output.id} successfully created in Code {code_name}.")
        return CodeVersion(
            project=self,
            id=code_version_output.id,
            name=code_version_output.name,
            description=code_version_output.description,
            version_number=code_version_output.version_number,
            uri=code_version_output.uri,
            is_starred=code_version_output.is_starred,
            git_version=GitVersion(
                repositoryName=code_version_output.git_version.repository_name,
                branchName=code_version_output.git_version.branch_name,
                isDirty=code_version_output.git_version.is_dirty,
                commitHash=code_version_output.git_version.commit_hash,
                commitComment=code_version_output.git_version.commit_comment,
                entrypoint=code_version_output.git_version.entrypoint,
                commitAuthorName=code_version_output.git_version.commit_author_name,
                commitAuthorEmail=code_version_output.git_version.commit_author_email,
                uri=code_version_output.git_version.uri,
            )
            if code_version_output.git_version is not None
            else None,
            version=code_version_output.version,
            code_id=code_version_output.code_id,
        )

    def get_code_version(
        self,
        version: Reference,
    ) -> CodeVersion:
        """
        Gets a specific version of this code.

        :param version: The version name or id

        :return: A CodeVersion or None if the version does not exist
        """
        logging.getLogger("Client").propagate = False
        code_version_output = self._client.get_code_version(version, self.id)
        code_name = self._client.get_code(code_version_output.code_id, self.id, self.workspace.id).name
        logging.getLogger("Client").propagate = True
        self._logger.info(
            f"CodeVersion with id: {code_version_output.id} successfully retrieved from Code {code_name}."
        )
        return CodeVersion(
            project=self,
            id=code_version_output.id,
            name=code_version_output.name,
            version_number=code_version_output.version_number,
            description=code_version_output.description,
            attachments="",
            is_starred=code_version_output.is_starred,
            version=code_version_output.version,
            git_version=GitVersion(
                repositoryName=code_version_output.git_version.repository_name,
                branchName=code_version_output.git_version.branch_name,
                isDirty=code_version_output.git_version.is_dirty,
                commitHash=code_version_output.git_version.commit_hash,
                commitComment=code_version_output.git_version.commit_comment,
                entrypoint=code_version_output.git_version.entrypoint,
                commitAuthorName=code_version_output.git_version.commit_author_name,
                commitAuthorEmail=code_version_output.git_version.commit_author_email,
                uri=code_version_output.git_version.uri,
            )
            if code_version_output.git_version is not None
            else None,
        )

    def list_code_versions(
        self, search: Optional[str] = None, page_index: int = 1, page_size: int = 20
    ) -> List[CodeVersion]:
        """
        Lists the code versions.

        Returns a List of the code Versions associated with the project.
        The CodeVersion can be used in runs or experiments.

        :param search: The name that contains the code versions
        :param page_index: The page index
        :param page_size: The page size

        :return: List of CodeVersions
        """

        code_version_output_list = self._client.list_code_versions(self.id, None, search, page_index, page_size)
        return [
            CodeVersion(
                project=self,
                id=code_version_output.id,
                name=code_version_output.name,
                version_number=code_version_output.version_number,
                description=code_version_output.description,
                is_starred=code_version_output.is_starred,
                git_version_id=code_version_output.git_version_id,
                version=code_version_output.version,
            )
            for code_version_output in code_version_output_list
        ]

    def update_code_version(
        self,
        version: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_starred: Optional[bool] = None,
        uri: Optional[str] = None,
        git_version: Optional[GitVersion] = None,
    ) -> CodeVersion:
        """
        Updates a code version.

        :param version: The code version name or id
        :param name: The name of the code version e.g Changes 'Version 1' to 'name'
        :param description: The description of the code version
        :param is_starred: Whether the dataset version is starred
        :param uri: The uri of the code version
        :param git_version: The GitVersion of the code version
        :return: The updated code version
        """
        logging.getLogger("Client").propagate = False
        code_version_object = self._client.get_code_version(version, self.id)
        if code_version_object is None:
            raise ValueError("The code version was not found. Please check the reference.")
        code_version_input = CodeVersionInput(
            name=name, description=description, isStarred=is_starred, uri=uri, GitVersion=git_version
        )
        code_version_output = self._client.update_code_version(code_version_input, code_version_object.id, self.id)
        code_name = self._client.get_code(code_version_output.code_id).name
        logging.getLogger("Client").propagate = True
        self._logger.info(f"CodeVersion with id: {code_version_output.id} successfully updated in Code {code_name}.")
        return CodeVersion(
            project=self,
            id=code_version_output.id,
            name=code_version_output.name,
            version_number=code_version_output.version_number,
            description=code_version_output.description,
            is_starred=code_version_output.is_starred,
            version=code_version_output.version_number,
            git_version_id=code_version_output.git_version_id,
        )

    def delete_code_version(
        self,
        version: Reference,
    ) -> None:
        """
        Deletes a specific code version.

        :param version: The code version name or id
        :return: None
        """
        self._client.delete_code_version(version, self.id)

    def create_stage(self, name: Optional[str] = None, status: Optional[StageStatus] = StageStatus.NotStarted) -> Stage:
        """
        Add a stage to the project. A documentation page is created with the title provided. The status can be 'Draft/InProgress/Completed'.

        :param name: The name of the stages documentation page.
        :param status: The status of the stage.

        :return: A Stage object
        """
        data = StageInput(name=name, status=status)
        stage_output = self._client.create_stage(data, self.id)
        self._logger.info(f"Stage '{stage_output.name}' created.")
        return Stage(
            stage_output.id,
            self,
            stage_output.name,
            StageStatus["InProgress" if stage_output.status == "Draft" else stage_output.status],
            StageOrigin[stage_output.origin],
        )

    def update_stage(
        self, stage: Reference, name: Optional[str] = None, status: Optional[StageStatus] = StageStatus.NotStarted
    ) -> Stage:
        """
        Update a stage of the project. A documentation page is updated with the title and status provided. The status can be 'Draft/InProgress/Completed'.

        :param stage: The name or id of the stage.
        :param name: The name of the stages documentation page.
        :param status: The status of the stage.

        :return: A Stage object
        """
        data = StageInput(name=name, status=status)
        stage_output = self._client.update_stage(stage, data, self.id)
        self._logger.info(f"Stage '{stage_output.name}' updated.")
        return Stage(
            stage_output.id,
            self,
            stage_output.name,
            "InProgress" if stage_output.status == "Draft" else StageStatus[stage_output.status],
            StageOrigin[stage_output.origin],
        )

    def get_stage(self, stage: Reference) -> Stage:
        """
        Get a stage of the project. A stage will be returned.

        :param stage: The name or id of the stage.

        :return: Stage
        """
        stage_output = self._client.get_stage(stage, self.id)
        self._logger.info(f"Stage '{stage_output.name}' retrieved.")
        return Stage(
            stage_output.id,
            self,
            stage_output.name,
            StageStatus["InProgress" if stage_output.status == "Draft" else stage_output.status],
            StageOrigin[stage_output.origin],
        )

    def list_stages(
        self, search: Optional[str] = None, page_index: int = Page.index, page_size: int = Page.size
    ) -> List[Stage]:
        """
        List all the stages of the project. A search term can be used.

        :param search: The search term to be used.

        :return: A list of stages
        """
        outputs = self._client.list_stages(self.id, None, search, page_index, page_size)
        self._logger.info("Stages successfully retrieved.")
        return [
            Stage(
                item.id,
                self,
                item.name,
                StageStatus["InProgress" if item.status == "Draft" else item.status],
                StageOrigin[item.origin],
            )
            for item in outputs
        ]

    def delete_stage(self, stage: Reference) -> None:
        """
        Delete a stage of the project. A documentation page related to the stage will be deleted aswell.

        :param stage: The name or id of the stage.

        :return: None
        """
        self._client.delete_stage(stage, self.id)
        self._logger.info(f"Stage '{stage}' successfully deleted.")
