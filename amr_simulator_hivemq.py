#!/usr/bin/env python3
"""
AMR Simulator for HiveMQ Cloud
Publishes realistic AMR position data to HiveMQ broker
"""
import paho.mqtt.client as mqtt
import json
import time
import math
import ssl

# Load configs
with open('config/hivemq_config.json', 'r') as f:
    hivemq_config = json.load(f)

with open('config/factory_floor_coordinates.json', 'r') as f:
    factory_config = json.load(f)

# HiveMQ connection
BROKER = hivemq_config['connection']['host']
PORT = hivemq_config['connection']['port']
USERNAME = hivemq_config['credentials']['username']
PASSWORD = hivemq_config['credentials']['password']

# Factory bounds
X_MIN = factory_config['bounds']['x_min']
X_MAX = factory_config['bounds']['x_max']
Y_MIN = factory_config['bounds']['y_min']
Y_MAX = factory_config['bounds']['y_max']
CENTER_X = factory_config['dimensions']['center_x']
CENTER_Y = factory_config['dimensions']['center_y']

# AMR Configuration - Map directly to Twinzo tugger IDs
AMRS = [
    {"id": "tugger-01", "mac": "f4:7b:09:0e:04:1b", "battery": 85, "speed": 800, "path": "circle"},
    {"id": "tugger-02", "mac": "10:3d:1c:66:67:55", "battery": 78, "speed": 900, "path": "oval"},
    {"id": "tugger-03", "mac": "f4:4e:e3:f6:c7:91", "battery": 92, "speed": 1000, "path": "figure8"},
    {"id": "tugger-04", "mac": "ec:2e:98:4a:7c:f7", "battery": 88, "speed": 850, "path": "horizontal"},
    {"id": "dzdB2rvp3k", "mac": "04:00:00:00:00:00", "battery": 95, "speed": 950, "path": "vertical"},
    {"id": "kjuSXGs4Y9", "mac": "04:00:00:00:00:01", "battery": 82, "speed": 880, "path": "diagonal"},
]

HZ = 10.0  # Update frequency: 10 times per second for smooth animation
UPDATE_INTERVAL = 1.0 / HZ  # 0.1 seconds between updates

def calculate_position(amr_index, time_offset):
    """Calculate smooth path position for AMR based on path type"""
    amr = AMRS[amr_index]
    path_type = amr["path"]

    # Path parameters
    radius_x = (X_MAX - X_MIN) / 2.5
    radius_y = (Y_MAX - Y_MIN) / 3.0

    # Angular frequency for smooth loops (~5 seconds per full loop for fast demo)
    w = 2 * math.pi / 5.0  # Complete loop in 5 seconds instead of 60
    phase = amr_index * 0.6  # Phase offset for each AMR

    angle = w * time_offset + phase

    if path_type == "circle":
        # Simple circular path
        x = CENTER_X + radius_x * math.sin(angle)
        y = CENTER_Y + radius_y * math.cos(angle)

    elif path_type == "oval":
        # Oval path (elliptical)
        x = CENTER_X + radius_x * math.sin(angle)
        y = CENTER_Y + radius_y * math.cos(0.8 * angle)

    elif path_type == "figure8":
        # Figure-8 / lemniscate pattern
        x = CENTER_X + radius_x * math.sin(angle)
        y = CENTER_Y + radius_y * math.cos(0.8 * angle + 0.5 * phase)

    elif path_type == "horizontal":
        # Horizontal ellipse
        x = CENTER_X + radius_x * 1.2 * math.sin(angle)
        y = CENTER_Y + radius_y * 0.4 * math.cos(angle)

    elif path_type == "vertical":
        # Vertical ellipse
        x = CENTER_X + radius_x * 0.4 * math.sin(angle)
        y = CENTER_Y + radius_y * 1.2 * math.cos(angle)

    elif path_type == "diagonal":
        # Diagonal ellipse
        x = CENTER_X + radius_x * 0.9 * math.sin(angle)
        y = CENTER_Y + radius_y * 0.9 * math.cos(0.8 * angle + 0.3)

    else:
        # Default: circle
        x = CENTER_X + radius_x * math.sin(angle)
        y = CENTER_Y + radius_y * math.cos(angle)

    # Keep within bounds
    x = max(X_MIN + 1000, min(X_MAX - 1000, x))
    y = max(Y_MIN + 1000, min(Y_MAX - 1000, y))

    return x, y

def create_amr_message(amr, x, y):
    """Create AMR position message"""
    return {
        "device_id": amr["id"],
        "mac_address": amr["mac"],
        "timestamp": int(time.time() * 1000),
        "position": {
            "x": round(x, 2),
            "y": round(y, 2),
            "z": 0.0
        },
        "battery": amr["battery"],
        "status": "moving",
        "speed": round(amr["speed"] * 1000, 2),  # mm/s
        "sector_id": 1
    }

def on_connect(client, userdata, flags, rc):
    """Callback when connected"""
    if rc == 0:
        print("=" * 80)
        print("CONNECTED TO HIVEMQ CLOUD")
        print("=" * 80)
        print(f"Broker: {BROKER}")
        print()
    else:
        print(f"Connection failed, return code: {rc}")

def on_publish(client, userdata, mid):
    """Callback when message published"""
    pass  # Silent to avoid spam

def main():
    print("=" * 80)
    print("TWINZO AMR SIMULATOR - Smooth Movement (10 Hz)")
    print("=" * 80)
    print()
    print(f"Simulating {len(AMRS)} devices with FLUID movement patterns")
    print(f"Update Rate: {HZ} Hz ({UPDATE_INTERVAL*1000:.0f}ms intervals)")
    print(f"Factory Bounds: X=[{X_MIN}, {X_MAX}], Y=[{Y_MIN}, {Y_MAX}]")
    print()
    for i, amr in enumerate(AMRS):
        print(f"  {i+1}. {amr['id']:15s} - {amr['path']:12s} path (speed={amr['speed']} units/s)")
    print()

    # Create MQTT client
    client = mqtt.Client(client_id="hitech-amr-simulator")
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        # Connect
        print(f"Connecting to {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()

        # Wait for connection
        time.sleep(2)

        print("=" * 80)
        print("PUBLISHING AMR POSITION DATA (Press Ctrl+C to stop)")
        print("=" * 80)
        print()

        update_count = 0
        start_time = time.time()

        while True:
            time_offset = time.time() - start_time

            # Print status every 5 updates (every 0.5 seconds at 10Hz)
            if update_count % 5 == 0:
                print(f"\nUpdate #{update_count + 1} at {time.strftime('%H:%M:%S')}")
                print("-" * 80)

            for i, amr in enumerate(AMRS):
                # Calculate position
                x, y = calculate_position(i, time_offset)

                # Create message
                message = create_amr_message(amr, x, y)

                # Publish to HiveMQ
                topic = f"hitech/amr/{amr['id']}/position"
                result = client.publish(topic, json.dumps(message), qos=1)

                # Print only every 5 updates (0.5 seconds)
                if update_count % 5 == 0:
                    print(f"  {amr['id']}: ({x:,.1f}, {y:,.1f}) Bat={amr['battery']}% {amr['path']}")

            update_count += 1

            # Decrease battery slowly
            if update_count % 100 == 0:  # Every 10 seconds at 10Hz
                for amr in AMRS:
                    amr['battery'] = max(10, amr['battery'] - 1)

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print()
        print("=" * 80)
        print(f"STOPPED - Total updates sent: {update_count}")
        print("=" * 80)

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected from broker")

if __name__ == "__main__":
    main()
