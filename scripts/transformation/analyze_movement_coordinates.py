"""
Analyze tugger movement coordinates from Twinzo map.
Extract patterns and check for rotation.
"""
import csv
import numpy as np
import matplotlib.pyplot as plt


def load_coordinates(csv_path):
    """Load coordinate reference points from CSV."""
    coordinates = {'tug-55': [], 'tug-39': []}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tugger = row['Tugger']
            x = float(row['Twinzo_X'])
            y = float(row['Twinzo_Y'])
            point_name = row['Point_Name']
            coordinates[tugger].append({
                'name': point_name,
                'x': x,
                'y': y
            })

    return coordinates


def analyze_tugger_55(points):
    """Analyze Tugger 55 movement pattern."""
    print("=" * 80)
    print("TUGGER 55 MOVEMENT ANALYSIS")
    print("=" * 80)
    print()

    left = points[0]
    right = points[1]

    # Calculate distance and direction
    dx = right['x'] - left['x']
    dy = right['y'] - left['y']
    distance = np.sqrt(dx**2 + dy**2)

    print(f"Left Point:  ({left['x']:.2f}, {left['y']:.2f})")
    print(f"Right Point: ({right['x']:.2f}, {right['y']:.2f})")
    print()
    print(f"Delta X: {dx:.2f}")
    print(f"Delta Y: {dy:.2f}")
    print(f"Distance: {distance:.2f} units")
    print()

    # Check if movement is horizontal
    y_variance = abs(dy)
    if y_variance < 1000:  # Within 1000 units
        print(f"Movement: HORIZONTAL (Y variance: {y_variance:.2f} units)")
        print("This suggests NO Y-AXIS ROTATION in the transformation")
    else:
        angle = np.degrees(np.arctan2(dy, dx))
        print(f"Movement: ANGLED at {angle:.2f} degrees from horizontal")

    return {
        'left': left,
        'right': right,
        'dx': dx,
        'dy': dy,
        'distance': distance,
        'is_horizontal': y_variance < 1000
    }


def analyze_tugger_39(points):
    """Analyze Tugger 39 movement pattern."""
    print()
    print("=" * 80)
    print("TUGGER 39 MOVEMENT ANALYSIS")
    print("=" * 80)
    print()

    # Check if Point 4 is an outlier
    y_coords = [p['y'] for p in points[:3]]  # First 3 points
    y_mean = np.mean(y_coords)
    y_std = np.std(y_coords)

    print("Points:")
    for i, p in enumerate(points, 1):
        is_outlier = ""
        if i == 4 and abs(p['y'] - y_mean) > 3 * y_std:
            is_outlier = " (OUTLIER - likely human error)"
        print(f"  Point {i}: ({p['x']:.2f}, {p['y']:.2f}){is_outlier}")

    print()

    # Analyze first 3 points only (exclude potential outlier)
    valid_points = points[:3]

    # Check if points form vertical or horizontal lines
    x_coords = [p['x'] for p in valid_points]
    y_coords = [p['y'] for p in valid_points]

    x_variance = max(x_coords) - min(x_coords)
    y_variance = max(y_coords) - min(y_coords)

    print(f"X Range (first 3 points): {min(x_coords):.2f} to {max(x_coords):.2f} (variance: {x_variance:.2f})")
    print(f"Y Range (first 3 points): {min(y_coords):.2f} to {max(y_coords):.2f} (variance: {y_variance:.2f})")
    print()

    # Check movement pattern
    if x_variance < 1000 and y_variance > 5000:
        print("Movement Pattern: Primarily VERTICAL")
    elif y_variance < 1000 and x_variance > 5000:
        print("Movement Pattern: Primarily HORIZONTAL")
    else:
        print("Movement Pattern: Mixed (both horizontal and vertical)")

    return {
        'points': valid_points,
        'x_range': x_variance,
        'y_range': y_variance,
        'has_outlier': len(points) > 3
    }


def visualize_movements(tug55_data, tug39_data):
    """Visualize tugger movement patterns."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Tugger 55
    x55 = [tug55_data['left']['x'], tug55_data['right']['x']]
    y55 = [tug55_data['left']['y'], tug55_data['right']['y']]

    ax1.plot(x55, y55, 'b-o', linewidth=2, markersize=10, label='Movement path')
    ax1.scatter(x55[0], y55[0], c='green', s=200, marker='s', label='Start', zorder=5)
    ax1.scatter(x55[1], y55[1], c='red', s=200, marker='s', label='End', zorder=5)
    ax1.set_xlabel('X (Twinzo units)')
    ax1.set_ylabel('Y (Twinzo units)')
    ax1.set_title('Tugger 55 Movement')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')

    # Tugger 39
    x39 = [p['x'] for p in tug39_data['points']]
    y39 = [p['y'] for p in tug39_data['points']]

    ax2.plot(x39, y39, 'r-o', linewidth=2, markersize=10, label='Movement path')
    ax2.scatter(x39[0], y39[0], c='green', s=200, marker='s', label='Start', zorder=5)
    for i, (x, y) in enumerate(zip(x39, y39), 1):
        ax2.annotate(f'P{i}', (x, y), xytext=(5, 5), textcoords='offset points')
    ax2.set_xlabel('X (Twinzo units)')
    ax2.set_ylabel('Y (Twinzo units)')
    ax2.set_title('Tugger 39 Movement')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')

    plt.tight_layout()
    plt.savefig('movement_images/movement_pattern_analysis.png', dpi=150, bbox_inches='tight')
    print()
    print("Visualization saved to: movement_images/movement_pattern_analysis.png")
    plt.show()


def main():
    csv_path = 'movement_images/coordinate_reference_points.csv'

    print("TUGGER MOVEMENT COORDINATE ANALYSIS")
    print("=" * 80)
    print()

    # Load coordinates
    coords = load_coordinates(csv_path)

    # Analyze Tugger 55
    tug55_analysis = analyze_tugger_55(coords['tug-55'])

    # Analyze Tugger 39
    tug39_analysis = analyze_tugger_39(coords['tug-39'])

    # Overall assessment
    print()
    print("=" * 80)
    print("TRANSFORMATION ASSESSMENT")
    print("=" * 80)
    print()

    if tug55_analysis['is_horizontal']:
        print("Tugger 55 moves horizontally on the Twinzo map.")
        print("This suggests that ATI X-axis maps to Twinzo X-axis WITHOUT rotation.")
        print()
        print("RECOMMENDATION: Remove rotation terms (AFFINE_B and AFFINE_C) from transformation.")
        print("A pure scaling + translation transform should work:")
        print("  X_twinzo = AFFINE_A * X_ati + AFFINE_TX")
        print("  Y_twinzo = AFFINE_D * Y_ati + AFFINE_TY")
        print()
        print("The small rotation (~0.35 degrees) in the current transform is likely")
        print("due to measurement error in the original reference points.")

    # Visualize
    print()
    print("Generating visualization...")
    visualize_movements(tug55_analysis, tug39_analysis)


if __name__ == "__main__":
    main()
