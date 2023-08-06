from __future__ import annotations

import datetime
import logging
import urllib
from typing import Optional, TYPE_CHECKING, List
from urllib.parse import urlencode

from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .job import JobApi
from .json import RunInput, RunOutput, Page, PagedResponse, PropertyOutput, PropertyInput
from .reference import InvalidReferenceError, BadReferenceError, MissingReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class RunApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorHandler = HttpErrorHandler()
        self._logger = logging.getLogger(self.__class__.__name__)

    def list_runs(
        self,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: str = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[RunOutput]:
        if not isinstance(job, str) and not isinstance(job, int):
            raise InvalidReferenceError("job", job)
        parent_job = JobApi(self._auth).get_job(job, project, workspace)
        if parent_job.project is None:
            raise BadReferenceError("job", job)
        else:
            url = f"/metadata/project/{parent_job.project.id}/job/{parent_job.id}/run"
        queries = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        runs = self._auth._get(url + "?" + urlencode(queries))
        return PagedResponse(
            item_cls=RunOutput,
            total=runs["total"],
            page=runs["page"],
            items=runs["items"],
        )

    def get_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> RunOutput:
        if isinstance(run, int):
            url = f"/metadata/run/{run}"
        elif isinstance(run, str):
            if job is None:
                raise MissingReferenceError("run", "job")
            parent_job = JobApi(self._auth).get_job(job, project, workspace)
            if parent_job is None:
                raise BadReferenceError("job")
            url = f"/metadata/project/{parent_job.project.id}/job/{parent_job.id}/run/name/{urllib.parse.quote(run)}"
        else:
            raise InvalidReferenceError("run", run)
        try:
            response = self._auth._get(url)
        except HttpError as e:
            raise self._httpErrorHandler.handleGetHttpError(e, "run", run)
        return RunOutput(**response)

    def create_run(
        self,
        data: RunInput,
        job: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> RunOutput:
        if data.status is None:
            raise ValueError('"status" must be provided in run.')
        if data.startDate is None:
            raise ValueError('"startDate" must be provided in run.')
        parent_job = JobApi(self._auth).get_job(job, project, workspace)
        if data.name is None:
            data.name = parent_job.name + " " + datetime.datetime.now().isoformat()
        url = f"/metadata/project/{parent_job.project.id}/job/{parent_job.id}/run"
        try:
            response = self._auth._post(url, data)
            return RunOutput(**response)
        except HttpError as e:
            raise self._httpErrorHandler.handlePostHttpError(e, "run")

    def update_run(self, data: RunOutput) -> RunOutput:
        url = f"/metadata/run/{data.id}"
        response = self._auth._put(url, data)
        return RunOutput(**response)

    def delete_run(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ):
        if isinstance(run, int):
            url = f"/metadata/run/{run}"
        elif isinstance(run, str):
            run_output = self.get_run(run, job, project, workspace)
            url = f"/metadata/run/{run_output.id}"
        self._auth._delete(url)

    def create_run_properties(
        self,
        run: Reference,
        properties: List[PropertyInput],
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> RunOutput:
        parent_run = self.get_run(run, job, project, workspace)
        url = f"/metadata/project/{parent_run.job.project.id}/job/{parent_run.job.id}/run/{parent_run.id}"
        if properties:
            for prop in properties:
                self._auth._post(f"{url}/entityProperty/", prop)
        parent_run = self.get_run(run, job, project, workspace)
        self._logger.info(
            f"Properties with names: {[k.key for k in properties]} successfully added to Run {parent_run.name}."
        )
        return parent_run

    def list_run_properties(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[PropertyOutput]:
        parent_run = self.get_run(run, job, project, workspace)
        url = f"/metadata/project/{parent_run.job.project.id}/job/{parent_run.job.id}/run/{parent_run.id}"
        queries = {"index": page_index, "size": page_size}
        run_properties = self._auth._get(url + "/entityProperty?" + urlencode(queries))
        properties = [PropertyOutput.from_dict(property).as_dict() for property in run_properties["items"]]
        return PagedResponse(
            item_cls=PropertyOutput,
            total=run_properties["total"],
            page=run_properties["page"],
            items=properties,
        )
