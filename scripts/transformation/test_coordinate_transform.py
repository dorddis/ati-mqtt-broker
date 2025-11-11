"""
Test the coordinate transformation with real ATI data examples.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get transformation parameters
AFFINE_A = float(os.getenv('AFFINE_A', '1000.0'))
AFFINE_B = float(os.getenv('AFFINE_B', '0.0'))
AFFINE_C = float(os.getenv('AFFINE_C', '0.0'))
AFFINE_D = float(os.getenv('AFFINE_D', '1000.0'))
AFFINE_TX = float(os.getenv('AFFINE_TX', '100000.0'))
AFFINE_TY = float(os.getenv('AFFINE_TY', '100000.0'))


def transform_xy(x, y):
    """Transform ATI coordinates to Twinzo coordinates."""
    x_twinzo = AFFINE_A * x + AFFINE_B * y + AFFINE_TX
    y_twinzo = AFFINE_C * x + AFFINE_D * y + AFFINE_TY
    return x_twinzo, y_twinzo


# Test with reference points
test_points = [
    ("Origin", 0.0, 0.0, 94843.64, 164031.47),
    ("XL Engine Pickup W", 10.404, 70.727, 107666.41, 94491.60),
    ("XL Engine dropup W", -1.329, 16.690, 94562.85, 159221.02),
    ("Battery pickupup W", 110.664, 62.390, 219066.46, 85115.92),
    ("Battery Dropup W", 34.800, 46.500, 125626.01, 106711.93),
]

# Real ATI data examples (from logs)
real_data_points = [
    ("Tug 55 (recent)", 110.943, 62.396),
    ("Tug 39 (recent)", -11.387, 40.950),
    ("Tug 133 (recent)", 10.404, 70.727),
]

print("=" * 80)
print("COORDINATE TRANSFORMATION TEST")
print("=" * 80)
print()
print("Transformation Parameters:")
print(f"  X_twinzo = {AFFINE_A:.6f} * X_ati + {AFFINE_B:.6f} * Y_ati + {AFFINE_TX:.2f}")
print(f"  Y_twinzo = {AFFINE_C:.6f} * X_ati + {AFFINE_D:.6f} * Y_ati + {AFFINE_TY:.2f}")
print()
print("=" * 80)
print("REFERENCE POINTS VERIFICATION")
print("=" * 80)
print()

for name, x_ati, y_ati, x_expected, y_expected in test_points:
    x_calc, y_calc = transform_xy(x_ati, y_ati)
    error_x = abs(x_calc - x_expected)
    error_y = abs(y_calc - y_expected)

    print(f"{name}:")
    print(f"  ATI:       ({x_ati:10.3f}, {y_ati:10.3f})")
    print(f"  Expected:  ({x_expected:10.2f}, {y_expected:10.2f})")
    print(f"  Calculated:({x_calc:10.2f}, {y_calc:10.2f})")
    print(f"  Error:     ({error_x:10.2f}, {error_y:10.2f})")
    print()

print("=" * 80)
print("REAL ATI DATA TRANSFORMATION")
print("=" * 80)
print()

for name, x_ati, y_ati in real_data_points:
    x_twinzo, y_twinzo = transform_xy(x_ati, y_ati)

    print(f"{name}:")
    print(f"  ATI coordinates:    ({x_ati:10.3f}, {y_ati:10.3f}) meters")
    print(f"  Twinzo coordinates: ({x_twinzo:10.2f}, {y_twinzo:10.2f})")
    print()

print("=" * 80)
print("COORDINATE RANGE ANALYSIS")
print("=" * 80)
print()

# Test coordinate range
ati_coords = [
    (-15, 0),   # Min observed
    (0, 0),     # Origin
    (120, 0),   # Max observed X
    (0, 80),    # Max observed Y
]

print("ATI Range Test:")
for x_ati, y_ati in ati_coords:
    x_twinzo, y_twinzo = transform_xy(x_ati, y_ati)
    print(f"  ATI ({x_ati:6.1f}, {y_ati:6.1f}) -> Twinzo ({x_twinzo:10.2f}, {y_twinzo:10.2f})")

print()
print("SUMMARY:")
print(f"  ATI range: X=[-15, 120], Y=[0, 80] meters")
print(f"  Twinzo range (approx): X=[{transform_xy(-15, 0)[0]:.0f}, {transform_xy(120, 0)[0]:.0f}],")
print(f"                         Y=[{transform_xy(0, 80)[1]:.0f}, {transform_xy(0, 0)[1]:.0f}]")
print()
print("=" * 80)
