from __future__ import annotations

import logging
from typing import Optional, TYPE_CHECKING, List, Union


from vectice.api import Client
from vectice.api.json.stage import StageStatus, StageOrigin
from vectice.api.json.block import BlockInput, BlockType, BlockVariant, BlockState
from .block import Block
from .attachment_container import AttachmentContainer

if TYPE_CHECKING:
    from vectice.models import Project


class Stage:
    """
    Describes a Documentation Page
    """

    def __init__(
        self,
        id: int,
        project: Project,
        name: str,
        status: Union[StageStatus, str] = StageStatus.InProgress,
        origin: Optional[StageOrigin] = None,
    ):
        """
        :param id: the documentation page identifier
        :param project: the project the dataset belong to
        :param name: the name of the documentation page
        :param status: the name of the documentation status

        """
        self._id = id
        self._name = name
        self._status = status
        self._origin = origin
        self._project: Project = project
        self._client: Client = project._client
        self._logger = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        return f"Stage(id={self.id}, name={self.name}, status={self.status}, origin={self.origin})"

    @property
    def id(self) -> int:
        """
        Stage identifier.
        :return: int
        """
        return self._id

    @id.setter
    def id(self, dataset_id: int):
        self._id = dataset_id

    @property
    def project(self) -> Project:
        """
        The project this stage belong to.
        :return: Optional[Project]
        """
        return self._project

    @property
    def name(self) -> str:
        """
        Name of the stage
        :return: str
        """
        return self._name

    @property
    def status(self) -> Union[StageStatus, str]:
        """
        Name of the stage
        :return: str
        """
        return self._status

    @property
    def origin(self) -> Optional[StageOrigin]:
        """
        Origin of the stage
        :return: str
        """
        return self._origin

    def add_block(
        self,
        dataset: Optional[int] = None,
        dataset_version: Optional[int] = None,
        model: Optional[int] = None,
        model_version: Optional[int] = None,
        run: Optional[int] = None,
        text: Optional[str] = None,
        formula: Optional[str] = None,
        code: Optional[str] = None,
        divider: Optional[bool] = False,
        path: Optional[str] = None,
        position: Optional[int] = None,
    ) -> Stage:
        """
        Add a block to the documentation stage/documentation which belongs to a Dataset or Model. Project refers to a stage and Dataset or Model refers to the documentation for the Dataset or Model. If no position is provided then the block is added at the end of the documentation.

        If the artifact version name is provided as a string then the artifact reference is needed to get the artifact version.

        :param dataset: The dataset id
        :param dataset_version: The model id
        :param model: The model id
        :param model_version: The model id
        :param run: The run id
        :param text: The text that will populate the block.
        :param formula: The formula of the block
        :param code: The code of the block
        :param divider: Add a divider
        :param path: The path to the NOTEBOOK/FILE/IMAGE
        :param position: The position to add the block.
        :return: None
        """
        if dataset or dataset_version or model or model_version or run:
            block_type = BlockType.VECTICE_RESOURCE
            if dataset:
                variant = BlockVariant.DATASET
                resource_id = dataset
                name = self._client.get_dataset(dataset).name
            elif dataset_version:
                variant = BlockVariant.DATASET_VERSION
                resource_id = dataset_version
                name = self._client.get_dataset_version(dataset_version).name
            elif model:
                variant = BlockVariant.MODEL
                resource_id = model
                name = self._client.get_model(model).name
            elif model_version:
                variant = BlockVariant.MODEL_VERSION
                resource_id = model_version
                name = self._client.get_model_version(model_version).name
            elif run:
                variant = BlockVariant.RUN
                resource_id = run
                name = self._client.get_run(run).name
            else:
                raise ValueError("Please provide valid input for the block.")
            block_input = BlockInput(
                variant=variant,
                type=block_type,
                resourceId=resource_id,
                position=position,
                name=name,
                state=BlockState.FULL,
            )
        elif text:
            block_type = BlockType.EDITABLE
            variant = BlockVariant.TEXT
            block_input = BlockInput(
                variant=variant, type=block_type, content=f"<p>{text}</p>", searchableContent=text, position=position
            )
        elif divider:
            block_type = BlockType.OTHER
            variant = BlockVariant.DIVIDER
            block_input = BlockInput(
                variant=variant, type=block_type, content=text, searchableContent=text, position=position
            )
        elif code:
            block_type = BlockType.EDITABLE
            variant = BlockVariant.CODE
            block_input = BlockInput(
                variant=variant, type=block_type, content=code, searchableContent=code, position=position
            )
        elif formula:
            block_type = BlockType.EDITABLE
            variant = BlockVariant.FORMULA
            block_input = BlockInput(
                variant=variant, type=block_type, content=formula, searchableContent=formula, position=position
            )
        elif path:
            attachment_container = AttachmentContainer(self.name, self.id, self.project._client, "project")
            try:
                attachment_container.add_attachments(file_path=path)
                attachments = attachment_container._list_attachments()
                if attachments[-1].fileName == path.split("/")[-1]:
                    file_name = attachments[-1].fileName
                    file_type = attachments[-1].contentType
                    file_id = attachments[-1].fileId
                else:
                    raise ValueError("Please check the path provided.")
            except RuntimeError:
                self._logger.warning(
                    f"The file '{path}' already exists, update the file in Vectice if this version is newer."
                )
                attachments = attachment_container._list_attachments()
                file_name, file_type, file_id = None, None, None
                for attachment in attachments:
                    if attachment.fileName == path.split("/")[-1]:
                        file_name = attachment.fileName
                        file_type = attachment.contentType
                        file_id = attachment.fileId
                if file_name is None or file_type is None or file_id is None:
                    raise ValueError("File could not be found in Vectice.")
            block_type = BlockType.CLOUD_FILE
            if file_type == "Notebook":
                variant = BlockVariant.NOTEBOOK
            elif file_type == "ImageFile":
                variant = BlockVariant.IMAGE
            elif file_type is not None and isinstance(file_type, str):
                variant = BlockVariant.FILE
            else:
                raise ValueError(f"Unknown file type {file_type}")
            block_input = BlockInput(
                variant=variant,
                type=block_type,
                position=position,
                entityFileId=file_id,
                name=file_name,
                state=BlockState.FULL,
            )
        else:
            raise ValueError("Please provide valid input for the block.")
        result = self._client.create_block(self.id, block_input, self.project.id, self.project.workspace.id)
        self._logger.info(
            f"Block(type={result.type}, variant={result.variant}, position={result.position}) has been created in the Stage '{self.name}'"
        )
        return self

    def _add_header(self, text: str) -> Stage:
        block_type = BlockType.EDITABLE
        variant = BlockVariant.TEXT
        block_input = BlockInput(
            variant=variant, type=block_type, content=f"<h2><strong>{text}</strong></h2>", searchableContent=text
        )
        result = self._client.create_block(self.id, block_input)
        self._logger.info(
            f"Block(type={result.type}, variant={result.variant}, position={result.position}) has been created in the Stage '{self.name}'"
        )
        return self

    def _add_model_table(self, model_id: Union[int, str], model_version_id: int) -> Stage:
        block_type = BlockType.VECTICE_RESOURCE
        variant = BlockVariant.MODEL
        model = self._client.get_model(model_id)
        resource_id = model.id
        model_version = self._client.get_model_version(model_version_id)
        block_input = BlockInput(
            variant=variant,
            type=block_type,
            resourceId=resource_id,
            name=model.name,
            state=BlockState.FULL,
            config={"filters": '{"name":[{"key":"name","match":"EQUAL","value":"%s"}]}' % model_version.name},
        )
        self._client.create_block(self.id, block_input)
        return self

    def _add_attachment(self, attachment) -> Stage:
        file_name = attachment.fileName
        file_type = attachment.contentType
        file_id = attachment.fileId
        block_type = BlockType.CLOUD_FILE
        if file_type == "Notebook":
            variant = BlockVariant.NOTEBOOK
        elif file_type == "ImageFile":
            variant = BlockVariant.IMAGE
        elif file_type is not None and isinstance(file_type, str):
            variant = BlockVariant.FILE
        else:
            raise ValueError(f"Unknown file type {file_type}")
        block_input = BlockInput(
            variant=variant,
            type=block_type,
            entityFileId=file_id,
            name=file_name,
            state=BlockState.FULL,
        )
        self._client.create_block(self.id, block_input)
        return self

    def delete_block(self, position: int) -> None:
        """
        Deletes a file block.

        :param position: The position of the block.

        :return: Stage
        """
        self._client.delete_block(position, self.id, self.project.id, self.project.workspace.id)
        self._logger.info(f"Block at position {position} successfully deleted.")

    def list_blocks(self) -> List[Block]:
        """
        List the blocks associated to a stage.

        :return: List of Blocks
        """
        result = self._client.list_blocks(self.id, self.project.id, self.project.workspace.id)
        self._logger.info("Blocks successfully retrieved.")
        return [
            Block(
                position=item.position,
                type=BlockType[item.type],
                variant=BlockVariant[item.variant],
                state=BlockState[item.state] if item.state is not None else None,
                content=item.content,
                name=item.name,
                resource_id=item.resource_id,
                entity_file_id=item.entity_file_id,
            )
            for item in result
        ]
