# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module containing the helper functions useful when integrating asset creation, asset updates, data ingestion, etc
into the Switch Automation Platform.
"""
import json
import pandas
import requests
import datetime
import logging
import sys
from .._utils._constants import SUPPORT_PAYLOAD_TYPE  # , QUERY_LANGUAGE
from .._utils._utils import ApiInputs, requests_retry_session, is_valid_uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def _timezones(api_inputs: ApiInputs):
    """Get timezones

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.

    Returns
    -------
    df : pandas.DataFrame


    """
    # payload = {}
    headers = api_inputs.api_headers.default

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    # upload Blobs to folder
    url = f"{api_inputs.api_base_url}/timezones/all"
    logger.info("Sending request: GET %s", url)

    response = requests.request("GET", url, timeout=20, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()

    df = pandas.read_json(response.text, orient='index')
    df.rename(columns={0: 'TimezoneName'}, inplace=True)
    df['TimezoneId'] = df.index

    return df


def _timezone_offsets(api_inputs: ApiInputs, date_from: datetime.date, date_to: datetime.date,
                      installation_id_list: list):
    """Get timezones

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    date_from : datetime.date
        First (earliest) record
    date_to : datetime.date
        Last (latest) record
    installation_id_list : list
        List of InstallationIDs

    Returns
    -------
    df : pandas.DataFrame
        A dataframe containing the timezone offsets per InstallationID - if multiple timezone offsets occur for the
        submitted period, there will be a row per offset date range. E.g. for a timezone with daylight savings

    """
    payload = {
        "dateFrom": date_from.isoformat(),
        "dateTo": date_to.isoformat(),
        "installationIds": installation_id_list
    }

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    headers = api_inputs.api_headers.default

    url = f"{api_inputs.api_base_url}/timezones/offsets"
    logger.info("Sending request: POST %s", url)

    try:
        response = requests_retry_session(method_whitelist=['POST']).post(url, json=payload, headers=headers)

        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        response_data_frame = pandas.read_json(response.text)
        return response_data_frame
    except Exception as ex:
        logger.error("API Call was not successful.", ex)
        return pandas.DataFrame()


def _timezone_dst_offsets(api_inputs: ApiInputs, date_from: datetime.date, date_to: datetime.date,
                          installation_id_list: list = None, timezone_name: str = None):
    """Get timezones

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    date_from : datetime.date
        First (earliest) record
    date_to : datetime.date
        Last (latest) record
    installation_id_list : list
        List of InstallationIDs
    timezone_name: str
        Specific timezone name to retrieve DST offsets.
        Defaults to None.

    Returns
    -------
    df : pandas.DataFrame
        A dataframe containing the timezone offsets per InstallationID - if multiple timezone offsets occur for the
        submitted period, there will be a row per offset date range. E.g. for a timezone with daylight savings

    """
    payload = {
        "dateFrom": date_from.isoformat(),
        "dateTo": date_to.isoformat(),
        "installationIds": installation_id_list,
        "timezoneName": timezone_name
    }

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if timezone_name == '':
        logger.error("timezone_name parameter cannot be an empty string.")
        return pandas.DataFrame()

    headers = api_inputs.api_headers.default

    url = f"{api_inputs.api_base_url}/timezones/dst-transitions"
    if not timezone_name is None:
        url = f"{api_inputs.api_base_url}/timezones/name/dst-transitions"

    logger.info("Sending request: POST %s", url)

    try:
        response = requests_retry_session(method_whitelist=['POST']).post(url, json=payload, headers=headers)

        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        timezone_intervals = json.loads(response.text)
        site_timezones = pandas.DataFrame.from_dict(timezone_intervals['installationTimezoneList'])
        timezone_offsets = pandas.DataFrame.from_dict(timezone_intervals['dstTransitions'])
        timezone_offsets = timezone_offsets.explode('dstIntervals')
        timezone_offsets = timezone_offsets.reset_index(drop=True).join(timezone_offsets.reset_index(drop=True)
                                                                        .dstIntervals.apply(pandas.Series)).drop(columns=['dstIntervals', 'timezoneName'])
        if timezone_name is None:
            return site_timezones.merge(timezone_offsets, on='timezoneId')
        else:
            return timezone_offsets
    except Exception as ex:
        logger.error("API Call was not successful.", ex)
        return pandas.DataFrame()

def _upsert_entities_affected_count(api_inputs: ApiInputs, entities_affected_count: int):
    """Updates data feed and data feed file status entities affected count.

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    entities_affected_count : int
        Count of affected entities - i.e. how many records are being upserted, replaced or appended.

    Returns
    -------

    """

    if entities_affected_count is None:
        entities_affected_count = 0

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if not is_valid_uuid(api_inputs.data_feed_id):
        logger.error("Entities Affected Count can only be upserted when called in Production.")
        return False

    if not is_valid_uuid(api_inputs.data_feed_file_status_id):
        logger.error("Entities Affected Count can only be upserted when called in Production.")
        return False

    headers = api_inputs.api_headers.default

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/" \
          f"{api_inputs.data_feed_id}/file-status/{api_inputs.data_feed_file_status_id}/entities-affected/" \
          f"{entities_affected_count}"

    response = requests.request("PUT", url, timeout=20, headers=headers)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
    elif response.status_code == 200:
        logger.info("Entities Affected Count successfully upserted. ")


def _adx_support(api_inputs: ApiInputs, payload_type: SUPPORT_PAYLOAD_TYPE):
    """
        Call ADX Support endpoint to trigger SQL->ADX sync

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    payload_type : SUPPORT_PAYLOAD_TYPE
        Payload Type to sync ADX

    Returns
    -------


    """
    headers = api_inputs.api_headers.default

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if payload_type == None:
        logger.error("You must provide the ADX Support Payload Type to SYNC ADX.")
        return pandas.DataFrame()

    if not set([payload_type]).issubset(set(SUPPORT_PAYLOAD_TYPE.__args__)):
        logger.error('payload_type parameter must be set to one of the allowed values defined by the '
                     'SUPPORT_PAYLOAD_TYPE literal: %s', SUPPORT_PAYLOAD_TYPE.__args__)
        return pandas.DataFrame()

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/adx/sync/{payload_type}"

    response = requests.request("PUT", url, timeout=20, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()

    logger.info("API Call successful.")

    return response_status, response.text
