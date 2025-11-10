# Twinzo-Mock: AMR Integration System

Real-time AMR (Autonomous Mobile Robot) tracking system bridging ATI's MQTT feed to Twinzo's localization platform.

## 🎯 Overview

This system connects real AMR data from ATI's audit feed and streams it to Twinzo platform for two plants:
- **Old Plant (Sector 2)**: 7 AMRs via ATI audit feed
- **HiTech Plant (Sector 1)**: AMRs via HiveMQ Cloud

## 🏗️ Architecture

```
┌─────────────────┐    MQTTS     ┌─────────────────┐    OAuth+API    ┌─────────────────┐
│  ATI Audit Feed │ ──────────► │  Bridge (Node)  │ ──────────────► │  Twinzo API     │
│  (Real AMRs)    │             │  Authenticate   │                 │   Old Plant     │
└─────────────────┘             │  + Transform    │                 └─────────────────┘
                                └─────────────────┘
```

## 🚀 Quick Start

### Running the Audit Feed Bridge

```bash
# Start the ATI audit feed bridge
node src/bridge/bridge_audit_feed.js > logs/audit_feed_bridge.log 2>&1 &

# Monitor the bridge
tail -f logs/audit_feed_bridge.log

# Or use the unified starter (both plants)
python start_bridges.py
```

## 📊 Active AMRs (Old Plant - Sector 2)

| AMR Name | ATI Name | Battery | Status |
|----------|----------|---------|--------|
| tug-55-hosur-09 | tug-55-tvsmotor-hosur-09 | 75-85% | Active - Moving |
| tug-39-hosur-07 | tug-39-tvsmotor-hosur-07 | 68-81% | Active - Moving |
| tug-133 | tug-133 | 44-52% | Active - Stationary |
| tug-140 | tug-140 | 15-20% | Active |
| tug-78 | tug-78 | 60-73% | Active - Stationary |
| tug-24-hosur-05 | tug-24-tvsmotor-hosur-05 | 54-64% | Active - Stationary |
| tug-11 | tug-11 | 22-37% | Active - Stationary |

## 🔧 Configuration

### Environment Variables (.env)

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

# Coordinate Transform (ATI meters → Twinzo units)
AFFINE_A=1000      # X scale
AFFINE_D=1000      # Y scale
AFFINE_TX=100000   # X offset
AFFINE_TY=100000   # Y offset
```

### Coordinate Transformation

ATI coordinates (meters) are transformed to Twinzo units:

```
X_twinzo = X_ati × 1000 + 100,000
Y_twinzo = Y_ati × 1000 + 100,000
```

**Example:**
- ATI: (110.94m, 62.40m) → Twinzo: (210,940, 162,396)
- ATI: (-11.39m, 40.95m) → Twinzo: (88,610, 140,950)

## 📡 API Integration

### Twinzo Localization API

- **Auth URL**: `https://api.platform.twinzo.com/v3/authorization/authenticate`
- **Localization URL**: `https://api.platform.twinzo.com/v3/localization`
- **Headers**: `Client`, `Branch`, `Token`, `Api-Key`
- **Payload**: Array format `[{...}]`

### Sample Payload

```json
[{
  "Timestamp": 1731244858993,
  "SectorId": 2,
  "X": 210940,
  "Y": 162396,
  "Z": 0,
  "Interval": 100,
  "Battery": 85,
  "IsMoving": true,
  "LocalizationAreas": [],
  "NoGoAreas": []
}]
```

## 📁 Project Structure

```
twinzo-mock/
├── src/
│   ├── bridge/
│   │   ├── bridge_audit_feed.js    # ATI audit feed → Old Plant
│   │   ├── bridge_old_plant.py     # Alternative Python bridge
│   │   └── bridge_hitech.py        # HiveMQ → HiTech Plant
│   └── common/                      # Shared utilities
├── config/
│   └── mappings/
│       └── audit_feed_devices.json  # Device mapping
├── integrations/
│   ├── ati/                         # ATI integration utilities
│   └── twinzo/                      # Twinzo API utilities
├── scripts/
│   └── utils/
│       └── manage_twinzo_devices.py # Device management CLI
├── docs/                            # Documentation
├── logs/                            # Active bridge logs
├── archive/                         # Old/deprecated files
└── start_bridges.py                 # Unified bridge starter
```

## 🛠️ Device Management

```bash
# List all devices in both plants
python scripts/utils/manage_twinzo_devices.py list

# Create new device in Old Plant
python scripts/utils/manage_twinzo_devices.py create tugger-08-old old --title "Tugger 08"

# Delete device
python scripts/utils/manage_twinzo_devices.py delete <device_id> old
```

## 🔍 Key Features

- ✅ **Real AMR Data**: Live feed from ATI's production MQTT broker
- ✅ **Multi-Plant Support**: Old Plant (Sector 2) + HiTech Plant (Sector 1)
- ✅ **Per-Device OAuth**: Individual authentication with token caching
- ✅ **Coordinate Transform**: Configurable affine transformation
- ✅ **Movement Detection**: Smart IsMoving based on coordinate changes
- ✅ **Auto-Reconnect**: Resilient MQTT connection handling
- ✅ **Detailed Logging**: Full data flow visibility

## 📊 Current Status

**Old Plant Bridge (ATI Audit Feed):**
- Status: ✅ Active
- Connected: 7 AMRs
- Update Rate: 2-6 seconds (burst pattern)
- Transform: 1000x scale + 100k offset
- Coordinates: 88k-210k range

**Known Limitations:**
- ⚠️ Data comes in bursts with 8-11 minute gaps (ATI audit feed behavior)
- ⚠️ Coordinate alignment needs factory floor reference points for precise positioning

## 🎯 Next Steps

### Required from ATI Team:
1. **Factory floor coordinate mapping** (3-4 reference points)
   - Example: "Loading dock entrance at ATI (10, 20)"
2. **Coordinate system orientation** (which direction is X/Y axis)
3. **Factory floor plan PDF** with coordinate grid overlay

### Purpose:
Calculate proper affine transformation to align tuggers exactly with factory layout on Twinzo map.

## 🐛 Troubleshooting

### Check Bridge Status
```bash
# View recent logs
tail -50 logs/audit_feed_bridge.log

# Check for AMR data
grep "AMR:" logs/audit_feed_bridge.log | tail -10

# Verify coordinate transform
grep "Coordinate Transform:" logs/audit_feed_bridge.log
```

### Common Issues

**No movement detected:**
- Check if AMRs are actually moving (may be idle/waiting)
- 4 out of 7 AMRs are often stationary

**Connection loop:**
- Kill orphaned node processes: `ps -ef | grep node`
- Ensure only one bridge instance running

**Wrong positioning:**
- Verify AFFINE_* values in .env
- Requires factory floor reference points for accurate mapping

## 📚 Documentation

- **Production Setup**: See `docs/PRODUCTION_SETUP.md`
- **Audit Feed Analysis**: See `docs/AUDIT_FEED_ANALYSIS.md`
- **Project Guide**: See `CLAUDE.md`

---

**Status**: ✅ Production Active
**Last Updated**: November 2025
**Twinzo API Version**: v3
