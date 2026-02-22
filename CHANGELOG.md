# Changelog

## v0.2.1

- **Dynamic WAN interface detection**: the integration now automatically detects which WAN interface (WAN, WAN2, WAN3...) is associated with the cellular device, instead of hardcoding WAN3
- WAN health sensors (availability, latency, uptime) are dynamically named based on the detected interface

## v0.2.0

- Add reconfigure step: change API key or connection settings without removing the integration
- Fix API key instructions: now "Integrations > Create New API Key"
- Add GitHub Actions CI (HACS + hassfest validation)

## v0.1.0

- Initial release
- 45+ sensors: signal quality (RSRP, RSRQ, RSSI, SNR), radio info, per-SIM metrics, IP/geo, WAN health
- Multi-SIM and eSIM support
- Config flow with SSL toggle and site selection
