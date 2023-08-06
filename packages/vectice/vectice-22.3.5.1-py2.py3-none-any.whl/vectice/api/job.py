from __future__ import annotations

import urllib
from typing import Optional, TYPE_CHECKING
from urllib.parse import urlencode

from .reference import InvalidReferenceError, MissingReferenceError, BadReferenceError
from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import JobOutput, JobInput, Page, PagedResponse, JobType
from .project import ProjectApi

if TYPE_CHECKING:
    from vectice import Reference


class JobApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def delete_job(self, job: Reference, project: Optional[Reference], workspace: Optional[Reference]) -> None:
        if isinstance(job, int):
            url = f"/metadata/job/{job}"
        elif isinstance(job, str):
            if project is not None:
                job_object = self.get_job(job, project, workspace)
                url = f"/metadata/job/{job_object.id}"
            else:
                raise MissingReferenceError("job", "project")
        else:
            raise InvalidReferenceError("job", job)
        try:
            self._auth._delete(url)
        except HttpError as e:
            raise self._httpErrorhandler.handleDeleteHttpError(e, "job", job)
        except IndexError:
            raise ValueError("The job is invalid. Please check the entered value.")

    def get_job(self, job: Reference, project: Optional[Reference], workspace: Optional[Reference]) -> JobOutput:
        parent_project = None
        if project and isinstance(job, int):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/job/{job}"
        elif isinstance(job, int):
            url = f"/metadata/job/{job}"
        elif isinstance(job, str):
            if project is not None:
                parent_project = ProjectApi(self._auth).get_project(project, workspace)
                url = f"/metadata/project/{parent_project.id}/job/name/{urllib.parse.quote(job)}"
            else:
                raise MissingReferenceError("job", "project")
        else:
            raise InvalidReferenceError("job", job)
        try:
            response = self._auth._get(url)
            result = JobOutput(**response)
            if parent_project and result.project_id != parent_project.id:
                raise BadReferenceError("job", result.name, HttpError(0, "Not Found", url, "GET", ""))
            if result.project is None:
                result.project = parent_project
            return result
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "job", job)
        except IndexError:
            raise ValueError("The project is invalid. Please check the entered value.")

    def list_jobs(
        self,
        project: Reference,
        workspace: Optional[Reference] = None,
        search: str = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> PagedResponse[JobOutput]:
        if isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/job"
        else:
            url = f"/metadata/project/{project}/job"
        queries = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        jobs = self._auth._get(url + "?" + urlencode(queries))
        return PagedResponse(item_cls=JobOutput, total=jobs["total"], page=jobs["page"], items=jobs["items"])

    def create_job(self, project: Reference, workspace: Optional[Reference], job: JobInput) -> JobOutput:
        if isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/job"
        else:
            url = f"/metadata/project/{project}/job"
        if job.name is None:
            raise ValueError('"name" must be provided in job.')
        if job.type is None:
            job.type = JobType.OTHER
        return JobOutput(**self._auth._post(url, job.__dict__))

    def update_job(self, project: Optional[Reference], workspace: Optional[Reference], job: JobOutput) -> JobOutput:
        if isinstance(project, str):
            parent_project = ProjectApi(self._auth).get_project(project, workspace)
            url = f"/metadata/project/{parent_project.id}/job"
        else:
            url = f"/metadata/project/{project}/job"
        response = self._auth._put(url + "/" + str(job.id), job)
        return JobOutput(**response)
