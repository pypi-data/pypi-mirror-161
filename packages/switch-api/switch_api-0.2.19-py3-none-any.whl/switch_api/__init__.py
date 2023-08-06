# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Data Ingestion into the Switch Automation
=========================================

Complete package for ingestion data into the Switch Automation Platform.
"""
__all__ = ['dataset', 'analytics', 'pipeline', 'error_handlers', 'integration', 'initialize', 'cache']

from .initialize import initialize
from . import dataset
from . import analytics
from . import pipeline
from . import error_handlers
# from . import platform_insights
from . import integration
from . import cache


# import logging
# switch_log = logging.getLogger(__name__).addHandler(logging.NullHandler())
# switch_log.setLevel(logging.DEBUG)
#
# _ch = logging.StreamHandler(stream= sys.stdout)  # creates the handler
# _ch.setLevel(logging.INFO)  # sets the handler info
# _ch.setFormatter(logging.Formatter(INFOFORMATTER))  # sets the handler formatting
#
# # adds the handler to the global variable: log
# log.addHandler(_ch)
# https://dev.to/joaomcteixeira/setting-up-python-logging-for-a-library-app-6ml

__version__ = "0.2.19"
