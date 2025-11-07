# Hi-tech AMR Integration - PoC Requirements

**Project**: TVS Plant 4 AMR Integration with Twinzo Platform
**Vendor**: Hi-tech (AMR Provider)
**Integration Method**: MQTT via Ngrok Tunnel
**Date**: 2025-10-31

---

## PoC Goal

Enable real-time tracking of Hi-tech AMRs on Twinzo platform by:
1. Hi-tech publishes AMR position data to FoF's MQTT broker
2. FoF bridges data to Twinzo API
3. TVS views live AMR positions on Twinzo platform

**Timeline**: 7 days from data format confirmation

---

## What Factories of Future Provides

**MQTT Broker (via Ngrok)**
```
Host: [Will be provided after setup]
Port: 1883 (MQTT TCP) or 9001 (WebSocket)
Protocol: MQTT v3.1.1 or v5.0
Auth: Open (no username/password required)
Topic: hitech/amr/position
QoS: 1 recommended
```

**Requirements from Hi-tech**
- Publish JSON messages to the provided topic
- Minimum 1 message per minute per AMR
- UTF-8 encoded JSON format

---

## What We Need from Hi-tech

### 1. Network Connectivity

**Can your Hi-tech AMR system make outbound MQTT connections to an external internet-facing broker, and are there any firewall or network restrictions we should be aware of?** We will host the MQTT broker via Ngrok with a public internet address (not on TVS's local network). Please confirm if your system can connect to external MQTT brokers and let us know if there are any firewall restrictions, IP whitelisting requirements, or VPN needs. Also specify which protocol works better for your setup: standard MQTT TCP on port 1883, or MQTT over WebSocket on port 9001 (useful if firewalls block standard MQTT ports).

### 2. Position Data Format and Coordinate System

**What is the actual structure of your position data, and can you provide sample messages with real coordinate values from Plant 4?** Your JSON schema shows only data types (`"location.current": "Real"`) but we need to understand the actual format with real values. Please provide 2-3 sample messages with actual coordinate values from your AMRs, including: how position coordinates are structured (separate x, y, z values or different format?), what coordinate system you use (UTM with zone number, local grid system, lat/long GPS, etc.), the units of measurement (meters, millimeters, feet), and typical coordinate ranges (example: X from 195000 to 224000, Y from 188000 to 214000). This information is critical for correctly mapping your AMR positions onto the Twinzo platform and aligning with the Plant 4 facility layout.

**Example format we expect:**
```json
{
  "headerId": 123,
  "timestamp": "2025-10-31T10:30:45.123Z",
  "event": {
    "type": "tripUpdate",
    "amrId": "AMR-01",
    "location": { "current": { "x": 220000.0, "y": 209000.0, "z": 0.0 } },
    "status": 1,
    "batteryPercentage": 85.5
  }
}
```

### 3. Update Frequency and Message Behavior

**How often does your system publish position updates, are they sent continuously or only during active trips, and what do the status values mean?** For real-time tracking on Twinzo, we need at least 1 update per minute per AMR. Your JSON shows event-based structure with tripStart, tripUpdate, and tripEnd events. Please clarify the actual update frequency of your `tripUpdate` events (every 30 seconds, every minute, every 5 minutes?), whether updates publish continuously even when AMRs are idle or only during active trips, and the mapping for your `status` byte values (example: 0 = idle, 1 = moving, 2 = error). Also confirm your timestamp format (ISO 8601 with milliseconds like "2025-10-31T10:30:45.123Z"? UTC or IST timezone?). For best visualization, we need continuous updates regardless of trip status.

### 4. Device Information and IDs

**How many Hi-tech AMRs will be integrated, what is your device ID naming convention, and can you provide a complete list of device IDs?** We need to know the total number of AMR devices deployed in TVS Plant 4 and the exact device IDs that will be publishing data to our MQTT broker. Please clarify your naming convention (examples: "AMR-01", "AMR-02" or "Byte-01", "Byte-02" or "TVS-Hitech-001") and provide the complete list of device IDs. This allows us to set up correct device mappings in Twinzo before testing begins.

### 5. Coordinate System Alignment with Plant 4 Layout

**Can you provide coordinate system reference information including origin point, axis orientation, and at least 3 anchor points to align with the Plant 4 facility layout?** To display AMRs correctly on the Twinzo platform, we need to understand how your coordinate system maps to the physical Plant 4 facility. Please provide: where your origin point (0,0) is located in the facility (example: "Southwest corner of building", "Main entrance"), the orientation of your coordinate axes (which compass direction do positive X and Y point?), and at least 3 anchor/reference points with BOTH Hi-tech coordinates AND recognizable physical location descriptions (example: "Point 1: coords (x: 220000, y: 209000) = Main Loading Dock"). The more recognizable the physical locations, the easier it is to verify correct mapping on the Twinzo visualization.

---

## Quick Reference: Expected Data Mapping

| Hi-tech Field | Maps To | Notes |
|--------------|---------|-------|
| `event.amrId` | Device ID | String identifier |
| `timestamp` | Unix timestamp | Convert to milliseconds |
| `location.current.x/y/z` | Position | Needs coordinate transform |
| `batteryPercentage` | Battery % | 0-100 range |
| `status` | Movement status | Need value definitions |

---

## Next Steps

1. **Hi-tech**: Review requirements and provide answers
2. **FoF**: Set up Ngrok tunnel and share MQTT broker details
3. **All**: Schedule 15-min kickoff call to clarify data format
