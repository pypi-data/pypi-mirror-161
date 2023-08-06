# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Module defining the various definitions used internally by the pipeline module classes.
"""
# import uuid
from typing import List
from .._utils._utils import convert_to_pascal_case
from .._utils._constants import INTEGRATION_SETTINGS_EDITORS
# from ..integration import get_templates, get_units_of_measure
# from .. import initialize


class BaseProperty:
    """BaseProperty class definition

    Parameters
    ----------
    property_name : str
        Must be in pascal case
    display_label : str
        Pretty version of the property_name
    editor : INTEGRATION_SETTINGS_EDITORS
        The editor used in the UI
    default_value : , default=None
        The default value, if applicable, for the given property
    allowed_values : list, default=None
        the set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be None.

    """
    def __init__(self, property_name: str, display_label: str, editor: INTEGRATION_SETTINGS_EDITORS,
                 default_value: object = None, allowed_values: List[object] = None):
        """
        Parameters
        ----------
        property_name : str
            Must be in pascal case
        display_label : str
            Pretty version of the property_name
        editor : INTEGRATION_SETTINGS_EDITORS
            The editor used in the UI
        default_value : , default=None
            The default value, if applicable, for the given property
        allowed_values : list, default=None
            the set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be
            None.

        """
        self.property_name = property_name
        self.display_label = display_label
        self.editor = editor
        self.default_value = default_value
        self.allowed_values = allowed_values

    @property
    def property_name(self) -> str:
        """property_name : str
            Must be in pascal case"""
        return self._property_name

    @property_name.setter
    def property_name(self, value) -> str:
        """property_name : str
                    Must be in pascal case"""
        if type(value) != str:
            raise TypeError(f"The property_name parameter only accepts strings. ")
        elif type(value) == str and not 0 < len(value) < 50:
            raise ValueError(
                f"property_name length must be between 1 and 50. Supplied '{value}' "
                f"contains {len(value)} characters. ")
        elif type(value) == str and 0 < len(value) < 50 and value != convert_to_pascal_case(value):
            raise ValueError(
                f"property_name must be in pascal case - i.e. start with a capital letter and contain no spaces, "
                f"dashes, underscores, etc. The supplied '{value}' is not in pascal case. "
            )
        self._property_name = value

    @property
    def display_label(self) -> str:
        """The display label for the given property"""
        return self._display_label

    @display_label.setter
    def display_label(self, value) -> str:
        """The display label for the given property"""
        if type(value) != str:
            raise TypeError(f"The display_label parameter only accepts strings. ")
        elif type(value) == str and not 0 < len(value) <= 255:
            raise ValueError(
                f"display_label length must be between 1 and 50. Supplied '{value}' "
                f"contains {len(value)} characters. ")
        self._display_label = value

    @property
    def editor(self) -> INTEGRATION_SETTINGS_EDITORS:
        """The editor to be used in the UI"""
        return self._editor

    @editor.setter
    def editor(self, value) -> INTEGRATION_SETTINGS_EDITORS:
        """The editor to be used in the UI"""
        if not set([value]).issubset(set(INTEGRATION_SETTINGS_EDITORS.__args__)):
            raise ValueError(
                f"Supplied value '{value}' is invalid. The editor parameter must be set to one of the allowed values "
                f"defined by the INTEGRATION_SETTINGS_EDITORS literal: {INTEGRATION_SETTINGS_EDITORS.__args__}")
        self._editor = value


class EventWorkOrderFieldDefinition(BaseProperty):
    """EventWorkOrderFieldDefinition class definition

    Used to define the set of fields available in Events UI for creation of work orders in 3rd party systems.

    Parameters
    ----------
    property_name : str
        Must be in pascal case
    display_label : str
        Pretty version of the property_name (what is displayed in Events UI).
    editor : INTEGRATION_SETTINGS_EDITORS
        The editor used in the UI
    default_value : , default=None
        The default value, if applicable, for the given property
    allowed_values : list, default=None
        the set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be None.
    """
    def __init__(self, property_name, display_label, editor, default_value, allowed_values):
        """

        Parameters
        ----------
        property_name : str
            Must be in pascal case
        display_label : str
            Pretty version of the property_name
        editor : INTEGRATION_SETTINGS_EDITORS
            The editor used in the UI
        default_value : , default=None
            The default value, if applicable, for the given property
        allowed_values : list, default=None
            The set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be
            None.
        """
        super(EventWorkOrderFieldDefinition, self).__init__(
            property_name=property_name, display_label=display_label, editor=editor, default_value=default_value,
            allowed_values=allowed_values)


class AnalyticsSettings(BaseProperty):
    """

    """
    def __init__(self, property_name, display_label, editor, default_value, allowed_values):
        """
        Parameters
        ----------
        property_name : str
            Must be in pascal case
        display_label : str
            Pretty version of the property_name
        editor : INTEGRATION_SETTINGS_EDITORS
            The editor used in the UI
        default_value : , default=None
            The default value, if applicable, for the given property
        allowed_values : list, default=None
            the set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be
            None.
        """
        super(AnalyticsSettings, self).__init__(
            property_name=property_name, display_label=display_label, editor=editor, default_value=default_value,
            allowed_values=allowed_values)


class IntegrationSettings(BaseProperty):
    """Class used for defining the UI editors, default values, etc for the key-values passed to integration_settings
    dictionaries.

    Parameters
    ----------
    property_name : str
        Must be in pascal case
    display_label : str
        Pretty version of the property_name
    editor : INTEGRATION_SETTINGS_EDITORS
        The editor used in the UI
    default_value : , default=None
        The default value, if applicable, for the given property
    allowed_values : list, default=None
        the set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be
        None.
    """
    def __init__(self, property_name, display_label, editor, default_value, allowed_values):
        """

        Parameters
        ----------
        property_name : str
            Must be in pascal case
        display_label : str
            Pretty version of the property_name
        editor : INTEGRATION_SETTINGS_EDITORS
            The editor used in the UI
        default_value : , default=None
            The default value, if applicable, for the given property
        allowed_values : list, default=None
            the set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be
            None.
        """
        super(IntegrationSettings, self).__init__(
            property_name=property_name, display_label=display_label, editor=editor, default_value=default_value,
            allowed_values=allowed_values)


# class IntegrationDevicePropertyDefinition2:
#     def __init__(self, property_name: str, display_label: str, default_value: object = None,
#                  editor: INTEGRATION_SETTINGS_EDITORS = 'text_box', values: List[object] = None,
#                  required_for_task: bool = False, use_for_discovery: bool = False, editable_in_discovery: bool = False):
#         self.property_name = property_name
#         self.display_label = display_label
#         self.default_value = default_value
#         self.editor = editor
#         self.values = values
#         self.required_for_task = required_for_task
#         self.use_for_discovery = use_for_discovery
#         self.editable_in_discovery = editable_in_discovery
#
#     @property
#     def property_name(self):
#         return self._property_name
#
#     @property_name.setter
#     def property_name(self, value):
#         if type(value) != str:
#             raise TypeError(f"The property_name parameter only accepts strings. ")
#         elif type(value) == str and not 0 < len(value) < 50:
#             raise ValueError(
#                 f"property_name length must be between 1 and 50. Supplied '{value}' "
#                 f"contains {len(value)} characters. ")
#         elif type(value) == str and 0 < len(value) < 50 and value != convert_to_pascal_case(value):
#             raise ValueError(
#                 f"property_name must be in pascal case - i.e. start with a capital letter and contain no spaces, "
#                 f"dashes, underscores, etc. The supplied '{value}' is not in pascal case. "
#             )
#         self._property_name = value
#
#     @property
#     def display_label(self):
#         return self._display_label
#
#     @display_label.setter
#     def display_label(self, value):
#         if type(value) != str:
#             raise TypeError(f"The display_label parameter only accepts strings. ")
#         elif type(value) == str and not 0 < len(value) <= 255:
#             raise ValueError(
#                 f"display_label length must be between 1 and 50. Supplied '{value}' "
#                 f"contains {len(value)} characters. ")
#         self._display_label = value
#
#     @property
#     def editor(self):
#         return self._editor
#
#     @editor.setter
#     def editor(self, value):
#         if not set([value]).issubset(set(INTEGRATION_SETTINGS_EDITORS.__args__)):
#             raise ValueError(
#                 f"The editor parameter must be set to one of the allowed values defined by the "
#                 f"INTEGRATION_SETTINGS_EDITORS literal: {INTEGRATION_SETTINGS_EDITORS.__args__}")
#         self._editor = value
#
#     @property
#     def required_for_task(self):
#         return self._required_for_task
#
#     @required_for_task.setter
#     def required_for_task(self, value):
#         if type(value) != bool:
#             raise TypeError(f"The required_for_task parameter must be passed a boolean. ")
#         self._required_for_task = value
#
#     @property
#     def use_for_discovery(self):
#         return self._use_for_discovery
#
#     @use_for_discovery.setter
#     def use_for_discovery(self, value):
#         if type(value) != bool:
#             raise TypeError(f"The use_for_discovery parameter must be passed a boolean. ")
#         self._use_for_discovery = value
#
#     @property
#     def editable_in_discovery(self):
#         return self._editable_in_discovery
#
#     @editable_in_discovery.setter
#     def editable_in_discovery(self, value):
#         if type(value) != bool:
#             raise TypeError(f"The editable_in_discovery parameter must be passed a boolean. ")
#         self._editable_in_discovery = value


class IntegrationDeviceConfigPropertyDefinition(BaseProperty):
    """
    Class corresponding to the configuration properties for the Integration device type for the given task.

    Parameters
    ----------
    property_name : str
        Must be in pascal case
    display_label : str
        Pretty version of the property_name
    editor : INTEGRATION_SETTINGS_EDITORS
        The editor used in the UI
    default_value : , default=None
        The default value, if applicable, for the given property
    allowed_values : list, default=None
        the set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be
        None.
    required_for_task : bool, default=False
        Determines whether the given property is required for the task to run (Default Value = False).
    use_for_discovery: bool, default=False
        Determines whether the given property is required for the discovery to run (Default Value = False).
    editable_in_discovery: bool, default=False
        Determines whether the given property is editable when triggering discovery (Default value = False).
    """
    def __init__(self, property_name, display_label, editor, default_value, allowed_values,
                 required_for_task: bool = False, use_for_discovery: bool = False, editable_in_discovery: bool = False):
        """

        Parameters
        ----------
        property_name : str
            Must be in pascal case
        display_label : str
            Pretty version of the property_name
        editor : INTEGRATION_SETTINGS_EDITORS
            The editor used in the UI
        default_value : , default=None
            The default value, if applicable, for the given property
        allowed_values : list, default=None
            the set of allowed values (if applicable) for the given property_name. If editor=text_box, this should be
            None.
        required_for_task : bool, default=False
            Determines whether the given property is required for the task to run (Default Value = False).
        use_for_discovery: bool, default=False
            Determines whether the given property is required for the discovery to run (Default Value = False).
        editable_in_discovery: bool, default=False
            Determines whether the given property is editable when triggering discovery (Default value = False).
        """
        super(IntegrationDeviceConfigPropertyDefinition, self).__init__(
            property_name=property_name, display_label=display_label, editor=editor, default_value=default_value,
            allowed_values=allowed_values)
        self.required_for_task = required_for_task
        self.use_for_discovery = use_for_discovery
        self.editable_in_discovery = editable_in_discovery
        self._is_configuration = True

    @property
    def required_for_task(self) -> bool:
        """"Determines whether the given property is required for the task to run (Default Value = False). """
        return self._required_for_task

    @required_for_task.setter
    def required_for_task(self, value) -> bool:
        """Determines whether the given property is required for the task to run. """
        if type(value) != bool:
            raise TypeError(f"The required_for_task parameter must be passed a boolean. ")
        self._required_for_task = value

    @property
    def use_for_discovery(self) -> bool:
        """Defines whether the given property should be used when triggering a discovery. """
        return self._use_for_discovery

    @use_for_discovery.setter
    def use_for_discovery(self, value: bool) -> bool:
        """Defines whether the given property should be used when triggering a discovery. """
        if type(value) != bool:
            raise TypeError(f"The use_for_discovery parameter must be passed a boolean. ")
        self._use_for_discovery = value

    @property
    def editable_in_discovery(self) -> bool:
        """Defines whether the given property is editable when triggering a discovery. """
        return self._editable_in_discovery

    @editable_in_discovery.setter
    def editable_in_discovery(self, value) -> bool:
        """Defines whether the given property is editable when triggering a discovery. """
        if type(value) != bool:
            raise TypeError(f"The editable_in_discovery parameter must be passed a boolean. ")
        self._editable_in_discovery = value

    @property
    def is_configuration(self):
        return self._is_configuration


class IntegrationDeviceDefinition:
    """
    Aligns with the definition of the Integration DriverDeviceType.
    """
    def __init__(self, device_type: str, default_device_name: str,
                 config_properties: List[IntegrationDeviceConfigPropertyDefinition],
                 expose_address: bool, address_label: str):
        """

        Parameters
        ----------
        device_type : str
            The DriverDeviceType of the integration device type. Must be in pascal-case.
        default_device_name : str
            The default device name for this DriverDeviceType.
        config_properties : List[IntegrationDeviceConfigPropertyDefinition]
            A list of the configuration properties associated with the device type. The items in the list should be
            instances of the `IntegrationDeviceConfigPropertyDefinition` class.
        expose_address : bool
            Defines whether the Address is exposed to the user & platform UI.
        address_label : str or None
            If `expose_address` is True, tben this defines the label shown to user in UI.
        """
        self.device_type = device_type
        self.default_device_name = default_device_name
        self.config_properties = config_properties
        self._is_integration = True
        self.expose_address = expose_address
        self.address_label = address_label

    @property
    def device_type(self) -> str:
        """The DriverDeviceType of the integration device type. Must be in pascal-case. """
        return self._device_type

    @device_type.setter
    def device_type(self, value) -> str:
        """The DriverDeviceType of the integration device type. Must be in pascal-case. """
        if type(value) != str:
            raise TypeError(f"The device_type parameter only accepts strings. ")
        elif type(value) == str and not 0 < len(value) <= 100:
            raise ValueError(f"DeviceTypeDefinition.device_type length must be between 1 and 100. Supplied '{value}' "
                             f"contains {len(value)} characters. ")
        self._device_type = value

    @property
    def default_device_name(self) -> str:
        """The default device name for this DriverDeviceType. """
        return self._default_device_name

    @default_device_name.setter
    def default_device_name(self, value) -> str:
        """The default device name for this DriverDeviceType. """
        if type(value) != str:
            raise TypeError(f"The default_device_name parameter only accepts strings. ")
        elif type(value) == str and not 0 < len(value) < 50:
            raise ValueError(f"IntegrationDeviceTypeDefinition.default_device_name length must be between 1 and 50. "
                             f"Supplied '{value}' contains {len(value)} characters. ")
        self._default_device_name = value

    @property
    def config_properties(self) -> List[IntegrationDeviceConfigPropertyDefinition]:
        """A list of the configuration properties associated with the device type. The items in the list should be
            instances of the `IntegrationDeviceConfigPropertyDefinition` class. """
        return self._config_properties

    @config_properties.setter
    def config_properties(self, value) -> List[IntegrationDeviceConfigPropertyDefinition]:
        """A list of the configuration properties associated with the device type. The items in the list should be
            instances of the `IntegrationDeviceConfigPropertyDefinition` class. """
        if type(value) != list:
            raise TypeError(f"The sensor_properties parameter must be passed a list. ")
        elif type(value) == list:
            for i in range(len(value)):
                if isinstance(value[i], IntegrationDeviceConfigPropertyDefinition) == False:
                    raise TypeError(f"Each item in the list passed to the config_properties parameter must be an "
                                    f"instance of the IntegrationDeviceConfigPropertyDefinition class")
        self._config_properties = value

    @property
    def is_integration(self):
        return self._is_integration

    @property
    def expose_address(self) -> bool:
        """Defines whether the Address is exposed to the user & platform UI. """
        return self._expose_address

    @expose_address.setter
    def expose_address(self, value) -> bool:
        """Defines whether the Address is exposed to the user & platform UI. """
        if type(value) != bool:
            raise TypeError(f"The expose_address parameter must be passed a boolean. ")
        self._expose_address = value

    @property
    def address_label(self) -> str:
        """If `expose_address` is True, tben this defines the label shown to user in UI."""
        return self._address_label

    @address_label.setter
    def address_label(self, value) -> str:
        """If `expose_address` is True, tben this defines the label shown to user in UI."""
        if type(value) != str and self.expose_address == False and value is not None:
            raise TypeError(f"The address_label parameter only accepts strings. ")
        elif value is None and self.expose_address == True:
            raise ValueError(f"address_label must be set to a string (in PascalCase) when expose_address is True. The "
                             f"parameter address_label can only be set to None when expose_address is False. ")
        elif type(value) == str and value != convert_to_pascal_case(value):
            raise ValueError(
                f"address_label must be in PascalCase - i.e. start with a capital letter and contain no spaces, "
                f"dashes, underscores, etc. The supplied '{value}' is not in PascalCase. "
            )
        self._address_label = value


# class SensorDefinition:
#     def __init__(self, property_name: str, default_sensor_name: str, object_property_template_name, unit_of_measure,
#                  is_configuration: bool = False):
#         self.property_name = property_name
#         # self.is_configuration = is_configuration
#         self._is_configuration = False
#         self.default_sensor_name = default_sensor_name
#         self.object_property_template_name = object_property_template_name
#         self.unit_of_measure = unit_of_measure
#
#     @property
#     def property_name(self):
#         return self._property_name
#
#     @property_name.setter
#     def property_name(self, value):
#         if type(value) != str:
#             raise TypeError(f"The property_name parameter only accepts strings. ")
#         elif type(value) == str and not 0 < len(value) < 50:
#             raise ValueError(
#                 f"property_name length must be between 1 and 50. Supplied '{value}' "
#                 f"contains {len(value)} characters. ")
#         elif type(value) == str and 0 < len(value) < 50 and value != convert_to_pascal_case(value):
#             raise ValueError(
#                 f"property_name must be in pascal case - i.e. start with a capital letter and contain no spaces, "
#                 f"dashes, underscores, etc. The supplied '{value}' is not in pascal case. "
#             )
#         self._property_name = value
#
#     @property
#     def is_configuration(self):
#         return self._is_configuration
#
#     # @is_configuration.setter
#     # def is_configuration(self, value):
#     #     if type(value) != bool:
#     #         raise TypeError(f"The is_configuration parameter only accepts boolean values - i.e. True or False ")
#     #     self._is_configuration = value
#
#     @property
#     def object_property_template_name(self):
#         return self._object_property_template_name
#
#     @object_property_template_name.setter
#     def object_property_template_name(self, value):  # max characters = 255, pascal case
#         allowed_values = get_templates(api_inputs=api_inputs)
#         if self.is_configuration == False and not set([value]).issubset(set(allowed_values[
#                                                                                 'ObjectPropertyTemplateName'])):
#             raise ValueError(f"{value} is not an allowed value for ObjectPropertyTemplateName. Please use "
#                              f"sw.integration.get_templates() function to retrieve list of the allowed values. ")
#         elif self.is_configuration == True and value is not None:
#             raise ValueError(f"If the defined property has IsConfiguration set to True, the value for "
#                              f"ObjectPropertyTemplateName should be set to None. ")
#         elif self.is_configuration == True and value is None:
#             self._object_property_type = None
#         elif self.is_configuration == False and set([value]).issubset(set(
#                 allowed_values['ObjectPropertyTemplateName'])):
#             self._object_property_type = allowed_values[
#                 allowed_values['ObjectPropertyTemplateName'] == value].ObjectPropertyType.item()
#         self._object_property_template_name = value
#
#     # @object_property_template_name.setter
#     # def object_property_template_name(self, value):
#     #     allowed_values = get_templates(api_inputs=api_inputs)
#     #     if self.is_configuration == False and not set([value]).issubset(set(allowed_values[
#     #                                                                             'ObjectPropertyTemplateName'])):
#     #         raise ValueError(f"{value} is not an allowed value for ObjectPropertyTemplateName. Please use "
#     #                          f"sw.integration.get_templates() function to retrieve list of the allowed values. ")
#     #     elif self.is_configuration==True and value is not None:
#     #         raise ValueError(f"If the defined property has IsConfiguration set to True, the value for "
#     #                          f"ObjectPropertyTemplateName should be set to None. ")
#     #     elif self.is_configuration==True and value is None:
#     #         self._object_property_type = None
#     #     elif self.is_configuration == False and set([value]).issubset(set(
#     #             allowed_values['ObjectPropertyTemplateName'])):
#     #         self._object_property_type = allowed_values[
#     #             allowed_values['ObjectPropertyTemplateName'] == value].ObjectPropertyType.item()
#     #     self._object_property_template_name = value
#
#     @property
#     def unit_of_measure(self):
#         return self._unit_of_measure
#
#     @unit_of_measure.setter
#     def unit_of_measure(self, value):  # max chars = 50, sentence case
#         if self._object_property_type is not None:
#             allowed_values = get_units_of_measure(api_inputs=initialize(),
#                                                   object_property_type=self._object_property_type)
#             if self.is_configuration == False and not set([value]).issubset(set(allowed_values[
#                                                                                     'UnitOfMeasureDescription'])):
#                 raise ValueError(f"{value} is not an allowed value for the Unit of Measure. Please use "
#                                  f"sw.integration.get_units_of_measure() function to retrieve list of the "
#                                  f"allowed values. ")
#             elif self.is_configuration == True and value is not None:
#                 raise ValueError(f"If the defined property has IsConfiguration set to True, the value for "
#                                  f"UnitOfMeasure should be set to None. ")
#         self._unit_of_measure = value
#       # if self._object_property_type is not None:
#       #       allowed_values = sw.integration.get_units_of_measure(api_inputs=api_inputs,
#       #                                                            object_property_type=self._object_property_type)
#       #       if self.is_configuration == False and not set([value]).issubset(set(allowed_values[
#       #                                                                               'UnitOfMeasureDescription'])):
#       #           raise ValueError(f"{value} is not an allowed value for the Unit of Measure. Please use "
#       #                            f"sw.integration.get_units_of_measure() function to retrieve list of the "
#       #                            f"allowed values. ")
#       #       elif self.is_configuration==True:
#       #           raise ValueError(f"If the defined property has IsConfiguration set to True, the value for "
#       #                            f"UnitOfMeasure should be set to None. ")
#       #   elif self._object_property_type is None:
#       #       if self.is_configuration == False:
#       #           raise ValueError(f"unit_of_measure can only be set to None if the is_configuration parameter is set"
#       #                            f" to True. ")
#
#     @property
#     def default_sensor_name(self):
#         return self._default_sensor_name
#
#     @default_sensor_name.setter
#     def default_sensor_name(self, value):
#         if type(value) != str:
#             raise TypeError(f"The default_sensor_name parameter only accepts strings. ")
#         elif type(value) == str and not 0 < len(value) <= 255:
#             raise ValueError(
#                 f"default_sensor_name length must be between 1 and 255. Supplied '{value}' "
#                 f"contains {len(value)} characters. ")
#         self._default_sensor_name = value
#
#
# class DeviceTypeConfigPropertyDefinition(BaseProperty):
#     def __init__(self, property_name, display_label, default_value,
#                  editor, allowed_values):
#         super(DeviceTypeConfigPropertyDefinition, self).__init__(property_name, display_label, default_value,
#                                                                  editor, allowed_values)
#         self._is_configuration = True
#         self._object_property_template_name = 'Configuration'
#         self._unit_of_measure = None
#
#     @property
#     def is_configuration(self):
#         return self._is_configuration
#
#     @property
#     def object_property_template_name(self):
#         return self._object_property_template_name
#
#     @property
#     def unit_of_measure(self):
#         return self._unit_of_measure
#
#
# class DeviceTypeDefinition:
#     def __init__(self, device_type: str, default_device_name: str, sensor_properties: List[SensorDefinition],
#                  expose_address: bool, address_label: str,
#                  config_properties: List[DeviceTypeConfigPropertyDefinition] = None):
#         self.device_type = device_type
#         self.default_device_name = default_device_name
#         self.sensor_properties = sensor_properties
#         self._is_integration = False
#         self.expose_address = expose_address
#         self.address_label = address_label
#         self.config_properties = config_properties
#
#     @property
#     def device_type(self):
#         return self._device_type
#
#     @device_type.setter
#     def device_type(self, value):
#         if type(value) != str:
#             raise TypeError(f"The device_type parameter only accepts strings. ")
#         elif type(value) == str and not 0 < len(value) < 50:
#             raise ValueError(f"DeviceTypeDefinition.device_type length must be between 1 and 50. Supplied '{value}' "
#                              f"contains {len(value)} characters. ")
#         elif type(value) == str and 0 < len(value) < 50 and value != convert_to_pascal_case(value):
#             raise ValueError(
#                 f"device_type must be in pascal case - i.e. start with a capital letter and contain no spaces, "
#                 f"dashes, underscores, etc. The supplied '{value}' is not in pascal case. "
#             )
#         self._device_type = value
#
#     @property
#     def default_device_name(self):
#         return self._default_device_name
#
#     @default_device_name.setter
#     def default_device_name(self, value):
#         if type(value) != str:
#             raise TypeError(f"The default_device_name parameter only accepts strings. ")
#         elif type(value) == str and len(value) > 50:
#             raise ValueError(f"The default_device_name has a maximum character count of 100. Supplied '{value}' "
#                              f"contains {len(value)} characters. ")
#         elif type(value) == str and len(value) == 0:
#             raise ValueError(f"The default_device_name must not be an empty string. ")
#         self._default_device_name = value
#
#     @property
#     def sensor_properties(self):
#         return self._sensor_properties
#
#     @sensor_properties.setter
#     def sensor_properties(self, value):
#         if type(value) != list:
#             raise TypeError(f"The sensor_properties parameter must be passed a list. ")
#         elif type(value) == list:
#             for i in range(len(value)):
#                 if isinstance(value[i], SensorDefinition) == False:
#                     raise TypeError(f"Each item in the list passed to the sensor_properties parameter must be an "
#                                     f"instance of the SensorDefinition class")
#         self._sensor_properties = value
#
#     @property
#     def is_integration(self):
#         return self._is_integration
#
#     @property
#     def expose_address(self):
#         return self._expose_address
#
#     @expose_address.setter
#     def expose_address(self, value):
#         if type(value) != bool:
#             raise TypeError(f"The expose_address parameter must be passed a boolean. ")
#         self._expose_address = value
#
#     @property
#     def address_label(self):
#         return self._address_label
#
#     @address_label.setter
#     def address_label(self, value):
#         if type(value) != str:
#             raise TypeError(f"The address_label parameter only accepts strings. ")
#         elif type(value) == str and value != convert_to_pascal_case(value):
#             raise ValueError(
#                 f"address_label must be in pascal case - i.e. start with a capital letter and contain no spaces, "
#                 f"dashes, underscores, etc. The supplied '{value}' is not in pascal case. "
#             )
#         self._address_label = value
#
#     @property
#     def config_properties(self):
#         return self._config_properties
#
#     @config_properties.setter
#     def config_properties(self, value):
#         if type(value) != list and value is not None:
#             raise TypeError(f"The config_properties parameter must be passed a list. ")
#         elif type(value) == list:
#             for i in range(len(value)):
#                 if isinstance(value[i], DeviceTypeConfigPropertyDefinition) == False:
#                     raise TypeError(f"Each item in the list passed to the config_properties parameter must be an "
#                                     f"instance of the DeviceTypeConfigPropertyDefinition class")
#         self._config_properties = value
#
