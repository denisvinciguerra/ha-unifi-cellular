# UniFi Cellular - Home Assistant Integration

A Home Assistant custom integration for **UniFi 5G Max Outdoor** (and other UniFi MBB/cellular devices). Exposes cellular signal metrics, radio info, SIM status, data usage, and WAN health as HA sensor entities.

## Features

- **Signal Quality**: RSRP, RSRQ, RSSI, SNR, signal strength percentage with quality ratings
- **Radio Info**: RAT (LTE/5G/5G UW), band, channel, cell ID, operator, MCC/MNC, roaming status
- **Multi-SIM Support**: Per-SIM sensors for each slot (physical SIM + eSIM), carrier, ICCID, data usage, APN
- **Data Usage**: RX/TX bytes per SIM with total_increasing state class for proper HA tracking
- **IP & Geo**: Cellular IP, gateway, MTU, public IP, ISP
- **WAN Health**: WAN3 availability, latency, uptime
- **Device Info**: Connection state, MBB mode, uptime, IMEI, eSIM EID

## Requirements

- UniFi Dream Machine (UDM, UDM Pro, UDM SE) or UniFi Cloud Gateway
- UniFi 5G Max Outdoor (or any UniFi MBB device, type `umbb`)
- API Key (not username/password)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the **3 dots** menu (top right) > **Custom repositories**
4. Add this repository URL: `https://github.com/denisvinciguerra/ha-unifi-cellular`
5. Category: **Integration**
6. Click **Add**, then install **UniFi Cellular**
7. Restart Home Assistant

### Manual

1. Copy the `custom_components/unifi_cellular` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **UniFi Cellular**
3. Enter:
   - **Controller IP**: Your UDM IP address (e.g., `192.168.1.1`)
   - **API Key**: Generate one in UniFi OS: Integrations > Create New API Key
   - **Site name**: Usually `default`
   - **Verify SSL**: Leave unchecked for self-signed certificates (typical for local UDM)

## Sensors

All sensors are grouped under a single device (e.g., "U5G Max Outdoor") in Home Assistant.

### Signal Quality
| Sensor | Unit | Description |
|--------|------|-------------|
| RSRP | dBm | Reference Signal Received Power |
| RSRQ | dB | Reference Signal Received Quality |
| RSSI | dBm | Received Signal Strength Indicator |
| SNR | dB | Signal-to-Noise Ratio |
| Signal strength | % | Signal strength percentage |
| Signal level | - | Signal level (0-5) |

RSRP, RSRQ and SNR include a `rating` attribute (Excellent/Good/Fair/Poor).

### Radio
| Sensor | Description |
|--------|-------------|
| Radio access technology | LTE, 5G NR, etc. |
| Band | e.g., eutran-3, eutran-28 |
| Channel / RX channel / TX channel | EARFCN values |
| Cell ID | Serving cell identifier |
| Operator | Network operator code |
| MCC / MNC / Country | Mobile network identifiers |
| Roaming | Roaming status |

### Per-SIM (one set per SIM slot)
| Sensor | Description |
|--------|-------------|
| State | operational, esim-ready-to-activate, etc. |
| Carrier | e.g., Bouygues Telecom |
| ICCID | SIM card identifier |
| Active / eSIM | Status flags |
| Data received / Data sent | Cumulative bytes (total_increasing) |
| APN | Current APN |

### WAN3 Health
| Sensor | Unit | Description |
|--------|------|-------------|
| WAN3 availability | % | Uptime percentage |
| WAN3 latency | ms | Average latency |
| WAN3 uptime | s | Current uptime |

## API Authentication

This integration uses **API Key** authentication (`X-API-Key` header), not username/password login. To create an API key:

1. Open your UniFi OS console (e.g., `https://192.168.1.1`)
2. Go to **Integrations**
3. Select **Create New API Key**
5. Copy the key and use it during integration setup

> **Note**: Cloud SSO accounts with cookie-based authentication cannot use POST endpoints. API Key auth is the recommended method.

## Development

This integration was vibe-coded with [Claude Code](https://claude.ai/), Built with the standard Home Assistant custom integration patterns: `DataUpdateCoordinator` for polling, `ConfigFlow` for UI setup, `CoordinatorEntity` for sensors.

## License

MIT
