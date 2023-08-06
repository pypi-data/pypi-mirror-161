# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for .....
"""
# import datetime
import re
import uuid
from collections import namedtuple
from typing import Union, List
import string
import secrets
import pandas
import pandera
import logging
import sys
import requests
from requests.adapters import HTTPAdapter

from requests.sessions import session
from urllib3.util.retry import Retry
from .._utils._constants import WORK_ORDER_STATUS, WORK_ORDER_CATEGORY, WORK_ORDER_PRIORITY

__all__ = ['generate_password', 'convert_to_sqm', 'convert_to_pascal_case', 'ValidatedSetterProperty', 'ApiInputs',
           'DiscoveryIntegrationInput', 'DataFeedFileProcessOutput', 'requests_retry_session', 'is_valid_uuid', 'convert_bytes']

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


class ValidatedSetterProperty:
    def __init__(self, func, name=None, doc=None):
        self.func = func
        self.__name__ = name if name is not None else func.__name__
        self.__doc__ = doc if doc is not None else func.__doc__

    def __set__(self, obj, value):
        ret = self.func(obj, value)
        obj.__dict__[self.__name__] = value


def _column_name_cap(columns) -> list:
    renamed_columns = [name[0].upper() + name[1:] for name in columns.to_list()]
    return renamed_columns


def _with_func_attrs(**attrs):
    def with_attrs(f):
        for k, v in attrs.items():
            setattr(f, k, v)
        return f

    return with_attrs


def _is_valid_regex(regex):
    """Check if regex is valid.

    Parameters
    ----------
    regex : str
        A `regex` expression to be validated.

    Returns
    -------
    bool
        Valid if True, invalid if False.

    """
    try:
        re.compile(regex)
        return True
    except re.error:
        return False


ApiHeaders = namedtuple('ApiHeaders', ['default', 'integration'])

ApiInputs = namedtuple('ApiInputs',
                       ['email_address', 'user_id', 'api_project_id', 'data_feed_id', 'data_feed_file_status_id',
                        'bearer_token', 'api_base_url', 'api_projects_endpoint', 'subscription_key', 'api_headers'])

DiscoveryIntegrationInput = namedtuple(
    'DiscoveryIntegrationInput',
    ['api_project_id', 'installation_id', 'network_device_id', 'integration_device_id', 'user_id', 'batch_no', 'job_id'])
# DiscoveryIntegrationInput.__doc__ = """DiscoveryIntegrationInput(api_project_id, installation_id, network_device_id, integration_device_id, user_id, batch_no)
#
# Defines the required inputs to be provided to the run_discovery() method's integration_input parameter.
#
# Parameters
# ----------
# api_project_id : the unique identifier for the portfolio (ApiProjectID)
# installation_id : the unique identifier for the given site (InstallationID)
# network_device_id : the DeviceSpecs.NetworkDeviceID for the given integration_device_id
# integration_device_id : the unique identifier for the integration device the discovery is triggered against
# user_id : the unique identifier of the user who triggered the discovery
# batch_no : the unique identifier for the instance of the triggered discovery
# """
# DiscoveryIntegrationInput.api_project_id.__doc__ = "uuid.UUID : the unique identifier for the portfolio (ApiProjectID)"
# DiscoveryIntegrationInput.installation_id.__doc__ = "uuid.UUID : the unique identifier for the given site (InstallationID)"
# DiscoveryIntegrationInput.network_device_id.__doc__ = "uuid.UUID : the DeviceSpecs.NetworkDeviceID for the given integration_device_id"
# DiscoveryIntegrationInput.integration_device_id.__doc__ = "uuid.UUID : the unique identifier for the integration device the discovery is triggered against"
# DiscoveryIntegrationInput.user_id.__doc__ = "uuid.UUID : the unique identifier of the user who triggered the discovery"
# DiscoveryIntegrationInput.batch_no.__doc__ = "uuid.UUID : the unique identifier for the instance of the triggered discovery"

DataFeedFileProcessOutput = namedtuple('DataFeedFileProcessOutput',
                                       [
                                           'data_feed_id', 'data_feed_file_status_id',
                                           'client_tracking_id',
                                           'source_type', 'file_name', 'file_received',
                                           'file_process_status',
                                           'file_process_status_change', 'process_started',
                                           'process_completed',
                                           'minutes_since_received', 'minutes_since_processed',
                                           'file_size',
                                           'log_file_path', 'output', 'error'
                                       ])


def generate_password():
    """Generate a ten-character alphanumeric password with at least one lowercase character, at least one uppercase
    character, and at least three digits.
    """
    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(10))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3):
            break
    return password


def convert_to_sqm(df: pandas.DataFrame, sqft_col_name: str):
    """Convert to square metres

    Convert floor area from square feet to square metres.

    Parameters
    ----------
    df : pandas.DataFrame
        The site asset register dataframe.
    sqft_col_name : str
        The name of the column containing the Floor Area values in sq. ft. to be converted.

    Returns
    -------
    df : pandas.DataFrame
        The input dataframe after converting the `sqft_col_name` column to square metres.


    """
    df[sqft_col_name] = df[sqft_col_name] * 0.09290304
    return df


def convert_to_pascal_case(text: Union[str, List[str]]):
    """Convert to PascalCase

    Capitalises the first letter of each word and strips any non-alphanumeric (``[a-zA-Z0-9]``) characters from between
    words as well as any leading or trailing the string.

    Parameters
    ----------
    text : Union[str, List[str]]
        A string or list of strings

    Returns
    -------
    Union[str, List[str]]
        If passed a string, the function returns the converted string. If passed a list of strings, the function
        returns a list of converted strings.

    """
    if type(text) == str:
        text = re.sub(r"^[^a-zA-Z0-9]", '', str(text))
        text = str.upper(text[0]) + text[1:]
        if not text:
            return text
        text = re.sub(r"[^a-zA-Z0-9]([a-zA-Z0-9])", lambda matched: str.upper(matched.group(1)), text)
        return re.sub(r"[^a-zA-Z0-9]", '', text)
    elif type(text) == list and {isinstance(text[j], str) for j in range(len(text))}.issubset([True]):
        for i in range(len(text)):
            text_item = text[i]

            text_item = re.sub(r"^[^a-zA-Z0-9]", '', str(text_item))
            text_item = str.upper(text_item[0]) + text_item[1:]
            if not text_item:
                text[i] = text_item
            text_item = re.sub(r"[^a-zA-Z0-9]([a-zA-Z0-9])", lambda matched: str.upper(matched.group(1)), text_item)

            text[i] = re.sub(r"[^a-zA-Z0-9]", '', text_item)
        return text
    else:
        logger.exception(f"The value passed to the text parameter was not a string or a list of strings. "
                         f"Unable to convert to pascal case. ")
        return False


def requests_retry_session(retries=5, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=0.3, session=None, method_whitelist=["GET"]):
    """
    Provide retry policy for requests fired.

    Parameters
    ----------
    retries : number
        Number of retries the retry would do before declaring it as an exception.
        Defaults to 5.
    status_forcelist : List[number]
        A set of integer HTTP status codes that we should force a retry on.
        Defaults to 429, 500, 502, 503, 504.
    backoff_factor : number
        A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a second try without a delay).
        {backoff factor} * (2 ** ({number of total retries} - 1)) seconds
        Defaults to 0.3
    method_whitelist : List[string]
        Set of uppercased HTTP method verbs that we should retry on
        Defaults to: GET

    Returns
    -------
        Session containing the retry configuration.
        Can be changed as requests_retry_session().get() or .post() depending on requirements
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status_forcelist=status_forcelist,
        backoff_factor=backoff_factor,
        method_whitelist=method_whitelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter=adapter)
    session.mount('https://', adapter=adapter)
    return session

def is_valid_uuid(uuid_to_test: Union[uuid.UUID, str], version=4) -> bool:
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    """

    if uuid_to_test is None:
        return False

    if not isinstance(uuid_to_test, uuid.UUID) and not isinstance(uuid_to_test, str):
        print('uuid_to_test is not a valid UUID or str type.')
        return False

    try:
        if isinstance(uuid_to_test, uuid.UUID):

            if uuid_to_test == uuid.UUID(int=0):
                return False
            
            return uuid_to_test.version == version
         
        uuid_obj = uuid.UUID(str(uuid_to_test), version=version)
    except Exception:
        return False

    return str(uuid_obj) == uuid_to_test

def convert_bytes(bytes_number):
    tags = [ "Byte", "Kilobyte", "Megabyte", "Gigabyte", "Terabyte" ]
 
    i = 0
    double_bytes = bytes_number
 
    while (i < len(tags) and  bytes_number >= 1024):
            double_bytes = bytes_number / 1024.0
            i = i + 1
            bytes_number = bytes_number / 1024
 
    return str(round(double_bytes, 2)) + " " + tags[i]

_site_schema = pandera.DataFrameSchema(
    {
        'InstallationName': pandera.Column(pandera.String, checks=pandera.Check.str_length(1, 255)),
        'InstallationCode': pandera.Column(pandera.STRING, coerce=True, checks=pandera.Check.str_length(1, 100)),
        'Address': pandera.Column(pandera.String, checks=[pandera.Check.str_length(1, 250)]),
        'Country': pandera.Column(pandera.String, checks=[pandera.Check.str_length(1, 50)]),
        'Suburb': pandera.Column(pandera.String, checks=[pandera.Check.str_length(1, 50)]),
        'State': pandera.Column(pandera.String, checks=[pandera.Check.str_length(1, 100)], required=False),
        'StateName': pandera.Column(pandera.String, checks=[pandera.Check.str_length(1, 50, n_failure_cases=None)]),
        'FloorAreaM2': pandera.Column(pandera.Float, checks=[pandera.Check.greater_than_or_equal_to(0)]),
        'ZipPostCode': pandera.Column(pandera.STRING, checks=[pandera.Check.str_length(1, 20)]),
        'Latitude': pandera.Column(pandera.Float, required=False),
        'Longitude': pandera.Column(pandera.Float, required=False),
        'Timezone': pandera.Column(pandera.String, required=False),
        'InstallationId': pandera.Column(pandera.String, required=False),
    }
)

_work_order_schema = pandera.DataFrameSchema(
    columns={
        'WorkOrderId': pandera.Column(pandera.String, required=True),
        'InstallationId': pandera.Column(pandera.String, checks=[
            pandera.Check(lambda x: uuid.UUID(x).__class__ == uuid.UUID, element_wise=True)], required=True),
        'WorkOrderSiteIdentifier': pandera.Column(pandera.STRING, coerce=True, required=True),
        'WorkOrderCategory': pandera.Column(pandera.String, checks=[
            pandera.Check.isin(list(WORK_ORDER_CATEGORY.__args__), ignore_na=False)], required=True),
        'Type': pandera.Column(pandera.String, required=True),
        'Description': pandera.Column(pandera.String, required=True),
        'Priority': pandera.Column(pandera.String, checks=[
            pandera.Check.isin(list(WORK_ORDER_PRIORITY.__args__), ignore_na=False)], required=True),
        'Status': pandera.Column(pandera.String, checks=[
            pandera.Check.isin(list(WORK_ORDER_STATUS.__args__), ignore_na=False)], required=True),
        'CreatedDate': pandera.Column(pandera.DateTime, required=True, nullable=False),
        'LastModifiedDate': pandera.Column(pandera.DateTime, required=True, nullable=True),
        'WorkStartedDate': pandera.Column(pandera.DateTime, required=True, nullable=True),
        'WorkCompletedDate': pandera.Column(pandera.DateTime, required=True, nullable=True),
        'ClosedDate': pandera.Column(pandera.DateTime, required=True, nullable=True),
        'RawPriority': pandera.Column(pandera.String, required=True, nullable=False),
        'RawWorkOrderCategory': pandera.Column(pandera.String, required=True, nullable=False),
        'SubType': pandera.Column(pandera.String, required=False, nullable=True),
        'Vendor': pandera.Column(pandera.String, required=False, nullable=True),
        'VendorId': pandera.Column(pandera.String, required=False, nullable=True),
        'EquipmentClass': pandera.Column(pandera.String, required=False, nullable=True),
        'RawEquipmentClass': pandera.Column(pandera.String, required=False, nullable=True),
        'EquipmentLabel': pandera.Column(pandera.String, required=False, nullable=True),
        'RawEquipmentId': pandera.Column(pandera.String, required=False, nullable=True),
        'TenantId': pandera.Column(pandera.String, required=False, nullable=True),
        'TenantName': pandera.Column(pandera.String, required=False, nullable=True),
        'NotToExceedCost': pandera.Column(pandera.Float, required=False, nullable=True),
        'TotalCost': pandera.Column(pandera.Float, required=False, nullable=True),
        'BillableCost': pandera.Column(pandera.Float, required=False, nullable=True),
        'NonBillableCost': pandera.Column(pandera.Float, required=False, nullable=True),
        'Location': pandera.Column(pandera.String, required=False, nullable=True),
        'RawLocation': pandera.Column(pandera.String, required=False, nullable=True),
        'ScheduledStartDate': pandera.Column(pandera.DateTime, required=False, nullable=True),
        'ScheduledCompletionDate': pandera.Column(pandera.DateTime, required=False, nullable=True),
    },
    coerce=True,
    strict=False,
    name=None
)
