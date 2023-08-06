import logging
import os
from typing import BinaryIO, Union, List

from vectice.api import Client
from vectice.api.json.attachment import AttachmentOutput


class AttachmentContainer:
    def __init__(self, name: str, id: int, client: Client, container_type: str):
        self._client = client
        self._id = id
        self._name = name
        self._container_type = container_type

    def update_attachments(self, file_path: Union[str, List[str]]):
        """
        add an attachment to the entity

        :param file_path: the path to the attachment
        """
        attachments = []
        if isinstance(file_path, list):

            for file in file_path:
                try:
                    curr_file = ("file", (file, open(file, "rb")))
                    attachments.append(curr_file)
                except Exception:
                    logging.warning(f"Did not read {file}.")
        else:
            attachments = [("file", (file_path, open(file_path, "rb")))]
        self._client.update_attachments(self._container_type.lower(), attachments, self._id)

    def list_attachments(self) -> List[str]:
        """
        List attachments of the entity

        """
        attachments = self._client.list_attachments(self._container_type.lower(), self._id)
        files = []
        for attachment in attachments.list:
            files.append(attachment.fileName)
        return files

    def delete_attachments(self, file_path: Union[List[str], str]):
        """
        remove an attachment from the entity

        :param file_path: the path to the attachment
        """
        attachments: List[str] = []
        if isinstance(file_path, str):
            attachments.append(file_path)
        else:
            attachments = file_path

        try:
            attachment_list = {
                attach.fileName: attach.fileId
                for attach in self._client.list_attachments(self._container_type.lower(), self._id).list
            }
        except Exception as e:
            raise ValueError(f"{self._container_type} attachment failed to retrieve. Due to {e}")
        for file in attachments:
            file_id = attachment_list.get(file)
            if file_id:
                self._client.delete_attachment(self._container_type.lower(), self._id, file_id)
            else:
                raise ValueError(f"The file path for {file} is not valid. The file does not exist.")

    def add_attachments(self, file_path: Union[str, List[str]]):
        """
        add an attachment to the entity

        :param file_path: the path to the attachment
        """
        attachments = []
        attached_files = self.list_attachments()
        if isinstance(file_path, list):
            for file in file_path:
                try:
                    if not os.path.exists(file):
                        raise ValueError(f"the file path {file} is not valid. the file does not exist")
                    curr_file = ("file", (file, open(file, "rb")))
                    attachments.append(curr_file)
                    file_name = file.split("/")[-1]
                    if file_name in attached_files:
                        raise RuntimeError(f"{file_path} is already attached to '{self._name}'")
                except Exception:
                    logging.warning(f"Did not read {file}.")
        else:
            if not os.path.exists(file_path):
                raise ValueError(f"The file path {file_path} is not valid. The file does not exist.")
            attachments = [("file", (file_path, open(file_path, "rb")))]
            file_name = file_path.split("/")[-1]
            if file_name in attached_files:
                raise RuntimeError(f"{file_path} is already attached to '{self._name}'")
        self._client.create_attachments(self._container_type.lower(), attachments, self._id)

    def get_attachment(self, file_path: str) -> BinaryIO:
        """
        Get an attachment content from the entity

        :param file_path: the path to the attachment

        :return: BinaryIO
        """
        try:
            attachment_list = {
                attach.fileName: attach.fileId
                for attach in self._client.list_attachments(self._container_type.lower(), self._id).list
            }
        except Exception as e:
            raise ValueError(f"list of attachment for {self._container_type} failed . Due to {e}")
        file_id = attachment_list.get(file_path)
        if file_id:
            try:
                return self._client.get_attachment(self._container_type.lower(), file_id, self._id)
            except Exception as e:
                raise ValueError(
                    f"{self._container_type} attachment failed to retrieve attachment named '{file_path}' due to:\n {e}"
                )
        else:
            raise ValueError(
                f"{self._container_type} attachment failed to retrieve attachment named '{file_path}'. Please check the filename."
            )

    def get_attachment_as_file(self, file_path: str, saved_path: str):
        """
        Get an attachment content from the entity and store it in a file

        :param file_path: the path to the file
        :param saved_path: the path to the file

        :return: None
        """
        attachment = self.get_attachment(file_path)
        with open(saved_path, "wb") as content:
            while True:
                chunk = attachment.read(128)
                if not chunk:
                    break
                content.write(chunk)

    def _list_attachments(self) -> List[AttachmentOutput]:
        """
        List attachments of the entity

        """
        return self._client.list_attachments(self._container_type.lower(), self._id).list
