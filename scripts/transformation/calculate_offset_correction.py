"""
Calculate the offset correction needed based on user's reference points.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Current transformation parameters
AFFINE_A = float(os.getenv('AFFINE_A', '1114.231287'))
AFFINE_B = float(os.getenv('AFFINE_B', '-6.892942'))
AFFINE_C = float(os.getenv('AFFINE_C', '-193.182579'))
AFFINE_D = float(os.getenv('AFFINE_D', '-1021.818219'))
AFFINE_TX = float(os.getenv('AFFINE_TX', '94185.26'))
AFFINE_TY = float(os.getenv('AFFINE_TY', '168003.25'))


def transform_current(x_ati, y_ati):
    """Current transformation."""
    x_twinzo = AFFINE_A * x_ati + AFFINE_B * y_ati + AFFINE_TX
    y_twinzo = AFFINE_C * x_ati + AFFINE_D * y_ati + AFFINE_TY
    return x_twinzo, y_twinzo


# User's reference points from movement images
print("=" * 80)
print("OFFSET CORRECTION ANALYSIS")
print("=" * 80)
print()

# Tug-55 reference points from user
print("TUG-55 Reference Points (from user's screenshots):")
tug55_left = (129337.98, 105944.23)
tug55_right = (236349.76, 105428.33)
print(f"  Left:  X={tug55_left[0]:.2f}, Y={tug55_left[1]:.2f}")
print(f"  Right: X={tug55_right[0]:.2f}, Y={tug55_right[1]:.2f}")
print(f"  Y variance: {abs(tug55_right[1] - tug55_left[1]):.2f} (nearly horizontal)")
print()

# Tug-55 actual data from log (one sample)
print("TUG-55 Actual Data (from ATI MQTT):")
tug55_ati_sample = (116.15, 64.23)  # From log file
tug55_transformed = transform_current(tug55_ati_sample[0], tug55_ati_sample[1])
print(f"  ATI: X={tug55_ati_sample[0]:.2f}m, Y={tug55_ati_sample[1]:.2f}m")
print(f"  Current Transform: X={tug55_transformed[0]:.2f}, Y={tug55_transformed[1]:.2f}")
print()

# Expected position (approximate - should be between left and right)
# Since X=116.15m is toward the right end (max was 116.97m, min was 44.62m)
# It should be closer to the right point
expected_y = tug55_right[1]  # Use right point Y since it's near the right end
print(f"  Expected Y position: ~{expected_y:.2f}")
print()

# Calculate offset error
print("OFFSET ERROR:")
y_error = expected_y - tug55_transformed[1]
print(f"  Y Error: {y_error:.2f} (need to shift {abs(y_error):.0f} units {'down' if y_error > 0 else 'up'})")
print()

# The Y error tells us how much to adjust AFFINE_TY
print("CORRECTION NEEDED:")
print(f"  Current AFFINE_TY: {AFFINE_TY:.2f}")
print(f"  Suggested AFFINE_TY: {AFFINE_TY + y_error:.2f}")
print()

# Check if we should also simplify by removing rotation
print("=" * 80)
print("ROTATION ANALYSIS")
print("=" * 80)
print()
print("User observation: Tug-55 moves horizontally (confirmed by Y variance of only 516 units)")
print()
print("Current transformation includes rotation terms:")
print(f"  AFFINE_B = {AFFINE_B:.6f} (small, probably not needed)")
print(f"  AFFINE_C = {AFFINE_C:.6f} (larger, causes Y to change with X)")
print()
print("RECOMMENDATION: Try simplified transformation WITHOUT rotation:")
print()
print("  X_twinzo = AFFINE_A * X_ati + AFFINE_TX")
print("  Y_twinzo = AFFINE_D * Y_ati + AFFINE_TY")
print()
print("This means set AFFINE_B = 0 and AFFINE_C = 0")
print()

# Test simplified transformation
print("=" * 80)
print("TESTING SIMPLIFIED TRANSFORMATION")
print("=" * 80)
print()

# With simplified transform (no rotation), recalculate offset
# Using the horizontal movement of tug-55 as reference
# Average Y should be around 105,686 (average of left and right)
avg_ref_y = (tug55_left[1] + tug55_right[1]) / 2

print("Using tug-55 horizontal path as reference:")
print(f"  Average Y on map: {avg_ref_y:.2f}")
print()

# For simplified transform: Y_twinzo = AFFINE_D * Y_ati + AFFINE_TY
# We have Y_ati = 64.23m and want Y_twinzo ≈ 105,686
# So: 105,686 = AFFINE_D * 64.23 + AFFINE_TY
# With AFFINE_D = -1021.818219:
# 105,686 = -1021.818219 * 64.23 + AFFINE_TY
# AFFINE_TY = 105,686 + 1021.818219 * 64.23

y_ati_sample = 64.23
desired_y_twinzo = avg_ref_y

new_affine_ty = desired_y_twinzo - (AFFINE_D * y_ati_sample)

print("Calculated AFFINE_TY for simplified transform:")
print(f"  AFFINE_TY = {new_affine_ty:.2f}")
print()

# For X offset, use the reference points similarly
# X range in ATI: 44.62m to 116.97m (span 72.35m)
# X range in Twinzo: 129,338 to 236,350 (span 107,012)
# For X=116.15m (near max), should be around 223,000 - looks about right
# But let's be more precise

# From the data: when X_ati=116.15m, we got X_twinzo=223,165
# Reference suggests it should be closer to 236,350 (right end)
# But actually, X=116.15m might not be at the exact right end

# Let's use the left point as reference instead
# Need an ATI coordinate that corresponds to the left point
# From log: X_ati=44.62m to 116.97m
# Left point at Twinzo X=129,338

# Simple approach: calculate what AFFINE_TX should be for X to align
# Using left-most point from ATI data: X_ati=44.62m → should give X_twinzo≈129,338
x_ati_left = 44.62
desired_x_left = tug55_left[0]

new_affine_tx = desired_x_left - (AFFINE_A * x_ati_left)

print("Calculated AFFINE_TX for simplified transform:")
print(f"  AFFINE_TX = {new_affine_tx:.2f}")
print()

print("=" * 80)
print("RECOMMENDED NEW PARAMETERS")
print("=" * 80)
print()
print("SIMPLIFIED TRANSFORMATION (no rotation):")
print(f"  AFFINE_A  = {AFFINE_A:.6f}  (keep)")
print(f"  AFFINE_B  = 0.0  (remove rotation)")
print(f"  AFFINE_C  = 0.0  (remove rotation)")
print(f"  AFFINE_D  = {AFFINE_D:.6f}  (keep)")
print(f"  AFFINE_TX = {new_affine_tx:.2f}  (adjusted)")
print(f"  AFFINE_TY = {new_affine_ty:.2f}  (adjusted)")
print()
print("This should shift tuggers DOWN and slightly RIGHT as you described!")
