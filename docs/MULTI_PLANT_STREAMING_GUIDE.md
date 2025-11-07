# Multi-Plant Streaming Guide

## Overview

The bridge now supports streaming AMR data to **multiple Twinzo plants simultaneously**. This allows you to visualize the same AMR data on both the HiTech plant and the Old Plant layouts.

## Sector Configuration

Based on testing, the following sector IDs are confirmed:

| Plant | Sector Name | Sector ID | Branch ID | Branch GUID |
|-------|-------------|-----------|-----------|-------------|
| **HiTech Plant** | Sector 1 | `1` | 1 | `dcac4881-05ab-4f29-b0df-79c40df9c9c2` |
| **Old Plant** | Main | `2` | 2 | `40557468-2d57-4a3d-9a5e-3eede177daf5` |

### Sector Dimensions

- **HiTech (Sector 1)**: 265.34m x 265.34m
- **Old Plant (Sector 2)**: 250m x 250m

## Configuration

### Environment Variable

The `SECTOR_IDS` environment variable controls which plants receive data:

```bash
# Stream to both plants (default)
SECTOR_IDS=1,2

# Stream to HiTech only
SECTOR_IDS=1

# Stream to Old Plant only
SECTOR_IDS=2

# Stream to three plants (if you add more)
SECTOR_IDS=1,2,3
```

### Default Behavior

**By default, the bridge streams to BOTH plants** (SECTOR_IDS=1,2).

## Usage

### Option 1: Using Default (Both Plants)

Simply run the bridge without setting SECTOR_IDS:

```bash
# Standard MQTT bridge
python -X utf8 src/bridge/bridge.py

# WebSocket bridge (for ATI integration)
python -X utf8 integrations/ati/websocket_bridge_to_twinzo.py
```

This will stream to both HiTech and Old Plant automatically.

### Option 2: Specify Sectors

```bash
# Windows PowerShell
$env:SECTOR_IDS="1,2"
python -X utf8 src/bridge/bridge.py

# Windows CMD
set SECTOR_IDS=1,2
python -X utf8 src/bridge/bridge.py

# Linux/Mac
export SECTOR_IDS=1,2
python -X utf8 src/bridge/bridge.py
```

### Option 3: Stream to Single Plant

```bash
# Only HiTech
$env:SECTOR_IDS="1"
python -X utf8 src/bridge/bridge.py

# Only Old Plant
$env:SECTOR_IDS="2"
python -X utf8 src/bridge/bridge.py
```

## Testing

### Test Multi-Plant Streaming

Run the integration test to verify both plants are accessible:

```bash
python -X utf8 tests/integration/test_multi_plant_streaming.py
```

Expected output:
```
HiTech Plant (Sector 1): SUCCESS
Old Plant (Sector 2): SUCCESS

GREAT NEWS! Both plants are accessible!
```

### Live Streaming Test

1. Start the bridge:
   ```bash
   python -X utf8 src/bridge/bridge.py
   ```

2. Start the publisher (generates mock AMR data):
   ```bash
   python -X utf8 src/publisher/publisher.py
   ```

3. Check the bridge logs - you should see:
   ```
   POST ok 200 for tugger-01 to Sector 1 (X:..., Y:..., Battery:...%, Moving:...)
   POST ok 200 for tugger-01 to Sector 2 (X:..., Y:..., Battery:...%, Moving:...)
   ```

4. Open both plants in Twinzo UI:
   - HiTech Plant: https://platform.twinzo.com/branch/dcac4881-05ab-4f29-b0df-79c40df9c9c2
   - Old Plant: https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5

5. Verify AMRs appear on both layouts

## How It Works

### Authentication

- Devices authenticate to a specific branch (e.g., tugger-01 authenticates to HiTech)
- Authentication returns OAuth token, client ID, and branch GUID
- **Key finding**: The same credentials can post to ANY sector, not just the authenticated branch

### Data Flow

For each MQTT message:

1. Device authenticates (or uses cached token)
2. Extract pose data (X, Y, Z, theta)
3. Apply coordinate transformation (if configured)
4. Calculate battery and movement status
5. **For each sector in SECTOR_IDS:**
   - Create localization payload with that SectorId
   - POST to Twinzo API
   - Log success/failure

### Performance Impact

- Each sector adds one additional API call per message
- With 2 sectors and 3 robots at 10Hz: 60 API calls/second
- Twinzo API handles this load without issues

## Troubleshooting

### Issue: Only seeing data on one plant

**Solution**: Check SECTOR_IDS environment variable
```bash
echo $env:SECTOR_IDS  # PowerShell
echo %SECTOR_IDS%     # CMD
```

### Issue: POST failed for Sector 2

**Possible causes**:
1. Old plant sector not configured in Twinzo
2. Incorrect sector ID (should be integer, not GUID)
3. Network/API issues

**Debug**:
```bash
python -X utf8 tests/integration/test_multi_plant_streaming.py
```

### Issue: Different coordinates on each plant

This is **expected behavior** if plants have different layouts. The same X/Y coordinates will appear at different visual positions on each plant's map.

**Solution**: Use different coordinate transformations per sector (future enhancement).

## Future Enhancements

### Per-Sector Coordinate Transforms

Currently, the same affine transformation is applied to all sectors. Future versions could support:

```bash
SECTOR_1_AFFINE_A=1.0
SECTOR_1_AFFINE_TX=0.0
SECTOR_2_AFFINE_A=0.95
SECTOR_2_AFFINE_TX=5000.0
```

### Device-to-Sector Mapping

Allow different devices to stream to different sectors:

```bash
TUGGER_01_SECTORS=1,2  # Both plants
TUGGER_02_SECTORS=1    # HiTech only
TUGGER_03_SECTORS=2    # Old plant only
```

### Sector Discovery

Auto-discover available sectors from Twinzo API instead of hardcoding.

## Summary

The multi-plant streaming feature allows you to:

- ✅ Stream to both HiTech and Old Plant simultaneously
- ✅ Use a single device authentication for multiple plants
- ✅ Configure which sectors to stream to via environment variable
- ✅ Default to streaming to both plants for convenience
- ✅ Test with integration test script

**Default configuration streams to BOTH plants** - just run the bridge and it works!
