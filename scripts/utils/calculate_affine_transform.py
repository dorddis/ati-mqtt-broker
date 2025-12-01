#!/usr/bin/env python3
"""
Calculate optimal affine transformation from ATI to Twinzo coordinates
using least squares regression on multiple reference points.

Calculates two transformations:
- Option A: Full affine (6 parameters: A, B, C, D, TX, TY)
- Option B: Constrained similarity with 1000:1 scale (3 parameters: theta, TX, TY)
"""

import csv
import numpy as np
from pathlib import Path
import re
from scipy.optimize import minimize


def load_coordinate_pairs(csv_path):
    """Load ATI and Twinzo coordinate pairs from CSV"""
    pairs = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header

        for row_num, row in enumerate(reader, start=2):
            if len(row) < 7:
                continue

            sl_no = row[0].strip()
            amr_name = row[1].strip()
            station_name = row[2].strip()

            # Columns: Sl.no, AMR name, Station Name, ATI_X, ATI_Y, Twinzo_X, Twinzo_Y
            try:
                ati_x = float(row[3].strip())
                ati_y = float(row[4].strip())
                twinzo_x = float(row[5].strip())
                twinzo_y = float(row[6].strip())
            except (ValueError, IndexError):
                continue

            pairs.append({
                'sl_no': sl_no,
                'amr': amr_name,
                'station': station_name,
                'ati_x': ati_x,
                'ati_y': ati_y,
                'twinzo_x': twinzo_x,
                'twinzo_y': twinzo_y
            })
            print(f"Row {row_num}: {station_name:40s} ATI({ati_x:7.2f}, {ati_y:7.2f}) → Twinzo({twinzo_x:.2f}, {twinzo_y:.2f})")

    return pairs


def remove_duplicate_ati_coords(pairs):
    """Remove duplicate ATI coordinates, keeping first occurrence"""
    seen = set()
    unique_pairs = []
    duplicates = []

    for pair in pairs:
        key = (pair['ati_x'], pair['ati_y'])
        if key not in seen:
            seen.add(key)
            unique_pairs.append(pair)
        else:
            duplicates.append(pair)

    if duplicates:
        print("\nRemoved duplicate ATI coordinates (kept first occurrence):")
        print("-" * 80)
        for dup in duplicates:
            print(f"  {dup['station']:40s} ATI({dup['ati_x']:7.2f}, {dup['ati_y']:7.2f})")
        print()

    return unique_pairs


def calculate_affine_transform(pairs):
    """
    Calculate affine transformation parameters using least squares.

    Transformation:
    X_twinzo = A * X_ati + B * Y_ati + TX
    Y_twinzo = C * X_ati + D * Y_ati + TY

    Returns: (A, B, C, D, TX, TY)
    """
    n = len(pairs)

    # Build matrices for least squares: [A @ x = b]
    # For X equation: [x_ati, y_ati, 1] @ [A, B, TX]^T = x_twinzo
    # For Y equation: [x_ati, y_ati, 1] @ [C, D, TY]^T = y_twinzo

    # Design matrix (same for both X and Y)
    A_matrix = np.zeros((n, 3))
    for i, pair in enumerate(pairs):
        A_matrix[i] = [pair['ati_x'], pair['ati_y'], 1]

    # Target vectors
    b_x = np.array([pair['twinzo_x'] for pair in pairs])
    b_y = np.array([pair['twinzo_y'] for pair in pairs])

    # Solve least squares
    # x = (A^T A)^-1 A^T b
    params_x, residuals_x, rank_x, s_x = np.linalg.lstsq(A_matrix, b_x, rcond=None)
    params_y, residuals_y, rank_y, s_y = np.linalg.lstsq(A_matrix, b_y, rcond=None)

    A, B, TX = params_x
    C, D, TY = params_y

    return A, B, C, D, TX, TY, residuals_x, residuals_y


def calculate_similarity_transform_constrained(pairs, scale=1000.0):
    """
    Calculate similarity transformation with fixed scale and Y-axis flip.

    Transformation:
    X_twinzo = scale * (cos(θ) * X_ati + sin(θ) * Y_ati) + TX
    Y_twinzo = -scale * (-sin(θ) * X_ati + cos(θ) * Y_ati) + TY

    Which gives affine parameters:
    A = scale * cos(θ)
    B = scale * sin(θ)
    C = scale * sin(θ)
    D = -scale * cos(θ)  (negative for Y-axis flip)

    Only 3 free parameters: θ, TX, TY

    Returns: (A, B, C, D, TX, TY, theta, total_error)
    """
    n = len(pairs)

    # Extract coordinates
    x_ati = np.array([p['ati_x'] for p in pairs])
    y_ati = np.array([p['ati_y'] for p in pairs])
    x_twinzo = np.array([p['twinzo_x'] for p in pairs])
    y_twinzo = np.array([p['twinzo_y'] for p in pairs])

    # Objective function: minimize total squared error
    def objective(params):
        theta, tx, ty = params

        # Apply transformation
        x_pred = scale * (np.cos(theta) * x_ati + np.sin(theta) * y_ati) + tx
        y_pred = -scale * (-np.sin(theta) * x_ati + np.cos(theta) * y_ati) + ty

        # Calculate squared error
        error = np.sum((x_pred - x_twinzo)**2 + (y_pred - y_twinzo)**2)
        return error

    # Initial guess: no rotation, rough translation from data mean
    x_offset_guess = np.mean(x_twinzo) - scale * np.mean(x_ati)
    y_offset_guess = np.mean(y_twinzo) + scale * np.mean(y_ati)  # + because of Y-flip
    initial_guess = [0.0, x_offset_guess, y_offset_guess]

    # Optimize
    result = minimize(objective, initial_guess, method='BFGS')

    theta_opt, tx_opt, ty_opt = result.x

    # Convert to affine parameters
    A = scale * np.cos(theta_opt)
    B = scale * np.sin(theta_opt)
    C = scale * np.sin(theta_opt)
    D = -scale * np.cos(theta_opt)
    TX = tx_opt
    TY = ty_opt

    return A, B, C, D, TX, TY, theta_opt, result.fun


def evaluate_transform(pairs, A, B, C, D, TX, TY):
    """Evaluate transformation accuracy on given pairs"""
    errors = []

    print("\n" + "="*120)
    print("Transformation Accuracy Evaluation")
    print("="*120)
    print(f"{'Station':<40s} {'ATI (x,y)':<20s} {'Twinzo Actual':<25s} {'Twinzo Predicted':<25s} {'Error':<15s}")
    print("-"*120)

    for pair in pairs:
        x_ati = pair['ati_x']
        y_ati = pair['ati_y']
        x_twinzo_actual = pair['twinzo_x']
        y_twinzo_actual = pair['twinzo_y']

        # Apply transformation
        x_twinzo_pred = A * x_ati + B * y_ati + TX
        y_twinzo_pred = C * x_ati + D * y_ati + TY

        # Calculate error
        error = np.sqrt((x_twinzo_pred - x_twinzo_actual)**2 + (y_twinzo_pred - y_twinzo_actual)**2)
        errors.append(error)

        print(f"{pair['station']:<40s} ({x_ati:6.2f}, {y_ati:6.2f})  "
              f"({x_twinzo_actual:9.2f}, {y_twinzo_actual:9.2f})  "
              f"({x_twinzo_pred:9.2f}, {y_twinzo_pred:9.2f})  "
              f"{error:8.2f}")

    errors = np.array(errors)
    print("-"*120)
    print(f"{'Mean Error:':<40s} {np.mean(errors):8.2f} Twinzo units")
    print(f"{'Median Error:':<40s} {np.median(errors):8.2f} Twinzo units")
    print(f"{'Max Error:':<40s} {np.max(errors):8.2f} Twinzo units")
    print(f"{'Min Error:':<40s} {np.min(errors):8.2f} Twinzo units")
    print(f"{'Std Dev:':<40s} {np.std(errors):8.2f} Twinzo units")
    print("="*120)

    return errors


def print_transform_params(A, B, C, D, TX, TY, label="Transformation"):
    """Pretty print transformation parameters"""
    print(f"\n{label} Parameters:")
    print("="*80)
    print(f"AFFINE_A  = {A:15.6f}  # X scale + contribution from X_ati")
    print(f"AFFINE_B  = {B:15.6f}  # X contribution from Y_ati (rotation)")
    print(f"AFFINE_C  = {C:15.6f}  # Y contribution from X_ati (rotation)")
    print(f"AFFINE_D  = {D:15.6f}  # Y scale (NEGATIVE = Y-axis flip)")
    print(f"AFFINE_TX = {TX:15.2f}  # X offset")
    print(f"AFFINE_TY = {TY:15.2f}  # Y offset")
    print("="*80)

    # Calculate derived metrics
    scale_x = np.sqrt(A**2 + C**2)
    scale_y = np.sqrt(B**2 + D**2)
    rotation_rad = np.arctan2(B, A)
    rotation_deg = np.degrees(rotation_rad)

    print(f"\nDerived Metrics:")
    print(f"  X Scale Factor: {scale_x:.2f}")
    print(f"  Y Scale Factor: {scale_y:.2f}")
    print(f"  Rotation: {rotation_deg:.2f}° ({rotation_rad:.4f} rad)")
    print(f"  Y-axis flipped: {'Yes' if D < 0 else 'No'}")
    print()


def filter_battery_stations(pairs):
    """Remove battery-related stations which have poor reference quality"""
    filtered_pairs = []
    excluded_pairs = []

    for pair in pairs:
        station = pair['station'].lower()
        if 'battery' in station:
            excluded_pairs.append(pair)
        else:
            filtered_pairs.append(pair)

    if excluded_pairs:
        print("\nExcluded battery-related stations (poor reference quality):")
        print("-" * 80)
        for exc in excluded_pairs:
            print(f"  {exc['station']:40s} ATI({exc['ati_x']:7.2f}, {exc['ati_y']:7.2f})")
        print()

    return filtered_pairs


def main():
    # Load coordinate pairs
    csv_path = r"c:\Users\sidro\Downloads\Untitled spreadsheet - Sheet1 (3).csv"
    print(f"Loading coordinate pairs from: {csv_path}\n")

    pairs = load_coordinate_pairs(csv_path)
    print(f"\nLoaded {len(pairs)} coordinate pairs")

    # Remove duplicates
    pairs = remove_duplicate_ati_coords(pairs)
    print(f"After removing duplicates: {len(pairs)} unique coordinate pairs")

    # Remove battery stations (poor quality references)
    pairs = filter_battery_stations(pairs)
    print(f"Using {len(pairs)} HIGH-QUALITY coordinate pairs for calculation (battery stations excluded)")

    if len(pairs) < 3:
        print("ERROR: Need at least 3 coordinate pairs for affine transformation")
        return

    # Calculate OPTION A: Full affine transformation
    print("\n" + "="*80)
    print("OPTION A: Full Affine Transformation (6 parameters)")
    print("="*80)

    A_full, B_full, C_full, D_full, TX_full, TY_full, res_x, res_y = calculate_affine_transform(pairs)
    print_transform_params(A_full, B_full, C_full, D_full, TX_full, TY_full, "OPTION A (Full Affine)")

    # Calculate OPTION B: Constrained 1000:1 similarity transform
    print("\n" + "="*80)
    print("OPTION B: Constrained Similarity Transform (1000:1 scale, 3 parameters)")
    print("="*80)

    A_sim, B_sim, C_sim, D_sim, TX_sim, TY_sim, theta_opt, opt_error = calculate_similarity_transform_constrained(pairs, scale=1000.0)
    print(f"\nOptimized rotation angle: {np.degrees(theta_opt):.4f}° ({theta_opt:.6f} rad)")
    print_transform_params(A_sim, B_sim, C_sim, D_sim, TX_sim, TY_sim, "OPTION B (1000:1 Constrained)")

    # Print current parameters for comparison
    print("\n" + "="*80)
    print("CURRENT Production Parameters (for comparison):")
    print("="*80)
    A_old = 1087.830509
    B_old = 11.901981
    C_old = -141.229457
    D_old = -1020.016242
    TX_old = 96089.92
    TY_old = 164196.05
    print_transform_params(A_old, B_old, C_old, D_old, TX_old, TY_old, "CURRENT")

    # Evaluate all three transformations
    print("\n" + "="*80)
    print("EVALUATION: OPTION A (Full Affine)")
    print("="*80)
    errors_full = evaluate_transform(pairs, A_full, B_full, C_full, D_full, TX_full, TY_full)

    print("\n" + "="*80)
    print("EVALUATION: OPTION B (1000:1 Constrained)")
    print("="*80)
    errors_sim = evaluate_transform(pairs, A_sim, B_sim, C_sim, D_sim, TX_sim, TY_sim)

    print("\n" + "="*80)
    print("EVALUATION: CURRENT Production Transform")
    print("="*80)
    errors_old = evaluate_transform(pairs, A_old, B_old, C_old, D_old, TX_old, TY_old)

    # Comparison summary
    print("\n" + "="*120)
    print("FINAL COMPARISON SUMMARY")
    print("="*120)
    print(f"{'Metric':<30s} {'Current':<20s} {'Option A (Full)':<20s} {'Option B (1000:1)':<20s}")
    print("-"*120)
    print(f"{'Reference Points:':<30s} {'3 (best only)':<20s} {f'{len(pairs)} (high-qual)':<20s} {f'{len(pairs)} (high-qual)':<20s}")
    print(f"{'Parameters:':<30s} {'6 (unconstrained)':<20s} {'6 (unconstrained)':<20s} {'3 (constrained)':<20s}")
    print(f"{'Mean Error:':<30s} {np.mean(errors_old):8.2f} units     {np.mean(errors_full):8.2f} units     {np.mean(errors_sim):8.2f} units")
    print(f"{'Median Error:':<30s} {np.median(errors_old):8.2f} units     {np.median(errors_full):8.2f} units     {np.median(errors_sim):8.2f} units")
    print(f"{'Max Error:':<30s} {np.max(errors_old):8.2f} units     {np.max(errors_full):8.2f} units     {np.max(errors_sim):8.2f} units")
    print(f"{'Std Dev:':<30s} {np.std(errors_old):8.2f} units     {np.std(errors_full):8.2f} units     {np.std(errors_sim):8.2f} units")
    print("-"*120)

    # Determine best option
    if np.mean(errors_full) < np.mean(errors_sim):
        print("RECOMMENDATION: Option A (Full Affine) - Lower error")
        best_label = "OPTION A"
        A_best, B_best, C_best, D_best, TX_best, TY_best = A_full, B_full, C_full, D_full, TX_full, TY_full
        errors_best = errors_full
    else:
        print("RECOMMENDATION: Option B (1000:1 Constrained) - Simpler model with comparable/better accuracy")
        best_label = "OPTION B"
        A_best, B_best, C_best, D_best, TX_best, TY_best = A_sim, B_sim, C_sim, D_sim, TX_sim, TY_sim
        errors_best = errors_sim

    improvement = (1 - np.mean(errors_best)/np.mean(errors_old)) * 100
    print(f"Improvement over current: {improvement:.1f}%")
    print("="*120)

    # Save results
    output_dir = Path(__file__).parent.parent.parent / "logs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "affine_transform_highquality.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("AFFINE TRANSFORMATION - HIGH-QUALITY REFERENCE POINTS ONLY\n")
        f.write("="*80 + "\n\n")
        f.write(f"Based on {len(pairs)} HIGH-QUALITY reference coordinate pairs\n")
        f.write(f"(Battery stations excluded due to poor reference quality)\n\n")

        f.write("OPTION A: Full Affine (6 parameters)\n")
        f.write("-"*80 + "\n")
        f.write(f"AFFINE_A={A_full:.6f}\n")
        f.write(f"AFFINE_B={B_full:.6f}\n")
        f.write(f"AFFINE_C={C_full:.6f}\n")
        f.write(f"AFFINE_D={D_full:.6f}\n")
        f.write(f"AFFINE_TX={TX_full:.2f}\n")
        f.write(f"AFFINE_TY={TY_full:.2f}\n")
        f.write(f"Mean Error: {np.mean(errors_full):.2f} units\n")
        f.write(f"Max Error: {np.max(errors_full):.2f} units\n\n")

        f.write("OPTION B: Constrained 1000:1 Similarity (3 parameters)\n")
        f.write("-"*80 + "\n")
        f.write(f"AFFINE_A={A_sim:.6f}\n")
        f.write(f"AFFINE_B={B_sim:.6f}\n")
        f.write(f"AFFINE_C={C_sim:.6f}\n")
        f.write(f"AFFINE_D={D_sim:.6f}\n")
        f.write(f"AFFINE_TX={TX_sim:.2f}\n")
        f.write(f"AFFINE_TY={TY_sim:.2f}\n")
        f.write(f"Rotation: {np.degrees(theta_opt):.4f} degrees\n")
        f.write(f"Mean Error: {np.mean(errors_sim):.2f} units\n")
        f.write(f"Max Error: {np.max(errors_sim):.2f} units\n\n")

        f.write(f"RECOMMENDATION: {best_label}\n")
        f.write(f"Improvement: {improvement:.1f}%\n")

    print(f"\nResults saved to: {output_file}")

    # Save coordinate pairs for reference
    pairs_file = output_dir / "coordinate_pairs_highquality.txt"
    with open(pairs_file, 'w', encoding='utf-8') as f:
        f.write("HIGH-QUALITY REFERENCE COORDINATE PAIRS\n")
        f.write("(Duplicates removed, Battery stations excluded)\n")
        f.write("="*80 + "\n\n")
        for pair in pairs:
            f.write(f"{pair['station']:<40s}\n")
            f.write(f"  ATI:    ({pair['ati_x']:7.3f}, {pair['ati_y']:7.3f})\n")
            f.write(f"  Twinzo: ({pair['twinzo_x']:9.2f}, {pair['twinzo_y']:9.2f})\n\n")

    print(f"Cleaned coordinate pairs saved to: {pairs_file}")


if __name__ == "__main__":
    main()
