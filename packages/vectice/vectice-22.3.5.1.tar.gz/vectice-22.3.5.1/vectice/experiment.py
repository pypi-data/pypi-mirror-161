from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Dict, List, Union, BinaryIO, Any, Tuple

from vectice import Vectice
from vectice.api import BadReferenceError, Reference, MissingReferenceError
from vectice.api.json import (
    JobArtifactType,
    ModelVersionStatus,
    RunStatus,
    JobType,
    VersionStrategy,
    ModelType,
    FileMetadata,
    StageStatus,
)
from vectice.integrations import Integrations
from vectice.models import ArtifactReference
from vectice.models import CodeVersion
from vectice.models import DatasetVersion, Dataset
from vectice.models import ModelVersion, Model
from vectice.models import Run


def _ensure_reference(item: Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]) -> ArtifactReference:
    if isinstance(item, ArtifactReference):
        return item
    elif isinstance(item, CodeVersion):
        return ArtifactReference(code=item.code_id, version_id=item.id)
    elif isinstance(item, ModelVersion):
        return ArtifactReference(model=item.model.id, version_id=item.id, description=item.description)
    elif isinstance(item, DatasetVersion):
        return ArtifactReference(dataset=item.dataset.id, version_id=item.id, description=item.description)
    else:
        raise RuntimeError(f"can not create artifact reference from unknown object '{item}'")


class Experiment:
    """
    High level API that manages adapter and low level client. Multiple models can belong to an Experiment.

    Manages a run and implicitly manages the dataset version, model version, code version etc of the run.

    The workflow follows: `tasks -> experiment.start() -> tasks -> experiment.complete() -> auxiliary tasks`

    As a consequence, we got by default:

    - Any Model/Dataset/Code **before** the call to :func:`~Experiment.start` is an input
    - Any Model/Dataset/Code **after** the call to :func:`~Experiment.start` is an output.

    Any Model/Dataset/Code can be assigned as an input or output if the use cases requires something beyond
    the generic workflow.

    """

    def __init__(
        self,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        user_token: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        lib: Optional[object] = None,
        auto_code: bool = False,
        allow_self_signed_certificate: bool = True,
        auto_log: bool = False,
        job_type: JobType = JobType.OTHER,
        check_remote_repository: bool = True,
    ):
        """
        :param user_token: The user token to access a Vectice organisation.
        :param workspace: The workspace name or id the user wants to access.
        :param project: The project name or id the user wants to access.
        :param job: The job the user wants to work with or create.
        :param job_type: The job type the user defines.
        """
        self.job = job
        self._vectice = Vectice(
            workspace,
            project,
            user_token,
            api_endpoint,
            lib,
            allow_self_signed_certificate,
            auto_log,
        )
        self._logger = logging.getLogger(self.__class__.__name__)
        self._auto_code = auto_code
        self._check_remote_repository = check_remote_repository
        self._inputs: List[ArtifactReference] = []
        self._outputs: List[ArtifactReference] = []
        self._active_run: Optional[Run] = None
        try:
            self._job = self._vectice.get_job(job)
        except BadReferenceError:
            if isinstance(job, str):
                self._job = self._vectice.create_job(name=job, type=job_type)

    def __repr__(self):
        lib = self._vectice._integration_client
        return (
            "Experiment("
            + f"job={self._job.name}"
            + f", project={self._job.project.name}"
            + f", workspace={self._job.project.workspace.name}"
            + f", auto_code={self._auto_code}"
            + f", api_endpoint={self._vectice._client._auth.api_base_url}"
            + f", lib={lib.lib_name()}"
            if lib is not None
            else "" + ")"
        )

    @property
    def vectice(self) -> Vectice:
        return self._vectice

    @property
    def inputs(self) -> List[ArtifactReference]:
        return self._inputs.copy()

    @property
    def outputs(self) -> List[ArtifactReference]:
        return self._outputs.copy()

    def _get_run(
        self,
        create_run: bool = False,
        auto_code: Optional[bool] = None,
        check_remote_repository: Optional[bool] = None,
        run_notes: Optional[str] = None,
        run_properties: Optional[Dict] = None,
        system_name: Optional[str] = None,
    ) -> Optional[Run]:
        if self._active_run is None and create_run:
            run = self._job.create_run(
                name=f"Run {datetime.now().isoformat()}",
                properties=run_properties,
                auto_code=auto_code if auto_code is not None else self._auto_code,
                check_remote_repository=check_remote_repository
                if check_remote_repository is not None
                else self._check_remote_repository,
                notes=run_notes,
                system_name=system_name,
            )
            self._active_run = run
        return self._active_run

    def _add_artifact_reference(
        self, artifact_reference: ArtifactReference, artifact_type: Optional[JobArtifactType] = None
    ):
        run = self._get_run(create_run=False)
        if run is None:
            if self._is_input(artifact_type):
                if artifact_reference not in self._inputs:
                    self._inputs.append(artifact_reference)
            else:
                if artifact_reference not in self._outputs:
                    self._outputs.append(artifact_reference)
        else:
            if self._is_input(artifact_type):
                run.add_input(artifact_reference)
            else:
                run.add_output(artifact_reference)

    def update_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        name: Optional[str] = None,
        system_name: Optional[str] = None,
        status: Optional[RunStatus] = None,
    ) -> Run:
        """
        Update a run.

        Updates the specified run with the new information.

        :param job: The job name or id
        :param run: The run name or id
        :param name: The name of the job
        :param system_name: The name of the system
        :param status: The status of the run

        :return: the updated Run
        """
        return self._vectice.update_run(run=run, job=job, name=name, system_name=system_name, status=status)

    def add_dataset_version(
        self,
        dataset: Reference,
        version_name: Optional[str] = None,
        version_number: Optional[int] = None,
        version_id: Optional[int] = None,
        version_strategy: VersionStrategy = VersionStrategy.AUTOMATIC,
        description: Optional[str] = None,
        is_starred: Optional[bool] = None,
        properties: Optional[Dict[str, Any]] = None,
        resources: Optional[List[str]] = None,
        metadata: Optional[List[FileMetadata]] = None,
        attachments: Optional[List[str]] = None,
        artifact_type: Optional[JobArtifactType] = None,
    ) -> ArtifactReference:
        """
        Adds a Dataset Version to the managed run.

        If the Dataset Version exists already then the existing Dataset Version is used. If the Dataset Version
        does not exist then the Dataset Version will be created and added to the managed run. The Dataset Version
        can be passed as an input or output; if it isn't then the workflow process is followed and added as
        an input or output. Resources are cloud provider assets e.g Google Cloud Storage with a connection in the
        Vectice UI and metadata are assets with no connection in Vectice UI.

        :param dataset: The dataset name or id
        :param version_name: The name of the dataset version e.g Changes 'Version 1' to 'name'
        :param description: The description of the dataset version
        :param is_starred: Whether the dataset version is starred
        :param properties: The properties of the dataset version
        :param resources: The resource uri/s of the dataset version
        :param metadata: The metadata uri/s of the dataset version
        :param artifact_type: indicate if the dataset version is an input ou an output
        :param attachments: The attachment of the code version

        :return: ArtifactReference
        """
        logging.getLogger("Project").propagate = False
        logging.getLogger("Dataset").propagate = False
        if version_id is not None or version_name is not None or version_number is not None:
            version_strategy = VersionStrategy.MANUAL

        is_exclusive = 0
        is_exclusive += 1 if version_id is not None else 0
        is_exclusive += 1 if version_name is not None else 0
        is_exclusive += 1 if version_number is not None else 0
        is_exclusive += 1 if version_strategy is not VersionStrategy.MANUAL else 0

        if is_exclusive > 1:
            raise RuntimeError(
                "You must declare only one version strategy (automatic/manual) and one version (id,name,number)"
            )

        if version_strategy == VersionStrategy.AUTOMATIC and resources is None and metadata is None:
            result = ArtifactReference(dataset=dataset, version_strategy=version_strategy)
        else:
            if version_id is not None:
                dataset_version = self.vectice.get_dataset_version(version_id, dataset)
                result = ArtifactReference(
                    dataset=dataset, version_id=version_id, description=dataset_version.description
                )
            elif version_number is not None:
                result = ArtifactReference(dataset=dataset, version_number=version_number)
            elif version_name is not None:
                try:
                    dataset_version = self.vectice.get_dataset_version(version_name, dataset)
                except Exception:
                    dataset_version = None
                    dataset_object = self.vectice.get_dataset(dataset)
                    project_id = self._vectice.project.id if self._vectice.project is not None else None
                    workspace_id = self._vectice.workspace.id if self._vectice.workspace is not None else None
                    if resources is None and metadata is None:
                        self.vectice.create_dataset_version(
                            dataset,
                            version_name,
                            project_id,
                            workspace_id,
                            description,
                            is_starred,
                            properties,
                            dataset_object.resources,
                            None,
                            attachments,
                        )
                    else:
                        self.vectice.create_dataset_version(
                            dataset,
                            version_name,
                            project_id,
                            workspace_id,
                            description,
                            is_starred,
                            properties,
                            resources,
                            metadata,
                            attachments,
                        )
                        # # self._logger.info(
                        # #     f"Changes detected automatically in resources for dataset {dataset_object.name}"
                        # # )
                        # #
                        # # self._logger.info(f"Changes detected automatically in resources for dataset {dataset_object.name}")
                        # # self._logger.info(f"Creating and using version with id: {dataset_version.id}")
                        # self._logger.info(
                        #     f"Changes detected automatically in resources for dataset {dataset_object.name}"
                        # )
                        # self._logger.info(f"Creating and using version with id: {dataset_version.id}")
                if dataset_version:
                    result = ArtifactReference(
                        dataset=dataset,
                        version_id=dataset_version.id,
                        version_name=version_name,
                        description=dataset_version.description,
                    )
                else:
                    result = ArtifactReference(dataset=dataset, version_name=version_name)
            else:
                project_id = self._vectice.project.id if self._vectice.project is not None else None
                workspace_id = self._vectice.workspace.id if self._vectice.workspace is not None else None
                dataset_object = self._vectice.get_dataset(dataset)
                if dataset_object.connection is None and resources is not None:
                    raise RuntimeError(
                        "can not create dataset version: Data resources can't be saved without a connection"
                    )
                logging.getLogger("Dataset").propagate = True
                dataset_version = self._vectice.create_dataset_version(
                    dataset,
                    None,
                    project_id,
                    workspace_id,
                    description,
                    is_starred,
                    properties,
                    resources,
                    metadata,
                    attachments,
                    version_strategy,
                )
                result = ArtifactReference(
                    dataset=dataset, version_id=dataset_version.id, description=dataset_version.description
                )
        logging.getLogger("Project").propagate = True
        logging.getLogger("Dataset").propagate = True
        self._add_artifact_reference(result, artifact_type)
        return result

    def update_dataset(
        self,
        dataset: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
        connection: Optional[Reference] = None,
    ) -> Dataset:
        """
        Updates a dataset

        Updates a dataset. The connection is associated with the resources, e.g gcs connection for a gcs resource.

        :param dataset: dataset name or id
        :param name: The name of the dataset version e.g Changes 'Version 1' to 'name'
        :param description: The description of the dataset version
        :param connection: The connection name or id

        :return: the updated Dataset
        """
        return self._vectice.update_dataset(dataset=dataset, name=name, description=description, connection=connection)

    def update_dataset_version(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_starred: Optional[bool] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DatasetVersion:
        """
        Updates the dataset version given by the user.

        :param dataset: dataset name or id
        :param version: The dataset version name or id
        :param name: The name of the dataset version e.g Changes 'Version 1' to 'name'
        :param description: The description of the dataset version
        :param is_starred: Whether the dataset version is starred
        :param properties: The properties of the dataset version

        :return: None
        """
        return self._vectice.update_dataset_version(
            version, dataset, None, None, name, description, is_starred, properties
        )

    def list_datasets(self, search: Optional[str] = None, page_index: int = 1, page_size: int = 20) -> List[Dataset]:
        """
        List all the Datasets associated with the project.

        :param search: A search term
        :param page_index: The page index
        :param page_size: The page size

        :return: A list of Datasets
        """
        return self._vectice.list_datasets(search=search, page_index=page_index, page_size=page_size)

    def list_dataset_versions(
        self, dataset: Reference, search: Optional[str] = None, page_index: int = 1, page_size: int = 20
    ) -> List[DatasetVersion]:
        """
        List the dataset versions.

        Lists the dataset versions of the specified dataset.

        :param dataset: dataset name or id

        :return: List of DatasetVersions
        """
        project_ref = None
        workspace_ref = None
        return self._vectice.list_dataset_versions(dataset, project_ref, workspace_ref, search, page_index, page_size)

    def get_dataset_version(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
    ) -> Optional[DatasetVersion]:
        """
        Get a dataset version.

        Gets a specific dataset version of the specified dataset.

        :param version: The dataset version name or id
        :param dataset: dataset name or id if the version is a name

        :return: A DatasetVersion
        """
        return self._vectice.get_dataset_version(version, dataset)

    def delete_dataset_version(
        self,
        version: Reference,
        dataset: Optional[Reference] = None,
    ) -> None:
        """
        Delete a dataset version.

        Deletes a specific dataset in the specified project.

        :param dataset: dataset name or id
        :param version: The dataset version name or id

        :return: None
        """
        self._vectice.delete_dataset_version(version, dataset)

    def start(
        self,
        auto_code: Optional[bool] = None,
        check_remote_repository: Optional[bool] = None,
        run_notes: Optional[str] = None,
        run_properties: Optional[Dict] = None,
        system_name: Optional[str] = None,
        inputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None,
    ) -> Run:
        """
        Start the current experiments run.

        Once the run has started, all the Dataset/Model/Code Versions
        will be captured as outputs of the run.

        The group name allow to group several runs in one global run

        :return: Run
        """
        if inputs is not None:
            artifacts_references_inputs = [_ensure_reference(item) for item in inputs if item is not None]
            self._inputs.extend(artifacts_references_inputs)
        current_run = self._get_run(
            create_run=True,
            auto_code=auto_code,
            check_remote_repository=check_remote_repository,
            run_notes=run_notes,
            run_properties=run_properties,
            system_name=system_name,
        )
        if current_run is not None and current_run.status == RunStatus.STARTED:
            current_run.abort(reason="aborted as requesting a new Run in experiment")
            self._active_run = None
            current_run = self._get_run(
                create_run=True,
                auto_code=auto_code,
                check_remote_repository=check_remote_repository,
                run_notes=run_notes,
                run_properties=run_properties,
                system_name=system_name,
            )
        elif current_run is not None and current_run.status == RunStatus.COMPLETED:
            self._active_run = None
            self._inputs = []
            self._outputs = []
            current_run = self._get_run(
                create_run=True,
                auto_code=auto_code,
                check_remote_repository=check_remote_repository,
                run_notes=run_notes,
                run_properties=run_properties,
                system_name=system_name,
            )
        if current_run is not None:
            for input in self._inputs:
                current_run.add_input(input)
            for output in self._outputs:
                current_run.add_output(output)
            current_run.start(auto_code=auto_code, check_remote_repository=check_remote_repository)
            return current_run
        else:
            raise RuntimeError("can not create run")

    def complete(
        self, outputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None
    ) -> None:
        """
        Complete the current experiment run.

        Once the run is complete. All the Dataset/Model/Code Version/s will be captured as outputs to
        the run, that were done after the experiment.start().

        :return: None
        """
        current_run = self._get_run(create_run=False)
        if current_run is not None:
            if outputs is not None:
                artifacts_references_outputs = [_ensure_reference(item) for item in outputs if item is not None]
                current_run.add_outputs(artifacts_references_outputs)
            if self._outputs is not None:
                current_run.add_outputs(self._outputs)
            current_run.complete()
            if self._vectice._auto_document_run:
                """
                Captures an existing run. That is still running.
                """
                if self._vectice._document_stage is not None:
                    try:
                        stage = self._vectice.get_stage(self._vectice._document_stage)
                    except Exception:
                        logging.debug(f"Stage {self._vectice._document_stage} for auto documentation not found.")
                        stage = self._vectice.create_stage(self._vectice._document_stage, status=StageStatus.InProgress)
                else:
                    stage = self._vectice.create_stage(
                        f"Auto Document {current_run.name}", status=StageStatus.InProgress
                    )
                current_run._capture_run_info(stage)
        self._active_run = None
        self._inputs = []
        self._outputs = []

    def fail(
        self,
        reason: Optional[str] = None,
        outputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None,
    ) -> None:
        """
        Fail the current experiment run.

        Marks the experiment run as failed. Which will appear as the runs' STATUS, this can be viewed
        in the Vectice UI.

        :param reason: indicate why the run failed

        :return: None
        """
        current_run = self._get_run(create_run=False)
        if current_run is not None:
            if outputs is not None:
                artifacts_references_outputs = [_ensure_reference(item) for item in outputs if item is not None]
                current_run.add_outputs(artifacts_references_outputs)
            current_run.fail(reason=reason)
        self._active_run = None

    def abort(self, reason: Optional[str] = None) -> None:
        """
        Abort the current experiment run.

        Marks the experiment run as aborted. Which will appear as the runs' STATUS, this can be viewed
        in the Vectice UI.

        :param reason: Indicates why the run was aborted

        :return: None
        """
        current_run = self._get_run(create_run=False)
        if current_run is not None:
            current_run.abort(reason=reason)
        self._active_run = None

    def add_model_version_attachment(
        self,
        file: str,
        model_version: Optional[Reference] = None,
        model: Optional[Reference] = None,
    ) -> None:
        """
        attach a file to an existing Model Version.

        The Model Version Attachment will be added and associated to the Model Version if it exists.
        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation
        is successful. The Attachment can be seen in the Vectice UI or interacted with with the Python SDK.

        :param file: A file to attach on the model version
        :param model: The model name or id
        :param model_version: The model version name or id

        :return: None
        """
        if model is None and model_version is None:
            model, model_version = self._get_model_version_in_outputs()
            if model is None or model_version is None:
                raise MissingReferenceError("model version")
        if model_version is None:
            raise MissingReferenceError("model version")
        self._vectice.add_model_version_attachment(file, model_version, model)

    def delete_model_version_attachment(
        self,
        file: str,
        model_version: Reference,
        model: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the specified attachment from the model version.

        :param model: The model name or id
        :param model_version: The model version name or id
        :param file: The file name

        :return: None
        """
        self._vectice.delete_model_version_attachment(file, model_version, model)

    def get_model_version_attachment(
        self,
        file: str,
        model_version: Reference,
        model: Optional[Reference] = None,
    ) -> Optional[BinaryIO]:
        """
        Get a model version attachment.

        Gets the attachment of a model version.

        :param model: The model name or id
        :param model_version: The model version name or id
        :param file: The file name

        :return: An Artifact Version Attachment
        """
        return self._vectice.get_model_version_attachment(file, model_version, model)

    def list_models(self, search: Optional[str] = None, page_index: int = 1, page_size: int = 20) -> List[Model]:
        """
        List all the Models associated with the project.

        :param search: A search term
        :param page_index: The page index
        :param page_size: The page size

        :return: A list of Models
        """
        return self._vectice.list_models(search=search, page_index=page_index, page_size=page_size)

    def list_model_version_attachments(
        self,
        model_version: Reference,
        model: Optional[Reference] = None,
    ) -> List[str]:
        """
        List the files attached to a Model version.

        :param model: The model name or id
        :param model_version: The model version name or id

        :return: A list of file names
        """
        return self._vectice.list_model_version_attachments(model_version, model)

    def add_dataset_version_attachment(
        self,
        file: str,
        dataset_version: Reference,
        dataset: Optional[Reference] = None,
    ) -> None:
        """
        Adds a Dataset Version Attachment to an existing Dataset Version.

        The Dataset Version Attachment will be added and associated to the Dataset Version if it exists.
        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation
        is successful. The Attachment can be seen in the Vectice UI or interacted with with the Python SDK.

        :param file: A file to attach on the dataset version
        :param dataset: The dataset name or id
        :param dataset_version: The dataset version name or id

        :return: None
        """
        self._vectice.add_dataset_version_attachment(file, dataset_version, dataset)

    def get_dataset_version_attachment(
        self,
        file: str,
        dataset_version: Reference,
        dataset: Optional[Reference] = None,
    ) -> Optional[BinaryIO]:
        """
        Get a dataset version attachment.

        Gets the attachment of a dataset version.

        :param file: The file name
        :param dataset_version: The dataset version name or id
        :param dataset: The dataset name or id

        :return: An Artifact Version Attachment
        """
        return self._vectice.get_dataset_version_attachment(file, dataset_version, dataset)

    def delete_dataset_version_attachment(
        self,
        file: str,
        dataset_version: Reference,
        dataset: Optional[Reference] = None,
    ) -> None:
        """
        Deletes the specified attachment from the dataset version.

        :param dataset: The dataset name or id
        :param dataset_version: The dataset version name or id
        :param file: The file name

        :return: None
        """
        self._vectice.delete_dataset_version_attachment(file, dataset_version, dataset)

    def list_dataset_version_attachments(
        self,
        dataset_version: Reference,
        dataset: Optional[Reference] = None,
    ) -> List[str]:
        """
        List the files attached to a Dataset version.

        :param dataset: The dataset name or id
        :param dataset_version: The dataset version name or id

        :return: An Artifact Version Attachment
        """
        return self._vectice.list_dataset_version_attachments(dataset_version, dataset)

    def add_code_version_attachment(
        self,
        file: str,
        code_version: Reference,
    ) -> None:
        """
        Adds a Code Version Attachment to an existing Code Version.

        The Code Version Attachment will be added and associated to the Code Version if it exists.
        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation
        is successful. The Attachment can be seen in the Vectice UI or interacted with with the Python SDK.


        :param file: A file to attach on the dataset version
        :param code_version: The code version name or id

        :return: None
        """
        self._vectice.add_code_version_attachment(file, code_version)

    def delete_code_version_attachment(
        self,
        file: str,
        code_version: Reference,
    ) -> None:
        """
        Delete a Code Version Attachment.

        Deletes the specified attachment from the code version.

        :param code_version: The code version name or id
        :param file: The file name

        :return: None
        """
        self._vectice.delete_code_version_attachment(file, code_version)

    def get_code_version_attachment(
        self,
        file: str,
        code_version: Reference,
    ) -> Optional[BinaryIO]:
        """
        Get a code version attachment.

        Gets the attachment of a code version.

        :param code_version: The code version name or id
        :param file: The file name

        :return: A list of file name or uri
        """
        return self._vectice.get_code_version_attachment(file, code_version)

    def list_code_version_attachments(
        self,
        code_version: Reference,
    ) -> List[str]:
        """
        List the files attached to a Code version.

        :param code_version: The code version name or id
        :return: A list of file name or uri
        """
        return self._vectice.list_code_version_attachments(code_version)

    def add_run_attachment(
        self,
        file: str,
        run: Reference,
        job: Optional[Reference] = None,
    ) -> None:
        """
        Adds a Code Version Attachment to an existing Code Version.

        The Code Version Attachment will be added and associated to the Code Version if it exists.
        The Attachment is directly uploaded to Vectice and can be viewed immediately if the operation
        is successful. The Attachment can be seen in the Vectice UI or interacted with with the Python SDK.

        :param file: A file to attach on the dataset version
        :param run: The run name or id
        :param job: The job name or id
        :return: None
        """
        return self._vectice.add_run_attachment(file, run, job)

    def delete_run_attachment(
        self,
        file: str,
        run: Reference,
        job: Optional[Reference] = None,
    ) -> None:
        """
        Delete a Code Version Attachment.

        Deletes the specified attachment from the code version.

        :param run: The run name or id
        :param job: The job name or id
        :param file: The file name

        :return: None
        """
        self._vectice.delete_run_attachment(file, run, job)

    def get_run_attachment(
        self,
        file: str,
        run: Reference,
        job: Optional[Reference] = None,
    ) -> Optional[BinaryIO]:
        """
        Get a code version attachment.

        Gets the attachment of a code version.

        :param run: The run name or id
        :param job: The job name or id
        :param file: The file name

        :return: A list of file name or uri
        """
        return self._vectice.get_run_attachment(file, run, job)

    def list_run_attachments(
        self,
        run: Reference,
        job: Optional[Reference] = None,
    ) -> List[str]:
        """
        List the files attached to a Code version.

        :param run: The run name or id
        :param job: The job name or id
        :return: A list of file name or uri
        """
        return self._vectice.list_run_attachments(run, job)

    def _is_input(self, artifact_type: Optional[JobArtifactType] = None) -> bool:
        if artifact_type == JobArtifactType.INPUT:
            return True
        elif artifact_type == JobArtifactType.OUTPUT:
            return False
        else:
            run = self._get_run(create_run=False)
            if run is None:
                return True
            else:
                return run.status == RunStatus.SCHEDULED

    def add_model_version(
        self,
        model: Reference,
        version_name: Optional[str] = None,
        version_number: Optional[int] = None,
        version_id: Optional[int] = None,
        algorithm: Optional[str] = None,
        status: ModelVersionStatus = ModelVersionStatus.EXPERIMENTATION,
        hyper_parameters: Optional[Dict] = None,
        metrics: Optional[Dict] = None,
        artifact_type: Optional[JobArtifactType] = None,
        attachment: Optional[Union[str, List[str]]] = None,
    ) -> ArtifactReference:
        """
        Adds a Model Version to the managed run.

        If the Model Version exists already then the existing Model Version is used. If the Model Version
        does not exist then the Model Version will be created and added to the managed run. The Model Version
        can be passed as an input or output; if it isn't then the workflow process is followed and added as
        an input or output.

        :param model: The model reference (model name or model id)
        :param version_name: The name of the model version (Does not assign a Version Name)
        :param algorithm: The models' algorithm
        :param status: The model status 'EXPERIMENTATION'/'STAGING'/'PRODUCTION'
        :param hyper_parameters: The hyper parameters of the model
        :param metrics: The metrics of the model
        :param artifact_type: indicate if the model version is an input ou an output
        :param attachment: The attachment of the code version

        :return: None
        """
        try:
            parent_model = self._vectice.get_model(model)
        except BadReferenceError:
            parent_model = None
        if parent_model is None and (version_id is not None or version_number is not None):
            raise ValueError("Please provide a valid model and model version reference")

        if version_id is not None and parent_model is not None:
            model_version = self._vectice.get_model_version(version=version_id, model=parent_model.id)
            result = ArtifactReference(model=model, version_id=version_id, description=model_version.description)
        elif version_name is not None and parent_model is not None:
            try:
                model_version = self._vectice.get_model_version(version=version_name, model=parent_model.id)
                result = ArtifactReference(
                    model=model,
                    version_name=version_name,
                    description=model_version.description,
                    version_id=model_version.id,
                )
            except BadReferenceError:
                result = None
        elif version_number is not None and parent_model is not None:
            result = ArtifactReference(model=model, version_number=version_number)
        else:
            result = None

        if isinstance(model, str) and parent_model is None:
            parent_model = self._vectice.create_model(model)
        elif parent_model is None:
            raise ValueError(
                f"{model} was not found and a string is needed to create a model. Please provide a valid input."
            )

        if parent_model and result is None:
            model_version = parent_model.create_model_version(
                name=version_name,
                status=status,
                algorithm_name=algorithm,
                metrics=metrics,
                hyper_parameters=hyper_parameters,
                runId=None if self._active_run is None else self._active_run.id,
            )
            result = ArtifactReference(
                model=model,
                version_name=model_version.name,
                version_id=model_version.id,
                description=model_version.description,
            )
            if attachment:
                model_version.add_attachments(attachment)
        if result:
            self._add_artifact_reference(result, artifact_type)
        else:
            raise ValueError("Please check the inputs provided.")
        return result

    def update_model(
        self,
        model: Reference,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[ModelType] = ModelType.OTHER,
    ) -> Model:
        """
        Update a model.

        :param model: The model name or id
        :param name: The name of the model
        :param description: The description of the model
        :param type: The model type

        :return: Model
        """
        return self._vectice.update_model(model=model, name=name, description=description, type=type)

    def update_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[ModelVersionStatus] = ModelVersionStatus.EXPERIMENTATION,
        algorithm: Optional[str] = None,
        is_starred: Optional[bool] = False,
        metrics: Optional[Dict] = None,
        hyper_parameters: Optional[Dict] = None,
    ) -> ModelVersion:
        """
        Update a Model Version to the managed run.

        Updates the specified model version with the new params passed to this function.

        :param model: The model name or id the version belongs to
        :param version: The model version name or id
        :param name: The name of the model
        :param description: The description of the model
        :param status: The status of the model e.g 'EXPERIMENTATION'/'STAGING'/'PRODUCTION'
        :param algorithm: The algorithm the model version uses
        :param is_starred: Whether the model is starred or not
        :param metrics: The model version metrics
        :param hyper_parameters: The model version hyper parameters

        :return: None
        """
        return self._vectice.update_model_version(
            version, model, None, None, name, description, status, algorithm, is_starred, metrics, hyper_parameters
        )

    def list_model_versions(
        self, model: Reference, search: Optional[str] = None, page_index: int = 1, page_size: int = 20
    ) -> List[ModelVersion]:
        """
        List the model versions of a model.

        Lists all the versions created out of the specified model.

        :param model: The model name or id the versions belongs to

        :return: List of ModelVersions
        """
        return self._vectice.list_model_versions(model, search=search, page_index=page_index, page_size=page_size)

    def list_model_versions_dataframe(
        self, model: Reference, search: Optional[str] = None, page_index: int = 1, page_size: int = 20
    ) -> "pandas.DataFrame":  # type: ignore # noqa F821
        return self._vectice.list_model_versions_dataframe(
            model, search=search, page_index=page_index, page_size=page_size
        )

    def get_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
    ) -> ModelVersion:
        """
        Gets a specific version of a model.

        :param model: The model name or id the version belongs to
        :param version: The model version name or id

        :return: A ModelVersion
        """
        return self._vectice.get_model_version(version, model)

    def delete_model_version(
        self,
        version: Reference,
        model: Optional[Reference] = None,
    ) -> None:
        """
        Delete a model version.

        Deletes the specified version of a model.

        :param model: The model name or id the version belongs to
        :param version: The model version name or id

        :return: None
        """
        self._vectice.delete_model_version(version, model)

    def add_code_version(
        self,
        git_path: str = ".",
        check_remote_repository: bool = True,
        attachments: Optional[Union[str, List[str]]] = None,
    ) -> Optional[CodeVersion]:
        """
        Adds a Code Version to the managed run.

        Creates a code version in the specified project using the git repository path of the code version.

        :param git_path: The path to the git repository
        :param check_remote_repository: Indicate if we check file existence in remote repository
        :param attachments: Resources to attach to the code version e.g AWS S3 or local files

        :return: A CodeVersion
        """
        code_version = self._vectice.create_code_version(
            script_relative_path=git_path, check_remote_repository=check_remote_repository, attachments=attachments
        )
        if code_version is not None:
            self._add_artifact_reference(ArtifactReference(code=code_version.code_id, version_id=code_version.id))
        return code_version

    def add_code_version_uri(
        self,
        git_uri: str,
        entrypoint: str,
        artifact_type: Optional[JobArtifactType] = None,
        login_or_token: Optional[str] = None,
        password: Optional[str] = None,
        oauth2_token: Optional[str] = None,
        attachment: Optional[Union[str, List[str]]] = None,
    ) -> Optional[CodeVersion]:
        """
        Adds a Code Version to the managed run.

        If the Code Version exists already then the existing Code Version is used. If the Code Version
        does not exist then the Code Version will be created and added to the managed run. The Code Version
        can be passed as an input or output; if it isn't then the workflow process is followed and added as
        an input or output.

        :param git_uri: The uri of the file or folder in github/bitbucket/gitlab
        :param entrypoint: The relative path of the file or folder e.g folder/file.py
        :param artifact_type: indicate if the code version is an input ou an output
        :param login_or_token: A real login or a personal access token
        :param password: The password
        :param oauth2_token: The OAuth2 access token
        :param attachment: The attachment of the code version

        :return: None
        """

        git_version = Integrations.create_code_version_with_uri(
            git_uri, entrypoint, login_or_token, password, oauth2_token
        )
        if git_version is None:
            return None
        code_version = self._vectice.create_code_version(
            uri=git_version.uri, project=self._job.project.id, git_version=git_version
        )
        if isinstance(attachment, List):
            for item in attachment:
                if item is not None:
                    code_version.add_attachments(item)
        else:
            if attachment is not None:
                code_version.add_attachments(attachment)
        self._add_artifact_reference(
            ArtifactReference(code=code_version.code_id, version_id=code_version.id), artifact_type=artifact_type
        )
        return code_version

    def update_code_version(
        self,
        code_version: Reference,
        repository_name: str,
        branch_name: str,
        commit_hash: str,
        commit_comment: str,
        commit_author_name: str,
        commit_author_email: str,
        is_dirty: bool,
        uri: str,
        entrypoint: Optional[str] = None,
    ) -> None:
        """
        Update a code version.

        Updates the specified code version with the new given information in the params.

        :param code_version: The code version name or id
        :param repository_name: The repository name
        :param branch_name: The branch name
        :param commit_hash: The commit hash
        :param commit_comment: The commit comment
        :param commit_author_name: The commit author name
        :param commit_author_email: The commit author email
        :param is_dirty: Whether the commit is dirty
        :param uri: The uri
        :param entrypoint: The entrypoint

        :return: None
        """
        self._vectice.update_code_version(
            code_version,
            repository_name,
            branch_name,
            commit_hash=commit_hash,
            commit_comment=commit_comment,
            commit_author_name=commit_author_name,
            commit_author_email=commit_author_email,
            is_dirty=is_dirty,
            uri=uri,
            entrypoint=entrypoint,
        )

    def get_code_version(
        self,
        code_version: Reference,
    ) -> Optional[CodeVersion]:
        """
        Get a code version.

        Gets the specified version of a code artifact.

        :param code_version: The code version name or id

        :return: A CodeVersion
        """
        return self._vectice.get_code_version(code_version)

    def list_code_versions(
        self, search: Optional[str] = None, page_index: int = 1, page_size: int = 20
    ) -> Optional[List[CodeVersion]]:
        """
        List the code versions.

        Lists all the versions of a code artifact.

        :param search: A text to search for
        :param page_index: The page index
        :param page_size: The page size

        :return: A List of CodeVersions
        """
        return self._vectice.list_code_versions(search=search, page_index=page_index, page_size=page_size)

    def delete_code_version(
        self,
        code_version: Reference,
    ) -> None:
        """
        Delete a code version.

        Deletes the specified version of a code artifact.

        :param code_version: The code version name or id

        :return: None
        """
        self._vectice.delete_code_version(code_version)

    def _get_model_version_in_outputs(self) -> Tuple[Union[str, int, None], Union[str, int, None]]:
        run = self._get_run(create_run=False)
        if run:
            outputs = [item for item in run.outputs if item.model is not None]
        else:
            outputs = None
        if outputs and len(outputs) == 1:
            model = outputs[0].model
            if outputs[0].version_id:
                model_version: Union[str, int, None] = outputs[0].version_id
            elif outputs[0].version_name:
                model_version = outputs[0].version_name
            elif outputs[0].version_number:
                if model:
                    model_version = self.list_model_versions(model, search=str(outputs[0].version_number))[0].id
                else:
                    model_version = None
            else:
                model_version = None
            return model, model_version
        else:
            return None, None

    def log_metric(
        self,
        key: str,
        value: int,
        model_version: Optional[Reference] = None,
        model: Optional[Reference] = None,
        step: Optional[int] = None,
        epoch: Optional[int] = None,
    ) -> None:
        """
        Logs a metric to the Model Version specified.

        If the Model Version is not found the operation will fail. If the Model Version is found in the input or outputs
        the metrics will be directly uploaded to Vectice and assigned to the Model Version.
        A key is the metric name and the value is the metric value. Step and epoch are for deep learning models metrics.


        :param model: The model name or id
        :param model_version: The model version name or id/number
        :param key: The metric key
        :param value: The metric value
        :param step: The metric step
        :param epoch: The metric epoch

        :return: None
        """
        if model is None and model_version is None:
            model, model_version = self._get_model_version_in_outputs()
            if model is None or model_version is None:
                raise MissingReferenceError("model version")
        if model_version is None:
            raise MissingReferenceError("model version")
        self._vectice.get_model_version(model_version, model).create_metrics(metrics={key: value})

    def log_metrics(
        self,
        metrics: Dict,
        model: Optional[Reference] = None,
        model_version: Optional[Reference] = None,
        step: Optional[int] = None,
        epoch: Optional[int] = None,
    ) -> None:
        """
        Logs a dictionary of metrics to the Model Version specified.

        If the Model Version is not found the operation will fail. If the Model Version is found in the input or outputs
        the metrics will be directly uploaded to Vectice and assigned to the Model Version. A dictionary with the key,
        value, epoch and step is accepted.

        :param metrics: A dictionary of metrics
        :param model: The model name or id
        :param model_version: The model version name or id/number
        :param step: The metric step
        :param epoch: The metric epoch
        :return: None
        """
        if model is None and model_version is None:
            model, model_version = self._get_model_version_in_outputs()
            if model is None or model_version is None:
                raise MissingReferenceError("model version")
        if model_version is None:
            raise MissingReferenceError("model version")
        self._vectice.get_model_version(model_version, model).create_metrics(metrics=metrics)

    def list_metrics(
        self,
        model_version: Reference,
        model: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 20,
    ) -> Optional[Dict[str, Any]]:
        """
        Lists the metrics used for the specified model version.

        :param model: The model name or id the version belongs to
        :param model_version: The model version name or id
        :param search: A text to search for
        :param page_index: The page index
        :param page_size: The page size

        :return: A List of Metrics
        """
        return self._vectice.get_model_version(model_version, model).list_metrics(
            search=search, page_index=page_index, page_size=page_size
        )

    def delete_metrics(
        self,
        model_version: Reference,
        metrics: List[str],
        model: Optional[Reference] = None,
    ) -> None:
        """
        Delete a model version metric.

        Deletes a metric used for the specified model version.

        :param model: The model name or id the version belongs to
        :param model_version: The model version name or id
        :param metrics: The metric keys to delete

        :return: None
        """
        self._vectice.delete_model_version_metrics(model_version, metrics, model)

    def log_hyper_parameter(
        self,
        key: str,
        value: Union[int, float, str],
        model: Optional[Reference] = None,
        model_version: Optional[Reference] = None,
    ) -> None:
        """
        Logs a hyper parameter to the Model Version specified.

        If the Model Version is not found the operation will fail. If the Model Version is found in the input or outputs
        the hyper parameter will be directly uploaded to Vectice and assigned to the Model Version.
        A key is the hyper parameter name and the value is the metric value.

        :param key: The hyper parameter key
        :param value: The hyper parameter value
        :param model: The model name or id
        :param model_version: The model version name or id/number

        :return: None
        """
        if model is None and model_version is None:
            model, model_version = self._get_model_version_in_outputs()
            if model is None or model_version is None:
                raise MissingReferenceError("model version")
        if model_version is None:
            raise MissingReferenceError("model version")
        self._vectice.get_model_version(model_version, model).create_hyper_parameters(hyper_parameters={key: value})

    def log_hyper_parameters(
        self,
        hyper_parameters: Dict,
        model: Optional[Reference] = None,
        model_version: Optional[Reference] = None,
    ) -> None:
        """
        Update a model version hyper parameters.

        If the Model Version is not found the operation will fail. If the Model Version is found in the input or outputs
        the metrics will be directly uploaded to Vectice and assigned to the Model Version. A dictionary with multiple
        key and value pairs is accepted.

        :param hyper_parameters: The hyper_parameter ids or keys
        :param model: The model name or id the version belongs to
        :param model_version: The model version name or id

        :return: None
        """
        if model is None and model_version is None:
            model, model_version = self._get_model_version_in_outputs()
            if model is None or model_version is None:
                raise MissingReferenceError("model version")
        if model_version is None:
            raise MissingReferenceError("model version")
        self._vectice.get_model_version(model_version, model).create_hyper_parameters(hyper_parameters=hyper_parameters)

    def list_hyper_parameters(
        self,
        model_version: Reference,
        model: Optional[Reference] = None,
    ) -> Dict:
        """
        List the model version hyper parameters.

        :param model: The model name or id the version belongs to
        :param model_version: The model version name or id

        :return: A map containing the hyper parameters
        """
        return self._vectice.get_model_version(model_version, model).list_hyper_parameters()

    def delete_hyper_parameters(
        self,
        model_version: Reference,
        keys: List[str],
        model: Optional[Reference] = None,
    ) -> None:
        """
        Delete the model version hyper parameters

        Deletes the hyper parameters used for the specified model.

        :param keys: The list of keys to delete
        :param model: The model name or id the version belongs to
        :param model_version: The model version name or id

        :return: None
        """
        self._vectice.delete_model_version_hyper_parameters(model_version, keys, model)

    def document_run(self, run_id: Optional[int] = None, name: Optional[str] = None) -> None:
        """
        Captures all the assets of a run in a stage and documentation.

        :param run_id: The id of the run.
        :param name: The name of the stage.

        :return: None
        """
        if run_id is None:
            run = self._get_run(create_run=False)
        else:
            run = self._vectice.get_run(run_id)
            if run and run.status != RunStatus.COMPLETED:
                logging.warning(
                    "The run is not in a completed state and the auto documentation might not function as expected."
                )
            if name is not None:
                try:
                    stage = self._vectice.get_stage(name)
                except Exception:
                    logging.debug(f"Stage {name} for auto documentation not found.")
                    stage = self._vectice.create_stage(name, status=StageStatus.InProgress)
            else:
                stage = self._vectice.create_stage(f"Auto Document {run.name}", status=StageStatus.InProgress)
            run._capture_run_info(stage)
        if run_id is None and run is None:
            raise ValueError("Please provide a run ID or ensure there is an active run.")
        self._vectice.document_run(name=name, _experiment_run=run)
