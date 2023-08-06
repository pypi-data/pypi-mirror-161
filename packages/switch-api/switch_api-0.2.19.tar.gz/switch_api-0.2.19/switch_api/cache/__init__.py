# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for storing and retrieving state stored data in the Switch Platform.
"""

from .cache import (set_cache, get_cache)

__all__ = ['set_cache', 'get_cache']