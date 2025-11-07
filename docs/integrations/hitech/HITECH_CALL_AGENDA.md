# Hi-tech Technical Discussion - Call Agenda

**Duration:** 15 minutes
**Attendees:** TVS (Prashant), Hi-tech (Technical Lead), Factories of Future (Sid)
**Objective:** Share ready infrastructure and onboard Hi-tech AMRs to Twinzo platform

---

## 🎉 What's Already Complete

### ✅ MQTT Broker Setup
**HiveMQ Cloud** - Ready and tested, accessible from anywhere

**Connection Details:**
```
Host: 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud
Port: 8883 (TLS/SSL required)
WebSocket Port: 8884
Username: hitech-test
Password: HitechAMR@2025
```

**Limits:** 100 connections, 10GB/month (FREE)

### ✅ Factory Floor Coordinates Mapped
**Plant 4 Verified Bounds:**
```
X range: 0 to 265,000
Y range: 46,000 to 218,000
Width: 265,000 units
Height: 172,000 units
```

**Coordinate System:**
- X increases from LEFT to RIGHT (0 → 265k)
- Y increases from TOP to BOTTOM (46k → 218k)
- Z = 0 for floor level

### ✅ Twinzo Integration Working
**Tested Devices:**
- tugger-01 ✓
- tugger-02 ✓
- tugger-03 ✓
- tugger-04 ✓
- dzdB2rvp3k ✓
- kjuSXGs4Y9 ✓

**Bridge Status:** MQTT → Twinzo API bridge running and tested
**OAuth:** Automated authentication working
**Real-time Updates:** Verified with 1-second refresh rate

### ✅ End-to-End Testing Complete
- AMR simulator publishing position data ✓
- HiveMQ Cloud receiving messages ✓
- Bridge forwarding to Twinzo API ✓
- Tuggers moving on platform in real-time ✓
- External network access tested ✓

---

## 📋 Agenda

### 1. Demo Our Setup (5 min)

**What we'll show:**
- Live tuggers moving on Twinzo platform
- HiveMQ Cloud dashboard
- How their AMRs will appear once connected

### 2. Hi-tech Data Format (5 min)

**What we need from Hi-tech:**

1. **Sample Message** - One real position update from their AMR:
   ```json
   {
     "device_id": "???",
     "position": {
       "x": ???,
       "y": ???
     },
     "battery": ???,
     "timestamp": ???
   }
   ```

2. **Coordinate Verification** - Confirm their coordinate ranges:
   - "Our X values are typically between ___ and ___"
   - "Our Y values are typically between ___ and ___"
   - "Units: meters / millimeters / ?"

3. **Physical Anchor Points** - Map 1-2 locations:
   - "Loading dock is at (x: ???, y: ???)"
   - "Warehouse entrance is at (x: ???, y: ???)"

### 3. Device List (2 min)

**Questions:**
- How many Hi-tech AMRs in Plant 4? (Expected: 5-10)
- Device IDs list? (Will create OAuth accounts for each)
- All devices use same coordinate system?

### 4. Network & Publishing (3 min)

**Questions:**
- Can Hi-tech AMRs connect to internet MQTT broker? (HiveMQ Cloud)
- Any firewall restrictions?
- Preferred update frequency? (We support 1 update/second)
- MQTT client library being used?

---

## 📤 What Hi-tech Needs to Do

### Step 1: Test Connection (30 min)
Use any MQTT client to test connection:
```bash
# Using mosquitto_pub (or any MQTT tool)
mosquitto_pub -h 0c7fb7a06d4a4cd5a2868913301ad97d.s1.eu.hivemq.cloud \
  -p 8883 \
  -u hitech-test \
  -P HitechAMR@2025 \
  --capath /etc/ssl/certs/ \
  -t "hitech/amr/test-device/position" \
  -m '{"device_id":"test-amr","position":{"x":150000,"y":130000},"battery":85}'
```

**Expected result:** We'll see "test-amr" appear on Twinzo platform!

### Step 2: Publish Topic Format
```
Topic: hitech/amr/{device_id}/position

Example: hitech/amr/hitech-amr-01/position
```

### Step 3: Message Format
```json
{
  "device_id": "hitech-amr-01",
  "mac_address": "AA:BB:CC:DD:EE:01",
  "timestamp": 1730000000000,
  "position": {
    "x": 150000,
    "y": 130000,
    "z": 0
  },
  "battery": 85,
  "status": "moving",
  "speed": 500,
  "sector_id": 1
}
```

**Required fields:**
- `device_id` - Unique AMR identifier
- `position.x` - X coordinate (0-265000 range)
- `position.y` - Y coordinate (46000-218000 range)

**Optional fields:**
- `battery`, `status`, `speed`, `mac_address`, `timestamp`

### Step 4: Coordinate Transformation (If Needed)

If Hi-tech coordinates are different from Twinzo bounds, we'll create transformation:

```
twinzo_x = (hitech_x - hitech_min_x) / (hitech_max_x - hitech_min_x) * 265000
twinzo_y = (hitech_y - hitech_min_y) / (hitech_max_y - hitech_min_y) * 172000 + 46000
```

**We can do this transformation in the bridge - Hi-tech can publish in their native coordinates!**

---

## 🚀 Post-Call Actions

### Factories of Future (Sid):
1. ✅ MQTT broker credentials shared (already done)
2. ⏳ Create OAuth accounts for Hi-tech device IDs (need list from Hi-tech)
3. ⏳ Configure coordinate transformation if needed (need ranges from Hi-tech)
4. ⏳ Monitor bridge for incoming Hi-tech messages

### Hi-tech:
1. ⏳ Test MQTT connection using provided credentials
2. ⏳ Publish test message from 1 AMR
3. ⏳ Verify AMR appears on Twinzo platform
4. ⏳ Scale to all AMRs once verified
5. ⏳ Provide device ID list for OAuth setup

### TVS (Prashant):
1. ✅ Coordinate call between teams
2. ⏳ Follow up on integration progress

---

## 📊 Expected Timeline

| Milestone | Timeline | Owner |
|-----------|----------|-------|
| Share MQTT credentials | ✅ Done | FoF |
| Hi-tech tests connection | Day 1 | Hi-tech |
| Hi-tech sends 1 test AMR data | Day 1-2 | Hi-tech |
| Verify on Twinzo platform | Day 2 | FoF + Hi-tech |
| Configure all Hi-tech AMRs | Day 3-5 | Hi-tech |
| Live monitoring on Twinzo | Day 5+ | All |

---

## 📋 Information Needed from Hi-tech

Quick checklist of what we need:

- [ ] Sample position message (real data)
- [ ] Coordinate system details (min/max X/Y values)
- [ ] 1-2 physical anchor points with coordinates
- [ ] Complete device ID list
- [ ] Confirm network connectivity capability

---

## 💡 Key Points to Emphasize

1. **Infrastructure is ready** - No waiting, Hi-tech can start testing immediately
2. **Free tier** - HiveMQ free tier supports 100 connections, more than enough
3. **Flexible coordinates** - We can transform their coordinates to Twinzo format
4. **Real-time verified** - Already tested with 6 devices moving smoothly
5. **Simple format** - Minimal required fields, easy to integrate

---

## 🔧 Technical Support

**During integration:**
- Sid available for troubleshooting
- Can screen share for debugging
- Bridge logs show exactly what's happening

**Contact:** dorddis@gmail.com

---

## 📝 Notes Section (Fill during call)

**Hi-tech Data Format:**
```
[Space for notes during call]
```

**Coordinate Details:**
```
[Space for notes during call]
```

**Device IDs:**
```
[Space for notes during call]
```

**Timeline Agreement:**
```
[Space for notes during call]
```

---

**Status:** Ready for Hi-tech integration! 🚀
