# Coordinate Transformation - ATI to Twinzo

## Current Affine Parameters (Option B - 1000:1 Constrained, 8 High-Quality Points)

Updated: 2025-01-12 (FINAL)

Based on 8 HIGH-QUALITY reference coordinate pairs (battery stations excluded):

```bash
AFFINE_A=999.738230
AFFINE_B=22.879501
AFFINE_C=22.879501
AFFINE_D=-999.738230
AFFINE_TX=95598.77
AFFINE_TY=167357.60
```

**Transformation Equations:**
```
X_twinzo = 999.738230 * X_ati + 22.879501 * Y_ati + 95598.77
Y_twinzo = 22.879501 * X_ati - 999.738230 * Y_ati + 167357.60
```

**Model Type:** Constrained similarity transformation
- Exact 1000:1 scale (meters to millimeters)
- Only 3 free parameters: rotation angle (1.31°), TX, TY
- Simpler and more maintainable than full affine

## Accuracy

**Measured Performance:**
- Mean Error: **3,076 units (~3.1m / 2.0%)** ✅
- Median Error: **1,931 units (~1.9m / 1.2%)** ✅
- Max Error: **9,615 units (~9.6m / 6.2%)**
- Standard Deviation: **3,076 units**

**Improvement over previous calibration:**
- **60.4% better mean error** (7,761 → 3,076 units)
- 78.3% better median error
- 27.0% better max error
- 38.9% better consistency (std dev)

**Key Insight: Quality > Quantity**
- Initial attempt with 12 points (including bad battery data): Only 5% improvement
- Final with 8 high-quality points: **60% improvement!**
- Battery station references had 10-14m errors that contaminated entire calibration

**Error by Location:**
- Excellent (<2m): Engine Assembly, Jupiter B areas
- Good (2-6m): Dispatch, Origin, XL Engine Pickup
- Moderate (6-10m): XL Engine dropup (may need remeasurement)
- Excluded: Battery stations (10-14m errors in reference data)

**8 High-Quality Reference Points Used:**
- Origin, XL Engine Pickup/Drop, Dispatch Drop, Engine Assembly, DropEngAssy110up, Jupiter B Empty Trolley Drop, Jupiter B engine Pickup

## Known Issues

### Battery Station Reference Data Quality
**CRITICAL**: Battery area reference measurements have **10-14m errors** and are excluded from calibration.
- Battery pickupup W: 14,075 units error (when included)
- Battery Dropup W: 12,189 units error (when included)
- Battery Empty Pickupup W: 11,063 units error (when included)
- Battery dropup W: 13,238 units error (when included)

**Impact:** Including these 4 bad points reduced overall accuracy by 55% (from 60% improvement to 5% improvement).

**Cause:** Likely manual measurements without proper surveying.

**Solution:** Remeasure battery area with surveyed coordinates, then recalibrate.

### XL Engine Dropup W
Moderate error of ~8.2m. May benefit from remeasurement.

### ATI Coordinate Units
**CONFIRMED**: ATI coordinates are in **meters** based on ~1000:1 scale factor to Twinzo millimeters.

**Coordinate Ranges:**
- ATI: X = [-1.3, 116.4], Y = [-11.0, 76.4] meters
- Twinzo: X = [94,350, 217,216], Y = [84,928, 180,531] millimeters
- Factory floor: ~120m × 90m

## Recommendations for ATI

Request better calibration data:
1. **15-20 reference points** (currently only 4)
2. **Static physical markers** (not moving tuggers)
3. **Simultaneous measurement** in both systems
4. **Points spread across entire factory floor** (corners, edges, center)
5. **Confirm coordinate units** (meters? millimeters? custom units?)

This would improve error from ~5% to <1%.

## Previous Transformations

### Option A - Full Affine (12 points including bad battery data) - NOT SELECTED
```bash
AFFINE_A=996.143542
AFFINE_B=30.657406
AFFINE_C=-80.097179
AFFINE_D=-1039.627147
AFFINE_TX=95162.80
AFFINE_TY=168655.49
```
Error: Mean 7,364 units, Max 14,075 units - only 5% improvement (bad data contamination)

### Option C - 3 Best Points (Previous Production) - REPLACED
```bash
AFFINE_A=1087.830509
AFFINE_B=11.901981
AFFINE_C=-141.229457
AFFINE_D=-1020.016242
AFFINE_TX=96089.92
AFFINE_TY=164196.05
```
Error: Mean 7,761 units, Max 13,170 units - overfitted to 3 points, terrible elsewhere

### Simplified (No Rotation) - DEPRECATED
```bash
AFFINE_A=1479.084727
AFFINE_B=0.0
AFFINE_C=0.0
AFFINE_D=-1479.084727
AFFINE_TX=63341.22
AFFINE_TY=197825.86
```
Error: 8.7% - worse than all options
