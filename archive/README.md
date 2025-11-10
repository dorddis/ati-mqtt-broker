# Archive

Deprecated and experimental files preserved for reference.

## Purpose

This directory contains files that are no longer actively used but are preserved for:
- Historical reference
- Potential future recovery
- Understanding project evolution
- Debugging legacy issues

## Recent Cleanup (2025-11-10)

### old_scripts/
Recently archived scripts no longer needed:
- amr_simulator_hivemq.py - Old HiveMQ simulator (replaced by audit feed bridge)
- hivemq_to_twinzo_bridge.py - Old HiveMQ bridge (replaced by audit feed bridge)
- place_tuggers.py - Old testing script
- test_hivemq_connection.py - Old HiveMQ connection testing

### old_logs/
Old exploration and testing logs:
- ati_data_received.log, ati_messages.log, ati_topic_discovery.log - ATI exploration logs
- audit_feed_bridge.log - Old bridge logs (active logs moved to /logs/ directory)

### analysis/
One-time analysis files:
- analyze_coordinates.js - Coordinate range analysis script
- tugger_paths.txt - Tugger movement path analysis output

## Structure

### configs/
Old MQTT broker configurations:
- mosquitto_windows.conf - Windows-specific Mosquitto config
- mosquitto_local.conf - Local development config
- local_mqtt.conf - Alternative local config
- test_mqtt.conf - Test environment config
- ati_broker.conf - ATI-specific broker config
- websocket_mqtt.conf - WebSocket-focused config
- websocket_only.conf - WebSocket-only config

### experimental/
Experimental scripts and proof-of-concepts:
- minimal_test_client.py - Minimal MQTT test client

### reports/
Old reports and exports:
- tvs_focused_report_20250923_130124.json - TVS verification report
- email_draft.txt - Email communications
- WHATSAPP_MESSAGE.txt - WhatsApp messages

## Important Notes

- **Do not delete** files from archive without good reason
- Files here may contain useful configuration examples
- Check archive before recreating solutions to old problems
- Document why files were archived (in commit messages)

## Recovery

To recover an archived file:
1. Copy from archive/ to appropriate location
2. Update any paths or references
3. Test thoroughly before using in production
4. Document why file was recovered
