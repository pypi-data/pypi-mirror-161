from __future__ import annotations

import logging
import os.path
from typing import Optional, List, Union, Dict, BinaryIO, Any, TYPE_CHECKING

from vectice.api import BadReferenceError, Client
from vectice.api.json import (
    ModelType,
    JobType,
    ModelVersionStatus,
    WorkspaceInput,
    RunStatus,
    JobArtifactType,
    ArtifactType,
    FileMetadata,
    Page,
    StageStatus,
    VersionStrategy,
)
from vectice.api.reference import Reference, MissingReferenceError, InvalidReferenceError
from vectice.integrations import IntegrationFactory
from vectice.models import (
    Workspace,
    Project,
    Job,
    ModelVersion,
    Run,
    Dataset,
    DatasetVersion,
    Connection,
    Model,
    CodeVersion,
    GitVersion,
    ArtifactReference,
    Stage,
)
from vectice.models.integration import AbstractIntegration
from .__version__ import __version__
from .api.json.connection_type import ConnectionType
from .models.dataset_metadata import DatasetMetadata

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from botocore.session import Session


class Vectice:
    """
    High level class to list jobs and runs but also save runs

    The ability to toggle the autocode feature is enabled with the autocode argument. If autocode=True,
    Vectice will capture code artifacts relative to the .git file where you are executing your code. More can be found
    in the documentation at doc.vectice.com
    """

    def __init__(
        self,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
        user_token: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        lib: Optional[object] = None,
        allow_self_signed_certificate: bool = True,
        auto_log: bool = False,
    ):
        self._active_runs: Dict[int, Run] = {}
        logging.getLogger("Client").propagate = True
        self._client = Client(workspace, project, user_token, api_endpoint, True, allow_self_signed_certificate)
        self._auto_document_run = False
        self._document_stage: Optional[str] = None
        self._document_stage = None
        self._document_run = False
        logging.getLogger("Client").propagate = False
        self._logger = logging.getLogger(self.__class__.__name__)
        compatibility = self._client.check_compatibility()
        if compatibility.status != "OK":
            if compatibility.status == "Error":
                print(f"compatibility error : {compatibility.message}")
                self._logger.error(f"compatibility error : {compatibility.message}")
                raise RuntimeError(f"compatibility error : {compatibility.message}")
            else:
                print(f"compatibility warning : {compatibility.message}")
                self._logger.warning(f"compatibility warning : {compatibility.message}")
        try:
            self._integration_client: Optional[AbstractIntegration] = IntegrationFactory.create_adapter(
                lib=lib, vectice_client=self._client, auto_log=auto_log
            )
        except RuntimeError as e:
            self._logger.debug(f"Runtime {e}")
            self._integration_client = None

    def __repr__(self) -> str:
        lib = self._integration_client
        return (
            "Vectice("
            + f"workspace={self._client.workspace.name if self._client.workspace else 'None'}, "
            + f"project={self._client.project.name if self._client.project else 'None'}, "
            + f"api_endpoint={self._client._auth.api_base_url}, "
            + f"lib={lib.lib_name() if lib is not None else 'None'})"
        )

    @property
    def version(self) -> str:
        return __version__

    @property
    def project(self) -> Optional[Project]:
        if self._client.project is not None and self._client.workspace is not None and self.workspace is not None:
            result = Project(
                self._client.project.id, self.workspace, self._client.project.name, self._client.project.description
            )
            return result
        else:
            return None

    @property
    def workspace(self) -> Optional[Workspace]:
        if self._client.workspace is not None:
            result = Workspace(
                self._client.workspace.id, self._client.workspace.name, self._client.workspace.description
            )
            result.__post_init__(self._client, self._integration_client)
            return result
        else:
            return None

    def _get_parent_project(self, project, workspace) -> Project:
        if project is None and self.project is not None:
            project = self.project.id
        else:
            if project is None:
                raise MissingReferenceError("project")
            if isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        project_output = self._client.get_project(project, workspace)
        workspace_output = self._client.get_workspace(project_output.workspace_id)
        parent_workspace = Workspace(workspace_output.id, workspace_output.name, workspace_output.description)
        parent_workspace.__post_init__(self._client, self._integration_client)
        return Project(project_output.id, parent_workspace, project_output.name, project_output.description)

    def list_workspaces(
        self,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[Workspace]:
        """
        List workspaces.

        Lists the workspaces the user have access to with it's user connection.

        :return: List of Workspaces
        """
        outputs = self._client.list_workspaces(search, page_index, page_size)
        results = [Workspace(id=output.id, name=output.name, description=output.description) for output in outputs.list]
        for workspace in results:
            workspace.__post_init__(self._client, self._integration_client)
        return results

    def update_workspace(
        self, workspace: Reference, name: Optional[str] = None, description: Optional[str] = None
    ) -> Workspace:
        """
        Update workspace

        :param workspace:
        :param name:
        :param description:
        :return: the updated workspace
        """
        output = self._client.update_workspace(WorkspaceInput(name, description), workspace)
        result = Workspace(id=output.id, name=output.name, description=output.description)
        result.__post_init__(self._client, self._integration_client)
        self._logger.info(f"Workspace with id: {result.id} successfully updated.")
        return result

    def get_workspace(self, workspace: Reference) -> Workspace:
        """


        Gets the workspace with the specified reference (workspace name or id).

        :param workspace: The workspace name or id the user wants to access

        :return: Workspace
        """
        output = self._client.get_workspace(workspace)
        result = Workspace(output.id, output.name, output.description)
        result.__post_init__(self._client, self._integration_client)
        self._logger.info(f"Workspace with id: {result.id} successfully retrieved.")
        return result

    def get_project(self, project: Optional[Reference] = None, workspace: Optional[Reference] = None) -> Project:
        """
        Gets a project instance with the specified project name or id. If the user have the project id,
        it is enough to get the project otherwise the workspace should also be specified.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.

        :return: A Project
        """
        if project is None and self.project is not None:
            return self.project
        else:
            if project is None:
                raise MissingReferenceError("project")
            if isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        project_output = self._client.get_project(project, workspace)
        workspace_output = self._client.get_workspace(project_output.workspace_id)
        parent_workspace = Workspace(workspace_output.id, workspace_output.name, workspace_output.description)
        parent_workspace.__post_init__(self._client, self._integration_client)
        self._logger.info(f"Project with id: {project_output.id} successfully retrieved.")
        return Project(project_output.id, parent_workspace, project_output.name, project_output.description)

    # def get_job(self, job: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None):
    #     job_output = self._client.get_job(job, project, workspace)
    #     project_output = self._client.get_project(job_output.project_id)
    #     workspace_object = Workspace(
    #         project_output.workspace.id, project_output.workspace.name, project_output.workspace.description
    #     )
    #     workspace_object.__post_init__(self._client)
    #     project_object = Project(
    #         project_output.id,
    #         workspace_object,
    #         project_output.name,
    #         project_output.description,
    #     )
    #     return Job(
    #         job_output.name,
    #         job_output.id,
    #         project_object,
    #         job_output.description,
    #         job_output.type,
    #     )

    def get_model(self, model: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None):
        """
        Gets a model from the specified project.

        :param model: The model name or id
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.

        :return: A Model
        """
        if isinstance(model, int):
            model_output = self._client.get_model(model)
            if model_output is None:
                raise InvalidReferenceError("version", model)
            project_object = self._get_parent_project(model_output.project_id, workspace)
        elif isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            if isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
            if project is None:
                raise MissingReferenceError("model", "project")
            project_object = self._get_parent_project(project, workspace)
        else:
            raise MissingReferenceError("model", "model")
        return project_object.get_model(model)

    def get_dataset(
        self, dataset: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> Dataset:
        """
        Get a dataset.

        Gets a specific dataset from the specified project.

        :param dataset: dataset name or id
        :param project: The project name or id to get.
        :param workspace: The workspace name or id the project belongs to

        :return: A Dataset
        """
        if isinstance(dataset, int):
            dataset_output = self._client.get_dataset(dataset)
            if dataset_output is None:
                raise InvalidReferenceError("version", dataset)
            project_object = self._get_parent_project(dataset_output.project_id, workspace)
        elif isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            if isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
            if project is None:
                raise MissingReferenceError("dataset", "project")
            project_object = self._get_parent_project(project, workspace)
        else:
            raise MissingReferenceError("dataset", "model")
        return project_object.get_dataset(dataset)

    def update_project(
        self,
        project: Reference,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Project:
        """
        Updates the information of a project.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to update.
        :param name: The name of the project to be created.
        :param description: The description of the project to be created.

        :return: Project
        """
        if project is None and self.project is not None:
            return self.project
        else:
            if project is None:
                raise MissingReferenceError("project")
            if isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
        project_output = self._client.get_project(project, workspace)
        workspace_output = self._client.get_workspace(project_output.workspace_id)
        parent_workspace = Workspace(workspace_output.id, workspace_output.name, workspace_output.description)
        parent_workspace.__post_init__(self._client, self._integration_client)
        return parent_workspace.update_project(project, name, description)

    def create_model_version(
        self,
        name: str,
        model: Reference,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
        description: Optional[str] = None,
        status: Optional[ModelVersionStatus] = ModelVersionStatus.EXPERIMENTATION,
        algorithm: Optional[str] = None,
        is_starred: Optional[bool] = False,
        metrics: Optional[Dict] = None,
        hyper_parameters: Optional[Dict] = None,
        attachments: Optional[List[str]] = None,
    ) -> ModelVersion:
        """
        Create a new model version.

        Creates a new model version with all the existing params in Vectice.

        :param model:
        :param name: The name of the model
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param description: The description of the model
        :param algorithm: The algorithm the model version uses
        :param is_starred: Whether the model is starred or not
        :param metrics: The model version metrics
        :param hyper_parameters: The model version hyper parameters

        :return: A ModelVersion
        """
        logging.getLogger("Project").propagate = False
        model_object = self.get_model(model, project, workspace)
        logging.getLogger("Project").propagate = True
        version: ModelVersion = model_object.create_model_version(
            name,
            description,
            status,
            algorithm,
            is_starred,
            metrics,
            hyper_parameters,
            None,
        )
        if attachments is not None:
            version.add_attachments(attachments)
        return version

    def create_gcs_dataset(
        self,
        uri: Union[str, List[str]],
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        service_account_json_path: Optional[str] = None,
    ) -> Optional[DatasetVersion]:
        """
        Create a Google Cloud Storage dataset version using an uri. Creates a Google Cloud Storage resource attached to the dataset version.
        The uri is found in the google cloud console in the Google Cloud Storage tab.

        Example:
        File level :  bucket_name/folder_name/file_name.csv (Attach the file)
        Folder level: bucket_name/folder_name (Attaches everything in the the folder)
        List : ['bucket_name/folder_name/file_name.csv', 'bucket_name/folder_name']

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to update.
        :param uri: The uri list of the Google Cloud Storage resources that will be used to create a dataset version
        :param name: The dataset name
        :param description: The description of the dataset version
        :return: A DatasetMetadataArtifact that can be used in runs as an input or output
        """

        def normalize_name(text: str) -> str:
            text = text.split("/")[-1]
            return text

        if name is None:
            if isinstance(uri, str):
                name = normalize_name(uri)
            else:
                name = normalize_name(os.path.commonprefix(uri))

        if project is None and self.project is not None:
            project = self.project.id
        else:
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project", project)
        parent_project = self._get_parent_project(project, workspace)
        try:
            dataset = parent_project.get_dataset(name)
        except BadReferenceError:
            dataset = parent_project.create_dataset(
                name,
                description=description,
            )
        metadata = DatasetMetadata.create_gcs(uri, service_account_json_path)
        dataset_version = dataset.create_dataset_version(
            metadata=metadata, description=description, version_strategy=VersionStrategy.AUTOMATIC
        )
        return dataset_version

    def create_bigquery_dataset(
        self,
        uri: str,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        service_account_json_path: Optional[str] = None,
    ) -> Optional[DatasetVersion]:
        """
        Create a bigquery dataset version using an uri. Creates a BigQuery resource attached to the dataset version. The uri
        can be found in the table or dataset info.

        Example:
        Tables level : "Project_Name/Dataset_Name/Table_Name"
        Dataset level: "Project_Name/Dataset_Name"

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to update.
        :param uri: The url of the BigQuery dataset version that will be created
        :param name: The dataset name
        :param description: The description of the dataset version
        :return: A DatasetMetadataArtifact that can be used in runs as an input or output
        """

        def normalize_name(text: str) -> str:
            text = text.split("/")[-1]
            return text

        if name is None:
            if isinstance(uri, str):
                name = normalize_name(uri)
            else:
                name = normalize_name(os.path.commonprefix(uri))

        if project is None and self.project is not None:
            project = self.project.id
        else:
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project", project)
        parent_project = self._get_parent_project(project, workspace)
        try:
            dataset = parent_project.get_dataset(name)
        except BadReferenceError:
            dataset = parent_project.create_dataset(
                name,
                description=description,
            )
        metadata = DatasetMetadata.create_bigquery(uri, service_account_json_path)
        dataset_version = dataset.create_dataset_version(
            metadata=metadata, description=description, version_strategy=VersionStrategy.AUTOMATIC
        )
        return dataset_version

    def create_s3_dataset(
        self,
        uri: str,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        botocore_session: Optional[Session] = None,
    ) -> Optional[DatasetVersion]:
        """
        For credentials, please read AWS instructions at https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
        As describe the AWS client also support environment variables `AWS_ACCESS_KEY_ID `, `AWS_SECRET_ACCESS_KEY` and `AWS_SESSION_TOKEN`.
        It also support credentials file in `~/.aws/credentials`.

        :param uri: list of files/folders to be used for the dataset. the metadata will be extracted from this list.
        :type aws_access_key_id: string
        :param aws_access_key_id: AWS access key ID
        :type aws_secret_access_key: string
        :param aws_secret_access_key: AWS secret access key
        :type aws_session_token: string
        :param aws_session_token: AWS temporary session token
        :type region_name: string
        :param region_name: Default region when creating new connections
        :type profile_name: string
        :param profile_name: The name of a profile to use. If not given, then
                             the default profile is used.
        :type botocore_session: botocore.session.Session
        :param botocore_session: Use this Botocore session instead of creating
                                 a new default one.
        :param uri:
        :param project:
        :param workspace:
        :param name:
        :param description:
        :return:
        """

        def normalize_name(text: str) -> str:
            text = text.split("/")[-1]
            return text

        if name is None:
            if isinstance(uri, str):
                name = normalize_name(uri)
            else:
                name = normalize_name(os.path.commonprefix(uri))

        if project is None and self.project is not None:
            project = self.project.id
        else:
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project", project)
        parent_project = self._get_parent_project(project, workspace)
        try:
            dataset = parent_project.get_dataset(name)
        except BadReferenceError:
            dataset = parent_project.create_dataset(
                name,
                description=description,
            )
        metadata = DatasetMetadata.create_s3(
            uri,
            aws_access_key_id,
            aws_secret_access_key,
            aws_session_token,
            profile_name,
            region_name,
            botocore_session,
        )
        dataset_version = dataset.create_dataset_version(
            metadata=metadata, description=description, version_strategy=VersionStrategy.AUTOMATIC
        )
        return dataset_version

    def create_project(
        self, name: str, workspace: Optional[Reference] = None, description: Optional[str] = None
    ) -> Project:
        """
        Creates a new project in a workspace with the specified name. If no workspace name is given the project is created in the default workspace.

        :param workspace: The workspace name or id in which the project should be created.
        :param name: The name of the project to be created.
        :param description: The description of the project to be created.

        :return: Project
        """
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if workspace is None:
            raise MissingReferenceError("workspace", workspace)
        workspace_output = self._client.get_workspace(workspace)
        parent_workspace = Workspace(workspace_output.id, workspace_output.name, workspace_output.description)
        parent_workspace.__post_init__(self._client, self._integration_client)
        return parent_workspace.create_project(name, description)

    def delete_project(
        self,
        project: Reference,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the project specified by the user.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to delete.

        :return: None
        """
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id

        if workspace is not None:
            workspace_output = self._client.get_workspace(workspace)
            parent_workspace = Workspace(workspace_output.id, workspace_output.name, workspace_output.description)
            parent_workspace.__post_init__(self._client, self._integration_client)
            parent_workspace.delete_project(project)
        elif isinstance(project, int):
            project_instance = self._get_parent_project(project, None)
            project_instance.delete()  # This line is not working
        else:
            raise InvalidReferenceError("project", project)

    def list_projects(
        self,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[Project]:
        """
        Lists the projects available in the specified workspace. If No workspace reference(name or id) is given, the default workspace is selected.

        :param workspace: The workspace name or id the projects belong to
        :param search: The name to search
        :param page_index: The page index
        :param page_size: The page size
        :return: List of Projects
        """
        workspace_object = self.workspace if workspace is None else self.get_workspace(workspace)
        if workspace_object is None:
            raise InvalidReferenceError("workspace", workspace)

        return workspace_object.list_projects(search, page_index, page_size)

    def create_dataset(
        self,
        name: str,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        pattern: str = "*",
        description: Optional[str] = None,
        connection: Optional[Reference] = None,
        resources: Optional[List[str]] = None,
    ) -> Dataset:
        """
        Create a new dataset

        Creates a new dataset in a specific project. File/s and folder/s create resource/s associated with a dataset version
        that will belong to the created dataset.

        :param name: The name of the dataset
        :param project: The project name or id
        :param workspace: The workspace name or id
        :param pattern: The dataset pattern
        :param description: The description of the dataset
        :param properties: The properties of the dataset version
        :param connection: The connection name or id the dataset belong to
        :param resources: The file/s of the dataset version

        :return: Dataset
        """
        if project is None and self.project is not None:
            project = self.project.id
            workspace = None
        elif isinstance(project, str) and workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.create_dataset(name, pattern, description, connection, resources)

    def create_job(
        self,
        name: str,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        description: Optional[str] = None,
        type: JobType = JobType.OTHER,
    ) -> Job:
        """
        Create a new job in the project with the given attributes.

        The name is required and must be unique in the project.

        The default job type is `OTHER`. check the :class:`JobType` for other possible values.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id the job should belong to.
        :param name: name of the job
        :param description: quick description of the job
        :param type: the type of the job
        :return: the newly created job
        """
        if project is None and self.project is not None:
            project = self.project.id
            workspace = None
        elif isinstance(project, str) and workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("job", "project")
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.create_job(name, description, type)

    def list_jobs(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[Job]:
        """
        List the jobs.

        Lists the jobs in a specified project. The search parm helps filter the jobs depending on the name given.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param search: The name to search
        :param page_index: The page index
        :param page_size: The page size

        :return: List of Jobs
        """
        if project is None and self.project is not None:
            project = self.project.id
            workspace = None
        elif isinstance(project, str) and workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("job", "project")
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.list_jobs(search, page_index, page_size)

    def delete_job(
        self,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the specified job in a specific project.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param job: The job name or id

        :return: None
        """
        logging.getLogger("Project").propagate = False
        if isinstance(job, int):
            job_output = self._client.get_job(job)
            parent_project = self._get_parent_project(job_output.project_id, workspace)
            logging.getLogger("Project").propagate = True
            parent_project.delete_job(job_output.id)
        elif isinstance(job, str):
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("job", "project")
            parent_project = self._get_parent_project(project, workspace)
            job_output = parent_project._client.get_job(job)
            logging.getLogger("Project").propagate = True
            parent_project.delete_job(job_output.id)
        else:
            raise InvalidReferenceError("job", job)

    def get_job(
        self,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> Job:
        """
        Gets the specified job in a specific project.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param job: The job name or id

        :return: A Job
        """
        logging.getLogger("Project").propagate = False
        if isinstance(job, int):
            job_output = self._client.get_job(job)
            parent_project = self._get_parent_project(job_output.project_id, workspace)
        else:
            if project is None and self.project is not None:
                project = self.project.id
                workspace = None
            elif isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
            if project is None:
                raise MissingReferenceError("job", "project")
            parent_project = self._get_parent_project(project, workspace)
        logging.getLogger("Project").propagate = True
        return parent_project.get_job(job)

    def update_job(
        self,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        job_type: Optional[JobType] = None,
        description: Optional[str] = None,
    ) -> Job:
        """
        Updates the specified job with the new information.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param job: The job name or id
        :param name: The name of the job
        :param job_type: The job type
        :param description: The description of the job

        :return: None
        """
        logging.getLogger("Project").propagate = False
        if isinstance(job, int):
            job_output = self._client.get_job(job)
            parent_project = self._get_parent_project(job_output.project.id, job_output.project.workspace.id)
            job_object = Job(job_output.name, job_output.id, parent_project, job_output.description, job_output.type)
        elif isinstance(job, str):
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("job", "project")
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
            job_output = self._client.get_job(job, project, workspace)
            parent_project = self._get_parent_project(job_output.project.id, job_output.project.workspace.id)
            job_object = Job(job_output.name, job_output.id, parent_project, job_output.description, job_output.type)
        else:
            raise InvalidReferenceError("job", job)
        logging.getLogger("Project").propagate = True
        return job_object.project.update_job(job, name, description, job_type)

    def start_run(
        self,
        run: Run,
        inputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None,
    ) -> Run:
        """
        Start the run created before by calling :func:`~Vectice.create_run` function

        :param run: The runnable job to start
        :param inputs: A list of artifacts used as inputs by this run.
        :return: A reference to a run in progress
        """
        run.start(inputs)
        self._active_runs[run.id] = run
        return run

    def end_run(
        self,
        run: Run,
        outputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None,
        status: RunStatus = RunStatus.COMPLETED,
    ) -> Optional[int]:
        """
        End the current (last) active run started by :func:`~Vectice.start_run`.
        To end a specific run, use :func:`~Vectice.stop_run` instead.

        :return: Identifier of the run in Vectice if successfully saved
        """
        run.end_run(outputs, status)
        if self._auto_document_run:
            """
            Captures an existing run. That is still running.
            """
            if self._document_stage is not None:
                try:
                    stage = self.get_stage(self._document_stage)
                except Exception:
                    logger.debug(f"Stage {self._document_stage} for auto documentation not found.")
                    stage = self.create_stage(self._document_stage, status=StageStatus.InProgress)
            else:
                stage = self.create_stage(f"Auto Document {run.name}", status=StageStatus.InProgress)
            run._capture_run_info(stage)
        del self._active_runs[run.id]
        return run.id

    def create_run(
        self,
        job: Reference,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
        name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        auto_code: bool = False,
        check_remote_repository: bool = True,
    ) -> Run:
        """
        Create a run.

        Creates a run in the specified project with the information passed to this method.

        The run is not viewable in the Vectice platform until the job is started.

        See :class:`Run` for more information

        :param job: The job name or id the run belongs to
        :param workspace: The workspace name or id the run belongs to
        :param project: The project name or id the run belongs to
        :param name: The run name.
        :param properties: Properties of the run
        :param auto_code: If the run has auto code enabled
        :param check_remote_repository: If the run has the auto code, remote repository check enabled


        :return: Run
        """
        if project is None and self.project is not None:
            project = self.project.id
            workspace = None
        elif isinstance(project, str) and workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("job", "project")
        job_output = self._client.get_job(job, project, workspace)
        parent_project = self._get_parent_project(job_output.project.id, job_output.project.workspace.id)
        parent_job = Job(job_output.name, job_output.id, parent_project, job_output.description, job_output.type)
        run = parent_job.create_run(name, properties, auto_code, check_remote_repository)
        return run

    def list_runs(
        self,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[Run]:
        """
        List the runs.

        Lists the runs in a specific project.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param job: The job name or id
        :param page_index: The page index
        :param page_size: The page size

        :return: List of JobRuns
        """
        if project is None and self.project is not None:
            project = self.project.id
            workspace = None
        elif isinstance(project, str) and workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("job", "project")
        job_output = self._client.get_job(job, project, workspace)
        parent_project = self._get_parent_project(job_output.project.id, job_output.project.workspace.id)
        parent_job = Job(job_output.name, job_output.id, parent_project, job_output.description, job_output.type)
        logging.getLogger("Project").propagate = True
        return parent_job.list_runs(search, page_index, page_size)

    def delete_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the specified run in a specific project.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param run: The run name or id
        :param job: The job name or id

        :return: None
        """
        logging.getLogger("Vectice").propagate = False
        logging.getLogger("Project").propagate = False
        if isinstance(run, int):
            run_object = self.get_run(run, job)
        elif isinstance(run, str):
            if job is None:
                raise MissingReferenceError("run", "job")
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("job", "project")
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
            run_object = self.get_run(run, job, project, workspace)
        else:
            raise InvalidReferenceError("job", job)
        logging.getLogger("Project").propagate = True
        logging.getLogger("Vectice").propagate = True
        run_object.job.delete_run(run)

    def get_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> Run:
        """
        Get a Run in the specified workspace/project/job.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param job: The job name or id
        :param run: The run name or id

        :return: A Run
        """
        if isinstance(run, int):
            run_output = self._client.get_run(run, job, project, workspace)
            job_output = self._client.get_job(run_output.job_id, project, workspace)
            parent_project = self._get_parent_project(job_output.project.id, job_output.project.workspace_id)
            job_object = Job(job_output.name, job_output.id, parent_project, job_output.description, job_output.type)
            self._logger.info(f"Run with id: {run_output.id} successfully retrieved.")
            result = Run(
                id=run_output.id,
                job=job_object,
                name=run_output.name,
                system_name=run_output.system_name,
                created_date=run_output.created_date,
                start_date=run_output.start_date,
                end_date=run_output.end_date,
                status=run_output.status,
                description=run_output.description,
            )
        else:
            if job is None:
                raise MissingReferenceError("run", "job")
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("job", "project")
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
            job_output = self._client.get_job(job, project, workspace)
            parent_project = self._get_parent_project(job_output.project.id, job_output.project.workspace_id)
            job_object = Job(job_output.name, job_output.id, parent_project, job_output.description, job_output.type)
            logging.getLogger("Job").propagate = False
            result = job_object.get_run(run)
            logging.getLogger("Job").propagate = True
        artifacts = self._client.list_artifacts(result.id).list
        for artifact in artifacts:

            if artifact.artifact_type == ArtifactType.DATASET:
                logging.getLogger("Dataset").propagate = False
                artifact_version: Union[DatasetVersion, ModelVersion, CodeVersion] = self.get_dataset_version(
                    artifact.artifact_id
                )
                logging.getLogger("Dataset").propagate = True
            elif artifact.artifact_type == ArtifactType.MODEL:
                logging.getLogger("Model").propagate = False
                artifact_version = self.get_model_version(artifact.artifact_id)
                logging.getLogger("Model").propagate = False
            else:
                logging.getLogger("Project").propagate = False
                artifact_version = self.get_code_version(artifact.artifact_id)
                logging.getLogger("Project").propagate = False
            reference = ArtifactReference(
                version_id=artifact.artifact_id,
                version_name=artifact_version.name,
                version_number=artifact_version.version_number,
                dataset=artifact_version.dataset.name if isinstance(artifact_version, DatasetVersion) else None,
                model=artifact_version.model.name if isinstance(artifact_version, ModelVersion) else None,
                code=artifact_version.id if isinstance(artifact_version, CodeVersion) else None,
                description=artifact_version.description,
            )
            if artifact.job_artifact_type == JobArtifactType.INPUT:
                result._inputs.append(reference)
            else:
                result._outputs.append(reference)
        logging.getLogger("Job").propagate = True
        return result

    def update_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        system_name: Optional[str] = None,
        status: Optional[RunStatus] = None,
    ) -> Run:
        """
        Update a run.

        Updates the specified run with the new information.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param job: The job name or id
        :param run: The run name or id
        :param name: The name of the job
        :param system_name: The name of the system
        :param status: The status of the run

        :return: the updated Run
        """
        logging.getLogger("Project").propagate = False
        logging.getLogger("Dataset").propagate = False
        logging.getLogger("Vectice").propagate = False
        if isinstance(run, int):
            run_object = self.get_run(run)
        elif isinstance(run, str):
            if job is None:
                raise MissingReferenceError("run", "job")
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("job", "project")
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
            run_object = self.get_run(run, job, project, workspace)
        else:
            raise InvalidReferenceError("job", job)
        logging.getLogger("Project").propagate = True
        logging.getLogger("Dataset").propagate = True
        logging.getLogger("Vectice").propagate = True
        result: Run = run_object.job.update_run(run, name, system_name, None if status is None else status)
        return result

    def add_model_version_attachment(
        self,
        file: str,
        model_version: Reference,
        model: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> None:
        """
        Attach a file to an existing Model Version.

        The Model Version Attachment will be added and associated to the Model Version if it exists.
        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation
        is successful. The Attachment can be seen in the Vectice UI or interacted with with the Python SDK.

        :param file: A file to attach on the model version
        :param model: The model name or id
        :param model_version: The model version name or id
        :param workspace: The workspace name or id
        :param project: The project name or id
        :return: None
        """
        model_version_object = self.get_model_version(model_version, model, project, workspace)
        model_version_object.add_attachments(file)

    def delete_model_version_attachment(
        self,
        file: str,
        model_version: Reference,
        model: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> None:
        """
        Delete a Model Version Attachment.

        Deletes the specified attachment from the model version.

        :param model: The model name or id
        :param model_version: The model version name or id
        :param file: The file name
        :param workspace: The workspace name or id
        :param project: The project name or id
        :return: None
        """
        model_version_object = self.get_model_version(model_version, model, project, workspace)
        model_version_object.delete_attachments(file)

    def get_model_version_attachment(
        self,
        file: str,
        model_version: Reference,
        model: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> Optional[BinaryIO]:
        """
        Get a model version attachment.

        Gets the attachment of a model version.

        :param model: The model name or id
        :param model_version: The model version name or id
        :param file: The file name
        :param workspace: The workspace name or id
        :param project: The project name or id
        :return: An Artifact Version Attachment
        """
        model_version_object = self.get_model_version(model_version, model, project, workspace)
        return model_version_object.get_attachment(file)

    def list_model_version_attachments(
        self,
        model_version: Reference,
        model: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> List[str]:
        """
        List the files attached to a Model version.

        :param model: The model name or id
        :param model_version: The model version name or id
        :param workspace: The workspace name or id
        :param project: The project name or id
        :return: A list of file names
        """
        model_version_object = self.get_model_version(model_version, model, project, workspace)
        result = model_version_object.list_attachments()
        return result

    def add_dataset_version_attachment(
        self,
        file: str,
        dataset_version: Reference,
        dataset: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> None:
        """
        Adds a Dataset Version Attachment to an existing Dataset Version.

        The Dataset Version Attachment will be added and associated to the Dataset Version if it exists.
        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation
        is successful. The Attachment can be seen in the Vectice UI or interacted with with the Python SDK.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param file: A file to attach on the dataset version
        :param dataset: The dataset name or id
        :param dataset_version: The dataset version name or id

        :return: None
        """
        dataset_version_object: DatasetVersion = self.get_dataset_version(dataset_version, dataset, project, workspace)
        dataset_version_object.add_attachments(file)

    def delete_dataset_version_attachment(
        self,
        file: str,
        dataset_version: Reference,
        dataset: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the specified attachment from the dataset version.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param dataset: The dataset name or id
        :param dataset_version: The dataset version name or id
        :param file: The file name

        :return: None
        """
        dataset_version_object: DatasetVersion = self.get_dataset_version(dataset_version, dataset, project, workspace)
        dataset_version_object.delete_attachments(file)

    def list_dataset_version_attachments(
        self,
        dataset_version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> List[str]:
        """
        List the files attached to a Dataset version.
        :param workspace: The workspace name or id
        :param project: The project name or id
        :param dataset: The dataset name or id
        :param dataset_version: The dataset version name or id

        :return: An Artifact Version Attachment
        """
        dataset_version_object: DatasetVersion = self.get_dataset_version(dataset_version, dataset, project, workspace)
        return dataset_version_object.list_attachments()

    def add_code_version_attachment(
        self,
        file: Union[str, List[str]],
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Adds a Code Version Attachment to an existing Code Version.

        The Code Version Attachment will be added and associated to the Code Version if it exists.
        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation
        is successful. The Attachment can be seen in the Vectice UI or interacted with with the Python SDK.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param file: A file or list of files to attach on the dataset version
        :param code_version: The code version name or id

        :return: None
        """

        code_version = self.get_code_version(version, project, workspace)
        if code_version is None:
            raise ValueError("The code version was not found. Please check the reference provided.")
        code_version.add_attachments(file)

    def delete_code_version_attachment(
        self,
        file: Union[str, List[str]],
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the specified attachment from the code version.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param code_version: The code version name or id
        :param file: The file name

        :return: None
        """
        code_version = self.get_code_version(version, project, workspace)
        code_version.delete_attachments(file)

    def get_code_version_attachment(
        self,
        file: str,
        version: Reference,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> Optional[BinaryIO]:
        """
        Gets the attachment of a code version.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param code_version: The code version name or id
        :param file: The file name

        :return: A list of file name or uri
        """
        code_version = self.get_code_version(version, project, workspace)
        return code_version.get_attachment(file)

    def list_code_version_attachments(
        self,
        version: Reference,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> List[str]:
        """
        List the files attached to a Code version.


        :param workspace: The workspace name or id
        :param project: The project name or id
        :param code_version: The code version name or id
        :return: A list of file name or uri
        """
        code_version = self.get_code_version(version, project, workspace)
        return code_version.list_attachments()

    def add_run_attachment(
        self,
        file: str,
        run: Reference,
        job: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> None:
        """
        Adds a Code Version Attachment to an existing Code Version.

        The Code Version Attachment will be added and associated to the Code Version if it exists.
        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation
        is successful. The Attachment can be seen in the Vectice UI or interacted with with the Python SDK.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param file: A file to attach on the dataset version
        :param run: The run name or id
        :param job: The job name or id
        :return: None
        """
        run_object: Run = self.get_run(run, job, project, workspace)
        run_object.add_attachments(file)

    def delete_run_attachment(
        self,
        file: str,
        run: Reference,
        job: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> None:
        """
        Delete a Code Version Attachment.
        Deletes the specified attachment from the code version.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param run: The run name or id
        :param job: The job name or id
        :param file: The file name

        :return: None
        """
        run_object = self.get_run(run, job, project, workspace)
        run_object.delete_attachments(file)

    def get_run_attachment(
        self,
        file: str,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> Optional[BinaryIO]:
        """
        Gets the attachment of a code version.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param run: The run name or id
        :param job: The job name or id
        :param file: The file path

        :return: A list of file name or uri
        """
        run_object: Run = self.get_run(run, job, project, workspace)
        return run_object.get_attachment(file)

    def list_run_attachments(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> List[str]:
        """
        List the files attached to a Code version.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param run: The run name or id
        :param job: The job name or id
        :return: A list of file name or uri
        """
        run_object: Run = self.get_run(run, job, project, workspace)
        return run_object.list_attachments()

    def create_dataset_version(
        self,
        dataset: Reference,
        name: Optional[str] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        description: Optional[str] = None,
        is_starred: Optional[bool] = None,
        properties: Optional[Dict[str, Any]] = None,
        resources: Optional[List[str]] = None,
        metadata: Optional[List[FileMetadata]] = None,
        attachments: Optional[List[str]] = None,
        version_strategy: VersionStrategy = VersionStrategy.AUTOMATIC,
    ) -> DatasetVersion:
        """
        Create a dataset version.

        Creates a dataset version of the specified dataset. Resources are cloud provider assets e.g Google Cloud Storage
        with a connection in the Vectice UI and metadata are assets with no connection in Vectice UI.

        :param dataset: dataset name or id
        :param name: The name of the dataset version e.g Changes 'Version 1' to 'name'
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param description: The description of the dataset version
        :param is_starred: Whether the dataset version is starred
        :param properties: The properties of the dataset version
        :param resources: The resource uri/s of the dataset version
        :param metadata: The metadata uri/s of the dataset version


        :return: A DatasetVersion
        """
        if project is None and self.project is not None:
            project = self.project.id
            workspace = None
        elif isinstance(project, str) and workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        dataset_output = self._client.get_dataset(dataset, project, workspace)
        parent_project = self._get_parent_project(dataset_output.project_id, dataset_output.project.workspace_id)
        dataset_object: Dataset = Dataset(
            dataset_output.name,
            dataset_output.id,
            project=parent_project,
            description=dataset_output.description,
        )
        result = dataset_object.create_dataset_version(
            name, description, is_starred, properties, resources, metadata, attachments, version_strategy
        )
        return result

    def list_dataset_versions(
        self,
        dataset: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[DatasetVersion]:
        """
        List the dataset versions.

        Lists the dataset versions of the specified dataset.

        :param dataset: dataset name or id
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.

        :return: List of DatasetVersions
        """
        parent_dataset = self.get_dataset(dataset, project, workspace)
        return parent_dataset.list_dataset_versions(search, page_index, page_size)

    def get_dataset_version(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> DatasetVersion:
        """
        Get a dataset version.

        Gets a specific dataset version of the specified dataset.

        :param dataset: dataset name or id
        :param version: The dataset version name or id
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.

        :return: A DatasetVersion
        """
        logging.getLogger("Project").propagate = False
        if isinstance(version, int):
            dataset_version_output = self._client.get_dataset_version(version)
            if dataset_version_output is None:
                raise InvalidReferenceError("dataset version", version)
            parent_dataset: Dataset | None = self.get_dataset(dataset_version_output.dataset_id)
        else:
            if dataset is None:
                raise MissingReferenceError("dataset version", "dataset")
            parent_dataset = self.get_dataset(dataset, project, workspace)
        if parent_dataset is None:
            raise InvalidReferenceError("dataset", dataset)
        logging.getLogger("Project").propagate = True
        return parent_dataset.get_dataset_version(version)

    def get_dataset_version_attachment(
        self,
        file: str,
        dataset_version: Reference,
        dataset: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> Optional[BinaryIO]:
        """
        Get a model version attachment.

        Gets the attachment of a model version.

        :param dataset: The model name or id
        :param dataset_version: The model version name or id
        :param file: The file name
        :param workspace: The workspace name or id
        :param project: The project name or id
        :return: An Artifact Version Attachment
        """
        dataset_version_object = self.get_dataset_version(dataset_version, dataset, project, workspace)
        return dataset_version_object.get_attachment(file)

    def list_dataset_version_files_metadata(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> List[FileMetadata]:
        dataset_version = self.get_dataset_version(version, dataset, project, workspace)
        return dataset_version.list_files_metadata()

    def list_datasets(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> List[Dataset]:
        """
        List the datasets in a workspace.

        List the users connections having access to the specified workspace.

        :param workspace: The workspace name or id
        :param search: The connection name to search

        :return: List of Dataset
        """
        project_object = self._get_parent_project(project, workspace)
        return project_object.list_datasets(search, page_index, page_size)

    def delete_dataset(
        self, dataset: Reference, workspace: Optional[Reference] = None, project: Optional[Reference] = None
    ) -> None:
        """
        Deletes a dataset and all the versions that belong to it.

        :param dataset: The dataset name or id
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.

        :return: None
        """
        logging.getLogger("Project").propagate = False
        dataset_object = self.get_dataset(dataset, project, workspace)
        if dataset_object.project is None:
            raise SystemError("Project could not be found in dataset")
        logging.getLogger("Project").propagate = True
        dataset_object.project.delete_dataset(dataset_object.id)

    def delete_dataset_version(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes a specific dataset in the specified project.

        :param dataset: dataset name or id
        :param version: The dataset version name or id
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.

        :return: None
        """
        logging.getLogger("Dataset").propagate = False
        dataset_version_object = self.get_dataset_version(version, dataset, workspace, project)
        if dataset_version_object.dataset is None:
            raise SystemError("Dataset could not be found in dataset version")
        logging.getLogger("Dataset").propagate = True
        dataset_version_object.dataset.delete_dataset_version(dataset_version_object.id)

    def update_dataset(
        self,
        dataset: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        connection: Optional[Reference] = None,
    ) -> Dataset:
        """
        Updates a dataset. The connection is associated with the resources, e.g gcs connection for a gcs resource.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param dataset: dataset name or id
        :param name: The name of the dataset version e.g Changes 'Version 1' to 'name'
        :param description: The description of the dataset version
        :param connection: The connection name or id

        :return: the updated Dataset
        """
        logging.getLogger("Project").propagate = False
        dataset_object = self.get_dataset(dataset, project, workspace)
        if dataset_object.project is None:
            raise SystemError("Project not found for dataset")
        logging.getLogger("Project").propagate = True
        return dataset_object.project.update_dataset(dataset, name, description, connection)

    def update_dataset_version(
        self,
        version: Reference,
        dataset: Optional[Reference],
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_starred: Optional[bool] = None,
        properties: Optional[Dict] = None,
        resources: Optional[List[str]] = None,
        metadata: Optional[List[FileMetadata]] = None,
    ) -> DatasetVersion:
        """
        Updates a dataset version. The resource update is unique as if the hash is the same then the resource is
        not updated. If the hash is different then the resource will be updated.

        :param dataset: dataset name or id
        :param version: The dataset version name or id
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param name: The name of the dataset version e.g Changes 'Version 1' to 'name'
        :param description: The description of the dataset version
        :param is_starred: Whether the dataset version is starred
        :param properties: The properties of the dataset version
        :param resources: The resource/s uri/s of the dataset version
        :param metadata: The metadata uri/s of the dataset version

        :return: the updated Dataset Version
        """
        logging.getLogger("Project").propagate = False
        if isinstance(version, int):
            dataset_version_output = self._client.get_dataset_version(version)
            if dataset_version_output is None:
                raise InvalidReferenceError("version", version)
            parent_dataset = self.get_dataset(dataset_version_output.dataset_id)
        else:
            if dataset is None:
                raise MissingReferenceError("dataset version", "dataset")
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("job", "project")
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
            parent_dataset = self.get_dataset(dataset, project, workspace)
        logging.getLogger("Project").propagate = True
        return parent_dataset.update_dataset_version(
            version, name, description, is_starred, properties, resources, metadata
        )

    def create_connection(
        self,
        name: str,
        type: ConnectionType,
        parameters: Optional[Dict[str, Any]] = None,
        description: str = "",
        workspace: Optional[Reference] = None,
    ):
        """
        Create a connection with the specified connection name, description and
        parameters. The parameters keys and values depends on each connection Type.
        Example of required parameters. {"key_value": data, "file_name": "file.json", "connection_info": data}


        :param name: name of the connection
        :param type: the type of connection
        :param parameters: the parameters for the connection
        :param description: the description of the connection
        :param workspace: The workspace name or id
        :return: a connection
        """

        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if workspace is None:
            raise MissingReferenceError("connection", "workspace")
        parent_workspace = self.get_workspace(workspace)
        return parent_workspace.create_connection(name, type, parameters, description)

    def list_connections(
        self,
        workspace: Optional[Reference] = None,
        connection_type: Optional[str] = None,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[Connection]:
        """
        List the connections in a workspace.

        List the users connections having access to the specified workspace.

        :param workspace: The workspace name or id
        :param search: The connection name to search

        :return: List of Connections
        """
        workspace_object = self.workspace if workspace is None else self.get_workspace(workspace)
        if workspace_object is None:
            raise MissingReferenceError("workspace")
        return workspace_object.list_connections(connection_type, search, page_index, page_size)

    def get_connection(self, connection: Reference, workspace: Optional[Reference] = None) -> Connection:
        """
        retrieve an existing connection

        :param connection: The connection name or id
        :param workspace: the workspace where the connection has been created
        :return: A Connection if it is known
        """
        workspace_object = self.workspace if workspace is None else self.get_workspace(workspace)
        if workspace_object is None:
            raise MissingReferenceError("workspace")
        return workspace_object.get_connection(connection)

    def delete_connection(self, connection: Reference, workspace: Optional[Reference] = None):
        """
        Deletes the connection specified by the user.

        :param workspace: The workspace name or id the project belongs to
        :param connection: The connection name or id to delete.

        :return: None
        """
        workspace_object = self.workspace if workspace is None else self.get_workspace(workspace)
        if workspace_object is None:
            raise MissingReferenceError("workspace")
        return workspace_object.delete_connection(connection)

    def update_connection(
        self,
        connection: Reference,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        parameters: Optional[Dict] = None,
        description: Optional[str] = None,
    ) -> Connection:
        workspace_object = self.workspace if workspace is None else self.get_workspace(workspace)
        if workspace_object is None:
            raise MissingReferenceError("workspace")
        result = workspace_object.update_connection(connection, name, description=description, parameters=parameters)
        return result

    def update_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[ModelVersionStatus] = ModelVersionStatus.EXPERIMENTATION,
        algorithm: Optional[str] = None,
        is_starred: Optional[bool] = False,
        metrics: Optional[Dict] = None,
        hyper_parameters: Optional[Dict] = None,
    ) -> ModelVersion:
        """
        Update a model version.

        ?Updates the specified model version with the new params passed to this function. ?

        :param model: The model name or id the version belongs to
        :param version: The model version name or id
        :param name: The name of the model version
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param description: The description of the model
        :param status: The status of the model e.g 'EXPERIMENTATION'/'STAGING'/'PRODUCTION'
        :param algorithm: The algorithm the model version uses
        :param is_starred: Whether the model is starred or not
        :param metrics: The model version metrics
        :param hyper_parameters: The model version hyper parameters

        :return: None
        """
        logging.getLogger("Project").propagate = False
        if isinstance(version, int):
            model_version_output = self._client.get_model_version(version)
            parent_model = self.get_model(model_version_output.model_id)
        elif model is not None:
            parent_model = self.get_model(model, project, workspace)
        else:
            raise MissingReferenceError("model version", "model")
        logging.getLogger("Project").propagate = True
        result: ModelVersion = parent_model.update_model_version(
            version, name, description, status, algorithm, is_starred, metrics, hyper_parameters
        )
        return result

    def list_model_versions(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> List[ModelVersion]:
        """
        List the model versions of a model.

        Lists all the versions created out of the specified model.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param model: The model name or id the versions belongs to

        :return: List of ModelVersions
        """
        model_object: Model = self.get_model(model, project, workspace)
        return model_object.list_model_versions(search, page_index, page_size)

    def list_model_versions_dataframe(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> "pandas.DataFrame":  # type: ignore # noqa F821
        """
        Lists model versions in a pandas DataFrame and sorts by update date. Requires the pandas module to be installed,
        which can be done with ```pip install pandas``` or ```pip install vectice[pandas]```

        :param model: The id of the model
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param search: filter on name
        :param page_index: The page index. For example 1/20 would return page 1
        :param page_size: The number of versions on a page
        :return: pd.DataFrame
        """

        model_object: Model = self.get_model(model, project, workspace)
        return model_object.list_model_versions_dataframe(search, page_index, page_size)

    def get_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ModelVersion:
        """
        Gets a specific version of a model.

        :param model: The model name or id the version belongs to
        :param version: The model version name or id
        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.

        :return: A ModelVersion
        """

        if isinstance(version, int):
            model_version_output = self._client.get_model_version(version)
            if model_version_output is None:
                raise InvalidReferenceError("version", version)
            logging.getLogger("Project").propagate = False
            parent_model = self.get_model(model_version_output.model_id)
            logging.getLogger("Project").propagate = True
        elif model is not None:
            logging.getLogger("Project").propagate = False
            parent_model = self.get_model(model, project, workspace)
            logging.getLogger("Project").propagate = True
        else:
            raise MissingReferenceError("model version", "model")

        result: ModelVersion = parent_model.get_model_version(version)
        return result

    def delete_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the specified version of a model.

        :param workspace: The workspace name or id the project belongs to
        :param project: The project name or id to get.
        :param model: The model name or id the version belongs to
        :param version: The model version name or id

        :return: None
        """
        logging.getLogger("Project").propagate = False
        if isinstance(version, int):
            model_version_output = self._client.get_model_version(version)
            parent_model = self.get_model(model_version_output.model_id)
        else:
            if model is None:
                raise MissingReferenceError("dataset version", "dataset")
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("job", "project")
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
            parent_model = self.get_model(model, project, workspace)
        logging.getLogger("Project").propagate = True
        parent_model.delete_model_version(version)

    def delete_model_version_metrics(
        self,
        version: Reference,
        metrics: List[str],
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Delete a model version metrics.

        Delete a model version metrics.

        :param version: The version name or id of the model
        :param metrics: The metric keys to be deleted
        :param model: The model id or name
        :param project: The project name or id to get.
        :param workspace: The workspace name or id to get.

        :return:
        """
        model_version_object = self.get_model_version(version, model, project, workspace)
        model_version_object.model.delete_model_version_metrics(version, metrics)

    def delete_model_version_hyper_parameters(
        self,
        version: Reference,
        hyper_parameters: List[str],
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Delete a model version hyper parameters.

        Delete a model version hyper parameters.

        :param version: The version name or id of the model
        :param hyper_parameters: The hyper parameter keys to be deleted
        :param model: The model id or name
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return:
        """
        model_version_object = self.get_model_version(version, model, project, workspace)
        model_version_object.model.delete_model_version_properties(version, hyper_parameters)

    def create_model(
        self,
        name: str,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        description: Optional[str] = None,
        type: Optional[ModelType] = ModelType.OTHER,
    ) -> Model:
        """
        Create a model.

        Creates a new model in the specified project.

        :param name: The name of the model
        :param workspace: The workspace name or id
        :param project: The project name or id
        :param description: The description of the model
        :param type: The model type to use

        :return: A Model
        """
        if project is None and self.project is not None:
            project = self.project.id
            workspace = None
        elif isinstance(project, str) and workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.create_model(name, description, type)

    def update_model(
        self,
        model: Reference,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[ModelType] = ModelType.OTHER,
    ) -> Model:
        """
        Update a model.

        :param model: The model name or id
        :param workspace: The workspace name or id
        :param project: The project name or id
        :param name: The name of the model
        :param description: The description of the model
        :param type: The model type

        :return: Model
        """
        logging.getLogger("Project").propagate = False
        if isinstance(model, int):
            model_object = self.get_model(model)
        elif isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("model", "project")
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
            model_object = self.get_model(model, project, workspace)
        else:
            raise InvalidReferenceError("model", model)
        logging.getLogger("Project").propagate = True
        result: Model = model_object.project.update_model(model, name, description, type)
        return result

    def list_models(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> List[Model]:
        """
        List the models.

        Lists the models of the specified project, the search param helps find the models with the specified name.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param search: filter on name

        :return: List of Models
        """
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.list_models(search, page_index, page_size)

    def delete_model(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the model with the specified reference.

        :param model: The model name or id
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: None
        """
        logging.getLogger("Project").propagate = False
        model_object = self.get_model(model, project, workspace)
        logging.getLogger("Project").propagate = True
        model_object.project.delete_model(model)

    def create_code_version(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_starred: Optional[bool] = None,
        uri: Optional[str] = None,
        git_version: Optional[GitVersion] = None,
        script_relative_path: str = ".",
        check_remote_repository: bool = True,
        attachments: Optional[Union[str, List[str]]] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersion:
        """
        Create a code version.

        Creates a code version in the specified project using the git repository path of the code version.

        :param name: The name of the dataset version e.g Changes 'Version 1' to 'name'
        :param description: The description of the dataset version
        :param is_starred: Whether the dataset version is starred
        :param uri:
        :param git_version:
        :param script_relative_path: The path to the git repository
        :param check_remote_repository: indicate if the version should check the entry is existing on origin repository
        :param attachments: Resources to attach to the code version e.g AWS S3 or local files
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: A CodeVersion
        """
        logging.getLogger("Project").propagate = False
        if project is None and self.project is not None:
            project = self.project.id
        else:
            if project is None:
                raise MissingReferenceError("project")
            if isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        if git_version is None:
            git_version = GitVersion.create(script_relative_path, check_remote_repository=check_remote_repository)
        project_object = self._get_parent_project(project, workspace)
        logging.getLogger("Project").propagate = True
        code_version = project_object.create_code_version(name, description, uri, is_starred, git_version)
        if attachments is not None:
            for attachment in attachments:
                code_version.add_attachments(attachment)
        return code_version

    def create_code_version_github_uri(
        self,
        uri: str,
        script_relative_path: str,
        login_or_token: Optional[str] = None,
        password: Optional[str] = None,
        jwt: Optional[str] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersion:
        """
        Create a code version using an URI.

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param login_or_token: A real login or a personal access token
        :param password: The password
        :param jwt: The OAuth2 access token
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: A CodeVersion
        """
        git_version = GitVersion.create_from_github_uri(uri, script_relative_path, login_or_token, password, jwt)
        if git_version is None:
            raise ValueError("Please check the GitHub uri and script relative path.")
        project_object = self._get_parent_project(project, workspace)
        return project_object.create_code_version(git_version=git_version)

    def create_code_version_gitlab_uri(
        self,
        uri: str,
        script_relative_path: str,
        private_token: Optional[str] = None,
        oauth_token: Optional[str] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersion:
        """
        Create a code version using an URI.

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param private_token: A real login or a personal access token
        :param oauth_token: The password
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: A CodeVersion
        """
        git_version = GitVersion.create_from_gitlab_uri(uri, script_relative_path, private_token, oauth_token)
        if git_version is None:
            raise ValueError("Please check the Gitlab uri and script relative path.")
        project_object = self._get_parent_project(project, workspace)
        return project_object.create_code_version(git_version=git_version)

    def create_code_version_bitbucket_uri(
        self,
        uri: str,
        script_relative_path: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersion:
        """
        Create a code version using an URI.

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param username: A real login or a personal access token
        :param password: The password
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: A CodeVersion
        """
        git_version = GitVersion.create_from_bitbucket_uri(uri, script_relative_path, username, password)
        if git_version is None:
            raise ValueError("Please check the BitBucket uri and script relative path.")
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.create_code_version(git_version=git_version)

    def update_code_version(
        self,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_starred: Optional[bool] = None,
        repository_name: Optional[str] = None,
        branch_name: Optional[str] = None,
        commit_hash: Optional[str] = None,
        commit_comment: Optional[str] = None,
        commit_author_name: Optional[str] = None,
        commit_author_email: Optional[str] = None,
        is_dirty: Optional[bool] = None,
        uri: Optional[str] = None,
        entrypoint: Optional[str] = None,
        check_remote_repository: Optional[bool] = True,
    ) -> CodeVersion:
        """
        Updates the specified code version with the new given information in the params.
        If the code version id is given there is no need for specifying the workspace or project references.

        :param version: The code version name or id
        :param name: The name of the code version e.g Changes 'Version 1' to 'name'
        :param description: The description of the code version
        :param is_starred: Whether the code version is starred
        :param repository_name: The git repository name
        :param branch_name: The git branch name
        :param commit_hash: The git commit hash
        :param commit_comment: The git commit comment
        :param commit_author_email: The git commite author email
        :param commit_author_name: The git commit author name
        :param is_dirty: If the git commit is dirty
        :param uri: The git uri
        :param entrypoint: The entrypoint of the script
        :param check_remote_repository: Check the remote repository

        :return: The updated code version
        """
        logging.getLogger("Project").propagate = False
        git_version = None
        if entrypoint is None:
            if (
                repository_name is not None
                and branch_name is not None
                and commit_hash is not None
                and commit_comment is not None
                and commit_author_name is not None
                and commit_author_email is not None
                and is_dirty is not None
                and uri is not None
            ):
                git_version = GitVersion(
                    repository_name,
                    branch_name,
                    commit_hash,
                    commit_comment,
                    commit_author_name,
                    commit_author_email,
                    is_dirty,
                    uri,
                )
        elif entrypoint:
            git_version = GitVersion.create(
                entrypoint, check_remote_repository=check_remote_repository if check_remote_repository else False
            )
        if project is None and self.project is not None:
            project = self.project.id
        else:
            if project is None:
                raise MissingReferenceError("project")
            if isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        project_object = self._get_parent_project(project, workspace)
        logging.getLogger("Project").propagate = True
        return project_object.update_code_version(version, name, description, is_starred, uri, git_version=git_version)

    def list_code_versions(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> List[CodeVersion]:
        """
        Lists all the versions of a code artifact.

        :param workspace: The workspace name or id
        :param project: The project name or id
        :param search: Search code version term
        :param page_index: The page index
        :param page_size: The page size

        :return: List of CodeVersions
        """
        if project is None and self.project is not None:
            project = self.project.id
        else:
            if project is None:
                raise MissingReferenceError("project")
            if isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        project_object = self._get_parent_project(project, workspace)
        return project_object.list_code_versions(search, page_index, page_size)

    def get_code_version(
        self,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersion:
        """
        Gets the specified version of a code artifact. If the code version id is given
        there is no need for specifying the workspace or project references.

        :param version: The version name or id.
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: A CodeVersion
        """
        if isinstance(version, int):
            code_version_output = self._client.get_code_version(version)
            if code_version_output is None:
                raise InvalidReferenceError("code version", version)
            else:
                project_object = self._get_parent_project(code_version_output.code.project.id, workspace)
        elif isinstance(version, str) and project or self.project:
            if project is not None:
                project_object = self._get_parent_project(project, workspace)
            elif self.project is not None:
                project_object = self.project
            else:
                raise MissingReferenceError("code version", version)
        else:
            raise InvalidReferenceError("code version", version)
        return project_object.get_code_version(version)

    def delete_code_version(
        self,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the specified version of a code artifact. If the code version id is given
        there is no need for specifying the workspace or project references.


        :param workspace: The workspace name or id
        :param project: The project name or id
        :param version: The version name or id.

        :return: None
        """
        logging.getLogger("Project").propagate = False
        code_version = self.get_code_version(version, project, workspace)
        logging.getLogger("Project").propagate = False
        return code_version.project.delete_code_version(code_version.id)

    def create_stage(
        self,
        name: Optional[str] = None,
        status: Optional[StageStatus] = StageStatus.NotStarted,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> Stage:
        """
        Add a stage to the project. A documentation page is created with the title provided. The status can be 'NotStarted/InProgress/Completed'.

        :param name: The name of the stages documentation page.
        :param status: The status of the stage.
        :param project: The name or id of the project
        :param workspace: The name or id of the workspace

        :return: A Stage object
        """
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.create_stage(name, status)

    def update_stage(
        self,
        stage: Reference,
        name: Optional[str] = None,
        status: Optional[StageStatus] = StageStatus.NotStarted,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> Stage:
        """
        Update a stage of the project. A documentation page is updated with the title and status provided. The status can be 'Draft/InProgress/Completed'.

        :param stage: The name or id of the stage.
        :param name: The name of the stages documentation page.
        :param status: The status of the stage.
        :param project: The name or id of the project
        :param workspace: The name or id of the workspace

        :return: A Stage object
        """
        if isinstance(stage, int):
            stage_object = self.get_stage(stage)
        elif isinstance(stage, str):
            if project is None and self.project is not None:
                project = self.project.id
            if project is None:
                raise MissingReferenceError("stage", "project")
            if workspace is None and isinstance(project, str) and self.workspace is not None:
                workspace = self.workspace.id
            stage_object = self.get_stage(stage, project, workspace)
        else:
            raise InvalidReferenceError("stage", stage)
        result: Stage = stage_object.project.update_stage(stage, name, status)
        return result

    def get_stage(
        self, stage: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> Stage:
        """
        Get a stage of the project. A stage will be returned.

        :param stage: The name or id of the stage.
        :param project: The name or id of the project
        :param workspace: The name or id of the workspace

        :return: Stage
        """
        if isinstance(stage, int):
            stage_output = self._client.get_stage(stage)
            if stage_output is None:
                raise InvalidReferenceError("version", stage)
            project_object = self._get_parent_project(stage_output.project_id, None)
            if project_object:
                self._client._project = stage_output.project
        elif isinstance(stage, str):
            if project is None and self.project is not None:
                project = self.project.id
            if isinstance(project, str) and workspace is None and self.workspace is not None:
                workspace = self.workspace.id
            if project is None:
                raise MissingReferenceError("stage", "project")
            project_object = self._get_parent_project(project, workspace)
        else:
            raise MissingReferenceError("stage", "stage")
        return project_object.get_stage(stage)

    def list_stages(
        self,
        search: Optional[str] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> List[Stage]:
        """
        List all the stages of the project. A search term can be used.

        :param search: The search term to be used.
        :param project: The name or id of the project
        :param workspace: The name or id of the workspace
        :param page_index: The page index to be returned
        :param page_size: The page size to be returned

        :return: A list of stages
        """
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.list_stages(search, page_index, page_size)

    def delete_stage(
        self, stage: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> None:
        """
        Delete a stage of the project. A documentation page related to the stage will be deleted aswell.

        :param stage: The name or id of the stage.
        :param project: The name or id of the project
        :param workspace: The name or id of the workspace


        :return: None
        """
        parent_project = self._get_parent_project(project, workspace)
        return parent_project.delete_stage(stage)

    def document_run(self, run_id: Optional[int] = None, name: Optional[str] = None, **kwargs) -> None:
        """
        Captures all the assets of a run in a stage and documentation.

        :param run_id: The id of the run.
        :param name: The name of the stage.

        :return: None
        """
        logger.info("Run will be documented and captured in a Stage.")
        if run_id is not None:
            """
            Captures an existing run. That has been completed.
            """
            run = self.get_run(run_id)
            if run and run.status != RunStatus.COMPLETED:
                logging.warning(
                    "The run is not in a completed state and the auto documentation might not function as expected."
                )
            if name is not None:
                try:
                    stage = self.get_stage(name)
                except Exception:
                    logger.debug(f"Stage {name} for auto documentation not found.")
                    stage = self.create_stage(name, status=StageStatus.InProgress)
            else:
                stage = self.create_stage(f"Auto Document {run.name}", status=StageStatus.InProgress)
            run._capture_run_info(stage)
        elif run_id is None and len(self._active_runs) >= 1 or run_id is None and kwargs.get("_experiment_run"):
            """
            Sets up to capture the run upon completion. Experiment.complete() / vectice.end_run()
            """
            self._auto_document_run = True
            self._document_stage = name
        else:
            raise MissingReferenceError("No run provided and no active run.")
