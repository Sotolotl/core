"""The Meater Temperature Probe integration."""
import asyncio
import logging

from meater import MeaterApi

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

PLATFORMS = ["sensor"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Meater Temperature Probe component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Meater Temperature Probe from a config entry."""
    # Store an API object to access
    session = async_get_clientsession(hass)
    meater_api = MeaterApi(session)

    # Add the credentials
    try:
        _LOGGER.debug("Authenticating with the Meater API")
        await meater_api.authenticate(
            entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
        )
    # pylint: disable=broad-except
    except Exception as err:
        _LOGGER.error("Unable to authenticate with the Meater API: %s", err)
        return False

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][entry.entry_id] = meater_api
    hass.data[DOMAIN]["entities"] = {}

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
