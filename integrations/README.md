# Integrations

External system integrations for TVS, ATI, and Twinzo platforms.

## Structure

### tvs/
TVS MQTT broker integration:
- tvs_real_data_subscriber.py - Subscribe to real TVS MQTT data
- tvs_working_client.py - Working TVS client implementation
- tvs_robotspace_subscriber.py - Robotspace-specific subscriber

Connect to TVS broker to capture real AMR data and analyze data structures.
See docs/integrations/tvs/ for detailed documentation.

### ati/
ATI platform integration:
- setup_ati_broker.py - Setup ATI MQTT broker
- simulate_ati_publisher.py - Simulate ATI data publisher
- websocket_ati_publisher.py - WebSocket-based ATI publisher
- websocket_bridge_subscriber.py - WebSocket bridge subscriber
- websocket_bridge_to_twinzo.py - Bridge ATI data to Twinzo

Integration with ATI platform for real-time AMR data.
See docs/integrations/ati/ for detailed documentation.

### twinzo/
Twinzo API utilities:
- twinzo_test_client.py - Test Twinzo API integration

Tools for testing and validating Twinzo API integration.

## Usage

Always use `python -X utf8` on Windows:

```bash
# Connect to TVS broker
python -X utf8 integrations/tvs/tvs_real_data_subscriber.py

# Test ATI integration
python -X utf8 integrations/ati/simulate_ati_publisher.py

# Test Twinzo API
python -X utf8 integrations/twinzo/twinzo_test_client.py
```

## Configuration

Each integration requires specific credentials and configuration:
- TVS: Credentials in environment variables or config files
- ATI: MQTT broker configuration and topics
- Twinzo: OAuth credentials and API keys

See the respective documentation in docs/integrations/ for details.
