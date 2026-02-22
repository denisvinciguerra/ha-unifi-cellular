"""Sensor platform for UniFi Cellular integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import UniFiCellularCoordinator
from .const import (
    ALL_SENSORS,
    DOMAIN,
    SIM_SENSOR_TEMPLATES,
    UniFiCellularSensorDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UniFi Cellular sensors."""
    coordinator: UniFiCellularCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[UniFiCellularSensor] = []

    # Standard sensors (signal, radio, device, ip/geo, wan3)
    for description in ALL_SENSORS:
        entities.append(UniFiCellularSensor(coordinator, description))

    # Per-SIM sensors
    sim_count = coordinator.data.get("sim_count", 0)
    for slot in range(sim_count):
        sim_data = coordinator.data.get(f"sim_{slot}", {})
        slot_num = sim_data.get("slot", slot + 1)
        is_esim = sim_data.get("esim", False)
        label = f"eSIM Slot {slot_num}" if is_esim else f"SIM Slot {slot_num}"

        for template in SIM_SENSOR_TEMPLATES:
            entities.append(
                UniFiCellularSimSensor(coordinator, template, slot, label)
            )

    async_add_entities(entities)


class UniFiCellularSensor(CoordinatorEntity[UniFiCellularCoordinator], SensorEntity):
    """Representation of a UniFi Cellular sensor."""

    entity_description: UniFiCellularSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: UniFiCellularCoordinator,
        description: UniFiCellularSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        mac = coordinator.data.get("device_mac", "unknown")
        self._attr_unique_id = f"{mac}_{description.key}"
        self._attr_device_info = _build_device_info(coordinator)

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.attr_fn:
            return self.entity_description.attr_fn(self.coordinator.data)
        return None


class UniFiCellularSimSensor(CoordinatorEntity[UniFiCellularCoordinator], SensorEntity):
    """Representation of a per-SIM sensor."""

    entity_description: UniFiCellularSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: UniFiCellularCoordinator,
        description: UniFiCellularSensorDescription,
        slot_index: int,
        slot_label: str,
    ) -> None:
        """Initialize the SIM sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._slot_index = slot_index
        self._slot_label = slot_label

        mac = coordinator.data.get("device_mac", "unknown")
        self._attr_unique_id = f"{mac}_sim{slot_index}_{description.key}"
        self._attr_device_info = _build_device_info(coordinator)
        self._attr_name = f"{slot_label} {description.name or description.key}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        sim_data = self.coordinator.data.get(f"sim_{self._slot_index}", {})
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(sim_data)
        return None


def _build_device_info(coordinator: UniFiCellularCoordinator) -> DeviceInfo:
    """Build device info from coordinator data."""
    data = coordinator.data
    mac = data.get("device_mac", "unknown")
    model = data.get("device_shortname") or data.get("device_model") or "UniFi Cellular"
    return DeviceInfo(
        identifiers={(DOMAIN, mac)},
        name=data.get("device_name", "UniFi Cellular"),
        manufacturer="Ubiquiti",
        model=model,
        sw_version=data.get("device_version"),
        configuration_url=f"https://{coordinator.host}",
    )
