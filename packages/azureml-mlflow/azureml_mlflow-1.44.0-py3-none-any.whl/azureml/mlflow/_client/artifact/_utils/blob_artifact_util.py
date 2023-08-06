# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import re
from azure.storage.blob import BlobClient
from azureml.mlflow._client.artifact._utils.file_utils import makedirs_for_file_path
from azureml.mlflow._common._cloud.cloud import _get_cloud_or_default

module_logger = logging.getLogger(__name__)


def is_source_uri_matches_storage_blob(source_uri, **kwargs):
    """
    Regex matches the source_uri with azure storage blob url
    :param source_uri: The name of the file to normalize (may or may not contain the file extension).
    :type source_uri: str
    :return: true if regex matches successfully
    :rtype: bool
    """
    cloud = kwargs.pop("cloud", None)
    storage_endpoint = cloud.suffixes.storage_endpoint if cloud else _get_cloud_or_default().suffixes.storage_endpoint
    pattern = '^{}(.*){}(.*){}(.*){}(.*)'.format(re.escape("https://"),
                                                 re.escape(".blob.{}/".format(storage_endpoint)),
                                                 re.escape("/"),
                                                 re.escape("?"))
    return re.match(pattern, source_uri) is not None


def download_file(source_uri, path=None, **kwargs):
    module_logger.debug("downloading file to {path}".format(path=path))
    cloud = kwargs.pop("cloud", None)

    if path is None:
        module_logger.debug('Output file path is {}, the file was not downloaded.'.format(path))
        return

    if is_source_uri_matches_storage_blob(source_uri, cloud=cloud):
        blob_client = BlobClient.from_blob_url(source_uri)

        makedirs_for_file_path(path)

        with open(path, "wb") as file:
            blob_client.download_blob().readinto(file)


def upload_blob_from_stream(stream, artifact_uri):
    blob_client = BlobClient.from_blob_url(artifact_uri)
    module_logger.debug(f"Uploading stream to container {blob_client.container_name}")
    blob_client.upload_blob(stream)
