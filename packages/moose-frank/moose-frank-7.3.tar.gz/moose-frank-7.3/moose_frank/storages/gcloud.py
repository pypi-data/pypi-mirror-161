from datetime import timedelta

from django.contrib.staticfiles.storage import ManifestFilesMixin
from django.core.files.storage import get_storage_class
from google.oauth2 import service_account
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting


class StorageMixin:
    cache_control = (
        f"max-age={60 * 60 * 24 * 7}, s-maxage={60 * 60 * 24 * 7}, must-revalidate"
    )
    default_acl = "publicRead"
    file_overwrite = False
    retry = True


class ManifestStaticFilesStorage(StorageMixin, ManifestFilesMixin, GoogleCloudStorage):
    bucket_name = setting("STATIC_BUCKET_NAME")
    custom_endpoint = setting("STATIC_CUSTOM_ENDPOINT")
    location = setting("STATIC_LOCATION", "")
    manifest_name = setting("STATIC_MANIFEST_NAME", ManifestFilesMixin.manifest_name)
    credentials = (
        service_account.Credentials.from_service_account_info(
            setting("STATIC_CREDENTIALS")
        )
        if setting("STATIC_CREDENTIALS")
        else None
    )


class MediaStorage(StorageMixin, GoogleCloudStorage):
    bucket_name = setting("MEDIA_BUCKET_NAME")
    location = setting("MEDIA_LOCATION", "")
    custom_endpoint = setting("MEDIA_CUSTOM_ENDPOINT")
    credentials = (
        service_account.Credentials.from_service_account_info(
            setting("MEDIA_CREDENTIALS")
        )
        if setting("MEDIA_CREDENTIALS")
        else None
    )


class ThumbnailStorage(MediaStorage):
    file_overwrite = True


private_files_storage = get_storage_class()()

if hasattr(private_files_storage, "default_acl"):  # pragma: no cover
    private_files_storage.default_acl = "private"
    private_files_storage.expiration = timedelta(hours=1)
    private_files_storage.custom_endpoint = None
