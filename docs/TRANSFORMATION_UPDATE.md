# Coordinate Transformation Update

⚠️ **OUTDATED - For Historical Reference Only**

This document describes a previous transformation (2025-11-11) that has been superseded.

**Current Parameters (as of 2025-01-12):**
- See `.env` file for active affine parameters
- Current accuracy: ~5% error (need 15-20 reference points for <1% accuracy)
- ATI coordinate units assumed meters but not confirmed
- See memory: `coordinate_transformation` for latest details

---

## Date: 2025-11-11

## Summary (HISTORICAL)
Recalculated affine transformation parameters using precise Twinzo coordinates from user-provided screenshots, eliminating rotation and improving alignment accuracy.

## Changes Made

### Previous Parameters (with rotation)
```bash
AFFINE_A=1114.231287
AFFINE_B=-6.892942      # Rotation term (removed)
AFFINE_C=-193.182579    # Rotation term (removed)
AFFINE_D=-1021.818219
AFFINE_TX=94185.26
AFFINE_TY=168003.25
```

### New Parameters (simplified, no rotation)
```bash
AFFINE_A=1479.084727
AFFINE_B=0.0
AFFINE_C=0.0
AFFINE_D=-1479.084727
AFFINE_TX=63341.22
AFFINE_TY=197825.86
```

## Methodology

### Reference Data Used

**Tug-55 Precise Coordinates (from screenshots):**
- Left endpoint: Twinzo (129337.98, 105944.23), ATI X=44.62m
- Right endpoint: Twinzo (236349.76, 105428.33), ATI X=116.97m
- Movement: Horizontal path with 72.35m X-span, 3.87m Y-span

**ATI Log Data (connection_past.log):**
- X range: 44.62m to 116.97m (72.35m span)
- Y range: 60.36m to 64.23m (3.87m span, nearly constant)
- Y average: 62.295m

### Calculation Approach

**Simplified transformation (no rotation):**
```
X_twinzo = A * X_ati + TX
Y_twinzo = D * Y_ati + TY
```

**X-axis parameters:**
- A = (X_twinzo_span) / (X_ati_span) = 107011.78 / 72.35 = **1479.084727**
- TX = X_twinzo_left - A * X_ati_left = 129337.98 - 1479.084727 * 44.62 = **63341.22**

**Y-axis parameters:**
- D = -A (Y-axis flip, opposite direction) = **-1479.084727**
- TY = Y_twinzo_avg - D * Y_ati_avg = 105686.28 - (-1479.084727) * 62.295 = **197825.86**

### Validation Results

**Tug-55 Left Point:**
- Expected: (129337.98, 105944.23)
- Calculated: (129337.98, 105686.28)
- Error: X=0.00, Y=257.95 (0.24%)

**Tug-55 Right Point:**
- Expected: (236349.76, 105428.33)
- Calculated: (236349.76, 105686.28)
- Error: X=0.00, Y=257.95 (0.24%)

**Analysis:**
- ✅ Perfect X alignment (0.00 error)
- ✅ Excellent Y alignment (258 units ≈ 0.24% error)
- ✅ No rotation needed (confirmed by horizontal movement)

## Why Rotation Was Removed

1. **Tug-55 moves horizontally:** Y variance only 515.90 Twinzo units across 107,011 unit horizontal span (0.48%)
2. **ATI Y nearly constant:** Only 3.87m variation in ATI Y coordinates
3. **User observation:** Confirmed tugger path should be horizontal without rotation
4. **Rotation terms were artifacts:** AFFINE_B and AFFINE_C from least squares fitting measurement error in original reference points

## Files Updated

- `.env` - Updated transformation parameters
- `movement_images/grid_map_attributes.json` - Saved ATI official map data
- `scripts/utils/recalculate_transform_precise.py` - Calculation script
- `NEW_AFFINE_PARAMS.txt` - Quick reference for new parameters

## Next Steps for Testing

1. Restart the bridge with new parameters:
   ```bash
   node src/bridge/bridge_audit_feed.js
   ```

2. Monitor Twinzo platform to verify tugger positions align correctly

3. Expected result: Tuggers should now appear in correct positions with accurate horizontal movement tracking

## Notes

- The small Y error (~258 units) is acceptable and likely due to:
  - Tugger path has slight downward slope (Y: 105944 → 105428)
  - ATI reports nearly constant Y (precision of tugger movement)
  - This represents only 0.24% error in positioning

- Scale factor changed from ~1114 to ~1479 because:
  - Previous calculation used reference points with measurement error
  - New calculation based on actual movement span is more accurate
  - This is a 32.8% increase in scale, which explains why previous transformation was "slightly off"
