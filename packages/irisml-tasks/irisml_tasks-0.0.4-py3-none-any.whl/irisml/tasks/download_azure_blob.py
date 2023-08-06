import dataclasses
import hashlib
import logging
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, ContainerClient
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Download a single blob from Azure Blob Storage.

    Returns the downloaded bytes.

    There are two ways to specify the blob.
    1. Use blob_url
    2. Use container_url and blob_path.

    If both urls are specified, raises ValueError.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        blob_url: Optional[str] = None
        container_url: Optional[str] = None
        blob_path: Optional[str] = None
        sha1_hash: Optional[str] = None

    @dataclasses.dataclass
    class Outputs:
        data: bytes = None

    def execute(self, inputs):
        if self.config.blob_url and (self.config.container_url or self.config.blob_path):
            raise ValueError("You cannot specify both blob_url and container_url.")

        if not (self.config.blob_url or self.config.container_url):
            raise ValueError("You must specify either blob_url or container_url.")

        if self.config.container_url and not self.config.blob_path:
            raise ValueError("You must specify blob_path if container_url is used.")

        if self.config.blob_url:
            blob_client = BlobClient.from_blob_url(self.config.blob_url, credential=DefaultAzureCredential())
            downloaded_bytes = blob_client.download_blob().readall()
        elif self.config.container_url:
            container_client = ContainerClient.from_container_url(self.config.container_url, credential=DefaultAzureCredential())
            downloaded_bytes = container_client.download_blob(self.config.blob_path).readall()

        file_hash = hashlib.sha1(downloaded_bytes).hexdigest()
        logger.info(f"Downloaded {len(downloaded_bytes)} bytes. SHA1 hash: {file_hash}")

        if self.config.sha1_hash and self.config.sha1_hash != file_hash:
            raise ValueError(f"The downloaded file has an unexpected hash value. Expected: {self.config.sha1_hash}. Actual: {file_hash}")

        return self.Outputs(downloaded_bytes)
