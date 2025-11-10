"""
ATI Audit Feed Bridge - All Active AMRs to Twinzo Old Plant

This bridge uses the ATI audit feed credentials to monitor ALL active AMRs
and stream their positions to the appropriate Twinzo devices in Old Plant (Sector 2).

Features:
- Monitors ati_fm/sherpa/status for ALL AMRs
- Maps ATI sherpa_name to Twinzo device logins
- Streams to Old Plant (Sector 2) only
- Handles 7 active AMRs from multiple fleets

Usage:
    python -X utf8 src/bridge/bridge_audit_feed.py
"""

import os
import ssl
import time
import json
import requests
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# Load environment variables
load_dotenv()

# ATI Audit Feed Configuration
ATI_HOST = os.getenv("AUDIT_MQTT_HOST", "tvs-dev.ifactory.ai")
ATI_PORT = int(os.getenv("AUDIT_MQTT_PORT", "8883"))
ATI_USERNAME = os.getenv("AUDIT_USERNAME", "tvs-audit-user")
ATI_PASSWORD = os.getenv("AUDIT_PASSWORD", "TVSAudit@2025")
ATI_CLIENT_ID = "audit-bridge-old-plant"
ATI_TOPIC = "ati_fm/sherpa/status"

# Twinzo API Configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY")
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOC_URL = "https://api.platform.twinzo.com/v3/localization"

# Old Plant Configuration
OLD_PLANT_SECTOR = 2
OLD_PLANT_BRANCH = "40557468-2d57-4a3d-9a5e-3eede177daf5"

# Device Mapping: ATI sherpa_name -> Twinzo login
DEVICE_MAP = {
    "tug-55-tvsmotor-hosur-09": "tug-55-hosur-09",
    "tug-39-tvsmotor-hosur-07": "tug-39-hosur-07",
    "tug-133": "tug-133",
    "tug-140": "tug-140",
    "tug-78": "tug-78",
    "tug-24-tvsmotor-hosur-05": "tug-24-hosur-05",
    "tug-11": "tug-11"
}

# Coordinate transformation (if needed - adjust based on actual ATI coordinates)
AFFINE_A = float(os.getenv("AFFINE_A", "1.0"))
AFFINE_B = float(os.getenv("AFFINE_B", "0.0"))
AFFINE_C = float(os.getenv("AFFINE_C", "0.0"))
AFFINE_D = float(os.getenv("AFFINE_D", "1.0"))
AFFINE_TX = float(os.getenv("AFFINE_TX", "0.0"))
AFFINE_TY = float(os.getenv("AFFINE_TY", "0.0"))

# OAuth token cache
oauth_cache = {
    "tokens": {},
    "last_cleanup": time.time()
}

# Statistics
stats = {
    "messages_received": 0,
    "messages_sent": 0,
    "last_update": {},
    "errors": 0
}

# Requests session for connection pooling
session = requests.Session()


def transform_xy(x, y):
    """Apply affine transformation to coordinates"""
    return AFFINE_A*x + AFFINE_B*y + AFFINE_TX, AFFINE_C*x + AFFINE_D*y + AFFINE_TY


def authenticate_device(device_login):
    """Authenticate Twinzo device"""
    try:
        r = session.post(TWINZO_AUTH_URL, json={
            "client": TWINZO_CLIENT,
            "login": device_login,
            "password": TWINZO_PASSWORD
        }, timeout=10)

        if r.status_code == 200:
            d = r.json()
            oauth_cache["tokens"][device_login] = {
                "token": d["Token"],
                "client": d["Client"],
                "branch": d["Branch"],
                "expires": d["Expiration"]
            }
            print(f"OK OAuth successful for {device_login}")
            return oauth_cache["tokens"][device_login]
        else:
            print(f"FAIL OAuth failed for {device_login}: {r.status_code}")
            return None
    except Exception as e:
        print(f"FAIL OAuth error for {device_login}: {e}")
        return None


def get_device_credentials(device_login):
    """Get cached or fresh credentials"""
    now = time.time()

    # Cleanup expired tokens
    if now - oauth_cache["last_cleanup"] > 600:
        expired = [d for d, c in oauth_cache["tokens"].items() if c["expires"] < now * 1000]
        for d in expired:
            del oauth_cache["tokens"][d]
        oauth_cache["last_cleanup"] = now

    # Check if we have valid token
    if device_login in oauth_cache["tokens"]:
        creds = oauth_cache["tokens"][device_login]
        if creds["expires"] > (now + 60) * 1000:
            return creds

    # Get fresh token
    return authenticate_device(device_login)


def send_to_twinzo(device_login, x, y, heading):
    """Send position data to Twinzo"""
    try:
        creds = get_device_credentials(device_login)
        if not creds:
            return False

        # Prepare localization data
        data = {
            "SectorId": OLD_PLANT_SECTOR,
            "X": x,
            "Y": y,
            "Heading": heading
        }

        # Send to Twinzo
        headers = {
            "Authorization": f"Bearer {creds['token']}",
            "apikey": TWINZO_API_KEY
        }

        r = session.post(TWINZO_LOC_URL, json=data, headers=headers, timeout=5)

        if r.status_code in [200, 201, 204]:
            stats["messages_sent"] += 1
            return True
        else:
            print(f"FAIL Twinzo API error for {device_login}: {r.status_code}")
            stats["errors"] += 1
            return False

    except Exception as e:
        print(f"FAIL Error sending to Twinzo for {device_login}: {e}")
        stats["errors"] += 1
        return False


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback when connected to ATI broker"""
    if rc == 0:
        print("OK Connected to ATI audit feed")
        client.subscribe(ATI_TOPIC, qos=1)
        print(f"OK Subscribed to {ATI_TOPIC}")
    else:
        print(f"FAIL Connection failed with code {rc}")


def on_message(client, userdata, message):
    """Callback when MQTT message received"""
    try:
        stats["messages_received"] += 1

        # Parse the message
        payload = json.loads(message.payload.decode('utf-8'))

        sherpa_name = payload.get("sherpa_name")
        mode = payload.get("mode")
        pose = payload.get("pose")
        battery = payload.get("battery_status", 0)

        # Skip if not in our device map
        if sherpa_name not in DEVICE_MAP:
            return

        # Skip if disconnected or no position data
        if mode != "fleet" or not pose or len(pose) < 3:
            return

        # Get Twinzo device login
        device_login = DEVICE_MAP[sherpa_name]

        # Extract position
        x_raw, y_raw, heading = pose[0], pose[1], pose[2]

        # Apply coordinate transformation
        x, y = transform_xy(x_raw, y_raw)

        # Send to Twinzo
        success = send_to_twinzo(device_login, x, y, heading)

        # Update stats
        now = time.time()
        stats["last_update"][sherpa_name] = now

        # Log periodically
        if stats["messages_received"] % 50 == 0:
            active_count = len([t for t in stats["last_update"].values() if now - t < 30])
            print(f"\nStats: Received={stats['messages_received']}, "
                  f"Sent={stats['messages_sent']}, Active={active_count}, "
                  f"Errors={stats['errors']}")
            print(f"Recent updates: {list(stats['last_update'].keys())}\n")

    except json.JSONDecodeError:
        print(f"FAIL Invalid JSON in message")
        stats["errors"] += 1
    except Exception as e:
        print(f"FAIL Error processing message: {e}")
        stats["errors"] += 1


def main():
    """Main bridge function"""
    print("=" * 70)
    print("ATI Audit Feed Bridge - Old Plant (Sector 2)")
    print("=" * 70)
    print(f"ATI Broker: {ATI_HOST}:{ATI_PORT}")
    print(f"ATI Username: {ATI_USERNAME}")
    print(f"Client ID: {ATI_CLIENT_ID}")
    print(f"Topic: {ATI_TOPIC}")
    print(f"Old Plant Sector: {OLD_PLANT_SECTOR}")
    print(f"Old Plant Branch: {OLD_PLANT_BRANCH}")
    print(f"Active AMRs: {len(DEVICE_MAP)}")
    for ati_name, twinzo_login in DEVICE_MAP.items():
        print(f"  {ati_name} -> {twinzo_login}")
    print("=" * 70)

    if not ATI_USERNAME or not ATI_PASSWORD:
        print("\nFAIL ATI audit credentials not configured!")
        print("Set AUDIT_USERNAME and AUDIT_PASSWORD environment variables")
        return

    if not TWINZO_PASSWORD or not TWINZO_API_KEY:
        print("\nFAIL Twinzo credentials not configured!")
        print("Set TWINZO_PASSWORD and TWINZO_API_KEY environment variables")
        return

    # Create MQTT client
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=ATI_CLIENT_ID,
        protocol=mqtt.MQTTv5
    )
    client.username_pw_set(ATI_USERNAME, ATI_PASSWORD)

    # TLS configuration
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"\nConnecting to ATI audit feed...")
    print(f"Protocol: MQTT v5, QoS: 1")

    try:
        client.connect(ATI_HOST, ATI_PORT, keepalive=60)
        print("OK Bridge ready - streaming 7 AMRs to Old Plant\n")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nShutting down bridge...")
        print(f"Final stats: Received={stats['messages_received']}, "
              f"Sent={stats['messages_sent']}, Errors={stats['errors']}")
        client.disconnect()
        print("OK Bridge stopped")
    except Exception as e:
        print(f"FAIL Bridge error: {e}")


if __name__ == "__main__":
    main()
