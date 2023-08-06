from __future__ import annotations

from typing import Optional, List
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from ._auth import Auth
from ._http import HttpError
from .http_error_handlers import HttpErrorHandler
from .json import BlockInput, BlockOutput, Page
from .stage import StageApi
from .reference import InvalidReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class BlockApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def create_block(
        self, stage: Reference, data: BlockInput, project: Reference, workspace: Optional[Reference] = None
    ) -> BlockOutput:
        if isinstance(stage, int):
            url = f"/metadata/stages/{stage}/file/blocks"
        elif isinstance(stage, str):
            stage_object = StageApi(self._auth).get_stage(stage, project, workspace)
            url = f"/metadata/stages/{stage_object.id}/file/blocks"
        else:
            raise InvalidReferenceError("stage", stage)
        try:
            response = self._auth._post(url, data)
            return BlockOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePostHttpError(e, "block")

    def update_block(
        self,
        position: int,
        stage: Reference,
        data: BlockInput,
        project: Reference,
        workspace: Optional[Reference] = None,
    ) -> BlockOutput:
        if isinstance(stage, int):
            url = f"/metadata/stages/{stage}/file/blocks/{position}"
        elif isinstance(stage, str):
            stage_object = StageApi(self._auth).get_stage(stage, project, workspace)
            url = f"/metadata/stages/{stage_object.id}/file/blocks/{position}"
        else:
            raise InvalidReferenceError("stage", stage)
        try:
            response = self._auth._put(url, data)
            return BlockOutput(**response)
        except HttpError as e:
            raise self._httpErrorhandler.handlePutHttpError(e, "stage", stage)

    def list_blocks(
        self,
        stage: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
        search: Optional[str] = None,
        page_index=Page.index,
        page_size=Page.size,
    ) -> List[BlockOutput]:
        if isinstance(stage, int):
            base_url = f"/metadata/stages/{stage}/file"
        elif isinstance(stage, str):
            stage_output = StageApi(self._auth).get_stage(stage, project, workspace)
            base_url = f"/metadata/stages/{stage_output.id}/file"
        else:
            raise InvalidReferenceError("stage", stage)
        try:
            queries = {"index": page_index, "size": page_size}
            if search:
                queries["search"] = search
            response = self._auth._get(f"{base_url}?{urlencode(queries)}")
            result = [BlockOutput(item) for item in response["blocks"]]
            return result
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "stage", stage)

    def delete_block(
        self,
        position: int,
        stage: Reference,
        project: Optional[Reference] = None,
        workspace: Optional[Reference] = None,
    ) -> None:
        try:
            if isinstance(stage, int):
                self._auth._delete(f"/metadata/stages/{stage}/file/blocks/{position}")
            else:
                stage_object = StageApi(self._auth).get_stage(stage, project, workspace)
                self._auth._delete(f"/metadata/stages/{stage_object.id}/file/blocks/{position}")
        except HttpError as e:
            raise self._httpErrorhandler.handleGetHttpError(e, "stage", stage)
