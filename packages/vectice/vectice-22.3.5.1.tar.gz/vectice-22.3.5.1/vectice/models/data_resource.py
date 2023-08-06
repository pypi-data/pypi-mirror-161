from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from vectice.api.json.data_resource_schema import DataResourceSchema
from vectice.api.json.data_resource_path_type import DataResourcePathType
from vectice.api.json.data_resources_path import DataResourcePath


@dataclass
class DataResource:
    name: str
    description: Optional[str] = None
    path: Optional[DataResourcePath] = None
    schema: Optional[DataResourceSchema] = None

    @classmethod
    def create_resource(self, uri: str) -> DataResource:
        parsed_uri = urlparse(uri)
        items = parsed_uri.path.split("/")
        name = items[-1]
        path = parsed_uri.netloc + parsed_uri.path
        parent = parsed_uri.netloc + "/".join(items[:-1])
        return DataResource(
            name,
            "",
            path=DataResourcePath(
                name, parent, path, uri, path, DataResourcePathType.get_file_type(path), uri.endswith("/")
            ),
            schema=DataResourceSchema(
                DataResourcePathType.get_file_type(path), name, "", DataResourcePathType.get_file_type(path)
            ),
        )

    @classmethod
    def create_item_resource(cls, uri: str) -> DataResource:
        # sanity checks
        if not uri.startswith("gs://"):
            raise RuntimeError("The only file system supported is Google Cloud storage")
        # TODO: chek path is an item (file, table)
        path = uri.replace("gs://", "")
        name = uri.split("/")[-1]
        bucket = path.split("/")[0]
        return DataResource(
            name,
            "",
            path=DataResourcePath(name, bucket, path, uri, path, DataResourcePathType.get_file_type(path), False),
            schema=DataResourceSchema(
                DataResourcePathType.get_file_type(path), name, "", DataResourcePathType.get_file_type(path)
            ),
        )

    @classmethod
    def create_folder_resource(cls, folder: str) -> DataResource:
        # sanity checks
        if not folder.startswith("gs://"):
            raise RuntimeError("The only file system supported is Google Cloud storage")
        # TODO: check path is a folder (directory, schema)
        if not folder.endswith("/"):
            folder = folder + "/"
        path = folder.replace("gs://", "")
        name = folder.split("/")[-2]
        bucket = path.split("/")[0]
        return DataResource(
            name,
            "",
            path=DataResourcePath(name, bucket, path, folder, path, DataResourcePathType.Folder, True),
            schema=DataResourceSchema(DataResourcePathType.Folder, name, "", DataResourcePathType.Folder),
        )
