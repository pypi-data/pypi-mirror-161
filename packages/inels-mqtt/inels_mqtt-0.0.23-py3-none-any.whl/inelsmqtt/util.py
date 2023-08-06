"""Utility classes."""
from typing import Any, Dict

from inelsmqtt.mqtt_client import GetMessageType

from .const import (
    DEVICE_TYPE_DICT,
    SWITCH,
    SWITCH_SET,
    SWITCH_STATE,
)

ConfigType = Dict[str, str]


class DeviceValue(object):
    """Device value interpretation object."""

    def __init__(
        self,
        device_type: DEVICE_TYPE_DICT,
        inels_value: str = None,
        ha_value: Any = None,
    ) -> None:
        """initializing device info."""
        self.__inels_status_value = inels_value
        self.__inels_set_value: Any = None
        self.__ha_value = ha_value
        self.__device_type = device_type

        if self.__ha_value is None:
            self.__find_ha_value()

        if self.__inels_status_value is None:
            self.__find_inels_value()

    def __find_ha_value(self) -> None:
        """Find and crete device value object."""
        if self.__device_type == SWITCH:
            self.__ha_value = SWITCH_STATE[self.__inels_status_value]
            self.__inels_set_value = SWITCH_SET[self.__ha_value]

    def __find_inels_value(self) -> None:
        """Find inels mqtt value for specific device."""
        if self.__device_type == SWITCH:
            self.__inels_status_value = self.__find_keys_by_value(
                SWITCH_STATE, self.__ha_value
            )
            self.__inels_set_value = SWITCH_SET.get(self.__ha_value)

    def __find_keys_by_value(self, array: dict, value) -> Any:
        """Return key from dict by value

        Args:
            array (dict): dictionary where should I have to search
            value Any: by this value I'm goning to find key
        Returns:
            Any: value of the dict key
        """
        keys = list(array.keys())
        vals = list(array.values())

        index = vals.index(value)

        return keys[index]

    @property
    def ha_value(self) -> Any:
        """Converted value from inels mqtt broker into
           the HA format

        Returns:
            Any: object to corespond to HA device
        """
        return self.__ha_value

    @property
    def inels_status_value(self) -> str:
        """Raw inels value from mqtt broker

        Returns:
            str: quated string from mqtt broker
        """
        return self.__inels_status_value

    @property
    def inels_set_value(self) -> str:
        """Raw inels value for mqtt broker

        Returns:
            str: this is string format value for mqtt broker
        """
        return self.__inels_set_value


def get_value(status: GetMessageType, platform: str) -> Any:
    """Get value from pyload message."""
    if platform == SWITCH:
        return SWITCH_STATE[status]

    return None


def get_state_topic(cfg: ConfigType) -> str:
    """Get state topic."""
    return cfg["DDD"]


def get_set_topic(cfg: ConfigType) -> str:
    """Get set topic."""
    return cfg["OOO"]


def get_name(cfg: ConfigType) -> str:
    """Get name of the entity."""
    return cfg["Name"]
