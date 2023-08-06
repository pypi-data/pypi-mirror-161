from __future__ import annotations

import logging
from typing import Optional, Tuple, Any, BinaryIO, TYPE_CHECKING, Sequence, cast

from vectice.api._auth import Auth
from vectice.api.code_version import CodeVersionApi
from vectice.api.dataset_version import DatasetVersionApi
from vectice.api.model_version import ModelVersionApi
from vectice.api.project import ProjectApi
from vectice.api.run import RunApi
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import PagedResponse, AttachmentOutput
from .reference import InvalidReferenceError, MissingReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class AttachmentApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()
        self._logger = logging.getLogger(self.__class__.__name__)

    def _generate_artifact_url_and_id(
        self,
        _type: str,
        artifact_version: Optional[Reference] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> Tuple[str, Optional[str]]:
        url = None
        object_name = None
        try:
            if _type == "datasetversion":
                if isinstance(artifact_version, int):
                    dataset_version_object = DatasetVersionApi(self._auth).get_dataset_version(
                        version=artifact_version, dataset=artifact, project=project, workspace=workspace
                    )
                elif isinstance(artifact_version, str) and project:
                    dataset_version_object = DatasetVersionApi(self._auth).get_dataset_version(
                        version=artifact_version, dataset=artifact, project=project, workspace=workspace
                    )
                else:
                    raise MissingReferenceError("datasetversion", "project")
                url = f"/metadata/project/{dataset_version_object.dataset.project.id}/entityfiles/{_type}/{dataset_version_object.id}"
                object_name = "DatasetVersion with id: " + str(dataset_version_object.id)
            elif _type == "modelversion":
                if isinstance(artifact_version, int):
                    model_version_object = ModelVersionApi(self._auth).get_model_version(
                        version=artifact_version, model=artifact, project=project, workspace=workspace
                    )
                elif isinstance(artifact_version, str) and project:
                    model_version_object = ModelVersionApi(self._auth).get_model_version(
                        version=artifact_version, model=artifact, project=project, workspace=workspace
                    )
                else:
                    raise MissingReferenceError("modelversion", "project")
                url = f"/metadata/project/{model_version_object.model.project.id}/entityfiles/{_type}/{model_version_object.id}"
                object_name = "ModelVersion with id: " + str(model_version_object.id)
            elif _type == "codeversion":
                if isinstance(artifact_version, int):
                    code_version_object = CodeVersionApi(self._auth).get_code_version(
                        version=artifact_version, project=project, workspace=workspace
                    )
                elif isinstance(artifact_version, str) and project:
                    code_version_object = CodeVersionApi(self._auth).get_code_version(
                        version=artifact_version, project=project, workspace=workspace
                    )
                else:
                    raise MissingReferenceError("codeversion", "project")
                url = f"/metadata/project/{code_version_object.code.project.id}/entityfiles/{_type}/{code_version_object.id}"
                object_name = "CodeVersion with id: " + str(code_version_object.id)
            elif _type == "run":
                if isinstance(artifact_version, int):
                    run_object = RunApi(self._auth).get_run(
                        run=artifact_version, job=artifact, project=project, workspace=workspace
                    )
                elif isinstance(artifact_version, str) and project:
                    run_object = RunApi(self._auth).get_run(
                        run=artifact_version, job=artifact, project=project, workspace=workspace
                    )
                else:
                    raise MissingReferenceError("run", "project")
                url = f"/metadata/project/{run_object.job.project.id}/entityfiles/{_type}/{run_object.id}"
                object_name = "Run with id: " + str(run_object.id)
            elif _type == "project":
                if project:
                    project_object = ProjectApi(self._auth).get_project(project, workspace)
                else:
                    raise MissingReferenceError("project", "attachment")
                url = f"/metadata/project/{project_object.id}/entityfiles/{_type}/{project_object.id}"
            if url is None:
                raise RuntimeError("url cannot be none")
            return url, object_name
        except HttpError as e:
            if artifact_version:
                reference = artifact_version
            elif artifact:
                reference = artifact
            else:
                raise ValueError("No reference to artifact or artifact version provided.")
            raise self._httpErrorhandler.handleGetHttpError(e, _type, reference)

    def get_attachment(
        self,
        _type: str,
        file_id: int,
        artifact_version: Optional[Reference] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> BinaryIO:
        try:
            url, object_id = self._generate_artifact_url_and_id(_type, artifact_version, artifact, workspace, project)
            response = self._auth._get_attachment(url + f"/{file_id}")
            self._logger.info(f"Attachment with id: {file_id} successfully retrieved from {object_id}.")
            return cast(BinaryIO, response.raw)
        except HttpError as e:
            if artifact_version:
                reference = artifact_version
            elif artifact:
                reference = artifact
            else:
                raise ValueError("No reference to artifact or artifact version provided.")
            raise self._httpErrorhandler.handleGetHttpError(e, _type, reference)

    def post_attachment(
        self,
        _type: str,
        artifact_version: Optional[Reference] = None,
        files: Optional[Sequence[Tuple[str, Tuple[Any, BinaryIO]]]] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
        file_id: Optional[int] = None,
    ) -> None:
        try:
            url, object_id = self._generate_artifact_url_and_id(_type, artifact_version, artifact, workspace, project)
            if file_id:
                url = url + f"/{file_id}"
                self._logger.info(f"Attachment with id: {file_id} successfully attached to {object_id}.")
            if files and len(files) == 1:
                self._auth._post_attachments(url, files)
                self._logger.info(f"Attachment with name: {files[0][1][0]} successfully attached to {object_id}.")
            elif files and len(files) > 1:
                for file in files:
                    self._auth._post_attachments(url, [file])
                self._logger.info(
                    f"Attachments with names: {[f[1][0] for f in files]} successfully attached to {object_id}."
                )
        except HttpError as e:
            if artifact_version:
                reference = artifact_version
            elif artifact:
                reference = artifact
            elif _type == "project" and project:
                reference = project
            else:
                raise ValueError("No reference to artifact or artifact version provided.")
            raise self._httpErrorhandler.handleGetHttpError(e, _type, reference)

    def delete_attachment(
        self,
        _type: str,
        artifact_version: Reference,
        file_id: int,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ):
        try:
            url, object_id = self._generate_artifact_url_and_id(_type, artifact_version, artifact, workspace, project)
            response = self._auth._delete_attachment(url + f"/{file_id}")
            self._logger.info(f"Attachment with id: {file_id} successfully deleted from {object_id}.")
            return response
        except HttpError as e:
            if artifact_version:
                reference = artifact_version
            elif artifact:
                reference = artifact
            else:
                raise ValueError("No reference to artifact or artifact version provided.")
            raise self._httpErrorhandler.handleGetHttpError(e, _type, reference)

    def list_attachments(
        self,
        _type: str,
        artifact_version: Optional[Reference] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ) -> PagedResponse[AttachmentOutput]:
        url = None
        try:
            url, _ = self._generate_artifact_url_and_id(_type, artifact_version, artifact, workspace, project)
        except HttpError as e:
            if artifact_version:
                reference = artifact_version
            else:
                raise ValueError("No reference to artifact version provided.")
            self._httpErrorhandler.handleGetHttpError(e, _type, reference)
        if url is None:
            raise InvalidReferenceError("artifact version", artifact)
        attachments = self._auth._list_attachments(url)
        return PagedResponse(
            item_cls=AttachmentOutput,
            total=len(attachments),
            page={},
            items=attachments,
        )

    def update_attachments(
        self,
        _type: str,
        files: Sequence[Tuple[str, Tuple[Any, BinaryIO]]],
        artifact_version: Optional[Reference] = None,
        artifact: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        project: Optional[Reference] = None,
    ):
        try:
            url, object_id = self._generate_artifact_url_and_id(_type, artifact_version, artifact, workspace, project)
            attachments = {
                attach.fileName: attach.fileId
                for attach in self.list_attachments(_type, artifact_version, artifact, workspace, project).list
            }
            for file in files:
                file_name = file[1][0]
                file_id = attachments.get(file_name)
                if file_id:
                    self._auth._put_attachments(url + f"/{file_id}", [file])
            self._logger.info(
                f"Attachments with names: {[f[1][0] for f in files]} successfully updated in {object_id}."
            )
        except HttpError as e:
            if artifact_version:
                reference = artifact_version
            elif artifact:
                reference = artifact
            else:
                raise ValueError("No reference to artifact or artifact version provided.")
            self._httpErrorhandler.handleGetHttpError(e, _type, reference)
