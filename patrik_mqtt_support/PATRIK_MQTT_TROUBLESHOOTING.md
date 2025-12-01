# ATI MQTT Broker - Subscription Troubleshooting Guide

**For:** Patrik (Twinzo Team)
**Issue:** Can connect to `tvs-dev.ifactory.ai:8883` but cannot subscribe to topics
**Date:** 2025-11-20

---

## The Problem

You can connect to the ATI MQTT broker successfully, but subscription to topics fails:
- ❌ `ati_fm/sherpa/status` - Cannot subscribe
- ❌ `ati_fm/#` - Cannot subscribe

## Root Cause

The ATI broker uses **MQTT v5** with strict requirements:

1. **Client ID MUST match username exactly**
2. **Protocol version MUST be 5** (not 3.1.1 or 4)
3. **Clean session MUST be enabled**
4. **Session expiry MUST be 0**

## Solution: Correct Connection Settings

### For Node.js/JavaScript

```javascript
import mqtt from 'mqtt';

const connectionOptions = {
    protocol: 'mqtts',
    host: 'tvs-dev.ifactory.ai',
    port: 8883,

    // CRITICAL: Client ID must match username!
    clientId: 'tvs-audit-user',
    username: 'tvs-audit-user',
    password: 'TVSAudit@2025',

    // MQTT v5 required
    protocolVersion: 5,

    // Clean session required
    clean: true,

    // Connection timeouts
    reconnectPeriod: 5000,
    connectTimeout: 30000,

    // TLS settings
    rejectUnauthorized: false,

    // MQTT v5 properties
    properties: {
        sessionExpiryInterval: 0  // No persistent session
    }
};

const client = mqtt.connect(connectionOptions);

client.on('connect', () => {
    console.log('Connected!');

    // Subscribe with QoS 1
    const topics = {
        'ati_fm/#': { qos: 1 },
        'fleet/trips/info': { qos: 1 }
    };

    client.subscribe(topics, (err, granted) => {
        if (err) {
            console.error('Subscription error:', err);
            return;
        }
        console.log('Subscribed successfully:', granted);
    });
});

client.on('message', (topic, payload) => {
    console.log('Message received:', topic);
    console.log('Data:', JSON.parse(payload.toString()));
});
```

### For Python

```python
import paho.mqtt.client as mqtt

# CRITICAL: Client ID must match username!
MQTT_HOST = 'tvs-dev.ifactory.ai'
MQTT_PORT = 8883
MQTT_USERNAME = 'tvs-audit-user'
MQTT_PASSWORD = 'TVSAudit@2025'
MQTT_CLIENT_ID = MQTT_USERNAME  # Must be the same!

# Create client with MQTT v5
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=MQTT_CLIENT_ID,
    protocol=mqtt.MQTTv5,
    clean_start=True  # Clean session for MQTT v5
)

# Set credentials
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Enable TLS
client.tls_set()
client.tls_insecure_set(True)

# Callbacks
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected!")
        # Subscribe to topics with QoS 1
        topics = [
            ('ati_fm/#', 1),
            ('fleet/trips/info', 1)
        ]
        client.subscribe(topics)
    else:
        print(f"Connection failed: {reason_code}")

def on_message(client, userdata, message):
    print(f"Message on {message.topic}:")
    print(message.payload.decode('utf-8'))

client.on_connect = on_connect
client.on_message = on_message

# Connect
client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
client.loop_forever()
```

### For MQTT Clients (mqttx, mosquitto_sub, etc.)

```bash
# mosquitto_sub
mosquitto_sub \
    -h tvs-dev.ifactory.ai \
    -p 8883 \
    -i tvs-audit-user \
    -u tvs-audit-user \
    -P TVSAudit@2025 \
    -t "ati_fm/#" \
    -q 1 \
    -V 5 \
    --cafile /path/to/ca.crt \
    --insecure

# MQTTX CLI
mqttx sub \
    -h tvs-dev.ifactory.ai \
    -p 8883 \
    -i tvs-audit-user \
    -u tvs-audit-user \
    -P TVSAudit@2025 \
    -t "ati_fm/#" \
    -q 1 \
    --protocol-version 5 \
    --ssl \
    --insecure
```

## Available Topics

### Main Topics
- `ati_fm/#` - Wildcard for all ATI Fleet Manager topics
- `ati_fm/sherpa/status` - Individual AMR position updates
- `fleet/trips/info` - Trip information

### Expected Data Format

**Topic:** `ati_fm/sherpa/status`

```json
{
    "sherpa_name": "tug-55-tvsmotor-hosur-09",
    "mode": "fleet",
    "pose": [54.123, 32.456, 1.234],
    "battery_status": 78,
    "timestamp": 1700000000
}
```

**Fields:**
- `sherpa_name` - Device identifier (e.g., "tug-55-tvsmotor-hosur-09")
- `mode` - "fleet" (active) or "disconnected"
- `pose` - [x, y, heading] in meters
- `battery_status` - Battery percentage (0-100)
- `timestamp` - Unix timestamp

## Common Mistakes

### ❌ Wrong: Client ID ≠ Username

```javascript
// This will FAIL!
{
    clientId: 'my-client',
    username: 'tvs-audit-user',  // Different from clientId
    password: 'TVSAudit@2025'
}
```

### ✅ Correct: Client ID = Username

```javascript
// This will WORK!
{
    clientId: 'tvs-audit-user',
    username: 'tvs-audit-user',  // Same as clientId
    password: 'TVSAudit@2025'
}
```

### ❌ Wrong: MQTT v3.1.1

```javascript
// This will FAIL!
{
    protocolVersion: 4  // MQTT v3.1.1
}
```

### ✅ Correct: MQTT v5

```javascript
// This will WORK!
{
    protocolVersion: 5  // MQTT v5
}
```

### ❌ Wrong: Persistent Session

```javascript
// This will FAIL!
{
    clean: false,
    properties: {
        sessionExpiryInterval: 3600
    }
}
```

### ✅ Correct: Clean Session

```javascript
// This will WORK!
{
    clean: true,
    properties: {
        sessionExpiryInterval: 0
    }
}
```

## Test Scripts

We've created two test scripts for you to verify the connection:

### Node.js Test

```bash
node test_patrik_connection.js
```

**Location:** `test_patrik_connection.js` in the root directory

### Python Test

```bash
python -X utf8 test_patrik_connection.py
```

**Location:** `test_patrik_connection.py` in the root directory

Both scripts will:
1. ✅ Connect to the broker
2. ✅ Subscribe to topics
3. 📨 Show incoming messages
4. 📊 Display full message details

## Expected Output

When working correctly, you should see:

```
======================================================================
ATI MQTT Connection Test
======================================================================
Host: tvs-dev.ifactory.ai:8883
Username: tvs-audit-user
Client ID: tvs-audit-user
Protocol: MQTT v5
======================================================================

✅ CONNECTED successfully!

Attempting to subscribe to topics...

✅ SUBSCRIBED successfully!
Granted subscriptions:
  - Topic: ati_fm/#, QoS: 1
  - Topic: fleet/trips/info, QoS: 1

Listening for messages (press Ctrl+C to stop)...

======================================================================
📨 MESSAGE RECEIVED
Topic: ati_fm/sherpa/status
Time: 2025-11-20T10:30:45.123Z
Payload: {
  "sherpa_name": "tug-55-tvsmotor-hosur-09",
  "mode": "fleet",
  "pose": [54.123, 32.456, 1.234],
  "battery_status": 78
}
======================================================================
```

## Verification Checklist

Before testing, verify these settings:

- [ ] Protocol version is **5** (MQTT v5)
- [ ] Client ID is **exactly** `tvs-audit-user`
- [ ] Username is **exactly** `tvs-audit-user`
- [ ] Password is **exactly** `TVSAudit@2025`
- [ ] Clean session is **enabled** (true)
- [ ] Session expiry is **0**
- [ ] Port is **8883** (MQTTS)
- [ ] Host is **tvs-dev.ifactory.ai**
- [ ] TLS is **enabled**
- [ ] Certificate verification is **disabled** (insecure mode)

## Alternative Credentials (If Needed)

If the audit credentials don't work, you can try the individual AMR credentials:

```
Host: tvs-dev.ifactory.ai
Port: 8883
Username: amr-001
Password: TVSamr001@2025
Client ID: amr-001  (must match username!)
Topic: ati_fm/sherpa/status
```

## Active AMRs in the Feed

Currently streaming data for these 7 AMRs:

**Old Plant (Sector 2):**
- `tug-55-tvsmotor-hosur-09` → Twinzo device: `tug-55-hosur-09`
- `tug-39-tvsmotor-hosur-07` → Twinzo device: `tug-39-hosur-07`
- `tug-133` → Twinzo device: `tug-133`

**Not in Old Plant (data visible but ignored by bridge):**
- `tug-140`
- `tug-78`
- `tug-24-tvsmotor-hosur-05`
- `tug-11`

## Data Frequency

- **Update interval:** 2-6 seconds per AMR
- **Pattern:** Bursts of activity with 8-11 minute gaps
- **Not continuous:** Data comes in bursts, not a steady stream

## Need More Help?

If you're still having issues:

1. **Run the test scripts** (`test_patrik_connection.js` or `test_patrik_connection.py`)
2. **Capture the exact error message** you're seeing
3. **Check your MQTT client logs** for connection details
4. **Verify protocol version** - it MUST be v5
5. **Double-check Client ID** - it MUST match username

## Contact

If you need further assistance, send us:
- Your MQTT client type (Node.js, Python, MQTTX, etc.)
- Exact error message
- Connection settings you're using (redact password)
- Output from the test scripts

---

**Working Bridge Reference:** `src/bridge/bridge_audit_feed.js` (lines 204-254)
