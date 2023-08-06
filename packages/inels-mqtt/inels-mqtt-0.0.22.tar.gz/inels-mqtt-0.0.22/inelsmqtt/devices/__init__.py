"""Class handle base info about device."""
import logging
import json

from typing import Any

from inelsmqtt.util import DeviceValue
from inelsmqtt import InelsMqtt
from inelsmqtt.const import (
    DEVICE_TYPE_DICT,
    FRAGMENT_DOMAIN,
    TOPIC_FRAGMENTS,
    FRAGMENT_DEVICE_TYPE,
    FRAGMENT_SERIAL_NUMBER,
    FRAGMENT_UNIQUE_ID,
    DEVICE_CONNCTED,
)

_LOGGER = logging.getLogger(__name__)


class Device(object):
    """Carry basic device stuff

    Args:
        object (_type_): default object it is new style of python class coding
    """

    def __init__(
        self,
        mqtt: InelsMqtt,
        state_topic: str,
        title: str = None,
    ) -> None:
        """Initialize instance of device

        Args:
            mqtt (InelsMqtt): instance of mqtt broker
            status_topic (str): String format of status topic
            set_topic (str): Sring format of set topic
            title (str, optional): Formal name of the device. When None
            then will be same as unique_id. Defaults to None.
        """
        fragments = state_topic.split("/")

        self.__mqtt = mqtt
        self.__device_type = DEVICE_TYPE_DICT[
            fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]
        ]
        self.__unique_id = fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]
        self.__parent_id = fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]
        self.__state_topic = state_topic
        self.__set_topic = f"{fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]}/set/{fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]}"  # noqa: E501
        self.__connected_topic = f"{fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]}/connected/{fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]}"  # noqa: E501
        self.__title = title if title is not None else self.__unique_id
        self.__domain = fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]
        self.__state: Any = None

        # subscribe availability
        self.__mqtt.subscribe(self.__connected_topic, 0, None, None)

    @property
    def unique_id(self) -> str:
        """Get unique_id of the device

        Returns:
            str: Unique ID
        """
        return self.__unique_id

    @property
    def device_type(self) -> str:
        """Get type of the device

        Returns:
            str: Type
        """
        return self.__device_type

    @property
    def parent_id(self) -> str:
        """Get Id of the controller (PLC, Bridge)

        Returns:
            str: Parent ID
        """
        return self.__parent_id

    @property
    def title(self) -> str:
        """Get name of the device

        Returns:
            str: Name
        """
        return self.__title

    @property
    def is_available(self) -> bool:
        """Get info about availability of device

        Returns:
            bool: True/False
        """
        return DEVICE_CONNCTED.get(self.__mqtt.messages[self.__connected_topic])

    @property
    def set_topic(self) -> str:
        """Set topic

        Returns:
            str: string of the set topic
        """
        return self.__set_topic

    @property
    def state_topic(self) -> str:
        """State topic

        Returns:
            str: string of the status topic
        """
        return self.__state_topic

    @property
    def domain(self) -> str:
        """Domain name of the topic
           it should represent the manufacturer

        Returns:
            str: Name of the domain
        """
        return self.__domain

    @property
    def state(self) -> Any:
        """State of the device."""
        return self.__state

    def get_value(self) -> DeviceValue:
        """Get value from inels

        Returns:
            Any: DeviceValue
        """
        val = self.__mqtt.messages.get(self.state_topic)
        dev_value = DeviceValue(
            self.__device_type, inels_value=(val.decode() if val is not None else None)
        )

        self.__state = dev_value.ha_value

        return dev_value

    def set_ha_value(self, value: Any) -> bool:
        """Set HA value. Will automaticaly convert HA value
        into the inels value format.

        Args:
            value (Any): Object value belonging to HA device
        Returns:
            true/false if publishing is successfull or not
        """
        dev = DeviceValue(self.__device_type, ha_value=value)

        self.__state = dev.ha_value

        return self.__mqtt.publish(self.__set_topic, dev.inels_set_value)

    def set_inels_value(self, value: str) -> bool:
        """Set the value into the broker

        Args:
            payload (str): Data inserted into the set topic

        Returns:
            true/false if publishing is successfull or not
        """
        dev = DeviceValue(self.__device_type, inels_value=value)

        self.__state = dev.ha_value

        return self.__mqtt.publish(self.__set_topic, dev.inels_set_value)

    def info(self):
        """Device info."""
        return DeviceInfo(self)

    def info_serialized(self) -> str:
        """Device info in json format string

        Returns:
            str: JSON string format
        """
        info = {
            "name": self.__title,
            "device_type": self.__device_type,
            "id": self.__unique_id,
            "via_device": self.__parent_id,
        }

        json_serialized = json.dumps(info)
        _LOGGER.info("Device: %s", json_serialized)

        return json_serialized


class DeviceInfo(object):
    """Device info class."""

    def __init__(self, device: Device) -> None:
        """Create object of the class

        Args:
            device (Device): device object
        """
        self.__device = device

    @property
    def manufacturer(self) -> str:
        """Manufacturer property."""
        return self.__device.domain

    @property
    def model_number(self) -> str:
        """Modle of the device."""
        return "TODO: model"

    @property
    def sw_version(self) -> str:
        """Sw version of the device."""
        return "TODO: Sw version"

    @property
    def serial_number(self) -> str:
        """Serial number of the device."""
        return self.__device.unique_id
