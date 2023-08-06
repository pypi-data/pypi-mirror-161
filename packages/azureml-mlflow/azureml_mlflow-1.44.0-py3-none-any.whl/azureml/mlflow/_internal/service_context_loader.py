# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os

from six.moves.urllib import parse

from azureml.mlflow._common.constants import RunEnvVars

from .utils import (get_service_context_from_tracking_url_default_auth,
                    get_service_context_from_tracking_url_mlflow_env_vars,
                    get_v2_service_context)

logger = logging.getLogger(__name__)


def _mlflow_env_vars_set():
    return ("MLFLOW_TRACKING_URI" in os.environ
            and "MLFLOW_TRACKING_TOKEN" in os.environ and "MLFLOW_RUN_ID" in os.environ
            and ("MLFLOW_EXPERIMENT_ID" in os.environ or "MLFLOW_EXPERIMENT_NAME" in os.environ))


def _is_remote():
    return RunEnvVars.ID in os.environ or "MLFLOW_RUN_ID" in os.environ


class _AzureMLServiceContextLoader(object):
    """
    _AzureMLStoreLoader loads an AzureMLStore from 3 supported scenarios.

    1, new tracking_uri without is remote set to True. A store is created from the uri
    2, is remote set to true in a workspace tracking uri. Loads the
       store information from the current Run context and sets the experiment and ActiveRun.
    3, a cached result of option 1 or 2, this cache is relative to the netloc + path of the tracking_uri
    """

    _tracking_uri_to_service_context = {}

    @classmethod
    def has_service_context(cls, store_uri):
        cache_key = store_uri.split("?")[0]
        return cache_key in cls._tracking_uri_to_service_context

    @classmethod
    def add_service_context(cls, store_uri, service_context):
        cache_key = store_uri.split("?")[0]
        if not hasattr(service_context, "auth"):
            cls._tracking_uri_to_service_context[cache_key] = get_v2_service_context(service_context)
        else:
            cls._tracking_uri_to_service_context[cache_key] = service_context

    @classmethod
    def get_service_context(cls, store_uri):
        cache_key = store_uri.split("?")[0]
        return cls._tracking_uri_to_service_context[cache_key]

    @classmethod
    def load_service_context(cls, store_uri):
        parsed_url = parse.urlparse(store_uri)
        cache_key = store_uri.split("?")[0]

        if cls.has_service_context(cache_key):
            return cls.get_service_context(cache_key)

        elif _mlflow_env_vars_set():
            service_context = get_service_context_from_tracking_url_mlflow_env_vars(parsed_url)
            logger.debug(
                "Created a new service context from mlflow env vars: {}".format(service_context))
            cls.add_service_context(cache_key, service_context)
        else:
            service_context = get_service_context_from_tracking_url_default_auth(parsed_url)
            logger.debug("Creating a new {} for a local run".format(service_context))
            cls.add_service_context(cache_key, service_context)

        return cls.get_service_context(cache_key)
