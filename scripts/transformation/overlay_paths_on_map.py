"""
Overlay tugger paths on actual Twinzo map to validate transformation.
"""
import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from collections import defaultdict
import numpy as np


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


def overlay_on_map(tugger_data, map_image_path):
    """Overlay tugger paths on Twinzo map."""

    # Load map image
    try:
        map_img = mpimg.imread(map_image_path)
        print(f"Loaded map image: {map_image_path}")
        print(f"Image shape: {map_img.shape}")
    except Exception as e:
        print(f"ERROR loading map: {e}")
        return

    # Create figure with map overlay
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    colors = {
        'tug-55': '#FF1493',  # Hot pink - highly visible
        'tug-39': '#00FF00',  # Bright green
        'tug-133': '#00FFFF'  # Cyan
    }

    # ============================================================================
    # TOP LEFT: Map with overlay
    # ============================================================================
    ax_map = axes[0, 0]

    # We need to figure out the coordinate system of the map
    # Based on the reference points, estimate map bounds
    # From earlier: Twinzo range roughly X=[77k, 228k], Y=[86k, 168k]

    # Display the map
    # The image coordinates need to be mapped to Twinzo coordinates
    # We'll need to set the extent parameter properly

    # For now, let's estimate based on the coordinate ranges we've seen
    map_x_min = 70000
    map_x_max = 240000
    map_y_min = 70000
    map_y_max = 200000

    ax_map.imshow(map_img, extent=[map_x_min, map_x_max, map_y_max, map_y_min],
                  aspect='auto', alpha=0.7, origin='upper')

    # Overlay tugger paths
    for tugger, data in tugger_data.items():
        if data['twinzo']:
            x_coords = [p[0] for p in data['twinzo']]
            y_coords = [p[1] for p in data['twinzo']]
            color = colors.get(tugger, 'white')

            # Plot path
            ax_map.plot(x_coords, y_coords, '-', color=color, linewidth=3,
                       label=f'{tugger} path', alpha=0.9, zorder=10)

            # Plot points
            ax_map.scatter(x_coords, y_coords, c=color, s=50,
                          edgecolors='black', linewidths=1, alpha=0.8, zorder=11)

            # Mark start and end
            ax_map.scatter(x_coords[0], y_coords[0], c=color,
                          s=400, marker='s', edgecolors='white', linewidths=3,
                          zorder=12, label=f'{tugger} start')
            ax_map.scatter(x_coords[-1], y_coords[-1], c=color,
                          s=400, marker='*', edgecolors='white', linewidths=3,
                          zorder=12, label=f'{tugger} end')

    ax_map.set_xlabel('X (Twinzo units)', fontsize=12, fontweight='bold', color='white')
    ax_map.set_ylabel('Y (Twinzo units)', fontsize=12, fontweight='bold', color='white')
    ax_map.set_title('Tugger Paths Overlaid on Twinzo Map',
                     fontsize=14, fontweight='bold', color='white',
                     bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
    ax_map.legend(loc='upper right', fontsize=10,
                  facecolor='black', edgecolor='white', framealpha=0.8)
    ax_map.tick_params(colors='white', labelsize=10)
    ax_map.set_facecolor('black')

    # Set grid with white color
    ax_map.grid(True, alpha=0.3, color='white', linestyle='--')

    # ============================================================================
    # TOP RIGHT: Paths without map (for clarity)
    # ============================================================================
    ax_paths = axes[0, 1]

    for tugger, data in tugger_data.items():
        if data['twinzo']:
            x_coords = [p[0] for p in data['twinzo']]
            y_coords = [p[1] for p in data['twinzo']]
            color = colors.get(tugger, 'gray')

            ax_paths.plot(x_coords, y_coords, 'o-', color=color,
                         label=f'{tugger} ({len(x_coords)} points)',
                         alpha=0.7, markersize=4, linewidth=2)
            ax_paths.scatter(x_coords[0], y_coords[0], color=color,
                            s=300, marker='s', edgecolors='black', linewidths=2, zorder=5)
            ax_paths.scatter(x_coords[-1], y_coords[-1], color=color,
                            s=300, marker='*', edgecolors='black', linewidths=2, zorder=5)

    ax_paths.set_xlabel('X (Twinzo units)', fontsize=12)
    ax_paths.set_ylabel('Y (Twinzo units)', fontsize=12)
    ax_paths.set_title('Tugger Paths (Transformed Coordinates)', fontsize=14, fontweight='bold')
    ax_paths.legend()
    ax_paths.grid(True, alpha=0.3)
    ax_paths.axis('equal')

    # ============================================================================
    # BOTTOM LEFT: ATI Raw Data
    # ============================================================================
    ax_ati = axes[1, 0]

    for tugger, data in tugger_data.items():
        if data['ati']:
            x_coords = [p[0] for p in data['ati']]
            y_coords = [p[1] for p in data['ati']]
            color = colors.get(tugger, 'gray')

            ax_ati.plot(x_coords, y_coords, 'o-', color=color,
                       label=f'{tugger} ({len(x_coords)} points)',
                       alpha=0.7, markersize=4, linewidth=2)
            ax_ati.scatter(x_coords[0], y_coords[0], color=color,
                          s=300, marker='s', edgecolors='black', linewidths=2, zorder=5)
            ax_ati.scatter(x_coords[-1], y_coords[-1], color=color,
                          s=300, marker='*', edgecolors='black', linewidths=2, zorder=5)

    ax_ati.set_xlabel('X (meters)', fontsize=12)
    ax_ati.set_ylabel('Y (meters)', fontsize=12)
    ax_ati.set_title('ATI Raw Coordinates (Before Transformation)', fontsize=14, fontweight='bold')
    ax_ati.legend()
    ax_ati.grid(True, alpha=0.3)
    ax_ati.axis('equal')

    # ============================================================================
    # BOTTOM RIGHT: Statistics
    # ============================================================================
    ax_stats = axes[1, 1]
    ax_stats.axis('off')

    stats_text = "TRANSFORMATION VALIDATION\n"
    stats_text += "=" * 50 + "\n\n"

    for tugger, data in tugger_data.items():
        if data['ati']:
            x_ati = [p[0] for p in data['ati']]
            y_ati = [p[1] for p in data['ati']]
            x_twinzo = [p[0] for p in data['twinzo']]
            y_twinzo = [p[1] for p in data['twinzo']]

            stats_text += f"{tugger.upper()}:\n"
            stats_text += f"  Data points: {len(data['ati'])}\n"
            stats_text += f"  ATI Range:\n"
            stats_text += f"    X: {min(x_ati):.2f}m to {max(x_ati):.2f}m\n"
            stats_text += f"    Y: {min(y_ati):.2f}m to {max(y_ati):.2f}m\n"
            stats_text += f"  Twinzo Range:\n"
            stats_text += f"    X: {min(x_twinzo):.0f} to {max(x_twinzo):.0f}\n"
            stats_text += f"    Y: {min(y_twinzo):.0f} to {max(y_twinzo):.0f}\n"
            stats_text += "\n"

    stats_text += "\nVALIDATION CHECKLIST:\n"
    stats_text += "=" * 50 + "\n"
    stats_text += "Compare TOP-LEFT plot to screenshots:\n\n"
    stats_text += "  Tug-55 (pink):\n"
    stats_text += "    Should show horizontal movement\n"
    stats_text += "    with slight curve\n\n"
    stats_text += "  Tug-39 (green):\n"
    stats_text += "    Should show movement with\n"
    stats_text += "    two turns (if data available)\n\n"
    stats_text += "If paths match factory layout:\n"
    stats_text += "  => Transformation is CORRECT!\n\n"
    stats_text += "If paths look wrong:\n"
    stats_text += "  => Need to adjust parameters\n"

    ax_stats.text(0.1, 0.95, stats_text, transform=ax_stats.transAxes,
                 fontsize=10, verticalalignment='top', family='monospace',
                 bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    plt.tight_layout()

    # Save plot
    output_path = 'movement_images/paths_on_twinzo_map.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\nOverlay plot saved to: {output_path}")

    plt.show()


def main():
    print("=" * 80)
    print("OVERLAY TUGGER PATHS ON TWINZO MAP")
    print("=" * 80)
    print()

    log_path = 'logs/connection_past.log'
    map_path = 'movement_images/twinzo-map.png'

    print("Parsing log file...")
    tugger_data = parse_log_file(log_path)

    if not tugger_data:
        print("ERROR: No tugger data found in log file")
        return

    print(f"Found data for: {', '.join(tugger_data.keys())}")
    print()

    print("Creating overlay visualization...")
    overlay_on_map(tugger_data, map_path)

    print()
    print("=" * 80)
    print("CHECK THE OVERLAY:")
    print("=" * 80)
    print()
    print("Look at the TOP-LEFT plot showing paths on the actual map.")
    print("Pink line = Tug-55, Green line = Tug-39")
    print()
    print("Do the paths match the factory layout?")
    print("  YES => Transformation is working correctly!")
    print("  NO  => We need to adjust the transformation parameters")


if __name__ == "__main__":
    main()
