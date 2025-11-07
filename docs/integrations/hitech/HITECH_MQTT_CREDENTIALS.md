
# Hi-tech AMR MQTT Integration \- Credentials & Setup

**Document Purpose:** Share MQTT broker connection details with Hi-tech AMR vendor **Created:** November 4, 2025   
**Target Completion:** November 6, 2025   
**Status:** Ready for Integration

---

## MQTT Broker Connection Details \- Important

### HiveMQ Cloud Serverless

```` ``` ````  
`Broker Host: 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud`  
`Port: 8883 (MQTT over TLS/SSL)`  
`Protocol: MQTT v3.1.1 or v5.0`  
`Security: TLS Required`

`Username: hitech-test`  
`Password: HitechAMR@2025`

`Client ID: Use your robot ID (e.g., hitech-amr-001, hitech-amr-002, etc.)`  
`Keep Alive: 60 seconds`  
`Clean Session: true`  
`QoS Level: 1 (at least once delivery)`  
```` ``` ````

### Quick Connection Test

**Using mosquitto\_pub (Linux/Mac):**

```` ```bash ````  
`mosquitto_pub -h 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud \`  
  `-p 8883 -u hitech-test -P "HitechAMR@2025" \`  
  `--capath /etc/ssl/certs/ \`  
  `-t "hitech/test" -m "Hello from Hi-tech AMR"`  
```` ``` ````

**Using Python:**

```` ```python ````  
`import paho.mqtt.client as mqtt`  
`import ssl`

`client = mqtt.Client(client_id="test-client")`  
`client.username_pw_set("hitech-test", "HitechAMR@2025")`  
`client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)`  
`client.connect("0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud", 8883, 60)`  
`client.publish("hitech/test", "Hello from Hi-tech AMR", qos=1)`  
```` ``` ````

## Topic Structure \- Important

### Position Updates

`Topic: hitech/amr/{robot_id}/position`  
`Example: hitech/amr/hitech-amr-001/position`

### Battery Status (Optional)

`Topic: hitech/amr/{robot_id}/battery`  
`Example: hitech/amr/hitech-amr-001/battery`

### Robot Status (Optional)

`Topic: hitech/amr/{robot_id}/status`  
`Example: hitech/amr/hitech-amr-001/status`

**Note:** Replace `{robot_id}` with your actual robot identifier

## Message Format (JSON) \- Important

### Required Fields

```` ```json ````  
`{`  
  `"device_id": "hitech-amr-001",`  
  `"mac_address": "XX:XX:XX:XX:XX:XX",`  
  `"timestamp": 1730700000000,`  
  `"position": {`  
    `"x": 150000,`  
    `"y": 150000,`  
    `"z": 0`  
  `},`  
  `"battery": 85,`  
  `"status": "moving",`  
  `"speed": 500,`  
  `"sector_id": 1`  
`}`  
```` ``` ````

### 

### Field Specifications

| Field | Type | Description | Example |
| :---- | :---- | :---- | :---- |
| device\_id | string | Unique robot identifier | "hitech-amr-001" |
| mac\_address | string | Robot's MAC address | "f4:7b:09:0e:04:1b" |
| timestamp | integer | Unix time in milliseconds | 1730700000000 |
| position.x | float | X coordinate in millimeters | 150000.0 |
| position.y | float | Y coordinate in millimeters | 150000.0 |
| position.z | float | Z coordinate (usually 0\) | 0.0 |
| battery | integer | Battery percentage (0-100) | 85 |
| status | string | "moving", "idle", "charging" | "moving" |
| speed | integer | Speed in mm/s | 500 |
| sector\_id | integer | Plant/sector ID (see below) | 1 |

## 

## Plant/Sector Configuration

### Plant 4 (Primary \- Already Configured)

Sector ID: 1  
Coordinate Bounds:  
  X: \[0, 265,000\] millimeters (0 to 265 meters)  
  Y: \[46,000, 218,000\] millimeters (46 to 218 meters)  
Status: ACTIVE

### Plant 1 (Requested \- To Be Configured)

Sector ID: 2 (or as assigned by Twinzo)  
Coordinate Bounds: \[To be provided by TVS with FBX file\]  
Status: PENDING SETUP

**Important:** Specify which plant your robots are deployed in using the `sector_id` field in messages. For now keep `sector_id = 1`.

## Update Frequency Requirements

Recommended: 10 Hz (10 updates per second)

Minimum: 1 update per minute (0.0167 Hz)

Interval: 100ms between messages (for 10 Hz)

         60 seconds between messages (for minimum 1/minute)

## Robot ID Mapping to Twinzo

| Hi-tech Robot ID | Twinzo Tugger ID |
| :---- | :---- |
| hitech-amr-001 | tugger-01 |
| hitech-amr-002 | tugger-02 |
| hitech-amr-003 | tugger-03 |
| hitech-amr-004 | tugger-04 |

## 

## Example Python Implementation

### Minimal Working Example

```` ```python ````  
`#!/usr/bin/env python3`  
`"""`  
`Hi-tech AMR MQTT Publisher`  
`Publishes robot position data to HiveMQ broker`  
`"""`  
`import paho.mqtt.client as mqtt`  
`import json`  
`import time`  
`import ssl`

`# MQTT Configuration`  
`BROKER = "0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud"`  
`PORT = 8883`  
`USERNAME = "hitech-test"`  
`PASSWORD = "HitechAMR@2025"`

`# Robot Configuration (CHANGE FOR EACH ROBOT)`  
`ROBOT_ID = "hitech-amr-001"`  
`MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Your robot's actual MAC`  
`SECTOR_ID = 1  # Plant 4 = 1, Plant 1 = 2`

`def on_connect(client, userdata, flags, rc):`  
    `if rc == 0:`  
        `print(f"✓ Connected to MQTT broker")`  
    `else:`  
        `print(f"✗ Connection failed with code {rc}")`

`def get_robot_position():`  
    `"""`  
    `Replace this with actual code to read position from your robot`  
    `This is just a placeholder example`  
    `"""`  
    `# TODO: Read from your robot's localization system`  
    `x = 150000.0  # Example: 150 meters`  
    `y = 150000.0  # Example: 150 meters`  
    `battery = 85  # Example: 85%`  
    `speed = 500   # Example: 500 mm/s`  
    `return x, y, battery, speed`

`def main():`  
    `# Setup MQTT client`  
    `client = mqtt.Client(client_id=ROBOT_ID)`  
    `client.username_pw_set(USERNAME, PASSWORD)`  
    `client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)`  
    `client.on_connect = on_connect`

    `# Connect to broker`  
    `print(f"Connecting to {BROKER}:{PORT}...")`  
    `client.connect(BROKER, PORT, keepalive=60)`  
    `client.loop_start()`

    `# Wait for connection`  
    `time.sleep(2)`

    `# Publish loop (10 Hz)`  
    `print(f"Publishing position data for {ROBOT_ID} at 10 Hz...")`  
    `while True:`  
        `try:`  
            `# Get current position from robot`  
            `x, y, battery, speed = get_robot_position()`

            `# Create message`  
            `message = {`  
                `"device_id": ROBOT_ID,`  
                `"mac_address": MAC_ADDRESS,`  
                `"timestamp": int(time.time() * 1000),  # Milliseconds!`  
                `"position": {`  
                    `"x": x,`  
                    `"y": y,`  
                    `"z": 0.0`  
                `},`  
                `"battery": battery,`  
                `"status": "moving",`  
                `"speed": speed,`  
                `"sector_id": SECTOR_ID`  
            `}`

            `# Publish to MQTT`  
            `topic = f"hitech/amr/{ROBOT_ID}/position"`  
            `result = client.publish(topic, json.dumps(message), qos=1)`

            `if result.rc == mqtt.MQTT_ERR_SUCCESS:`  
                `print(f"✓ Published: {ROBOT_ID} at ({x:.0f}, {y:.0f})")`  
            `else:`  
                `print(f"✗ Publish failed: {result.rc}")`

            `# Wait 100ms (10 Hz)`  
            `time.sleep(0.1)`

        `except KeyboardInterrupt:`  
            `print("\nStopping...")`  
            `break`  
        `except Exception as e:`  
            `print(f"Error: {e}")`  
            `time.sleep(1)`

    `client.loop_stop()`  
    `client.disconnect()`

`if __name__ == "__main__":`  
    `main()`  
```` ``` ````

### Install Dependencies

```` ```bash ````  
`pip3 install paho-mqtt`  
```` ``` ````

## Testing & Verification \- Important

### Step 1: Test Connection

Run the Python script above with placeholder data to verify MQTT connection works.

### Step 2: Verify Messages

We can monitor incoming messages on our side. After you start publishing, contact us to confirm we're receiving data.

### Step 3: Check Twinzo

Once we confirm receipt, check the Twinzo platform to see if robots appear and move smoothly.

*Provided by Factories of Future \- Advanced Manufacturing Integration Solutions*