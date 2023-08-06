from __future__ import annotations

from typing import Optional, List, Tuple, Union, Generic, TypeVar, TYPE_CHECKING, Callable, Sequence, Dict

import re
from urllib.parse import urlparse

if TYPE_CHECKING:
    from mypy_boto3_s3.type_defs import ObjectTypeDef
    from google.cloud.storage import Blob
    from botocore.session import Session

from vectice.api.json import FileMetadataType, FileMetadata, DataResourceSchema, SchemaColumn, DataType

NOTEBOOK = {"ipynb": True}
IMAGE_FILE = {"png": True, "jpeg": True, "svg": True}

MetadataType = TypeVar("MetadataType")


def remove_ending_slashes(path):
    # we got some case where we have several '/'
    while path.endswith("/"):
        path = path[0:-1]
    return path


class FileEntry(Generic[MetadataType]):
    def __init__(self, path: str, metadata: MetadataType):
        self.path = path
        self.metadata = metadata

    def __repr__(self):
        return f"FileEntry(path={self.path})"


def create_tree(
    entries: Sequence[FileEntry], mapper: Callable[[FileEntry], FileMetadata], protocol: str
) -> List[FileMetadata]:
    metadata_index: Dict[str, FileMetadata] = {}

    def get_entry(path: str) -> Optional[FileMetadata]:
        return metadata_index.get(path, None)

    def add_folder_entry(path: str) -> FileMetadata:
        if "/" in path:
            parent_path, name = path.rsplit("/", 1)
            parent_path = remove_ending_slashes(parent_path)
        elif path == "":
            parent_path = None
            name = ""
        else:
            parent_path = ""
            name = path

        result = FileMetadata(
            name,
            path + "/",
            parent_path + "/" if parent_path is not None else None,
            path + "/",
            FileMetadataType.Folder,
            True,
            [],
            uri=f"{protocol}://{path}/",
        )
        if parent_path is not None:
            parent = get_entry(parent_path)
            if parent is None:
                parent = add_folder_entry(parent_path)
            parent.children.append(result)
        metadata_index[path] = result
        return result

    def add_file_entry(file_entry: FileEntry):
        path = remove_ending_slashes(file_entry.path)
        parent_path = path.rsplit("/", 1)[0]
        parent = get_entry(remove_ending_slashes(parent_path))
        if parent is None:
            parent = add_folder_entry(remove_ending_slashes(parent_path))
        parent.children.append(mapper(file_entry))

    for entry in entries:
        if not entry.path.endswith("/"):
            add_file_entry(entry)

    return metadata_index[""].children


class Node(Generic[MetadataType]):
    def __init__(self, path: str, metadata: MetadataType):
        self.path = path
        self.metadata = metadata


def schema_validation(description, max_length, precision, scale):
    return (
        description if description is not None else 0,
        max_length if max_length is not None else 0,
        precision if precision is not None else 0,
        scale if scale is not None else 0,
    )


def extract_table_data(table, table_name):
    schema_columns, type_check = [], None
    for schema in table.schema:
        data_type = str(schema.field_type).lower().capitalize()
        try:
            type_check = DataType[data_type].__dict__["_value_"]
        except KeyError:
            pass
        schema_description, schema_max_length, schema_precision, schema_scale = schema_validation(
            schema.description, schema.max_length, schema.precision, schema.scale
        )
        schema_columns += [
            SchemaColumn(
                name=schema.name,
                description=schema_description,
                dataType=type_check,
                length=schema_max_length,
                precision=schema_precision,
                scale=schema_scale,
            )
        ]
    data_resource_schema = DataResourceSchema(
        type=FileMetadataType.DataTable,
        name=table_name,
        description="",
        fileFormat="bigquery#table",
        columns=schema_columns,
    )
    return data_resource_schema


def get_all_files_in_folder(client, database_name, project_id) -> Tuple[List[FileMetadata], int]:
    from google.cloud.bigquery import DatasetReference

    files_size = 0
    children: List[FileMetadata] = []
    tables = client.list_tables(database_name)

    for curr_table in tables:
        table_name = curr_table.table_id
        table_reference = DatasetReference(project_id, database_name).table(table_name)
        table = client.get_table(table_reference)
        data_resource_schema = extract_table_data(table, table_name)
        table_name, created, updated, size = table.table_id, table.created, table.modified, table.num_bytes
        files_size += size
        uri = f"bigquery://{project_id}/bigquery-public-data.{database_name}.{table_name}"
        children += [
            FileMetadata(
                name=table_name,
                uri=uri,
                itemCreatedDate=created,
                itemUpdatedDate=updated,
                size=int(files_size),
                type=FileMetadataType.DataTable,
                metadata=data_resource_schema,
            )
        ]

    return children, files_size


def extract_bigquery_metadata(
    uri: str, service_account_json_path: Optional[str] = None
) -> Optional[List[FileMetadata]]:
    """
    The terms table and dataset are switched when working with the Google BigQuery SDK and looking at the UI.
    So a table is actually a dataset in the SDK and a dataset is a table.
    """
    from google.cloud import bigquery
    from google.cloud.bigquery import DatasetReference

    matches = re.search(r"bigquery://(.*?)/(.*?)/(.+)?", uri)
    if matches:
        match_project, match_dataset, match_table = matches.group(1), matches.group(2), matches.group(3)
    elif matches is None:
        matches = re.search(r"bigquery://(.*?)/(.+)?", uri)
        match_project, match_dataset, match_table = matches.group(1), matches.group(2), None  # type: ignore
    else:
        raise ValueError("Please provide a valid project/dataset/table uri.")

    if service_account_json_path is None:
        client = bigquery.Client(project=match_project)
    else:
        client = bigquery.Client.from_service_account_json(service_account_json_path, project=match_project)
    if match_table and match_dataset:
        table_reference = DatasetReference(match_project, match_dataset).table(match_table)
        table = client.get_table(table_reference)
        data_resource_schema = extract_table_data(table, match_table)
        name, created, updated, size = table.table_id, table.created, table.modified, table.num_bytes
        uri = f"bigquery://{match_project}/bigquery-public-data.{match_dataset}.{match_table}"
        return [
            FileMetadata(
                name=name,
                uri=uri,
                itemCreatedDate=created,
                itemUpdatedDate=updated,
                size=int(size),
                type=FileMetadataType.DataTable,
                metadata=data_resource_schema,
            )
        ]
    elif match_dataset and not match_table:
        children, files_size = get_all_files_in_folder(client, match_dataset, match_project)
        uri = f"bigquery://{match_dataset}"
        return [
            FileMetadata(
                name=match_dataset,
                uri=uri,
                size=files_size,
                isFolder=True,
                children=children,
                type=FileMetadataType.Folder,
            )
        ]
    else:
        raise ValueError("Please check that a valid uri was provided.")


def decode_hash(blob):
    import base64
    import binascii

    # decode the hash provided
    base64_message = blob.md5_hash
    md5_hash = binascii.hexlify(base64.urlsafe_b64decode(base64_message))
    return md5_hash.decode("utf-8")


def get_file_type(file_name):
    file_type = file_name.split(".", 1)
    if len(file_type) == 2:
        if "csv" == file_type[1].lower():
            return "CsvFile"
        elif NOTEBOOK.get(file_type[1].lower()):
            return "Notebook"
        elif IMAGE_FILE.get(file_type[1].lower()):
            return "ImageFile"
        elif "md" == file_type[1].lower():
            return "MdFile"
        else:
            return "File"
    else:
        return "File"


def extract_gcs_metadata(
    uri: Union[str, List[str]], service_account_json_path: Optional[str] = None
) -> Optional[List[FileMetadata]]:
    def create_metadata(entry: FileEntry[Blob]) -> FileMetadata:
        parts = entry.path.rsplit("/")
        filename = parts[-1]
        return FileMetadata(
            filename,
            entry.path,
            parts[0],
            entry.path,
            get_file_type(filename),
            entry.path.endswith("/"),
            [],
            entry.metadata.size,
            f"gs://{entry.path}",
            str(entry.metadata.generation),
            None,
            decode_hash(entry.metadata),
            entry.metadata.time_created,
            entry.metadata.updated,
        )

    try:
        from google.cloud import storage  # type: ignore

        if service_account_json_path is None:
            storage_client = storage.Client()
        else:
            storage_client = storage.Client.from_service_account_json(service_account_json_path)
        if isinstance(uri, str):
            uri = [uri]

        entries = []
        for item in uri:
            parsed_uri = urlparse(item)
            bucket_name = parsed_uri.netloc
            blob = parsed_uri.path[1:] if parsed_uri.path.startswith("/") else parsed_uri.path
            blobs_query = list(storage_client.list_blobs(bucket_name, prefix=blob))
            entries.extend([FileEntry(f"{bucket_name}/{(blob.name)}", blob) for blob in blobs_query])
        return create_tree(entries, create_metadata, "gs")
    except ModuleNotFoundError:
        raise RuntimeError("The google-cloud-storage package is needed to use this functionality")


def extract_s3_metadata(
    uri: Union[str, List[str]],
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    profile_name: Optional[str] = None,
    region_name: Optional[str] = None,
    botocore_session: Optional[Session] = None,
) -> Optional[List[FileMetadata]]:
    """
    For credentials, please read AWS instructions at https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    As describe the AWS client also support environment variables `AWS_ACCESS_KEY_ID `, `AWS_SECRET_ACCESS_KEY` and `AWS_SESSION_TOKEN`.
    It also support credentials file in `~/.aws/credentials`.

    :param uri: list of files/folders to be used for the dataset. the metadata will be extracted from this list.
    :type aws_access_key_id: string
    :param aws_access_key_id: AWS access key ID
    :type aws_secret_access_key: string
    :param aws_secret_access_key: AWS secret access key
    :type aws_session_token: string
    :param aws_session_token: AWS temporary session token
    :type region_name: string
    :param region_name: Default region when creating new connections
    :type profile_name: string
    :param profile_name: The name of a profile to use. If not given, then
                         the default profile is used.
    :type botocore_session: botocore.session.Session
    :param botocore_session: Use this Botocore session instead of creating
                             a new default one.
    :return:
    """

    def create_metadata(entry: FileEntry) -> FileMetadata:
        parts = entry.path.rsplit("/")
        filename = parts[-1]
        return FileMetadata(
            name=filename,
            isFolder=False,
            digest=entry.metadata["ETag"],
            path=entry.path,
            type=get_file_type(filename),
            size=entry.metadata["Size"],
            uri=f"s3://{entry.path}",
            itemUpdatedDate=entry.metadata["LastModified"],
            generation=None if "VersionId" not in entry.metadata else entry.metadata["VersionId"],
        )

    def create_file_entry(client, bucket_name, is_bucket_versioned, blob) -> FileEntry:
        if is_bucket_versioned:
            response = client.list_object_versions(Prefix=blob["Key"], Bucket=bucket_name)
            versions = [*response["Versions"]]
            current = list(filter(lambda v: v["IsLatest"] and v["Key"] == blob["Key"], versions))[0]
        else:
            current = blob
        return FileEntry(f"{bucket_name}/{current['Key']}", current)

    try:
        import boto3

        session = boto3.session.Session(
            profile_name=profile_name,
            aws_session_token=aws_session_token,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            botocore_session=botocore_session,
        )
        client = session.client("s3")
        if isinstance(uri, str):
            uri = [uri]
        entries = []
        for item in uri:
            parsed_uri = urlparse(item)
            bucket_name = parsed_uri.netloc
            response = client.get_bucket_versioning(Bucket=bucket_name)
            is_bucket_versioned = "Status" in response and response["Status"] == "Enabled"
            prefix = parsed_uri.path[1:] if parsed_uri.path.startswith("/") else parsed_uri.path
            blobs_query: List[ObjectTypeDef] = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)["Contents"]
            entries.extend([create_file_entry(client, bucket_name, is_bucket_versioned, blob) for blob in blobs_query])
        return create_tree(entries, create_metadata, "s3")
    except ModuleNotFoundError:
        raise RuntimeError("The boto3 package is needed to use this functionality")


class DatasetMetadata:
    @classmethod
    def create_bigquery(cls, uri: str, service_account_json_path: Optional[str] = None) -> Optional[List[FileMetadata]]:
        dataset_metadata_artifact = extract_bigquery_metadata(uri, service_account_json_path)
        return dataset_metadata_artifact

    @classmethod
    def create_gcs(
        cls, uri: Union[str, List[str]], service_account_json_path: Optional[str] = None
    ) -> Optional[List[FileMetadata]]:
        dataset_metadata_artifact = extract_gcs_metadata(uri, service_account_json_path)
        return dataset_metadata_artifact

    @classmethod
    def create_s3(
        cls,
        uri: Union[str, List[str]],
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        botocore_session: Optional[Session] = None,
    ) -> Optional[List[FileMetadata]]:
        """
        For credentials, please read AWS instructions at https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
        As describe the AWS client also support environment variables `AWS_ACCESS_KEY_ID `, `AWS_SECRET_ACCESS_KEY` and `AWS_SESSION_TOKEN`.
        It also support credentials file in `~/.aws/credentials`.

        :param uri: list of files/folders to be used for the dataset. the metadata will be extracted from this list.
        :type aws_access_key_id: string
        :param aws_access_key_id: AWS access key ID
        :type aws_secret_access_key: string
        :param aws_secret_access_key: AWS secret access key
        :type aws_session_token: string
        :param aws_session_token: AWS temporary session token
        :type region_name: string
        :param region_name: Default region when creating new connections
        :type profile_name: string
        :param profile_name: The name of a profile to use. If not given, then
                             the default profile is used.
        :type botocore_session: botocore.session.Session
        :param botocore_session: Use this Botocore session instead of creating
                                 a new default one.
        :return:
        """
        dataset_metadata_artifact = extract_s3_metadata(
            uri,
            aws_access_key_id,
            aws_secret_access_key,
            aws_session_token,
            profile_name,
            region_name,
            botocore_session,
        )
        return dataset_metadata_artifact
