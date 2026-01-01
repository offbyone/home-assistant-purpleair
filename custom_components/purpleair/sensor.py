"""The Purple Air air_quality platform."""

import logging

from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.sensor import SensorEntity

from .const import (
    DISPATCHER_PURPLE_AIR,
    DOMAIN,
    MANUFACTURER,
    SENSORS_MAP,
    SENSORS_DUAL_ONLY,
    MODEL_PA_FLEX,
    MODEL_PA_2,
    CONF_TEMP_OFFSET,
    CONF_HUMIDITY_OFFSET,
    TEMP_ADJUSTMENT,
    HUMIDITY_ADJUSTMENT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_schedule_add_entities):
    _LOGGER.debug("Registering aqi sensor with data: %s", config_entry.data)

    # Backwards compat for sensors added before 'is_dual' key created in config_flow
    if "is_dual" in config_entry.data:
        is_dual = config_entry.data["is_dual"]
    else:
        is_dual = config_entry.data["model"] in [
            MODEL_PA_FLEX,
            MODEL_PA_2,
        ]  # Backup to test for dual sensors

    # Get offset values from options first, then data, then defaults
    temp_offset = config_entry.options.get(
        CONF_TEMP_OFFSET, config_entry.data.get(CONF_TEMP_OFFSET, TEMP_ADJUSTMENT)
    )
    humidity_offset = config_entry.options.get(
        CONF_HUMIDITY_OFFSET,
        config_entry.data.get(CONF_HUMIDITY_OFFSET, HUMIDITY_ADJUSTMENT),
    )

    entities = []
    for index, entity_desc in SENSORS_MAP.items():
        if is_dual or entity_desc["key"] not in SENSORS_DUAL_ONLY:
            entities.append(
                PurpleAirQualitySensor(
                    hass, index, config_entry, entity_desc, temp_offset, humidity_offset
                )
            )

    async_schedule_add_entities(entities)


class PurpleAirQualitySensor(SensorEntity):
    """Sensor data reading from purple air device"""

    def __init__(
        self, hass, index, config_entry, entity_desc, temp_offset, humidity_offset
    ):
        self._data = config_entry.data
        self._hass = hass
        self._api = hass.data[DOMAIN]
        self._stop_listening = None
        self._temp_offset = temp_offset
        self._humidity_offset = humidity_offset

        self._uom = entity_desc["uom"]
        self._icon = entity_desc["icon"]
        self._src_key = entity_desc["key"]

        self.idx = index
        self.pa_sensor_id = self._data["id"]
        self.pa_sensor_name = self._data["title"]
        self.pa_ip_address = self._data["ip_address"]

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.pa_sensor_id),
                (DOMAIN, self.pa_ip_address),
            },
            "name": f"{self.pa_sensor_name} {MANUFACTURER}",
            "manufacturer": MANUFACTURER,
            "model": f"{self._data['model']} ({self.pa_ip_address})",
            "sw_version": self._data["sw_version"],
            "hw_version": self._data["hw_version"],
        }

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._uom

    @property
    def icon(self):
        return self._icon

    @property
    def name(self):
        nice_entity_title = self.idx.replace("_", " ").title()
        if "air_quality_index" in self.idx:
            left, last = nice_entity_title.rsplit(" ", 1)
            nice_entity_title = f"{left} ({last.upper()})"
        return f"{self.pa_sensor_name} {nice_entity_title}"

    @property
    def native_value(self):
        return self._api.get_reading(self.pa_sensor_id, self._src_key)

    @property
    def state_class(self):
        return "measurement" if self._uom is not None else None

    @property
    def unique_id(self):
        return f"{self.pa_sensor_id}_{self.idx}"

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._api.is_node_registered(self.pa_sensor_id)

    async def async_added_to_hass(self):
        self._api.register_node(
            self.pa_sensor_id,
            self.pa_ip_address,
            self._temp_offset,
            self._humidity_offset,
        )
        self._stop_listening = async_dispatcher_connect(
            self._hass, DISPATCHER_PURPLE_AIR, self.async_write_ha_state
        )

    async def async_will_remove_from_hass(self):
        if self._stop_listening:
            self._stop_listening()
            self._stop_listening = None
