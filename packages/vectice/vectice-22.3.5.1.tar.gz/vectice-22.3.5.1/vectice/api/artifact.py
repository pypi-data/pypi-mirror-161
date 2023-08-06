from typing import Optional
from urllib.parse import urlencode

from ._auth import Auth
from .json import ArtifactInput, ArtifactOutput, PagedResponse, Page
from .reference import Reference
from .run import RunApi


class ArtifactApi:
    def __init__(self, auth: Auth):
        self._auth = auth

    def create_artifact(
        self,
        data: ArtifactInput,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> ArtifactOutput:
        if data.artifactType is None:
            raise ValueError('"artifactType" must be provided in artifact.')
        if data.jobArtifactType is None:
            raise ValueError('"jobArtifactType" must be provided in artifact.')
        parent_run = RunApi(self._auth).get_run(run, job, project, workspace)
        url = f"/metadata/project/{parent_run.job.project.id}/job/{parent_run.job.id}/run/{parent_run.id}/artifact"
        response = self._auth._post(url, data.__dict__)
        return ArtifactOutput(**response)

    def list_artifacts(
        self,
        run: Reference,
        job: Optional[Reference] = None,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        page_index: int = Page.index,
        page_size: int = Page.size,
    ) -> PagedResponse[ArtifactOutput]:
        parent_run = RunApi(self._auth).get_run(run, job, project, workspace)
        url = f"/metadata/project/{parent_run.job.project.id}/job/{parent_run.job.id}/run/{parent_run.id}/artifact"
        queries = {"index": page_index, "size": page_size}
        artifacts = self._auth._get(url + "?" + urlencode(queries))
        return PagedResponse(
            item_cls=ArtifactOutput,
            total=int(artifacts["total"]),
            page=artifacts["page"],
            items=artifacts["items"],
        )

    def update_artifact(self, artifact: ArtifactOutput) -> ArtifactOutput:
        pass
        # url = f"/metadata/project/{parent_run.job.project.id}/job/{parent_run.job.id}/run/{parent_run.id}/artifact/{artifact.id}"
        # return ArtifactOutput(self._auth._put(self.api_base_path + "/" + str(artifact_id), artifact))
