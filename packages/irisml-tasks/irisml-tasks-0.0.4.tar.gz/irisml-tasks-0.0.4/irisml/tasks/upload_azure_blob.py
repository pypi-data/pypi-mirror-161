import dataclasses
import logging
import typing
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, ContainerClient
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Upload a binary file to Azure Storage Blob.

    For the details of Config, see download_azure_blob task's help.

    Raises:
        azure.storage.exceptions if failed.

    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        data: bytes

    @dataclasses.dataclass
    class Config:
        blob_url: typing.Optional[str] = None
        container_url: typing.Optional[str] = None
        blob_path: typing.Optional[str] = None

    def execute(self, inputs):
        if self.config.blob_url and (self.config.container_url or self.config.blob_path):
            raise ValueError("You cannot specify both blob_url and container_url.")

        if not (self.config.blob_url or self.config.container_url):
            raise ValueError("You must specify either blob_url or container_url.")

        if self.config.container_url and not self.config.blob_path:
            raise ValueError("You must specify blob_path if container_url is used.")

        if self.config.blob_url:
            blob_client = BlobClient.from_blob_url(self.config.blob_url, credential=DefaultAzureCredential())
            blob_client.upload_blob(inputs.data)
        elif self.config.container_url:
            container_client = ContainerClient.from_container_url(self.config.container_url, credential=DefaultAzureCredential())
            container_client.upload_blob(self.config.blob_path, inputs.data)

        logger.info(f"Uploaded {len(inputs.data)} bytes.")
        return self.Outputs()
