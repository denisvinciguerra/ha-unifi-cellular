"""The UniFi Cellular integration."""
from __future__ import annotations

import logging
import ssl
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_SITE,
    CONF_VERIFY_SSL,
    DEFAULT_SCAN_INTERVAL,
    API_DEVICES,
    API_HEALTH,
    DEVICE_TYPE_MBB,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up UniFi Cellular from a config entry."""
    coordinator = UniFiCellularCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class UniFiCellularCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch UniFi cellular device data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.host = entry.data[CONF_HOST]
        self.api_key = entry.data[CONF_API_KEY]
        self.site = entry.data[CONF_SITE]
        self.verify_ssl = entry.data.get(CONF_VERIFY_SSL, False)

        self._ssl_context: ssl.SSLContext | None = None
        if not self.verify_ssl:
            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from UniFi controller."""
        try:
            async with aiohttp.ClientSession() as session:
                devices = await self._fetch_all_devices(session)
                device_data = self._extract_mbb_metrics(devices)
                wan_data = await self._fetch_wan_health(session, devices, device_data)
                return {**device_data, **wan_data}
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with UniFi controller: {err}") from err

    async def _fetch_all_devices(self, session: aiohttp.ClientSession) -> list[dict[str, Any]]:
        """Fetch all devices from the controller."""
        url = f"https://{self.host}{API_DEVICES.format(site=self.site)}"
        headers = {"X-API-Key": self.api_key}

        async with session.get(
            url, headers=headers, ssl=self._ssl_context, timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 401:
                raise UpdateFailed("Authentication failed (invalid API key)")
            resp.raise_for_status()
            data = await resp.json()

        return data.get("data", [])

    def _extract_mbb_metrics(self, devices: list[dict[str, Any]]) -> dict[str, Any]:
        """Find MBB device and extract metrics."""
        device = next((d for d in devices if d.get("type") == DEVICE_TYPE_MBB), None)
        if not device:
            raise UpdateFailed("No UniFi MBB (cellular) device found")

        return self._extract_metrics(device)

    def _extract_metrics(self, device: dict[str, Any]) -> dict[str, Any]:
        """Extract all metrics from device data."""
        mbb = device.get("mbb", {})
        radio = mbb.get("radio", {})
        ip_settings = mbb.get("ip_settings", {})
        geo = mbb.get("geo_info", {})
        esim_info = mbb.get("esim", {})

        metrics: dict[str, Any] = {
            # Device info (used for device_info + sensors)
            "device_name": device.get("name", "UniFi Cellular"),
            "device_mac": device.get("mac", ""),
            "device_ip": device.get("ip", ""),
            "device_model": device.get("model", ""),
            "device_shortname": device.get("shortname", ""),
            "device_version": device.get("version", ""),
            "uptime": device.get("uptime", 0),
            "internet": device.get("internet", False),

            # MBB state
            "mbb_state": mbb.get("state", ""),
            "mbb_mode": mbb.get("mode", ""),
            "imei": mbb.get("imei", ""),

            # Signal quality (from radio)
            "rsrp": radio.get("rsrp"),
            "rsrq": radio.get("rsrq"),
            "rssi": radio.get("rssi"),
            "snr": radio.get("snr"),
            "signal_percent": radio.get("signal_percent"),
            "signal": radio.get("signal"),

            # Radio
            "rat": radio.get("rat", ""),
            "rat_mode_active": radio.get("rat_mode_active", ""),
            "rat_5g_uw": radio.get("rat_5g_uw", False),
            "band": radio.get("band", ""),
            "channel": radio.get("channel"),
            "rx_chan": radio.get("rx_chan"),
            "tx_chan": radio.get("tx_chan"),
            "cell_id": radio.get("cell_id"),
            "networkoperator": radio.get("networkoperator", ""),
            "mcc": radio.get("mcc"),
            "mnc": radio.get("mnc"),
            "mcc_cc2": radio.get("mcc_cc2", ""),
            "roaming": radio.get("roaming", False),
            "registration_state": radio.get("registration_state"),

            # IP & Geo
            "cellular_ip": ip_settings.get("ipv4_address", ""),
            "cellular_gateway": ip_settings.get("ipv4_gateway", ""),
            "mtu": ip_settings.get("mtu"),
            "public_ip": geo.get("address", ""),
            "isp": geo.get("isp", ""),

            # eSIM
            "esim_eid": esim_info.get("eid", ""),
        }

        # Per-SIM data
        sims = mbb.get("sim", [])
        metrics["sim_count"] = len(sims)
        for i, sim in enumerate(sims):
            metrics[f"sim_{i}"] = sim

        return metrics

    def _detect_wan_interface(
        self, devices: list[dict[str, Any]], cellular_ip: str
    ) -> str | None:
        """Detect which WAN interface corresponds to the cellular device.

        Matches the cellular IP from mbb.ip_settings.ipv4_address against
        the gateway's last_wan_interfaces to find the WAN name.
        """
        if not cellular_ip:
            return None

        for device in devices:
            wan_interfaces = device.get("last_wan_interfaces", {})
            if not wan_interfaces:
                continue
            for wan_name, wan_info in wan_interfaces.items():
                if wan_info.get("ip") == cellular_ip:
                    _LOGGER.debug(
                        "Detected cellular WAN interface: %s (IP: %s)",
                        wan_name, cellular_ip,
                    )
                    return wan_name

        return None

    async def _fetch_wan_health(
        self,
        session: aiohttp.ClientSession,
        devices: list[dict[str, Any]],
        device_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Fetch WAN health metrics for the dynamically detected interface."""
        cellular_ip = device_data.get("cellular_ip", "")
        wan_name = self._detect_wan_interface(devices, cellular_ip)

        if not wan_name:
            _LOGGER.debug("Could not detect WAN interface for cellular IP %s", cellular_ip)
            return {"wan_interface": None}

        url = f"https://{self.host}{API_HEALTH.format(site=self.site)}"
        headers = {"X-API-Key": self.api_key}

        try:
            async with session.get(
                url, headers=headers, ssl=self._ssl_context, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return {"wan_interface": wan_name}
                data = await resp.json()
        except aiohttp.ClientError:
            return {"wan_interface": wan_name}

        health_data = data.get("data", [])
        for subsystem in health_data:
            if subsystem.get("subsystem") == "wan":
                uptime_stats = subsystem.get("uptime_stats", {})
                wan_stats = uptime_stats.get(wan_name, {})
                if wan_stats:
                    return {
                        "wan_interface": wan_name,
                        "wan_availability": round(wan_stats.get("availability", 0), 2),
                        "wan_latency_avg": wan_stats.get("latency_average"),
                        "wan_uptime": wan_stats.get("uptime"),
                    }

        return {"wan_interface": wan_name}
