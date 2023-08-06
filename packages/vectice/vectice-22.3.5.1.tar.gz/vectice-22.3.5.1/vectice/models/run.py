from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Union, Dict, Tuple

from vectice.api.json import (
    RunStatus,
    ArtifactType,
    StopRunInput,
    ArtifactVersion,
    ArtifactReferenceInput,
    RulesDatasetVersionInput,
    RulesModelVersionInput,
    RulesCodeVersionInput,
    RunInput,
    JobInput,
    StartRunInput,
    ArtifactReferenceOutput,
    VersionStrategy,
)
from vectice.models import CodeVersion
from vectice.models import DatasetVersion
from vectice.models import ModelVersion
from .artifact_reference import ArtifactReference
from .attachment_container import AttachmentContainer
from .git_version import GitVersion
from .integration import AbstractIntegration

if TYPE_CHECKING:
    from vectice.models import Job, Stage


logger = logging.getLogger(__name__)


HEADERS = {
    "dataset": "The Dataset Used:",
    "datasets": "The Datasets Used:",
    "model": "The Model Used:",
    "models": "The Models Used:",
    "modelversion": "The Model Version Used:",
    "modelversions": "The Model Versions Used:",
    "mixed": "The Models And Datasets Used:",
    "dataset output": "The Output Dataset:",
    "datasets output": "The Output Datasets:",
    "model output": "The Output Model:",
    "models output": "The Output Models:",
    "modelversion output": "The Output Model Version:",
    "modelversions output": "The Output Model Versions:",
    "mixed output": "The Output Models And Datasets:",
}


def select_header(items, input=False, output=False) -> Tuple[str, bool]:
    datasets, dataset_versions, models, model_versions = 0, 0, 0, 0

    for item in items:
        if (
            (item.artifact_type.name == "DATASET" and item.version_id)
            or (item.artifact_type.name == "DATASET" and item.version_name)
            or (item.artifact_type.name == "DATASET" and item.version_strategy.value == "AUTOMATIC")
        ):
            dataset_versions += 1
        elif item.artifact_type.name == "DATASET":
            datasets += 1
        elif (item.artifact_type.name == "MODEL" and item.version_id) or (
            item.artifact_type.name == "MODEL" and item.version_name
        ):
            model_versions += 1
        elif item.artifact_type.name == "MODEL":
            models += 1

    if (datasets == 1 or dataset_versions == 1) and models == 0 and model_versions == 0 and input is True:
        return HEADERS["dataset"], False

    elif (datasets >= 1 or dataset_versions >= 1) and models == 0 and model_versions == 0 and input is True:
        return HEADERS["datasets"], True

    elif datasets == 0 and models == 1 and model_versions == 0 and dataset_versions == 0 and input is True:
        return HEADERS["model"], False

    elif datasets == 0 and models >= 1 and model_versions == 0 and dataset_versions == 0 and input is True:
        return HEADERS["models"], True

    elif datasets == 0 and models == 0 and model_versions == 1 and dataset_versions == 0 and input is True:
        return HEADERS["modelversion"], False

    elif datasets == 0 and (models >= 1 or model_versions >= 1) and dataset_versions == 0 and input is True:
        return HEADERS["models"], True

    elif (
        (input is True and datasets >= 1 and models >= 1)
        or (input is True and model_versions >= 1 and dataset_versions >= 1)
        or (input is True and datasets >= 1 and model_versions >= 1)
        or (input is True and models >= 1 and dataset_versions >= 1)
    ):
        return HEADERS["mixed"], True

    elif (datasets == 1 or dataset_versions == 1) and models == 0 and model_versions == 0 and output is True:
        return HEADERS["dataset output"], False

    elif (datasets >= 1 or dataset_versions >= 1) and models == 0 and model_versions == 0 and output is True:
        return HEADERS["datasets output"], True

    elif datasets == 0 and models == 1 and model_versions == 0 and dataset_versions == 0 and output is True:
        return HEADERS["model output"], False

    elif datasets == 0 and models >= 1 and model_versions == 0 and dataset_versions == 0 and output is True:
        return HEADERS["models output"], True

    elif datasets == 0 and models == 0 and model_versions == 1 and dataset_versions == 0 and output is True:
        return HEADERS["modelversion output"], False

    elif datasets == 0 and models == 0 and model_versions >= 1 and dataset_versions == 0 and output is True:
        return HEADERS["modelversions output"], True

    elif datasets == 0 and (models >= 1 or model_versions >= 1) and dataset_versions == 0 and output is True:
        return HEADERS["models output"], True

    elif (
        (output is True and datasets >= 1 and models >= 1)
        or (output is True and model_versions >= 1 and dataset_versions >= 1)
        or (output is True and datasets >= 1 and model_versions >= 1)
        or (output is True and models >= 1 and dataset_versions >= 1)
    ):
        return HEADERS["mixed output"], True

    else:
        raise ValueError("No header was assigned.")


def inputs_documentation(inputs: List[ArtifactReference], stage: Stage, client) -> None:
    if len(inputs) < 1:
        logging.warning("There are no inputs for the run.")
        return
    header, multiple = select_header(inputs, input=True)
    if multiple is True:
        stage._add_header(header)
        stage.add_block(text=" ")
    for item in inputs:
        if item.artifact_type.name == "DATASET":
            if multiple is False:
                stage._add_header(header)
                stage.add_block(text=" ")
            if item.version_id:
                if item.description:
                    stage.add_block(text=item.description)
                stage.add_block(dataset_version=item.version_id)
            elif item.version_strategy.value == "AUTOMATIC":
                dataset_versions: List[DatasetVersion] = sorted(
                    client.list_dataset_versions(item.dataset).list, key=lambda x: x.id
                )
                stage.add_block(dataset_version=dataset_versions[-1].id)
            elif item.dataset and isinstance(item.dataset, int):
                stage.add_block(dataset=item.dataset)
        elif item.artifact_type.name == "MODEL":
            if multiple is False:
                stage._add_header(header)
                stage.add_block(text=" ")
            if item.description:
                stage.add_block(text=item.description)
            if item.version_id:
                attachments = client.list_attachments("modelversion", item.version_id).list
                if item.model:
                    stage._add_model_table(item.model, item.version_id)
                if len(attachments) >= 1:
                    stage.add_block(text="The Model Version Attachments:")
                    for attachment in attachments:
                        stage._add_attachment(attachment)
            elif item.model and isinstance(item.model, int):
                stage.add_block(model=item.model)


def outputs_documentation(outputs: List[ArtifactReference], stage: Stage, client):
    if len(outputs) < 1:
        logging.warning("There are no outputs for the run.")
        return
    header, multiple = select_header(outputs, output=True)
    if multiple is True:
        stage._add_header(header)
        stage.add_block(text=" ")
    for item in outputs:
        if item.artifact_type.name == "MODEL":
            if multiple is False:
                stage._add_header(header)
                stage.add_block(text=" ")
            if item.description:
                stage.add_block(text=item.description)
            if item.version_id:
                attachments = client.list_attachments("modelversion", item.version_id).list
                if item.model:
                    stage._add_model_table(item.model, item.version_id)
                if len(attachments) >= 1:
                    stage.add_block(text="The Model Version Attachments:")
                    for attachment in attachments:
                        stage._add_attachment(attachment)
            elif item.model and isinstance(item.model, int):
                stage.add_block(model=item.model)
        elif item.artifact_type.name == "DATASET":
            if multiple is False:
                stage._add_header(header)
                stage.add_block(text=" ")
            if item.description:
                stage.add_block(text=item.description)
            if item.version_id:
                stage.add_block(dataset_version=item.version_id)
            elif item.version_strategy.value == "AUTOMATIC":
                dataset_versions: List[DatasetVersion] = sorted(
                    client.list_dataset_versions(item.dataset).list, key=lambda x: x.id
                )
                stage.add_block(dataset_version=dataset_versions[-1].id)
            elif item.dataset and isinstance(item.dataset, int):
                stage.add_block(dataset=item.dataset)


def __create_artifact_input__(item: ArtifactReference) -> ArtifactReferenceInput:
    result = ArtifactReferenceInput(item.artifact_type)
    if item.dataset is not None:
        result.dataset = __to_dataset_version_input__(item)
    elif item.model is not None:
        result.model = __to_model_version_input__(item)
    elif item.code is not None:
        result.code = __to_code_version_input__(item)
    return result


def __to_code_version_input__(artifact_reference: ArtifactReference) -> RulesCodeVersionInput:
    result = RulesCodeVersionInput()
    if isinstance(artifact_reference.code, int):
        result.parentId = artifact_reference.code
    else:
        result.parentName = str(artifact_reference.code)
    result.version = ArtifactVersion(version_id=artifact_reference.version_id)
    return result


def __to_dataset_version_input__(artifact_reference: ArtifactReference) -> RulesDatasetVersionInput:
    result = RulesDatasetVersionInput()
    if isinstance(artifact_reference.dataset, int):
        result.parentId = artifact_reference.dataset
    else:
        result.parentName = str(artifact_reference.dataset)
    if artifact_reference.description is not None:
        result.description = artifact_reference.description
    if artifact_reference.version_id is not None:
        result.autoVersion = False
        result.version = ArtifactVersion(version_id=artifact_reference.version_id)
        return result
    if artifact_reference.version_name is not None:
        result.autoVersion = False
        result.version = ArtifactVersion(version_name=artifact_reference.version_name)
        return result
    if artifact_reference.version_number is not None:
        result.autoVersion = False
        result.version = ArtifactVersion(version_number=artifact_reference.version_number)
        return result
    if artifact_reference.version_strategy is not None:
        result.autoVersion = True
        return result
    raise RuntimeError(f"Missing version information for dataset {artifact_reference.dataset}")


def __to_model_version_input__(artifact_reference: ArtifactReference) -> RulesModelVersionInput:
    result = RulesModelVersionInput()
    if isinstance(artifact_reference.model, int):
        result.parentId = artifact_reference.model
    else:
        result.parentName = str(artifact_reference.model)
    if artifact_reference.description is not None:

        result.description = artifact_reference.description
    if artifact_reference.version_id is not None:
        result.version = ArtifactVersion(id=artifact_reference.version_id)
        return result
    if artifact_reference.version_name is not None:
        result.version = ArtifactVersion(version_name=artifact_reference.version_name)
        return result
    if artifact_reference.version_number is not None:
        result.version = ArtifactVersion(version_number=artifact_reference.version_number)
        return result
    raise RuntimeError(f"Missing version information for model {artifact_reference.model}")


def _ensure_reference(item: Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]) -> ArtifactReference:
    if isinstance(item, ArtifactReference):
        return item
    elif isinstance(item, CodeVersion):
        return ArtifactReference(code=item.code_id, version_id=item.id)
    elif isinstance(item, DatasetVersion):
        return ArtifactReference(dataset=item.dataset.id, version_id=item.id, description=item.description)
    elif isinstance(item, ModelVersion):
        return ArtifactReference(model=item.model.id, version_id=item.id, description=item.description)
    else:
        raise RuntimeError(f"can not create artifact reference from unknown object '{item}'")


class Run(AttachmentContainer):
    """
    The Run acts as the ActiveRun, JobRun and Job.
    The run is not viewable in the Vectice platform until the job is started.
    """

    def __init__(
        self,
        id: int,
        job: Job,
        name: str,
        system_name: Optional[str] = "",
        created_date: Optional[datetime] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: RunStatus = RunStatus.SCHEDULED,
        auto_code: bool = False,
        check_remote_repository: bool = True,
        description: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
    ):
        """
        :param id: The id of the run
        :param job: The job of the run
        :param name: The name of the run
        :param system_name: The system name this run was executed in
        :param created_date: The creation date of the run
        :param start_date: The starting date of the run
        :param end_date: The ending date of the run
        :param status: The status of the run
        :param auto_code: If the auto code is activated
        :param check_remote_repository: If checking remote repository option is activated.
        :param description: A quick description of the run
        :param properties: The properties of the run
        """
        super().__init__(name, id, job._client, "Run")
        self._job = job
        self._systemName = system_name
        self._description = description
        self._properties = properties
        self._createdDate = created_date
        self._startDate = start_date
        self._endDate = end_date
        self._status = status
        self._duration: Optional[int] = None
        self._integration_client: Optional[AbstractIntegration] = job._integration_client
        self._inputs: List[ArtifactReference] = []
        self._outputs: List[ArtifactReference] = []
        self._auto_code = auto_code
        self._check_remote_repository = check_remote_repository
        self._auto_document_run = False
        self._document_stage = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        return f"Run(id={self.id}, job={self.job}, name={self.name}, system_name={self.system_name}, start_date={self.start_date}, end_date={self.end_date}, duration={self.duration}, status={self.status}, inputs={self.inputs}, outputs={self.outputs})"

    def __enter__(self) -> Run:
        if self._status == RunStatus.SCHEDULED:
            self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        status = RunStatus.COMPLETED if exc_type is None else RunStatus.FAILED
        try:
            self.end_run(status=status)
        except Exception as e:
            self.fail(reason=str(e))
        finally:
            return exc_type is None

    @property
    def id(self) -> int:
        """
        The run identifier.
        :return: int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        self._id = id

    @property
    def job(self) -> Job:
        """
        The parent Job object of the run.
        :return: Job
        """
        return self._job

    @job.setter
    def job(self, job):
        self._job = job

    @property
    def name(self) -> str:
        """
        The run name.
        :return: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def system_name(self) -> Optional[str]:
        """
        The system name the run is executed in.
        :return: Optional[str]
        """
        return self._systemName

    @system_name.setter
    def system_name(self, system_name: str):
        self._systemName = system_name

    @property
    def description(self) -> Optional[str]:
        """
        A quick description of the run.
        :return: Optional[str]
        """
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

    @property
    def properties(self) -> Optional[Dict]:
        """
        The run properties.
        :return: Optional[Dict]
        """
        return self._properties

    @properties.setter
    def properties(self, properties: Dict):
        self._properties = properties

    @property
    def start_date(self) -> Optional[datetime]:
        """
        The starting date of the run.
        :return: Optional[datetime]
        """
        return self._startDate

    @property
    def end_date(self) -> Optional[datetime]:
        """
        The ending date of the run.
        :return: Optional[datetime]
        """
        return self._endDate

    @end_date.setter
    def end_date(self, end_date: datetime):
        self._endDate = end_date

    @property
    def status(self) -> RunStatus:
        """
        The status of the run.
        :return: RunStatus
        """
        return self._status

    @status.setter
    def status(self, status: RunStatus):
        self._status = status

    @property
    def duration(self) -> Optional[int]:
        """
        The duration of the run.
        :return: Optional[int]
        """
        return self._duration

    @duration.setter
    def duration(self, duration: int):
        self._duration = duration

    @property
    def inputs(self) -> List[ArtifactReference]:
        """
        The artifact inputs of the run.
        :return: List[ArtifactReference]
        """
        return self._inputs.copy()

    @property
    def outputs(self) -> List[ArtifactReference]:
        """
        The artifact outputs of the run.
        :return: List[ArtifactReference]
        """
        return self._outputs.copy()

    def to_reference_input(self, item: ArtifactReference) -> ArtifactReferenceInput:
        return ArtifactReferenceInput(
            item.artifact_type,
            item.description,
            RulesDatasetVersionInput(
                parentName=str(item.dataset) if not isinstance(item.dataset, int) else None,
                parentId=item.dataset if isinstance(item.dataset, int) else None,
                version=ArtifactVersion(item.version_number, item.version_name, item.version_id)
                if item.version_strategy == VersionStrategy.MANUAL
                else None,
                autoVersion=True if item.version_strategy == VersionStrategy.AUTOMATIC else None,
                description=item.description,
            )
            if item.artifact_type == ArtifactType.DATASET
            else None,
            RulesModelVersionInput(
                parentName=str(item.model) if not isinstance(item.model, int) else None,
                parentId=item.model if isinstance(item.model, int) else None,
                version=ArtifactVersion(item.version_number, item.version_name, item.version_id),
                description=item.description,
            )
            if item.artifact_type == ArtifactType.MODEL
            else None,
            RulesCodeVersionInput(
                parentName=str(item.model) if not isinstance(item.model, int) else None,
                parentId=item.model if isinstance(item.model, int) else None,
                version=ArtifactVersion(item.version_number, item.version_name, item.version_id),
            )
            if item.artifact_type == ArtifactType.CODE
            else None,
        )

    def add_output(self, output: ArtifactReference):
        """
        Adds an artifact as output to the run.

        :param output: The artifact to be added as an output
        :return: None
        """
        if self._outputs is None:
            self._outputs = [output]
        else:
            self._outputs.append(output)
        if self.status != RunStatus.SCHEDULED:
            self._client.fill_run(
                self.id,
                outputs=[self.to_reference_input(output)],
            )

    def add_outputs(self, outputs: List[ArtifactReference]):
        """
        Adds a list of artifacts as outputs to the run.

        :param outputs: The list of artifacts to be added as outputs
        :return: None
        """
        if self._outputs is None:
            self._outputs = outputs
        else:
            self._outputs.extend(outputs)
        if self.status != RunStatus.SCHEDULED:
            self._client.fill_run(
                self.id,
                outputs=[self.to_reference_input(output) for output in outputs],
            )

    def add_input(self, input: ArtifactReference):
        """
        Adds an artifact as input to the run.

        :param input: The artifact to be added as an input
        :return: None
        """
        if self._inputs is None:
            self._inputs = [input]
        else:
            if input not in self._inputs:
                self._inputs.append(input)
                # finally, if run is started, add it to the server
                if self.status != RunStatus.SCHEDULED:
                    response = self._client.fill_run(
                        self.id,
                        inputs=[self.to_reference_input(input)],
                    )
                    # artifacts = [ArtifactReferenceOutput(**item) for item in response["outputArtifacts"]]
                    # reused_dataset = [
                    #     item for item in artifacts if item["reusedVersion"] is True and item.get("dataSetVersion")
                    # ]
                    # if len(reused_dataset) >= 1:
                    #     for dataset_version in reused_dataset:
                    #         parent_dataset = dataset_version["dataSetVersion"]["dataSet"]["name"]
                    #         self._logger.info(
                    #             f"Reusing version {dataset_version['dataSetVersionId']} of dataset {parent_dataset}"
                    #         )
                    artifacts = [ArtifactReferenceOutput(**item) for item in response["outputArtifacts"]]
                    for artifact in artifacts:
                        # logging.info(artifact)
                        if artifact["reusedVersion"] is True:
                            # self._logger.info(artifact)
                            parent_dataset = self._client.get_dataset(artifact["dataSetVersion"]["dataSetId"])
                            # self._logger.info(artifact["dataSetVersion"]["dataSetId"])
                            self._logger.info(
                                f"Reusing version {artifact['dataSetVersionId']} of dataset {parent_dataset.name}"
                            )
                        else:
                            logging.info("ICIIIIIIIII")
                            if (
                                artifact.get("dataSetVersion", None) is not None
                                and artifact["dataSetVersion"]["versionType"] is True
                            ):
                                parent_dataset = self._client.get_dataset(artifact["dataSetVersion"]["dataSetId"])
                                self._logger.info(
                                    f"Changes detected automatically in resources for dataset {parent_dataset.name}"
                                )
                                self._logger.info(f"Creating and using version with id: {artifact['dataSetVersionId']}")

    def add_inputs(self, artifacts: List[ArtifactReference]):
        """
        Adds a list of artifact as inputs to the run.

        :param artifacts: The list of artifacts to be added as inputs
        :return: None
        """
        # first, remove duplicate from provided list
        inputs = []
        for input in artifacts:
            if input not in inputs:
                inputs.append(input)
        # then call add_input
        for input in inputs:
            self.add_input(input)

    def start(
        self,
        inputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None,
        auto_code: Optional[bool] = None,
        check_remote_repository: Optional[bool] = None,
    ) -> None:
        """
        Starts the run.
        :param inputs: The artifacts to be added as inputs to the run
        :param auto_code: Boolean for the auto code option
        :param check_remote_repository: Boolean for the checking remote repository option
        :return: None
        """
        if inputs is not None:
            artifacts_references_inputs = [_ensure_reference(item) for item in inputs if item is not None]
            self.add_inputs(artifacts_references_inputs)

        if auto_code is True or (auto_code is None and self._auto_code is True):
            code_artifact_is_present = False
            if self._inputs is not None:
                for artifact in self._inputs:
                    code_artifact_is_present = code_artifact_is_present or artifact.artifact_type == ArtifactType.CODE
            if not code_artifact_is_present:
                git_version = GitVersion.create(
                    check_remote_repository=check_remote_repository
                    if check_remote_repository is not None
                    else self._check_remote_repository
                )
                if git_version:
                    code_version = self.job.project.create_code_version(git_version=git_version)
                    self.add_input(ArtifactReference(code=code_version.code_id, version_id=code_version.id))

        job_input = JobInput(self.job.name, self.job.description, self.job.type)
        self._status = RunStatus.STARTED
        self._startDate = datetime.utcnow()
        run_input = RunInput(self.name, job_input, self.system_name, self._startDate, self.end_date, self.status)
        if self._inputs is None:
            artifact_inputs = None
        else:
            artifact_inputs = [__create_artifact_input__(artifact) for artifact in self._inputs]
        rule_input = StartRunInput(job_input, run_input, artifact_inputs)
        if self._integration_client:
            try:
                self._integration_client.before_start(self)
            except Exception as e:
                logging.warning(e)
        self._client.start_run(rule_input)
        if self._integration_client:
            try:
                self._integration_client.after_start(self)
            except Exception as e:
                logging.warning(e)

    def end_run(
        self,
        outputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None,
        status: RunStatus = RunStatus.COMPLETED,
        reason: Optional[str] = None,
    ) -> None:
        """
        Ends the current (last) active run started by :func:`~Vectice.start_run`.
        To end a specific run, use :func:`~Vectice.stop_run` instead.

        :param outputs: The artifacts to be added as outputs to the run
        :param status: Status of the run changes by default to COMPLETED
        :param reason: Reason note for ending the run
        :return: None
        """
        if outputs is not None:
            artifacts_references_inputs = [_ensure_reference(item) for item in outputs if item is not None]
            self.add_outputs(artifacts_references_inputs)
        run_output = self._client.get_run(self.id)
        run_output["status"] = status
        run_output["endDate"] = datetime.utcnow()
        run_output["reason"] = reason
        rule_output = StopRunInput(run_output)
        if self._integration_client is not None:
            try:
                self._integration_client.before_stop(self)
            except Exception as e:
                logging.warning(e)
        output = self._client.stop_run(rule_output)
        self._status = output.jobRun.status
        self._duration = output.jobRun.duration
        self._startDate = output.jobRun.start_date
        self._endDate = output.jobRun.end_date
        if self._integration_client is not None:
            try:
                self._integration_client.after_stop(self)
            except Exception as e:
                logging.warning(e)

    def complete(
        self, outputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None
    ) -> None:
        """
        Completes the run.

        :param outputs: The artifacts to be added as outputs to the run

        :return: None
        """
        self.end_run(outputs=outputs, status=RunStatus.COMPLETED)

    def fail(
        self,
        outputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Fails the run.

        :param outputs: The artifacts to be added as outputs to the run
        :param reason: Reason note for failing the run

        :return: None
        """
        self.end_run(outputs=outputs, status=RunStatus.FAILED, reason=reason)

    def abort(
        self,
        outputs: Optional[List[Union[ArtifactReference, CodeVersion, ModelVersion, DatasetVersion]]] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Aborts the run.

        The end date of the Run will be set at the time this method is called.

        :param outputs: The artifacts to be added as outputs to the run
        :param reason: Reason note for aborting the run
        :return: None
        """
        self.end_run(outputs=outputs, status=RunStatus.ABORTED, reason=reason)

    def clean(self):
        """
        Cleans and rests to None all the data of the run.

        """
        self._outputs = None
        self._inputs = None
        self._endDate = None
        self._duration = None
        self._status = RunStatus.SCHEDULED

    def _capture_run_info(self, stage: Stage):
        inputs = self.inputs
        outputs = self.outputs
        logging.getLogger("Stage").propagate = False
        inputs_documentation(inputs, stage, self._client)
        # Run
        stage.add_block(divider=True)
        stage._add_header("The Original Run:")
        if self.description:
            stage.add_block(text=self.description)
        stage.add_block(text=" ")
        stage.add_block(run=self.id)
        stage.add_block(divider=True)

        outputs_documentation(outputs, stage, self._client)
        logging.getLogger("Stage").propagate = True
