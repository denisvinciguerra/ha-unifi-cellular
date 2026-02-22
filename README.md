# 📡 UniFi Cellular - Home Assistant Integration

A Home Assistant custom integration for **UniFi 5G Max Outdoor** (and other UniFi MBB/cellular devices).

Exposes cellular signal metrics, radio info, SIM status, data usage, and WAN health as HA sensor entities.

---

## ✨ Features

- 📶 **Signal Quality** — RSRP, RSRQ, RSSI, SNR, signal strength percentage with quality ratings
- 📻 **Radio Info** — RAT (LTE/5G/5G UW), band, channel, cell ID, operator, MCC/MNC, roaming status
- 💳 **Multi-SIM Support** — Per-SIM sensors for each slot (physical SIM + eSIM), carrier, ICCID, data usage, APN
- 📊 **Data Usage** — RX/TX bytes per SIM with `total_increasing` state class for proper HA tracking
- 🌐 **IP & Geo** — Cellular IP, gateway, MTU, public IP, ISP
- 🔄 **WAN Health** — Automatic detection of the WAN interface associated with the cellular device (WAN, WAN2, WAN3...), with availability, latency, and uptime sensors
- 🔧 **Device Info** — Connection state, MBB mode, uptime, IMEI, eSIM EID

---

## 📋 Requirements

- UniFi Dream Machine (UDM, UDM Pro, UDM SE) or UniFi Cloud Gateway
- UniFi 5G Max Outdoor (or any UniFi MBB device, type `umbb`)
- API Key (not username/password)

---

## 📦 Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the **3 dots** menu (top right) → **Custom repositories**
4. Add this repository URL: `https://github.com/denisvinciguerra/ha-unifi-cellular`
5. Category: **Integration**
6. Click **Add**, then install **UniFi Cellular**
7. Restart Home Assistant

### Manual

1. Copy the `custom_components/unifi_cellular` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

---

## ⚙️ Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **UniFi Cellular**
3. Enter:
   - **Controller IP** — Your UDM IP address (e.g., `192.168.1.1`)
   - **API Key** — Generate one in UniFi OS (see below)
   - **Site name** — Usually `default`
   - **Verify SSL** — Leave unchecked for self-signed certificates (typical for local UDM)

> 💡 Need to change the API key later? Use the **Reconfigure** option in the integration settings — no need to remove and re-add the integration.

---

## 🔑 API Authentication

This integration uses **API Key** authentication (`X-API-Key` header), not username/password login.

To create an API key:

1. Open your UniFi OS console (e.g., `https://192.168.1.1`)
2. Go to **Integrations**
3. Select **Create New API Key**
4. Copy the key and use it during integration setup

> ⚠️ Cloud SSO accounts with cookie-based authentication cannot use POST endpoints. API Key auth is the recommended method.

---

## 📊 Sensors

All sensors are grouped under a single device (e.g., "U5G Max Outdoor") in Home Assistant.

### 📶 Signal Quality

| Sensor | Unit | Description |
|--------|------|-------------|
| RSRP | dBm | Reference Signal Received Power |
| RSRQ | dB | Reference Signal Received Quality |
| RSSI | dBm | Received Signal Strength Indicator |
| SNR | dB | Signal-to-Noise Ratio |
| Signal strength | % | Signal strength percentage |
| Signal level | — | Signal level (0-5) |

> RSRP, RSRQ and SNR include a `rating` attribute (Excellent / Good / Fair / Poor).

### 📻 Radio

| Sensor | Description |
|--------|-------------|
| Radio access technology | LTE, 5G NR, etc. |
| Active RAT mode | Currently active radio mode |
| 5G Ultra Wideband | 5G UW status |
| Band | e.g., eutran-3, eutran-28 |
| Channel / RX channel / TX channel | EARFCN values |
| Cell ID | Serving cell identifier |
| Operator | Network operator name |
| MCC / MNC / Country | Mobile network identifiers |
| Roaming | Roaming status |
| Registration state | Network registration state |

### 💳 Per-SIM (one set per SIM slot)

| Sensor | Description |
|--------|-------------|
| State | operational, esim-ready-to-activate, etc. |
| Carrier | e.g., Bouygues Telecom |
| ICCID | SIM card identifier |
| Active / eSIM | Status flags |
| Data received / Data sent | Cumulative bytes (`total_increasing`) |
| Data limited | Data cap status |
| APN | Current access point name |
| ASN | Autonomous system number |

### 🔄 WAN Health (auto-detected)

The integration automatically detects which WAN interface is associated with the cellular device by matching the cellular IP against the gateway's WAN interfaces. Sensors are named accordingly (e.g., "WAN3 Availability" if the device is on WAN3).

| Sensor | Unit | Description |
|--------|------|-------------|
| Availability | % | Uptime percentage |
| Latency Avg | ms | Average latency |
| Uptime | s | Current uptime |

### 🔧 Device

| Sensor | Description |
|--------|-------------|
| Connection state | MBB connection state |
| MBB mode | Failover / primary mode |
| Internet | Internet connectivity status |
| Uptime | Device uptime |
| IMEI | Device IMEI |
| eSIM EID | eSIM identifier |

### 🌐 IP & Geo

| Sensor | Description |
|--------|-------------|
| Cellular IP | IPv4 address on the cellular link |
| Cellular gateway | Gateway IP |
| MTU | Maximum transmission unit |
| Public IP | Public-facing IP address |
| ISP | Internet service provider |

---

## 🛠️ Development

This integration was vibe-coded with [Claude Code](https://claude.ai/).

Built with standard Home Assistant custom integration patterns: `DataUpdateCoordinator` for polling, `ConfigFlow` for UI setup, `CoordinatorEntity` for sensors.

---

## 📄 License

MIT
