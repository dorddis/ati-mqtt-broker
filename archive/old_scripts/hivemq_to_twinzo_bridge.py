#!/usr/bin/env python3
"""
HiveMQ to Twinzo Bridge
Subscribes to HiveMQ broker and forwards AMR data to Twinzo API
"""
import paho.mqtt.client as mqtt
import requests
import json
import time
import ssl

# Load configs
with open('config/hivemq_config.json', 'r') as f:
    hivemq_config = json.load(f)

# HiveMQ connection
BROKER = hivemq_config['connection']['host']
PORT = hivemq_config['connection']['port']
USERNAME = hivemq_config['credentials']['username']
PASSWORD = hivemq_config['credentials']['password']
SUBSCRIBE_TOPIC = hivemq_config['topics']['amr_positions']

# Twinzo API
TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

# OAuth token cache (also used for position tracking)
oauth_cache = {}

# Statistics
stats = {
    "messages_received": 0,
    "messages_forwarded": 0,
    "messages_failed": 0,
    "started_at": time.time()
}

def authenticate_device(device_id):
    """Authenticate device with Twinzo OAuth"""
    if device_id in oauth_cache:
        # Check if token is still valid (assume 1 hour expiry)
        if time.time() - oauth_cache[device_id].get('auth_time', 0) < 3600:
            return oauth_cache[device_id]

    try:
        auth_payload = {
            "client": TWINZO_CLIENT,
            "login": device_id,
            "password": TWINZO_PASSWORD
        }

        response = requests.post(TWINZO_AUTH_URL, json=auth_payload, timeout=10)

        if response.status_code == 200:
            auth_data = response.json()
            oauth_cache[device_id] = {
                "token": auth_data["Token"],
                "client": auth_data["Client"],
                "branch": auth_data["Branch"],
                "expires": auth_data["Expiration"],
                "auth_time": time.time()
            }
            print(f"    Authenticated: {device_id}")
            return oauth_cache[device_id]
        else:
            print(f"    Auth failed for {device_id}: {response.status_code}")
            return None

    except Exception as e:
        print(f"    Auth error for {device_id}: {e}")
        return None

def send_to_twinzo(amr_data):
    """Forward AMR data to Twinzo API"""
    device_id = amr_data.get("device_id")
    if not device_id:
        print("    ERROR: No device_id in message")
        return False

    # Use device_id directly (already in correct format: tugger-01, tugger-02, etc.)
    tugger_id = device_id

    # Authenticate
    credentials = authenticate_device(tugger_id)
    if not credentials:
        return False

    # Get current position
    x = amr_data["position"]["x"]
    y = amr_data["position"]["y"]

    # Calculate movement based on coordinate changes (same logic as original bridge)
    device_key = f"{tugger_id}_last_pos"
    if device_key not in oauth_cache:
        # First position for this device
        oauth_cache[device_key] = {"x": x, "y": y, "time": time.time()}
        is_moving = True
    else:
        # Check movement since last update
        last_pos = oauth_cache[device_key]
        distance = ((x - last_pos["x"])**2 + (y - last_pos["y"])**2)**0.5
        time_diff = time.time() - last_pos["time"]

        # Movement threshold: 250 units (same as original working bridge)
        # Only update stored position if significant movement or 1 second passed
        if distance > 250 or time_diff > 1.0:
            is_moving = distance > 250
            oauth_cache[device_key] = {"x": x, "y": y, "time": time.time()}
        else:
            is_moving = distance > 250

    # Prepare Twinzo payload
    payload = [{
        "Timestamp": amr_data.get("timestamp", int(time.time() * 1000)),
        "SectorId": amr_data.get("sector_id", 1),
        "X": x,
        "Y": y,
        "Z": amr_data["position"].get("z", 0.0),
        "Interval": 100,  # 100ms for 10Hz smooth updates
        "Battery": amr_data.get("battery", 100),
        "IsMoving": is_moving,  # Dynamic based on actual movement
        "LocalizationAreas": [],
        "NoGoAreas": []
    }]

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials["client"],
        "Branch": credentials["branch"],
        "Token": credentials["token"],
        "Api-Key": TWINZO_API_KEY
    }

    try:
        response = requests.post(TWINZO_LOCALIZATION_URL, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            moving_status = "MOVING" if payload[0]['IsMoving'] else "static"
            print(f"    Twinzo OK: {tugger_id} at ({payload[0]['X']:.1f}, {payload[0]['Y']:.1f}) [{moving_status}]")
            return True
        else:
            print(f"    Twinzo FAIL: {tugger_id} - Status {response.status_code}")
            return False

    except Exception as e:
        print(f"    Twinzo ERROR: {tugger_id} - {e}")
        return False

def on_connect(client, userdata, flags, rc):
    """Callback when connected to HiveMQ"""
    if rc == 0:
        print("=" * 80)
        print("BRIDGE CONNECTED TO HIVEMQ")
        print("=" * 80)
        print(f"Broker: {BROKER}")
        print(f"Subscribing to: {SUBSCRIBE_TOPIC}")
        print()

        # Subscribe to all AMR position topics
        client.subscribe(SUBSCRIBE_TOPIC)
        print("Listening for AMR position data...")
        print()
    else:
        print(f"Connection failed, return code: {rc}")

def on_message(client, userdata, msg):
    """Callback when message received from HiveMQ"""
    try:
        stats["messages_received"] += 1

        # Parse message
        payload = json.loads(msg.payload.decode())

        print(f"\n[{stats['messages_received']}] Received from {msg.topic}")
        print(f"    Device: {payload.get('device_id')}")
        print(f"    Position: ({payload['position']['x']:.1f}, {payload['position']['y']:.1f})")
        print(f"    Battery: {payload.get('battery', 'N/A')}%")

        # Forward to Twinzo
        if send_to_twinzo(payload):
            stats["messages_forwarded"] += 1
        else:
            stats["messages_failed"] += 1

    except Exception as e:
        print(f"    ERROR processing message: {e}")
        stats["messages_failed"] += 1

def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscription confirmed"""
    print(f"Subscription confirmed (QoS: {granted_qos[0]})")
    print()

def print_stats():
    """Print statistics"""
    runtime = time.time() - stats['started_at']
    print()
    print("=" * 80)
    print("BRIDGE STATISTICS")
    print("=" * 80)
    print(f"Runtime: {runtime:.1f} seconds")
    print(f"Messages Received: {stats['messages_received']}")
    print(f"Messages Forwarded to Twinzo: {stats['messages_forwarded']}")
    print(f"Messages Failed: {stats['messages_failed']}")
    if stats['messages_received'] > 0:
        success_rate = (stats['messages_forwarded'] / stats['messages_received']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    print("=" * 80)

def main():
    print("=" * 80)
    print("HIVEMQ TO TWINZO BRIDGE")
    print("=" * 80)
    print()
    print("This bridge will:")
    print("  1. Subscribe to HiveMQ Cloud for AMR position data")
    print("  2. Authenticate each AMR with Twinzo OAuth")
    print("  3. Forward position updates to Twinzo API")
    print("  4. Display real-time tugger positions on Twinzo platform")
    print()

    # Create MQTT client
    client = mqtt.Client(client_id="twinzo-hivemq-bridge")
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    try:
        # Connect to HiveMQ
        print(f"Connecting to {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, keepalive=60)

        # Start loop
        client.loop_forever()

    except KeyboardInterrupt:
        print()
        print_stats()

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        client.disconnect()
        print()
        print("Bridge disconnected")

if __name__ == "__main__":
    main()
