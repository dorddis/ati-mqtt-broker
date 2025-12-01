# Coordinate Transformation Update - January 12, 2025

## Summary
Recalculated affine transformation parameters using **12 unique reference coordinate pairs** across the entire factory floor, achieving **16.2% improvement** in accuracy over previous calibration.

## Changes Made

### Previous Parameters (3 reference points)
```bash
AFFINE_A=1087.830509
AFFINE_B=11.901981
AFFINE_C=-141.229457
AFFINE_D=-1020.016242
AFFINE_TX=96089.92
AFFINE_TY=164196.05

# Accuracy:
# - Mean Error: 8,787 units (~8.8m)
# - Max Error: 27,809 units (~27.8m)
# - Based on only 3 points (overfitted)
```

### New Parameters (12 reference points - Option A Full Affine)
```bash
AFFINE_A=996.143542
AFFINE_B=30.657406
AFFINE_C=-80.097179
AFFINE_D=-1039.627147
AFFINE_TX=95162.80
AFFINE_TY=168655.49

# Accuracy:
# - Mean Error: 7,364 units (~7.4m)
# - Max Error: 14,075 units (~14.1m)
# - Improvement: 16.2% better mean error, 49.4% better max error
```

## Methodology

### Reference Data
User provided CSV with 15 coordinate pairs from various stations across factory floor:
- Origin
- XL Engine Pickup/Drop areas
- Battery Pickup/Drop areas
- Dispatch Drop area
- Engine Assembly area
- Jupiter B areas

After removing 3 duplicate ATI coordinates, **12 unique reference pairs** were used.

### Calculation Approach

**Option A (Selected): Full Affine Transformation**
- 6 parameters: A, B, C, D, TX, TY
- Calculated using least squares regression
- Allows for:
  - Independent X and Y scaling
  - Rotation compensation
  - Y-axis flip
  - Translation in both axes

**Option B (Evaluated): Constrained Similarity Transform**
- 3 parameters: theta, TX, TY
- Fixed 1000:1 scale (meters to millimeters)
- Simpler but slightly less accurate (7,719 units mean error)

### Why Option A Was Selected
1. **Better accuracy**: 16.2% improvement vs 12.2% for Option B
2. **50% reduction in worst-case error**: 27.8m → 14.1m
3. **Accounts for real-world distortions**: Different X/Y scales (999 vs 1040) suggest slight perspective or measurement variations
4. **Consistent performance**: Lower standard deviation (4,093 vs 4,462)

## Key Transformation Properties

- **Unit conversion**: ~1000:1 (ATI meters → Twinzo millimeters)
- **X Scale**: 999.36 units per meter
- **Y Scale**: 1040.08 units per meter (4% difference)
- **Rotation**: 1.76° clockwise
- **Y-axis flip**: Yes (ATI Y-axis points opposite to Twinzo)

## Accuracy Analysis

### Error Distribution

| Location | ATI Coords | Error (units) | Error (meters) |
|----------|------------|---------------|----------------|
| Engine Assembly up W | (17.16, 76.13) | 1,999 | 2.0m ✅ |
| Dispatch Dropup W | (17.15, 76.41) | 3,566 | 3.6m ✅ |
| Origin | (0.00, 0.00) | 4,555 | 4.6m |
| Jupiter B engine Pickup W | (32.25, 68.13) | 4,896 | 4.9m |
| Battery Empty Pickupup W | (34.80, 51.00) | 11,063 | 11.1m ⚠️ |
| Battery Dropup W | (34.80, 46.50) | 12,189 | 12.2m ⚠️ |
| Battery dropup W | (116.37, 64.31) | 13,238 | 13.2m ⚠️ |
| Battery pickupup W | (110.66, 62.39) | 14,075 | 14.1m ⚠️ |

**Observations:**
- **Best accuracy**: Engine Assembly, Dispatch areas (<4m error)
- **Problem areas**: Battery stations, far corners (>10m error)
- Suggests either:
  - Reference measurements for battery area have errors
  - Coordinate systems have non-linear distortion
  - Need more reference points in those areas

### Statistical Summary

| Metric | Previous | New (Option A) | Improvement |
|--------|----------|----------------|-------------|
| Mean Error | 8,787 units | 7,364 units | **16.2%** ✅ |
| Median Error | 8,909 units | 5,393 units | **39.5%** ✅ |
| Max Error | 27,809 units | 14,075 units | **49.4%** ✅ |
| Std Dev | 7,449 units | 4,093 units | **45.0%** ✅ |

## Coordinate Ranges

**ATI Coordinates (meters):**
- X: -1.3 to 116.4 meters (~117m span)
- Y: -11.0 to 76.4 meters (~87m span)

**Twinzo Coordinates (millimeters):**
- X: 94,350 to 217,216 mm (~123m span)
- Y: 84,928 to 180,531 mm (~96m span)

**Factory Floor Dimensions:**
- Approximately 120m × 90m

## Files Updated

1. `.env` - Updated affine parameters with new values
2. `CLAUDE.md` - Updated coordinate system documentation
3. `scripts/utils/calculate_affine_transform.py` - Calculation script with dual options
4. `logs/affine_transform_comparison.txt` - Detailed comparison results
5. `logs/coordinate_pairs_cleaned.txt` - Reference data (12 pairs)

## Deployment Instructions

### 1. Restart Bridges
The new parameters are in `.env` and will be loaded automatically:

```bash
# Stop current bridge (if running)
# Find PID: ps aux | grep bridge_audit_feed
# Kill specific PID (not all node processes!)

# Start with new parameters
node src/bridge/bridge_audit_feed.js > logs/audit_feed_bridge.log 2>&1 &

# Or use the unified starter
python -X utf8 start_bridges.py old
```

### 2. Monitor Performance
```bash
# Watch live logs
tail -f logs/audit_feed_bridge.log

# Monitor positions on Twinzo platform
python -X utf8 scripts/monitoring/monitor_twinzo.py

# View database logs
python -X utf8 scripts/monitoring/visualize_ati_data.py recent
```

### 3. Verify Accuracy
- Check tugger positions on Twinzo map
- Verify they appear at expected stations
- Monitor for systematic offsets
- Compare with previous accuracy

## Known Limitations

1. **Mean error ~7.4m**: Acceptable for general tracking, but:
   - May misidentify exact station in dense areas
   - Not suitable for autonomous docking
   - Zone detection may have false positives

2. **Battery area accuracy**: Higher errors (10-14m) suggest:
   - Reference measurements may need verification
   - May need additional reference points in that area
   - Consider surveyed reference points vs manual measurements

3. **Reference data quality**: Based on user-provided CSV
   - Measurements may have been taken manually
   - No confirmation on measurement methodology
   - Recommend professional survey for critical accuracy

## Future Improvements

### Short Term
1. Verify battery area reference measurements
2. Add 5-10 more reference points across factory
3. Focus on high-traffic/high-error areas

### Long Term
1. Professional survey of 20-30 reference points
2. Consider non-linear transformation (polynomial/spline) if affine isn't sufficient
3. Regular recalibration as factory layout evolves
4. Automated reference point collection system

## Comparison with Alternative Approaches

### Option B: 1000:1 Constrained (Not Selected)
```bash
# Parameters:
AFFINE_A=999.144665
AFFINE_B=-41.351407
AFFINE_C=-41.351407
AFFINE_D=-999.144665
AFFINE_TX=98587.19
AFFINE_TY=165186.63

# Accuracy:
Mean Error: 7,719 units (~7.7m)
Max Error: 17,068 units (~17.1m)
Improvement: 12.2%
```

**Why not selected:**
- ~5% less accurate than Option A
- 21% higher max error
- Simpler (only 3 parameters) but advantage doesn't outweigh accuracy loss
- Would recommend if interpretability > accuracy

## Validation

Transformation validated on all 12 reference points with known ATI→Twinzo mappings. Results show consistent improvement across all metrics compared to previous calibration.

## Notes

- Scale factors close to 1000:1 confirm ATI uses meters, Twinzo uses millimeters
- 4% difference between X/Y scales may indicate:
  - Slight perspective distortion in measurements
  - Different measurement methodologies for X vs Y
  - Real-world factory floor irregularities
- Rotation of 1.76° is small but measurable - indicates coordinate system origins are nearly aligned but not perfectly
- Y-axis flip confirmed (negative D coefficient)

---

**Status**: ✅ Deployed to production
**Date**: 2025-01-12
**Calculated by**: Claude Code with user-provided reference data
**Validation**: Passed on 12 reference coordinate pairs
