# Hi-tech Integration - Technical Steps Overview

**For:** Sid (FoF) - Your reference guide
**Purpose:** Detailed breakdown of what needs to happen after Hi-tech responds

---

## What You Currently Have

Based on your repo, you have a complete MQTT → Twinzo integration system:

1. **MQTT Broker** (Mosquitto) - Can receive data from AMRs
2. **Bridge Service** - Transforms MQTT data and posts to Twinzo API with OAuth
3. **Device Mapping System** - Maps device IDs to Twinzo credentials
4. **Coordinate Transformation** - Handles coordinate system conversions
5. **Working Twinzo API Integration** - OAuth + localization API calls

---

## What Needs to Happen (Step-by-Step)

### Phase 1: Get Requirements from Hi-tech (Days 1-2)

**Goal:** Understand their data format and coordinate system

**What you're asking for:**
1. Sample messages with REAL coordinate values (not just schema)
2. Coordinate system details (UTM? Local grid? Units? Ranges?)
3. Device IDs (How many AMRs? What are they named?)
4. Update frequency (Can they do 1 per minute?)
5. Network connectivity (Can they reach external MQTT brokers?)

**Why you need this:**
- Their JSON schema only shows data TYPES, not actual VALUES
- You need to write code to transform their format to Twinzo's format
- You need their coordinates to map to Plant 4 layout correctly

---

### Phase 2: Set Up MQTT Broker (Day 1 after requirements)

**What you do:**

1. **Start Ngrok tunnel:**
   ```bash
   cd C:\Users\sidro\all-code\archived\twinzo-mock
   python -X utf8 scripts/utils/expose_mqtt.py
   ```
   - This exposes your local MQTT broker to the internet
   - Ngrok gives you a URL like: `tcp://2.tcp.ngrok.io:12345`
   - **Note:** This URL changes each time you restart Ngrok (it's temporary)

2. **Start local MQTT broker:**
   ```bash
   docker-compose up -d broker
   ```

3. **Test it's working:**
   ```bash
   python -X utf8 tests/mqtt/simple_mqtt_test.py
   ```

4. **Share connection details with Hi-tech:**
   ```
   MQTT Host: [ngrok URL without protocol]
   MQTT Port: [ngrok port]
   Protocol: MQTT TCP (or WebSocket if they prefer)
   Topic: hitech/amr/position
   Auth: None required (or set up credentials if they want)
   ```

**Why Ngrok:**
- Quick and easy to expose local broker to internet
- Free tier works fine for PoC
- You don't need to deploy to cloud immediately
- Yes, it's temporary - but fine for PoC testing

---

### Phase 3: Create Hi-tech Device Mappings (Day 2)

**What you do:**

1. **Create Hi-tech device mapping file:**
   Edit `config/mappings/device_mapping.json`:
   ```json
   {
     "hitech-amr-01": {
       "name": "Hi-tech AMR 01",
       "twinzo_device": "hitech-01",
       "oauth_login": "Hitech01"
     },
     "hitech-amr-02": {
       "name": "Hi-tech AMR 02",
       "twinzo_device": "hitech-02",
       "oauth_login": "Hitech02"
     }
   }
   ```

2. **Get OAuth credentials from TVS/Twinzo:**
   - Ask Prashant: What are the OAuth login credentials for Hi-tech devices in Twinzo?
   - Format: Each device needs a "login" name (like "Hitech01")
   - These devices must exist in Twinzo platform first

**Why you need this:**
- Twinzo uses per-device OAuth authentication
- Each AMR needs its own OAuth token
- Bridge service handles OAuth automatically using this mapping

---

### Phase 4: Create Data Transformation (Days 3-4)

**What you do:**

1. **Analyze Hi-tech's data format** (once you get samples)

2. **Update bridge to handle Hi-tech format:**

   Edit `src/bridge/bridge.py` in the `on_message` function:

   ```python
   # Extract data based on Hi-tech's format
   # Example if they send:
   # {"event": {"type": "tripUpdate", "amrId": "AMR-01",
   #            "location": {"current": {"x": 220000, "y": 209000, "z": 0}},
   #            "batteryPercentage": 85.5}}

   if "event" in payload:  # Hi-tech format
       device_id = payload["event"]["amrId"]
       x = payload["event"]["location"]["current"]["x"]
       y = payload["event"]["location"]["current"]["y"]
       z = payload["event"]["location"]["current"]["z"]
       battery = payload["event"]["batteryPercentage"]
   else:  # Existing mock format
       device_id = payload.get("sherpa_name")
       x, y, z, theta = extract_pose(payload)
       battery = payload.get("battery_status", 85)
   ```

3. **Handle coordinate transformation:**
   - If Hi-tech uses different coordinate system than Twinzo
   - Update the affine transform parameters in docker-compose.yml
   - Or add coordinate conversion logic in bridge

**Why you need this:**
- Hi-tech's JSON format will be different from your mock format
- Bridge needs to understand both formats
- Coordinates might need conversion to match Twinzo's expected system

---

### Phase 5: Testing (Days 4-5)

**What you do:**

1. **Monitor MQTT messages:**
   ```bash
   python -X utf8 scripts/monitoring/monitor_twinzo.py live
   ```

2. **Check data is arriving:**
   - See messages in console
   - Verify device IDs are recognized
   - Check coordinates are in expected ranges

3. **Verify Twinzo API calls:**
   - Bridge should show "POST ok 200" for successful calls
   - Check OAuth tokens are working
   - Verify data format matches Twinzo API requirements

4. **Check Twinzo platform:**
   - Log into Twinzo dashboard
   - See if Hi-tech AMRs appear on map
   - Verify positions match Plant 4 layout
   - Check positions update in real-time

**Common issues you might face:**
- OAuth fails → Check device credentials in mapping file
- Coordinates out of bounds → Need coordinate transformation
- Data not appearing → Check JSON format transformation
- Wrong positions → Coordinate system mismatch

---

### Phase 6: Coordinate Verification (Days 5-6)

**What you do:**

1. **Use anchor points from Hi-tech:**
   - They tell you: "Loading dock is at x:220000, y:209000"
   - You check on Twinzo if AMR appears at loading dock
   - If not, adjust coordinate transformation

2. **Calculate transformation if needed:**
   - If their coordinate system is different
   - Use 3 anchor points to calculate affine transform
   - Update transform parameters in bridge configuration

3. **Verify with Plant 4 FBX layout:**
   - Overlay Hi-tech positions on Plant 4 3D model
   - Confirm AMRs are in correct locations
   - Adjust if positions are offset or rotated

**Why this is critical:**
- Wrong coordinates = AMRs show up in wrong locations
- Could show AMR "outside building" or "in wrong room"
- Must match physical reality for useful visualization

---

### Phase 7: Production Handoff (Day 7)

**What you do:**

1. **Document final configuration:**
   - MQTT broker details (if you deploy permanently)
   - Device mapping file
   - Coordinate transformation parameters
   - Any special handling for Hi-tech format

2. **Set up monitoring:**
   - Error alerting
   - Connection health checks
   - Message rate monitoring

3. **Create runbook:**
   - How to restart services
   - How to add new Hi-tech devices
   - Troubleshooting guide

4. **Handoff to TVS:**
   - Show them the working system
   - Provide access credentials
   - Train on monitoring and basic troubleshooting

---

## Key Files You'll Edit

1. **config/mappings/device_mapping.json**
   - Add Hi-tech device IDs and OAuth logins

2. **src/bridge/bridge.py**
   - Update `on_message` function to handle Hi-tech format
   - May need to update coordinate transformation

3. **docker-compose.yml**
   - Update coordinate transform parameters if needed
   - Update MQTT topic if needed

4. **scripts/utils/expose_mqtt.py**
   - Run this to start Ngrok tunnel

---

## Twinzo API Details (What You Need)

**Authentication:**
- OAuth endpoint: `https://api.platform.twinzo.com/v3/authorization/authenticate`
- Per-device authentication (each AMR has own login)
- Returns: Token, Client, Branch (used in subsequent calls)

**Localization API:**
- Endpoint: `https://api.platform.twinzo.com/v3/localization`
- Method: POST
- Headers: Token, Client, Branch, Api-Key
- Payload format:
  ```json
  [{
    "Timestamp": 1730000000000,
    "SectorId": 1,
    "X": 220000.0,
    "Y": 209000.0,
    "Z": 0.0,
    "Interval": 100,
    "Battery": 85,
    "IsMoving": true,
    "LocalizationAreas": [],
    "NoGoAreas": []
  }]
  ```

**What your bridge does:**
1. Receives MQTT message from Hi-tech AMR
2. Extracts position, battery, device ID
3. Looks up device OAuth credentials
4. Transforms to Twinzo format
5. POSTs to Twinzo localization API
6. Logs result

---

## Questions You Might Have During Call

**If they ask: "What's MQTT?"**
- "It's a messaging system - like a post office. Your AMRs post position updates, and our system subscribes to receive them."

**If they ask: "What's a topic?"**
- "It's like a channel name or address. All your AMRs will publish to 'hitech/amr/position' and our system will listen to that channel."

**If they ask: "Do we need to change our system?"**
- "Only if you can't publish to external MQTT brokers. Otherwise, you just need to send your existing data to our broker URL."

**If they ask: "What format should we send?"**
- "Keep your existing format! Just send us real examples, and we'll write code to transform it to what Twinzo needs."

**If they ask: "How secure is this?"**
- "The Ngrok tunnel is encrypted (HTTPS). For production, we can add MQTT username/password or deploy to a cloud server with better security."

**If they ask: "What if the URL changes?"**
- "For this PoC, you're right - Ngrok URL changes when restarted. If that's a problem, we can deploy to Railway or Render (free cloud hosting) for a permanent URL. But for quick testing, Ngrok is faster to set up."

---

## Success Criteria

You'll know it's working when:
1. ✅ Hi-tech AMRs connect to your MQTT broker
2. ✅ You see their messages in console: `python -X utf8 scripts/monitoring/monitor_twinzo.py live`
3. ✅ Bridge shows "POST ok 200" for Twinzo API calls
4. ✅ Hi-tech devices appear on Twinzo dashboard/map
5. ✅ Positions update in real-time (at least every 60 seconds)
6. ✅ Positions match physical locations in Plant 4

---

## What Could Go Wrong (and How to Fix)

**Problem:** Hi-tech can't connect to Ngrok URL
- **Fix:** Check firewall, try WebSocket protocol, or deploy to Railway/Render

**Problem:** OAuth fails for Hi-tech devices
- **Fix:** Verify device logins exist in Twinzo, check credentials in mapping file

**Problem:** Coordinates are wrong on Twinzo map
- **Fix:** Calculate coordinate transformation using anchor points

**Problem:** Data format is completely different than expected
- **Fix:** Update bridge transformation logic - you might need to handle nested structures differently

**Problem:** Ngrok URL keeps changing and Hi-tech complains
- **Fix:** Deploy to Railway/Render for permanent URL (takes 30 mins to set up)

---

## You Got This! 💪

You have:
- ✅ Working MQTT broker
- ✅ Working bridge that talks to Twinzo
- ✅ OAuth authentication handling
- ✅ Coordinate transformation capability
- ✅ All the code you need

You just need to:
1. Get Hi-tech's data format and coordinates
2. Add their device mappings
3. Update bridge to handle their format
4. Test and verify on Twinzo

I'll help you through each step when they respond!
