from fastapi import FastAPI

from fa_common import StorageType, get_settings, logger

from .base_client import BaseClient

# from minio.error import ResponseError


def setup_storage(app: FastAPI) -> None:
    settings = get_settings()
    if settings.STORAGE_TYPE == StorageType.MINIO:
        from minio import Minio
        from minio.credentials import IamAwsProvider, StaticProvider

        if settings.MINIO_ENDPOINT is None:
            raise ValueError("Minio endpoint missing from env variables")

        # Minio has a `ChainedProvider` class which should allow us to define multiple options however
        # it doesn't appear to work properly?
        if settings.MINIO_ACCESS_KEY is None and settings.MINIO_SECRET_KEY is None:
            logger.info("Storage set to Minio using IAM AWS authentication")
            credential_provider = IamAwsProvider()
        else:
            if settings.MINIO_ACCESS_KEY is None or settings.MINIO_SECRET_KEY is None:
                raise ValueError("Missing minio settings from env variables")
            else:
                logger.info("Storage set to Minio using access/secret key authentication")
                credential_provider = StaticProvider(
                    settings.MINIO_ACCESS_KEY, settings.MINIO_SECRET_KEY.get_secret_value()
                )

        minioClient = Minio(
            settings.MINIO_ENDPOINT,
            credentials=credential_provider,
            secure=settings.MINIO_SSL,
        )

        app.minio = minioClient  # type: ignore
    elif settings.STORAGE_TYPE in [
        StorageType.GCP_STORAGE,
        StorageType.FIREBASE_STORAGE,
    ]:
        from google.cloud.storage import Client as GCPClient

        # Uses GOOGLE_APPLICATION_CREDENTIALS Env Var
        gcp_storage_client = GCPClient()
        app.gcp_storage = gcp_storage_client  # type: ignore
    elif settings.STORAGE_TYPE == StorageType.NONE:
        logger.info("Storage set to NONE and cannot be used")
        return
    else:
        raise ValueError("STORAGE_TYPE Setting is not a valid storage option.")


def get_storage_client() -> BaseClient:
    if get_settings().STORAGE_TYPE == StorageType.MINIO:
        from .minio_client import MinioClient

        return MinioClient()
    elif get_settings().STORAGE_TYPE == StorageType.GCP_STORAGE:
        from .gcp_client import GoogleStorageClient

        return GoogleStorageClient()
    elif get_settings().STORAGE_TYPE == StorageType.FIREBASE_STORAGE:
        from .gcp_client import FirebaseStorageClient

        return FirebaseStorageClient()

    raise ValueError("STORAGE_TYPE Setting is not a valid storage option.")
