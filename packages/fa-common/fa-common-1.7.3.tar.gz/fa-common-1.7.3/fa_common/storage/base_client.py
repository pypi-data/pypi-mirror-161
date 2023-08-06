import abc
from io import BytesIO
from typing import List, Optional, Union

from fastapi import UploadFile

from .model import File


class BaseClient(abc.ABC):
    @abc.abstractmethod
    async def make_bucket(self, name: str) -> None:
        pass

    @abc.abstractmethod
    async def bucket_exists(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    async def delete_bucket(self, name: str):
        pass

    @abc.abstractmethod
    async def list_files(self, bucket_name: str, parent_path: str = "") -> List[File]:
        pass

    @abc.abstractmethod
    async def upload_file(
        self, file: UploadFile, bucket_name: str, parent_path: str = "", timeout: int = 60
    ) -> File:
        pass

    @abc.abstractmethod
    async def upload_string(
        self,
        string: Union[str, bytes],
        bucket_name: str,
        file_path: str,
        content_type="text/plain",
    ) -> File:
        pass

    @abc.abstractmethod
    async def get_file_ref(self, bucket_name: str, file_path: str) -> Optional[File]:
        pass

    @abc.abstractmethod
    async def get_file(self, bucket_name: str, file_path: str) -> Optional[BytesIO]:
        pass

    @abc.abstractmethod
    async def file_exists(self, bucket_name: str, file_path: str) -> bool:
        pass

    @abc.abstractmethod
    async def folder_exists(self, bucket_name: str, path: str) -> bool:
        pass

    @abc.abstractmethod
    async def delete_file(self, bucket_name: str, file_path: str, recursive: bool = False) -> None:
        """
        Deletes a file or folder from the specified bucket

        Arguments:
            bucket_name {str} -- [description]
            file_path {str} -- [description]

        Keyword Arguments:
            recursive {bool} -- Deletes all child & folders files from a non empty folder (default: {False})

        """

    @abc.abstractmethod
    async def rename_file(self, bucket_name: str, file_path: str, new_file_path: str) -> File:
        pass

    @abc.abstractmethod
    async def copy_file(self, from_bucket: str, from_path: str, to_bucket: str, to_path: str) -> None:
        pass

    @abc.abstractmethod
    async def create_temp_file_url(self, bucket: str, path: str, expire_time_hours: int = 3) -> File:
        """Enable file to be downloaded without auth via a URL temporarily"""

    @abc.abstractclassmethod
    def get_uri(cls, bucket_name: str, path: str) -> str:
        pass
