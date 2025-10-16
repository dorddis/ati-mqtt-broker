# Tests

All test files organized by category and integration type.

## Test Structure

### unit/
Unit tests for individual components (planned)
- test_publisher.py
- test_bridge.py

### integration/
End-to-end integration tests:
- test_working_localization.py - Tests working Twinzo localization
- test_docker_bridge.py - Docker bridge integration
- test_final_format.py - Final data format validation
- test_complete_mqtt_flow.py - Complete MQTT flow test

### mqtt/
MQTT broker and connection tests:
- test_mqtt_client.py
- test_simple_mqtt_working.py
- test_local_mqtt.py
- simple_mqtt_test.py
- quick_mqtt_test.py
- test_subscriber.py

### tvs/
TVS MQTT broker integration tests:
- tvs_comprehensive_verification.py
- tvs_focused_verification.py
- tvs_quick_check.py
- tvs_unique_client_test.py
- tvs_exhaustive_topic_test.py
- tvs_publisher_test.py
- tvs_comprehensive_test.py
- tvs_extensive_data_test.py
- data_structure_comparison.py

### ati/
ATI integration tests:
- test_ati_integration.py
- diagnose_websocket.py

### render/
Render.com deployment tests:
- test_render_connection.py
- test_http_only.py
- test_mqtt_websocket_fixed.py
- test_simple_mqtt.py

## Running Tests

Always use `python -X utf8` on Windows to avoid Unicode issues:

```bash
# Run specific test
python -X utf8 tests/integration/test_working_localization.py

# Run MQTT tests
python -X utf8 tests/mqtt/quick_mqtt_test.py

# Run TVS integration test
python -X utf8 tests/tvs/tvs_quick_check.py
```
