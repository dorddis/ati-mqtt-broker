# Factory Floor Coordinate Mapping - Completed

## Summary

Successfully mapped the TVS Motor Plant 4 factory floor coordinate system through systematic testing with tuggers on the Twinzo platform.

## Final Verified Coordinates

```json
{
  "bounds": {
    "x_min": 0,
    "x_max": 265000,
    "y_min": 46000,
    "y_max": 218000
  },
  "dimensions": {
    "width": 265000,
    "height": 172000
  }
}
```

## Verified Corner Positions

| Corner | X | Y | Status |
|--------|---|---|--------|
| Top-Left | 0 | 46,000 | ✓ Verified on floor |
| Top-Right | 265,000 | 46,000 | ✓ Verified on floor |
| Bottom-Left | 0 | 218,000 | ✓ Verified on floor |
| Bottom-Right | 265,000 | 218,000 | ✓ Verified on floor |

## Coordinate System Orientation

- **X-axis**: Increases from LEFT (0) to RIGHT (265k)
- **Y-axis**: Increases from TOP (46k) to BOTTOM (218k)
- **Z-axis**: Not tested (assumed 0 for floor level)

## Testing Methodology

1. **LEFT edge discovery**: Tested X=0, 25k, 50k, 75k, 100k → Confirmed X=0
2. **RIGHT edge discovery**: Tested X=200k, 225k, 250k, 275k, 300k → Found between 250k-275k → Refined to 265k
3. **TOP edge discovery**: Tested Y=0, 25k, 42k, 46k, 50k, 75k → Refined to 46k
4. **BOTTOM edge discovery**: Tested Y=200k, 218k, 220k, 225k, 250k → Refined to 218k
5. **Corner verification**: All 4 corners placed and visually confirmed on Twinzo platform

## Devices Used for Testing

- tugger-01 (OAuth: tugger-01)
- tugger-02 (OAuth: tugger-02)
- tugger-03 (OAuth: tugger-03)
- tugger-04 (OAuth: tugger-04)

## Configuration File

Coordinates saved to: `config/factory_floor_coordinates.json`

## Testing Tool

Command-line tool created: `place_tuggers.py`

Usage:
```bash
# Place single tugger
python -X utf8 place_tuggers.py 1 <x> <y>

# Place all tuggers
python -X utf8 place_tuggers.py all "x1,y1" "x2,y2" "x3,y3" "x4,y4"
```

## Next Steps for Hi-tech Integration

1. Share coordinate bounds with Hi-tech:
   - X range: 0 to 265,000
   - Y range: 46,000 to 218,000

2. Hi-tech must configure their AMRs to publish positions within these bounds

3. Test Hi-tech AMR data on Twinzo platform to verify correct positioning

4. Establish anchor points: Map physical factory locations to coordinates for validation

## Archived Files

All coordinate testing scripts moved to `archive/`:
- test_twinzo_live.py
- test_coordinates.py
- find_bounds.py
- map_factory.py
- find_left_edge.py
- grid_coordinate_test.py
- test_four_corners.py

## Date Completed

November 3, 2025
