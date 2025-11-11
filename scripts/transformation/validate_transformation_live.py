"""
Validate coordinate transformation by collecting live tugger data and plotting paths.
This will help verify if the transformation matches the actual Twinzo map.
"""
import os
import ssl
import json
import time
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

# ATI MQTT Configuration
MQTT_HOST = os.getenv('AUDIT_MQTT_HOST', 'tvs-dev.ifactory.ai')
MQTT_PORT = int(os.getenv('AUDIT_MQTT_PORT', '8883'))
MQTT_USERNAME = os.getenv('AUDIT_USERNAME', 'tvs-audit-user')
MQTT_PASSWORD = os.getenv('AUDIT_PASSWORD', 'TVSAudit@2025')
MQTT_TOPIC = 'ati_fm/sherpa/status'

# Transformation parameters
AFFINE_A = float(os.getenv('AFFINE_A', '1114.231287'))
AFFINE_B = float(os.getenv('AFFINE_B', '-6.892942'))
AFFINE_C = float(os.getenv('AFFINE_C', '-193.182579'))
AFFINE_D = float(os.getenv('AFFINE_D', '-1021.818219'))
AFFINE_TX = float(os.getenv('AFFINE_TX', '94185.26'))
AFFINE_TY = float(os.getenv('AFFINE_TY', '168003.25'))

# Tuggers to track
TUGGERS_TO_TRACK = {
    'tug-55-tvsmotor-hosur-09': 'tug-55',
    'tug-39-tvsmotor-hosur-07': 'tug-39'
}

# Data storage
tugger_data = defaultdict(lambda: {'ati': [], 'twinzo': [], 'timestamps': []})
message_count = 0
target_messages = 100  # Collect 100 messages (about 5-10 minutes of data)


def transform_coordinates(x_ati, y_ati):
    """Apply affine transformation to ATI coordinates."""
    x_twinzo = AFFINE_A * x_ati + AFFINE_B * y_ati + AFFINE_TX
    y_twinzo = AFFINE_C * x_ati + AFFINE_D * y_ati + AFFINE_TY
    return x_twinzo, y_twinzo


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print(f"OK Connected to ATI MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC, qos=1)
        print(f"OK Subscribed to {MQTT_TOPIC}")
        print()
        print(f"Collecting {target_messages} messages for tug-55 and tug-39...")
        print("This will take 5-10 minutes. Please wait...")
        print()
    else:
        print(f"FAIL Connection failed with code {rc}")


def on_message(client, userdata, message):
    """Callback for when a message is received."""
    global message_count

    try:
        payload = json.loads(message.payload.decode('utf-8'))
        sherpa_name = payload.get('sherpa_name', '')
        mode = payload.get('mode', '')
        pose = payload.get('pose', [])

        # Only process tracked tuggers that are moving
        if sherpa_name not in TUGGERS_TO_TRACK:
            return
        if mode != 'fleet' or not pose or len(pose) < 3:
            return

        # Extract coordinates
        x_ati, y_ati, heading = pose
        tugger_short_name = TUGGERS_TO_TRACK[sherpa_name]

        # Transform to Twinzo coordinates
        x_twinzo, y_twinzo = transform_coordinates(x_ati, y_ati)

        # Store data
        tugger_data[tugger_short_name]['ati'].append((x_ati, y_ati))
        tugger_data[tugger_short_name]['twinzo'].append((x_twinzo, y_twinzo))
        tugger_data[tugger_short_name]['timestamps'].append(time.time())

        message_count += 1

        # Print progress
        if message_count % 10 == 0:
            tug55_count = len(tugger_data['tug-55']['ati'])
            tug39_count = len(tugger_data['tug-39']['ati'])
            print(f"Progress: {message_count}/{target_messages} messages | tug-55: {tug55_count} points | tug-39: {tug39_count} points")

        # Stop after collecting enough messages
        if message_count >= target_messages:
            print()
            print(f"OK Collected {target_messages} messages!")
            print("Generating plots...")
            client.disconnect()

    except Exception as e:
        print(f"ERROR processing message: {e}")


def plot_results():
    """Plot the collected data."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    colors = {
        'tug-55': 'blue',
        'tug-39': 'red'
    }

    # Plot ATI coordinates
    ax_ati = axes[0, 0]
    for tugger, data in tugger_data.items():
        if data['ati']:
            x_coords = [p[0] for p in data['ati']]
            y_coords = [p[1] for p in data['ati']]
            ax_ati.plot(x_coords, y_coords, 'o-', color=colors[tugger],
                       label=tugger, alpha=0.6, markersize=3, linewidth=1)
            ax_ati.scatter(x_coords[0], y_coords[0], color=colors[tugger],
                          s=200, marker='s', edgecolors='black', linewidths=2, zorder=5)
            ax_ati.scatter(x_coords[-1], y_coords[-1], color=colors[tugger],
                          s=200, marker='*', edgecolors='black', linewidths=2, zorder=5)

    ax_ati.set_xlabel('X (meters)', fontsize=12)
    ax_ati.set_ylabel('Y (meters)', fontsize=12)
    ax_ati.set_title('ATI Coordinates (Raw Data from MQTT)', fontsize=14, fontweight='bold')
    ax_ati.legend()
    ax_ati.grid(True, alpha=0.3)
    ax_ati.axis('equal')

    # Plot Twinzo coordinates (main plot)
    ax_twinzo = axes[0, 1]
    for tugger, data in tugger_data.items():
        if data['twinzo']:
            x_coords = [p[0] for p in data['twinzo']]
            y_coords = [p[1] for p in data['twinzo']]
            ax_twinzo.plot(x_coords, y_coords, 'o-', color=colors[tugger],
                          label=tugger, alpha=0.6, markersize=3, linewidth=1)
            ax_twinzo.scatter(x_coords[0], y_coords[0], color=colors[tugger],
                             s=200, marker='s', edgecolors='black', linewidths=2, zorder=5, label=f'{tugger} start')
            ax_twinzo.scatter(x_coords[-1], y_coords[-1], color=colors[tugger],
                             s=200, marker='*', edgecolors='black', linewidths=2, zorder=5, label=f'{tugger} end')

    ax_twinzo.set_xlabel('X (Twinzo units)', fontsize=12)
    ax_twinzo.set_ylabel('Y (Twinzo units)', fontsize=12)
    ax_twinzo.set_title('Twinzo Coordinates (After Transformation)', fontsize=14, fontweight='bold')
    ax_twinzo.legend()
    ax_twinzo.grid(True, alpha=0.3)
    ax_twinzo.axis('equal')

    # Plot X over time
    ax_x_time = axes[1, 0]
    for tugger, data in tugger_data.items():
        if data['twinzo'] and data['timestamps']:
            times = [(t - data['timestamps'][0]) / 60 for t in data['timestamps']]  # Minutes
            x_coords = [p[0] for p in data['twinzo']]
            ax_x_time.plot(times, x_coords, 'o-', color=colors[tugger],
                          label=tugger, alpha=0.6, markersize=3)

    ax_x_time.set_xlabel('Time (minutes)', fontsize=12)
    ax_x_time.set_ylabel('X (Twinzo units)', fontsize=12)
    ax_x_time.set_title('X Coordinate Over Time', fontsize=14, fontweight='bold')
    ax_x_time.legend()
    ax_x_time.grid(True, alpha=0.3)

    # Plot Y over time
    ax_y_time = axes[1, 1]
    for tugger, data in tugger_data.items():
        if data['twinzo'] and data['timestamps']:
            times = [(t - data['timestamps'][0]) / 60 for t in data['timestamps']]  # Minutes
            y_coords = [p[1] for p in data['twinzo']]
            ax_y_time.plot(times, y_coords, 'o-', color=colors[tugger],
                          label=tugger, alpha=0.6, markersize=3)

    ax_y_time.set_xlabel('Time (minutes)', fontsize=12)
    ax_y_time.set_ylabel('Y (Twinzo units)', fontsize=12)
    ax_y_time.set_title('Y Coordinate Over Time', fontsize=14, fontweight='bold')
    ax_y_time.legend()
    ax_y_time.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'movement_images/live_validation_{timestamp}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Plot saved to: {filename}")

    # Print statistics
    print()
    print("=" * 80)
    print("DATA COLLECTION SUMMARY")
    print("=" * 80)
    for tugger, data in tugger_data.items():
        print(f"\n{tugger.upper()}:")
        print(f"  Points collected: {len(data['ati'])}")
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

    plt.show()


def main():
    print("=" * 80)
    print("LIVE TRANSFORMATION VALIDATION")
    print("=" * 80)
    print()
    print("Transformation Parameters:")
    print(f"  X_twinzo = {AFFINE_A:.6f} * X_ati + {AFFINE_B:.6f} * Y_ati + {AFFINE_TX:.2f}")
    print(f"  Y_twinzo = {AFFINE_C:.6f} * X_ati + {AFFINE_D:.6f} * Y_ati + {AFFINE_TY:.2f}")
    print()

    # Create MQTT client
    client = mqtt.Client(client_id=MQTT_USERNAME, protocol=mqtt.MQTTv5)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Set up TLS
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Connect and start loop
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        client.disconnect()
        if message_count > 10:
            print("Generating plots with collected data...")
            plot_results()

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        if message_count >= target_messages:
            plot_results()


if __name__ == "__main__":
    main()
