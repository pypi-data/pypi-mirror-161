# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
This module contains the helper functions for error handling.

The module contains three functions:
    - invalid_file_format() which should be used to validate the source file received against the expected schema and
      post any issues identified to the data feed dashboard.

    - post_errors() which is used to post errors (apart from those identified by the invalid_file_format() function) to
      the data feed dashboard.

    - validate_datetime() which checks whether the values of the datetime column(s) of the source file are valid. Any
      datetime errors identified by this function should be passed to the post_errors() function.

The validate_datetime() function can be used to validate the datetime column(s) of the source file. The output
`df_invalid_datetime` from this function should be passed to the post_errors() function. For example,

>>> import pandas as pd
>>> import switch_api as sw
>>> api_inputs = sw.initialize(api_project_id=api_project_id) # set api_project_id to the relevant portfolio
>>> test_df = pd.DataFrame({'DateTime':['2021-06-01 00:00:00', '2021-06-01 00:15:00', '', '2021-06-01 00:45:00'],
... 'Value':[10, 20, 30, 40], 'device_id':['xyz', 'xyz', 'xyz', 'xyz']})
>>> df_invalid_datetime, df = validate_datetime(df=test_df, datetime_col=['DateTime'], dt_fmt='%Y-%m-%d %H:%M:%S')
>>> if df_invalid_datetime.shape[0] != 0:
...     sw.error_handlers.post_errors(api_inputs, df_invalid_datetime, error_type='DateTime')

"""
import pandas
import pandera
import logging
import requests
import sys
import json
from typing import Optional, List, Union
from .._utils._constants import ERROR_TYPE, PROCESS_STATUS
from .._utils._utils import ApiInputs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def invalid_file_format(api_inputs: ApiInputs, schema: pandera.DataFrameSchema, raw_df: pandas.DataFrame):
    """Validates the raw file format and posts any errors to data feed dashboard

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by call to initialize()
    schema : pandera.DataFrameSchema
        The defined data frame schema object to be used for validation.
    raw_df : pandas.DataFrame
        The raw dataframe created by reading the file.

    Returns
    -------
    response_boolean: boolean
        True or False indicating the success of the call

    """
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    headers = api_inputs.api_headers.default

    error_type = 'FileFormat'
    process_status = 'Failed'

    try:
        schema.validate(raw_df, lazy=True)
    except pandera.errors.SchemaErrors as err:
        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/" \
              f"{api_inputs.data_feed_id}/errors?status={process_status}&errorType={error_type}&statusId=" \
              f"{api_inputs.data_feed_file_status_id}"
        logger.info("Sending request: POST %s", url)
        logger.error('Schema errors present: %s', err.failure_cases)

        schema_error = err.failure_cases

        response = requests.post(url, data=schema_error.to_json(orient='records'), headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        return response.text


def post_errors(api_inputs: ApiInputs, errors: Union[pandas.DataFrame, str], error_type: ERROR_TYPE,
                process_status: PROCESS_STATUS = 'ActionRequired'):
    """Post errors to the Data Feed Dashboard

    Post dataframe containing the errors of type ``error_type`` to the Data Feed Dashboard in the Switch Platform.

    Parameters
    ----------
    api_inputs : ApiInputs
        The object returned by call to initialize() function.
    errors : Union[pandas.DataFrame, str]
        The dataframe containing the row(s) with errors or a string describing the error(s).
    error_type : ERROR_TYPE
        The type of error being posted to Data Feed Dashboard.
    process_status: PROCESS_STATUS, optional
        Set the status of the process to one of the allowed values specified by the PROCESS_STATUS literal
        (Default value = 'ActionRequired').

    Returns
    -------
    response_boolean: boolean
        True or False indicating the success of the call

    """
    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if (api_inputs.data_feed_id == '00000000-0000-0000-0000-000000000000' or
            api_inputs.data_feed_file_status_id == '00000000-0000-0000-0000-000000000000'):
        logger.error("Post Errors can only be called in Production.")
        return False

    if not set([error_type]).issubset(set(ERROR_TYPE.__args__)):
        logger.error('error_type parameter must be set to one of the allowed values defined by the '
                     'ERROR_TYPE literal: %s', ERROR_TYPE.__args__)
        return False

    if not set([process_status]).issubset(set(PROCESS_STATUS.__args__)):
        logger.error('process_status parameter must be set to one of the allowed values defined by the '
                     'PROCESS_STATUS literal: %s', PROCESS_STATUS.__args__)
        return False

    headers = api_inputs.api_headers.default

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/" \
          f"{api_inputs.data_feed_id}/errors?status={process_status}&errorType={error_type}&statusId=" \
          f"{api_inputs.data_feed_file_status_id}"
    logger.info("Sending request: POST %s", url)

    payload = ""
    if (isinstance(errors, pandas.DataFrame)):
        payload = json.dumps(json.loads(errors.to_json(orient='table'))['data'])
    elif (isinstance(errors, str)):
        payload = errors
    else:
        logger.error('errors_content parameter must be set to either a type of pandas.DataFrame or string')
        return False

    response = requests.post(url,
                             data=payload,
                             headers=headers)

    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, False
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, False

    logger.error(f'Directive:ProcessStatus={str(process_status)}')

    return response.text


def validate_datetime(df: pandas.DataFrame, datetime_col: Union[str, List[str]],
                      dt_fmt: Optional[str] = None):  # -> tuple[pandas.DataFrame, pandas.DataFrame]:
    """Check for datetime errors.

    Returns a tuple ``(df_invalid_datetime, df)``, where:
        - ``df_invalid_datetime`` is a dataframe containing the extracted rows of the input df with invalid datetime
        values.

        - ``df`` is the original dataframe input after dropping any rows with datetime errors.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe that contains the columns to be validated.
    datetime_col: List[str]
        List of column names that contain the datetime values to be validated. If passing a single column name in as a
        string, it will be coerced to a list.
    dt_fmt : Optional[str]
        The expected format of the datetime columns to be coerced. The strftime to parse time, eg "%d/%m/%Y", note
        that "%f" will parse all the way up to nanoseconds. See strftime documentation for more information on
        choices: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

    Returns
    -------
    df_invalid_datetime, df : tuple[pandas.DataFrame, pandas.DataFrame]
        (df_invalid_datetime, df) - where: `df_invalid_date

    Notes
    -----
    If the ``df_invalid_datetime`` dataframe is not empty, then the dataframe should be passed to the ``post_errors()``
    function using ``error_type = 'DateTime'``. See example code below:

    >>> import pandas as pd
    >>> import switch_api as sw
    >>> api_inputs = sw.initialize(api_project_id = api_project_id) # set api_project_id to the relevant portfolio
    >>> test_df = pd.DataFrame({'DateTime':['2021-06-01 00:00:00', '2021-06-01 00:15:00', '', '2021-06-01 00:45:00'],
    ... 'Value':[10, 20, 30, 40], 'device_id':['xyz', 'xyz', 'xyz', 'xyz']})
    >>> df_invalid_datetime, df = validate_datetime(df=test_df, datetime_col=['DateTime'], dt_fmt='%Y-%m-%d %H:%M:%S')
    >>> if df_invalid_datetime.shape[0] != 0:
    ...     sw.error_handlers.post_errors(api_inputs, df_invalid_datetime, error_type='DateTime')

    """

    if type(datetime_col) == str:
        datetime_col = [datetime_col]
    elif type(datetime_col) == list:
        datetime_col = datetime_col
    else:
        logger.error('datetime_col: Invalid format - datetime_col must be a string or list of strings.')

    val_dt_cols = []
    for i in datetime_col:
        val_dt_cols.append(i + '_dt')
    lst = [None] * len(datetime_col)

    if dt_fmt is None:
        for i in range(len(datetime_col)):
            df[val_dt_cols[i]] = pandas.to_datetime((df[datetime_col[i]]), errors='coerce')
            lst[i] = df[df[val_dt_cols[i]].isnull()]
            df = df[df[val_dt_cols[i]].notnull()]
            lst[i] = lst[i].drop(val_dt_cols[i], axis=1)
            df = df.drop(val_dt_cols[i], axis=1)
        df_invalid_datetime = pandas.concat(lst, axis=0)
        df[datetime_col] = df[datetime_col].apply(lambda x: pandas.to_datetime(x))
        logger.info('Row count with invalid datetime values: %s', df_invalid_datetime.shape[0])
        logger.info('Row count with valid datetime values: %s', df.shape[0])
        return df_invalid_datetime, df
    else:
        for i in range(len(datetime_col)):
            df[val_dt_cols[i]] = pandas.to_datetime((df[datetime_col[i]]), errors='coerce', format=dt_fmt)
            lst[i] = df[df[val_dt_cols[i]].isnull()]
            df = df[df[val_dt_cols[i]].notnull()]
            lst[i] = lst[i].drop(val_dt_cols[i], axis=1)
            df = df.drop(val_dt_cols[i], axis=1)
        df_invalid_datetime = pandas.concat(lst, axis=0)
        df[datetime_col] = df[datetime_col].apply(lambda x: pandas.to_datetime(x, format=dt_fmt))
        logger.info('Row count with invalid datetime values: %s', df_invalid_datetime.shape[0])
        logger.info('Row count with valid datetime values: %s', df.shape[0])
        return df_invalid_datetime, df
