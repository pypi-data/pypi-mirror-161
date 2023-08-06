# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Module defining the Automation class which contains register, deployment and helper methods.

----------
Automation
----------

This class contains the helper methods used to register, deploy, and test the created tasks. Additional helper functions
 for retrieving details of existing tasks on the Switch Automation Platform are also included in this module.

"""
from typing import List, Union
import pandas
import requests
import inspect
import json
import logging
import sys
import uuid
from io import StringIO
from azure.servicebus import ServiceBusClient, ServiceBusReceiveMode  # , ServiceBusMessage
from .._utils._utils import _is_valid_regex, ApiInputs, _column_name_cap, DataFeedFileProcessOutput
from .._utils._constants import (argus_prefix, EXPECTED_DELIVERY, MAPPING_ENTITIES,
                                 QUEUE_NAME, ERROR_TYPE, SCHEDULE_TIMEZONE, DEPLOY_TYPE)
from .._utils._platform import _get_ingestion_service_bus_connection_string
from .pipeline import (Task, QueueTask, IntegrationTask, LogicModuleTask, AnalyticsTask, EventWorkOrderTask,
                       DiscoverableIntegrationTask)
from .definitions import (IntegrationDeviceDefinition, EventWorkOrderFieldDefinition, AnalyticsSettings,
                          IntegrationSettings, IntegrationDeviceConfigPropertyDefinition)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


class Automation:
    """Automation class defines the methods used to register and deploy tasks. """

    @staticmethod
    def run_queue_task(task: QueueTask, api_inputs: ApiInputs, consume_all_messages: bool = False):
        """Runs a Queue Task when in Development Mode

        The Queue Name should ideally be a testing Queue as messages will be consumed

        Parameters
        ----------
        task : QueueTask
            The custom QueueTask instance created by the user.
        api_inputs : ApiInputs
            Object returned by initialize() function.
        consume_all_messages : bool, default=False
            Consume all messages as they are read.

        Returns
        -------
        bool
            indicating whether the call was successful

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        if not issubclass(type(task), QueueTask):
            logger.error(
                "Driver must be an implementation of the QueueTask (Task).")
            return False

        logger.info("Running queue for  %s (%s) using queue name: %s", str(type(task).__name__), str(task.id),
                    str(task.queue_name))

        task.start(api_inputs)

        message_count = 0

        with ServiceBusClient.from_connection_string(
                _get_ingestion_service_bus_connection_string(api_inputs)) as client:
            with client.get_queue_receiver(task.queue_name,
                                           receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE) as receiver:
                while True:
                    messages = []
                    received_message_array = receiver.receive_messages(
                        max_message_count=task.maximum_message_count_per_call, max_wait_time=2)
                    for message in received_message_array:
                        messages.append(str(message))
                        message_count += 1

                    if len(received_message_array) == 0:
                        break

                    task.process_queue(api_inputs, messages)

                    if consume_all_messages == False:
                        break
        logger.info('Total messages consumed: %s', str(message_count))

    @staticmethod
    def reserve_instance(task: Task, api_inputs: ApiInputs, data_feed_id: uuid.UUID, minutes_to_reserve: int = 10):
        """Reserve a testing instance.

        Reserves a testing instance for the `driver`.

        Parameters
        ----------
        task : Task
            The custom Driver class created by the user.
        api_inputs : ApiInputs
            Object returned by initialize() function.
        data_feed_id : uuid.UUID
            The unique identifier of the data feed being tested.
        minutes_to_reserve : int, default = 10
                The duration in minutes that the testing instance will be reserved for (Default value = 10).

        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the details of the reserved testing instance.

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        logger.info("Reserving a testing instance for %s (%s) on Data Feed Id (%s). ", str(type(task).__name__),
                    str(task.id), str(data_feed_id))

        url = argus_prefix + "ReserveInstance/" + str(data_feed_id) + "/" + str(minutes_to_reserve)
        logger.info("Sending request: GET %s", url)

        response = requests.request("GET", url, timeout=20, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text, typ="Series")

        return df

    @staticmethod
    def register_task(api_inputs: ApiInputs, task: Union[Task, IntegrationTask, DiscoverableIntegrationTask, QueueTask,
                                                         AnalyticsTask, LogicModuleTask, EventWorkOrderTask]):
        """Register the task.

        Registers the task that was defined.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        task : Union[Task, IntegrationTask, DiscoverableIntegrationTask, QueueTask, AnalyticsTask, LogicModuleTask, EventWorkOrderTask]
            An instance of the custom class created from the Abstract Base Class `Task` or its abstract sub-classes:
            `IntegrationTask`,`DiscoverableIntegrationTask`, `AnalyticsTask`, `QueueTask`, `EventWorkOrderTask`, or
            `LogicModuleTask`.

        Returns
        -------
        pandas.DataFrame

        """

        if not issubclass(type(task), Task):
            logger.error(
                "Driver must be an implementation of the Abstract Base Class (Task).")
            return False

        base_class = ''
        allowed_base_classes = tuple([Task] + Task.__subclasses__())
        if issubclass(type(task), allowed_base_classes):
            base_class = task.__class__.__base__.__qualname__

        if base_class == '':
            logger.error(
                'Task must be an implementation of one of the Task sub-classes: IntegrationTask, LogicModuleTask, '
                'AnalyticsTask, EventWorkOrderTask, DiscoverableIntegrationTask.')
            return pandas.DataFrame()
        elif not set([base_class]).issubset(
                {allowed_base_classes[i].__qualname__ for i in range(len(allowed_base_classes))}):
            logger.error(f"Task must be an implementation of one of the Task sub-classes: IntegrationTask, "
                         f"LogicModuleTask, AnalyticsTask, EventWorkOrderTask, DiscoverableIntegrationTask.)")

        if type(task.mapping_entities) != list:
            logger.error('The mapping_entities parameter must have type = list. ')
            return pandas.DataFrame()
        elif not set(task.mapping_entities).issubset(set(MAPPING_ENTITIES.__args__)):
            logger.error('mapping_entities property must be a list containing one of the allowed values defined by the '
                         'MAPPING_ENTITIES literal: %s', MAPPING_ENTITIES.__args__)
            return pandas.DataFrame()

        task_settings = dict()

        if base_class == 'DiscoverableIntegrationTask':
            if not issubclass(type(task.integration_device_type_definition), IntegrationDeviceDefinition):
                logger.error(f"The integration_device_type_definition property must be a subclass of the "
                             f"IntegrationDeviceDefinition class. Current integration_device_type_definition property "
                             f"is a {type(task.integration_device_type_definition)}")
                return pandas.DataFrame()
            elif issubclass(type(task.integration_device_type_definition), IntegrationDeviceDefinition):
                props = task.integration_device_type_definition.config_properties

                if type(task.integration_device_type_definition.config_properties) != list:
                    logger.error(f"The task.integration_device_type_definition.config_properties must have type = list")
                    return pandas.DataFrame()
                else:
                    integration_settings_list = list()
                    if task.integration_device_type_definition.expose_address == True:
                        integration_settings_list.append({
                            'property_name': 'Address',
                            'display_name': task.integration_device_type_definition.address_label,
                            'editor': 'text_box', 'default_value': None, 'allowed_values': None})
                    prop_types = {True: [], False: []}
                    prop_issubclass = set()
                    for setting in task.integration_device_type_definition.config_properties:
                        val = issubclass(type(setting), IntegrationDeviceConfigPropertyDefinition)
                        prop_issubclass.add(val)
                        prop_types[val] += [setting]
                        integration_settings_list.append({
                            'property_name': setting.property_name, 'display_label': setting.display_label,
                            'editor': setting.editor, 'default_value': setting.default_value,
                            'allowed_values': setting.allowed_values})

                    if not prop_issubclass.issubset({True}):
                        logger.error(f"The task.integration_device_type_definition.config_properties parameter must be "
                                     f"a list containing one or more subclasses of the "
                                     f"IntegrationDeviceConfigPropertyDefinition class. {len(prop_types[False])} out of "
                                     f"the {len(task.integration_device_type_definition.config_properties)} items in the"
                                     f" list do not conform to this requirement. ")

            if len(integration_settings_list) > 0:
                task_settings['integration_settings'] = integration_settings_list

        if base_class == 'EventWorkOrderTask':
            # Validate that the work_order_fields_definition property matches required definition format.
            if type(task.work_order_fields_definition) != list:
                logger.error(f"The task.work_order_fields_definition property must have type list")
                return pandas.DataFrame
            else:
                prop_types = {True: [], False: []}
                prop_issubclass = set()
                work_order_input_list = list()
                for setting in task.work_order_fields_definition:
                    val = issubclass(type(setting), EventWorkOrderFieldDefinition)
                    prop_issubclass.add(val)
                    prop_types[val] += [setting]
                    work_order_input_list.append({'property_name': setting.property_name,
                                                  'display_label': setting.display_label,
                                                  'editor': setting.editor, 'default_value': setting.default_value,
                                                  'allowed_values': setting.allowed_values})
                if not prop_issubclass.issubset({True}):
                    logger.error(f"The task.work_order_fields_definition property must be a list containing one or "
                                 f"more subclasses of the EventWorkOrderFieldDefinition class. "
                                 f"{len(prop_types[False])} out of the {len(task.work_order_fields_definition)} items "
                                 f"in the list do not conform to this requirement. ")

            # Validate that the integration_settings_definition property matches required definition format.
            if type(task.integration_settings_definition) != list:
                logger.error(f"The task.integration_settings_definition property must have type list")
                return pandas.DataFrame
            else:
                prop_types = {True: [], False: []}
                prop_issubclass = set()
                integration_settings_list = list()
                for setting in task.integration_settings_definition:
                    val = issubclass(type(setting), IntegrationSettings)
                    prop_issubclass.add(val)
                    prop_types[val] += [setting]
                    integration_settings_list.append({'property_name': setting.property_name,
                                                      'display_label': setting.display_label,
                                                      'editor': setting.editor, 'default_value': setting.default_value,
                                                      'allowed_values': setting.allowed_values})
                if not prop_issubclass.issubset({True}):
                    logger.error(f"The task.integration_settings_definition property must be a list containing one or "
                                 f"more subclasses of the IntegrationSettings class. {len(prop_types[False])} "
                                 f"out of the {len(task.integration_settings_definition)} items in the list do not "
                                 f"conform to this requirement. ")
            if len(work_order_input_list) > 0 and len(integration_settings_list) > 0:
                task_settings['work_order_input'] = work_order_input_list
                task_settings['integration_settings'] = integration_settings_list

        if base_class == 'AnalyticsTask':
            # Validate that the analytics_settings_definition matches required definition format.
            if type(task.analytics_settings_definition) != list:
                logger.error(f"The task.analytics_settings_definition property must have type list")
                return pandas.DataFrame
            else:
                prop_types = {True: [], False: []}
                prop_issubclass = set()
                analytics_settings_list = list()
                for setting in task.analytics_settings_definition:
                    val = issubclass(type(setting), AnalyticsSettings)
                    prop_issubclass.add(val)
                    prop_types[val] += [setting]
                    analytics_settings_list.append({'property_name': setting.property_name,
                                                    'display_label': setting.display_label,
                                                    'editor': setting.editor, 'default_value': setting.default_value,
                                                    'allowed_values': setting.allowed_values})
                if not prop_issubclass.issubset({True}):
                    logger.error(f"The task.analytics_settings_definition property must be a list containing one or "
                                 f"more subclasses of the AnalyticsSettings class. "
                                 f"{len(prop_types[False])} out of the {len(task.analytics_settings_definition)} items "
                                 f"in the list do not conform to this requirement. ")

            if len(analytics_settings_list) > 0:
                task_settings['analytics_settings'] = analytics_settings_list

        logger.info("Registering %s (%s) to the Switch Driver Library: ", str(type(task).__name__), str(task.id))

        json_payload_verify = {
            "driverId": str(task.id),
            "name": type(task).__name__
        }

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/drivers/verification"
        logger.info("Sending request: POST %s", url)

        response = requests.post(url, json=json_payload_verify, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif response.text == "Failed":
            logger.error("This Driver Guid is already associated with a Driver with a Different Name.")
            return response_status, pandas.DataFrame()

        json_payload = {
            "driverId": str(task.id),
            "name": type(task).__name__,
            "specification": task.description,
            "mappingEntities": task.mapping_entities,
            "scriptCode": Automation._get_task_code(task),
            "baseClass": base_class,
            "settings": task_settings
            # {"integration_settings":[{"property_name":"Dummy1", "display_name":"", "default_value":"", "allowed_values":[], "editor":""}], "work_order_input":[], "analytics_settings":[], }
        }

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/script-driver/registration"
        logger.info("Sending request: POST %s", url)

        response = requests.post(url, json=json_payload, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text)
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def list_tasks(api_inputs: ApiInputs, search_name_pattern: str = '*'):
        """Get a list of the registered tasks.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        search_name_pattern : str, optional
            A pattern that should be used as a filter when retrieving the list of deployed drivers
            (Default value = '*').

        Returns
        -------
        pandas.DataFrame
            Dataframe containing the registered tasks.

        """
        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/drivers"

        if search_name_pattern != '*' and search_name_pattern != '':
            url += f"?name={search_name_pattern}"

        logger.info("Sending request: GET %s", url)

        response = requests.request("GET", url, timeout=20, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text)
        df = df.drop(columns=['driverId'])
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def deploy_as_on_demand_data_feed(task: EventWorkOrderTask,
                                      api_inputs: ApiInputs, data_feed_id: uuid.UUID, settings: dict,
                                      queue_name: QUEUE_NAME = 'task', data_feed_name: str = None):
        """Deploy the custom driver as an on demand data feed.

        This deployment method is only suitable for the tasks that subclass the EventWorkOrderTask base class.

        Parameters
        ----------
        task : EventWorkOrderTask
            The custom driver class created from the Abstract Base Class `EventWorkOrderTask`
        api_inputs : ApiInputs
            Object returned by initialize() function.
        data_feed_id : uuid.UUID
            The DataFeedId to update if existing, else will create a new record with the given value.
        settings : dict
            List of settings used to deploy the driver. May containing information needed to access 3rd party api
             - e.g. URI, Username, Pwd, AccessToken, etc
        queue_name : QUEUE_NAME, optional
            The queue name (Default value = 'task').
        data_feed_name : str, Optional
            The name of the data feed (to be displayed in Task Insights UI). If not provided, will default to the
            task name.

        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the details of the deployed https endpoint data feed.

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        if not issubclass(task.__class__, EventWorkOrderTask):
            logger.error("Only task derived from EventWorkOrderTask can be deployed as OnDemand.")
            return pandas.DataFrame()

        if not isinstance(settings, dict):
            logger.error("setting parameter should be of type dict.")
            return pandas.DataFrame()
        elif not settings or not bool(settings) or len(settings) == 0:
            logger.error("setting parameter for On Demand Data Feed cannot be empty.")
            return pandas.DataFrame()

        if data_feed_id is None and data_feed_name is None:
            data_feed_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
            data_feed_name = task.__class__.__qualname__
        elif data_feed_id is not None and data_feed_name is None:
            data_feed_id = data_feed_id
            data_feed_name = data_feed_name

        headers = api_inputs.api_headers.default

        if not set([queue_name]).issubset(set(QUEUE_NAME.__args__)):
            logger.error('queue_name parameter must be set to one of the allowed values defined by the '
                         'QUEUE_NAME literal: %s', QUEUE_NAME.__args__)
            return pandas.DataFrame()

        logger.info('Deploy %s (%s) as a data feed for ApiProjectID: %s', type(task).__name__, str(task.id),
                    api_inputs.api_project_id)

        payload = {
            "dataFeedId": str(data_feed_id),
            "driverId": str(task.id),
            "name": data_feed_name,
            "feedType": ",".join(task.mapping_entities),
            "expectedDelivery": "NA",
            "sourceType": "OnDemand",
            "queueName": queue_name,
            "settings": settings
        }

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/tasks/deployment"

        logger.info("Sending request: POST %s", url)

        response = requests.post(url, json=payload, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(StringIO(response.text), typ='Series').to_frame().T
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def deploy_as_email_data_feed(task: Union[Task, IntegrationTask, DiscoverableIntegrationTask, QueueTask,
                                              AnalyticsTask, LogicModuleTask, EventWorkOrderTask],
                                  api_inputs: ApiInputs, data_feed_id: uuid.UUID,
                                  expected_delivery: EXPECTED_DELIVERY, email_subject_regex: str,
                                  email_address_domain: str, queue_name: QUEUE_NAME = 'task',
                                  data_feed_name: str = None):
        """Deploy task as an email data feed.

        Deploys the created `task` as an email data feed. This allows the driver to ingest data sent via email. The
        data must be sent to data@switchautomation.com to be processed. If it is sent to another email address, the task
        will not be run.

        Parameters
        ----------
        task : Union[Task, IntegrationTask, DiscoverableIntegrationTask, QueueTask, AnalyticsTask, LogicModuleTask,
        EventWorkOrderTask]
            The custom driver class created from the Abstract Base Class `Task`
        api_inputs : ApiInputs
            Object returned by initialize() function.
        data_feed_id : uuid.UUID
            The DataFeedId to update if existing, else will create a new record with the given value.
        expected_delivery : EXPECTED_DELIVERY
            The expected delivery frequency.
        email_subject_regex : str
            Regex expression used to parse the email subject line to determine which driver the received file will
            be processed by.
        email_address_domain : str
            The email domain, without the @ symbol, of the sender. For example, if the email address that will send
            file(s) for this data feed to the Switch Automation Platform is sender@test.com, the string that should be
            passed to this parameter is "test.com".
        queue_name : QUEUE_NAME, Optional
            The name of queue (Default value = 'task').
        data_feed_name : str, Optional
            The name of the data feed (to be displayed in Task Insights UI). If not provided, the API will automatically
            default to using the task.name property of the `task` passed to function.


        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the details of the deployed email data feed.

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        if data_feed_id is None and data_feed_name is None:
            data_feed_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
            data_feed_name = task.__class__.__qualname__
        elif data_feed_id is not None and data_feed_name is None:
            data_feed_id = data_feed_id
            data_feed_name = data_feed_name

        headers = api_inputs.api_headers.default

        logger.info('Deploy %s (%s) as a data feed for ApiProjectID: %s', type(task).__name__, str(task.id),
                    api_inputs.api_project_id)

        if not _is_valid_regex(email_subject_regex):
            logger.error("%s is not valid regex.", email_subject_regex)
            return pandas.DataFrame()

        if email_address_domain == "switchautomation.com":
            logger.info("Emails can only be received from the %s domain.", email_address_domain)

        if "@" in email_address_domain:
            logger.error("Do not include the @ in the email_address_domain parameter. ")
            return pandas.DataFrame()

        if not set([expected_delivery]).issubset(set(EXPECTED_DELIVERY.__args__)):
            logger.error('expected_delivery parameter must be set to one of the allowed values defined by the '
                         'EXPECTED_DELIVERY literal: %s', EXPECTED_DELIVERY.__args__)
            return pandas.DataFrame()

        if not set([queue_name]).issubset(set(QUEUE_NAME.__args__)):
            logger.error('queue_name parameter must be set to one of the allowed values defined by the '
                         'QUEUE_NAME literal: %s', QUEUE_NAME.__args__)
            return pandas.DataFrame()

        inbox_container = "data-exchange"
        payload = {
            "dataFeedId": str(data_feed_id),
            "driverId": str(task.id),
            "name": data_feed_name,
            "feedType": ",".join(task.mapping_entities),
            "expectedDelivery": expected_delivery,
            "sourceType": "Email",
            "queueName": queue_name,
            "email": {
                "emailAddressDomain": email_address_domain,
                "emailSubjectRegex": email_subject_regex,
                "container": inbox_container
            }
        }

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/tasks/deployment"

        logger.info("Sending request: POST %s", url)

        response = requests.post(url, json=payload, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text, typ='Series').to_frame().T
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def deploy_as_ftp_data_feed(task: Union[Task, IntegrationTask, DiscoverableIntegrationTask, QueueTask,
                                            AnalyticsTask, LogicModuleTask, EventWorkOrderTask],
                                api_inputs: ApiInputs, data_feed_id: uuid.UUID, expected_delivery: EXPECTED_DELIVERY,
                                ftp_user_name: str, ftp_password: str, queue_name: QUEUE_NAME = 'task',
                                data_feed_name: str = None):
        """Deploy the custom driver as an FTP data feed

        Deploys the custom driver to receive data via an FTP data feed. Sets the `ftp_user_name` & `ftp_password` and
        the `expected_delivery` of the file.

        Parameters
        ----------
        task : Task
            The custom driver class created from the Abstract Base Class 'Task'
        api_inputs : ApiInputs
            Object returned by the initialize() function.
        data_feed_id : uuid.UUID
            The DataFeedId to update if existing, else will create a new record with the given value.
        expected_delivery : EXPECTED_DELIVERY
            The expected delivery frequency of the data.
        ftp_user_name : str
            The user_name to be used by the ftp service to authenticate delivery of the data feed.
        ftp_password : str
            The password to be used by the ftp service for the given `ftp_user_name` to authenticate delivery of the
            data feed.
        queue_name : QUEUE_NAME, default = 'task'
            The queue name (Default value = 'task').
        data_feed_name : str, Optional
            The name of the data feed (to be displayed in Task Insights UI). If not provided, will default to the
            task name.

        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the details of the deployed ftp data feed.

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        if data_feed_id is None and data_feed_name is None:
            data_feed_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
            data_feed_name = task.__class__.__qualname__
        elif data_feed_id is not None and data_feed_name is None:
            data_feed_id = data_feed_id
            data_feed_name = data_feed_name

        headers = api_inputs.api_headers.default

        if not set([expected_delivery]).issubset(set(EXPECTED_DELIVERY.__args__)):
            logger.error('expected_delivery parameter must be set to one of the allowed values defined by the '
                         'EXPECTED_DELIVERY literal: %s', EXPECTED_DELIVERY.__args__)
            return pandas.DataFrame()

        if not set([queue_name]).issubset(set(QUEUE_NAME.__args__)):
            logger.error('queue_name parameter must be set to one of the allowed values defined by the '
                         'QUEUE_NAME literal: %s', QUEUE_NAME.__args__)
            return pandas.DataFrame()

        logger.info('Deploy %s (%s) as a data feed for ApiProjectID: %s', type(task).__name__, str(task.id),
                    api_inputs.api_project_id)

        inbox_container = "data-exchange"
        payload = {
            "dataFeedId": str(data_feed_id),
            "driverId": str(task.id),
            "name": data_feed_name,
            "feedType": ",".join(task.mapping_entities),
            "expectedDelivery": expected_delivery,
            "sourceType": "Ftp",
            "queueName": queue_name,
            "ftp": {
                "ftpUserName": ftp_user_name,
                "ftpPassword": ftp_password,
                "container": inbox_container
            }
        }

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/tasks/deployment"

        logger.info("Sending request: POST %s", url)

        response = requests.post(url, json=payload, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text, typ='Series').to_frame().T
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def deploy_as_upload_data_feed(task: Union[Task, IntegrationTask, DiscoverableIntegrationTask, QueueTask,
                                               AnalyticsTask, LogicModuleTask, EventWorkOrderTask],
                                   api_inputs: ApiInputs, data_feed_id: uuid.UUID, expected_delivery: EXPECTED_DELIVERY,
                                   queue_name: QUEUE_NAME = 'task', data_feed_name: str = None):
        """Deploy the custom driver as a REST API end point Datafeed.

        To upload a file to the deployed data feed, use the UploadUrl from the response dataframe (with request type
        POST) with the following two headers:

        - 'Ocp-Apim-Subscription-Key' - set to the value of ``api_inputs.subscription_key``
        - 'Authorization' - set to the value 'Bearer ``api_inputs.bearer_token``'

        For example, to upload a file using the ``requests`` package:

        >>> import requests
        >>> url = df.loc[0,'UploadUrl']
        >>> payload={}
        >>> file_path = 'C:/xxyyzz.txt'
        >>> files={'file': open(file_path, 'rb')}
        >>> headers = {'Ocp-Apim-Subscription-Key': api_inputs.subscription_key, 'Authorization': f'Bearer {api_inputs.bearer_token}'}
        >>> response = requests.request("POST", url, headers=headers, data=payload, files=files)
        >>> print(response.text)

        Parameters
        ----------
        task : Task
            The custom driver class created from the Abstract Base Class 'Task'
        api_inputs : ApiInputs
            Object returned by the initialize() function.
        data_feed_id : uuid.UUID
            The DataFeedId to update if existing, else will create a new record with the given value.
        expected_delivery : EXPECTED_DELIVERY
            The expected delivery frequency of the data.
        queue_name : QUEUE_NAME, optional
            The queue name (Default value = 'task').
        data_feed_name : str, Optional
            The name of the data feed (to be displayed in Task Insights UI). If not provided, will default to the
            task name.

        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the details of the deployed https endpoint data feed.

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        if data_feed_id is None and data_feed_name is None:
            data_feed_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
            data_feed_name = task.__class__.__qualname__
        elif data_feed_id is not None and data_feed_name is None:
            data_feed_id = data_feed_id
            data_feed_name = data_feed_name

        headers = api_inputs.api_headers.default

        if not set([expected_delivery]).issubset(set(EXPECTED_DELIVERY.__args__)):
            logger.error('expected_delivery parameter must be set to one of the allowed values defined by the '
                         'EXPECTED_DELIVERY literal: %s', EXPECTED_DELIVERY.__args__)
            return pandas.DataFrame()

        if not set([queue_name]).issubset(set(QUEUE_NAME.__args__)):
            logger.error('queue_name parameter must be set to one of the allowed values defined by the '
                         'QUEUE_NAME literal: %s', QUEUE_NAME.__args__)
            return pandas.DataFrame()

        logger.info('Deploy %s (%s) as a data feed for ApiProjectID: %s', type(task).__name__, str(task.id),
                    api_inputs.api_project_id)

        payload = {
            "dataFeedId": str(data_feed_id),
            "driverId": str(task.id),
            "name": data_feed_name,
            "feedType": ",".join(task.mapping_entities),
            "expectedDelivery": expected_delivery,
            "sourceType": "Upload",
            "queueName": queue_name,
            "upload": {
                "placeholder": ""
            },
        }

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/tasks/deployment"

        logger.info("Sending request: POST %s", url)

        response = requests.post(url, json=payload, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(StringIO(response.text), typ='Series').to_frame().T
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def deploy_on_timer(task: Union[Task, IntegrationTask, DiscoverableIntegrationTask, QueueTask,
                                    AnalyticsTask, LogicModuleTask, EventWorkOrderTask],
                        api_inputs: ApiInputs, data_feed_id: uuid.UUID, expected_delivery: EXPECTED_DELIVERY,
                        cron_schedule: str, queue_name: QUEUE_NAME = "task", settings: dict = None,
                        schedule_timezone: SCHEDULE_TIMEZONE = 'Local', timezone_offset_minutes: int = None,
                        data_feed_name: str = None):
        """Deploy driver to run on timer.

        Parameters
        ----------
        task : Task
            The custom driver class created from the Abstract Base Class `Task`.
        api_inputs : ApiInputs
            Object returned by initialize.initialize() function
        data_feed_id : uuid.UUID
            The DataFeedId to update if existing, else will create a new record with the given value.
        expected_delivery : EXPECTED_DELIVERY
            The expected delivery frequency.
        cron_schedule : str
            The CRONOS cron object containing the required schedule for the driver to be run. For details on the
            required format, see: https://crontab.cronhub.io/
        queue_name : QUEUE_NAME, optional
            The queue name (Default value = 'task').
        settings : dict, Optional
            List of settings used to deploy the driver. For example, may contain the user_name and password required to
            authenticate calls to a third-party API (Default value = None).
        schedule_timezone : SCHEDULE_TIMEZONE, optional
            Whether the ``cron_schedule`` should be applied based on Local or Utc timezone. If set to `Local`, this is
            taken as the timezone of the western-most site in the given portfolio (Default value = 'Local').
        timezone_offset_minutes: int, Optional
            Timezone offset in minutes (from UTC) to be used when applying the ``cron_schedule`` (Default value = None).
        data_feed_name : str, Optional
            The name of the data feed (to be displayed in Task Insights UI). If not provided, will default to the
            task name.

        Returns
        -------
        pandas.Dataframe
            A dataframe containing the details of the deployed data feed.

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        if data_feed_id is None and data_feed_name is None:
            data_feed_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
            data_feed_name = task.__class__.__qualname__
        elif data_feed_id is not None and data_feed_name is None:
            data_feed_id = data_feed_id
            data_feed_name = data_feed_name

        if timezone_offset_minutes is None:
            timezone_offset_minutes = 0

        headers = api_inputs.api_headers.default

        if not set([expected_delivery]).issubset(set(EXPECTED_DELIVERY.__args__)):
            logger.error('expected_delivery parameter must be set to one of the allowed values defined by the '
                         'EXPECTED_DELIVERY literal: %s', EXPECTED_DELIVERY.__args__)
            return pandas.DataFrame()

        if not set([schedule_timezone]).issubset(set(SCHEDULE_TIMEZONE.__args__)):
            logger.error('schedule_timezone parameter must be set to one of the allowed values defined by the '
                         'SCHEDULE_TIMEZONE literal: %s', SCHEDULE_TIMEZONE.__args__)
            return pandas.DataFrame()

        if not set([queue_name]).issubset(set(QUEUE_NAME.__args__)):
            logger.error('queue_name parameter must be set to one of the allowed values defined by the '
                         'QUEUE_NAME literal: %s', QUEUE_NAME.__args__)
            return pandas.DataFrame()

        if 5 > len(cron_schedule.split(' ')) > 6:
            logger.error("cron_schedule parameter must be in the format * * * * *")
            return pandas.DataFrame()

        # if task.__class__.__qualname__ == 'DiscoverableIntegrationTask':
        #     config_props = task.integration_device_type_definition.config_properties
        #     property_name_dict = dict
        #     for i in range(len(config_props)):
        #         property_name_dict[config_props[i].property_name] = config_props[i].default_value

        # if task.__class__.__qualname__ == 'EventWorkOrderTask':
        #     config_props = task.integration_settings_definition
        #     property_name_list = []
        #     property_defaults_dict = {}
        #     for i in len(config_props):
        #         property_name_list.append(config_props[i].property_name)
        #         property_defaults_dict[config_props[i].property_name] = config_props[i].default_value
        #
        #     if settings is not None and not set(settings.keys()).issubset(set(property_name_list)):
        #         missing_keys = list(set(property_name_list).difference(set(settings.keys())))
        #         missing_required_keys = []
        #         missing_optional_keys = []
        #         for j in range(len(missing_keys)):
        #             if property_defaults_dict[missing_keys[j]] is None or property_defaults_dict[missing_keys[j]] == '':
        #                 missing_required_keys.append(missing_keys[j])
        #                 missing_optional_keys
        #             else:
        #                 missing_optional_keys.append(missing_keys[j])
        #                 missing_required_keys
        #         if len(missing_required_keys) > 0 and len(missing_optional_keys) == 0:
        #             loggger.error(f"settings parameter is missing the following required key(s): {missing_required_keys}.")

        logger.info('Deploy %s (%s) on timer for ApiProjectID: %s and schedule: %s.', type(task).__name__,
                    str(task.id), api_inputs.api_project_id, cron_schedule)
        logger.info('Feed Type is %s', str(task.mapping_entities))
        logger.info('Settings to be passed to the driver on start are: %s', str(settings))

        payload = {
            "dataFeedId": str(data_feed_id),
            "driverId": str(task.id),
            "name": data_feed_name,
            "feedType": ",".join(task.mapping_entities),
            "expectedDelivery": expected_delivery,
            "sourceType": "Timer",
            "queueName": queue_name,
            "timer": {
                "cronSchedule": cron_schedule,
                "timezoneOffsetMinutes": timezone_offset_minutes,
                "scheduleTimezone": schedule_timezone
            },
            "settings": settings
        }

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/tasks/deployment"

        logger.info("Sending request: POST %s", url)

        response = requests.post(url, json=payload, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200 and len(response.text) > 0:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            error_df = pandas.read_json(response.text)
            return response_status, error_df
        elif response.status_code != 200 and len(response.text) == 0:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text, typ='Series').to_frame().T
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def cancel_deployed_data_feed(api_inputs: ApiInputs, data_feed_id: uuid.UUID, deployment_type: List[DEPLOY_TYPE]):
        """Cancel deployment for a given `data_feed_id` and `deployment_type`

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize.initialize() function
        data_feed_id: uuid.UUID
            Datafeed Id to cancel deployment
        deployment_type: List[DEPLOY_TYPE]


        Returns
        -------
        str
            A string containing the response text.

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        if data_feed_id == None or data_feed_id == '':
            logger.error('Data feed Id cannot be Empty or None')
            return

        if type(deployment_type) != list:
            logger.error('deployment_type should be of type  list.')
            return
        elif deployment_type == None or len(deployment_type) == 0:
            logger.error('deployment_type cannot be empty. Please specify deployment_type to cancel deployment.')
            return
        elif not set(deployment_type).issubset(set(DEPLOY_TYPE.__args__)):
            logger.error('deployment_type item parameter must be set to one of the allowed values defined by the '
                         'DEPLOY_TYPE literal: %s', DEPLOY_TYPE.__args__)
            return

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/deployment/" \
              f"{data_feed_id}/cancel"

        logger.info("Cancel deployment type/s with DataFeedID: %s for ApiProjectID: %s", data_feed_id,
                    api_inputs.api_project_id)
        logger.info("Source Types: %s", ",".join(deployment_type))
        logger.info("Sending request: POST %s", url)

        payload = {
            'sourceTypes': deployment_type
        }

        response = requests.post(url, headers=headers, json=deployment_type)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        # Check if there's any timer deploy_type being cancelled, delete it as well by calling delete method
        if any("Timer" in deploy_type for deploy_type in deployment_type):
            return Automation.delete_deployed_data_feed(api_inputs=api_inputs, data_feed_id=data_feed_id)

        df = pandas.read_json(response.text, typ='Series').to_frame().T
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def delete_deployed_data_feed(api_inputs: ApiInputs, data_feed_id: uuid.UUID):
        """Delete deployment for a given `data_feed_id`.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize.initialize() function
        data_feed_id: uuid.UUID
            Datafeed Id to cancel deployment

        Returns
        -------
        str
            A string containing the response text.

        """
        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        if data_feed_id == None or data_feed_id == '':
            logger.error('Data feed Id cannot be None')
            return

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/deployment/" \
              f"{data_feed_id}/delete"

        logger.info("Delete deployment with DataFeedID: %s for ApiProjectID: %s", data_feed_id,
                    api_inputs.api_project_id)
        logger.info("Sending request: POST %s", url)

        response = requests.delete(url, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text, typ='Series').to_frame().T
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def list_deployments(api_inputs: ApiInputs, search_name_pattern='*'):
        """Retrieve list of deployed drivers.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize.initialize() function
        search_name_pattern : str
                A pattern that should be used as a filter when retrieving the list of deployed drivers
                (Default value = '*').

        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the drivers deployed for the given ApiProjectID that match the `search_name_pattern`.

        """

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/search"

        if search_name_pattern != '' and search_name_pattern != '*':
            url += f"?name={search_name_pattern}"

        logger.info("Sending request: GET %s", url)

        response = requests.request("GET", url, timeout=20, headers=headers)
        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text)
        df.columns = _column_name_cap(df.columns)
        return df

    @staticmethod
    def list_data_feed_history(api_inputs: ApiInputs, data_feed_id: uuid.UUID, top_count: int = 10):
        """Retrieve data feed history

        Retrieves the `top_count` records for the given `data_feed_id`.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize.initialize() function
        data_feed_id : uuid.UUID
            The unique identifier for the data feed that history should be retrieved for.
        top_count : int, default = 10
            The top record count to be retrieved. (Default value = 10).

        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the `top_count` history records for the given `data_feed_id`.

        """

        if data_feed_id is None or data_feed_id == '':
            logger.error('The data_feed_id parameter must be provided. ')
            return

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/" \
              f"{data_feed_id}/history?topCount={top_count}"

        logger.info("Sending request: GET %s", url)

        response = requests.request("GET", url, timeout=20, headers=headers)

        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text)
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def data_feed_history_process_output(api_inputs: ApiInputs, data_feed_id: uuid.UUID = None,
                                         data_feed_file_status_id: uuid.UUID = None, row_number: int = None):
        """Retrieve data feed history process output

        Retrieves the `top_count` records for the given `data_feed_id`.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize.initialize() function
        data_feed_id : uuid.UUID, default = None
            The unique identifier for the data feed that output should be retrieved for. This parameter works with the
            `row_number`
        data_feed_file_status_id : uuid.UUID, default = None
            The unique identifier for the data feed history should be retrieved for. This UUID can be retrieved from
            the list_data_feed_history() method.
        row_number: int, default = 0
            The row number from the list_data_feed_history method. It can be used in place of the file_status_id. Use
            row_number=0 to retrieve the most recent process.

        Returns
        -------
        log : str
            Containing the full print and output log for the process

        """

        if data_feed_id is None and data_feed_file_status_id is None:
            logger.error('Must supply either the data_feed_id + row_number, or the file_status_id')
            return
        elif data_feed_id is not None and data_feed_file_status_id is None and row_number is None:
            logger.error('When supplying the data_feed_id, you must also provide the row_number to retrieve. ')
            return
        elif data_feed_id is None and data_feed_file_status_id is not None and row_number is not None:
            logger.error('Please supply either the data_feed_id + row_number, or the file_status_id. ')
            return
        elif data_feed_id is not None and data_feed_file_status_id is not None and row_number is not None:
            logger.error('Please supply either the data_feed_id + row_number, or the file_status_id. ')
            return
        elif data_feed_id is not None and data_feed_file_status_id is not None and row_number is None:
            logger.error('Please supply either the data_feed_id + row_number or the file_status_id. ')
            return

        if row_number is None:
            row_number = -1

        if data_feed_id is None:
            data_feed_id = '00000000-0000-0000-0000-000000000000'

        if data_feed_file_status_id is None:
            data_feed_file_status_id = '00000000-0000-0000-0000-000000000000'

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/" \
              f"{data_feed_id}/file-status/{data_feed_file_status_id}/process-output?rowCount={row_number}"
        logger.info("Sending request: GET %s", url)

        response = requests.request("GET", url, timeout=20, headers=headers)

        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        data_feed_file_process_output = json.loads(response.text, object_hook=lambda d: DataFeedFileProcessOutput(
            data_feed_id=d['dataFeedId'], data_feed_file_status_id=d['fileStatusId'],
            client_tracking_id=d['clientTrackingId'],
            source_type=d['sourceType'], file_name=d['fileName'], file_received=d['fileReceived'],
            file_process_status=d['fileProcessStatus'], file_process_status_change=d['fileProcessStatusChange'],
            process_started=d['processStarted'], process_completed=d['processCompleted'],
            minutes_since_received=d['minutesSinceReceived'], minutes_since_processed=d['minutesSinceProcessed'],
            file_size=d['fileSize'], log_file_path=d['logFile'], output=d['output'], error=d['error']))

        return data_feed_file_process_output

    @staticmethod
    def data_feed_history_process_errors(api_inputs: ApiInputs, data_feed_id: uuid.UUID,
                                         data_feed_file_status_id: uuid.UUID):
        """Retrieve the unique error types for a given data feed file.

        Retrieves the distinct error types present for the given `data_feed_id` and `data_feed_file_status_id`.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize.initialize() function
        data_feed_id : uuid.UUID
            The unique identifier for the data feed that errors should be retrieved for.
        data_feed_file_status_id : uuid.UUID
            The unique identifier for the file processed for a given data feed that errors should be retrieved for.

        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the distinct error types present for the given data_feed_file_status_id.

        """

        if data_feed_id == '' or data_feed_file_status_id == '':
            logger.error('The data_feed_id and data_feed_file_status_id parameters must be provided. ')
            return

        if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
            logger.error("You must call initialize() before using API.")
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/" \
              f"{data_feed_id}/file-status/{data_feed_file_status_id}/process-errors"
        logger.info("Sending request: GET %s", url)

        response = requests.request("GET", url, timeout=20, headers=headers)

        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_json(response.text)
        df.columns = _column_name_cap(df.columns)

        return df

    @staticmethod
    def data_feed_history_errors_by_type(api_inputs: ApiInputs, data_feed_id: uuid.UUID,
                                         data_feed_file_status_id: uuid.UUID, error_type: ERROR_TYPE):
        """Retrieve the encountered errors for a given error type, data feed & file.

        Retrieves the errors identified for a given `error_type` for the `data_feed_id` and `data_feed_file_status_id`.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize.initialize() function
        data_feed_id : uuid.UUID
            The unique identifier for the data feed that errors should be retrieved for.
        data_feed_file_status_id
            The unique identifier for the data feed that errors should be retrieved for.
        error_type: ERROR_TYPE
            The error type of the structured logs to be retrieved.

        Returns
        -------
        df : pandas.DataFrame
            Dataframe containing the errors identified for the given `data_feed_file_status_id`.

        """

        if (data_feed_id == '' or data_feed_file_status_id == '' or data_feed_id is None or
                data_feed_file_status_id is None):
            logger.error('The data_feed_id and data_feed_file_status_id parameters must be provided. ')
            return

        if not set([error_type]).issubset(set(ERROR_TYPE.__args__)):
            logger.error('error_type parameter must be set to one of the allowed values defined by the '
                         'ERROR_TYPE literal: %s', ERROR_TYPE.__args__)
            return pandas.DataFrame()

        headers = api_inputs.api_headers.default

        url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/" \
              f"{data_feed_id}/file-status/{data_feed_file_status_id}/process-errors/type/{error_type}"

        logger.info("Sending request: GET %s", url)

        response = requests.request("GET", url, timeout=20, headers=headers)

        response_status = '{} {}'.format(response.status_code, response.reason)
        if response.status_code != 200:
            logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                         response.reason)
            return response_status, pandas.DataFrame()
        elif len(response.text) == 0:
            logger.error('No data returned for this API call. %s', response.request.url)
            return response_status, pandas.DataFrame()

        df = pandas.read_csv(StringIO(response.text), sep=",")  # , error_bad_lines=False)
        return df

    @staticmethod
    def _get_task_code(task):
        """

        Parameters
        ----------
        task : Task
            The custom driver class created from the Abstract Base Class `Task`.

        Returns
        -------
        driver_code : str
            The code used to create the `task`

        """
        task_type = type(task)
        task_code = ''
        parent_module = inspect.getmodule(task_type)
        for codeLine in inspect.getsource(parent_module).split('\n'):
            if codeLine.startswith('import ') or codeLine.startswith('from '):
                task_code += codeLine + '\n'

        task_code += '\n'
        task_code += inspect.getsource(task_type)
        task_code += ''
        task_code += 'task = ' + task_type.__name__ + '()'

        return task_code
