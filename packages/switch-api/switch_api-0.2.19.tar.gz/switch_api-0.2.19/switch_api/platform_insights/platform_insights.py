# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for interacting with the insights platform services, etc of the Switch Automation Platform.
"""
# import sys
# import pandas
# import logging
# from .._utils._platform import Blob
# from .._utils._utils import ApiInputs
# from io import StringIO
#
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# consoleHandler = logging.StreamHandler(stream=sys.stdout)
# consoleHandler.setLevel(logging.INFO)
#
# logger.addHandler(consoleHandler)
# formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
#                               datefmt='%Y-%m-%dT%H:%M:%S')
# consoleHandler.setFormatter(formatter)
#
#
# def get_current_insights_by_equipment(api_inputs: ApiInputs):
#     """Get current insights by equipment.
#
#     Parameters
#     ----------
#     api_inputs : ApiInputs
#         Object returned by initialize() function.
#
#     Returns
#     -------
#     df : pandas.DataFrame
#
#
#     """
#     # payload = {}
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
#     # Get Live Insights for specific Portfolio
#     path = f'live-insights/{str(api_inputs.api_project_id)}.csv'
#     live_insights_bytes = Blob.download(api_inputs=api_inputs, account='SwitchStorage', container='data-ingestion-adx',
#                                         blob_name=path)
#     if len(live_insights_bytes) == 0:
#         logger.error(f'No data returned for this API call. File: {path}')
#         return pandas.DataFrame()
#
#     df = pandas.read_csv(StringIO(str(live_insights_bytes, 'utf-8')))
#
#     return df
