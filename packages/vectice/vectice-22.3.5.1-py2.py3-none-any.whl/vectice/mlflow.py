from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, List

import mlflow
from mlflow.entities import Experiment as MlflowExperiment, Run as MlflowRun
from mlflow.tracking import MlflowClient

from vectice.api import Client
from vectice.api.json import ModelInput
from vectice.api.json import PropertyInput
from vectice.api.json import RunStatus
from vectice.integrations import AbstractIntegration
from vectice.models.artifact_reference import ArtifactReference
from vectice.models.run import Run

VECTICE_RUN_TAG = "vectice.run.id"
_STATUSES_MAP = {
    "RUNNING": RunStatus.STARTED,
    "SCHEDULED": RunStatus.SCHEDULED,
    "FINISHED": RunStatus.COMPLETED,
    "FAILED": RunStatus.FAILED,
    "KILLED": RunStatus.ABORTED,
}

_STATUSES_VECTICE_TO_MLFLOW = {
    "STARTED": "RUNNING",
    "SCHEDULED": "SCHEDULED",
    "COMPLETED": "FINISHED",
    "FAILED": "FAILED",
    "ABORTED": "KILLED",
}

UNWANTED_TAGS = ["mlflow.log-model.history"]


class MLflowIntegration(AbstractIntegration):
    def __init__(self, mlflow_client: MlflowClient, vectice_client: Client, auto_log: Optional[bool] = False):

        self._auto_log = auto_log
        self._mlflow_client = mlflow_client
        self._vectice_client = vectice_client
        self._auto_log = auto_log
        self._logger = logging.getLogger(self.__class__.__name__)
        self._experiment_name: Optional[str] = None
        self._mlflow_run = None
        self._output_artifacts: List[ArtifactReference] = []

    @property
    def experiment_name(self):
        return self._experiment_name

    @property
    def lib_name(self) -> str:
        return "mlflow"

    def before_start(self, vectice_run: Run):
        mlflow.set_experiment(vectice_run.job.name)
        self._experiment_name = vectice_run.job.name

    def after_start(self, vectice_run: Run) -> None:
        """
        Updated the existing job.
        """
        ml_run = mlflow.start_run()
        self._mlflow_run = ml_run

    def before_stop(self, vectice_run: Run):
        """
        Might be useful.
        """
        pass

    def after_stop(self, vectice_run: Run):
        """
        Clean up.
        """
        if mlflow.active_run() is None:
            self._logger.debug("No active run found.")
            return None
        status = _STATUSES_VECTICE_TO_MLFLOW[vectice_run.status.name]
        mlflow.end_run(status=status)
        self._output_artifacts = self._extract_from_mlflow(self._mlflow_run, vectice_run)
        if self._mlflow_run is not None:
            self._mlflow_client.set_tag(self._mlflow_run.info.run_id, VECTICE_RUN_TAG, vectice_run.id)
        elif self._mlflow_run is None:
            logging.warning("There is no MLflow run.")
        self._experiment_name = vectice_run.job.name
        vectice_run.add_outputs(self._output_artifacts)

    def _extract_from_mlflow(
        self, mlflow_run: MlflowRun, vectice_run: Run, experiment: MlflowExperiment = None
    ) -> List[ArtifactReference]:
        ml_exp = self._mlflow_client.get_experiment(mlflow_run.info.experiment_id)
        if vectice_run is not None:
            output_artifacts = self._extract_outputs(mlflow_run, ml_exp, vectice_run)
        else:
            output_artifacts = []
        self._extract_run(mlflow_run, vectice_run)
        return output_artifacts

    def _extract_run(self, mlflow_run: MlflowRun, vectice_run: Run):
        """
        Updated run
        """
        from vectice.api.json.run import RunOutput

        tags = []
        run_name = None
        for tag in mlflow_run.data.tags.items():
            if tag[0] not in UNWANTED_TAGS:
                tags.append(PropertyInput(tag[0], tag[1]))
        if vectice_run:
            run_name = vectice_run.name
        self._vectice_client.create_run_properties(vectice_run.id, tags)
        if vectice_run is not None:
            run_input = RunOutput(
                id=vectice_run.id,
                start_date=datetime.fromtimestamp(mlflow_run.info.start_time / 1000),
                end_date=datetime.fromtimestamp(mlflow_run.info.end_time / 1000) if mlflow_run.info.end_time else None,
                name=run_name if run_name else None,
            )
            self._vectice_client.update_run(run_input)

    def _extract_outputs(
        self, mlflow_run: MlflowRun, experiment: MlflowExperiment, run: Run
    ) -> List[ArtifactReference]:
        from vectice.api.json import ModelType
        from vectice.models.model import Model
        from vectice.api.reference import BadReferenceError

        updated_run = self._mlflow_client.get_run(mlflow_run.info.run_id)

        parameters = updated_run.data.params
        metrics = updated_run.data.metrics
        parameters[
            "mlflow_url"
        ] = f"{mlflow.get_tracking_uri()}/#/experiments/{mlflow_run.info.experiment_id}/runs/{mlflow_run.info.run_id}"
        try:
            model_output = self._vectice_client.get_model(experiment.name)
        except BadReferenceError:
            model_output = None
        if model_output is None:
            model_input = ModelInput(name=experiment.name, type=ModelType.OTHER.name)
            model_output = self._vectice_client.create_model(data=model_input, project=run.job.project.id)
        model = Model(
            model_output.name, model_output.id, run.job.project, model_output.description, ModelType[model_output.type]
        )
        model_version = model.create_model_version(
            experiment.name + "-" + mlflow_run.info.run_id,
            algorithm_name=mlflow_run.data.tags.get("estimator_name"),
            metrics=metrics,
            hyper_parameters=parameters,
            runId=run.id,
        )
        result = ArtifactReference(model=model.id, version_id=model_version.id)
        return [result]
