# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Module defining the Task abstract base class which is inherited by the following specific task types:

- IntegrationTask
- DiscoverableIntegrationTask
- AnalyticsTask
- LogicModuleTask
- QueueTask
- EventWorkOrderTask

Also includes the Automation class which contains helper functions.

---------------
IntegrationTask
---------------
Base class used to create integrations between the Switch Automation Platform and other platforms, low-level services,
or hardware.

Examples include:
    - Pulling readings or other types of data from REST APIs
    - Protocol Translators which ingest data sent to the platform via email, ftp or direct upload within platform.

---------------------------
DiscoverableIntegrationTask
---------------------------
Base class used to create integrations between the Switch Automation Platform and 3rd party APIs.

Similar to the IntegrationTask, but includes a secondary method `run_discovery()` which triggers discovery of available
points on the 3rd party API and upserts these records to the Switch Platform backend so that the records are available
in Build - Discovery & Selection UI.

Examples include:
    - Pulling readings or other types of data from REST APIs


-------------
AnalyticsTask
-------------
Base class used to create specific analytics functionality which may leverage existing data from the platform. Each
task may add value to, or supplement, this data and write it back.

Examples include:
    - Anomaly Detection
    - Leaky Pipes
    - Peer Tracking

---------------
LogicModuleTask
---------------
Base class that handles the running, reprocessing and scheduling of the legacy logic modules in a way which enables
integration with other platform functionality.

---------
QueueTask
---------
Base class used to create data pipelines that are fed via a queue.

----------
Automation
----------
This class contains the helper methods used to register, deploy, and test the created tasks. Additional helper
functions for retrieving details of existing tasks on the Switch Automation Platform are also included in this module.

"""

from .pipeline import (IntegrationTask, QueueTask, LogicModuleTask, AnalyticsTask, DiscoverableIntegrationTask,
                       EventWorkOrderTask, logger)
from .automation import Automation
from .definitions import (IntegrationDeviceConfigPropertyDefinition, IntegrationDeviceDefinition,
                          AnalyticsSettings, EventWorkOrderFieldDefinition, IntegrationSettings)

__all__ = ['IntegrationTask', 'QueueTask', 'LogicModuleTask', 'AnalyticsTask', 'DiscoverableIntegrationTask',
           'EventWorkOrderTask','Automation', 'logger', 'IntegrationDeviceConfigPropertyDefinition',
           'IntegrationDeviceDefinition', 'EventWorkOrderFieldDefinition',
           'AnalyticsSettings', 'IntegrationSettings']
