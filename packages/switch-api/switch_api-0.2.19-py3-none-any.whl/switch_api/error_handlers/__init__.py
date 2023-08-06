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
>>> api_inputs = sw.initialize(user_id, api_project_id) # set api_project_id to the relevant portfolio and user_id to
                                                       # your own user identifier
>>> test_df = pd.DataFrame({'DateTime':['2021-06-01 00:00:00', '2021-06-01 00:15:00', '', '2021-06-01 00:45:00'],
... 'Value':[10, 20, 30, 40], 'device_id':['xyz', 'xyz', 'xyz', 'xyz']})
>>> df_invalid_datetime, df = validate_datetime(df=test_df, datetime_col=['DateTime'], dt_fmt='%Y-%m-%d %H:%M:%S')
>>> if df_invalid_datetime.shape[0] != 0:
...     sw.error_handlers.post_errors(api_inputs, df_invalid_datetime, error_type='DateTime')

"""

from .error_handlers import invalid_file_format, validate_datetime, post_errors

__all__ = ['validate_datetime', 'invalid_file_format', 'post_errors']
