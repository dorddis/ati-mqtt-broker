# 📋 TVS Client Requirements for Twinzo Integration

## 🎯 **What Twinzo Needs from TVS (IVT)**

Based on the Twinzo requirements and your mock implementation, here's everything the actual TVS client needs to provide:

## 🔗 **1. MQTT Broker Connection Details**

### **Required Information:**
```yaml
URL: 
  - Format: mqtt://hostname:port or mqtts://hostname:port
  - Example: "mqtt://tvs-mqtt-broker.company.com:1883"
  - Or secure: "mqtts://tvs-mqtt-broker.company.com:8883"

Username: 
  - MQTT authentication username
  - Example: "twinzo_integration" or "external_client"

Password: 
  - MQTT authentication password  
  - Should be secure and dedicated for Twinzo access
  - Example: "TwinzoAccess2025!@#"

QoS Level:
  - Recommended: 1 (at least once delivery)
  - Acceptable: 0 (at most once) or 2 (exactly once)

Update Rate:
  - Current: 1/min (too slow)
  - Ideal: 10/min (6-second intervals)
```

### **Network Requirements:**
```yaml
Protocol Support:
  - MQTT v3.1.1 or v5.0
  - TCP or WebSocket transport
  - Optional: TLS/SSL encryption

Firewall/Security:
  - Outbound MQTT port access (1883 or 8883)
  - IP whitelisting if required
  - Certificate management for TLS

Connection Stability:
  - Persistent connection preferred
  - Automatic reconnection on failure
  - Keep-alive interval: 60 seconds recommended
```

## 📡 **2. MQTT Topic Structure**

### **Required Topic Information:**
```yaml
Topic Pattern:
  - Your mock uses: "ati_fm/sherpa/status"
  - TVS should provide: Their actual topic structure
  - Examples:
    * "tvs/tuggers/location"
    * "fleet/vehicles/telemetry"
    * "ivt/devices/status"

Topic Permissions:
  - Read access for Twinzo client
  - Subscription permissions
  - Topic-level security if implemented
```

## 📊 **3. Data Format Specification**

### **Message Structure (JSON):**
The TVS client should provide data in this format (based on your successful mock):

```json
{
  "device_id": "tugger-01",           // Required: Unique device identifier
  "timestamp": 1754309000000,         // Required: Unix timestamp (milliseconds)
  "position": {                       // Required: Location data
    "x": 220000.0,                   // X coordinate (meters)
    "y": 209000.0,                   // Y coordinate (meters) 
    "z": 0.0,                        // Z coordinate (meters)
    "heading": 1.57                  // Heading in radians
  },
  "battery": 79.0,                   // Battery percentage (0-100)
  "status": "Fleet",                 // Operating mode/status
  "is_active": true,                 // Device active status
  "error_message": "",               // Error description (empty if no error)
  "trip_info": {                     // Optional: Trip management
    "trip_id": 1001,
    "leg_id": 5001
  },
  "speed": 850.5,                    // Optional: Current speed (m/s)
  "is_moving": true                  // Optional: Movement detection
}
```

### **Alternative Format (Your Mock Format):**
If TVS prefers to keep their existing format, they can provide:

```json
{
  "sherpa_name": "tugger-01",
  "pose": [220000.0, 209000.0, 0.0, 0.0, 0.0, 1.57],
  "battery_status": 79.0,
  "mode": "Fleet",
  "disabled": false,
  "error": "",
  "trip_id": 1001,
  "trip_leg_id": 5001
}
```

*Twinzo can transform this format using the mapping you've already provided.*

## 🗺️ **4. Coordinate System Information**

### **Required Specifications:**
```yaml
Coordinate System:
  - Reference system (UTM, WGS84, local grid, etc.)
  - Zone information if UTM
  - Units (meters, feet, etc.)
  - Origin point if local coordinate system

Coordinate Bounds:
  - Minimum X, Y values
  - Maximum X, Y values
  - Working area boundaries
  - Example from your mock:
    * X: 195630.16 to 223641.36
    * Y: 188397.78 to 213782.93
    * Units: Meters

Transformation Requirements:
  - Any coordinate transformations needed
  - Calibration points if available
  - Mapping to facility layout
```

## 🚛 **5. Device Information**

### **Fleet Details:**
```yaml
Device List:
  - Total number of devices
  - Device naming convention
  - Device types (tuggers, forklifts, etc.)
  - Example: tugger-01, tugger-02, tugger-03

Device Capabilities:
  - Position accuracy
  - Update frequency capability
  - Battery reporting
  - Status reporting
  - Error reporting

Device States:
  - Possible operating modes
  - Error conditions
  - Maintenance states
  - Offline/online status
```

## 🔒 **6. Security & Access Control**

### **Authentication Requirements:**
```yaml
MQTT Authentication:
  - Username/password for Twinzo client
  - Client certificate if using mutual TLS
  - Access control lists (ACLs)
  - Token-based auth if supported

Network Security:
  - VPN requirements if any
  - IP whitelisting
  - Port restrictions
  - SSL/TLS configuration

Data Security:
  - Data encryption requirements
  - Compliance requirements (if any)
  - Audit logging needs
  - Data retention policies
```

## 📈 **7. Performance & Reliability**

### **Service Level Requirements:**
```yaml
Availability:
  - Expected uptime (99.9%?)
  - Maintenance windows
  - Failover capabilities
  - Backup systems

Performance:
  - Message throughput capacity
  - Latency requirements
  - Connection limits
  - Bandwidth considerations

Monitoring:
  - Health check endpoints
  - Status monitoring
  - Alert mechanisms
  - Logging capabilities
```

## 🛠️ **8. Technical Support & Documentation**

### **Required Documentation:**
```yaml
Technical Specs:
  - MQTT broker configuration
  - Message schema documentation
  - API documentation if applicable
  - Integration examples

Support Information:
  - Technical contact details
  - Support hours
  - Escalation procedures
  - Change management process

Testing Support:
  - Test environment access
  - Sample data for testing
  - Integration testing support
  - Go-live support
```

## 📋 **9. Operational Requirements**

### **Deployment Information:**
```yaml
Environment Details:
  - Production MQTT broker details
  - Staging/test environment
  - Development environment access
  - Environment promotion process

Change Management:
  - How updates are communicated
  - Maintenance schedules
  - Version control
  - Rollback procedures

Monitoring & Alerts:
  - System health monitoring
  - Performance metrics
  - Alert notifications
  - Incident response
```

## ✅ **10. Comparison: Your Mock vs Real Requirements**

### **What Your Mock Provides (Excellent!):**
```yaml
✅ MQTT broker with authentication
✅ WebSocket support for external access
✅ Real-time data (10Hz - better than requested 10/min)
✅ Proper JSON message format
✅ Device identification (sherpa_name)
✅ Position data with pose array
✅ Battery status reporting
✅ Trip/leg management
✅ Error handling
✅ Coordinate system with bounds
✅ Multiple device simulation (3 tuggers)
✅ Continuous operation
✅ Security with username/password
```

### **What TVS Client Still Needs to Provide:**
```yaml
🔄 Production MQTT broker URL
🔄 Production credentials
🔄 Actual coordinate system specification
🔄 Real device list and capabilities
🔄 Production support contacts
🔄 SLA and availability commitments
🔄 Change management process
🔄 Long-term operational support
```

## 🎯 **Summary for TVS Client**

Your mock system demonstrates that the integration is **technically feasible and working**. The TVS client now needs to provide:

1. **Production MQTT broker access** (URL, credentials, topic)
2. **Coordinate system specification** (reference system, bounds, units)
3. **Device fleet information** (device list, capabilities, naming)
4. **Operational support** (SLA, contacts, change management)
5. **Security requirements** (authentication, network access, compliance)

The data format and integration approach you've proven with your mock can be directly applied to the production system! 🎉