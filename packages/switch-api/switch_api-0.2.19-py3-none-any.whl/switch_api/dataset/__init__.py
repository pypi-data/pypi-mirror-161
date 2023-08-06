# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for integrating asset creation, asset updates, data ingestion, etc into the Switch Automation Platform.
"""

from .dataset import get_data, get_datasets_list, get_folders

__all__ = ['get_data', 'get_datasets_list', 'get_folders']
