# 🚀 Twinzo MQTT Integration Guide

## 📋 **Connection Details**

```yaml
Protocol: MQTT over WebSocket (ws://)
URL: https://[ngrok-url-provided-at-runtime]
Username: mock_tvs
Password: Twinzo2025!@#
Topic: ati_fm/sherpa/status
QoS: 1 (recommended)
Keep Alive: 60 seconds
Update Rate: 10Hz (100ms intervals)
```

## 📊 **Data Mapping: MQTT → Twinzo Platform**

### **Raw MQTT Message Format**
```json
{
  "sherpa_name": "tugger-01",
  "mode": "Fleet",
  "error": "",
  "disabled": false,
  "disabled_reason": "",
  "pose": [220000.0, 209000.0, 0.0, 0.0, 0.0, 1.57],
  "battery_status": 79.0,
  "trip_id": 1001,
  "trip_leg_id": 5001
}
```

### **Field Mapping Table**

| MQTT Field | Type | Twinzo Field | Transformation | Notes |
|------------|------|--------------|----------------|-------|
| `sherpa_name` | string | `device_id` / `login` | Direct mapping | Device identifier |
| `pose[0]` | float | `X` | Direct mapping | X coordinate (meters) |
| `pose[1]` | float | `Y` | Direct mapping | Y coordinate (meters) |
| `pose[2]` | float | `Z` | Direct mapping | Z coordinate (meters) |
| `pose[5]` | float | `heading` / `theta` | Direct mapping | Yaw angle in radians (0-2π) |
| `battery_status` | float | `battery` | Direct mapping | Battery percentage (0-100) |
| `mode` | string | `status` / `mode` | Direct mapping | Operating mode |
| `disabled` | boolean | `is_active` | Invert: `!disabled` | Device active status |
| `error` | string | `error_message` | Direct mapping | Error description |
| `trip_id` | integer | `trip_id` | Direct mapping | Current trip identifier |
| `trip_leg_id` | integer | `leg_id` | Direct mapping | Current leg identifier |

### **Calculated Fields**

| Field | Calculation | Purpose |
|-------|-------------|---------|
| `timestamp` | `Date.now()` or message receive time | When data was received |
| `is_moving` | Calculate from position delta | Movement detection |
| `speed` | Calculate from position/time delta | Current speed |
| `sector_id` | Map from coordinates | Location zone |

## 🔧 **Integration Code Examples**

### **JavaScript/Node.js MQTT Client**

```javascript
const mqtt = require('mqtt');

// Connection configuration
const options = {
  username: 'mock_tvs',
  password: 'Twinzo2025!@#',
  keepalive: 60,
  protocolId: 'MQTT',
  protocolVersion: 4,
  clean: true,
  reconnectPeriod: 1000,
  connectTimeout: 30 * 1000,
};

// Connect to MQTT broker
const client = mqtt.connect('wss://[ngrok-url]', options);

client.on('connect', () => {
  console.log('✅ Connected to TVS MQTT broker');
  client.subscribe('ati_fm/sherpa/status', { qos: 1 });
});

client.on('message', (topic, message) => {
  try {
    const data = JSON.parse(message.toString());
    const twinzoData = transformToTwinzoFormat(data);
    
    // Send to Twinzo platform
    sendToTwinzoPlatform(twinzoData);
    
  } catch (error) {
    console.error('Error processing message:', error);
  }
});

// Transform MQTT data to Twinzo format
function transformToTwinzoFormat(mqttData) {
  return {
    device_id: mqttData.sherpa_name,
    timestamp: Date.now(),
    position: {
      x: mqttData.pose[0],
      y: mqttData.pose[1],
      z: mqttData.pose[2],
      heading: mqttData.pose[5]
    },
    battery: mqttData.battery_status,
    status: mqttData.mode,
    is_active: !mqttData.disabled,
    error_message: mqttData.error,
    trip_info: {
      trip_id: mqttData.trip_id,
      leg_id: mqttData.trip_leg_id
    },
    // Calculate movement from previous position
    is_moving: calculateMovement(mqttData.sherpa_name, mqttData.pose),
    speed: calculateSpeed(mqttData.sherpa_name, mqttData.pose)
  };
}
```

### **Python MQTT Client**

```python
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "wss://[ngrok-url]"
MQTT_USERNAME = "mock_tvs"
MQTT_PASSWORD = "Twinzo2025!@#"
MQTT_TOPIC = "ati_fm/sherpa/status"

# Device position tracking for movement calculation
device_positions = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to TVS MQTT broker")
        client.subscribe(MQTT_TOPIC, qos=1)
    else:
        print(f"❌ Connection failed: {rc}")

def on_message(client, userdata, msg):
    try:
        mqtt_data = json.loads(msg.payload.decode())
        twinzo_data = transform_to_twinzo_format(mqtt_data)
        
        # Send to Twinzo platform
        send_to_twinzo_platform(twinzo_data)
        
    except Exception as e:
        print(f"Error processing message: {e}")

def transform_to_twinzo_format(mqtt_data):
    device_id = mqtt_data['sherpa_name']
    current_pos = mqtt_data['pose'][:3]  # [x, y, z]
    
    # Calculate movement
    is_moving = calculate_movement(device_id, current_pos)
    speed = calculate_speed(device_id, current_pos)
    
    return {
        'device_id': device_id,
        'timestamp': int(time.time() * 1000),  # milliseconds
        'position': {
            'x': mqtt_data['pose'][0],
            'y': mqtt_data['pose'][1], 
            'z': mqtt_data['pose'][2],
            'heading': mqtt_data['pose'][5]
        },
        'battery': mqtt_data['battery_status'],
        'status': mqtt_data['mode'],
        'is_active': not mqtt_data['disabled'],
        'error_message': mqtt_data['error'],
        'trip_info': {
            'trip_id': mqtt_data['trip_id'],
            'leg_id': mqtt_data['trip_leg_id']
        },
        'is_moving': is_moving,
        'speed': speed
    }

def calculate_movement(device_id, current_pos):
    """Calculate if device is moving based on position delta"""
    if device_id not in device_positions:
        device_positions[device_id] = {
            'last_pos': current_pos,
            'last_time': time.time()
        }
        return True
    
    last_data = device_positions[device_id]
    distance = ((current_pos[0] - last_data['last_pos'][0])**2 + 
                (current_pos[1] - last_data['last_pos'][1])**2)**0.5
    
    # Movement threshold: 0.5 meters
    is_moving = distance > 0.5
    
    # Update position tracking
    device_positions[device_id] = {
        'last_pos': current_pos,
        'last_time': time.time()
    }
    
    return is_moving

# Setup MQTT client
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect and start listening
client.connect_async(MQTT_BROKER.replace('wss://', ''), 443, 60)
client.loop_forever()
```

## 📍 **Coordinate System Information**

### **Current Coordinate Bounds**
```yaml
Region:
  Top Left: 
    X: 195630.16
    Y: 188397.78
  Bottom Right:
    X: 223641.36  
    Y: 213782.93
  
Units: Meters (UTM/projected coordinates)
Reference System: Real-world coordinates for TVS Hosur facility
```

### **Device Movement Patterns**
```yaml
tugger-01:
  Pattern: Loop
  Speed: 800 units/second
  Battery: 79%
  
tugger-02:
  Pattern: Loop  
  Speed: 1000 units/second
  Battery: 77%
  
tugger-03:
  Pattern: Loop
  Speed: 1200 units/second
  Battery: 75%
```

## 🔄 **Data Flow Architecture**

```
TVS Mock System → MQTT Broker → ngrok Tunnel → Twinzo Middleware → Twinzo Platform
     ↓                ↓              ↓              ↓                    ↓
  3 Tuggers      Mosquitto     Secure HTTPS    Your Integration    Live Dashboard
  (10Hz each)    (WebSocket)    (Encrypted)      (Transform)       (Visualization)
```

## 🛡️ **Security & Authentication**

### **Connection Security**
- **Transport**: HTTPS/WSS (encrypted via ngrok)
- **Authentication**: Username/Password (MQTT CONNECT)
- **Authorization**: Topic-based (subscribe to `ati_fm/sherpa/status`)

### **Credentials Management**
```yaml
Environment Variables (Recommended):
  MQTT_BROKER_URL: "wss://[ngrok-url]"
  MQTT_USERNAME: "mock_tvs"
  MQTT_PASSWORD: "Twinzo2025!@#"
  MQTT_TOPIC: "ati_fm/sherpa/status"
```

## 📊 **Monitoring & Diagnostics**

### **Health Check Indicators**
```yaml
Connection Health:
  - MQTT connection status
  - Message receive rate (should be ~30 msg/sec for 3 devices at 10Hz)
  - Last message timestamp per device
  
Data Quality:
  - Position coordinate validation (within bounds)
  - Battery level range (0-100)
  - Message format validation
  
Device Status:
  - All 3 devices reporting (tugger-01, tugger-02, tugger-03)
  - Movement detection working
  - No error messages in 'error' field
```

### **Sample Monitoring Code**
```javascript
// Message rate monitoring
let messageCount = 0;
let lastRateCheck = Date.now();

client.on('message', (topic, message) => {
  messageCount++;
  
  // Check rate every 10 seconds
  if (Date.now() - lastRateCheck > 10000) {
    const rate = messageCount / 10;
    console.log(`Message rate: ${rate} msg/sec (expected: ~30)`);
    messageCount = 0;
    lastRateCheck = Date.now();
  }
});
```

## 🚨 **Error Handling**

### **Common Issues & Solutions**
```yaml
Connection Issues:
  - Check ngrok URL is current (changes on restart)
  - Verify credentials (mock_tvs / Twinzo2025!@#)
  - Ensure WebSocket protocol support

Data Issues:
  - Validate JSON parsing
  - Check coordinate bounds
  - Handle missing fields gracefully

Network Issues:
  - Implement reconnection logic
  - Buffer messages during disconnection
  - Monitor connection health
```

## 📞 **Support & Contact**

```yaml
Technical Contact: [Your contact information]
System Status: All systems operational
Data Availability: 24/7 during testing period
Response Time: Real-time (100ms intervals)
```

---

**🎉 This integration guide provides everything Twinzo needs to connect their middleware to your MQTT broker and transform the data into their platform format!**