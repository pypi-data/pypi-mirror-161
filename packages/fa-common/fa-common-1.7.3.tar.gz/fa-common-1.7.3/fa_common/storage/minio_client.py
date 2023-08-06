from io import BytesIO
from typing import List, Optional, Union

from fastapi import UploadFile
from minio import Minio
from minio.commonconfig import CopySource
from minio.datatypes import Object
from minio.deleteobjects import DeleteObject
from minio.error import MinioException

from fa_common import StorageError, force_async, get_current_app
from fa_common import logger as LOG
from fa_common import sizeof_fmt

from .base_client import BaseClient
from .model import File


class MinioClient(BaseClient):
    """
    Singleton client for interacting with Minio. Note we are wrapping all the call in threads to
    enable async support to a sync library.
    Please don't use it directly, use `core.storage.utils.get_storage_client`.
    """

    __instance = None
    minio: Minio = None

    def __new__(cls) -> "MinioClient":
        """
        Get called before the constructor __init__ and allows us to return a singleton instance.

        Returns:
            [MinioClient] -- [Singleton Instance of client]
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.minio = app.minio  # type: ignore
        return cls.__instance

    async def make_bucket(self, name: str) -> None:
        try:
            await force_async(self.minio.make_bucket)(name)
        except MinioException as err:
            if hasattr(err, "code") and err.code == "BucketAlreadyOwnedByYou":
                LOG.warning(f"Bucket {name} already owned by app")
                return
            if hasattr(err, "code") and err.code == "BucketAlreadyExists":
                LOG.warning(f"Bucket {name} already exists")
                return

            LOG.error(f"Unable to create bucket {name}")
            LOG.error(err)
            raise err

    async def bucket_exists(self, name: str) -> bool:
        return await force_async(self.minio.bucket_exists)(name)

    @classmethod
    def get_uri(cls, bucket_name: str, path: str) -> str:
        # FIXME: this probably won't work as indented
        return f"{bucket_name}/{path}"

    @classmethod
    def object_to_file(cls, obj: Object, bucket_name: str, file_name: str = None) -> Optional[File]:
        is_dir = obj.is_dir
        path = obj.object_name
        path_segments = path.split("/")

        if is_dir:
            if len(path_segments) == 1:
                return None
            path_segments = path_segments[0:-1]

        name = path_segments[-1]
        path = "/".join(path_segments[0:-1])

        LOG.debug("Converting Minio Object: {}", obj)

        return File(
            id=obj.object_name,
            url=obj.bucket_name + obj.object_name,
            size=sizeof_fmt(obj.size),
            size_bytes=obj.size,
            dir=is_dir,
            path=path,
            name=name,
            content_type=obj.content_type,
        )

    async def list_files(self, bucket_name: str, parent_path: str = "") -> List[File]:
        objects = await force_async(self.minio.list_objects)(bucket_name, prefix=parent_path)
        files: List[File] = []
        for obj in objects:
            file = self.object_to_file(obj, bucket_name)
            if file is not None:
                files.append(file)
        return files

    async def upload_string(
        self,
        string: Union[str, bytes],
        bucket_name: str,
        file_path: str,
        content_type="text/plain",
    ) -> File:
        try:
            string_io: BytesIO = (
                BytesIO(string.encode("utf-8")) if isinstance(string, str) else BytesIO(string)
            )
            await force_async(self.minio.put_object)(
                bucket_name,
                file_path,
                string_io,
                len(string),
                content_type=content_type,
            )

        except MinioException as err:
            LOG.error(str(err))
            raise StorageError("Something went wrong uploading file {}", file_path)
        obj = await force_async(self.minio.stat_object)(bucket_name, file_path)
        scidra_file = self.object_to_file(obj, bucket_name, file_path)
        if scidra_file is None:
            raise StorageError("A file could not be created from the Minio obj")
        return scidra_file

    async def upload_file(
        self, file: UploadFile, bucket_name: str, parent_path: str = "", timeout: int = 60
    ) -> File:

        # Passing timeout as function argument to as baseclient accepts it for gcp.
        # This parameter will not affect function execution for minio.
        LOG.info("Minio put_object currently does not support setting timeout to: {}", timeout)

        if parent_path != "":
            parent_path += "/"
        try:
            await force_async(self.minio.put_object)(
                bucket_name, parent_path + file.filename, file.file, -1, part_size=10 * 1024 * 1024
            )

        except MinioException as err:
            LOG.error(str(err))
            raise StorageError("Something went wrong uploading file {}", parent_path + file.filename)
        obj = await force_async(self.minio.stat_object)(bucket_name, parent_path + file.filename)
        scidra_file = self.object_to_file(obj, bucket_name, parent_path + file.filename)
        if scidra_file is None:
            raise StorageError("A file could not be created from the Minio obj")
        return scidra_file

    async def get_file_ref(self, bucket_name: str, file_path: str) -> Optional[File]:
        obj_ref = await force_async(self.minio.stat_object)(bucket_name, file_path)
        return self.object_to_file(obj_ref, bucket_name)

    async def get_file(self, bucket_name: str, file_path: str) -> Optional[BytesIO]:
        obj = None
        try:
            obj = await force_async(self.minio.get_object)(bucket_name, file_path)
            return BytesIO(obj.read())
        except MinioException as err:
            if hasattr(err, "code") and err.code == "NoSuchKey":
                return None
            # Likely the file doesn't exist
            LOG.error(str(err))
            raise StorageError("Error getting file {}", file_path)
        finally:
            if obj is not None:
                obj.close()
                obj.release_conn()

    async def file_exists(self, bucket_name: str, file_path: str) -> bool:
        try:
            stats = await force_async(self.minio.stat_object)(bucket_name, file_path)
            LOG.info(stats)
            return stats is not None
        except MinioException as err:
            if hasattr(err, "code") and err.code == "NoSuchKey":
                return False
            LOG.error(str(err))
            raise StorageError("Error checking if {} exists", file_path)

    async def folder_exists(self, bucket_name: str, path: str) -> bool:
        objects = await force_async(self.minio.list_objects)(bucket_name, prefix=path)
        for obj in objects:
            if obj is not None:
                return True
        else:
            return False

    async def delete_file(self, bucket_name: str, file_path: str, recursive: bool = False) -> None:
        try:
            if recursive:
                delete_object_list = map(
                    lambda x: DeleteObject(x.object_name),
                    self.minio.list_objects(bucket_name, file_path, recursive=True),
                )
                errors = self.minio.remove_objects(bucket_name, delete_object_list)
                for error in errors:
                    LOG.error(f"Error occured when deleting file(s) {error}")
            else:
                await force_async(self.minio.remove_object)(bucket_name, file_path)
        except MinioException as err:
            LOG.error(err)
            raise StorageError(f"Somthing went wrong deleting file(s) {bucket_name}/{file_path}")

    async def delete_bucket(self, name: str):
        try:
            await self.delete_file(name, "", True)
            return await force_async(self.minio.remove_bucket)(name)
        except MinioException as err:
            LOG.error(f"Unable to delete bucket {name}")
            LOG.error(err)
            raise err

    async def rename_file(self, bucket_name: str, file_path: str, new_file_path: str) -> File:
        try:
            await force_async(self.minio.copy_object)(
                bucket_name, new_file_path, CopySource(bucket_name, file_path)
            )
        except MinioException as err:
            LOG.error(f"Error renaming {file_path} to {new_file_path} in bucket {bucket_name}: {str(err)}")
            raise StorageError(f"Somthing went wrong renaming {file_path} to {new_file_path}")
        await self.delete_file(bucket_name, file_path)
        obj = await force_async(self.minio.stat_object)(bucket_name, new_file_path)
        file = self.object_to_file(obj, bucket_name, new_file_path)
        if file is None:
            raise StorageError("A file could not be created from the Minio obj")
        return file

    async def copy_file(self, from_bucket: str, from_path: str, to_bucket: str, to_path: str) -> None:
        try:
            await force_async(self.minio.copy_object)(to_bucket, to_path, CopySource(from_bucket, from_path))
        except MinioException as err:
            LOG.error(f"Error copying {from_bucket} {from_path} to {to_bucket} {to_path} : {str(err)}")
            raise StorageError(f"Somthing went wrong copying {from_path} to {to_path}")

    async def create_temp_file_url(self, bucket: str, path: str, expire_time_hours: int = 3) -> File:
        # FIXME make this work
        raise NotImplementedError("Minio support for temp downloads currently not working.")
