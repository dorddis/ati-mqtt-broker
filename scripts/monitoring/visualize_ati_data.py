"""
Visualize ATI Data from Database

This script reads the logged ATI data from the SQLite database and provides
various visualization and analysis options.

Usage:
    python -X utf8 scripts/monitoring/visualize_ati_data.py [command] [options]

Commands:
    stats              Show statistics for all devices
    recent [device]    Show recent messages (default: all devices)
    plot [device]      Plot movement path for a device
    export [device]    Export data to CSV
    cleanup [days]     Delete data older than N days (default: 30)
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "logs" / "ati_data.db"


def connect_db():
    """Connect to the SQLite database"""
    if not DB_PATH.exists():
        print(f"Database not found at: {DB_PATH}")
        print("Run the bridge first to create the database.")
        sys.exit(1)
    return sqlite3.connect(str(DB_PATH))


def show_stats(hours=24):
    """Show statistics for all devices"""
    conn = connect_db()
    cursor = conn.cursor()

    print("="*80)
    print(f"ATI DATA STATISTICS (Last {hours} hours)")
    print("="*80)

    # Overall stats
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN posted_to_api = 1 THEN 1 END) as posted,
            COUNT(CASE WHEN error IS NOT NULL THEN 1 END) as errors,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen
        FROM ati_messages
        WHERE timestamp > datetime('now', '-' || ? || ' hours')
    """, (hours,))

    row = cursor.fetchone()
    print(f"\nOverall:")
    print(f"  Total Messages: {row[0]}")
    print(f"  Posted to API:  {row[1]} ({row[1]/row[0]*100 if row[0] > 0 else 0:.1f}%)")
    print(f"  Errors:         {row[2]} ({row[2]/row[0]*100 if row[0] > 0 else 0:.1f}%)")
    print(f"  First Seen:     {row[3]}")
    print(f"  Last Seen:      {row[4]}")

    # Per-device stats
    cursor.execute("""
        SELECT
            device_name,
            COUNT(*) as message_count,
            COUNT(CASE WHEN posted_to_api = 1 THEN 1 END) as posted_count,
            COUNT(CASE WHEN error IS NOT NULL THEN 1 END) as error_count,
            AVG(battery_status) as avg_battery,
            MAX(timestamp) as last_seen
        FROM ati_messages
        WHERE timestamp > datetime('now', '-' || ? || ' hours')
        GROUP BY device_name
        ORDER BY last_seen DESC
    """, (hours,))

    print(f"\n{'Device':<40} {'Messages':<10} {'Posted':<10} {'Errors':<10} {'Battery':<10} {'Last Seen':<20}")
    print("-"*120)

    for row in cursor.fetchall():
        device, msgs, posted, errors, battery, last_seen = row
        battery_str = f"{battery:.0f}%" if battery else "N/A"
        print(f"{device:<40} {msgs:<10} {posted:<10} {errors:<10} {battery_str:<10} {last_seen:<20}")

    conn.close()


def show_recent(device_name=None, limit=20):
    """Show recent messages"""
    conn = connect_db()
    cursor = conn.cursor()

    print("="*80)
    print(f"RECENT MESSAGES (Last {limit})")
    print("="*80)

    if device_name:
        cursor.execute("""
            SELECT timestamp, device_name, ati_x, ati_y, twinzo_x, twinzo_y,
                   battery_status, posted_to_api, error
            FROM ati_messages
            WHERE device_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (device_name, limit))
    else:
        cursor.execute("""
            SELECT timestamp, device_name, ati_x, ati_y, twinzo_x, twinzo_y,
                   battery_status, posted_to_api, error
            FROM ati_messages
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

    print(f"\n{'Time':<20} {'Device':<30} {'ATI (m)':<20} {'Twinzo':<20} {'Battery':<8} {'Posted':<7} {'Error':<20}")
    print("-"*160)

    for row in cursor.fetchall():
        timestamp, device, ati_x, ati_y, twin_x, twin_y, battery, posted, error = row
        ati_pos = f"({ati_x:.2f}, {ati_y:.2f})"
        twin_pos = f"({twin_x:.0f}, {twin_y:.0f})"
        battery_str = f"{battery}%" if battery else "N/A"
        posted_str = "YES" if posted else "NO"
        error_str = error[:20] if error else ""
        print(f"{timestamp:<20} {device:<30} {ati_pos:<20} {twin_pos:<20} {battery_str:<8} {posted_str:<7} {error_str:<20}")

    conn.close()


def plot_movement(device_name, hours=24):
    """Plot movement path for a device"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("ERROR: matplotlib required for plotting. Install with: pip install matplotlib")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, ati_x, ati_y, twinzo_x, twinzo_y, battery_status
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

    timestamps = [datetime.fromisoformat(r[0]) for r in rows]
    ati_x = [r[1] for r in rows]
    ati_y = [r[2] for r in rows]
    twin_x = [r[3] for r in rows]
    twin_y = [r[4] for r in rows]
    battery = [r[5] if r[5] else 0 for r in rows]

    # Create figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    # Plot 1: ATI coordinates
    scatter1 = ax1.scatter(ati_x, ati_y, c=battery, cmap='RdYlGn', s=20, alpha=0.6)
    ax1.plot(ati_x, ati_y, 'b-', alpha=0.3, linewidth=0.5)
    ax1.set_xlabel('X (meters)')
    ax1.set_ylabel('Y (meters)')
    ax1.set_title(f'ATI Coordinates - {device_name}')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, label='Battery %')

    # Plot 2: Twinzo coordinates
    scatter2 = ax2.scatter(twin_x, twin_y, c=battery, cmap='RdYlGn', s=20, alpha=0.6)
    ax2.plot(twin_x, twin_y, 'r-', alpha=0.3, linewidth=0.5)
    ax2.set_xlabel('X (Twinzo units)')
    ax2.set_ylabel('Y (Twinzo units)')
    ax2.set_title(f'Twinzo Coordinates - {device_name}')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=ax2, label='Battery %')

    # Plot 3: Battery over time
    ax3.plot(timestamps, battery, 'g-', linewidth=2)
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Battery %')
    ax3.set_title(f'Battery Level - {device_name}')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)

    plt.tight_layout()

    # Save to file
    output_file = f"logs/{device_name}_movement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")
    print(f"Data points: {len(rows)}")
    print(f"Time range: {timestamps[0]} to {timestamps[-1]}")

    plt.show()


def export_csv(device_name=None, hours=24):
    """Export data to CSV"""
    conn = connect_db()
    cursor = conn.cursor()

    if device_name:
        output_file = f"logs/{device_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        cursor.execute("""
            SELECT * FROM ati_messages
            WHERE device_name = ?
            AND timestamp > datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp ASC
        """, (device_name, hours))
    else:
        output_file = f"logs/all_devices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        cursor.execute("""
            SELECT * FROM ati_messages
            WHERE timestamp > datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp ASC
        """, (hours,))

    rows = cursor.fetchall()

    if not rows:
        print("No data to export")
        conn.close()
        return

    # Get column names
    columns = [description[0] for description in cursor.description]

    # Write CSV
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write(','.join(columns) + '\n')

        # Data
        for row in rows:
            f.write(','.join(str(v) if v is not None else '' for v in row) + '\n')

    conn.close()
    print(f"Exported {len(rows)} records to: {output_file}")


def cleanup_old_data(days=30):
    """Delete data older than N days"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM ati_messages
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    """, (days,))

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    print(f"Deleted {deleted} records older than {days} days")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    try:
        if command == 'stats':
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            show_stats(hours)

        elif command == 'recent':
            device = sys.argv[2] if len(sys.argv) > 2 else None
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            show_recent(device, limit)

        elif command == 'plot':
            if len(sys.argv) < 3:
                print("Error: device name required for plot command")
                return
            device = sys.argv[2]
            hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
            plot_movement(device, hours)

        elif command == 'export':
            device = sys.argv[2] if len(sys.argv) > 2 else None
            hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
            export_csv(device, hours)

        elif command == 'cleanup':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            cleanup_old_data(days)

        else:
            print(f"Unknown command: {command}")
            print(__doc__)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
