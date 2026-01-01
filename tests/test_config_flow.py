"""Test the PurpleAir config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.purpleair.const import (
    DOMAIN,
    CONF_TEMP_OFFSET,
    CONF_HUMIDITY_OFFSET,
    TEMP_ADJUSTMENT,
    HUMIDITY_ADJUSTMENT,
)


async def test_form(hass: HomeAssistant, mock_purpleair_device) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.purpleair.config_flow.async_get_clientsession"
    ) as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_purpleair_device)
        mock_session.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "192.168.1.100",
                CONF_NAME: "Test PurpleAir",
                CONF_TEMP_OFFSET: TEMP_ADJUSTMENT,
                CONF_HUMIDITY_OFFSET: HUMIDITY_ADJUSTMENT,
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Test PurpleAir"
    assert result2["data"] == {
        "title": "Test PurpleAir",
        "place": "Test Location",
        "id": "12345",
        "ip_address": "192.168.1.100",
        "sw_version": "7.00",
        "hw_version": "2.0",
        "model": "PA-II",
        "is_dual": True,
        CONF_TEMP_OFFSET: TEMP_ADJUSTMENT,
        CONF_HUMIDITY_OFFSET: HUMIDITY_ADJUSTMENT,
    }


async def test_form_invalid_ip(hass: HomeAssistant) -> None:
    """Test we handle invalid IP."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_IP_ADDRESS: "invalid",
            CONF_NAME: "Test PurpleAir",
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_ip_address"}


async def test_options_flow(
    hass: HomeAssistant, mock_config_entry_data, mock_config_entry_options
) -> None:
    """Test options flow."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options=mock_config_entry_options,
    )
    config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_TEMP_OFFSET: -10,
            CONF_HUMIDITY_OFFSET: 5,
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_TEMP_OFFSET: -10,
        CONF_HUMIDITY_OFFSET: 5,
    }
