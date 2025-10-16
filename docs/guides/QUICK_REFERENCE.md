# 📋 Quick Reference: TVS → Twinzo Data Mapping

## 🔗 **Connection Info**
```
URL: https://[provided-at-runtime].ngrok-free.app
Username: mock_tvs
Password: Twinzo2025!@#
Topic: ati_fm/sherpa/status
Protocol: MQTT over WebSocket
```

## 📊 **Data Transformation**

### **Input (MQTT Message)**
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

### **Output (Twinzo Format)**
```json
{
  "device_id": "tugger-01",
  "timestamp": 1754309000000,
  "x": 220000.0,
  "y": 209000.0,
  "z": 0.0,
  "heading": 1.57,
  "battery": 79.0,
  "status": "Fleet",
  "is_active": true,
  "error_message": "",
  "trip_id": 1001,
  "leg_id": 5001,
  "is_moving": true,
  "speed": 850.5
}
```

## 🔄 **Field Mappings**
```
sherpa_name → device_id
pose[0] → x
pose[1] → y  
pose[2] → z
pose[5] → heading
battery_status → battery
mode → status
!disabled → is_active
error → error_message
trip_id → trip_id
trip_leg_id → leg_id
```

## 📍 **Coordinate Bounds**
```
X: 195630.16 to 223641.36
Y: 188397.78 to 213782.93
Units: Meters
```

## 🚛 **Active Devices**
```
tugger-01: Battery 79%, Speed 800 u/s
tugger-02: Battery 77%, Speed 1000 u/s  
tugger-03: Battery 75%, Speed 1200 u/s
```

## ⚡ **Data Rate**
```
Frequency: 10Hz per device (30 total msg/sec)
Interval: 100ms
Format: JSON
QoS: 1 (recommended)
```