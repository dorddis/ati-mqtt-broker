"""
Parse connection_past.log and visualize tugger movement paths.
"""
import re
import matplotlib.pyplot as plt
from collections import defaultdict
import os


def parse_log_file(log_path):
    """Parse log file and extract tugger positions."""
    tugger_data = defaultdict(lambda: {'ati': [], 'twinzo': []})

    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by tugger blocks
    blocks = content.split('AMR: ')

    for block in blocks[1:]:  # Skip first empty split
        # Extract tugger name
        tugger_match = re.search(r'(tug-\d+)-tvsmotor-hosur-\d+ -> (tug-\d+-hosur-\d+)', block)
        if not tugger_match:
            tugger_match = re.search(r'(tug-\d+) -> (tug-\d+)', block)

        if not tugger_match:
            continue

        tugger_name = tugger_match.group(1)

        # Extract ATI coordinates
        ati_match = re.search(r'ATI Raw Coordinates: X=([\d.-]+)m, Y=([\d.-]+)m', block)
        if ati_match:
            x_ati = float(ati_match.group(1))
            y_ati = float(ati_match.group(2))
        else:
            continue

        # Extract Twinzo coordinates
        twinzo_match = re.search(r'Twinzo Transformed: X=([\d.-]+), Y=([\d.-]+)', block)
        if twinzo_match:
            x_twinzo = float(twinzo_match.group(1))
            y_twinzo = float(twinzo_match.group(2))
        else:
            continue

        # Store data
        tugger_data[tugger_name]['ati'].append((x_ati, y_ati))
        tugger_data[tugger_name]['twinzo'].append((x_twinzo, y_twinzo))

    return tugger_data


def plot_tugger_paths(tugger_data):
    """Plot tugger movement paths."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    colors = {
        'tug-55': 'blue',
        'tug-39': 'red',
        'tug-133': 'green'
    }

    # Plot ATI coordinates
    ax_ati = axes[0, 0]
    for tugger, data in tugger_data.items():
        if data['ati']:
            x_coords = [p[0] for p in data['ati']]
            y_coords = [p[1] for p in data['ati']]
            color = colors.get(tugger, 'gray')
            ax_ati.plot(x_coords, y_coords, 'o-', color=color,
                       label=f'{tugger} ({len(x_coords)} points)',
                       alpha=0.6, markersize=2, linewidth=1)
            ax_ati.scatter(x_coords[0], y_coords[0], color=color,
                          s=200, marker='s', edgecolors='black', linewidths=2, zorder=5)
            ax_ati.scatter(x_coords[-1], y_coords[-1], color=color,
                          s=200, marker='*', edgecolors='black', linewidths=2, zorder=5)

    ax_ati.set_xlabel('X (meters)', fontsize=12)
    ax_ati.set_ylabel('Y (meters)', fontsize=12)
    ax_ati.set_title('ATI Coordinates (Raw MQTT Data)', fontsize=14, fontweight='bold')
    ax_ati.legend()
    ax_ati.grid(True, alpha=0.3)
    ax_ati.axis('equal')

    # Plot Twinzo coordinates
    ax_twinzo = axes[0, 1]
    for tugger, data in tugger_data.items():
        if data['twinzo']:
            x_coords = [p[0] for p in data['twinzo']]
            y_coords = [p[1] for p in data['twinzo']]
            color = colors.get(tugger, 'gray')
            ax_twinzo.plot(x_coords, y_coords, 'o-', color=color,
                          label=f'{tugger} ({len(x_coords)} points)',
                          alpha=0.6, markersize=2, linewidth=1)
            ax_twinzo.scatter(x_coords[0], y_coords[0], color=color,
                             s=200, marker='s', edgecolors='black', linewidths=2, zorder=5)
            ax_twinzo.scatter(x_coords[-1], y_coords[-1], color=color,
                             s=200, marker='*', edgecolors='black', linewidths=2, zorder=5)

    ax_twinzo.set_xlabel('X (Twinzo units)', fontsize=12)
    ax_twinzo.set_ylabel('Y (Twinzo units)', fontsize=12)
    ax_twinzo.set_title('Twinzo Coordinates (After Transformation)', fontsize=14, fontweight='bold')
    ax_twinzo.legend()
    ax_twinzo.grid(True, alpha=0.3)
    ax_twinzo.axis('equal')

    # Plot X coordinates over index
    ax_x = axes[1, 0]
    for tugger, data in tugger_data.items():
        if data['twinzo']:
            x_coords = [p[0] for p in data['twinzo']]
            color = colors.get(tugger, 'gray')
            ax_x.plot(range(len(x_coords)), x_coords, 'o-', color=color,
                     label=tugger, alpha=0.6, markersize=2)

    ax_x.set_xlabel('Sample Index', fontsize=12)
    ax_x.set_ylabel('X (Twinzo units)', fontsize=12)
    ax_x.set_title('X Coordinate Over Time', fontsize=14, fontweight='bold')
    ax_x.legend()
    ax_x.grid(True, alpha=0.3)

    # Plot Y coordinates over index
    ax_y = axes[1, 1]
    for tugger, data in tugger_data.items():
        if data['twinzo']:
            y_coords = [p[1] for p in data['twinzo']]
            color = colors.get(tugger, 'gray')
            ax_y.plot(range(len(y_coords)), y_coords, 'o-', color=color,
                     label=tugger, alpha=0.6, markersize=2)

    ax_y.set_xlabel('Sample Index', fontsize=12)
    ax_y.set_ylabel('Y (Twinzo units)', fontsize=12)
    ax_y.set_title('Y Coordinate Over Time', fontsize=14, fontweight='bold')
    ax_y.legend()
    ax_y.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save plot
    output_path = 'movement_images/log_data_analysis.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {output_path}")

    plt.show()


def print_statistics(tugger_data):
    """Print statistics about the collected data."""
    print("=" * 80)
    print("LOG DATA ANALYSIS")
    print("=" * 80)
    print()

    for tugger, data in tugger_data.items():
        print(f"{tugger.upper()}:")
        print(f"  Data points: {len(data['ati'])}")

        if data['ati']:
            x_ati = [p[0] for p in data['ati']]
            y_ati = [p[1] for p in data['ati']]
            x_twinzo = [p[0] for p in data['twinzo']]
            y_twinzo = [p[1] for p in data['twinzo']]

            print(f"  ATI Range:")
            print(f"    X: {min(x_ati):.2f}m to {max(x_ati):.2f}m (span: {max(x_ati)-min(x_ati):.2f}m)")
            print(f"    Y: {min(y_ati):.2f}m to {max(y_ati):.2f}m (span: {max(y_ati)-min(y_ati):.2f}m)")
            print(f"  Twinzo Range:")
            print(f"    X: {min(x_twinzo):.0f} to {max(x_twinzo):.0f} (span: {max(x_twinzo)-min(x_twinzo):.0f})")
            print(f"    Y: {min(y_twinzo):.0f} to {max(y_twinzo):.0f} (span: {max(y_twinzo)-min(y_twinzo):.0f})")
        print()


def main():
    log_path = 'logs/connection_past.log'

    if not os.path.exists(log_path):
        print(f"ERROR: Log file not found: {log_path}")
        return

    print("Parsing log file...")
    tugger_data = parse_log_file(log_path)

    print_statistics(tugger_data)

    if not tugger_data:
        print("ERROR: No tugger data found in log file")
        return

    print("Generating plots...")
    plot_tugger_paths(tugger_data)

    print()
    print("=" * 80)
    print("ASSESSMENT")
    print("=" * 80)
    print()
    print("Compare the generated plot with your screenshots:")
    print("  - Tug-55 path should match Image #1 (horizontal with curve)")
    print("  - Tug-39 path should match Image #2 (with 2 turns)")
    print()
    print("If paths match: Transformation is CORRECT!")
    print("If paths don't match: We need to adjust transformation parameters.")


if __name__ == "__main__":
    main()
