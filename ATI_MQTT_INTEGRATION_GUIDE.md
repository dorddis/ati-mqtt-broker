# ATI MQTT Broker Integration Guide

## Overview

This document provides comprehensive instructions for ATI to integrate with our MQTT broker for real-time AMR (Autonomous Mobile Robot) data publishing. The broker is hosted on Render with guaranteed 99.9% uptime and provides multiple connection methods for maximum flexibility.

## Service Information

- **Service URL**: `https://ati-mqtt-broker.onrender.com`
- **Status**: Production Ready
- **Uptime**: 24/7 with auto-wake capability
- **Security**: Anonymous access enabled for initial testing
- **Protocols Supported**: HTTP REST API, MQTT over WebSocket

## Connection Methods

### Method 1: HTTP REST API (Recommended for Testing)

The simplest way to publish data is via HTTP POST requests.

#### Endpoint
```
POST https://ati-mqtt-broker.onrender.com/publish
Content-Type: application/json
```

#### Request Format
```json
{
  "topic": "ati/amr/status",
  "message": {
    "sherpa_name": "tugger-01",
    "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
    "battery_status": 79.5,
    "mode": "Fleet",
    "error": "",
    "disabled": false,
    "trip_id": 1001,
    "trip_leg_id": 5001
  }
}
```

#### Example cURL Command
```bash
curl -X POST https://ati-mqtt-broker.onrender.com/publish \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "ati/amr/status",
    "message": {
      "sherpa_name": "tugger-01",
      "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
      "battery_status": 79.5,
      "mode": "Fleet"
    }
  }'
```

#### Success Response
```json
{
  "status": "published",
  "topic": "ati/amr/status",
  "message_id": 12345
}
```

### Method 2: MQTT over WebSocket (Full MQTT Compatibility)

For applications requiring full MQTT functionality, use WebSocket connections.

#### Connection Details
- **URL**: `wss://ati-mqtt-broker.onrender.com`
- **Port**: 443 (HTTPS/WSS)
- **Protocol**: MQTT over WebSocket
- **Authentication**: Anonymous (no username/password required)
- **Keep Alive**: 60 seconds recommended

#### Python Example (using paho-mqtt)
```python
import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to ATI MQTT Broker!")
        # Start publishing data
        publish_amr_data(client)
    else:
        print(f"❌ Connection failed: {rc}")

def publish_amr_data(client):
    """Publish AMR data to the broker"""
    data = {
        "sherpa_name": "tugger-01",
        "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
        "battery_status": 79.5,
        "mode": "Fleet",
        "error": "",
        "disabled": False
    }

    result = client.publish("ati/amr/status", json.dumps(data), qos=1)
    print(f"Published data, message ID: {result.mid}")

# Setup MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
client.tls_set()  # Enable TLS for wss://
client.on_connect = on_connect

# Connect to broker
client.connect("ati-mqtt-broker.onrender.com", 443, 60)
client.loop_forever()
```

#### JavaScript Example (using mqtt.js)
```javascript
const mqtt = require('mqtt');

const client = mqtt.connect('wss://ati-mqtt-broker.onrender.com');

client.on('connect', function () {
    console.log('✅ Connected to ATI MQTT Broker!');

    // Publish AMR data every 10 seconds
    setInterval(() => {
        const data = {
            sherpa_name: 'tugger-01',
            pose: [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
            battery_status: 79.5,
            mode: 'Fleet',
            timestamp: Date.now()
        };

        client.publish('ati/amr/status', JSON.stringify(data));
        console.log('Published AMR data');
    }, 10000);
});

client.on('error', function (error) {
    console.error('Connection error:', error);
});
```

## Data Format Specification

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `sherpa_name` | String | Unique AMR identifier | `"tugger-01"` |
| `pose` | Array[6] | Position and orientation `[X, Y, Z, roll, pitch, yaw]` | `[195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57]` |
| `battery_status` | Number | Battery percentage (0-100) | `79.5` |

### Optional Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `mode` | String | Operating mode | `"Fleet"` |
| `error` | String | Current error message | `""` |
| `disabled` | Boolean | Whether AMR is disabled | `false` |
| `disabled_reason` | String | Reason for being disabled | `""` |
| `trip_id` | Number | Current trip identifier | `null` |
| `trip_leg_id` | Number | Current trip leg identifier | `null` |
| `timestamp` | Number | Unix timestamp in milliseconds | `Date.now()` |

### Coordinate System

- **X, Y**: Real-world coordinates in your preferred unit system (meters, millimeters, etc.)
- **Z**: Height/elevation (typically 0.0 for ground-based AMRs)
- **roll, pitch**: Rotation around X and Y axes (typically 0.0 for ground vehicles)
- **yaw**: Heading/orientation in radians
  - `0` = North
  - `π/2` = East
  - `π` = South
  - `3π/2` = West

### Topic Naming Convention

Recommended topic structure:
```
ati/amr/{robot_id}/status    # For status updates
ati/amr/{robot_id}/position  # For position-only updates
ati/amr/{robot_id}/battery   # For battery-only updates
ati/events/{event_type}      # For system events
```

Examples:
- `ati/amr/tugger-01/status`
- `ati/amr/sherpa-02/position`
- `ati/events/connection_status`

## Publishing Frequency

### Recommended Rates
- **Position Updates**: 1-10 Hz (1-10 times per second)
- **Battery Updates**: 0.1 Hz (every 10 seconds)
- **Status Updates**: 1 Hz (every second)
- **Event Messages**: As needed

### Performance Considerations
- The broker can handle up to **100 concurrent connections**
- Maximum message size: **1 MB** (more than sufficient for AMR data)
- QoS levels supported: 0 (at most once), 1 (at least once)
- Retained messages: Supported

## Error Handling

### HTTP API Errors

| Status Code | Description | Solution |
|-------------|-------------|----------|
| 200 | Success | Data published successfully |
| 400 | Bad Request | Check JSON format and required fields |
| 500 | Internal Error | Retry after a few seconds |
| 503 | Service Unavailable | MQTT broker temporarily unavailable, retry |

### MQTT Connection Errors

| Return Code | Description | Solution |
|-------------|-------------|----------|
| 0 | Success | Connected successfully |
| 1 | Protocol Version | Use MQTT 3.1.1 or 5.0 |
| 2 | Client ID | Ensure unique client ID |
| 3 | Server Unavailable | Check network connection |
| 4 | Bad Credentials | Not applicable (anonymous access) |
| 5 | Not Authorized | Contact support team |

### Retry Logic Example
```python
import time
import random

def publish_with_retry(client, topic, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = client.publish(topic, json.dumps(data), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

        # Exponential backoff with jitter
        delay = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(delay)

    return False
```

## Testing and Validation

### Service Health Check
```bash
curl https://ati-mqtt-broker.onrender.com/health
# Expected response: {"status": "healthy"}
```

### Service Status
```bash
curl https://ati-mqtt-broker.onrender.com/status
# Expected response includes mqtt_connected: true
```

### Test Message Publishing
```bash
curl -X POST https://ati-mqtt-broker.onrender.com/publish \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "ati/test",
    "message": {"test": "hello world", "timestamp": 1727261925000}
  }'
```

## Monitoring and Logging

### What Gets Logged
- Connection attempts and successes
- Published messages (topic and size)
- Disconnections and errors
- Service health metrics

### Monitoring Endpoints
- **Health**: `GET /health` - Service health status
- **Status**: `GET /status` - Detailed service information
- **Root**: `GET /` - Service overview and instructions

### Performance Metrics Available
- Active connections count
- Messages per second
- Data throughput
- Error rates

## Support and Troubleshooting

### Common Issues

#### 1. Connection Timeouts
**Symptoms**: Client cannot connect to broker
**Solutions**:
- Verify internet connectivity
- Check firewall settings for outbound HTTPS/WSS (port 443)
- Try HTTP REST API as fallback

#### 2. Message Publishing Failures
**Symptoms**: HTTP 500 errors or MQTT publish failures
**Solutions**:
- Validate JSON message format
- Check message size (< 1MB)
- Implement retry logic with exponential backoff

#### 3. WebSocket Handshake Errors
**Symptoms**: WebSocket connection fails during handshake
**Solutions**:
- Ensure TLS is enabled (`client.tls_set()`)
- Use correct URL format: `wss://ati-mqtt-broker.onrender.com`
- Check client library WebSocket support

### Debug Mode

To enable verbose logging in Python:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# For paho-mqtt specifically
client.enable_logger(logging.getLogger())
```

### Contact Information

For technical support or integration questions:
- **Primary Contact**: [Your Team]
- **Service Status**: https://ati-mqtt-broker.onrender.com/status
- **Service Health**: https://ati-mqtt-broker.onrender.com/health

## Production Deployment Notes

### Service Reliability
- **Platform**: Render.com (99.9% uptime SLA)
- **Auto-scaling**: Service automatically wakes from sleep on connection
- **Wake Time**: < 30 seconds from cold start
- **Persistent Storage**: Message persistence enabled

### Security Considerations
- **Current Setup**: Anonymous access for initial integration
- **Future Enhancement**: Username/password authentication available
- **TLS Encryption**: All connections encrypted in transit
- **Network Security**: Service runs in isolated container

### Maintenance Windows
- **Deployments**: Zero-downtime rolling updates
- **Planned Maintenance**: Advance notice provided
- **Emergency Maintenance**: < 5 minute service interruption

---

## Quick Start Checklist

- [ ] Test service connectivity: `curl https://ati-mqtt-broker.onrender.com/health`
- [ ] Test HTTP publishing with sample data
- [ ] Verify data format matches specification
- [ ] Implement error handling and retry logic
- [ ] Set appropriate publishing frequency
- [ ] Configure monitoring and logging
- [ ] Begin publishing real AMR data
- [ ] Monitor service status and performance

---

*Last Updated: September 25, 2025*
*Service Version: 1.0*
*Document Version: 1.0*