from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Union
from enum import EnumMeta

from .data_resource_schema import DataResourceSchema


class FileMetadataType(EnumMeta):
    """
    Supported type of resources.
    """

    Folder = "Folder"
    """"""
    CsvFile = "CsvFile"
    """"""
    ImageFile = "ImageFile"
    """"""
    ExcelFile = "ExcelFile"
    """"""
    TextFile = "TextFile"
    """"""
    MdFile = "MdFile"
    """"""
    DataSet = "DataSet"
    """"""
    DataTable = "DataTable"
    """"""
    File = "File"
    """"""
    Notebook = "Notebook"
    """"""


@dataclass
class FileMetadata:
    name: Optional[str] = None
    id: Optional[str] = None
    parentId: Optional[str] = None
    path: Optional[str] = None
    type: Optional[Union[FileMetadataType, str]] = None
    isFolder: Optional[bool] = False
    children: List[FileMetadata] = field(default_factory=list)
    size: Optional[int] = 0
    uri: Optional[str] = None
    generation: Optional[str] = None
    metadata: Optional[DataResourceSchema] = None
    digest: Optional[str] = None
    itemCreatedDate: Optional[datetime] = None
    itemUpdatedDate: Optional[datetime] = None

    def append(self, child):
        return self.children.append(child)
