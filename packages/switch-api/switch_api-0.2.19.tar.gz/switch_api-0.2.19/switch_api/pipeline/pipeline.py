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
This class contains the helper methods used to register, deploy, and test the created tasks. Additional helper functions
 for retrieving details of existing tasks on the Switch Automation Platform are also included in this module.

"""
import enum
import sys
# # import re
# import pandas
# import requests
# import inspect
import uuid
import logging
import datetime
# import json
from typing import List
from abc import ABC, abstractmethod
# from azure.servicebus import ServiceBusClient, ServiceBusReceiveMode  # , ServiceBusMessage
from .._utils._utils import ApiInputs, DiscoveryIntegrationInput  # , _is_valid_regex, generate_password, _column_name_cap, DataFeedFileProcessOutput
from .._utils._constants import (MAPPING_ENTITIES  # , api_prefix, argus_prefix, EXPECTED_DELIVERY, DEPLOY_TYPE,
                                 # QUEUE_NAME, ERROR_TYPE, SCHEDULE_TIMEZONE)
                                 )
from ..integration.helpers import get_templates, get_units_of_measure
from .definitions import (IntegrationDeviceDefinition, EventWorkOrderFieldDefinition, AnalyticsSettings, # BaseProperty
                          IntegrationSettings)  # , DeviceTypeDefinition
# from .._utils._platform import _get_ingestion_connection_string
# from io import StringIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


# Base Definitions in Switch package
class Task(ABC):
    """An Abstract Base Class called Task.

    Attributes
    ----------
    id : uuid.UUID
        Unique identifier of the task. This is an abstract property that needs to be overwritten when sub-classing.
        A new unique identifier can be created using uuid.uuid4()
    description : str
        Brief description of the task
    mapping_entities : List[MAPPING_ENTITIES]
        The type of entities being mapped. An example is:

        ``['Installations', 'Devices', 'Sensors']``
    author : str
        The author of the task.
    version : str
        The version of the task.

    """

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:
        """Unique identifier of the task. Create a new unique identifier using uuid.uuid4() """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of the task"""
        pass

    @property
    @abstractmethod
    def mapping_entities(self) -> List[MAPPING_ENTITIES]:
        """The type of entities being mapped."""
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        """"The author of the task."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """The version of the task"""
        pass


class IntegrationTask(Task):
    """Integration Task

    This class is used to create integrations that post data to the Switch Automation Platform.


    Only one of the following methods should be implemented per class, based on the type of integration required:

    - process_file()
    - process_stream()
    - process()

    """

    @abstractmethod
    def process_file(self, api_inputs: ApiInputs, file_path_to_process: str):
        """Method to be implemented if a file will be processed by the Integration Task.

        The method should contain all code used to cleanse, reformat & post the data contained in the file.

        Parameters
        ----------
        api_inputs : ApiInputs
            object returned by call to initialize()
        file_path_to_process : str
            the file path

        """
        pass

    @abstractmethod
    def process_stream(self, api_inputs: ApiInputs, stream_to_process):
        """Method to be implemented if data received via stream

        The method should contain all code used to cleanse, reformat & post the data received via the stream.

        Parameters
        ----------
        api_inputs: ApiInputs
            The object returned by call to initialize()
        stream_to_process
            The details of the stream to be processed.
        """
        pass

    @abstractmethod
    def process(self, api_inputs: ApiInputs, integration_settings: dict):
        """Method to be implemented if data

        The method should contain all code used to cleanse, reformat & post the data pulled via the integration.

        Parameters
        ----------
        api_inputs: ApiInputs
            object returned by call to initialize()
        integration_settings : dict
            Any settings required to be passed to the integration to run. For example, username & password, api key,
            auth token, etc.

        """
        pass


class DiscoverableIntegrationTask(Task):
    """Discoverable Integration Task

    This class is used to create integrations that post data to the Switch Automation Platform from 3rd party APIs that
    have discovery functionality.

    The `process()` method should contain the code required to post data for the integration. The `run_discovery()`
    method upserts records into the Integrations table so that end users can configure the points and import as
    devices/sensors within the Build - Discovery and Selection UI in the Switch Automation Platform.

    Additional properties are required to be created to support both the discovery functionality & the subsequent
    device/sensor creation from the discovery records.

    """

    @property
    @abstractmethod
    def integration_device_type_definition(self) -> IntegrationDeviceDefinition:
        """The IntegrationDeviceDefinition used to create the DriverDevices records required for the Integration
        DeviceType to be available to drag & drop in the Build - Integration Schematic UI. Contains the properties that
        define the minimum set of required fields to be passed to the integration_settings dictionaries for the
        `process()` and `run_discovery()` methods"""
        pass

    # @property
    # @abstractmethod
    # def device_type_definitions(self) -> List[DeviceTypeDefinition]:
    #     """List of DeviceTypeDefinition classes used to create the Device Types available for selection in the
    #     Build - Discovery & Selection UI in the Switch Automation Platform. """
    #     pass

    def check_integration_settings_valid(self, integration_settings: dict):
        required_integration_keys = set()

        if self.integration_device_type_definition.expose_address == True:
            required_integration_keys.add(self.integration_device_type_definition.address_label)

        for setting in self.integration_device_type_definition.config_properties:
            if setting.required_for_task == True:
                required_integration_keys.add(setting.property_name)

        if not required_integration_keys.issubset(set(integration_settings.keys())):
            logger.error(f'The integration_settings passed to the task do not contain the required keys: '
                         f'{required_integration_keys} ')
            return False
        else:
            return True

    @abstractmethod
    def run_discovery(self, api_inputs: ApiInputs, integration_settings: dict,
                      integration_input: DiscoveryIntegrationInput):
        """Method to implement discovery of available points from 3rd party API.

        The method should contain all code used to retrieve available points, reformat & post information to populate
        the Build - Discovery & Selection UI in the platform and allows users to configure discovered points prior to
        import.

        Parameters
        ----------
        api_inputs: ApiInputs
            object returned by call to initialize()
        integration_settings : dict
            Any settings required to be passed to the integration to run. For example, username & password, api key,
            auth token, etc.
        integration_input : DiscoveryIntegrationInput
            The information required to be sent to the container when the `run_discovery` method is triggered by a user
            from the UI. This information is the ApiProjectID, InstallationID, NetworkDeviceID and IntegrationDeviceID.

        """
        pass

    @abstractmethod
    def process(self, api_inputs: ApiInputs, integration_settings: dict):
        """Method to be implemented if data

        The method should contain all code used to cleanse, reformat & post the data pulled via the integration.

        Parameters
        ----------
        api_inputs: ApiInputs
            object returned by call to initialize()
        integration_settings : dict
            Any settings required to be passed to the integration to run. For example, username & password, api key,
            auth token, etc.

        """
        pass


class EventWorkOrderTask(Task):
    """Event Work Order Task

    This class is used to create work orders in 3rd party systems via tasks that are created in the Events UI of the
    Switch Automation Platform.

    """

    @property
    @abstractmethod
    def work_order_fields_definition(self) -> List[EventWorkOrderFieldDefinition]:
        """Define the fields available in Events UI when creating a work order in 3rd Party System.

        The definition of the dictionary keys, display labels in Events UI, default value & allowed values
        for the generate_work_order() method's ``work_order_input`` parameter.

            property_name - the ``work_order_input`` dictionary key
            display_label - the display label for the given property_name in Events UI Work Order creation screen
            editor - the editor shown in Events UI Work Order creation screen
            default_value - default value for this property_name (if applicable)
            allowed_values - the set of allowed values (if applicable) for the given property_name. If editor=text_box,
            this should be None.

        """
        pass

    @property
    @abstractmethod
    def integration_settings_definition(self) -> List[IntegrationSettings]:
        """Define the generate_work_order() method's integration_settings dictionary requirements & defaults.

        The definition of the dictionary keys, display labels in Task Insights UI, default value & allowed values
        for the generate_work_order() method's ``integration_settings`` input parameter.

            property_name - the ``integration_settings`` dictionary key
            display_label - the display label for the given property_name in Task Insights UI
            editor - the editor shown in Task Insights UI
            default_value - default value for this property_name (if applicable)
            allowed_values - the set of allowed values (if applicable) for the given property_name. If editor=text_box,
            this should be None.

        """
        pass

    def check_work_order_input_valid(self, work_order_input: dict):
        required_work_order_input_keys = set(['EventTaskId', 'Description', 'IntegrationId', 'DueDate', 'EventLink',
                                              'EventSummary', 'InstallationId'])

        for setting in self.work_order_fields_definition:
            required_work_order_input_keys.add(setting.property_name)

        if not required_work_order_input_keys.issubset(set(work_order_input.keys())):
            logger.error(f'The work_order_input passed to the task do not contain the required keys: '
                         f'{required_work_order_input_keys} ')
            return False
        else:
            return True

    def check_integration_settings_valid(self, integration_settings: dict):
        required_integration_keys = set()

        for setting in self.integration_settings_definition:
            required_integration_keys.add(setting.property_name)

        if not required_integration_keys.issubset(set(integration_settings.keys())):
            logger.error(f'The integration_settings passed to the task do not contain the required keys: '
                         f'{required_integration_keys} ')
            return False
        else:
            return True

    @abstractmethod
    def generate_work_order(self, api_inputs: ApiInputs, integration_settings: dict, work_order_input: dict):
        """Generate work order in 3rd party system via Events UI

        Method to generate work order in 3rd party system based on a work order task created in Events UI in the Switch
        Automation platform.

        Notes
        -----
        In addition to the defined `work_order_fields_definition` fields, the `work_order_input` dictionary passed to
        this method will contain the following keys:

        - `EventTaskId`
            - unique identifier (uuid.UUID) for the given record in the Switch Automation Platform
        - `Description`
            - free text field describing the work order to be generated.
        - `IntegrationId`
            - if linked to an existing work order in the 3rd party API, this will contain that system's identifier for
            the workorder. If generating a net new workorder, this field will be null (None).
        - `DueDate`
            - The due date for the work order as set in the Switch Automation Platform.
        - `EventLink`
            - The URL link to the given Event in the Switch Automation Platform UI.
        - `EventSummary`
            - The Summary text associated with the given Event in the Switch Automation Platform UI.
        - `InstallationId`
            - The unique identifier of the site in the Switch Automation Platform that the work order is associated
            with.

        Parameters
        ----------
        api_inputs: ApiInputs
            object returned by call to initialize()
        integration_settings : dict
            Any settings required to be passed to the integration to run. For example, username & password, api key,
            auth token, etc.
        work_order_input : dict
            The work order defined by the task created in the Events UI of the Switch Automation Platform. To be sent
            to 3rd party system for creation.
        """

        pass


class QueueTask(Task):
    """Queue Task

    This class is used to create integrations that post data to the Switch Automation Platform using a Queue as the
    data source.

    Only one of the following methods should be implemented per class, based on the type of integration required:

    - process_queue()

    """

    @property
    @abstractmethod
    def queue_name(self) -> str:
        """The name of the queue to receive Data .. Name will actually be constructed as {ApiProjectId}_{queue_name} """
        pass

    @property
    @abstractmethod
    def maximum_message_count_per_call(self) -> int:
        """ The maximum amount of messages which should be passed to the process_queue at any one time
            set to zero to consume all
        """
        pass

    @abstractmethod
    def start(self, api_inputs: ApiInputs):
        """Method to be implemented if a file will be processed by the QueueTask Task.
        This will run once at the start of the processing and should contain

        """
        pass

    @abstractmethod
    def process_queue(self, api_inputs: ApiInputs, messages: List):
        """Method to be implemented if a file will be processed by the QueueTask Task.

        The method should contain all code used to consume the messages

        Parameter
        _________
        api_inputs : ApiInputs
            object returned by call to initialize()
        messages:List)
            list of serialized json strings which have been consumed from the queue

        """
        pass


class AnalyticsTask(Task):

    @property
    @abstractmethod
    def analytics_settings_definition(self) -> List[AnalyticsSettings]:
        """Define the start() method's analytics_settings dictionary requirements & defaults.

        The definition of the dictionary keys, display labels in Task Insights UI, default value & allowed values
        for the start() method's ``analytics_settings`` input parameter.

        property_name - the analytics_settings dictionary key
        display_label - the display label for the given property_name in Task Insights UI
        editor - the editor shown in Task Insights UI
        default_value - default value for this property_name (if applicable)
        allowed_values - the set of allowed values (if applicable) for the given property_name. If editor=text_box, this
        should be None.

        """
        pass

    def check_analytics_settings_valid(self, analytics_settings: dict):
        # required_analytics_settings_keys = set(['task_id'])
        required_analytics_settings_keys= set()

        for setting in self.analytics_settings_definition:
            required_analytics_settings_keys.add(setting.property_name)

        if not required_analytics_settings_keys.issubset(set(analytics_settings.keys())):
            logger.error(f'The analytics_setting passed to the task do not contain the required keys: '
                         f'{required_analytics_settings_keys} ')
            return False
        else:
            return True

    @abstractmethod
    def start(self, api_inputs: ApiInputs, analytics_settings: dict):
        """Start.

        The method should contain all code used by the task.

        Notes
        -----
        The method should first check the analytics_settings passed to the task are valid. Pseudo code below:
         >>> if self.check_analytics_settings_valid(analytics_settings=analytics_settings == True:
         >>>    # Your actual task code here - i.e. proceed with the task if valid analytics_settings passed.
         >>> else:
         >>>    sw.pipeline.logger.error('Invalid analytics_settings passed to driver. ')

        Parameters
        ----------
        api_inputs : ApiInputs
            the object returned by call to initialize()
        analytics_settings : dict
            any setting required by the AnalyticsTask

        """
        pass


class LogicModuleTask(Task):

    @abstractmethod
    def start(self, start_date_time: datetime.date, end_date_time: datetime.date, installation_id: uuid.UUID,
              share_tag_group: str, share_tags: list):
        pass

    # Needs to be implemented into the deploy_on_timer


class RunAt(enum.Enum):
    """ """
    Every15Minutes = 1
    Every1Hour = 3
    EveryDay = 4
    EveryWeek = 5


