from __future__ import annotations

from typing import Optional, Dict


from vectice.api.json.block import BlockType, BlockState, BlockVariant


class Block:
    """
    Describes a block that belongs to page
    """

    def __init__(
        self,
        type: BlockType,
        variant: BlockVariant,
        state: Optional[BlockState] = None,
        name: Optional[str] = None,
        position: Optional[int] = None,
        content: Optional[str] = None,
        resource_id: Optional[int] = None,
        entity_file_id: Optional[int] = None,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        url: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        """
        :param type: the block type
        :param variant: the block variant
        :param state: the block state
        :param name: the name of the block
        :param position: the position of the block
        :param content: the block content such as text
        :param resource_id: the vectice resource id
        :param entity_file_id: the entity file id
        :param file_path: the file path of the notebook/image
        :param file_size: the size of the file
        :param url: the url of the block


        """
        self._type = type
        self._variant = variant
        self._state = state
        self._name = name
        self._position = position
        self._content = content
        self._resource_id = resource_id
        self._entity_file_id = entity_file_id
        self._file_path = file_path
        self._file_size = file_size
        self._url = url
        self._config = config

    def __repr__(self):
        return f"Block(position={self.position}, type={self.type}, variant={self.variant}, resource_id={self.resource_id}, content={self.content})"

    @property
    def type(self) -> BlockType:
        return self._type

    @property
    def variant(self) -> BlockVariant:
        return self._variant

    @property
    def content(self) -> Optional[str]:
        return self._content

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def position(self) -> Optional[int]:
        return self._position

    @property
    def searchable_content(self) -> Optional[str]:
        return self._content

    @property
    def state(self) -> Optional[BlockState]:
        return self._state

    @property
    def resource_id(self) -> Optional[int]:
        return self._resource_id

    @property
    def entity_file_id(self) -> Optional[int]:
        return self._entity_file_id

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path

    @property
    def url(self) -> Optional[str]:
        return self._url

    @property
    def config(self) -> Optional[Dict]:
        return self._config
