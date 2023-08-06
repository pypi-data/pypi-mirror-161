import asyncio
import datetime
from io import BytesIO
from typing import Iterator, List, Optional, Union

from fastapi import UploadFile
from google.auth import compute_engine
from google.auth.exceptions import RefreshError
from google.auth.transport import requests
from google.cloud.exceptions import Conflict, GoogleCloudError, NotFound
from google.cloud.storage import Client as GCPClient
from google.cloud.storage.bucket import Blob, Bucket

from fa_common import StorageError, force_async, get_current_app, get_settings
from fa_common import logger as LOG
from fa_common import sizeof_fmt

from .base_client import BaseClient
from .model import File


class GoogleStorageClient(BaseClient):
    """
    Singleton client for interacting with GoogleStorage. Note we are wrapping all the call in threads to
    enable async support to a sync library.
    Please don't use it directly, use `core.storage.utils.get_storage_client`.
    """

    __instance = None
    gcp_storage: GCPClient = None

    def __new__(cls) -> "GoogleStorageClient":
        """
        Get called before the constructor __init__ and allows us to return a singleton instance.

        Returns:
            [GoogleStorageClient] -- [Singleton Instance of client]
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.gcp_storage = app.gcp_storage  # type: ignore
        return cls.__instance

    async def make_bucket(self, name: str) -> None:
        try:
            await force_async(self.gcp_storage.create_bucket)(name)
        except Conflict:
            LOG.warning(f"Bucket {name} already exists")

    async def bucket_exists(self, name: str) -> bool:
        bucket = await force_async(self.gcp_storage.lookup_bucket)(name)
        return bucket is not None

    async def delete_bucket(self, name: str):
        try:
            bucket = await self._get_bucket(name)
            return await force_async(bucket.delete)(force=True)
        except ValueError:
            LOG.warning(f"Too many object in the bucket, unable to delete Bucket: {name}")
            raise StorageError(f"Too many object in the bucket, unable to delete Bucket: {name}")

    async def _get_bucket(self, name: str) -> Bucket:
        """
        Internal method to GCP bucket
        """
        try:
            return await force_async(self.gcp_storage.get_bucket)(name)
        except NotFound:
            LOG.error("Trying to get bucket {} that doesn't exist", name)
            raise StorageError(f"Trying to get bucket {name} that doesn't exist")

    async def _get_blob(self, bucket_name, path):
        """
        Internal method to get GCP blob reference
        """
        # bucket = self.gcp_storage.bucket(bucket_name)
        bucket = await self._get_bucket(bucket_name)
        return bucket.blob(self.convert_path_in(path, bucket_name))

    async def _list_blobs(self, bucket_name, prefix) -> Iterator[Blob]:
        bucket = await self._get_bucket(bucket_name)
        return await force_async(bucket.list_blobs)(prefix=self.convert_path_in(prefix, bucket_name))

    @classmethod
    def convert_path_in(cls, path: str, bucket_name) -> str:
        return path

    @classmethod
    def convert_path_out(cls, path: str, bucket_name) -> str:
        return path

    @classmethod
    def get_uri(cls, bucket_name: str, path: str) -> str:
        return f"gs://{bucket_name}/{path}"

    @classmethod
    def blob_to_file(cls, blob: Blob, bucket_name: str) -> Optional[File]:
        if blob.size is None and blob.exists():
            blob.reload()

        is_dir = blob.name.endswith("/")
        path = cls.convert_path_out(blob.name, bucket_name)
        path_segments = path.split("/")

        gs_uri = None
        if is_dir:
            if len(path_segments) == 1:
                return None
            path_segments = path_segments[0:-1]
        else:
            gs_uri = f"gs://{blob.bucket.name}/{blob.name}"

        name = path_segments[-1]
        path = "/".join(path_segments[:-1])

        return File(
            id=blob.id,
            url=blob.public_url,
            gs_uri=gs_uri,
            size=sizeof_fmt(blob.size),
            size_bytes=blob.size,
            dir=is_dir,
            path=path,
            name=name,
            content_type=blob.content_type,
        )

    async def list_files(self, bucket_name: str, parent_path: str = "") -> List[File]:
        blobs = await self._list_blobs(bucket_name, parent_path)
        files: List[File] = []
        for blob in blobs:
            file = self.blob_to_file(blob, bucket_name)
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

        blob = await self._get_blob(bucket_name, file_path)
        try:
            await force_async(blob.upload_from_string)(string, content_type=content_type)
        except GoogleCloudError as err:
            LOG.error(str(err))
            raise StorageError("Something went wrong uploading file {}", file_path)
        scidra_file = self.blob_to_file(blob, bucket_name)
        if scidra_file is None:
            raise StorageError("A file could not be created from the GCP blob")
        return scidra_file

    async def upload_file(
        self, file: UploadFile, bucket_name: str, parent_path: str = "", timeout: int = 60
    ) -> File:
        bucket = await self._get_bucket(bucket_name)
        path = self.convert_path_in(parent_path, bucket_name)
        if path != "":
            path += "/"

        blob = bucket.blob(path + file.filename)
        try:
            file.file.seek(0)
            # Increasing timeout instead of using default to allow processing of really large files.
            await force_async(blob.upload_from_file)(
                file.file, content_type=file.content_type, timeout=timeout
            )
        except GoogleCloudError as err:
            LOG.error(str(err))
            raise StorageError("Something went wrong uploadinf file {}", path + file.filename)
        scidra_file = self.blob_to_file(blob, bucket_name)
        if scidra_file is None:
            raise StorageError("A file could not be created from the GCP blob")
        return scidra_file

    async def get_file_ref(self, bucket_name: str, file_path: str) -> Optional[File]:
        blob = await self._get_blob(bucket_name, file_path)
        return self.blob_to_file(blob, bucket_name)

    async def get_file(self, bucket_name: str, file_path: str) -> Optional[BytesIO]:
        blob = await self._get_blob(bucket_name, file_path)
        if not (blob and blob.exists()):
            return None

        byte_stream = BytesIO()
        await force_async(blob.download_to_file)(byte_stream)
        byte_stream.seek(0)
        return byte_stream

    async def file_exists(self, bucket_name: str, file_path: str) -> bool:
        blob = await self._get_blob(bucket_name, file_path)

        return blob.exists()

    async def folder_exists(self, bucket_name: str, path: str) -> bool:
        blobs = await self._list_blobs(bucket_name, path)
        for blob in blobs:
            return True

        return False

    async def _delete_blob(self, blob: Blob):
        await force_async(blob.delete)()

    async def delete_file(self, bucket_name: str, file_path: str, recursive: bool = False) -> None:
        try:
            if recursive:
                blobs = await self._list_blobs(bucket_name, file_path)
                futures = [self._delete_blob(blob) for blob in blobs]
                if futures:
                    await asyncio.wait(futures)
                else:
                    raise StorageError(
                        f"Trying to delete a folder {bucket_name}/{file_path} that doesn't exist."
                    )
            else:
                blob = await self._get_blob(bucket_name, file_path)
                await self._delete_blob(blob)
        except NotFound:
            raise StorageError(f"Trying to delete a file {bucket_name}/{file_path} that doesn't exist.")

    async def rename_file(self, bucket_name: str, file_path: str, new_file_path: str) -> File:
        bucket = await self._get_bucket(bucket_name)
        blob = bucket.blob(self.convert_path_in(file_path, bucket_name))
        if blob.exists():
            new_blob = await force_async(bucket.rename_blob)(
                blob, self.convert_path_in(new_file_path, bucket_name)
            )
        else:
            raise StorageError(f"Trying to rename a file {bucket_name}/{file_path} that doesn't exist.")

        LOG.debug(f"{file_path} renamed to {new_file_path}")
        file = self.blob_to_file(new_blob, bucket_name)
        if file is None:
            raise StorageError("A file could not be created from the GCP blob")
        return file

    async def copy_file(self, from_bucket: str, from_path: str, to_bucket: str, to_path: str) -> None:
        bucket = await self._get_bucket(from_bucket)
        blob = bucket.blob(self.convert_path_in(from_path, from_bucket))
        if blob.exists():
            await force_async(bucket.copy_blob)(
                blob,
                await self._get_bucket(to_bucket),
                self.convert_path_in(to_path, to_bucket),
            )
        else:
            raise StorageError(f"Trying to copy a file {from_bucket}/{from_path} that doesn't exist.")
        LOG.debug(f"{from_path} copied to {to_path}")

    async def create_temp_file_url(self, bucket: str, path: str, expire_time_hours: int = 3) -> File:
        blob = await self._get_blob(bucket, path)
        expire_time = datetime.timedelta(hours=expire_time_hours)

        try:
            # GCE signer does not work as expected causing generate_signed_url to fail
            # without private key associated with service account supplied.
            # This happens even when cloud run is executed with the service account.
            # See https://github.com/googleapis/google-auth-library-python/issues/50.
            # Current workaround is to supply the credentials as an argument.
            # See https://gist.github.com/jezhumble/91051485db4462add82045ef9ac2a0ec.
            signing_credentials = compute_engine.IDTokenCredentials(
                requests.Request(),
                "",
                service_account_email=self.gcp_storage._credentials.service_account_email,
            )
            url = blob.generate_signed_url(
                expiration=expire_time, credentials=signing_credentials, version="v4"
            )
        except RefreshError:
            # Refresh error may occur if Compute engine metadata is unavailable, in which case signing
            # is done using json supplied.
            # Retaining this so that existing usage that does not utilise cloud run does not break.
            url = blob.generate_signed_url(expiration=expire_time, version="v4")
        LOG.info(f"Created url: {url} for file download")
        file_ref = self.blob_to_file(blob, bucket)
        if file_ref is None:
            raise StorageError(f"Cannot generate a temporary url {bucket}/{path} for a folder.")
        file_ref.url = url
        return file_ref


class FirebaseStorageClient(GoogleStorageClient):
    """
    Singleton client for interacting with FirebaseStorage. Note this is the same as the GoogleStorageClient
    except it uses a single bucket with folders
    Please don't use it directly, use `core.storage.utils.get_storage_client`.
    """

    __instance = None
    # gcp_storage: storage.Client = None
    bucket: Bucket = None

    def __new__(cls) -> "FirebaseStorageClient":
        """
        Get called before the constructor __init__ and allows us to return a singleton instance.

        Returns:
            [FirebaseStorageClient] -- [Singleton Instance of client]
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.gcp_storage = app.gcp_storage  # type: ignore
            cls.__instance.bucket = app.gcp_storage.get_bucket(get_settings().BUCKET_NAME)  # type: ignore
        return cls.__instance

    @classmethod
    def convert_path_in(cls, path: str, bucket_name) -> str:
        if path.startswith("/"):
            path = path[1:]
        return get_settings().BUCKET_USER_FOLDER + bucket_name + "/" + path

    @classmethod
    def convert_path_out(cls, path: str, bucket_name) -> str:
        return path.replace(get_settings().BUCKET_USER_FOLDER + bucket_name + "/", "")

    @classmethod
    def get_uri(cls, bucket_name: str, path: str) -> str:
        return f"gs://{get_settings().BUCKET_NAME}/{cls.convert_path_in(path, bucket_name)}"

    # Override to return single bucket for all users
    async def _get_bucket(self, name: str) -> Bucket:
        return self.bucket

    async def make_bucket(self, name: str) -> None:
        blob = self.bucket.blob(get_settings().BUCKET_USER_FOLDER + name + "/")
        await force_async(blob.upload_from_string)(
            "", content_type="application/x-www-form-urlencoded;charset=UTF-8"
        )

    async def bucket_exists(self, name: str) -> bool:
        blob = self.bucket.blob(get_settings().BUCKET_USER_FOLDER + name + "/")
        return await force_async(blob.exists)()

    @staticmethod
    def log_error_not_found(blob):
        LOG.warning("Trying to delete file {} that doesn't exist", blob.name)

    async def delete_bucket(self, name: str):
        blobs = list(
            await force_async(self.bucket.list_blobs)(prefix=get_settings().BUCKET_USER_FOLDER + name + "/")
        )
        await force_async(self.bucket.delete_blobs)(blobs, on_error=self.log_error_not_found)
