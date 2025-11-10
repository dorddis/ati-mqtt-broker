# ATI Audit Feed Exploration Files

This directory contains files used during the exploration and development phase of the ATI audit feed integration.

## Archived Files (2025-11-10)

### Exploration Scripts
- `shared_ati_code.js` - Pavan's reference implementation for connecting to audit feed
- `comprehensive_mqtt_verification.py` - Python MQTT verification script
- `discover_all_ati_topics.py` - Topic discovery tool
- `listen_to_ati_mqtt.py` - MQTT listener for testing
- `check_ati_data.py` - Data format verification
- `test_mqtt_definitively.py` - Connection testing

### Development Versions
- `bridge_audit_feed.py` - Python version of the bridge (replaced by JS version)

## Why Archived?

These files were used to:
1. Explore the ATI audit feed MQTT structure
2. Discover active AMRs and their data formats
3. Test different connection approaches (Python vs JavaScript)
4. Verify credentials and permissions

The production bridge (`src/bridge/bridge_audit_feed.js`) successfully implements the functionality discovered through these exploration scripts.

## Production Bridge

The live production bridge is at: `src/bridge/bridge_audit_feed.js`

It streams data from 7 active AMRs to Twinzo Old Plant (Sector 2).
