from __future__ import annotations

from typing import Optional

from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import RunStatus, RunOutput, StartRunInput, StopRunOutput, StopRunInput
from .json.rule import FillRunInput, FillRunOutput
from .project import ProjectApi
from .reference import Reference
from .run import RunApi


class RuleApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorHandler = HttpErrorHandler()

    def start_run(
        self,
        data: StartRunInput,
        project: Reference,
        workspace: Optional[Reference] = None,
    ) -> RunOutput:
        data.run.status = RunStatus.STARTED
        try:
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/rules/start-run"
            try:
                response = self._auth._post(url, data)
                return RunOutput(**response)
            except HttpError as e:
                raise self._httpErrorHandler.handlePostHttpError(e, "run", "start")
        except HttpError as e:
            raise self._httpErrorHandler.handleGetHttpError(e, "project", project)

    def stop_run(self, data: StopRunInput) -> StopRunOutput:
        if data.jobRun.id is None:
            raise ValueError('"id" must be provided in run.')
        try:
            run_output = RunApi(self._auth).get_run(data.jobRun.id)
            url = f"/metadata/project/{run_output.job.project.id}/rules/stop-run"
            response = self._auth._post(url, data)
            return StopRunOutput(**response)
        except HttpError as e:
            raise self._httpErrorHandler.handlePostHttpError(e, "run", "stop")

    def fill_run(self, data: FillRunInput):
        if data.jobRunId is None:
            raise ValueError('"jobRunId" must be provided in input.')
        try:
            run_output = RunApi(self._auth).get_run(data.jobRunId)
            url = f"/metadata/project/{run_output.job.project.id}/rules/fill-run"
            response = self._auth._post(url, data)
            return FillRunOutput(**response)
        except HttpError as e:
            raise self._httpErrorHandler.handlePostHttpError(e, "run", "fill")
