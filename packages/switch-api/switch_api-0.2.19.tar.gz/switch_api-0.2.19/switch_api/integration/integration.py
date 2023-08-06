# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for integrating asset creation, asset updates, data ingestion, etc into the Switch Automation Platform.
"""
import gc
import re
import sys
from typing import Union
import pandas
import pandas as pd
from ..integration.helpers import get_timezones
import pandera
import requests
import datetime
import logging
import uuid
from .._utils._platform import _get_structure, Blob
from .._utils._utils import (ApiInputs, _with_func_attrs, _column_name_cap, _work_order_schema, convert_bytes)
from .._utils._constants import TAG_LEVEL
from ..integration._utils import _timezone_offsets, _upsert_entities_affected_count, _adx_support, _timezone_dst_offsets

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


@_with_func_attrs(df_required_columns=['ApiProjectId', 'InstallationId', 'NetworkDeviceId', 'UserId', 'BatchNo',
                                       'DriverUniqueId', 'Timestamp', 'DiscoveredValue', 'DriverClassName', 'JobId'],
                  df_optional_columns=['DriverDeviceType', 'ObjectPropertyTemplateName', 'UnitOfMeasureAbbrev',
                                       'DeviceName', 'DisplayName', 'EquipmentType', 'EquipmentLabel', ])
def upsert_discovered_records(df: pandas.DataFrame, api_inputs: ApiInputs, discovery_properties_columns: list,
                              device_tag_columns: list = None, sensor_tag_columns: list = None,
                              metadata_columns: list = None):  # , ontology_tag_columns: list = None):
    """Upsert discovered records to populate Build - Discovery & Selection UI.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the discovered records including the minimum required set of columns.
    api_inputs : ApiInputs
        Object returned by initialize() function.
    discovery_properties_columns : list
        List of the discovery property columns returned by 3rd party API.
    device_tag_columns : list, default = None
        List of columns that represent device-level tag group(s) (Default value = None)
    sensor_tag_columns : list, default = None
        List of column names in input `df` that represent sensor-level tag group(s) (Default value = None).
    metadata_columns : list, default = None
        List of column names in input `df` that represent device-level metadata key(s) (Default value = None).
    # ontology_tag_columns : list, default = None
    #     List of BRICK schema or Haystack tags that apply to a given point (Default value = None).

    Returns
    -------
    tuple[pandas.DataFrame, pandas.DataFrame]
        (response_df, errors_df) - Returns the response dataframe and the dataframe containing the parsed errors text
        (if no errors, then empty dataframe).

    """

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    data_frame = df.copy()

    required_columns = ['ApiProjectId', 'InstallationId', 'NetworkDeviceId', 'UserId', 'BatchNo', 'DriverUniqueId',
                        'Timestamp', 'DiscoveredValue', 'DriverClassName', 'JobId']
    optional_columns = ['DriverDeviceType', 'ObjectPropertyTemplateName', 'UnitOfMeasureAbbrev', 'DeviceName',
                        'DisplayName', 'EquipmentType', 'EquipmentLabel', ]
    proposed_columns = data_frame.columns.tolist()

    if not set(required_columns).issubset(proposed_columns):
        logger.exception('Missing required column(s): %s', set(required_columns).difference(proposed_columns))
        return 'integration.upsert_discovered_records() - df must contain the following columns: ' + ', '.join(
            required_columns) + '. Optional Columns include: ' + ', '.join(optional_columns)

    missing_optional_columns = set(optional_columns) - set(proposed_columns)
    for missing_column in missing_optional_columns:
        data_frame[missing_column] = None

    if discovery_properties_columns is not None and not set(discovery_properties_columns).issubset(data_frame.columns):
        logger.exception('Missing expected discovery property column(s): %s',
                         set(discovery_properties_columns).difference(proposed_columns))
        return 'Integration.upsert_discovered_records(): data_frame must contain the following discovery property column(s): ' + \
               ', '.join(discovery_properties_columns)
    elif discovery_properties_columns is None:
        logger.exception('Missing expected discovery property column(s): %s',
                         set(discovery_properties_columns).difference(proposed_columns))
        return 'Integration.upsert_discovered_records(): data_frame must contain the following discovery property' \
               ' columns: ' + ', '.join(discovery_properties_columns)

    if device_tag_columns is not None and not set(device_tag_columns).issubset(data_frame.columns):
        logger.exception('Missing expected device tag column(s): %s',
                         set(device_tag_columns).difference(proposed_columns))
        return 'Integration.upsert_discovered_records(): data_frame expected to contain the following device tag ' \
               'column(s): ' + ', '.join(device_tag_columns)
    elif device_tag_columns is None:
        device_tag_columns = []

    if sensor_tag_columns is not None and not set(sensor_tag_columns).issubset(data_frame.columns):
        logger.exception('Missing expected sensor tag column(s): %s',
                         set(sensor_tag_columns).difference(proposed_columns))
        return 'Integration.upsert_discovered_records(): data_frame expected to contain the following sensor tag ' \
               'column(s): ' + ', '.join(sensor_tag_columns)
    elif sensor_tag_columns is None:
        sensor_tag_columns = []

    if metadata_columns is not None and not set(metadata_columns).issubset(data_frame.columns):
        logger.exception('Missing expected metadata column(s): %s',
                         set(metadata_columns).difference(proposed_columns))
        return 'Integration.upsert_discovered_records(): data_frame expected to contain the following metadata ' \
               'column(s): ' + ', '.join(metadata_columns)
    elif metadata_columns is None:
        metadata_columns = []

    # if ontology_tag_columns is not None and not set(ontology_tag_columns).issubset(data_frame.columns):
    #     logger.exception('Missing expected ontology tag column(s): %s',
    #                      set(ontology_tag_columns).difference(proposed_columns))
    #     return 'Integration.upsert_discovered_records(): data_frame expected to contain the following ontology tag ' \
    #            'column(s): ' + ', '.join(ontology_tag_columns)
    # elif ontology_tag_columns is None:
    #     ontology_tag_columns = []

    # convert timestamp format to required format
    data_frame.Timestamp = data_frame.Timestamp.dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    data_frame = data_frame.rename(columns={'DiscoveredValue': 'CurrentValue'})

    column_dict = {'DiscoveryProperties': discovery_properties_columns + ['Timestamp'],
                   'DeviceTags': device_tag_columns,
                   'SensorTags': sensor_tag_columns,
                   'Metadata': metadata_columns,
                   # 'OntologyTags': ontology_tag_columns
                   }

    def set_properties(raw_df: pandas.DataFrame, column_dict: dict):
        for key, value in column_dict.items():

            def update_values(row):
                j_row = row[value].to_dict()
                return j_row

            if len(value) > 0:
                raw_df[key] = raw_df.apply(update_values, axis=1)
            else:
                raw_df[key] = None

        return raw_df

    data_frame = set_properties(raw_df=data_frame, column_dict=column_dict)
    data_frame = data_frame.drop(columns=discovery_properties_columns + ['Timestamp'] + device_tag_columns +
                                 sensor_tag_columns + metadata_columns  # + ontology_tag_columns
                                 )
    data_frame = data_frame.assign(OntologyTags=None)

    final_req_cols = ['ApiProjectId', 'InstallationId', 'NetworkDeviceId', 'DriverClassName', 'UserId', 'BatchNo',
                      'DriverUniqueId', 'CurrentValue', 'DriverDeviceType', 'ObjectPropertyTemplateName',
                      'UnitOfMeasureAbbrev', 'DeviceName', 'DisplayName', 'EquipmentType', 'EquipmentLabel',
                      'DeviceTags', 'SensorTags', 'OntologyTags', 'Metadata', 'DiscoveryProperties', 'JobId']

    if set(data_frame.columns.tolist()).issubset(final_req_cols):
        batch_size = 50
        chunk_list = []
        payload_error_list = []
        grouped_df = data_frame.reset_index(drop=True).groupby(by=lambda x: x // batch_size, axis=0)

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/integrations/driver-discovery"
        headers = api_inputs.api_headers.default

        logger.info(f"Input has been batched into {grouped_df.ngroups} group(s). ")

        for name, group in grouped_df:
            discovery_payload = group.groupby(
                by=['ApiProjectId', 'InstallationId', 'NetworkDeviceId', 'DriverClassName', 'UserId', 'BatchNo', 'JobId']).apply(
                lambda x: x[['DriverUniqueId', 'CurrentValue', 'DriverDeviceType', 'ObjectPropertyTemplateName',
                             'UnitOfMeasureAbbrev', 'DeviceName', 'DisplayName', 'EquipmentType', 'EquipmentLabel',
                             'DeviceTags', 'SensorTags', 'OntologyTags', 'Metadata', 'DiscoveryProperties']].to_dict(
                    orient='records')).reset_index().rename(columns={0: 'Sensors'}).to_json(orient='records')

            # remove outer [] from json
            discovery_payload = re.sub(r"^[\[]", '', re.sub(r"[\]]$", '', discovery_payload))

            logger.info(f"Upserting discovery record group {name} of {grouped_df.ngroups - 1}. ")
            response = requests.post(url=url, headers=headers, data=discovery_payload)

            response_status = '{} {}'.format(response.status_code, response.reason)
            if response.status_code != 200 and len(response.text) > 0:
                logger.error(f"API Call was not successful. Response Status: {response.status_code}. "
                             f"Reason: {response.reason}. Error Text: {response.text}")
                payload_error_list += [{'Chunk': name, 'Payload': discovery_payload}]
                if response.text.startswith('{'):
                    response_content = response.json()
                    chunk_list += [{'Chunk': name, 'response_status': response.status_code,
                                    'response_reason': response.reason, 'error_code': response_content['ErrorCode'],
                                    'errors': response_content['Errors']}]
                elif response.text.startswith('"'):
                    chunk_list += [{'Chunk': name, 'response_status': response.status_code,
                                    'response_reason': response.reason, 'errors': response.json()}]
                else:
                    chunk_list += [{'Chunk': name, 'response_status': response.status_code,
                                    'response_reason': response.reason, 'errors': response.text}]
            elif response.status_code != 200 and len(response.text) == 0:
                logger.error(f"API Call was not successful. Response Status: {response.status_code}. "
                             f"Reason: {response.reason}. ")
                payload_error_list += [{'Chunk': name, 'Payload': discovery_payload}]
                chunk_list += [{'Chunk': name, 'response_status': response.status_code,
                                'response_reason': response.reason}]
            elif response.status_code == 200:
                logger.info(f"API Call was successful. ")
                chunk_list += [{'Chunk': name, 'response_status': response.status_code,
                                'response_reason': response.reason}]

        upsert_response_df = pandas.DataFrame(chunk_list)

        if 0 < len(payload_error_list) <= grouped_df.ngroups:
            payload_error_df = pandas.DataFrame(payload_error_list)
            logger.error(f"Errors on upsert of discovered records. ")
            return upsert_response_df, payload_error_df

    return upsert_response_df, pandas.DataFrame()


@_with_func_attrs(df_required_columns=['InstallationCode', 'DeviceCode', 'DeviceName', 'SensorName', 'SensorTemplate',
                                       'SensorUnitOfMeasure', 'EquipmentClass', 'EquipmentLabel'])
def upsert_device_sensors(df: pandas.DataFrame, api_inputs: ApiInputs, tag_columns: list = None,
                          metadata_columns: list = None, save_additional_columns_as_slices: bool = False):
    """Upsert device(s) and sensor(s)

    Required fields are:

    - InstallationCode
    - DeviceCode
    - DeviceName
    - SensorName
    - SensorTemplate
    - SensorUnitOfMeasure
    - EquipmentClass
    - EquipmentLabel

    Parameters
    ----------
    df: pandas.DataFrame
        The asset register created by the driver including the minimum required set of columns.
    api_inputs : ApiInputs
        Object returned by initialize() function.
    tag_columns : list, default = None
        Columns of dataframe that contain tags (Default value = None).
    metadata_columns : list, default = None
        Column(s) of dataframe that contain device-level metadata (Default value = None).
    save_additional_columns_as_slices : bool, default = False
        Whether additional columns should be saved as slices (Default value = False).

    Returns
    -------
    tuple[list, pandas.DataFrame]
        (response_status_list, upsert_response_df) - Returns the list of response statuses and the dataframe containing
        the parsed response text.

    """

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    data_frame = df.copy()

    required_columns = ['InstallationCode', 'DeviceCode', 'DeviceName', 'SensorName', 'SensorTemplate',
                        'SensorUnitOfMeasure', 'EquipmentClass', 'EquipmentLabel']
    proposed_columns = data_frame.columns.tolist()

    if not set(required_columns).issubset(data_frame.columns):
        logger.exception('Missing required column(s): %s', set(required_columns).difference(proposed_columns))
        return 'Integration.upsert_device_sensors(): data_frame must contain the following columns: ' + ', '.join(
            required_columns)

    if tag_columns is not None and not set(tag_columns).issubset(data_frame.columns):
        logger.exception('Missing expected tag column(s): %s', set(tag_columns).difference(proposed_columns))
        return 'Integration.upsert_device_sensors(): data_frame expected to contain the following tag column(s): ' + \
               ', '.join(tag_columns)
    elif tag_columns is None:
        tag_columns = []

    if metadata_columns is not None and not set(metadata_columns).issubset(data_frame.columns):
        logger.exception('Missing expected metadata column(s): %s', set(metadata_columns).difference(proposed_columns))
        return 'Integration.upsert_device_sensors(): data_frame expected to contain the following metadata ' \
               'column(s): ' + ', '.join(metadata_columns)
    elif metadata_columns is None:
        metadata_columns = []

    slice_columns = set(proposed_columns).difference(set(required_columns)) - set(tag_columns) - set(metadata_columns)
    slices_data_frame = pandas.DataFrame()

    if len(slice_columns) > 0 or len(tag_columns) > 0 or len(metadata_columns) > 0:
        def update_values(row, mode):
            if mode == 'A':
                j_row = row[slice_columns].to_json()
                return str(j_row)
            elif mode == 'B':
                j_row = row[tag_columns].to_json()
                return str(j_row)
            else:
                j_row = row[metadata_columns].to_json()
                return str(j_row)

        data_frame['Slices'] = data_frame.apply(update_values, args="A", axis=1)
        data_frame['TagsJson'] = data_frame.apply(update_values, args="B", axis=1)
        data_frame['MetadataJson'] = data_frame.apply(update_values, args="C", axis=1)
        data_frame = data_frame.drop(columns=slice_columns)
        slices_data_frame = data_frame[['DeviceCode', 'Slices']]

    headers = api_inputs.api_headers.integration

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/devices/upsert-ingestion"

    data_frame_grpd = data_frame.groupby(['InstallationCode', 'DeviceCode'])
    chunk_list = []
    for name, group in data_frame_grpd:
        logger.info("Sending request: POST %s", url)
        logger.info('Upserting data for InstallationCode = %s and DeviceCode = %s', str(name[0]), str(name[1]))
        # logger.info('Sensor count to upsert: %s', str(group.shape[0]))

        response = requests.post(url, data=group.to_json(orient='records'), headers=headers)

        response_status = '{} {}'.format(response.status_code, response.reason)
        logger.info("Response status: %s", response_status)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            chunk_list += [{'Chunk': name, 'DeviceCountToUpsert': 1, 'SensorCountToUpsert': str(group.shape[0]),
                            'response_status': response_status, 'response_df': pandas.DataFrame(),
                            'invalid_rows': pandas.DataFrame()}]
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            chunk_list += [{'Chunk': name, 'DeviceCountToUpsert': 1, 'SensorCountToUpsert': str(group.shape[0]),
                            'response_status': response_status, 'response_df': pandas.DataFrame(),
                            'invalid_rows': pandas.DataFrame()}]
        elif response.status_code == 200 and len(response.text) > 0:
            response_data_frame = pandas.read_json(response.text)
            logger.info('Dataframe response row count = %s', str(response_data_frame.shape[0]))
            if response_data_frame.shape[1] > 0:
                response_data_frame = response_data_frame.assign(InstallationCode=str(name[0]),
                                                                 SensorCount=group.shape[0])
                invalid_rows = response_data_frame[response_data_frame['status'] != 'Ok']
                if invalid_rows.shape[0] > 0:
                    logger.error("The following rows contain invalid data: %s", invalid_rows)
                    chunk_list += [
                        {'Chunk': name, 'DeviceCountToUpsert': 1,
                         'SensorCountToUpsert': str(group.shape[0]),
                         'response_status': response_status,
                         'response_df': response_data_frame[response_data_frame['status'] == 'Ok'],
                         'invalid_rows': invalid_rows}]
                else:
                    chunk_list += [{'Chunk': name, 'DeviceCountToUpsert': 1,
                                    'SensorCountToUpsert': str(group.shape[0]),
                                    'response_status': response_status, 'response_df': response_data_frame,
                                    'invalid_rows': invalid_rows}]

    upsert_response_df = pandas.DataFrame()
    upsert_invalid_rows_df = pandas.DataFrame()
    upsert_response_status_list = []
    for i in range(len(chunk_list)):
        upsert_response_df = upsert_response_df.append(chunk_list[i]['response_df'])
        upsert_invalid_rows_df = upsert_invalid_rows_df.append(chunk_list[i]['invalid_rows'])
        upsert_response_status_list += [chunk_list[i]['response_status']]

    if save_additional_columns_as_slices and slices_data_frame.shape[0] > 0:
        slices_merged = pandas.merge(left=upsert_response_df, right=slices_data_frame, left_on='deviceCode',
                                     right_on='DeviceCode')
        slices_data_frame = slices_merged[['deviceId', 'Slices']]
        slices_data_frame = slices_data_frame.rename(columns={'deviceId': 'DeviceId'})
        upsert_data(slices_data_frame, api_inputs=api_inputs, key_columns=['DeviceId'], table_name='DeviceSensorSlices',
                    is_slices_table=True)

    upsert_response_df.columns = _column_name_cap(columns=upsert_response_df.columns)
    _upsert_entities_affected_count(api_inputs=api_inputs,
                                    entities_affected_count=upsert_response_df['SensorCount'].sum())
    _adx_support(api_inputs=api_inputs, payload_type='Sensors')

    logger.info("Ingestion Complete. ")
    return upsert_response_status_list, upsert_response_df


@_with_func_attrs(df_required_columns=['InstallationName', 'InstallationCode', 'Address', 'Country', 'Suburb', 'State',
                                       'StateName', 'FloorAreaM2', 'ZipPostCode'],
                  df_optional_columns=['Latitude', 'Longitude', 'Timezone', 'InstallationId'])
def upsert_sites(df: pandas.DataFrame, api_inputs: ApiInputs, tag_columns: list = None,
                 save_additional_columns_as_slices: bool = False):
    """Upsert site(s).

    The `df` input must contain the following columns:
        - InstallationName
        - InstallationCode
        - Address
        - Suburb
        - State
        - StateName
        - Country
        - FloorAreaM2
        - ZipPostCode

    The following additional columns are optional:
        - Latitude
        - Longitude
        - Timezone
        - InstallationId
            - The UUID of the existing site within the Switch Automation Platform.

    Parameters
    ----------
    df: pandas.DataFrame :
        The dataframe containing the sites to be created/updated in the Switch platform. All required columns must be
        present with no null values.
    api_inputs : ApiInputs
        Object returned by initialize() function.
    tag_columns : list, default=[]
        The columns containing site-level tags. The column header will be the tag group name. (Default value = True)
    save_additional_columns_as_slices : bool, default = False
        Whether any additional columns should be saved as slices. (Default value = False)

    Returns
    -------
    tuple[str, pandas.DataFrame]
        (response, response_data_frame) - Returns the response status and the dataframe containing the parsed response
        text.

    """

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    data_frame = df.copy()

    required_columns = ['InstallationName', 'InstallationCode', 'Address', 'Country', 'Suburb', 'State', 'StateName',
                        'FloorAreaM2', 'ZipPostCode']
    optional_columns = ['Latitude', 'Longitude', 'Timezone', 'InstallationId']
    proposed_columns = data_frame.columns.tolist()

    if not set(required_columns).issubset(proposed_columns):
        logger.exception('Missing required column(s): %s', set(required_columns).difference(proposed_columns))
        return 'Integration.upsert_sites() - data_frame must contain the following columns: ' + ', '.join(
            required_columns) + '. Optional Columns include: ' + ', '.join(optional_columns)

    if tag_columns is not None and not set(tag_columns).issubset(data_frame.columns):
        logger.exception('Missing expected tag column(s): %s', set(tag_columns).difference(proposed_columns))
        return 'Integration.upsert_sites(): data_frame must contain the following tag columns: ' + ', '.join(
            tag_columns)
    elif tag_columns is None:
        tag_columns = []

    slice_columns = set(proposed_columns).difference(set(required_columns + optional_columns)) - set(tag_columns)
    slices_data_frame = pandas.DataFrame()

    if len(slice_columns) > 0 or len(tag_columns) > 0:
        def update_values(row, mode):
            if mode == 'A':
                j_row = row[slice_columns].to_json()
                return str(j_row)
            else:
                j_row = row[tag_columns].to_json()
                return str(j_row)

        data_frame['Slices'] = data_frame.apply(update_values, args=('A',), axis=1)
        data_frame['TagsJson'] = data_frame.apply(update_values, args=('B',), axis=1)

        data_frame = data_frame.drop(columns=slice_columns)
        slices_data_frame = data_frame[['InstallationCode', 'Slices']]

    headers = api_inputs.api_headers.integration

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/installations/upsert-ingestion"
    logger.info("Sending request: POST %s", url)

    response = requests.post(url, data=data_frame.to_json(orient='records'), headers=headers)

    response_data_frame = pandas.read_json(response.text)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()

    if save_additional_columns_as_slices and slices_data_frame.shape[0] > 0:
        slices_merged = pandas.merge(left=response_data_frame, right=slices_data_frame, left_on='installationCode',
                                     right_on='InstallationCode')
        slices_data_frame = slices_merged[['installationId', 'Slices']]
        slices_data_frame = slices_data_frame.rename(columns={'installationId': 'InstallationId'})
        upsert_data(slices_data_frame, api_inputs=api_inputs, key_columns=['InstallationId'],
                    table_name='InstallationSlices', is_slices_table=True)

    response_data_frame.columns = _column_name_cap(columns=response_data_frame.columns)

    count_entities = response_data_frame.apply(
        lambda row: 'Created' if (row['IsInserted'] == True and row['IsUpdated'] == False) else (
            'Updated' if row['IsInserted'] == False and row['IsUpdated'] == True else 'Failed'), axis=1).isin(
        ['Created', 'Updated']).sum()

    _upsert_entities_affected_count(api_inputs=api_inputs, entities_affected_count=count_entities)
    _adx_support(api_inputs=api_inputs, payload_type='Sites')

    logger.info("Ingestion complete. ")

    return response_status, response_data_frame


@_with_func_attrs(df_required_columns=['WorkOrderId', 'InstallationId', 'WorkOrderSiteIdentifier', 'Status',
                                       'RawStatus', 'Priority', 'RawPriority', 'WorkOrderCategory',
                                       'RawWorkOrderCategory', 'Type', 'Description', 'CreatedDate',
                                       'LastModifiedDate', 'WorkStartedDate', 'WorkCompletedDate', 'ClosedDate'],
                  df_optional_columns=['SubType', 'Vendor', 'VendorId', 'EquipmentClass', 'RawEquipmentClass',
                                       'EquipmentLabel', 'RawEquipmentId', 'TenantId', 'TenantName', 'NotToExceedCost',
                                       'TotalCost', 'BillableCost', 'NonBillableCost', 'Location', 'RawLocation',
                                       'ScheduledStartDate', 'ScheduledCompletionDate'])
def upsert_workorders(df: pandas.DataFrame, api_inputs: ApiInputs, save_additional_columns_as_slices: bool = False):
    """Upsert data to the Workorder table.

    The following columns are required to be present in the df:

    - ``WorkOrderId``: unique identifier for the work order instance
    - ``InstallationId``: the InstallationId (guid) used to uniquely identify a given site within the Switch platform
    - ``WorkOrderSiteIdentifier``: the work order provider's raw/native site identifier field
    - ``Status``: the status mapped to the Switch standard values defined by literal: `WORK_ORDER_STATUS`
    - ``RawStatus``: the work order provider's raw/native status
    - ``Priority``: the priority mapped to the Switch standard values defined by literal: `WORK_ORDER_PRIORITY`
    - ``RawPriority``: the work order provider's raw/native priority
    - ``WorkOrderCategory``: the category mapped to the Switch standard values defined by literal: `WORK_ORDER_CATEGORY`
    - ``RawWorkOrderCategory``: the work order provider's raw/native category
    - ``Type`` - work order type (as defined by provider) - e.g. HVAC - Too Hot, etc.
    - ``Description``: description of the work order.
    - ``CreatedDate``: the date the work order was created (Submitted status)
    - ``LastModifiedDate``: datetime the workorder was last modified
    - ``WorkStartedDate``: datetime work started on the work order (In Progress status)
    - ``WorkCompletedDate``: datetime work was completed for the work order (Resolved status)
    - ``ClosedDate``: datetime the workorder was closed (Closed status)

    The following columns are optional:

    - ``SubType``: the sub-type of the work order
    - ``Vendor``: the name of the vendor
    - ``VendorId``: the vendor id
    - ``EquipmentClass``: the Switch defined Equipment Class mapped from the work order provider's definition
    - ``RawEquipmentClass``: the work order provider's raw/native equipment class
    - ``EquipmentLabel``: the EquipmentLabel as defined within the Switch platform
    - ``RawEquipmentId``: the work order provider's raw/native equipment identifier/label
    - ``TenantId``: the tenant id
    - ``TenantName``: the name of the tenant
    - ``NotToExceedCost``: the cost not to be exceeded for the given work order
    - ``TotalCost``: total cost of the work order
    - ``BillableCost``: the billable portion of the work order cost
    - ``NonBillableCost``: the non-billable portion of the work order cost.
    - ``Location``: the Location as defined within the Switch platform
    - ``RawLocation``: the work order provider's raw/native location definition
    - ``ScheduledStartDate``: datetime work was scheduled to start on the given work order
    - ``ScheduledCompletionDate``" datetime work was scheduled to be completed for the given work order


    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe containing the work order data to be upserted.
    api_inputs: ApiInputs
        Object returned by initialize() function.
    save_additional_columns_as_slices : bool, default = False
         (Default value = False)

    Returns
    -------

    """

    data_frame = df.copy()

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    required_columns = ['WorkOrderId', 'InstallationId', 'WorkOrderSiteIdentifier', 'Status',
                        'RawStatus', 'Priority', 'RawPriority', 'WorkOrderCategory', 'RawWorkOrderCategory', 'Type',
                        'Description', 'CreatedDate', 'LastModifiedDate', 'WorkStartedDate', 'WorkCompletedDate',
                        'ClosedDate']
    optional_columns = ['SubType', 'Vendor', 'VendorId', 'EquipmentClass', 'RawEquipmentClass', 'EquipmentLabel',
                        'RawEquipmentId', 'TenantId', 'TenantName', 'NotToExceedCost', 'TotalCost', 'BillableCost',
                        'NonBillableCost', 'Location', 'RawLocation', 'ScheduledStartDate', 'ScheduledCompletionDate']

    req_cols = ', '.join(required_columns)
    proposed_columns = data_frame.columns.tolist()

    if not set(required_columns).issubset(proposed_columns):
        logger.exception('Missing required column(s): %s', set(required_columns).difference(proposed_columns))
        return 'Integration.upsert_workorder() - data_frame must contain the following columns: ' + req_cols

    try:
        _work_order_schema.validate(data_frame, lazy=True)
    except pandera.errors.SchemaErrors as err:
        logger.error('Errors present with columns in df provided.')
        logger.error(err.failure_cases)
        schema_error = err.failure_cases
        return schema_error

    slice_columns = set(proposed_columns).difference(set(required_columns + optional_columns))

    missing_optional_columns = set(optional_columns) - set(proposed_columns)
    for missing_column in missing_optional_columns:
        data_frame[missing_column] = ''

    if len(slice_columns) > 0 and save_additional_columns_as_slices is True:
        def update_values(row):
            j_row = row[slice_columns].to_json()
            return str(j_row)

        data_frame['Meta'] = data_frame.apply(update_values, axis=1)
        data_frame = data_frame.drop(columns=slice_columns)
    elif len(slice_columns) > 0 and save_additional_columns_as_slices is not True:
        data_frame = data_frame.drop(columns=slice_columns)
        data_frame['Meta'] = ''
    else:
        data_frame['Meta'] = ''

    # payload = {}
    headers = api_inputs.api_headers.integration

    logger.info("Upserting data to Workorders.")

    data_frame = data_frame.loc[:, ['WorkOrderId', 'InstallationId', 'WorkOrderSiteIdentifier', 'Status', 'Priority',
                                    'WorkOrderCategory', 'Type', 'Description', 'CreatedDate', 'LastModifiedDate',
                                    'WorkStartedDate', 'WorkCompletedDate', 'ClosedDate', 'RawPriority',
                                    'RawWorkOrderCategory', 'RawStatus', 'SubType', 'Vendor', 'VendorId',
                                    'EquipmentClass', 'RawEquipmentClass', 'EquipmentLabel', 'RawEquipmentId',
                                    'TenantId', 'TenantName', 'NotToExceedCost', 'TotalCost', 'BillableCost',
                                    'NonBillableCost', 'Location', 'RawLocation', 'ScheduledStartDate',
                                    'ScheduledCompletionDate', 'Meta']]

    upload_result = Blob.upload(api_inputs=api_inputs, data_frame=data_frame, name='WorkOrder')
    json_payload = {"path": upload_result[0], "fileCount": upload_result[1], "operation": "append",
                    "tableDef": _get_structure(data_frame),
                    "keyColumns": ["WorkOrderId"]
                    }

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/adx/work-order-operation"
    logger.info("Sending request: POST %s", url)

    logger.info("Sending request to ingest %s files from %s", str(upload_result[1]), upload_result[0])
    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()
    elif response.status_code == 200:
        _upsert_entities_affected_count(api_inputs=api_inputs, entities_affected_count=data_frame.shape[0])

    response_df = pandas.read_json(response.text, typ='series').to_frame().T
    response_df.columns = _column_name_cap(columns=response_df.columns)

    logger.info("Response status: %s", response_status)
    logger.info("Ingestion complete. ")

    return response_status, response_df


@_with_func_attrs(df_required_columns=['ObjectPropertyId', 'InstallationId', 'Timestamp', 'Value'])
def upsert_timeseries_ds(df: pandas.DataFrame, api_inputs: ApiInputs, is_local_time: bool = True,
                         save_additional_columns_as_slices: bool = False, data_feed_file_status_id: uuid.UUID = None):
    """Upserts to Timeseries_Ds table.

    The following columns are required to be present in the data_frame:
    - InstallationId
    - ObjectPropertyId
    - Timestamp
    - Value

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe containing the data to be appended to timeseries.
    api_inputs: ApiInputs
        Object returned by initialize() function.
    is_local_time : bool, default = True
         Whether the datetime values are in local time or UTC. If false, then UTC (Default value = True).
    save_additional_columns_as_slices : bool, default = False
         (Default value = False)
    data_feed_file_status_id : uuid.UUID, default = None
         Enables developer to identify upserted rows using during development. This data is posted to the
         DataFeedFileStatusId in the Timeseries_Ds table.

         Once deployed, the DataFeedFileStatusId field will contain a unique Guid which will assist in
         tracking upload results and logging.

    Returns
    -------
    tuple[str, pandas.DataFrame]
        (response_status, response_df) - Returns the response status and the dataframe containing the parsed response
        text.

    """

    data_frame = df.copy()

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    required_columns = ['ObjectPropertyId', 'InstallationId', 'Timestamp', 'Value']
    req_cols = ', '.join(required_columns)
    proposed_columns = data_frame.columns.tolist()

    if not set(required_columns).issubset(proposed_columns):
        logger.exception('Missing required column(s): %s', set(required_columns).difference(proposed_columns))
        return 'integration.upsert_timeseries_ds() - data_frame must contain the following columns: ' + req_cols

    slice_columns = set(proposed_columns).difference(set(required_columns))

    if len(slice_columns) > 0 and save_additional_columns_as_slices is True:
        def update_values(row):
            j_row = row[slice_columns].to_json()
            return str(j_row)

        # data_frame['Meta'] = data_frame.apply(update_values, axis=1)
        data_frame['Meta'] = data_frame[slice_columns].assign(
            **data_frame[slice_columns].select_dtypes(['datetime', 'object']).astype(str)).apply(update_values, axis=1)

        data_frame = data_frame.drop(columns=slice_columns)
    elif len(slice_columns) > 0 and save_additional_columns_as_slices is not True:
        data_frame = data_frame.drop(columns=slice_columns)
        data_frame['Meta'] = ''
    else:
        data_frame['Meta'] = ''

    if api_inputs.data_feed_file_status_id is not None and api_inputs.data_feed_file_status_id != '00000000-0000-0000' \
                                                                                                  '-0000-000000000000':
        data_frame['DataFeedFileStatusId'] = api_inputs.data_feed_file_status_id
    elif data_feed_file_status_id is not None:
        data_frame['DataFeedFileStatusId'] = data_feed_file_status_id
    else:
        data_frame['DataFeedFileStatusId'] = '00000000-0000-0000-0000-000000000000'

    site_list = data_frame['InstallationId'].unique().tolist()
    start_date = data_frame['Timestamp'].min(axis=0, skipna=True)
    end_date = data_frame['Timestamp'].max(axis=0, skipna=True)

    timezones = _timezone_offsets(api_inputs=api_inputs, date_from=start_date.date(), date_to=end_date.date(),
                                  installation_id_list=site_list)
    timezones['dateFrom'] = timezones['dateFrom'].apply(lambda x: pandas.to_datetime(x))
    timezones['dateTo'] = timezones['dateTo'].apply(lambda x: pandas.to_datetime(x))

    data_frame = data_frame.merge(timezones, left_on='InstallationId', right_on='installationId', how='inner')

    def in_range(row):
        j_row = (row['Timestamp'] >= row['dateFrom']) & (
            row['Timestamp'] < (row['dateTo'] + datetime.timedelta(days=1)))
        return str(j_row)

    data_frame['InDateRange'] = data_frame.apply(in_range, axis=1)
    data_frame = data_frame[data_frame['InDateRange'] == 'True']

    if is_local_time:
        def to_utc(row):
            if row['offsetToUtcMinutes'] >= 0:
                j_row = row['TimestampLocal'] - datetime.timedelta(minutes=row['offsetToUtcMinutes'])
            else:
                j_row = row['TimestampLocal'] + datetime.timedelta(minutes=abs(row['offsetToUtcMinutes']))
            return j_row

        data_frame = data_frame.assign(TimestampLocal=data_frame['Timestamp'])
        data_frame['Timestamp'] = data_frame.apply(to_utc, axis=1)
    elif not is_local_time:
        def from_utc(row):
            if row['offsetToUtcMinutes'] >= 0:
                j_row = row['Timestamp'] + datetime.timedelta(minutes=row['offsetToUtcMinutes'])
            else:
                j_row = row['Timestamp'] - datetime.timedelta(minutes=abs(row['offsetToUtcMinutes']))
            return j_row

        data_frame['TimestampLocal'] = data_frame.apply(from_utc, axis=1)

    def bin_to_15_minute_interval(row, date_col):
        if row[date_col].minute < 15:
            j_row = row[date_col].replace(minute=0)
            return j_row
        elif row[date_col].minute >= 15 and row[date_col].minute < 30:
            j_row = row[date_col].replace(minute=15)
            return j_row
        elif row[date_col].minute >= 30 and row[date_col].minute < 45:
            j_row = row[date_col].replace(minute=30)
            return j_row
        else:
            j_row = row[date_col].replace(minute=45)
            return j_row

    data_frame['TimestampId'] = data_frame.apply(bin_to_15_minute_interval, args=('Timestamp',), axis=1)
    data_frame['TimestampLocalId'] = data_frame.apply(bin_to_15_minute_interval, args=('TimestampLocal',), axis=1)
    data_frame = data_frame.drop(columns=['InDateRange', 'dateFrom', 'dateTo', 'installationId', 'offsetToUtcMinutes'])

    # payload = {}
    headers = api_inputs.api_headers.integration

    logger.info("Upserting data to Timeseries_Ds.")

    data_frame = data_frame.loc[:, ['ObjectPropertyId', 'Timestamp', 'TimestampId', 'TimestampLocal',
                                    'TimestampLocalId', 'Value', 'DataFeedFileStatusId', 'InstallationId', 'Meta']]
    name = 'Timeseries_Ds'

    upload_result = Blob.upload(api_inputs=api_inputs, data_frame=data_frame, name=name, batch_id=data_feed_file_status_id)

    json_payload = {"path": upload_result[0], "fileCount": upload_result[1], "operation": "upsert",
                    "isLocalTime": is_local_time,
                    "tableDef": _get_structure(data_frame),
                    "keyColumns": ["ObjectPropertyId", "Timestamp"]
                    }

    # {'ObjectPropertyId': 'object', 'Timestamp': 'datetime64[ns]', 'Value': 'float64', 'InstallationId': 'object'}

    # ObjectPropertyId: string, Timestamp: datetime, TimestampId: datetime, TimestampLocal: datetime,
    # TimestampLocalId: datetime, Value: real, DataFeedFileStatusId: string, InstallationId: string, Meta: dynamic

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/adx/time-series-operation?originalName=" \
          f"{name}"
    logger.info("Sending request: POST %s", url)

    logger.info("Sending request to ingest %s files from %s", str(upload_result[1]), upload_result[0])
    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()
    elif response.status_code == 200:
        _upsert_entities_affected_count(api_inputs=api_inputs, entities_affected_count=data_frame.shape[0])

    response_df = pandas.read_json(response.text, typ='series').to_frame().T
    response_df.columns = _column_name_cap(columns=response_df.columns)

    logger.info("Response status: %s", response_status)
    logger.info("Ingestion complete. ")
    return response_status, response_df


@_with_func_attrs(df_required_columns=['ObjectPropertyId', 'InstallationId', 'Timestamp', 'Value'])
def upsert_timeseries(df: pandas.DataFrame, api_inputs: ApiInputs, is_local_time: bool = True,
                      save_additional_columns_as_slices: bool = False, data_feed_file_status_id: uuid.UUID = None, 
                      is_specific_timezone: Union[bool, str] = False):
    """Upserts timeseries to EventHub for processing.

    The following columns are required to be present in the data_frame:
    - InstallationId
    - ObjectPropertyId
    - Timestamp
    - Value

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe containing the data to be appended to timeseries.
    api_inputs: ApiInputs
        Object returned by initialize() function.
    is_local_time : bool, default = True
         Whether the datetime values are in local time or UTC. If, False and is_specific_timezone is False, then UTC (Default value = True).
         Should be set to False when 'is_specific_timezone' has value.
    save_additional_columns_as_slices : bool, default = False
         (Default value = False)
    data_feed_file_status_id : uuid.UUID, default = None
         Enables developer to identify upserted rows using during development. This data is posted to the
         DataFeedFileStatusId in the Timeseries_Ds table.

         Once deployed, the DataFeedFileStatusId field will contain a unique Guid which will assist in
         tracking upload results and logging.
    is_specific_timezone : Union[False, str]
        Accepts a timezone name as the specific timezone used by the source data. Defaults to False.
        Cannot have value if 'is_local_time' is set to True.
        Retrieve list of timezones using 'sw.integration.get_timezones()'

    Returns
    -------
    tuple[str, pandas.DataFrame]
        (response_status, response_df) - Returns the response status and the dataframe containing the parsed response
        text.

    """

    data_frame = df.copy()
    timezones_df = pd.DataFrame()
    logger.info(f'Data frame size: {convert_bytes(data_frame.memory_usage(deep=True).sum())}')

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if not isinstance(is_specific_timezone, str) and not isinstance(is_specific_timezone, bool):
        logger.error("'is_specific_timezone' parameter can only be of type str or bool.")
        return pandas.DataFrame()

    if is_specific_timezone != False and is_local_time == True:
        logger.error("Assigning specific timezone is only possible if 'is_local_time' is set to False.")
        return pandas.DataFrame()

    if is_specific_timezone == True:
        logger.error("'is_specific_timezone' parameter value, if not False, should be a valid timezone. Retrieve list of timezones using 'sw.integration.get_timezones()")
        return pandas.DataFrame()

    if is_specific_timezone == '':
        logger.error("'is_specific_timezone' cannot be an empty string. Retrieve list of timezones using 'sw.integration.get_timezones()")
        return pandas.DataFrame()

    is_specific_timezone_conversion = False
    if is_specific_timezone != False and (isinstance(is_specific_timezone, str) and is_specific_timezone != ''):
        timezone_name_df = get_timezones(api_inputs=api_inputs)

        if timezone_name_df is None or timezone_name_df.__len__() == 0:
            logger.error("Failed to retrieve the allowed Timezone names.")
            return pandas.DataFrame()
        
        if not is_specific_timezone in timezone_name_df.TimezoneName.values:
            logger.error(f"'is_specific_timezone' parameter value '{is_specific_timezone}' is not found in Timezone Names list.")
            logger.info(f"'Timezone name list can be retrieved using 'sw.integration.get_timezones()' method.")
            return pandas.DataFrame()
        
        is_specific_timezone_conversion = True

    required_columns = ['ObjectPropertyId', 'InstallationId', 'Timestamp', 'Value']
    req_cols = ', '.join(required_columns)
    proposed_columns = data_frame.columns.tolist()

    if not set(required_columns).issubset(proposed_columns):
        logger.exception('Missing required column(s): %s', set(required_columns).difference(proposed_columns))
        return 'integration.upsert_timeseries() - data_frame must contain the following columns: ' + req_cols

    if not pandas.api.types.is_datetime64_ns_dtype(data_frame['Timestamp']):
        logger.exception("Timestamp series value is not of type: datetime64[ns] dtype.")
        return "Timestamp series value is not of type: datetime64[ns] dtype."

    null_count_timestamp = data_frame['Timestamp'].isna().sum()
    if null_count_timestamp > 0:
        logger.warning(f"There are {null_count_timestamp} records with a null or empty Timestamp value. " \
            f"These are being dropped resulting in {data_frame.shape[0] - null_count_timestamp} records will be upserted.")
        data_frame = data_frame.dropna(subset=['Timestamp'])

    slice_columns = set(proposed_columns).difference(set(required_columns))

    if len(list(slice_columns)) > 0 and save_additional_columns_as_slices is True:
        def update_values(row):
            j_row = row[list(slice_columns)].to_json()
            return str(j_row)

        logger.info('Creating Meta Column.')
        data_frame['Meta'] = data_frame[list(slice_columns)].assign(
            **data_frame[list(slice_columns)].select_dtypes(['datetime', 'object']).astype(str)).apply(update_values, axis=1)

        data_frame = data_frame.drop(columns=list(slice_columns))
    elif len(list(slice_columns)) > 0 and save_additional_columns_as_slices is not True:
        data_frame = data_frame.drop(columns=list(slice_columns))
        data_frame['Meta'] = ''
    else:
        data_frame['Meta'] = ''

    if api_inputs.data_feed_file_status_id is not None and \
            api_inputs.data_feed_file_status_id != '00000000-0000-0000-0000-000000000000' and \
            api_inputs.data_feed_file_status_id != '':
        data_frame['DataFeedFileStatusId'] = api_inputs.data_feed_file_status_id
        data_feed_file_status_id = api_inputs.data_feed_file_status_id
    elif data_feed_file_status_id is not None and \
            data_feed_file_status_id != '00000000-0000-0000-0000-000000000000' and \
            data_feed_file_status_id != '':
        data_frame['DataFeedFileStatusId'] = data_feed_file_status_id
    else:
        data_feed_file_status_id = uuid.uuid4()
        data_frame['DataFeedFileStatusId'] = data_feed_file_status_id

    
    start_date = data_frame['Timestamp'].min(axis=0, skipna=True)
    end_date = data_frame['Timestamp'].max(axis=0, skipna=True)

    specific_timezone_df = pd.DataFrame()

    def convert_dst_interval_dates(row):
        row['start'] = pd.to_datetime(row['start'])
        row['end'] = pd.to_datetime(row['end'])
        row['offsetToUtcMinutes'] = row['standardOffsetUtc'] + row['dstOffsetUtc']
        return row

    if is_specific_timezone_conversion:
        def timezone_to_utc(row):
            if row['offsetToUtcMinutes'] >= 0:
                j_row = row['Timestamp'] - datetime.timedelta(minutes=row['offsetToUtcMinutes'])
            else:
                j_row = row['Timestamp'] + datetime.timedelta(minutes=abs(row['offsetToUtcMinutes']))
            return j_row

        specific_timezone_df = _timezone_dst_offsets(api_inputs=api_inputs, date_from=start_date.date(), date_to=end_date.date(), timezone_name=is_specific_timezone)

        if specific_timezone_df.empty:
            logger.exception('Failed to retrieve the specific timezone offsets.')
            return 'Failed to retrieve the specific timezone offsets.'

        specific_timezone_df = specific_timezone_df.apply(convert_dst_interval_dates, axis=1)
        specific_timezone_df = specific_timezone_df.drop(columns=['timezoneId', 'standardOffsetUtc', 'dstOffsetUtc'])
        
        data_frame['year'] = pd.DatetimeIndex(data_frame['Timestamp']).year
        data_frame = data_frame.merge(specific_timezone_df, left_on='year', right_on='year', how='inner')

        del specific_timezone_df
        gc.collect()

        data_frame = data_frame[(data_frame.Timestamp >= data_frame.start) & (data_frame.Timestamp < data_frame.end) & (data_frame.Timestamp.apply(lambda x: x.year) == data_frame.year)]
        data_frame = data_frame.drop(columns=['start', 'end', 'year'])
        
        data_frame['Timestamp'] = data_frame.apply(timezone_to_utc, axis=1)
        data_frame = data_frame.drop(columns=['offsetToUtcMinutes'])

        # Set automatically to is_local_time = False 
        is_local_time = False

    site_list = data_frame['InstallationId'].unique().tolist()
    timezones_df = _timezone_dst_offsets(api_inputs=api_inputs, date_from=start_date.date(), date_to=end_date.date(),
                                         installation_id_list=site_list)

    if timezones_df.empty:
        logger.exception('Timezone DST offsets failed to retrieve.')
        return 'Timezone DST offsets failed to retrieve.'

    timezones_df = timezones_df.apply(convert_dst_interval_dates, axis=1)

    if not is_local_time:
        def convert_dst_interval_range_to_utc(row):
            dst_start = row['start']
            dst_end = row['end']

            if row['standardOffsetUtc'] >= 0:
                dst_start = dst_start - (datetime.timedelta(minutes=row['standardOffsetUtc'])) - datetime.timedelta(minutes=row['dstOffsetUtc'])
                dst_end = dst_end - (datetime.timedelta(minutes=row['standardOffsetUtc'])) - datetime.timedelta(minutes=row['dstOffsetUtc'])
            else:
                dst_start = dst_start + (datetime.timedelta(minutes=row['standardOffsetUtc'])) + datetime.timedelta(minutes=row['dstOffsetUtc'])
                dst_end = dst_end + (datetime.timedelta(minutes=row['standardOffsetUtc'])) + datetime.timedelta(minutes=row['dstOffsetUtc'])
            row['start'] = dst_start
            row['end'] = dst_end

            return row

        timezones_df = timezones_df.apply(convert_dst_interval_range_to_utc, axis=1)
    timezones_df = timezones_df.drop(columns=['timezoneId', 'standardOffsetUtc', 'dstOffsetUtc'])

    logger.info('Merging data frame input with timezone installation dst offsets.')
    data_frame = data_frame.merge(timezones_df, left_on='InstallationId', right_on='installationId', how='inner')
    
    del timezones_df
    gc.collect()

    data_frame = data_frame[(data_frame.Timestamp >= data_frame.start) & (data_frame.Timestamp < data_frame.end) & (data_frame.Timestamp.apply(lambda x: x.year) == data_frame.year)]
    data_frame = data_frame.drop(columns=['start', 'end', 'year'])

    if is_local_time:
        def to_utc(row):
            if row['offsetToUtcMinutes'] >= 0:
                j_row = row['TimestampLocal'] - datetime.timedelta(minutes=row['offsetToUtcMinutes'])
            else:
                j_row = row['TimestampLocal'] + datetime.timedelta(minutes=abs(row['offsetToUtcMinutes']))
            return j_row

        data_frame = data_frame.assign(TimestampLocal=data_frame['Timestamp'])
        data_frame['Timestamp'] = data_frame.apply(to_utc, axis=1)

    elif not is_local_time:
        def from_utc(row):
            if row['offsetToUtcMinutes'] >= 0:
                j_row = row['Timestamp'] + datetime.timedelta(minutes=row['offsetToUtcMinutes'])
            else:
                j_row = row['Timestamp'] - datetime.timedelta(minutes=abs(row['offsetToUtcMinutes']))
            return j_row
        data_frame['TimestampLocal'] = data_frame.apply(from_utc, axis=1)

    def bin_to_15_minute_interval(row, date_col):
        if row[date_col].minute < 15:
            j_row = row[date_col].replace(minute=0)
            return j_row
        elif row[date_col].minute >= 15 and row[date_col].minute < 30:
            j_row = row[date_col].replace(minute=15)
            return j_row
        elif row[date_col].minute >= 30 and row[date_col].minute < 45:
            j_row = row[date_col].replace(minute=30)
            return j_row
        else:
            j_row = row[date_col].replace(minute=45)
            return j_row

    logger.info('Date time conversion and formatting.')
    data_frame['TimestampId'] = data_frame.apply(bin_to_15_minute_interval, args=('Timestamp',), axis=1)
    data_frame['TimestampLocalId'] = data_frame.apply(bin_to_15_minute_interval, args=('TimestampLocal',), axis=1)

    timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
    timestamp_normalized_format = "%Y-%m-%dT%H:%M:00Z"
    data_frame['Timestamp'] = data_frame['Timestamp'].dt.strftime(timestamp_format)
    data_frame['TimestampLocal'] = data_frame['TimestampLocal'].dt.strftime(timestamp_format)
    data_frame['TimestampId'] = data_frame['TimestampId'].dt.strftime(timestamp_normalized_format)
    data_frame['TimestampLocalId'] = data_frame['TimestampLocalId'].dt.strftime(timestamp_normalized_format)

    headers = api_inputs.api_headers.integration

    logger.info("Upserting data to Timeseries.")
    data_frame = data_frame.loc[:, ['ObjectPropertyId', 'Timestamp', 'TimestampId', 'TimestampLocal',
                                    'TimestampLocalId', 'Value', 'DataFeedFileStatusId', 'InstallationId', 'Meta']]

    container = 'data-ingestion-timeseries-adx'
    folder = 'to-eventhub'
    name = 'Timeseries'
    
    logger.info(f'Data frame size: {convert_bytes(data_frame.memory_usage(deep=True).sum())}')
    upload_result = Blob.upload(api_inputs=api_inputs, data_frame=data_frame, container=container, folder=folder, name=name, batch_id=data_feed_file_status_id, include_header=True)

    json_payload = {"path": upload_result[0], "fileCount": upload_result[1]}

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/timeseries"
    logger.info("Sending request: POST %s", url)

    logger.info("Sending request to ingest %s files from %s", str(upload_result[1]), upload_result[0])

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()
    elif response.status_code == 200:
        _upsert_entities_affected_count(api_inputs=api_inputs, entities_affected_count=data_frame.shape[0])

    response_df = pandas.read_json(response.text, typ='series').to_frame().T
    response_df.columns = _column_name_cap(columns=response_df.columns)

    logger.info("Response status: %s", response_status)
    logger.info("Ingestion complete. ")
    return response_status, response_df


def upsert_data(data_frame, api_inputs: ApiInputs, table_name: str, key_columns: list,
                is_slices_table=False):
    """Upsert data

    Upserts data to the `table_name` provided to the function call and uses the `key_columns` provided to determine the
    unique records.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        Dataframe containing the data to be upserted.
    api_inputs : ApiInputs
        Object returned by initialize() function.
    table_name : str
        The name of the table where data will be upserted.
    key_columns : list
        The columns that determine a unique instance of a record. These are used to update records if new data is
        provided.
    is_slices_table : bool
         (Default value = False)

    Returns
    -------
    tuple[str, pandas.DataFrame]
        (response_status, response_df) - Returns the response status and the dataframe containing the parsed response
        text.

    """
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    headers = api_inputs.api_headers.integration

    if len(key_columns) == 0 or key_columns is None:
        logger.error(
            "You must provide key_columns. This allows the Switch Automation Platform to identify the rows to update.")
        return False

    logger.info("Data is being upserted for %s", table_name)

    table_structure = _get_structure(data_frame)
    if is_slices_table is True and 'Slices' in table_structure:
        table_structure['Slices'] = 'dynamic'

    # upload Blobs to folder
    upload_result = Blob.upload(api_inputs=api_inputs, data_frame=data_frame, name=table_name)
    json_payload = {"path": upload_result[0], "fileCount": upload_result[1], "operation": "upsert",
                    "tableDef": table_structure, "keyColumns": key_columns}

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/adx/data-operation?tableName={table_name}"
    logger.info("Sending request: POST %s", url)

    logger.info("Sending request to ingest %s files from %s", str(upload_result[1]), upload_result[0])

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()
    elif response.status_code == 200:
        _upsert_entities_affected_count(api_inputs=api_inputs, entities_affected_count=data_frame.shape[0])

    response_df = pandas.read_json(response.text, typ='series').to_frame().T
    response_df.columns = _column_name_cap(columns=response_df.columns)

    logger.info("Response status: %s", response_status)
    logger.info("Ingestion complete. ")

    return response_status, response_df


def replace_data(data_frame, api_inputs: ApiInputs, table_name: str):
    """Replace data

    Replaces the data in the ``table_name`` provided to the function call.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        Data frame to be used to replace the data in the `table_name` table.
    api_inputs : ApiInputs
        Object returned by initialize() function.
    table_name :
        The name of the table where data will be replaced.

    Returns
    -------
    tuple[str, pandas.DataFrame]
        (response_status, response_df) - Returns the response status and the dataframe containing the parsed response
        text.

    """
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    headers = api_inputs.api_headers.integration

    logger.info("Replacing all data for %s", table_name)

    # upload Blobs to folder
    upload_result = Blob.upload(api_inputs=api_inputs, data_frame=data_frame, name=table_name)
    json_payload = {"path": upload_result[0], "fileCount": upload_result[1], "operation": "replace",
                    "tableDef": _get_structure(data_frame)}
    logger.info(json_payload)

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/adx/data-operation?tableName={table_name}"
    logger.info("Sending request: POST %s", url)

    logger.info("Sending request to ingest %s files from %s", str(upload_result[1]), upload_result[0])

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, pandas.DataFrame()
    elif response.status_code == 200:
        _upsert_entities_affected_count(api_inputs=api_inputs, entities_affected_count=data_frame.shape[0])

    response_df = pandas.read_json(response.text, typ='series').to_frame().T
    response_df.columns = _column_name_cap(columns=response_df.columns)

    logger.info("Ingestion complete. ")

    return response_status, response_df


def append_data(data_frame, api_inputs: ApiInputs, table_name: str):
    """Append data.

    Appends data to the ``table_name`` provided to the function call.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        Data to be appended.
    api_inputs : ApiInputs
        Object returned by initialize() function.
    table_name : str
        The name of the table where data will be appended.

    Returns
    -------
    tuple[str, pandas.DataFrame]
        (response_status, response_df) - Returns the response status and the dataframe containing the parsed response
        text.

    """
    # payload = {}
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    # payload = {}
    headers = api_inputs.api_headers.integration

    logger.info("Appending data for %s", table_name)

    # upload Blobs to folder
    upload_result = Blob.upload(api_inputs=api_inputs, data_frame=data_frame, name=table_name)
    json_payload = {"path": upload_result[0], "fileCount": upload_result[1], "operation": "append",
                    "tableDef": _get_structure(data_frame)}

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/adx/data-operation?tableName={table_name}"
    logger.info("Sending request: POST %s", url)
    logger.info("Sending request to ingest %s files from %s", str(upload_result[1]), upload_result[0])

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status
    elif response.status_code == 200:
        _upsert_entities_affected_count(api_inputs=api_inputs, entities_affected_count=data_frame.shape[0])

    response_df = pandas.read_json(response.text, typ='series').to_frame().T
    response_df.columns = _column_name_cap(columns=response_df.columns)

    logger.info("API Response: %s", response_status)
    logger.info("Ingestion complete. ")

    return response_status, response_df


def upsert_file_row_count(api_inputs: ApiInputs, row_count: int):
    """Updates data feed file status row count.

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    row_count : number
        Number of rows

    Returns
    -------
    str
        Response status as a string.
    """

    if row_count is None:
        row_count = 0

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if (api_inputs.data_feed_id == '00000000-0000-0000-0000-000000000000' or
            api_inputs.data_feed_file_status_id == '00000000-0000-0000-0000-000000000000'):
        logger.error("upsert_file_row_count() can only be called in Production.")
        return False

    headers = api_inputs.api_headers.default

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/" \
          f"{api_inputs.data_feed_id}/file-status/{api_inputs.data_feed_file_status_id}/row-count/{row_count}"

    response = requests.request("PUT", url, timeout=20, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status

    return response_status


def upsert_event_work_order_id(api_inputs: ApiInputs, event_task_id: uuid.UUID, integration_id: str,
                               work_order_status: str):
    """

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    event_task_id : uuid.UUID
        The value of the `work_order_input['EventTaskId']`
    integration_id : str
        The 3rd Party work order system's unique identifier for the work order
    work_order_status : str
        The status of the work order

    Returns
    -------
    (str, str)
        response_status, response.text - The response status of the call and the text from the response body.

    """

    if api_inputs.api_projects_endpoint == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return 'Error', 'You must call initialize() before using the API.'

    header = api_inputs.api_headers.default

    payload = {
        "IntegrationId": integration_id,
        "Status": work_order_status
    }

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/events/{str(event_task_id)}/work-order"

    response = requests.put(url=url, json=payload, headers=header)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, response.text

    return response_status, response.text


@_with_func_attrs(df_required_columns=['Identifier'])
def upsert_tags(api_inputs: ApiInputs, df: pandas.DataFrame, tag_level: TAG_LEVEL):
    """
    Upsert tags to Site/Device/Sensors as specified by the tag_level argument.
    
    Required fields are:
    - Identifier
    - Additional columns as TagGroups / Tags

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    df : DataFrame
        List of Devices along with corresponding TagsJson to upsert
    tag_level : TAG_LEVEL
        Level of tagging applied to the list of Identifier input.
            If tag_level is Site, Identifier should be InstallationIds.
            If tag_level is Device, Identifier should be DeviceIds.
            If tag_level is Sensor, Identifier should be ObjectPropertyIds.

    Returns
    -------
    List of affected records
    
    """
    data_frame = df.copy()

    # validate inputs
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    # validate df
    if data_frame.empty:
        logger.error("Data Frame is empty. Nothing to upsert.")
        return pandas.DataFrame()

    # validate tag level
    if not set([tag_level]).issubset(set(TAG_LEVEL.__args__)):
        logger.error('tag_level parameter must be set to one of the allowed values defined by the '
                        'TAG_LEVEL literal: %s', TAG_LEVEL.__args__)
        return pandas.DataFrame()

    required_columns = getattr(upsert_tags, 'df_required_columns')
    req_cols = ', '.join(required_columns)
    proposed_columns = data_frame.columns.tolist()

    # check if required columns are present
    if not set(required_columns).issubset(proposed_columns):
        logger.exception('Missing required column(s): %s', set(required_columns).difference(proposed_columns))
        return 'integration.upsert_tags() - data_frame must contain the following columns: ' + req_cols

    slice_columns = set(proposed_columns).difference(set(required_columns))

    if len(list(slice_columns)) > 0:
        def update_values(row):
            j_row = row[list(slice_columns)].to_json()
            return str(j_row)

        data_frame['TagsJson'] = data_frame[list(slice_columns)].assign(
            **data_frame[list(slice_columns)].select_dtypes(['datetime', 'object']).astype(str)).apply(update_values, axis=1)
        data_frame = data_frame.drop(columns=list(slice_columns))
    else:
        logger.error("Additional Columns aside from Identifier is required to set as TagsJson.")
        return pandas.DataFrame()

    switcher_tag_level_identifier = {
        'Site': 'InstallationId',
        'Device': 'DeviceId',
        'Sensor': 'ObjectPropertyId'
    }

    tag_level_identifier_id = switcher_tag_level_identifier.get(tag_level)

    data_frame.rename(columns = {'Identifier':tag_level_identifier_id}, inplace = True)

    # action request
    headers = api_inputs.api_headers.integration

    switcher_tag_level_uri = {
        'Site': f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/installations/upsert-ingestion-tags",
        'Device': f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/devices/upsert-ingestion-tags",
        'Sensor': f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/sensors/upsert-ingestion-tags",
    }

    url = switcher_tag_level_uri.get(tag_level)

    logger.info("Sending request: POST %s", url)
    response = requests.post(url, data=data_frame.to_json(orient='records'), headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)

    logger.info("Response status: %s", response_status)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                        response.reason)
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)

    response_df = pandas.read_json(response.text)
    response_df.columns = _column_name_cap(response_df.columns)

    return response_df


@_with_func_attrs(df_required_columns=['DeviceId'])
def upsert_device_metadata(api_inputs: ApiInputs, df: pandas.DataFrame):
    """
    Upsert metadata on created devices.

    Required fields are:
    - DeviceId
    - Additional columns as Metadata

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    df : DataFrame
        List of Devices along with corresponding MetadataJson to upsert

    Returns
    -------
    List of affected Devices
    """
    data_frame = df.copy()

    # validate inputs
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    # validate df
    if data_frame.empty:
        logger.error("Data Frame is empty. Nothing to upsert.")
        return pandas.DataFrame()

    required_columns = getattr(upsert_device_metadata, 'df_required_columns')

    req_cols = ', '.join(required_columns)
    proposed_columns = data_frame.columns.tolist()

    # check if required columns are present
    if not set(required_columns).issubset(proposed_columns):
        logger.exception('Missing required column(s): %s', set(required_columns).difference(proposed_columns))
        return 'integration.upsert_device_metadata() - data_frame must contain the following columns: ' + req_cols

    slice_columns = set(proposed_columns).difference(set(required_columns))

    if len(list(slice_columns)) > 0:
        def update_values(row):
            j_row = row[list(slice_columns)].to_json()
            return str(j_row)

        data_frame['MetadataJson'] = data_frame[list(slice_columns)].assign(
            **data_frame[list(slice_columns)].select_dtypes(['datetime', 'object']).astype(str)).apply(update_values, axis=1)
        data_frame = data_frame.drop(columns=list(slice_columns))
    else:
        logger.error("Additional Columns aside from DeviceId is required to set as MetadataJson.")
        return pandas.DataFrame()

    # action request
    headers = api_inputs.api_headers.integration

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/devices/upsert-ingestion-metadata"

    logger.info("Sending request: POST %s", url)
    response = requests.post(url, data=data_frame.to_json(orient='records'), headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)

    logger.info("Response status: %s", response_status)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                        response.reason)
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)

    response_df = pandas.read_json(response.text)
    response_df.columns = _column_name_cap(response_df.columns)

    return response_df
