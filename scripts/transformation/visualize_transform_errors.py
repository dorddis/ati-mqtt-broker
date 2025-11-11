"""
Visualize the transformation errors to understand the coordinate mapping.
"""
import matplotlib.pyplot as plt
import numpy as np


def parse_coordinate_string(coord_str):
    """Parse coordinate string like '110.664,62.390' into tuple."""
    parts = coord_str.replace(' ', '').split(',')
    return float(parts[0]), float(parts[1])


# Reference points from CSV
reference_data = [
    ("Origin", "0,0", "94843.64, 164031.47"),
    ("XL Engine Pickup W", "10.404, 70.727", "107666.41,94491.6"),
    ("XL Engine dropup W", "-1.329, 16.690", "94562.85,159221.02"),
    ("Battery pickupup W", "110.664,62.390", "219066.46,85115.92"),
    ("Battery Dropup W", "34.800,46.500", "125626.01,106711.93"),
]

reference_points = []
labels = []
for label, ati_str, twinzo_str in reference_data:
    x_ati, y_ati = parse_coordinate_string(ati_str)
    x_twinzo, y_twinzo = parse_coordinate_string(twinzo_str)
    reference_points.append((x_ati, y_ati, x_twinzo, y_twinzo))
    labels.append(label)

# Transformation parameters (calculated)
A = 1114.231287
B = -6.892942
C = -193.182579
D = -1021.818219
TX = 94185.26
TY = 168003.25

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Plot 1: ATI coordinates
ax1 = axes[0, 0]
ati_x = [p[0] for p in reference_points]
ati_y = [p[1] for p in reference_points]
ax1.scatter(ati_x, ati_y, c='blue', s=100, alpha=0.6)
for i, label in enumerate(labels):
    ax1.annotate(label, (ati_x[i], ati_y[i]), fontsize=8, ha='right')
ax1.set_xlabel('X (meters)')
ax1.set_ylabel('Y (meters)')
ax1.set_title('ATI Coordinate System')
ax1.grid(True, alpha=0.3)
ax1.axis('equal')

# Plot 2: Twinzo coordinates (actual)
ax2 = axes[0, 1]
twinzo_x_actual = [p[2] for p in reference_points]
twinzo_y_actual = [p[3] for p in reference_points]
ax2.scatter(twinzo_x_actual, twinzo_y_actual, c='green', s=100, alpha=0.6, label='Actual')

# Calculate transformed coordinates
twinzo_x_calc = [A * p[0] + B * p[1] + TX for p in reference_points]
twinzo_y_calc = [C * p[0] + D * p[1] + TY for p in reference_points]
ax2.scatter(twinzo_x_calc, twinzo_y_calc, c='red', s=100, alpha=0.6, marker='x', label='Calculated')

# Draw error vectors
for i in range(len(reference_points)):
    ax2.plot([twinzo_x_actual[i], twinzo_x_calc[i]],
             [twinzo_y_actual[i], twinzo_y_calc[i]],
             'k--', alpha=0.3)
    ax2.annotate(labels[i], (twinzo_x_actual[i], twinzo_y_actual[i]), fontsize=8, ha='right')

ax2.set_xlabel('X (Twinzo units)')
ax2.set_ylabel('Y (Twinzo units)')
ax2.set_title('Twinzo Coordinate System - Actual vs Calculated')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.axis('equal')

# Plot 3: Error magnitudes
ax3 = axes[1, 0]
errors_x = [abs(twinzo_x_calc[i] - twinzo_x_actual[i]) for i in range(len(reference_points))]
errors_y = [abs(twinzo_y_calc[i] - twinzo_y_actual[i]) for i in range(len(reference_points))]
errors_total = [np.sqrt(errors_x[i]**2 + errors_y[i]**2) for i in range(len(reference_points))]

x_pos = np.arange(len(labels))
ax3.bar(x_pos - 0.2, errors_x, 0.4, label='X Error', alpha=0.7)
ax3.bar(x_pos + 0.2, errors_y, 0.4, label='Y Error', alpha=0.7)
ax3.set_xticks(x_pos)
ax3.set_xticklabels(labels, rotation=45, ha='right')
ax3.set_ylabel('Error (Twinzo units)')
ax3.set_title('Transformation Errors by Point')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Summary statistics
ax4 = axes[1, 1]
ax4.axis('off')

summary_text = f"""
TRANSFORMATION PARAMETERS:
========================
X_twinzo = {A:.6f} * X_ati + {B:.6f} * Y_ati + {TX:.2f}
Y_twinzo = {C:.6f} * X_ati + {D:.6f} * Y_ati + {TY:.2f}

INTERPRETATION:
- X Scale: {A:.1f} (meters to Twinzo units)
- Y Scale: {D:.1f} (NEGATIVE = Y-axis flip)
- Rotation: {np.degrees(np.arctan2(B, A)):.2f} degrees
- Origin offset: ({TX:.0f}, {TY:.0f})

ERROR STATISTICS:
================
Max X Error: {max(errors_x):.2f} units
Max Y Error: {max(errors_y):.2f} units
Max Total Error: {max(errors_total):.2f} units

Average X Error: {np.mean(errors_x):.2f} units
Average Y Error: {np.mean(errors_y):.2f} units
Average Total Error: {np.mean(errors_total):.2f} units

COORDINATE RANGES:
==================
ATI: X=[{min(ati_x):.1f}, {max(ati_x):.1f}], Y=[{min(ati_y):.1f}, {max(ati_y):.1f}]
Twinzo: X=[{min(twinzo_x_actual):.0f}, {max(twinzo_x_actual):.0f}],
        Y=[{min(twinzo_y_actual):.0f}, {max(twinzo_y_actual):.0f}]

RECOMMENDATION:
===============
Errors are {max(errors_total)/((max(twinzo_x_actual)-min(twinzo_x_actual)))*100:.1f}% of X-range
and {max(errors_total)/((max(twinzo_y_actual)-min(twinzo_y_actual)))*100:.1f}% of Y-range.

{"ACCEPTABLE for visualization" if max(errors_total) < 10000 else "HIGH - Consider using simpler transform"}
"""

ax4.text(0.1, 0.95, summary_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()
plt.savefig('transform_analysis.png', dpi=150, bbox_inches='tight')
print("\nVisualization saved to: transform_analysis.png")
print("\nOpening visualization...")
plt.show()
