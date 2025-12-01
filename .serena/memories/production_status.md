# Production Status - Twinzo Mock Bridge

Updated: 2025-01-12

## Active Production Setup

### Old Plant (Sector 2) - ATI Audit Feed ✅ ACTIVE

**Bridge**: `src/bridge/bridge_audit_feed.js` (Node.js)
**Data Source**: ATI MQTTS Audit Feed
**Target**: Twinzo Old Plant (Sector 2)
**Status**: Production, streaming live data

**MQTT Connection:**
- Host: `tvs-dev.ifactory.ai:8883` (MQTT5 with TLS)
- Username: `tvs-audit-user`
- Password: `TVSAudit@2025`
- Client ID: Must match username
- Topics: `ati_fm/#` (wildcard), `fleet/trips/info`
- QoS: 1

**Active AMRs (3 devices):**
1. `tug-55-tvsmotor-hosur-09` → `tug-55-hosur-09`
2. `tug-39-tvsmotor-hosur-07` → `tug-39-hosur-07`
3. `tug-133` → `tug-133`

**Disabled AMRs** (data ignored):
- tug-140, tug-78, tug-24-tvsmotor-hosur-05, tug-11

**Data Format:**
- `sherpa_name`: Device identifier
- `pose`: [x, y, heading] array in unknown units (assumed meters)
- `battery_status`: 0-100%
- `mode`: "fleet" (moving) or "disconnected"
- Update frequency: 2-6 seconds (burst pattern with 8-11 min gaps)

### HiTech Plant (Sector 1) - DISABLED

**Bridge**: `src/bridge/bridge_hitech.py` (Python)
**Status**: Not currently in production

## Environment Variables

```bash
# Twinzo API
TWINZO_CLIENT=TVSMotor
TWINZO_PASSWORD=Tvs@Hosur$2025
TWINZO_API_KEY=sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S

# ATI Audit Feed
AUDIT_MQTT_HOST=tvs-dev.ifactory.ai
AUDIT_MQTT_PORT=8883
AUDIT_USERNAME=tvs-audit-user
AUDIT_PASSWORD=TVSAudit@2025

# Affine Transform (Option C - 3 best points)
AFFINE_A=1087.830509
AFFINE_B=11.901981
AFFINE_C=-141.229457
AFFINE_D=-1020.016242
AFFINE_TX=96089.92
AFFINE_TY=164196.05
```

## Starting the Bridge

```bash
# Manual start
node src/bridge/bridge_audit_feed.js

# Background (with logging)
node src/bridge/bridge_audit_feed.js > logs/audit_feed_bridge.log 2>&1 &

# Or use starter script
python -X utf8 start_bridges.py old
```

## Monitoring

```bash
# Check database stats
python -X utf8 scripts/monitoring/visualize_ati_data.py stats

# View recent data
python -X utf8 scripts/monitoring/visualize_ati_data.py recent tug-55-tvsmotor-hosur-09

# Quick query
node scripts/monitoring/query_database.js
```

## Known Issues

1. **Coordinate precision**: ~5% error due to limited reference points (only 4 pairs)
2. **Data bursts**: ATI sends data in bursts, not continuous stream (8-11 min gaps)
3. **Unit uncertainty**: ATI coordinate units not confirmed (assumed meters)

## Pending Improvements

1. **Better calibration data**: Request 15-20 coordinate pairs from ATI
2. **Continuous streaming**: Investigate ATI data burst pattern
3. **Unit confirmation**: Get ATI documentation on coordinate units
