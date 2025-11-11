"""
Recalculate affine transformation using precise coordinates from user screenshots.

This script uses:
1. Precise Twinzo coordinates from movement path screenshots
2. ATI coordinates from actual log data
3. Simplified transformation (no rotation: B=0, C=0)
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Precise coordinates from user screenshots
PRECISE_COORDS = {
    'tug-55': {
        'left': {'twinzo': (129337.98, 105944.23)},
        'right': {'twinzo': (236349.76, 105428.33)}
    }
}

# ATI coordinates from log analysis (connection_past.log)
ATI_COORDS = {
    'tug-55': {
        'x_range': (44.62, 116.97),  # Min and max X in meters
        'y_range': (60.36, 64.23),   # Min and max Y in meters
        'y_avg': 62.295              # Average Y (nearly constant)
    }
}

print("=" * 80)
print("RECALCULATING TRANSFORMATION WITH PRECISE COORDINATES")
print("=" * 80)
print()

print("Reference Data:")
print("-" * 80)
print(f"Tug-55 Left Point:")
print(f"  Twinzo: X={PRECISE_COORDS['tug-55']['left']['twinzo'][0]:.2f}, Y={PRECISE_COORDS['tug-55']['left']['twinzo'][1]:.2f}")
print(f"  ATI:    X={ATI_COORDS['tug-55']['x_range'][0]:.2f}m (min from log)")
print()

print(f"Tug-55 Right Point:")
print(f"  Twinzo: X={PRECISE_COORDS['tug-55']['right']['twinzo'][0]:.2f}, Y={PRECISE_COORDS['tug-55']['right']['twinzo'][1]:.2f}")
print(f"  ATI:    X={ATI_COORDS['tug-55']['x_range'][1]:.2f}m (max from log)")
print()

print(f"Tug-55 Movement Analysis:")
print(f"  ATI X span:    {ATI_COORDS['tug-55']['x_range'][1] - ATI_COORDS['tug-55']['x_range'][0]:.2f}m")
print(f"  ATI Y span:    {ATI_COORDS['tug-55']['y_range'][1] - ATI_COORDS['tug-55']['y_range'][0]:.2f}m (nearly constant)")
print(f"  Twinzo X span: {PRECISE_COORDS['tug-55']['right']['twinzo'][0] - PRECISE_COORDS['tug-55']['left']['twinzo'][0]:.2f}")
print(f"  Twinzo Y span: {abs(PRECISE_COORDS['tug-55']['right']['twinzo'][1] - PRECISE_COORDS['tug-55']['left']['twinzo'][1]):.2f}")
print()

print("=" * 80)
print("CALCULATING SIMPLIFIED TRANSFORMATION (NO ROTATION)")
print("=" * 80)
print()
print("Transformation equations:")
print("  X_twinzo = A * X_ati + TX")
print("  Y_twinzo = D * Y_ati + TY")
print()

# Calculate A (X scale factor)
x_ati_left = ATI_COORDS['tug-55']['x_range'][0]
x_ati_right = ATI_COORDS['tug-55']['x_range'][1]
x_twinzo_left = PRECISE_COORDS['tug-55']['left']['twinzo'][0]
x_twinzo_right = PRECISE_COORDS['tug-55']['right']['twinzo'][0]

A = (x_twinzo_right - x_twinzo_left) / (x_ati_right - x_ati_left)

print(f"Calculating A (X scale):")
print(f"  A = (X_twinzo_right - X_twinzo_left) / (X_ati_right - X_ati_left)")
print(f"  A = ({x_twinzo_right:.2f} - {x_twinzo_left:.2f}) / ({x_ati_right:.2f} - {x_ati_left:.2f})")
print(f"  A = {x_twinzo_right - x_twinzo_left:.2f} / {x_ati_right - x_ati_left:.2f}")
print(f"  A = {A:.6f}")
print()

# Calculate TX (X offset)
TX = x_twinzo_left - A * x_ati_left

print(f"Calculating TX (X offset):")
print(f"  TX = X_twinzo_left - A * X_ati_left")
print(f"  TX = {x_twinzo_left:.2f} - {A:.6f} * {x_ati_left:.2f}")
print(f"  TX = {TX:.2f}")
print()

# Calculate D (Y scale factor) and TY (Y offset)
# Use both endpoints to average
y_ati_avg = ATI_COORDS['tug-55']['y_avg']
y_twinzo_avg = (PRECISE_COORDS['tug-55']['left']['twinzo'][1] +
                PRECISE_COORDS['tug-55']['right']['twinzo'][1]) / 2

# For D, we need to check the direction
# If ATI Y increases upward and Twinzo Y increases downward, D should be negative
# Let's estimate D from the small Y variation we see

# From the log, Y_ati varied 60.36 to 64.23 (3.87m change)
# Twinzo Y varied 105428.33 to 105944.23 (515.90 change)
# But this is a small sample, so let's use a reasonable default scale

# Typically factory coordinate systems have similar scales for X and Y
# Since A ≈ 1478, let's assume D has similar magnitude but check sign

# From earlier analysis, D was negative (-1021.818219)
# Let's recalculate it properly

# We need at least one Y reference point. Let's use the average Y positions
# and assume D should be similar magnitude to A but possibly negative

# Actually, let's calculate D from the Y variance we observe
y_ati_span = ATI_COORDS['tug-55']['y_range'][1] - ATI_COORDS['tug-55']['y_range'][0]
y_twinzo_span = abs(PRECISE_COORDS['tug-55']['right']['twinzo'][1] -
                     PRECISE_COORDS['tug-55']['left']['twinzo'][1])

# This gives us a rough D estimate
D_magnitude = y_twinzo_span / y_ati_span if y_ati_span > 0 else A

print(f"Estimating D (Y scale):")
print(f"  Y_ati span:    {y_ati_span:.2f}m")
print(f"  Y_twinzo span: {y_twinzo_span:.2f}")
print(f"  D magnitude:   {D_magnitude:.2f}")
print()

# Since Y span is small, this estimate might not be accurate
# Let's use the previous D value but verify sign
# From user: "shift tuggers slightly to the bottom and very slightly to the right"
# This suggests our Y values are too high (need to go down)

# Let's use a more robust approach: assume D is similar to A
# and check the sign based on whether Y-axis is flipped

# For now, let's calculate TY assuming D ≈ -A (Y-axis likely flipped)
D = -A  # Assume Y-axis is flipped

print(f"Using D = -A (assuming Y-axis flip):")
print(f"  D = {D:.6f}")
print()

# Calculate TY
TY = y_twinzo_avg - D * y_ati_avg

print(f"Calculating TY (Y offset):")
print(f"  TY = Y_twinzo_avg - D * Y_ati_avg")
print(f"  TY = {y_twinzo_avg:.2f} - ({D:.6f}) * {y_ati_avg:.2f}")
print(f"  TY = {TY:.2f}")
print()

print("=" * 80)
print("RECOMMENDED NEW PARAMETERS")
print("=" * 80)
print()
print("Simplified transformation (no rotation):")
print(f"  AFFINE_A  = {A:.6f}")
print(f"  AFFINE_B  = 0.0")
print(f"  AFFINE_C  = 0.0")
print(f"  AFFINE_D  = {D:.6f}")
print(f"  AFFINE_TX = {TX:.2f}")
print(f"  AFFINE_TY = {TY:.2f}")
print()

# Validation: Transform the reference points back
print("=" * 80)
print("VALIDATION: Transform reference points")
print("=" * 80)
print()

def transform(x_ati, y_ati, A, B, C, D, TX, TY):
    x_twinzo = A * x_ati + B * y_ati + TX
    y_twinzo = C * x_ati + D * y_ati + TY
    return x_twinzo, y_twinzo

print("Tug-55 Left Point:")
x_t, y_t = transform(x_ati_left, y_ati_avg, A, 0, 0, D, TX, TY)
print(f"  ATI:      X={x_ati_left:.2f}m, Y={y_ati_avg:.2f}m")
print(f"  Expected: X={x_twinzo_left:.2f}, Y={PRECISE_COORDS['tug-55']['left']['twinzo'][1]:.2f}")
print(f"  Got:      X={x_t:.2f}, Y={y_t:.2f}")
print(f"  Error:    X={abs(x_t - x_twinzo_left):.2f}, Y={abs(y_t - PRECISE_COORDS['tug-55']['left']['twinzo'][1]):.2f}")
print()

print("Tug-55 Right Point:")
x_t, y_t = transform(x_ati_right, y_ati_avg, A, 0, 0, D, TX, TY)
print(f"  ATI:      X={x_ati_right:.2f}m, Y={y_ati_avg:.2f}m")
print(f"  Expected: X={x_twinzo_right:.2f}, Y={PRECISE_COORDS['tug-55']['right']['twinzo'][1]:.2f}")
print(f"  Got:      X={x_t:.2f}, Y={y_t:.2f}")
print(f"  Error:    X={abs(x_t - x_twinzo_right):.2f}, Y={abs(y_t - PRECISE_COORDS['tug-55']['right']['twinzo'][1]):.2f}")
print()

print("=" * 80)
print("UPDATE .env FILE")
print("=" * 80)
print()
print("Replace the following lines in .env:")
print()
print(f"AFFINE_A={A:.6f}")
print(f"AFFINE_B=0.0")
print(f"AFFINE_C=0.0")
print(f"AFFINE_D={D:.6f}")
print(f"AFFINE_TX={TX:.2f}")
print(f"AFFINE_TY={TY:.2f}")
print()

# Save parameters to file for easy copying
output_file = Path(__file__).parent.parent.parent / 'NEW_AFFINE_PARAMS.txt'
with open(output_file, 'w') as f:
    f.write(f"AFFINE_A={A:.6f}\n")
    f.write(f"AFFINE_B=0.0\n")
    f.write(f"AFFINE_C=0.0\n")
    f.write(f"AFFINE_D={D:.6f}\n")
    f.write(f"AFFINE_TX={TX:.2f}\n")
    f.write(f"AFFINE_TY={TY:.2f}\n")

print(f"Parameters saved to: {output_file}")
