# Configuration

All configuration files for the Twinzo Mock system.

## Structure

### mosquitto/
MQTT broker configuration (production):
- mosquitto.conf - Main Mosquitto configuration
- data/ - MQTT persistence data (gitignored)
- log/ - MQTT broker logs (gitignored)

This is the primary MQTT configuration used by docker-compose.yml.

### mappings/
Data mapping configurations:
- device_mapping.json - Device ID to name mappings
- field_mapping.json - Field name transformation rules
- topic_mapping.json - MQTT topic routing configuration

Used by the bridge to transform data from MQTT format to Twinzo API format.

### environments/
Environment-specific configurations:
- local.env.example - Example local environment variables
- production.env.example - Example production environment variables

Copy .example files to create your actual .env files (not committed to git).

## Configuration Files

### mosquitto.conf
Main MQTT broker configuration. Key settings:
- Port 1883 for MQTT
- Port 9001 for WebSockets
- Anonymous access or ACL-based authentication
- Persistence settings

### device_mapping.json
Maps device MAC addresses or IDs to human-readable names:
```json
{
  "AA:BB:CC:DD:EE:FF": "tugger-01",
  "11:22:33:44:55:66": "tugger-02"
}
```

### field_mapping.json
Transforms field names between systems:
```json
{
  "source_field": "target_field",
  "battery_level": "Battery"
}
```

### topic_mapping.json
Routes MQTT topics to specific handlers:
```json
{
  "ati_fm/sherpa/status": "amr_location",
  "tvs/robot/#": "tvs_integration"
}
```

## Usage

Configuration files are referenced by:
- docker-compose.yml (mosquitto config)
- bridge/bridge.py (mapping files)
- Publisher and subscriber scripts

See the root README.md and CLAUDE.md for environment variable configuration.
