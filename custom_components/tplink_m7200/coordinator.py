"""Poll the modem and hand data to entities."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import M7200Client, M7200Error
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class M7200Coordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, client: M7200Client) -> None:
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=30)
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(self._fetch)
        except M7200Error as err:
            raise UpdateFailed(str(err)) from err

    def _fetch(self) -> dict:
        # ponytail: re-login every cycle — no token-TTL tracking. If the device
        # rate-limits logins, cache self.client.token and re-login only on error.
        # status alone carries signal, data counters, speeds, battery, etc.
        self.client.login()
        return self.client.get_status()
