# ATI Fleet Manager → Twinzo Integration

**Integration Status: TESTED & OPERATIONAL** - 36+ messages successfully processed

## Implementation Requirements

1. Install Python MQTT client: `pip install paho-mqtt`
2. Integrate the provided publisher code
3. Configure connection details (provided by Factories of Future)
4. Deploy to production environment

**Integration Architecture:** Factories of Future manages the MQTT broker infrastructure, tunnel connectivity, and Twinzo API forwarding.

## Integration Code

```python
import paho.mqtt.client as mqtt
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ATITwinzoPublisher:
    def __init__(self, mqtt_host, mqtt_port):
        self.host = mqtt_host
        self.port = mqtt_port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.connected = False

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        self.connected = (rc == 0)
        status = "SUCCESS" if rc == 0 else "FAILED"
        logger.info(f"{status} MQTT connection: {rc}")

    def connect(self):
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

        timeout = 10
        while not self.connected and timeout > 0:
            time.sleep(0.1)
            timeout -= 0.1
        return self.connected

    def publish_sherpa(self, sherpa_data):
        if not self.connected:
            return False

        # Add timestamp if missing
        if "timestamp" not in sherpa_data:
            sherpa_data["timestamp"] = int(time.time() * 1000)

        topic = f"ati/amr/{sherpa_data['sherpa_name']}/status"
        message = json.dumps(sherpa_data)
        result = self.client.publish(topic, message, qos=1)

        success = result.rc == 0
        if success:
            logger.info(f"Published {sherpa_data['sherpa_name']} status")
        return success

    def disconnect(self):
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()

# Usage Example
def main():
    # UPDATE THESE WITH OUR PROVIDED DETAILS
    MQTT_HOST = "YOUR_NGROK_HOST"  # e.g., "0.tcp.ngrok.io"
    MQTT_PORT = YOUR_NGROK_PORT    # e.g., 12345

    publisher = ATITwinzoPublisher(MQTT_HOST, MQTT_PORT)

    if not publisher.connect():
        logger.error("Connection failed")
        return

    # Your sherpa data from ATI Fleet Manager
    sherpa_data = {
        "sherpa_name": "val-sherpa-01",
        "mode": "Fleet",
        "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
        "battery_status": 82.5,
        "trip_id": 1234
    }

    # Publish
    success = publisher.publish_sherpa(sherpa_data)
    result = "Success" if success else "Failed"
    logger.info(f"Publication result: {result}")

    publisher.disconnect()

if __name__ == "__main__":
    main()
```

## Data Format

```python
{
    "sherpa_name": "val-sherpa-01",        # Required
    "mode": "Fleet",                       # Required
    "pose": [X, Y, Z, roll, pitch, yaw],  # Required
    "battery_status": 82.5,               # Required
    "trip_id": 1234,                      # Optional
    "error": "",                          # Optional
    "disabled": false                     # Optional
}
```

## Integration Steps

1. **Test Connection**: Run the code with our connection details
2. **Replace Data Source**: Connect to your ATI Fleet Manager data
3. **Continuous Publishing**: Add to your main loop

```python
# In your ATI system loop:
while True:
    sherpa_data = get_current_sherpa_data()  # Your function
    publisher.publish_sherpa(sherpa_data)
    time.sleep(5)  # Every 5 seconds (tested frequency)
```

## Checklist

- [ ] `paho-mqtt` installed
- [ ] Connection details received from us
- [ ] Test script works
- [ ] Connected to ATI Fleet Manager data
- [ ] Ready for production

**Contact Factories of Future when implementation checklist is complete for production deployment coordination.**

---

**Tested with 3 robots at 5-second intervals. Verified working.**

---

*Provided by Factories of Future - Advanced Manufacturing Integration Solutions* 