# HiveMQ Cloud - Quick Start Guide

## ✅ Setup Complete!

Your HiveMQ Cloud broker is **LIVE** and **TESTED**!

---

## 🚀 Test The Complete System

### Step 1: Start the Bridge (Terminal 1)

The bridge subscribes to HiveMQ and forwards data to Twinzo:

```bash
python -X utf8 hivemq_to_twinzo_bridge.py
```

**You should see:**
```
BRIDGE CONNECTED TO HIVEMQ
Subscribing to: hitech/amr/+/position
Listening for AMR position data...
```

**Keep this running!**

---

### Step 2: Start the AMR Simulator (Terminal 2)

The simulator publishes AMR position data to HiveMQ:

```bash
python -X utf8 amr_simulator_hivemq.py
```

**You should see:**
```
AMR SIMULATOR CONNECTED TO HIVEMQ
Simulating 3 Hi-tech AMRs

Update #1 at 23:45:12
--------------------------------------------------------------------------------
  hitech-amr-01: (132,500.0, 132,000.0) Battery=85%
  hitech-amr-02: (150,000.0, 140,000.0) Battery=78%
  hitech-amr-03: (120,000.0, 125,000.0) Battery=92%
```

---

### Step 3: Watch The Bridge (Terminal 1)

The bridge should start receiving messages and forwarding to Twinzo:

```
[1] Received from hitech/amr/hitech-amr-01/position
    Device: hitech-amr-01
    Position: (132500.0, 132000.0)
    Battery: 85%
    Authenticated: tugger-01
    Twinzo OK: tugger-01 at (132500.0, 132000.0)
```

---

### Step 4: Check Twinzo Platform

Open https://platform.twinzo.com and you should see:
- **tugger-01, tugger-02, tugger-03** moving in circular paths!
- Real-time position updates every 2 seconds
- Battery levels decreasing over time

---

## 📱 Test from Phone (External Network)

### Install MQTT Client App

**Android:**
- **MQTT Dash** (recommended)
- **IoT MQTT Panel**

**iOS:**
- **MQTTool**
- **MQTT Explorer**

### Configure Connection

```
Host: 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud
Port: 8883
Username: hitech-test
Password: HitechAMR@2025
Enable SSL/TLS: YES
```

### Test Publishing

1. **Turn OFF WiFi** (use cellular data)
2. **Connect** to broker
3. **Publish** to topic: `hitech/amr/phone-test/position`
4. **Message** (copy/paste):

```json
{
  "device_id": "tugger-04",
  "mac_address": "AA:BB:CC:DD:EE:04",
  "timestamp": 1730000000000,
  "position": {
    "x": 150000,
    "y": 150000,
    "z": 0
  },
  "battery": 95,
  "status": "moving",
  "speed": 500,
  "sector_id": 1
}
```

5. **Watch** Terminal 1 - bridge should receive and forward to Twinzo
6. **Check** Twinzo platform - tugger-04 should appear at (150k, 150k)!

---

## 🎯 Data Flow

```
AMR Simulator → HiveMQ Cloud → Bridge → Twinzo API → Platform
     (PC)          (Cloud)        (PC)     (API)      (Web)

      OR

Phone (4G/5G) → HiveMQ Cloud → Bridge → Twinzo API → Platform
```

---

## 📊 What The Bridge Does

1. **Subscribes** to `hitech/amr/+/position` on HiveMQ
2. **Receives** AMR position data in JSON format
3. **Maps** device IDs: `hitech-amr-01` → `tugger-01`
4. **Authenticates** each tugger with Twinzo OAuth
5. **Transforms** data to Twinzo format
6. **POSTs** to Twinzo localization API
7. **Logs** success/failure for each message

---

## 🔍 Troubleshooting

### Bridge not receiving messages?
- Check simulator is running
- Check topic names match: `hitech/amr/*/position`
- Verify HiveMQ credentials in `config/hivemq_config.json`

### Twinzo API errors?
- Check tugger OAuth logins exist (tugger-01, tugger-02, tugger-03)
- Check password: `Tvs@Hosur$2025`
- Check API key in bridge script

### Phone can't connect?
- Ensure SSL/TLS is enabled (port 8883, not 1883)
- Turn OFF WiFi (use cellular)
- Check username/password exactly

---

## 🎉 Success Criteria

✅ Bridge connects to HiveMQ
✅ Simulator publishes position data
✅ Bridge receives and forwards data
✅ Tuggers appear on Twinzo platform
✅ Tuggers move in real-time
✅ Phone can publish from external network

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `config/hivemq_config.json` | HiveMQ connection details |
| `test_hivemq_connection.py` | Connection test script |
| `amr_simulator_hivemq.py` | Mock AMR data generator |
| `hivemq_to_twinzo_bridge.py` | MQTT → Twinzo bridge |

---

## 🚀 Ready for Hi-tech Integration!

Once tested, share with Hi-tech:
1. **HiveMQ connection details** (from `config/hivemq_config.json`)
2. **Topic structure**: `hitech/amr/{device_id}/position`
3. **Message format**: See example in phone test section
4. **Coordinate bounds**: X=[0, 265000], Y=[46000, 218000]

They can now publish AMR data from their real vehicles!

---

**Happy Testing! 🎉**
