# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module defining constants referenced by methods and functions defined in  other modules in the package. This module
is not directly referenced by end users.
"""
from typing import Literal
__all__ = ['api_prefix', 'argus_prefix', 'DATETIME_COL_FMT', 'DEPLOY_TYPE', 'EXPECTED_DELIVERY', 'WORK_ORDER_PRIORITY',
           'WORK_ORDER_STATUS', 'WORK_ORDER_CATEGORY', 'ERROR_TYPE', 'MAPPING_ENTITIES', 'QUEUE_NAME', 'QUERY_LANGUAGE',
           'ACCOUNT', 'PROCESS_STATUS', 'AUTH_ENDPOINT_DEV', 'AUTH_ENDPOINT_PROD', 'SCHEDULE_TIMEZONE',
           'SWITCH_ENVIRONMENT', 'INTEGRATION_SETTINGS_EDITORS', 'DATA_INGESTION_CONTAINER', 'CACHE_SCOPE', 'TAG_LEVEL']

# @deprecated suggestion: Up for deprecation as this is not used anymore in the API
# api_prefix = "http://localhost:7071/api/SwitchApi/"
api_prefix = "https://pivotstreams.azurewebsites.net/api/SwitchApi/"

# @deprecated suggestion: Up for deprecation as this is not used anymore in the API (except for automation.reserve_instance)
# argus_prefix = "http://localhost:7071/api/"
argus_prefix = "https://arguslogicv4b.azurewebsites.net/api/"

AUTH_ENDPOINT_DEV = "https://restapi-dev.switchautomation.com/auth"
AUTH_ENDPOINT_PROD = "https://restapi-us.switchautomation.com/auth"

DATETIME_COL_FMT = Literal['DateTime', 'Date', 'Time']

# ['DateTime in 1 column',
#  'Date and Time in 2 columns',
#  'Split year and month in 2 columns',
#  'Start and End Date in 2 columns']

EXPECTED_DELIVERY = Literal['5min', '15min', 'Hourly', 'Daily', 'Weekly', 'Monthly', 'Quarterly']

# deploy_type 'File' for (FTP. Email, Upload)
DEPLOY_TYPE = Literal['Email', 'Ftp', 'Upload', 'Timer']

ACCOUNT = Literal['SwitchStorage', 'SwitchContainer', 'Argus', 'DataIngestion']

DATA_INGESTION_CONTAINER = Literal['data-ingestion-adx', 'data-ingestion-timeseries-adx']

QUERY_LANGUAGE = Literal['sql', 'kql']

ERROR_TYPE = Literal['DateTime', 'MissingDevices', 'NonNumeric', 'MissingRequiredField(s)', 'MissingSite(s)',
                     'DuplicateRecords', 'MissingSensors', 'UnableToReadFile', 'InvalidFileType', 'InvalidInputSettings']

PROCESS_STATUS = Literal['ActionRequired', 'Failed']

MAPPING_ENTITIES = Literal['Installations', 'Devices/Sensors', 'Readings', 'Work Orders']

WORK_ORDER_CATEGORY = Literal['Preventative Maintenance', 'Tenant Request']

WORK_ORDER_PRIORITY = Literal['Low', 'Medium', 'High']

WORK_ORDER_STATUS = Literal['Submitted', 'Open', 'In Progress', 'Waiting for 3rd Party', 'Resolved', 'Abandoned',
                            'Closed']

QUEUE_NAME = Literal['task', 'highpriority']

SCHEDULE_TIMEZONE = Literal['Local', 'Utc']

SWITCH_ENVIRONMENT = Literal['Development', 'Staging', 'Testing', 'Production']

SUPPORT_PAYLOAD_TYPE = Literal['Sites', 'Sensors', 'Portfolio']

INTEGRATION_SETTINGS_EDITORS = Literal['text_box', 'numeric_stepper', 'custom_combo', 'tag_groups_combo',
                                       'equipment_combo']

CACHE_SCOPE = Literal['Portfolio', 'Task', 'DataFeed']
TAG_LEVEL = Literal['Site', 'Device', 'Sensor']
