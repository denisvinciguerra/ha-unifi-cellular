"""Constants for UniFi Cellular integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfInformation,
    UnitOfTime,
)

DOMAIN = "unifi_cellular"

# Configuration keys
CONF_HOST = "host"
CONF_API_KEY = "api_key"
CONF_SITE = "site"
CONF_VERIFY_SSL = "verify_ssl"

# Defaults
DEFAULT_HOST = "192.168.1.1"
DEFAULT_SITE = "default"
DEFAULT_VERIFY_SSL = False
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

# API
API_DEVICES = "/proxy/network/api/s/{site}/stat/device"
API_HEALTH = "/proxy/network/api/s/{site}/stat/health"
DEVICE_TYPE_MBB = "umbb"


@dataclass(frozen=True)
class UniFiCellularSensorDescription(SensorEntityDescription):
    """Describes a UniFi Cellular sensor."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


def _signal_rating(val: float | None, thresholds: list[float]) -> str:
    if val is None:
        return "N/A"
    if val >= thresholds[0]:
        return "Excellent"
    if val >= thresholds[1]:
        return "Good"
    if val >= thresholds[2]:
        return "Fair"
    return "Poor"


# --- Signal Quality sensors ---

SIGNAL_SENSORS: tuple[UniFiCellularSensorDescription, ...] = (
    UniFiCellularSensorDescription(
        key="rsrp",
        translation_key="rsrp",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("rsrp"),
        attr_fn=lambda d: {"rating": _signal_rating(d.get("rsrp"), [-80, -95, -110])},
    ),
    UniFiCellularSensorDescription(
        key="rsrq",
        translation_key="rsrq",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("rsrq"),
        attr_fn=lambda d: {"rating": _signal_rating(d.get("rsrq"), [-5, -10, -15])},
    ),
    UniFiCellularSensorDescription(
        key="rssi",
        translation_key="rssi",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("rssi"),
    ),
    UniFiCellularSensorDescription(
        key="snr",
        translation_key="snr",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: round(d["snr"], 2) if d.get("snr") is not None else None,
        attr_fn=lambda d: {"rating": _signal_rating(d.get("snr"), [20, 10, 3])},
    ),
    UniFiCellularSensorDescription(
        key="signal_percent",
        translation_key="signal_percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal-cellular-3",
        value_fn=lambda d: d.get("signal_percent"),
    ),
    UniFiCellularSensorDescription(
        key="signal_level",
        translation_key="signal_level",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal-cellular-3",
        value_fn=lambda d: d.get("signal"),
    ),
)

# --- Radio Info sensors ---

RADIO_SENSORS: tuple[UniFiCellularSensorDescription, ...] = (
    UniFiCellularSensorDescription(
        key="rat",
        translation_key="rat",
        icon="mdi:antenna",
        value_fn=lambda d: d.get("rat"),
    ),
    UniFiCellularSensorDescription(
        key="rat_mode_active",
        translation_key="rat_mode_active",
        icon="mdi:antenna",
        value_fn=lambda d: d.get("rat_mode_active"),
    ),
    UniFiCellularSensorDescription(
        key="rat_5g_uw",
        translation_key="rat_5g_uw",
        icon="mdi:signal-5g",
        value_fn=lambda d: d.get("rat_5g_uw"),
    ),
    UniFiCellularSensorDescription(
        key="band",
        translation_key="band",
        icon="mdi:radio-tower",
        value_fn=lambda d: d.get("band"),
    ),
    UniFiCellularSensorDescription(
        key="channel",
        translation_key="channel",
        icon="mdi:radio-tower",
        value_fn=lambda d: d.get("channel"),
    ),
    UniFiCellularSensorDescription(
        key="rx_channel",
        translation_key="rx_channel",
        icon="mdi:radio-tower",
        value_fn=lambda d: d.get("rx_chan"),
    ),
    UniFiCellularSensorDescription(
        key="tx_channel",
        translation_key="tx_channel",
        icon="mdi:radio-tower",
        value_fn=lambda d: d.get("tx_chan"),
    ),
    UniFiCellularSensorDescription(
        key="cell_id",
        translation_key="cell_id",
        icon="mdi:cellphone-marker",
        value_fn=lambda d: d.get("cell_id"),
    ),
    UniFiCellularSensorDescription(
        key="operator",
        translation_key="operator",
        icon="mdi:sim",
        value_fn=lambda d: d.get("networkoperator"),
    ),
    UniFiCellularSensorDescription(
        key="mcc",
        translation_key="mcc",
        icon="mdi:earth",
        value_fn=lambda d: d.get("mcc"),
    ),
    UniFiCellularSensorDescription(
        key="mnc",
        translation_key="mnc",
        icon="mdi:earth",
        value_fn=lambda d: d.get("mnc"),
    ),
    UniFiCellularSensorDescription(
        key="country",
        translation_key="country",
        icon="mdi:earth",
        value_fn=lambda d: d.get("mcc_cc2"),
    ),
    UniFiCellularSensorDescription(
        key="roaming",
        translation_key="roaming",
        icon="mdi:airplane",
        value_fn=lambda d: d.get("roaming"),
    ),
    UniFiCellularSensorDescription(
        key="registration_state",
        translation_key="registration_state",
        icon="mdi:check-network",
        value_fn=lambda d: d.get("registration_state"),
    ),
)

# --- Device-level sensors ---

DEVICE_SENSORS: tuple[UniFiCellularSensorDescription, ...] = (
    UniFiCellularSensorDescription(
        key="connection_state",
        translation_key="connection_state",
        icon="mdi:lan-connect",
        value_fn=lambda d: d.get("mbb_state"),
    ),
    UniFiCellularSensorDescription(
        key="mbb_mode",
        translation_key="mbb_mode",
        icon="mdi:swap-horizontal",
        value_fn=lambda d: d.get("mbb_mode"),
    ),
    UniFiCellularSensorDescription(
        key="internet",
        translation_key="internet",
        icon="mdi:web",
        value_fn=lambda d: d.get("internet"),
    ),
    UniFiCellularSensorDescription(
        key="uptime",
        translation_key="uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("uptime"),
    ),
    UniFiCellularSensorDescription(
        key="imei",
        translation_key="imei",
        icon="mdi:barcode",
        value_fn=lambda d: d.get("imei"),
    ),
)

# --- IP & Geo sensors ---

IP_GEO_SENSORS: tuple[UniFiCellularSensorDescription, ...] = (
    UniFiCellularSensorDescription(
        key="cellular_ip",
        translation_key="cellular_ip",
        icon="mdi:ip-network",
        value_fn=lambda d: d.get("cellular_ip"),
    ),
    UniFiCellularSensorDescription(
        key="cellular_gateway",
        translation_key="cellular_gateway",
        icon="mdi:ip-network",
        value_fn=lambda d: d.get("cellular_gateway"),
    ),
    UniFiCellularSensorDescription(
        key="mtu",
        translation_key="mtu",
        icon="mdi:resize",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("mtu"),
    ),
    UniFiCellularSensorDescription(
        key="public_ip",
        translation_key="public_ip",
        icon="mdi:earth",
        value_fn=lambda d: d.get("public_ip"),
    ),
    UniFiCellularSensorDescription(
        key="isp",
        translation_key="isp",
        icon="mdi:web",
        value_fn=lambda d: d.get("isp"),
    ),
    UniFiCellularSensorDescription(
        key="esim_eid",
        translation_key="esim_eid",
        icon="mdi:sim",
        value_fn=lambda d: d.get("esim_eid"),
    ),
)

# --- WAN Health sensors (dynamically associated to detected WAN interface) ---

WAN_SENSORS: tuple[UniFiCellularSensorDescription, ...] = (
    UniFiCellularSensorDescription(
        key="wan_availability",
        translation_key="wan_availability",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:check-network",
        value_fn=lambda d: d.get("wan_availability"),
    ),
    UniFiCellularSensorDescription(
        key="wan_latency_avg",
        translation_key="wan_latency_avg",
        native_unit_of_measurement="ms",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer-outline",
        value_fn=lambda d: d.get("wan_latency_avg"),
    ),
    UniFiCellularSensorDescription(
        key="wan_uptime",
        translation_key="wan_uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_fn=lambda d: d.get("wan_uptime"),
    ),
)

# --- Per-SIM sensor templates (instantiated per slot) ---

SIM_SENSOR_TEMPLATES: tuple[UniFiCellularSensorDescription, ...] = (
    UniFiCellularSensorDescription(
        key="state",
        translation_key="sim_state",
        icon="mdi:sim",
        value_fn=lambda d: d.get("display_state"),
    ),
    UniFiCellularSensorDescription(
        key="carrier",
        translation_key="sim_carrier",
        icon="mdi:sim",
        value_fn=lambda d: d.get("spn"),
    ),
    UniFiCellularSensorDescription(
        key="iccid",
        translation_key="sim_iccid",
        icon="mdi:sim",
        value_fn=lambda d: d.get("iccid"),
    ),
    UniFiCellularSensorDescription(
        key="active",
        translation_key="sim_active",
        icon="mdi:sim",
        value_fn=lambda d: d.get("active"),
    ),
    UniFiCellularSensorDescription(
        key="esim",
        translation_key="sim_esim",
        icon="mdi:sim",
        value_fn=lambda d: d.get("esim"),
    ),
    UniFiCellularSensorDescription(
        key="rx_bytes",
        translation_key="sim_rx_bytes",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:download",
        value_fn=lambda d: int(d.get("rxbytes", 0)) if d.get("rxbytes") else None,
    ),
    UniFiCellularSensorDescription(
        key="tx_bytes",
        translation_key="sim_tx_bytes",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:upload",
        value_fn=lambda d: int(d.get("txbytes", 0)) if d.get("txbytes") else None,
    ),
    UniFiCellularSensorDescription(
        key="data_limited",
        translation_key="sim_data_limited",
        icon="mdi:alert-circle",
        value_fn=lambda d: d.get("data_limited"),
    ),
    UniFiCellularSensorDescription(
        key="apn",
        translation_key="sim_apn",
        icon="mdi:access-point-network",
        value_fn=lambda d: (d.get("current_apn") or {}).get("apn"),
    ),
    UniFiCellularSensorDescription(
        key="asn",
        translation_key="sim_asn",
        icon="mdi:earth",
        value_fn=lambda d: d.get("asn"),
    ),
)

# All non-SIM, non-WAN sensors combined
ALL_SENSORS = SIGNAL_SENSORS + RADIO_SENSORS + DEVICE_SENSORS + IP_GEO_SENSORS
