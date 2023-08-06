from __future__ import annotations

import logging
from typing import List, Optional, TYPE_CHECKING, Tuple, BinaryIO, Any, Dict, Sequence

from vectice.api._auth import Auth
from vectice.api.artifact import ArtifactApi
from vectice.api.code import CodeApi
from vectice.api.code_version import CodeVersionApi
from vectice.api.connections import ConnectionApi
from vectice.api.dataset import DatasetApi
from vectice.api.dataset_version import DatasetVersionApi
from vectice.api.job import JobApi
from vectice.api.json_object import JsonObject
from vectice.api.run import RunApi
from .attachment import AttachmentApi
from .compatibility import CompatibilityApi
from .stage import StageApi
from .block import BlockApi
from .json import (
    ModelVersionOutput,
    ModelVersionInput,
    PagedResponse,
    ModelOutput,
    ModelInput,
    JobInput,
    ArtifactOutput,
    ProjectInput,
    ConnectionInput,
    Page,
    StartRunInput,
    StopRunInput,
    StopRunOutput,
    FileMetadata,
    StageInput,
    StageOutput,
    BlockInput,
    BlockOutput,
)
from .json.compatibility import CompatibilityOutput
from .json.metric import MetricInput, MetricOutput
from .json.property import PropertyOutput, PropertyInput
from .json.rule import ArtifactReferenceInput, FillRunInput
from .json.workspace import WorkspaceInput
from .model import ModelApi
from .model_version import ModelVersionApi
from .project import ProjectApi
from .reference import MissingReferenceError
from .rule import RuleApi
from .workspace import WorkspaceApi

if TYPE_CHECKING:
    from vectice import Reference
    from .json import JobOutput
    from .json import RunOutput, RunInput
    from .json import WorkspaceOutput
    from .json import ProjectOutput
    from .json import ArtifactInput
    from .json import ConnectionOutput
    from .json import DatasetInput, DatasetOutput
    from .json import DatasetVersionOutput, DatasetVersionInput
    from .json import AttachmentOutput
    from .json import CodeOutput, CodeInput
    from .json import CodeVersionOutput, CodeVersionInput


class Client:
    """
    Low level Vectice API client.
    """

    def __init__(
        self,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
        token: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        auto_connect=True,
        allow_self_certificate=True,
    ):
        self._auth = Auth(
            api_endpoint=api_endpoint,
            api_token=token,
            auto_connect=auto_connect,
            allow_self_certificate=allow_self_certificate,
        )
        self._logger = logging.getLogger(self.__class__.__name__)
        self._workspace = None
        self._project = None
        if auto_connect and workspace is not None:
            if isinstance(project, int):
                self._project = self.get_project(project)
                self._workspace = self._project.workspace
                if workspace is not None:
                    if isinstance(workspace, str):
                        if workspace != self._workspace.name:
                            raise ValueError(
                                f"Inconsistency in configuration: project {project} does not belong to workspace {workspace}"
                            )
                    else:
                        if workspace != self._workspace.id:
                            raise ValueError(
                                f"Inconsistency in configuration: project {project} does not belong to workspace {workspace}"
                            )
                self._logger.info(
                    f"Successfully authenticated. You'll be working on Project: {self._project.name} part of Workspace: {self._workspace.name}"
                )
            else:
                self._workspace = self.get_workspace(workspace)
                if project is not None:
                    self._project = self.get_project(project, workspace)
                    self._logger.info(
                        f"Successfully authenticated. You'll be working on Project: {self._project.name} part of Workspace: {self._workspace.name}"
                    )
                else:
                    self._logger.info(f"The entered Workspace is OK and allows you to work on {self._workspace.name}")
        elif auto_connect and workspace is None and project:
            self._project = self.get_project(project)
            if self._project is not None:
                self._workspace = self._project.workspace
            self._logger.info(
                f"Successfully authenticated. You'll be working on Project: {self._project.name} part of Workspace: {self._workspace.name}"
            )

    @property
    def workspace(self) -> Optional[WorkspaceOutput]:
        """
        The workspace object.
        :return: WorkspaceOutput
        """
        return self._workspace

    @property
    def project(self) -> Optional[ProjectOutput]:
        """
        The project object.
        :return: ProjectOutput
        """
        return self._project

    def check_compatibility(self) -> CompatibilityOutput:
        return CompatibilityApi(self._auth).check_version()

    def create_project(self, data: ProjectInput, workspace: Reference) -> ProjectOutput:
        """
         Creates a project.

        :param data: The ProjectInput json structure
        :param workspace: The workspace name or id

        :return: The ProjectOutput json structure
        """
        result = ProjectApi(self._auth).create_project(data, workspace)
        self._logger.info(f"Project with id: {result.id} successfully created.")
        return result

    def delete_project(self, project: Reference, workspace: Optional[Reference] = None):
        """
         Deletes a project.

        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        ProjectApi(self._auth).delete_project(project, workspace)

    def update_project(self, data: ProjectInput, project: Reference, workspace: Reference) -> ProjectOutput:
        """
        Updates a project.

        :param data: The ProjectInput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The ProjectOutput json structure
        """
        return ProjectApi(self._auth).update_project(data, project, workspace)

    def list_projects(
        self,
        workspace: Reference,
        search: Optional[str] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> PagedResponse[ProjectOutput]:
        """
        Lists the projects in a workspace.

        :param workspace: The workspace name or id
        :param search: A text to search for
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[ProjectOutput]
        """
        return ProjectApi(self._auth).list_projects(workspace, search, page_index, page_size)

    def get_project(self, project: Reference, workspace: Optional[Reference] = None) -> ProjectOutput:
        """
        Gets a project.

        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The ProjectOutput json structure
        """
        return ProjectApi(self._auth).get_project(project, workspace)

    def get_workspace(self, workspace: Reference) -> WorkspaceOutput:
        """
        Gets a workspace.

        :param workspace: The workspace name or id

        :return: The WorkspaceOutput json structure
        """
        return WorkspaceApi(self._auth).get_workspace(workspace)

    def create_workspace(self, data: WorkspaceInput) -> WorkspaceOutput:
        """
        Creates a workspace.

        :param data: The WorkspaceInput json structure

        :return: The WorkspaceOutput json structure
        """
        result = WorkspaceApi(self._auth).create_workspace(data)
        return result

    def update_workspace(self, data: WorkspaceInput, workspace: Reference) -> WorkspaceOutput:
        """
        Updates a workspace.

        :param data: The WorkspaceInput json structure
        :param workspace: The workspace name or id

        :return: The WorkspaceOutput json structure
        """
        return WorkspaceApi(self._auth).update_workspace(data, workspace)

    def list_workspaces(
        self, search: Optional[str] = None, page_index: int = 1, page_size: int = 20
    ) -> PagedResponse[WorkspaceOutput]:
        """
        Lists the workspaces.

        :param search: A text to search for
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[WorkspaceOutput]
        """
        return WorkspaceApi(self._auth).list_workspaces(search, page_index, page_size)

    def get_job(
        self, job: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> JobOutput:
        """
        Gets a job.

        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The JobOutput json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return JobApi(self._auth).get_job(job, project, workspace)

    def delete_job(
        self, job: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> None:
        """
        Deletes a job.

        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """

        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        JobApi(self._auth).delete_job(job, project, workspace)

    def start_run(
        self, data: StartRunInput, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> JsonObject:
        """
        Start a run.

        :param data: The StartRunInput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: A json object
        """
        if project is None and self._project is not None:
            project = self._project.id
        if project is None:
            raise MissingReferenceError("run", "project")
        return RuleApi(self._auth).start_run(data, project, workspace)

    def fill_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        inputs: Optional[List[ArtifactReferenceInput]] = None,
        outputs: Optional[List[ArtifactReferenceInput]] = None,
    ):
        """
        Fills a run.

        :param run: The run name or id
        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id
        :param inputs: The list of artifact references
        :param outputs: The list of artifact references

        :return:  FillRunOutput
        """
        if inputs is not None or outputs is not None:
            run_object = self.get_run(run, job, project, workspace)
            return RuleApi(self._auth).fill_run(
                FillRunInput(run_object.id, [] if inputs is None else inputs, [] if outputs is None else outputs)
            )

    def stop_run(
        self,
        data: StopRunInput,
    ) -> StopRunOutput:
        """
        Stops a run.

        :param data: The StopRunInput json structure

        :return: The StopRunOutput json structure
        """
        return RuleApi(self._auth).stop_run(data)

    def list_jobs(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[JobOutput]:
        """
        Lists the jobs in a project.

        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: A text to filter jobs we are looking for
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[JobOutput]
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return JobApi(self._auth).list_jobs(project, workspace, search, page_index, page_size)

    def create_job(
        self, data: JobInput, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> JobOutput:
        """
        Creates a job.

        :param data: The JobInput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: A JobOutput instance
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return JobApi(self._auth).create_job(project, workspace, data)

    def update_job(self, data: JobOutput, project: Optional[Reference] = None, workspace: Optional[Reference] = None):
        """
        Updates a job.

        :param data: The JobOutput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The JobOutput json structure
        """

        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return JobApi(self._auth).update_job(project, workspace, data)

    def list_runs(
        self,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[RunOutput]:
        """
        Lists the runs of a specific job.

        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: A name to search for
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[RunOutput]
        """
        result = RunApi(self._auth).list_runs(job, project, workspace, search, page_index, page_size)
        return result

    def create_run(
        self,
        data: RunInput,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> RunOutput:
        """
        Creates a run.

        :param data: The RunInput json structure
        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The RunOutput json structure
        """
        if isinstance(job, str):
            if project is None and self.project is not None:
                project = self.project.id
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return RunApi(self._auth).create_run(data, job, project, workspace)

    def get_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> RunOutput:
        """
        Gets a run.

        :param run: The run name or id
        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The RunOutput json structure
        """
        if isinstance(job, str):
            if project is None and self.project is not None:
                project = self.project.id
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return RunApi(self._auth).get_run(run, job, project, workspace)

    def list_artifacts(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> PagedResponse[ArtifactOutput]:
        """
        Lists the artifacts of a run.

        :param run: The run name or id
        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: PagedResponse[ArtifactOutput]
        """

        if isinstance(job, str):
            if project is None and self.project is not None:
                project = self.project.id
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return ArtifactApi(self._auth).list_artifacts(run, job, project, workspace)

    def update_run(self, data: RunOutput):
        """
        Updates a run.

        :param data: The RunOutput json sturcture

        :return: The RunOutput json structure
        """
        if data.id is None:
            raise ValueError("the id is required")
        return RunApi(self._auth).update_run(data)

    def delete_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Deletes a run.

        :param run: The run name or id
        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        RunApi(self._auth).delete_run(run, job, project, workspace)

    def create_run_properties(
        self,
        run: Reference,
        properties: List[PropertyInput],
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> RunOutput:
        """
        Creates run properties.

        :param run: The run name or id
        :param properties: The list of PropertyInput json structure
        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The RunOutput json structure
        """
        if isinstance(job, str) and isinstance(run, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return RunApi(self._auth).create_run_properties(run, properties, job, project, workspace)

    def list_run_properties(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[PropertyOutput]:
        """
        Lists the run properties.

        :param run: The run name or id
        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[PropertyOutput]
        """
        if isinstance(job, str) and isinstance(run, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return RunApi(self._auth).list_run_properties(
            run,
            job,
            project,
            workspace,
            page_index,
            page_size,
        )

    def create_artifact(
        self,
        data: ArtifactInput,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Creates an artifact.

        :param data: The ArtifactInput json structure
        :param run: The run name or id
        :param job: The job name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The ArtifactOutput json structure
        """
        return ArtifactApi(self._auth).create_artifact(data, run, job, project, workspace)

    def update_artifact(self, artifact: ArtifactOutput):
        """
        Updates an artifact.

        :param artifact: The ArtifactOutput json structure

        :return: The json structure
        """
        return ArtifactApi(self._auth).update_artifact(artifact)

    def get_dataset(
        self, dataset: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> DatasetOutput:
        """
        Gets a dataset.

        :param dataset: The dataset name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The DatasetOutput json structure
        """
        if isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return DatasetApi(self._auth).get_dataset(dataset, project, workspace)

    def list_datasets(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: str = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[DatasetOutput]:
        """
        Lists the datasets in a project.

        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: A name to search for
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[DatasetOutput]
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return DatasetApi(self._auth).list_datasets(project, workspace, search, page_index, page_size)

    def create_dataset(
        self, data: DatasetInput, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> DatasetOutput:
        """
        Creates a dataset.

        :param data: The DatasetOutput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The DatasetOutput json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return DatasetApi(self._auth).create_dataset(data, project, workspace)

    def update_dataset(
        self,
        data: DatasetOutput,
        dataset: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> DatasetOutput:
        """
        Updates a dataset.

        :param data: The DatasetOutput json structure
        :param dataset: Teh dataset name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The DatasetOutput json structure
        """
        if isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return DatasetApi(self._auth).update_dataset(data, dataset, project, workspace)

    def delete_dataset(
        self, dataset: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> None:
        """
        Deletes a dataset.

        :param dataset: The dataset name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        DatasetApi(self._auth).delete_dataset(dataset, project, workspace)

    def get_model(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Gets a model.

        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The ModelOutput json structure
        """
        if isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return ModelApi(self._auth).get_model(model, project, workspace)

    def list_models(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[ModelOutput]:
        """
        Lists the models in a project.

        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: The name to search
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[ModelOutput]
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return ModelApi(self._auth).list_models(project, workspace, search, page_index, page_size)

    def create_model(
        self, data: ModelInput, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ):
        """
        Creates a model.

        :param data: The ModelInput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The ModelOutput json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return ModelApi(self._auth).create_model(data, project, workspace)

    def update_model(
        self,
        data: ModelInput,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Updates a model.

        :param data: The ModelInput json structure
        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The ModelOutput json structure

        """
        if isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return ModelApi(self._auth).update_model(data, model, project, workspace)

    def delete_model(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Deletes a model.

        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None

        """
        ModelApi(self._auth).delete_model(model, project, workspace)

    def list_dataset_versions(
        self,
        dataset: Reference,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> PagedResponse[DatasetVersionOutput]:
        """
        Lists dataset versions.

        :param dataset: The dataset name or id
        :param search: A name to search
        :param page_index: The index of the page
        :param page_size: The size of the page
        :param project: The project name or id
        :param workspace: the workspace name or id

        :return: PagedResponse[DatasetVersionOutput]
        """
        if isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return DatasetVersionApi(self._auth).list_dataset_versions(
            dataset, workspace, project, search, page_index, page_size
        )

    def create_dataset_version(
        self,
        data: DatasetVersionInput,
        dataset: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> DatasetVersionOutput:
        """
        Creates a dataset version.

        :param data: The DatasetVersionOutput json structure
        :param dataset: The parent dataset name or id
        :param project: The project name or id
        :param workspace: the workspace name or id

        :return: The DatasetVersionOutput json structure
        """
        if isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return DatasetVersionApi(self._auth).create_dataset_version(data, dataset, project, workspace)

    def update_dataset_version(
        self,
        data: DatasetVersionOutput,
        version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> DatasetVersionOutput:
        """
        Updates a dataset version.

        :param data: The DatasetVersionOutput json structure
        :param version: The version name or id
        :param dataset: The parent dataset name or id
        :param project: The project name or id
        :param workspace: the workspace name or id

        :return: The DatasetVersionOutput json structure
        """
        if isinstance(version, str) and isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return DatasetVersionApi(self._auth).update_dataset_version(data, version, dataset, project, workspace)

    def get_dataset_version(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> DatasetVersionOutput:
        """
        Gets a dataset version.

        :param version: The version name or id
        :param dataset: The parent dataset name or id
        :param project: The project name or id
        :param workspace: the workspace name or id

        :return: DatasetVersionOutput json structure
        """
        if isinstance(version, str) and isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return DatasetVersionApi(self._auth).get_dataset_version(version, dataset, project, workspace)

    def delete_dataset_version(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Deletes a dataset version.

        :param version: The version name or id
        :param dataset: The parent dataset name or id
        :param project: The project name or id
        :param workspace: the workspace name or id

        :return: None
        """
        if isinstance(version, str) and isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        DatasetVersionApi(self._auth).delete_dataset_version(version, dataset, project, workspace)

    def list_dataset_version_files_metadata(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> List[FileMetadata]:
        """
        Lists the dataset version properties.

        :param version: The dataset version name or ID
        :param dataset: The parent dataset name or ID
        :param project: The project name or ID
        :param workspace: The workspace name or ID

        :return: DatasetVersionOutput json structure
        """
        return DatasetVersionApi(self._auth).list_files_metadata(version, dataset, project, workspace)

    def create_dataset_version_properties(
        self,
        version: Reference,
        properties: Dict[str, Any],
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Creates dataset version properties.

        :param version: The dataset version name or ID
        :param properties: The properties dictionary
        :param dataset: The parent dataset name or ID
        :param project: The project name or ID
        :param workspace: The workspace name or ID

        :return: DatasetVersionOutput json structure
        """
        if isinstance(version, str) and isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        result = DatasetVersionApi(self._auth).create_dataset_version_properties(
            version, properties, dataset, project, workspace
        )
        self._logger.info(
            f"Properties with names: {list(properties.keys())} successfully added to DatasetVersion {result.name}."
        )
        return result

    def update_dataset_version_properties(
        self,
        version: Reference,
        property_id: int,
        properties: Dict[str, Any],
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Updates dataset version properties.

        :param version: The dataset version name or id
        :param property_id: The property key or id to update
        :param properties: The properties dictionary
        :param dataset: The parent dataset name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if isinstance(version, str) and isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        result = DatasetVersionApi(self._auth).update_dataset_version_properties(
            version, property_id, properties, dataset, project, workspace
        )
        dataset_version = DatasetVersionApi(self._auth).get_dataset_version(version, dataset, project, workspace)
        self._logger.info(
            f"Properties with names: {list(properties.keys())} successfully updated in DatasetVersion {dataset_version.name}."
        )
        return result

    def list_dataset_version_properties(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[PropertyOutput]:
        """
        Lists dataset version properties.

        :param version: The dataset version name or id
        :param page_index: The index of the page
        :param page_size: The size of the page
        :param dataset: Teh parent dataset name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: PagedResponse[PropertyOutput]
        """
        if isinstance(version, str) and isinstance(dataset, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return DatasetVersionApi(self._auth).list_dataset_version_properties(
            version,
            dataset,
            project,
            workspace,
            page_index,
            page_size,
        )

    def get_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ModelVersionOutput:
        """
        Gets a model version.

        :param version: The model version name or id
        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: ModelVersionOutput
        """
        if isinstance(version, str) and isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return ModelVersionApi(self._auth).get_model_version(version, model, project, workspace)

    def list_model_versions(
        self,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[ModelVersionOutput]:
        """
        Lists model versions.

        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: The word to search
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[ModelVersionOutput]
        """
        if isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return ModelVersionApi(self._auth).list_model_versions(model, project, workspace, search, page_index, page_size)

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
        """
        Lists model versions.

        :param model: The model name or id
        :param version: The model version name or id
        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: The word to search
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return:PagedResponse[MetricOutput]
        """
        if isinstance(version, str) and isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str) and self.workspace is not None:
                if workspace is None:
                    workspace = self.workspace.id
        return ModelVersionApi(self._auth).list_model_version_metrics(
            version,
            model,
            project,
            workspace,
            search,
            page_index,
            page_size,
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
        """
        Lists model version properties.

        :param model: The model name or id
        :param version: The model version name or id
        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: The word to search
        :param page_index: The index of the page
        :param page_size: The size of the page

        :return: PagedResponse[PropertyOutput]
        """
        if isinstance(version, str):
            if project is None and self.project is not None:
                project = self.project.id
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return ModelVersionApi(self._auth).list_model_version_properties(
            version, model, project, workspace, search, page_index, page_size
        )

    def create_model_version_properties(
        self,
        version: Reference,
        properties: List[PropertyInput],
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Creates model version properties.

        :param model: The model name or id
        :param version: The model version name or id
        :param properties: The properties object
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return ModelVersionApi(self._auth).create_model_version_properties(
            version, properties, model, project, workspace
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
        """
        Creates model version properties.

        :param model: The model name or id
        :param version: The model version name or id
        :param property_id: The property id
        :param properties: The properties object
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None

        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return ModelVersionApi(self._auth).update_model_version_properties(
            version,
            property_id,
            properties,
            model,
            project,
            workspace,
        )

    def create_model_version_metrics(
        self,
        version: Reference,
        metrics: List[MetricInput],
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Creates model version metrics.

        :param model: The model name or id
        :param version: The model version name or id
        :param metrics: The properties object
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return ModelVersionApi(self._auth).create_model_version_metrics(version, metrics, model, project, workspace)

    def update_model_version_metrics(
        self,
        model: Reference,
        version: Reference,
        metric_id: int,
        metrics: List[MetricInput],
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Creates model version metrics.

        :param model: The model name or id
        :param version: The model version name or id
        :param metric_id: The metrics id
        :param metrics: The metrics object
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return ModelVersionApi(self._auth).update_model_version_metrics(
            version,
            metric_id,
            metrics,
            model,
            project,
            workspace,
        )

    def create_model_version(
        self,
        data: ModelVersionInput,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ModelVersionOutput:
        """
        Creates a model version.

        :param data: The ModelVersionInput json structure
        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The ModelVersionOutput json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return ModelVersionApi(self._auth).create_model_version(data, model, project, workspace)

    def update_model_version(
        self,
        data: ModelVersionInput,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ModelVersionOutput:
        """
        Updates a model version.

        :param data: The ModelVersionInput json structure
        :param version: The model version name or id
        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The ModelVersionOutput json structure

        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return ModelVersionApi(self._auth).update_model_version(data, version, model, project, workspace)

    def delete_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Deletes a dataset version.

        :param version: The model version name or id
        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if isinstance(version, str) and isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        ModelVersionApi(self._auth).delete_model_version(version, model, project, workspace)

    def delete_model_version_metrics(
        self,
        version: Reference,
        metric_id: int,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Deletes a model version metric.

        :param version: The model version name or id
        :param metric_id: The metrics id
        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if isinstance(version, str) and isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return ModelVersionApi(self._auth).delete_model_version_metrics(version, metric_id, model, project, workspace)

    def delete_model_version_properties(
        self,
        version: Reference,
        property_id: int,
        model: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Deletes a model version property.

        :param version: The model version name or id
        :param property_id: The property id
        :param model: The model name or id
        :param project: The project name or id
        :param workspace: The workspace name or id
        :return: None
        """
        if isinstance(version, str) and isinstance(model, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return ModelVersionApi(self._auth).delete_model_version_properties(
            version, property_id, model, project, workspace
        )

    def get_attachment(
        self,
        _type: str,
        file_id: int,
        version: Optional[Reference] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> BinaryIO:
        """
        Downloads the specified attachment.

        :param _type: Artifact type of the attachment, it can be "datasetversion", "codeversion" or "modelversion"
        :param file_id: The file id
        :param version: The artifact version name or id
        :param artifact: The artifact name or id
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: BinaryIO
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return AttachmentApi(self._auth).get_attachment(_type, file_id, version, artifact, workspace, project)

    def create_attachments(
        self,
        _type: str,
        files: Optional[Sequence[Tuple[str, Tuple[Any, BinaryIO]]]],
        version: Optional[Reference] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ):
        """
        Creates an attachment

        :param _type: Artifact type of the attachment, it can be "datasetversion", "codeversion" or "modelversion"
        :param files: The paths to the files to attach
        :param version: The artifact version name or id
        :param artifact: The artifact name or id
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: The json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return AttachmentApi(self._auth).post_attachment(_type, version, files, artifact, workspace, project)

    def update_attachments(
        self,
        _type: str,
        files: Sequence[Tuple[str, Tuple[Any, BinaryIO]]],
        version: Optional[Reference] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ):
        """
        Updates an attachment.

        :param _type: Artifact type of the attachment, it can be "datasetversion", "codeversion" or "modelversion"
        :param files: The paths to the files to attach
        :param version: The artifact version name or id
        :param artifact: The artifact name or id
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: None
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return AttachmentApi(self._auth).update_attachments(_type, files, version, artifact, workspace, project)

    def delete_attachment(
        self,
        _type: str,
        version: Reference,
        file_id: int,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ):
        """
        Deletes an attachment.

        :param _type: Artifact type of the attachment, it can be "datasetversion", "codeversion" or "modelversion"
        :param version: The artifact version name or id
        :param file_id: The file id
        :param artifact: The artifact name or id
        :param workspace: The workspace name or id
        :param project: The project name or id


        :return: None
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return AttachmentApi(self._auth).delete_attachment(_type, version, file_id, artifact, workspace, project)

    def list_attachments(
        self,
        _type: str,
        version: Optional[Reference] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> PagedResponse[AttachmentOutput]:
        """
        Lists the attachments of an artifact.

        :param _type: Artifact type of the attachment, it can be "datasetversion", "codeversion" or "modelversion"
        :param version: The artifact version name or id
        :param artifact: The artifact name or id
        :param workspace: The workspace name or id
        :param project: The project name or id

        :return: PagedResponse[AttachmentOutput]
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return AttachmentApi(self._auth).list_attachments(_type, version, artifact, workspace, project)

    def get_connection(self, connection: Reference, workspace: Optional[Reference] = None) -> ConnectionOutput:
        """
        Gets the specified connection in a workspace.

        :param connection: The connection name or id
        :param workspace: The workspace name or id

        :return: The ConnectionOutput json structure
        """

        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if workspace is None:
            raise MissingReferenceError("workspace")
        return ConnectionApi(self._auth).get_connection(connection, workspace)

    def list_connections(
        self,
        workspace: Optional[Reference] = None,
        connection_type: Optional[str] = None,
        search: Optional[str] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> PagedResponse[ConnectionOutput]:
        """
        Lists the connections in a workspace.

        :param workspace: The workspace name or id
        :param search: A name to search for
        :param connection_type: The connection type to search for
        :param page_index: The page index
        :param page_size: The page size

        :return: PagedResponse[ConnectionOutput]
        """
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if workspace is None:
            raise MissingReferenceError("workspace")
        return ConnectionApi(self._auth).list_connections(workspace, connection_type, search, page_index, page_size)

    def create_connection(self, data: ConnectionInput, workspace: Optional[Reference] = None) -> ConnectionOutput:
        """
        Creates a connection in a workspace.

        :param data: The ConnectionInput json structure
        :param workspace: The workspace name or id

        :return: The ConnectionOutput json structure
        """
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if workspace is None:
            raise MissingReferenceError("workspace")
        return ConnectionApi(self._auth).create_connection(data, workspace)

    def delete_connection(self, connection: Reference, workspace: Optional[Reference] = None):
        """
        Deletes a connection from a workspace.

        :param connection: The connection name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if workspace is None:
            raise MissingReferenceError("workspace")
        ConnectionApi(self._auth).delete_connection(connection, workspace)

    def update_connection(
        self, data: ConnectionInput, connection: Reference, workspace: Optional[Reference] = None
    ) -> ConnectionOutput:
        """
        Updates a connection in a workspace.

        :param data: The new ConnectionInput json structure
        :param connection: The connection name or id
        :param workspace: The workspace name or id

        :return: The ConnectionOutput json structure
        """
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if workspace is None:
            raise MissingReferenceError("workspace")
        return ConnectionApi(self._auth).update_connection(data, connection, workspace)

    def create_code(
        self,
        code_data: CodeInput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeOutput:
        """
        Creates a code in a project.

        :param code_data: The CodeInput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The CodeOutput json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        result = CodeApi(self._auth).create_code(code_data, project, workspace)
        self._logger.info(f"Code with id: {result.id} successfully created.")
        return result

    def get_code(
        self,
        code: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeOutput:
        """
        Gets a code in a project.

        :param code: The code name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The CodeOutput json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        result = CodeApi(self._auth).get_code(code, project, workspace)
        self._logger.info(f"Code with id: {result.id} successfully retrieved.")
        return result

    def list_codes(
        self,
        project: Reference,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[CodeOutput]:
        """
        Lists the codes in a project.

        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: A name to search for
        :param page_index: The page index
        :param page_size: The page size

        :return: PagedResponse[CodeOutput]
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        return CodeApi(self._auth).list_codes(project, workspace, search, page_index, page_size)

    def update_code(
        self,
        code_data: CodeOutput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        """
        Updates a code in a project.

        :param code_data: The CodeOutput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The CodeOutput json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        result = CodeApi(self._auth).update_code(code_data, project, workspace)
        self._logger.info(f"Code with id: {result.id} successfully updated.")
        return result

    def delete_code(
        self,
        code: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes a code in a project.

        :param code: The code name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        code_id = CodeApi(self._auth).get_code(code, project, workspace).id
        CodeApi(self._auth).delete_code(code, project, workspace)
        self._logger.info(f"Code with id: {code_id} successfully deleted.")

    def create_code_version(
        self,
        code_data: CodeVersionInput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersionOutput:
        """
        Creates a code version.

        :param code_data: The CodeVersionInput json structure
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The CodeVersionOutput json structure
        """
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return CodeVersionApi(self._auth).create_code_version(code_data, project, workspace)

    def get_code_version(
        self,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersionOutput:
        """
        Gets a code version.

        :param version: The code version name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The CodeVersionOutput json structure
        """

        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return CodeVersionApi(self._auth).get_code_version(version, project, workspace)

    def list_code_versions(
        self,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> List[CodeVersionOutput]:
        """
        Lists the code versions in a project.

        :param project: The project name or id
        :param workspace: The workspace name or id
        :param search: A name to search for
        :param page_index: The page index
        :param page_size: The page size

        :return: List[CodeVersionOutput]
        """

        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return CodeVersionApi(self._auth).list_code_versions(project, workspace, search, page_index, page_size)

    def update_code_version(
        self,
        code_version_data: CodeVersionInput,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> CodeVersionOutput:
        """
        Updates a code version.

        :param code_version_data: The CodeVersionInput json structure
        :param version: The code version name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: The CodeVersionOutput json structure
        """

        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return CodeVersionApi(self._auth).update_code_version(code_version_data, version, project, workspace)

    def delete_code_version(
        self,
        version: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        """
        Deletes a code version.

        :param version: The code version name or id
        :param project: The project name or id
        :param workspace: The workspace name or id

        :return: None
        """
        if isinstance(version, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        code_version = CodeVersionApi(self._auth).get_code_version(version, project, workspace)
        version_id = code_version.id
        code_name = code_version.code.name
        CodeVersionApi(self._auth).delete_code_version(version, project, workspace)
        self._logger.info(f"CodeVersion with id: {version_id} successfully deleted from Code {code_name}.")

    def create_stage(
        self, data: StageInput, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> StageOutput:
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return StageApi(self._auth).create_stage(data, project, workspace)

    def update_stage(
        self,
        stage: Reference,
        data: StageInput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> StageOutput:
        if isinstance(stage, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return StageApi(self._auth).update_stage(data, stage, project, workspace)

    def get_stage(
        self, stage: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> StageOutput:
        if isinstance(stage, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return StageApi(self._auth).get_stage(stage, project, workspace)

    def list_stages(
        self,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
        search: Optional[str] = "",
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> List[StageOutput]:
        if project is None and self.project is not None:
            project = self.project.id
        elif isinstance(project, str):
            if workspace is None and self.workspace is not None:
                workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return StageApi(self._auth).list_stages(project, workspace, search, page_index, page_size)

    def delete_stage(
        self, stage: Reference, project: Optional[Reference] = None, workspace: Optional[Reference] = None
    ) -> None:
        if isinstance(stage, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
        return StageApi(self._auth).delete_stage(stage, project, workspace)

    def create_block(
        self,
        stage: Reference,
        data: BlockInput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> BlockOutput:
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return BlockApi(self._auth).create_block(stage, data, project, workspace)

    def update_block(
        self,
        position: int,
        stage: Reference,
        data: BlockInput,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> BlockOutput:
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return BlockApi(self._auth).update_block(position, stage, data, project, workspace)

    def delete_block(
        self,
        position: int,
        stage: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        if isinstance(stage, str):
            if project is None and self.project is not None:
                project = self.project.id
            elif isinstance(project, str):
                if workspace is None and self.workspace is not None:
                    workspace = self.workspace.id
            elif project is None and self.workspace is None:
                raise MissingReferenceError("project")
        return BlockApi(self._auth).delete_block(position, stage, project, workspace)

    def list_blocks(
        self,
        stage: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> List[BlockOutput]:
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        if project is None:
            raise MissingReferenceError("project")
        return BlockApi(self._auth).list_blocks(stage, project, workspace, search, page_index, page_size)
