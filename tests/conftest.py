"""Fixtures for PurpleAir integration tests."""

import pytest
from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_IP_ADDRESS
from custom_components.purpleair.const import (
    DOMAIN,
    CONF_TEMP_OFFSET,
    CONF_HUMIDITY_OFFSET,
    TEMP_ADJUSTMENT,
    HUMIDITY_ADJUSTMENT,
)


pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_purpleair_device():
    """Mock a PurpleAir device response."""
    return {
        "SensorId": "12345",
        "place": "Test Location",
        "version": "7.00",
        "hardwareversion": "2.0",
        "hardwarediscovered": "2.0+BME280+PMSX003-B+PMSX003-A",
        "current_temp_f": 75,
        "current_humidity": 50,
        "current_dewpoint_f": 55,
        "pressure": 1013.25,
        "pm1_0_atm": 5.0,
        "pm2_5_atm": 10.0,
        "pm10_0_atm": 15.0,
        "pm2.5_aqi": 42,
        "pm2.5_aqi_b": 41,
        "pm1_0_atm_b": 5.1,
        "pm2_5_atm_b": 10.1,
        "pm10_0_atm_b": 15.1,
        "rssi": -45,
    }


@pytest.fixture
def mock_config_entry_data():
    """Mock config entry data."""
    return {
        "title": "Test PurpleAir",
        "place": "Test Location",
        "id": "12345",
        CONF_IP_ADDRESS: "192.168.1.100",
        "sw_version": "7.00",
        "hw_version": "2.0",
        "model": "PA-II",
        "is_dual": True,
        CONF_TEMP_OFFSET: TEMP_ADJUSTMENT,
        CONF_HUMIDITY_OFFSET: HUMIDITY_ADJUSTMENT,
    }


@pytest.fixture
def mock_config_entry_options():
    """Mock config entry options."""
    return {
        CONF_TEMP_OFFSET: TEMP_ADJUSTMENT,
        CONF_HUMIDITY_OFFSET: HUMIDITY_ADJUSTMENT,
    }
