"""
Calculate affine transformation from ATI coordinates to Twinzo coordinates
using reference points from the mapping table.
"""
import numpy as np
import csv


def parse_coordinate_string(coord_str):
    """Parse coordinate string like '110.664,62.390' into tuple."""
    parts = coord_str.replace(' ', '').split(',')
    return float(parts[0]), float(parts[1])


def calculate_affine_transform(reference_points):
    """
    Calculate affine transformation parameters using least squares.

    Affine transformation:
        X_twinzo = A * X_ati + B * Y_ati + TX
        Y_twinzo = C * X_ati + D * Y_ati + TY

    Args:
        reference_points: List of tuples [(x_ati, y_ati, x_twinzo, y_twinzo), ...]

    Returns:
        Dictionary with parameters {A, B, C, D, TX, TY}
    """
    n = len(reference_points)

    # Build matrices for least squares: A @ params = b
    # For X: [x_ati, y_ati, 1] @ [A, B, TX] = x_twinzo
    # For Y: [x_ati, y_ati, 1] @ [C, D, TY] = y_twinzo

    A_matrix = np.zeros((n, 3))
    b_x = np.zeros(n)
    b_y = np.zeros(n)

    for i, (x_ati, y_ati, x_twinzo, y_twinzo) in enumerate(reference_points):
        A_matrix[i] = [x_ati, y_ati, 1]
        b_x[i] = x_twinzo
        b_y[i] = y_twinzo

    # Solve least squares for X and Y transformations
    params_x, residuals_x, rank_x, s_x = np.linalg.lstsq(A_matrix, b_x, rcond=None)
    params_y, residuals_y, rank_y, s_y = np.linalg.lstsq(A_matrix, b_y, rcond=None)

    A, B, TX = params_x
    C, D, TY = params_y

    return {
        'AFFINE_A': A,
        'AFFINE_B': B,
        'AFFINE_C': C,
        'AFFINE_D': D,
        'AFFINE_TX': TX,
        'AFFINE_TY': TY,
        'residuals_x': residuals_x,
        'residuals_y': residuals_y
    }


def verify_transformation(params, reference_points):
    """Verify transformation accuracy with reference points."""
    print("\n=== TRANSFORMATION VERIFICATION ===\n")

    A = params['AFFINE_A']
    B = params['AFFINE_B']
    C = params['AFFINE_C']
    D = params['AFFINE_D']
    TX = params['AFFINE_TX']
    TY = params['AFFINE_TY']

    print(f"Transformation parameters:")
    print(f"  X_twinzo = {A:.6f} * X_ati + {B:.6f} * Y_ati + {TX:.2f}")
    print(f"  Y_twinzo = {C:.6f} * X_ati + {D:.6f} * Y_ati + {TY:.2f}")
    print()

    max_error_x = 0
    max_error_y = 0

    for x_ati, y_ati, x_twinzo_actual, y_twinzo_actual in reference_points:
        # Apply transformation
        x_twinzo_calc = A * x_ati + B * y_ati + TX
        y_twinzo_calc = C * x_ati + D * y_ati + TY

        # Calculate errors
        error_x = abs(x_twinzo_calc - x_twinzo_actual)
        error_y = abs(y_twinzo_calc - y_twinzo_actual)

        max_error_x = max(max_error_x, error_x)
        max_error_y = max(max_error_y, error_y)

        print(f"ATI ({x_ati:8.3f}, {y_ati:8.3f})")
        print(f"  Expected: ({x_twinzo_actual:10.2f}, {y_twinzo_actual:10.2f})")
        print(f"  Calculated: ({x_twinzo_calc:10.2f}, {y_twinzo_calc:10.2f})")
        print(f"  Error: ({error_x:8.2f}, {error_y:8.2f})")
        print()

    print(f"Maximum errors: X={max_error_x:.2f}, Y={max_error_y:.2f}")

    if max_error_x < 100 and max_error_y < 100:
        print("\nTransformation looks EXCELLENT (errors < 100 units)")
    elif max_error_x < 500 and max_error_y < 500:
        print("\nTransformation looks GOOD (errors < 500 units)")
    else:
        print("\nWARNING: Large errors detected - check reference points")


def main():
    csv_path = r"c:\Users\sidro\Downloads\Untitled spreadsheet - Sheet1.csv"

    print("Reading reference points from CSV...")
    reference_points = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            if len(row) >= 5:
                sl_no = row[0]
                amr_name = row[1]
                station_name = row[2]
                ati_coords = row[3]
                twinzo_coords = row[4]

                x_ati, y_ati = parse_coordinate_string(ati_coords)
                x_twinzo, y_twinzo = parse_coordinate_string(twinzo_coords)

                reference_points.append((x_ati, y_ati, x_twinzo, y_twinzo))
                print(f"  {sl_no}. {station_name}: ATI({x_ati:.3f}, {y_ati:.3f}) -> Twinzo({x_twinzo:.2f}, {y_twinzo:.2f})")

    print(f"\nTotal reference points: {len(reference_points)}")

    # Calculate transformation
    print("\nCalculating affine transformation...")
    params = calculate_affine_transform(reference_points)

    # Verify transformation
    verify_transformation(params, reference_points)

    # Print .env format
    print("\n=== COPY TO .env FILE ===\n")
    print(f"AFFINE_A={params['AFFINE_A']:.6f}")
    print(f"AFFINE_B={params['AFFINE_B']:.6f}")
    print(f"AFFINE_C={params['AFFINE_C']:.6f}")
    print(f"AFFINE_D={params['AFFINE_D']:.6f}")
    print(f"AFFINE_TX={params['AFFINE_TX']:.2f}")
    print(f"AFFINE_TY={params['AFFINE_TY']:.2f}")

    return params


if __name__ == "__main__":
    main()
