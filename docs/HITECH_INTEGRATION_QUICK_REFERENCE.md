# Hi-tech AMR Integration - Quick Reference

**Integration Method:** MQTT over TLS
**Target:** Twinzo RTLS Platform
**Date:** November 2025

---

## 1. Connection Details

```
Broker: 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud
Port: 8883 (MQTT with TLS/SSL)
Protocol: MQTT v3.1.1 or v5.0
Username: hitech-test
Password: HitechAMR@2025
TLS Required: Yes (use standard CA certificates)
```

**Test connection:**
```bash
mosquitto_pub -h 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud \
  -p 8883 -u hitech-test -P "HitechAMR@2025" \
  --capath /etc/ssl/certs/ \
  -t "test/hello" -m "test message"
```

---

## 2. Topic Structure

```
hitech/amr/{robot_id}/position
hitech/amr/{robot_id}/battery
hitech/amr/{robot_id}/status
```

**Examples:**
- `hitech/amr/hitech-amr-001/position`
- `hitech/amr/hitech-amr-002/position`
- `hitech/amr/hitech-amr-003/position`

**Wildcards for testing:**
- Subscribe to all robots: `hitech/amr/+/position`
- Subscribe to everything: `hitech/amr/#`

---

## 3. Message Format (JSON)

**Position Update:**
```json
{
  "device_id": "hitech-amr-001",
  "mac_address": "XX:XX:XX:XX:XX:XX",
  "timestamp": 1730000000000,
  "position": {
    "x": 150000,
    "y": 150000,
    "z": 0
  },
  "battery": 85,
  "status": "moving",
  "speed": 500,
  "sector_id": 1
}
```

**Field Descriptions:**
- `device_id`: Unique robot identifier (string)
- `mac_address`: Robot's MAC address (string, format: XX:XX:XX:XX:XX:XX)
- `timestamp`: Unix timestamp in milliseconds (integer)
- `position.x`: X coordinate in millimeters (float)
- `position.y`: Y coordinate in millimeters (float)
- `position.z`: Z coordinate, usually 0 (float)
- `battery`: Battery percentage 0-100 (integer)
- `status`: "moving", "idle", "charging", etc. (string)
- `speed`: Speed in mm/s (integer)
- `sector_id`: Factory sector/zone ID (integer)

---

## 4. Coordinate System

```
Factory Floor Bounds:
  X: [0, 265,000] millimeters (0 to 265 meters)
  Y: [46,000, 218,000] millimeters (46 to 218 meters)

Origin: Bottom-left corner
Units: Millimeters (mm)
Coordinate System: Cartesian (X-right, Y-up)
```

**Important:** If your robot's coordinate system differs:
- Provide us with transformation parameters (rotation, offset, scaling)
- We can handle coordinate transformation on our side

---

## 5. Update Frequency

```
Recommended: 10 Hz (10 updates per second)
Minimum: 5 Hz (5 updates per second)
Interval: 100ms between messages
QoS Level: 1 (at least once delivery)
Retain: false
```

**Why 10 Hz?**
- Enables smooth fluid animation on Twinzo platform
- Prevents jumpy/jarred movement visualization
- Industry standard for RTLS systems

---

## 6. Implementation Options

### Option A: Python Script (Recommended for Quick Start)

```python
#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
import ssl

# Configuration
BROKER = "0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "hitech-test"
PASSWORD = "HitechAMR@2025"
ROBOT_ID = "hitech-amr-001"  # Change per robot

# Setup
client = mqtt.Client(client_id=ROBOT_ID)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

# Publish loop (10 Hz)
while True:
    x, y, battery = get_robot_position()  # Your function

    message = {
        "device_id": ROBOT_ID,
        "mac_address": "XX:XX:XX:XX:XX:XX",
        "timestamp": int(time.time() * 1000),
        "position": {"x": x, "y": y, "z": 0},
        "battery": battery,
        "status": "moving",
        "speed": 500,
        "sector_id": 1
    }

    topic = f"hitech/amr/{ROBOT_ID}/position"
    client.publish(topic, json.dumps(message), qos=1)

    time.sleep(0.1)  # 10 Hz
```

**Install dependencies:**
```bash
pip3 install paho-mqtt
```

### Option B: ROS MQTT Bridge (If Using ROS)

**Install:**
```bash
sudo apt install ros-humble-mqtt-client
```

**Config file** (`config/mqtt_bridge.yaml`):
```yaml
broker:
  host: "0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud"
  port: 8883
  user: "hitech-test"
  pass: "HitechAMR@2025"
  tls:
    enabled: true

client:
  id: "hitech-amr-001"
  keep_alive_interval: 60

bridge:
  ros2mqtt:
    - ros_topic: "/robot/pose"
      mqtt_topic: "hitech/amr/hitech-amr-001/position"
      msg_type: "geometry_msgs/PoseStamped"
```

**Launch:**
```bash
ros2 run mqtt_client mqtt_client --ros-args --params-file config/mqtt_bridge.yaml
```

---

## 7. Testing Checklist

- [ ] MQTT client can connect to broker
- [ ] TLS/SSL certificate validation passes
- [ ] Authentication succeeds with provided credentials
- [ ] Messages publish to correct topics
- [ ] JSON format matches specification
- [ ] Timestamp is in milliseconds (not seconds!)
- [ ] Coordinates are in millimeters (not meters!)
- [ ] Update frequency is 10 Hz (100ms intervals)
- [ ] QoS level is set to 1
- [ ] Client reconnects automatically on disconnect

---

## 8. Verification

**Test from your side:**
```bash
# Subscribe to see published messages
mosquitto_sub -h 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud \
  -p 8883 -u hitech-test -P "HitechAMR@2025" \
  --capath /etc/ssl/certs/ \
  -t "hitech/amr/+/position" -v
```

**What you should see:**
```
hitech/amr/hitech-amr-001/position {"device_id":"hitech-amr-001","timestamp":1730000000000,...}
hitech/amr/hitech-amr-001/position {"device_id":"hitech-amr-001","timestamp":1730000000100,...}
hitech/amr/hitech-amr-001/position {"device_id":"hitech-amr-001","timestamp":1730000000200,...}
```

**We verify:**
- Our bridge receives your messages
- Data transforms correctly to Twinzo format
- Tuggers appear on Twinzo platform
- Movement is smooth and fluid

---

## 9. Robot ID Mapping

**Your IDs** → **Twinzo Tugger IDs:**

| Your Robot ID | Twinzo Tugger | MAC Address (Example) |
|---------------|---------------|----------------------|
| hitech-amr-001 | tugger-01 | f4:7b:09:0e:04:1b |
| hitech-amr-002 | tugger-02 | 10:3d:1c:66:67:55 |
| hitech-amr-003 | tugger-03 | f4:4e:e3:f6:c7:91 |
| hitech-amr-004 | tugger-04 | ec:2e:98:4a:7c:f7 |

**Note:** Our bridge handles the mapping. You publish with your IDs, we transform to Twinzo tugger IDs.

---

## 10. Common Issues & Solutions

### Connection Refused
**Problem:** Can't connect to broker
**Check:**
- Port 8883 is open in your firewall
- Using TLS/SSL (not plain MQTT on port 1883)
- Credentials are correct (case-sensitive!)
- Internet connectivity from robot network

### Authentication Failed
**Problem:** Connection rejected with code 4
**Solution:**
- Verify username: `hitech-test` (exact)
- Verify password: `HitechAMR@2025` (exact, case-sensitive)
- Check for extra spaces in credentials

### Messages Not Received
**Problem:** Publishing succeeds but we don't see messages
**Check:**
- Topic format matches exactly: `hitech/amr/{id}/position`
- No typos in topic name
- QoS is set to 1 (not 0)
- JSON is valid (test with jsonlint.com)

### Coordinates Off
**Problem:** Robot appears in wrong location on Twinzo
**Solution:**
- Verify units are millimeters (not meters!)
- Check coordinate system matches (X-right, Y-up)
- Provide us coordinate transformation if needed

### Timestamp Errors
**Problem:** Twinzo shows wrong times
**Solution:**
- Use milliseconds, not seconds: `int(time.time() * 1000)`
- Ensure robot's system clock is synchronized (NTP)

---

## 11. Support & Contact

**Technical Questions:**
- Email: [Your email]
- Phone: [Your phone]
- Available: [Your hours]

**Integration Status:**
- Real-time monitoring: [Monitoring dashboard URL if available]
- Test environment: [If you set up test Twinzo instance]

**Escalation:**
- Critical issues: [Emergency contact]

---

## 12. Next Steps

1. **Week 1-2:** Development & Initial Testing
   - Set up MQTT client on one test robot
   - Test connection to our HiveMQ broker
   - Verify message format
   - Send us test data to validate

2. **Week 3:** Pilot Deployment
   - Deploy to 1-3 robots
   - Extended testing (24+ hours)
   - Monitor stability
   - Fix any issues

3. **Week 4+:** Full Deployment
   - Deploy to all robots
   - Production monitoring
   - Documentation handover
   - Operator training

---

## 13. Required Deliverables from Hi-tech

Please provide:

1. **Architecture document** - How your MQTT integration works
2. **Configuration guide** - Where settings are stored, how to update
3. **Troubleshooting guide** - Common issues and fixes
4. **Test report** - Results from pilot deployment
5. **Support contact** - Who to contact for issues
6. **Deployment timeline** - When robots will go live

---

## Quick Command Reference

```bash
# Install Python MQTT client
pip3 install paho-mqtt

# Test publish
mosquitto_pub -h 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud \
  -p 8883 -u hitech-test -P "HitechAMR@2025" \
  --capath /etc/ssl/certs/ \
  -t "hitech/amr/test/position" \
  -m '{"device_id":"test","timestamp":1730000000000,"position":{"x":150000,"y":150000,"z":0},"battery":85,"status":"moving","speed":500,"sector_id":1}'

# Test subscribe
mosquitto_sub -h 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud \
  -p 8883 -u hitech-test -P "HitechAMR@2025" \
  --capath /etc/ssl/certs/ \
  -t "hitech/amr/#" -v
```

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Contact:** [Your Name] - [Your Email] - [Your Phone]
