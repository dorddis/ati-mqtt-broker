# AMR Vendor Integration Guide
## How AMR Vendors Connect to External MQTT Brokers

This guide explains how AMR (Autonomous Mobile Robot) vendors like Hi-tech typically integrate with external MQTT brokers from their perspective.

---

## Understanding AMR System Architecture

### Typical AMR System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      AMR VENDOR SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐         ┌──────────────┐                   │
│  │   Robot    │         │    Fleet     │                    │
│  │ Onboard    │◄───────►│  Management  │                    │
│  │  Computer  │ WiFi/5G │   System     │                    │
│  └────────────┘         └──────────────┘                    │
│       │                        │                             │
│       │ ROS/Internal          │ Configuration                │
│       │                        │                             │
│  ┌────▼───────┐         ┌─────▼────────┐                   │
│  │   Sensor   │         │    MQTT      │                    │
│  │   Data     │────────►│   Bridge     │────────►           │
│  │ (Lidar,    │         │   Service    │         │          │
│  │  IMU, etc) │         └──────────────┘         │          │
│  └────────────┘                                   │          │
│                                                    │          │
└────────────────────────────────────────────────────┼──────────┘
                                                     │
                                         ┌───────────▼──────────┐
                                         │  EXTERNAL MQTT       │
                                         │  BROKER (HiveMQ)     │
                                         └──────────────────────┘
```

### Key Points:

1. **Robot Onboard Computer** - Runs Robot Operating System (ROS/ROS2) with sensors and localization
2. **Fleet Management System** - Centralized control, mission dispatch, monitoring (optional for simple setups)
3. **MQTT Bridge Service** - Converts internal robot data to MQTT messages
4. **External MQTT Broker** - Your HiveMQ Cloud instance

---

## How AMR Vendors Send Data to MQTT

AMR vendors have **several options** for sending data to your MQTT broker:

### Option 1: ROS-MQTT Bridge Package (Most Common for ROS-based AMRs)

**If their AMRs run ROS/ROS2** (very common), they would:

1. **Install MQTT client package**:
   ```bash
   # For ROS2
   sudo apt install ros-humble-mqtt-client

   # Or use Python
   pip install paho-mqtt
   ```

2. **Create configuration file** (`config/mqtt_bridge.yaml`):
   ```yaml
   # MQTT Broker Configuration
   broker:
     host: "0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud"
     port: 8883
     user: "hitech-test"
     pass: "HitechAMR@2025"
     tls:
       enabled: true
       ca_certificate: ""  # Optional if using public CA

   client:
     id: "hitech-amr-001"  # Unique per robot
     keep_alive_interval: 60

   # Map ROS topics to MQTT topics
   bridge:
     ros2mqtt:
       - ros_topic: "/robot/pose"           # Internal ROS topic
         mqtt_topic: "hitech/amr/hitech-amr-001/position"
         msg_type: "geometry_msgs/PoseStamped"
       - ros_topic: "/robot/battery"
         mqtt_topic: "hitech/amr/hitech-amr-001/battery"
         msg_type: "sensor_msgs/BatteryState"
   ```

3. **Launch the bridge**:
   ```bash
   ros2 run mqtt_client mqtt_client --ros-args --params-file config/mqtt_bridge.yaml
   ```

**Advantages:**
- No custom code needed
- Well-tested packages available
- Easy to configure via YAML files
- Supports automatic reconnection

---

### Option 2: Custom Python Script (Simple Integration)

If they want **simple integration** or don't use ROS, they'd write a Python script:

**Where it runs:** On each robot's onboard computer or on a central gateway server

**Example structure:**

```python
#!/usr/bin/env python3
"""
Hi-tech AMR MQTT Publisher
Runs on each AMR to publish position data to external broker
"""
import paho.mqtt.client as mqtt
import json
import time
import ssl

# MQTT Configuration - stored in config file or environment variables
BROKER = "0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "hitech-test"
PASSWORD = "HitechAMR@2025"

# Robot-specific settings
ROBOT_ID = "hitech-amr-001"  # Unique per robot
MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"

def get_robot_position():
    """
    Read position from robot's localization system
    This varies by vendor - could be:
    - Reading from ROS topic
    - Reading from vendor's API
    - Reading from shared memory
    - Reading from internal database
    """
    # Example: Read from robot's internal system
    position = read_from_robot_api()  # Vendor-specific
    return position

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to {BROKER}")
    else:
        print(f"Connection failed: {rc}")

def main():
    # Setup MQTT client
    client = mqtt.Client(client_id=ROBOT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.on_connect = on_connect

    # Connect to broker
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    # Publish position data continuously
    while True:
        # Get current position from robot's system
        x, y, battery = get_robot_position()

        # Create message in your specified format
        message = {
            "device_id": ROBOT_ID,
            "mac_address": MAC_ADDRESS,
            "timestamp": int(time.time() * 1000),
            "position": {"x": x, "y": y, "z": 0.0},
            "battery": battery,
            "status": "moving",
            "speed": 500,
            "sector_id": 1
        }

        # Publish to your topic structure
        topic = f"hitech/amr/{ROBOT_ID}/position"
        client.publish(topic, json.dumps(message), qos=1)

        # Send updates at 10 Hz (every 100ms)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
```

**Advantages:**
- Full control over data format
- Easy to understand and modify
- No ROS dependency

---

### Option 3: Fleet Management System Integration (Enterprise)

If Hi-tech has a **centralized fleet management system**:

```
┌────────────┐         ┌──────────────┐         ┌──────────────┐
│  Robot 1   │────────►│              │         │              │
├────────────┤ Internal│    Fleet     │  MQTT   │   HiveMQ     │
│  Robot 2   │────────►│  Management  │────────►│    Cloud     │
├────────────┤ Protocol│    System    │ Bridge  │              │
│  Robot 3   │────────►│              │         │              │
└────────────┘         └──────────────┘         └──────────────┘
```

The fleet system would:
1. Collect data from all robots via their internal protocol
2. Aggregate and transform data
3. Publish to your MQTT broker using a single bridge service

**Advantages:**
- Centralized configuration
- Better for large fleets (10+ robots)
- Can implement business logic before publishing

---

## Configuration Storage Methods

AMR vendors typically store MQTT configuration in:

### 1. Configuration Files (Most Common)

**Location on robot's computer:**
```
/etc/amr/mqtt_config.yaml          # System-wide config
/opt/hitech/config/broker.conf     # Application config
~/robot_config/mqtt_settings.json  # User config
```

**Example config file:**
```yaml
# /etc/amr/mqtt_config.yaml
mqtt:
  broker:
    host: "0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud"
    port: 8883
    use_tls: true
  credentials:
    username: "hitech-test"
    password: "HitechAMR@2025"
  topics:
    position: "hitech/amr/{robot_id}/position"
    battery: "hitech/amr/{robot_id}/battery"
    status: "hitech/amr/{robot_id}/status"
  robot:
    id: "hitech-amr-001"
    mac_address: "XX:XX:XX:XX:XX:XX"
  publish:
    frequency_hz: 10
    qos: 1
```

### 2. Environment Variables

```bash
# /etc/environment or systemd service file
MQTT_BROKER_HOST=0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud
MQTT_BROKER_PORT=8883
MQTT_USERNAME=hitech-test
MQTT_PASSWORD=HitechAMR@2025
MQTT_USE_TLS=true
ROBOT_ID=hitech-amr-001
```

### 3. Web-based Configuration UI

Many modern AMRs have a **web interface** where operators can configure MQTT settings:

```
http://robot-001.local:8080/settings/mqtt

┌─────────────────────────────────────────┐
│         MQTT Broker Configuration       │
├─────────────────────────────────────────┤
│                                         │
│  Broker Address: [________________]    │
│  Port: [8883]  □ Use SSL/TLS          │
│  Username: [________________]          │
│  Password: [****************]          │
│                                         │
│  Topic Prefix: [hitech/amr/]          │
│  Robot ID: [hitech-amr-001]           │
│                                         │
│  Update Rate: [10] Hz                  │
│                                         │
│  [Test Connection]  [Save Changes]     │
└─────────────────────────────────────────┘
```

### 4. Database Configuration (Fleet Systems)

Centralized fleet management systems often store configuration in a database:

```sql
-- fleet_management_db.robots table
CREATE TABLE robot_mqtt_config (
    robot_id VARCHAR(50) PRIMARY KEY,
    broker_host VARCHAR(255),
    broker_port INT,
    username VARCHAR(100),
    password_encrypted VARCHAR(255),
    topic_template VARCHAR(255),
    publish_frequency_hz FLOAT,
    enabled BOOLEAN
);
```

---

## Data They Need to Provide

For Hi-tech to integrate with your HiveMQ broker, share:

### Connection Details
```
Broker Host: 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud
Port: 8883 (MQTT over TLS)
Username: hitech-test
Password: HitechAMR@2025
Protocol: MQTT v3.1.1 or v5.0
TLS Required: Yes
```

### Topic Structure
```
Position updates: hitech/amr/{robot_id}/position
Battery status:   hitech/amr/{robot_id}/battery
Robot status:     hitech/amr/{robot_id}/status

Where {robot_id} is replaced with actual robot ID:
  - hitech-amr-001
  - hitech-amr-002
  - hitech-amr-003
  etc.
```

### Message Format (JSON)
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

### Coordinate System
```
Factory Floor Coordinates:
  X Range: [0, 265000] (millimeters or units they use)
  Y Range: [46000, 218000]
  Origin: Bottom-left corner (or specify their convention)

Update Frequency: 10 Hz (10 messages per second)
QoS Level: 1 (at least once delivery)
```

---

## How Their Data Storage Works

### Real-time Data vs Historical Storage

AMR systems typically have **two data layers**:

#### 1. Real-time Data (In-Memory)

**Location:** RAM on robot's onboard computer

- Current position (x, y, theta)
- Current battery level
- Sensor readings (Lidar, IMU, cameras)
- Active mission/task
- Real-time status

**Access:**
- ROS topics (e.g., `/robot/pose`)
- Shared memory
- Local API (HTTP/REST on localhost)

**Retention:** Only current state, no history

#### 2. Historical Data (Persistent Storage)

**Location:** Database or log files

**On the robot:**
```
/var/log/amr/position_history.db  (SQLite)
/var/log/amr/events.log           (text logs)
```

**On fleet server:**
```
PostgreSQL/MySQL database with tables:
- robot_positions (timestamped x,y data)
- robot_events (status changes, errors)
- mission_history (completed tasks)
```

**Purpose:**
- Analytics
- Troubleshooting
- Fleet optimization
- Historical playback

---

## Integration Process from Vendor's Side

When Hi-tech wants to integrate with your MQTT broker:

### Step 1: Requirements Discussion (Done!)
- You provided: broker details, topic structure, message format
- They confirm: their robots can publish at required frequency

### Step 2: Development (Their Side)

**Option A: ROS-based robots**
1. Install `ros-humble-mqtt-client` package
2. Create YAML config file with your broker details
3. Test with one robot
4. Deploy to all robots

**Option B: Custom integration**
1. Write Python/C++ client using Paho MQTT
2. Integrate with their robot's API to read position
3. Test connection to HiveMQ
4. Deploy script to all robots

### Step 3: Testing (Both Sides)

**Their tests:**
- MQTT connection to HiveMQ ✓
- TLS/SSL certificate validation ✓
- Authentication with credentials ✓
- Message publishing at 10 Hz ✓
- Proper JSON format ✓

**Your tests:**
- Bridge receives MQTT messages ✓
- Data transforms to Twinzo format ✓
- Tuggers appear on Twinzo platform ✓
- Smooth animation (not jumping) ✓

### Step 4: Deployment

**Per-robot deployment:**
```bash
# SSH into each robot
ssh operator@hitech-amr-001.local

# Copy configuration
sudo cp mqtt_config.yaml /etc/amr/

# Enable MQTT publisher service
sudo systemctl enable amr-mqtt-publisher
sudo systemctl start amr-mqtt-publisher

# Verify it's running
sudo systemctl status amr-mqtt-publisher
```

**Or centralized push:**
```bash
# Ansible playbook deployment
ansible-playbook -i inventory/robots.yml deploy_mqtt_config.yml
```

### Step 5: Monitoring

They would monitor:
- MQTT connection status
- Message publish success rate
- Network latency
- Any errors/reconnections

---

## Common Integration Challenges & Solutions

### Challenge 1: Firewall / Network Access

**Problem:** Robots on factory WiFi can't reach external broker

**Solution:**
- Open port 8883 (MQTT/TLS) in firewall
- Use VPN or site-to-site tunnel
- Use edge gateway as proxy

### Challenge 2: Coordinate System Mismatch

**Problem:** Robot's internal coordinates don't match factory floor layout

**Solution:**
- Apply affine transformation (rotation, translation, scaling)
- Calibrate robot's map to factory coordinates
- Document coordinate system clearly

### Challenge 3: Authentication per Robot

**Problem:** Each robot needs unique credentials

**Solutions:**

**Option A:** Shared credentials (what you have now)
```
All robots use: hitech-test / HitechAMR@2025
Differentiated by: Client ID and topic name
```

**Option B:** Individual credentials
```
Robot 1: hitech-amr-001 / password1
Robot 2: hitech-amr-002 / password2
Robot 3: hitech-amr-003 / password3
```

### Challenge 4: Update Frequency

**Problem:** Vendor's default is 1 Hz, you need 10 Hz

**Solution:**
- Configure publish frequency in their config file
- Ensure robot's localization runs at ≥10 Hz
- May require changing robot's internal update rate

---

## What to Expect from Hi-tech

After receiving your integration details, they should:

### Week 1-2: Development & Testing
- Set up one test robot with MQTT client
- Test connection to your HiveMQ broker
- Verify message format matches your spec
- Send test data for you to verify on Twinzo

### Week 3: Pilot Deployment
- Deploy to 1-3 robots in their test facility
- Run extended testing (continuous operation)
- Monitor for connection stability
- Fix any issues discovered

### Week 4+: Full Deployment
- Deploy to all robots going to customer
- Create deployment documentation
- Train operators on monitoring
- Provide troubleshooting guide

---

## Documentation to Request from Hi-tech

Ask them to provide:

1. **Architecture Overview**
   - How their MQTT client is implemented
   - Where it runs (onboard each robot vs central server)
   - How they access position data internally

2. **Configuration Guide**
   - Where MQTT settings are stored
   - How to update broker details if needed
   - How to restart MQTT service

3. **Troubleshooting Guide**
   - How to check if MQTT is running
   - Log file locations
   - Common errors and fixes

4. **Contact Information**
   - Technical support contact
   - Escalation procedure if issues arise
   - Remote access method for debugging

---

## Summary: Integration Methods

| Method | Best For | Complexity | Typical Timeline |
|--------|----------|------------|------------------|
| **ROS MQTT Bridge Package** | ROS-based AMRs | Low | 1-2 weeks |
| **Custom Python Script** | Simple integration | Medium | 2-3 weeks |
| **Fleet System Integration** | Large fleets (10+) | High | 4-6 weeks |
| **Vendor SDK/API** | Proprietary systems | Medium | 3-4 weeks |

---

## Next Steps for Hi-tech

Share with them:

1. **This guide** for understanding the integration options
2. **HiveMQ connection details** (already in `config/hivemq_config.json`)
3. **Message format examples** (from your simulator)
4. **Test credentials** to try publishing from their side
5. **Your bridge monitoring** so they can verify data arrives at Twinzo

---

## Questions to Ask Hi-tech

During your call, ask:

1. **"What operating system and software do your robots run?"**
   - (Expecting: Linux + ROS/ROS2 or proprietary system)

2. **"How do you currently access robot position data internally?"**
   - (Helps understand their architecture)

3. **"Do you have experience publishing to external MQTT brokers?"**
   - (Gauge their MQTT expertise)

4. **"Where would you store our MQTT configuration details?"**
   - (Understand their config management)

5. **"What's your typical integration timeline?"**
   - (Set expectations)

6. **"Can you provide us access to test with one robot first?"**
   - (Establish testing process)

7. **"What update frequency can your robots support?"**
   - (Verify 10 Hz is achievable)

8. **"How do you handle authentication and credentials?"**
   - (Security discussion)

---

## Conclusion

Most AMR vendors will use either:
- **ROS MQTT bridge** (if ROS-based) - configuration in YAML files
- **Python/C++ client script** (if custom) - configuration in config files or environment variables
- **Fleet management system** (if enterprise) - configuration in database

The key is providing them clear documentation of:
1. Broker connection details
2. Topic structure
3. Message format
4. Coordinate system
5. Update frequency requirements

With this information, a competent AMR vendor should be able to integrate within 2-4 weeks.
