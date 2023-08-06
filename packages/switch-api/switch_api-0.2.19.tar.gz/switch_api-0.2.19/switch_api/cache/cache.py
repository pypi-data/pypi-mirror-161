# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for Cache data requests
"""

from datetime import datetime
import json
import logging
import sys
import requests
import uuid

import pandas

from .._utils._utils import (ApiInputs, is_valid_uuid)
from .._utils._constants import CACHE_SCOPE


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def set_cache(api_inputs: ApiInputs, scope: CACHE_SCOPE, key: str, val: any, scope_id: uuid.UUID = None):
    """
    Sets data to be stored in cache for later retrieval.

    Parameters
    ----------
    api_inputs: ApiInputs
        Object returned by initialize() function.
    scope: CACHE_SCOPE
        Cache scope for the stored data
    key: str
        Key of to be stored data. Used when retrieving this data.
    val: any
        Data to be stored for later retrieval.
    scope_id: UUID
        UUID in relation to the scope that was set. Used as well when retrieving the data later on.
        For Task scope provide TaskId (self.id when calling from the driver)
        For DataFeed scope provide UUID4 for local testing. 
            api_inputs.data_feed_id will be used when running in the cloud. 
        For Portfolio scope, scope_id will be ignored and api_inputs.api_project_id will be used.

    Returns
    -------
    """
    
    if not set([scope]).issubset(set(CACHE_SCOPE.__args__)):
        logger.error('scope parameter must be set to one of the allowed values defined by the '
                        'CACHE_SCOPE literal: %s', CACHE_SCOPE.__args__)
        return pandas.DataFrame()
    
    scope_id_str = str(scope_id)
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if scope != 'Portfolio' and not is_valid_uuid(scope_id_str):
        logger.error("Invalid UUID v4 passed into scope_id parameter. Please provide a valid UUID v4.")
        return pandas.DataFrame()
    
    if isinstance(val, pandas.DataFrame):
        val = val.to_json(orient="records")
        memory_usage = sys.getsizeof(val)
        if (memory_usage > 2000000):
            logger.error(f"Data size limit reached. Only 2mb data size is allowed for cache. Size reached {round(memory_usage / 1000000, 2)}mb.")
            return pandas.DataFrame()
    elif isinstance(val, datetime):
        val = val.isoformat()

    headers = api_inputs.api_headers.integration
    
    json_payload = {
        "key": key.strip(),
        "value": val,
        "settings": {
            "dataFeedId": scope_id_str if api_inputs.data_feed_id is None \
                or api_inputs.data_feed_id == '00000000-0000-0000-0000-000000000000' \
                    or api_inputs.data_feed_id == '' else api_inputs.data_feed_id,
            "taskId": scope_id_str,
            "cacheScope": scope
        }
    }

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/task-insights/cache/set"
    logger.info("Sending request: POST %s", url)

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    response_json = json.loads(response.text)

    logger.info("Response status: %s", response_status)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                        response_json['message'])
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)

    return response_json
    
    

def get_cache(api_inputs: ApiInputs, scope: CACHE_SCOPE, key: str, scope_id: uuid.UUID = None):
    """
    Gets data stored in cache.

    Parameters
    ----------
    api_inputs: ApiInputs
        Object returned by initialize() function.
    scope: CACHE_SCOPE
        Cache scope for the stored data
    key: str
        Key of to be stored data. Used when retrieving this data.
    scope_id: UUID
        UUID in relation to the scope that was set. Used as well when retrieving the data later on.
        For Task scope provide TaskId (self.id when calling from the driver)
        For DataFeed scope provide UUID4 for local testing. 
            api_inputs.data_feed_id will be used when running in the cloud. 
        For Portfolio scope, scope_id will be ignored and api_inputs.api_project_id will be used.

    Returns
    -------
    """

    if not set([scope]).issubset(set(CACHE_SCOPE.__args__)):
        logger.error('scope parameter must be set to one of the allowed values defined by the '
                        'CACHE_SCOPE literal: %s', CACHE_SCOPE.__args__)
        return pandas.DataFrame()

    scope_id_str = str(scope_id)
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if scope != 'Portfolio' and not is_valid_uuid(scope_id_str):
        logger.error("Invalid UUID v4 passed into scope_id parameter. Please provide a valid UUID v4.")
        return pandas.DataFrame()

    headers = api_inputs.api_headers.integration

    json_payload = {
        "key": key.strip(),
        "settings": {
            "dataFeedId": scope_id_str if api_inputs.data_feed_id is None \
                or api_inputs.data_feed_id == '00000000-0000-0000-0000-000000000000' \
                    or api_inputs.data_feed_id == '' else api_inputs.data_feed_id,
            "taskId": scope_id_str,
            "cacheScope": scope
        }
    }

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/task-insights/cache/get"
    logger.info("Sending request: POST %s", url)

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    response_json = json.loads(response.text)
    
    logger.info("Response status: %s", response_status)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                        response_json['message'])
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
    
    return response_json
    
