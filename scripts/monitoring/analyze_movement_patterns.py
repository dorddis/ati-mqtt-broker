"""
Analyze and visualize AMR movement patterns

This script provides enhanced visualization of AMR movement patterns with:
- Time-based color gradients showing path progression
- Start/end markers
- Movement statistics (distance, velocity, stationary periods)
- Unique position analysis

Usage:
    python -X utf8 scripts/monitoring/analyze_movement_patterns.py [device_name] [hours]
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "logs" / "ati_data.db"


def connect_db():
    """Connect to the SQLite database"""
    if not DB_PATH.exists():
        print(f"Database not found at: {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(str(DB_PATH))


def analyze_movement(device_name, hours=24, coord_system='ati'):
    """Analyze and visualize movement patterns"""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.collections import LineCollection
        from matplotlib.colors import LinearSegmentedColormap
    except ImportError:
        print("ERROR: matplotlib required. Install with: pip install matplotlib")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, ati_x, ati_y, twinzo_x, twinzo_y
        FROM ati_messages
        WHERE device_name = ?
        AND timestamp > datetime('now', '-' || ? || ' hours')
        ORDER BY timestamp ASC
    """, (device_name, hours))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No data found for device: {device_name}")
        return

    timestamps = np.array([datetime.fromisoformat(r[0]) for r in rows])

    # Select coordinate system
    if coord_system.lower() == 'ati':
        x = np.array([r[1] for r in rows])
        y = np.array([r[2] for r in rows])
        x_label = 'X (meters)'
        y_label = 'Y (meters)'
        title_prefix = 'ATI Coordinates'
    else:
        x = np.array([r[3] for r in rows])
        y = np.array([r[4] for r in rows])
        x_label = 'X (Twinzo units)'
        y_label = 'Y (Twinzo units)'
        title_prefix = 'Twinzo Coordinates'

    # Calculate statistics
    total_points = len(x)
    unique_positions = len(set(zip(x, y)))

    # Calculate distances between consecutive points
    distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
    total_distance = np.sum(distances)

    # Calculate time differences
    time_diffs = np.diff(timestamps).astype('timedelta64[s]').astype(float)
    velocities = np.where(time_diffs > 0, distances / time_diffs, 0)

    # Identify stationary periods (velocity near zero)
    stationary_threshold = 0.01  # meters/second or units/second
    stationary_count = np.sum(velocities < stationary_threshold)
    moving_count = len(velocities) - stationary_count

    # Print statistics
    print("\n" + "="*80)
    print(f"MOVEMENT PATTERN ANALYSIS: {device_name}")
    print("="*80)
    print(f"\nData Range: {timestamps[0]} to {timestamps[-1]}")
    print(f"Duration: {(timestamps[-1] - timestamps[0]).total_seconds() / 60:.1f} minutes")
    print(f"\nPosition Statistics:")
    print(f"  Total data points: {total_points}")
    print(f"  Unique positions: {unique_positions}")
    print(f"  Position diversity: {unique_positions/total_points*100:.1f}%")
    print(f"\nMovement Statistics:")
    print(f"  Total distance: {total_distance:.2f} {x_label.split('(')[1].split(')')[0]}")
    print(f"  Moving periods: {moving_count} ({moving_count/len(velocities)*100:.1f}%)")
    print(f"  Stationary periods: {stationary_count} ({stationary_count/len(velocities)*100:.1f}%)")
    if moving_count > 0:
        moving_velocities = velocities[velocities >= stationary_threshold]
        print(f"  Average velocity (when moving): {np.mean(moving_velocities):.3f} {x_label.split('(')[1].split(')')[0]}/s")
        print(f"  Max velocity: {np.max(velocities):.3f} {x_label.split('(')[1].split(')')[0]}/s")

    # Identify distinct positions and dwell times
    position_times = {}
    for i, (px, py, ts) in enumerate(zip(x, y, timestamps)):
        pos_key = (round(px, 2), round(py, 2))
        if pos_key not in position_times:
            position_times[pos_key] = []
        position_times[pos_key].append(ts)

    # Find positions where AMR spent significant time
    print(f"\nTop 5 Positions by Dwell Time:")
    position_durations = {}
    for pos, times in position_times.items():
        if len(times) > 1:
            duration = (times[-1] - times[0]).total_seconds() / 60
            position_durations[pos] = (len(times), duration)

    sorted_positions = sorted(position_durations.items(), key=lambda x: x[1][1], reverse=True)[:5]
    for pos, (count, duration) in sorted_positions:
        print(f"  {pos}: {count} points, {duration:.1f} minutes")

    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Path with time-based color gradient
    time_colors = np.linspace(0, 1, len(x))

    # Create line segments
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create colormap from blue (start) to red (end)
    lc = LineCollection(segments, cmap='viridis', linewidth=2)
    lc.set_array(time_colors)

    ax1.add_collection(lc)

    # Mark start and end
    ax1.scatter(x[0], y[0], c='green', s=200, marker='o', edgecolors='black', linewidth=2,
                label='Start', zorder=5)
    ax1.scatter(x[-1], y[-1], c='red', s=200, marker='s', edgecolors='black', linewidth=2,
                label='End', zorder=5)

    # Mark stationary positions (where AMR stayed longest)
    if sorted_positions:
        top_pos = sorted_positions[0][0]
        ax1.scatter(top_pos[0], top_pos[1], c='yellow', s=300, marker='*',
                   edgecolors='black', linewidth=2, label='Main Station', zorder=5)

    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label)
    ax1.set_title(f'{title_prefix} - Movement Path\n{device_name}')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.axis('equal')

    # Add colorbar for time
    plt.colorbar(lc, ax=ax1, label='Time progression (blue → yellow)')

    # Plot 2: Velocity heatmap (position colored by typical velocity at that location)
    sc = ax2.scatter(x[:-1], y[:-1], c=velocities, cmap='hot_r', s=30, alpha=0.6)
    ax2.scatter(x[0], y[0], c='green', s=200, marker='o', edgecolors='black', linewidth=2,
                label='Start', zorder=5)
    ax2.scatter(x[-1], y[-1], c='red', s=200, marker='s', edgecolors='black', linewidth=2,
                label='End', zorder=5)

    ax2.set_xlabel(x_label)
    ax2.set_ylabel(y_label)
    ax2.set_title(f'{title_prefix} - Velocity Heatmap\n{device_name}')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.axis('equal')

    plt.colorbar(sc, ax=ax2, label='Velocity (units/s)')

    plt.tight_layout()

    # Save to file
    output_file = f"logs/{device_name}_pattern_{coord_system}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")

    plt.show()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable devices:")
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT device_name FROM ati_messages ORDER BY device_name")
        for row in cursor.fetchall():
            print(f"  - {row[0]}")
        conn.close()
        return

    device_name = sys.argv[1]
    hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    coord_system = sys.argv[3] if len(sys.argv) > 3 else 'ati'

    analyze_movement(device_name, hours, coord_system)


if __name__ == '__main__':
    main()
