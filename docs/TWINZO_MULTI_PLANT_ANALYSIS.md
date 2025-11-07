# Twinzo Multi-Plant Analysis

## Problem Summary

You want to stream data to both plants simultaneously, but there's only 1 sector in the Twinzo API while there are 2 branches. The authentication system returns the **Branch GUID** (not the sector ID), which is causing confusion.

## Current State

### Branches (Plants)
The API returns 2 branches:

1. **Plant 4 - HiTech** (NEW)
   - Branch ID: `1`
   - Branch GUID: `dcac4881-05ab-4f29-b0df-79c40df9c9c2`
   - Has sectors defined (but empty in branches response)

2. **Plant 1 - Oldest Original** (OLD)
   - Branch ID: `2`
   - Branch GUID: `40557468-2d57-4a3d-9a5e-3eede177daf5`
   - Has sectors defined (but empty in branches response)

### Sectors
The API returns only 1 sector:

1. **Sector 1** (belongs to HiTech plant)
   - Sector ID: `1` (INTEGER)
   - Sector GUID: `8010257b-d416-43e2-b1a3-cc98604bb117`
   - Branch ID: `1` (points to HiTech plant)
   - Dimensions: 265337.97 x 265337.97 mm (~265m x 265m)

### Authentication Behavior

When authenticating a device (e.g., "tugger-01"):
- Returns: `Branch: dcac4881-05ab-4f29-b0df-79c40df9c9c2` (HiTech plant GUID)
- This is the **Branch GUID**, not a sector ID
- The device is bound to HiTech plant (Branch ID 1)

## The Core Issue

### Why There's Only 1 Sector

**The old plant (Plant 1 - Oldest Original) has NO sectors defined in Twinzo.**

This is why you can't stream to both plants:
- The localization API requires a `SectorId` (integer)
- Only Plant 4 (HiTech) has a sector (SectorId: 1)
- Plant 1 (Oldest Original) has no sectors configured

### Why GUIDs Don't Work as SectorId

The localization endpoint validation shows:
```
"$[0].SectorId":["The JSON value could not be converted to System.Nullable`1[System.Int32]"]
```

This means:
- **SectorId MUST be an integer** (cannot use GUID strings)
- Branch GUIDs and Sector GUIDs are NOT valid for the SectorId field
- You must use the integer Sector ID (e.g., 1, 2, 3)

## Device-to-Branch Binding

Authentication reveals that devices are bound to branches:
- Device "tugger-01" is bound to Branch `dcac4881-05ab-4f29-b0df-79c40df9c9c2` (HiTech)
- This binding is returned in the auth response as the `Branch` field
- You cannot post data to a branch/sector that the device is not authorized for

## Solutions

### Solution 1: Create Sector for Old Plant (RECOMMENDED)

**In the Twinzo admin/configuration UI:**

1. Navigate to "Plant 1 - Oldest Original" (Branch ID 2)
2. Create a new sector for this plant:
   - Title: "Sector 1" or "Main Area"
   - Set appropriate dimensions based on your spaghetti diagram
   - Define the coordinate bounds
3. This will create a new Sector with ID `2`
4. Configure devices to be authorized for both branches

**Result:**
- Old plant will have SectorId: 2
- New plant (HiTech) has SectorId: 1
- You can stream to both by using the appropriate SectorId

### Solution 2: Device Duplication Strategy

If devices can only be bound to one branch at a time:

1. Create duplicate device entries in Twinzo:
   - `tugger-01-plant1` -> bound to old plant (Branch ID 2)
   - `tugger-01-plant4` -> bound to new plant (Branch ID 1)

2. Authenticate with different device logins based on target plant

3. Stream the same data to both devices (with appropriate SectorId)

### Solution 3: Multi-Branch Authorization (if supported)

Check if Twinzo supports multi-branch device authorization:
- A single device authorized for multiple branches
- Would allow posting to different SectorIds with the same credentials
- Requires Twinzo platform support

## Implementation Changes Needed

### Current Code (bridge.py:175)
```python
twinzo_payload = [
    {
        "Timestamp": int(time.time() * 1000),
        "SectorId": 1,  # Hardcoded to HiTech plant sector
        ...
    }
]
```

### Updated Code for Multi-Plant Support
```python
# Map devices to their target sectors
DEVICE_SECTOR_MAP = {
    "tugger-01": [1, 2],  # Post to both sectors
    "tugger-02": [1],      # Only HiTech
    "tugger-03": [2],      # Only old plant
}

# For each device, post to all mapped sectors
sector_ids = DEVICE_SECTOR_MAP.get(device_id, [1])
for sector_id in sector_ids:
    twinzo_payload = [
        {
            "Timestamp": int(time.time() * 1000),
            "SectorId": sector_id,
            ...
        }
    ]
    # Post with appropriate credentials
```

## What's Wrong with Twinzo?

To answer your question "What the fuck is wrong with Twinzo?":

1. **Inconsistent ID usage:**
   - Authentication returns Branch GUID
   - Localization requires integer Sector ID
   - No clear mapping between the two in the API

2. **Poor API documentation:**
   - No clear indication that SectorId must be integer
   - Error messages are generic validation errors
   - No explanation of Branch vs Sector relationship

3. **Incomplete data structure:**
   - Branches endpoint returns `"Sectors": []` (always empty)
   - Can't get branch details by GUID
   - No way to query which sectors belong to which branch via API

4. **Configuration-dependent:**
   - The old plant exists but has no sectors
   - This is a configuration issue on the Twinzo admin side
   - API should prevent or warn about plants without sectors

## Next Steps

1. **Immediate**: Check Twinzo admin UI to see if old plant has sectors
2. **If no sectors exist**: Create sector for old plant (Solution 1)
3. **Configure devices**: Ensure devices are authorized for both branches
4. **Test authentication**: Verify which branch each device is bound to
5. **Update bridge code**: Add multi-sector posting capability
6. **Test streaming**: Verify data appears in both plant visualizations

## Testing Commands

```bash
# Check device authorization for different plants
python -X utf8 scripts/verification/investigate_twinzo_structure.py

# Test posting to multiple sectors
# (After creating sector for old plant)
python -X utf8 tests/integration/test_multi_plant_streaming.py
```

## References

- Old Plant GUID: `40557468-2d57-4a3d-9a5e-3eede177daf5`
- New Plant GUID: `dcac4881-05ab-4f29-b0df-79c40df9c9c2`
- HiTech Sector GUID: `8010257b-d416-43e2-b1a3-cc98604bb117`
- HiTech Sector ID: `1` (integer)
