# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for .....
"""
# from io import StringIO
import pandas
import requests
import sys
import logging
import uuid
import datetime
from typing import List
# from .._utils._constants import api_prefix
from .._utils._utils import ApiInputs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def get_parent_modules_list(api_inputs: ApiInputs, search_filter: str = ""):
    """Get list of data sets.

    Retrieves the list of parent modules either for the entire project across all installations
    or filter by name on the `search_filter`

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    search_filter : str
        Uses contains on the parent module Name (Default value = "").

    Returns
    -------
    tuple (str, pandas.DataFrame)
        Returns the response status of the call and a dataframe containing the data returned by the call.

    """
    payload = {}

    headers = api_inputs.api_headers.default

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/analytics/logic-modules"

    if search_filter != "*" and search_filter != '':
        url = url + f"?searchFilter={search_filter}"

    response = requests.request("GET", url, data=payload, timeout=20, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()

    df = pandas.read_json(response.text)
    logger.info("API Call successful.")

    return response_status, df


def get_clone_modules_list(api_inputs: ApiInputs, parent_module_id: uuid.UUID, search_filter="*"):
    """Get list of data sets.

    Retrieves the list of clone modules either for the specified parent_module_id
    or filter by shared Tag Name on the `search_filter`

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    parent_module_id : uuid.UIID
        Parent logic module identifier
    search_filter : str
        Uses contains on the parent module Name (Default value = "*").

    Returns
    -------
    tuple (str, pandas.DataFrame)
        Returns the response status of the call and a dataframe containing the data returned by the call.

    """
    payload = {}

    headers = api_inputs.api_headers.default

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/analytics/logic-modules-clones/" \
          f"parent-module/{parent_module_id}"

    if search_filter != "*" and search_filter != '':
        url = url + f"?searchFilter={search_filter}"

    response = requests.request("GET", url, data=payload, timeout=20, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()

    df = pandas.read_json(response.text)
    logger.info("API Call successful.")

    return response_status, df


# def run_clone_modules(api_inputs: ApiInputs, parent_module_id: uuid.UUID, start_date: datetime.date,
#                       end_date: datetime.date, share_to_tags: List[str] = None):
#     """Get list of data sets.
#
#     Run the list of clone modules for the specified parent_module_id
#     and the share to tags list
#
#     Parameters
#     ----------
#     api_inputs : ApiInputs
#         Object returned by initialize() function.
#     parent_module_id : uuid.UUID
#         Identifier for parent module.
#     start_date : datetime.date
#         Date the reprocess should start at.
#     end_date : datetime.date
#         Date the reprocess should finish at.
#     share_to_tags : List[str], optional
#         List of Tag names received via the get_clone_modules_list method
#
#     Returns
#     -------
#     tuple (str, pandas.DataFrame)
#         Returns the response status of the call and a dataframe containing the data returned by the call.
#
#     """
#     if start_date > end_date:
#         logger.error('start_date must be prior to end_date: start_date= %s, end_date= %s', start_date.__str__(),
#                      end_date.__str__())
#         return pandas.DataFrame()
#
#     payload = {
#         "parentModuleId": parent_module_id,
#         "dateFrom": start_date.isoformat(),
#         "dateTo": end_date.isoformat(),
#         "tagsList": share_to_tags
#     }
#
#     headers = {
#         'x-functions-key': api_inputs.api_key,
#         'Content-Type': 'application/json; charset=utf-8',
#         'user-key': api_inputs.user_id
#     }
#
#     if api_inputs.datacentre == '' or api_inputs.api_key == '':
#         logger.error("You must call initialize() before using API.")
#         return pandas.DataFrame()
#
#     url = api_prefix + api_inputs.datacentre + "/" + api_inputs.api_project_id + "/RunLogicModule"
#     response = requests.post(url, json=payload, headers=headers)
#     response_status = '{} {}'.format(response.status_code, response.reason)
#     if response.status_code != 200:
#         logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
#                      response.reason)
#         return response_status, pandas.DataFrame()
#     elif len(response.text) == 0:
#         logger.error('No data returned for this API call. %s', response.request.url)
#         return response_status, pandas.DataFrame()
#
#     table_data = StringIO(response.text)
#     df = pandas.read_table(table_data, sep=',')
#     logger.info("API Call successful.")
#     return response_status, df


def sensor_has_not_changed(api_inputs: ApiInputs, start_date: datetime.date, end_date: datetime.date,
                           templates: List[str] = None, hours_unchanged: int = 24):
    """Get list of sensors which haven't changed value for the given period and at least ``hours_unchanged``.

    Run the Has Not Changed Query for Selected List of Sites (empty List means All)
    and Selected List of Templates  (empty List means All)

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    start_date : datetime.date
        Date the reprocess should start at.
    end_date : datetime.date
        Date the reprocess should finish at.
    templates : List[str]
        List of ObjectPropertyTemplateNames
    hours_unchanged: int
        number of hours the sensor value has not changed

    Returns
    -------
    tuple (str, pandas.DataFrame)
        Returns the response status of the call and a dataframe containing the data returned by the call as a tuple.

    """

    headers = api_inputs.api_headers.default

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if templates.count == 0:
        logger.error("You must supply templates to report on.")
        return pandas.DataFrame()

    payload = {
        "dateFrom": start_date.isoformat(),
        "dateTo": end_date.isoformat(),
        "templatesList": templates,
        "hoursUnchanged": hours_unchanged
    }

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/analytics/run-adx-query/SensorHasNotChanged"

    response = requests.post(url, json=payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()

    df = pandas.read_json(response.text)
    logger.info("API Call successful.")
    return response_status, df
