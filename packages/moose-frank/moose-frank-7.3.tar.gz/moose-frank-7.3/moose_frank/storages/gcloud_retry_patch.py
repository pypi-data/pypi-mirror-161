from google.api_core import retry
from google.cloud.storage import Client
from storages.backends.gcloud import GoogleCloudFile, GoogleCloudStorage
from storages.utils import clean_name, setting


_original_gcloud_file_init = GoogleCloudFile.__init__
_original_gcloud_storage_init = GoogleCloudStorage.__init__
_original_gcloud_storage_get_default_settings = GoogleCloudStorage.get_default_settings
_original_gcloud_storage_listdir = GoogleCloudStorage.listdir
_original_gcloud_storage_client = GoogleCloudStorage.client
_original_gcloud_storage_bucket = GoogleCloudStorage.bucket


def _gcloud_file_patched_init(self, name, mode, storage):
    _original_gcloud_file_init(self, name, mode, storage)
    if self.blob:
        self._apply_backoff_blob()


def _gcloud_file__apply_backoff_blob(self):
    """
    Every Blob method that needs a backoff wrapper
    and is used by this class must be wrapped here
    """
    self.blob.upload_from_file = self._storage.retry_handler(self.blob.upload_from_file)
    self.blob.download_to_file = self._storage.retry_handler(self.blob.download_to_file)


def _gcloud_storage_patched_init(self, **settings):
    _original_gcloud_storage_init(self, **settings)
    if self.retry:
        predicate = (
            retry.if_exception_type(*self.retryable)
            if self.retryable
            else retry.if_transient_error
        )

        # Most functions aren't available at this point
        # so we'll keep this wrapper to wrap them later
        self.retry_handler = retry.Retry(
            predicate=predicate,
            initial=self.initial_delay,
            maximum=self.max_delay,
            deadline=self.deadline,
        )
        self._apply_backoff_self()
    else:
        self.retry_handler = lambda func, on_error=None: func


def _gcloud_storage_patched_get_default_settings(self):
    default_settings = _original_gcloud_storage_get_default_settings(self)
    default_settings.update(
        {
            "retry": setting("GS_RETRY", False),
            "initial_delay": setting("GS_INITIAL_DELAY", 1.0),
            "max_delay": setting("GS_MAX_DELAY", 60.0),
            "deadline": setting("GS_DEADLINE", 120.0),
            "retryable": setting("GS_RETRYABLE", None),
        }
    )
    return default_settings


def _gcloud_storage_patched_listdir(self, name):
    name = self._normalize_name(clean_name(name))
    # For bucket.list_blobs and logic below name needs to end in /
    # but for the root path "" we leave it as an empty string
    if name and not name.endswith("/"):
        name += "/"

    prefixes, blobs = self._get_blobs(name, "/")

    files = []
    dirs = []

    for blob in blobs:
        parts = blob.name.split("/")
        files.append(parts[-1])
    for folder_path in prefixes:
        parts = folder_path.split("/")
        dirs.append(parts[-2])

    return list(dirs), files


def _gcloud_storage_patched_property_client(self):
    if self._client is None:
        self._client = Client(project=self.project_id, credentials=self.credentials)
        self._apply_backoff_client()
    return self._client


def _gcloud_storage_patched_property_bucket(self):
    if self._bucket is None:
        self._bucket = self.client.bucket(self.bucket_name)
        self._apply_backoff_bucket()
    return self._bucket


def _gcloud_storage__apply_backoff_self(self):
    """
    If any class method needs a backoff wrapper
    then it must be wrapped here. In most cases
    wrapping a whole class method is the last
    thing you should do. Instead of this, you
    should try to wrap a Client/Bucket method.
    """
    self._get_blobs = self.retry_handler(self._get_blobs)


def _gcloud_storage__apply_backoff_client(self):
    """
    Every Client method that needs a backoff wrapper
    and is used by this class must be wrapped here
    """
    self.client.create_bucket = self.retry_handler(self.client.create_bucket)
    self.client.get_bucket = self.retry_handler(self.client.get_bucket)


def _gcloud_storage__apply_backoff_bucket(self):
    """
    Every Bucket method that needs a backoff wrapper
    and is used by this class must be wrapped here
    """
    self.bucket.delete_blob = self.retry_handler(self.bucket.delete_blob)
    self.bucket.get_blob = self.retry_handler(self.bucket.get_blob)


def _gcloud_storage__get_blobs(self, prefix, delimiter):
    """
    This method allows us to treat the whole
    list_blobs process as if it were just one
    API request. Thus, it's easier to wrap it with
    a backoff handler and to control the time it
    uses in case of getting an internal server error.
    """
    iterator = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
    blobs = list(iterator)
    return iterator.prefixes, blobs


def apply_gcloud_retry_patch():
    GoogleCloudFile.__init__ = _gcloud_file_patched_init
    GoogleCloudFile._apply_backoff_blob = _gcloud_file__apply_backoff_blob

    GoogleCloudStorage.__init__ = _gcloud_storage_patched_init
    GoogleCloudStorage.get_default_settings = (
        _gcloud_storage_patched_get_default_settings
    )
    GoogleCloudStorage.listdir = _gcloud_storage_patched_listdir
    GoogleCloudStorage.client = property(_gcloud_storage_patched_property_client)
    GoogleCloudStorage.bucket = property(_gcloud_storage_patched_property_bucket)

    GoogleCloudStorage._apply_backoff_self = _gcloud_storage__apply_backoff_self
    GoogleCloudStorage._apply_backoff_client = _gcloud_storage__apply_backoff_client
    GoogleCloudStorage._apply_backoff_bucket = _gcloud_storage__apply_backoff_bucket
    GoogleCloudStorage._get_blobs = _gcloud_storage__get_blobs


def revert_gcloud_retry_patch():
    GoogleCloudFile.__init__ = _original_gcloud_file_init
    GoogleCloudStorage.__init__ = _original_gcloud_storage_init
    GoogleCloudStorage.get_default_settings = (
        _original_gcloud_storage_get_default_settings
    )
    GoogleCloudStorage.listdir = _original_gcloud_storage_listdir
    GoogleCloudStorage.client = _original_gcloud_storage_client
    GoogleCloudStorage.bucket = _original_gcloud_storage_bucket
