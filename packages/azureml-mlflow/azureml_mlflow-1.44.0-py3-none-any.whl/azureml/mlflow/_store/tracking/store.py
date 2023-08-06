# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""**AzureMLflowStore** provides a class to read and record run metrics and artifacts on Azure via MLflow."""

import logging
import os

from functools import wraps
from azureml.mlflow._common.constants import RunEnvVars
from azureml.mlflow._store.azureml_reststore import AzureMLAbstractRestStore

VERSION_WARNING = "Could not import {}. Please upgrade to Mlflow 1.4.0 or higher."

logger = logging.getLogger(__name__)

try:
    from mlflow.store.tracking.rest_store import RestStore
except ImportError:
    logger.warning(VERSION_WARNING.format("from mlflow"))
    from mlflow.store.rest_store import RestStore

_MLFLOW_RUN_ID_ENV_VAR = "MLFLOW_RUN_ID"


class AzureMLRestStore(AzureMLAbstractRestStore, RestStore):
    """
    Client for a remote tracking server accessed via REST API calls.

    :param service_context: Service context for the AzureML workspace
    :type service_context: azureml._restclient.service_context.ServiceContext
    """

    def __init__(self, service_context, host_creds=None, **kwargs):
        """
        Construct an AzureMLRestStore object.

        :param service_context: Service context for the AzureML workspace
        :type service_context: azureml._restclient.service_context.ServiceContext
        """
        logger.debug("Initializing the AzureMLRestStore")
        AzureMLAbstractRestStore.__init__(self, service_context, host_creds)
        RestStore.__init__(self, self.get_host_creds, **kwargs)

    @wraps(RestStore.update_run_info)
    def update_run_info(self, run_id, *args, **kwargs):
        remote_run_id = os.environ.get(RunEnvVars.ID)
        if remote_run_id is not None and run_id == remote_run_id:
            logger.debug("Status update was skipped for remote run {}".format(run_id))
            return self.get_run(run_id).info
        return super(AzureMLRestStore, self).update_run_info(run_id, *args, **kwargs)
