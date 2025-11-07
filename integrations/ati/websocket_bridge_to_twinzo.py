#!/usr/bin/env python3
"""
WebSocket MQTT Bridge to Twinzo using existing proven code
Modified version of bridge/bridge.py for WebSocket MQTT
"""
import os, json, time, math
import requests
from paho.mqtt import client as mqtt
from datetime import datetime, timezone

# Use existing bridge configuration
MQTT_HOST = "localhost"
MQTT_PORT = 9001  # WebSocket MQTT port
MQTT_TOPIC = "ati/amr/+/status"  # ATI topic pattern

# Existing Twinzo OAuth configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

# Existing API URLs
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

# Existing OAuth token cache
oauth_cache = {
    "tokens": {},
    "last_cleanup": time.time()
}

# Existing affine transform (identity by default)
A = float(os.getenv("AFFINE_A", "1.0"))
B = float(os.getenv("AFFINE_B", "0.0"))
C = float(os.getenv("AFFINE_C", "0.0"))
D = float(os.getenv("AFFINE_D", "1.0"))
TX = float(os.getenv("AFFINE_TX", "0.0"))
TY = float(os.getenv("AFFINE_TY", "0.0"))

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
LOG_EVERY_N = int(os.getenv("LOG_EVERY_N", "1"))  # Log every message for testing

# Multi-plant support: Comma-separated list of sector IDs to stream to
# Default: "1,2" streams to both HiTech (1) and Old Plant (2)
SECTOR_IDS = [int(x.strip()) for x in os.getenv("SECTOR_IDS", "1,2").split(",")]

# Existing functions from bridge.py
def transform_xy(x, y):
    xp = A*x + B*y + TX
    yp = C*x + D*y + TY
    return xp, yp

def extract_pose(payload):
    x = y = z = theta = 0.0
    if "pose" in payload and isinstance(payload["pose"], (list, tuple)) and len(payload["pose"]) >= 6:
        x = float(payload["pose"][0])
        y = float(payload["pose"][1])
        z = float(payload["pose"][2])
        theta = float(payload["pose"][5])
    elif "pose" in payload and isinstance(payload["pose"], dict):
        x = float(payload["pose"].get("x", 0))
        y = float(payload["pose"].get("y", 0))
        z = float(payload["pose"].get("z", 0))
        theta = float(payload["pose"].get("theta", 0))
    return x, y, z, theta

def authenticate_device(device_login):
    """Existing OAuth authentication"""
    try:
        auth_payload = {
            "client": TWINZO_CLIENT,
            "login": device_login,
            "password": TWINZO_PASSWORD
        }

        auth_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(TWINZO_AUTH_URL, headers=auth_headers, json=auth_payload, timeout=10)

        if response.status_code == 200:
            auth_data = response.json()
            oauth_cache["tokens"][device_login] = {
                "token": auth_data["Token"],
                "client": auth_data["Client"],
                "branch": auth_data["Branch"],
                "expires": auth_data["Expiration"]
            }
            print(f"OAuth successful for {device_login}")
            return oauth_cache["tokens"][device_login]
        else:
            print(f"OAuth failed for {device_login}: {response.status_code}")
            return None

    except Exception as e:
        print(f"OAuth error for {device_login}: {e}")
        return None

def get_device_credentials(device_login):
    """Existing credential caching"""
    now = time.time()

    if now - oauth_cache["last_cleanup"] > 600:
        expired_devices = []
        for device, creds in oauth_cache["tokens"].items():
            if creds["expires"] < now * 1000:
                expired_devices.append(device)

        for device in expired_devices:
            del oauth_cache["tokens"][device]
            print(f"Cleaned up expired token for {device}")

        oauth_cache["last_cleanup"] = now

    if device_login in oauth_cache["tokens"]:
        creds = oauth_cache["tokens"][device_login]
        if creds["expires"] > now * 1000:
            return creds
        else:
            print(f"Token expired for {device_login}, re-authenticating...")
            del oauth_cache["tokens"][device_login]

    return authenticate_device(device_login)

counter = 0
session = requests.Session()

def on_message(client, userdata, msg):
    """Existing message processing with WebSocket MQTT"""
    global counter
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        device_id = payload.get("sherpa_name")
        if not device_id:
            return

        credentials = get_device_credentials(device_id)
        if not credentials:
            if counter % LOG_EVERY_N == 0:
                print(f"No valid credentials for {device_id}")
            return

        x, y, z, theta = extract_pose(payload)
        X, Y = transform_xy(x, y)

        # Use battery from payload
        battery = payload.get("battery_status", 85)

        # Existing movement detection
        device_key = f"{device_id}_last_pos"
        if device_key not in oauth_cache:
            oauth_cache[device_key] = {"x": X, "y": Y, "time": time.time()}
            is_moving = True
        else:
            last_pos = oauth_cache[device_key]
            distance = ((X - last_pos["x"])**2 + (Y - last_pos["y"])**2)**0.5
            time_diff = time.time() - last_pos["time"]

            if distance > 250 or time_diff > 1.0:
                is_moving = distance > 250
                oauth_cache[device_key] = {"x": X, "y": Y, "time": time.time()}
            else:
                is_moving = distance > 250

        # Create headers with OAuth credentials (used for all sectors)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Client": credentials["client"],
            "Branch": credentials["branch"],
            "Token": credentials["token"],
            "Api-Key": TWINZO_API_KEY
        }

        # Post to all configured sectors (multi-plant support)
        timestamp = int(time.time() * 1000)

        for sector_id in SECTOR_IDS:
            # Create Twinzo localization payload for this sector
            twinzo_payload = [
                {
                    "Timestamp": timestamp,
                    "SectorId": sector_id,
                    "X": X,
                    "Y": Y,
                    "Z": z,
                    "Interval": 100,
                    "Battery": int(battery),
                    "IsMoving": is_moving,
                    "LocalizationAreas": [],
                    "NoGoAreas": []
                }
            ]

            if DRY_RUN:
                if counter % LOG_EVERY_N == 0:
                    print(f"[DRY] would POST for {device_id} to Sector {sector_id}:", twinzo_payload)
            else:
                r = session.post(TWINZO_LOCALIZATION_URL, headers=headers, json=twinzo_payload, timeout=5)
                if r.status_code >= 300:
                    if counter % LOG_EVERY_N == 0:
                        print(f"POST failed {r.status_code} for {device_id} to Sector {sector_id}: {r.text}")
                elif counter % LOG_EVERY_N == 0:
                    print(f"POST ok {r.status_code} for {device_id} to Sector {sector_id} (X:{X:.1f}, Y:{Y:.1f}, Battery:{battery}%, Moving:{is_moving})")

        counter += 1
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    print("Starting WebSocket MQTT to Twinzo Multi-Plant Bridge")
    print(f"Auth URL: {TWINZO_AUTH_URL}")
    print(f"Localization URL: {TWINZO_LOCALIZATION_URL}")
    print(f"Client: {TWINZO_CLIENT}")
    print(f"DRY_RUN: {DRY_RUN}")
    print(f"Target Sectors: {SECTOR_IDS} (Sector 1=HiTech, Sector 2=Old Plant)")

    # WebSocket MQTT client
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="websocket_twinzo_bridge",
        transport="websockets"
    )

    client.on_message = on_message
    client.ws_set_options(path="/", headers=None)

    client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    client.subscribe(MQTT_TOPIC, qos=1)

    print(f"Bridge subscribed to WebSocket MQTT at {MQTT_HOST}:{MQTT_PORT} topic '{MQTT_TOPIC}'")
    print("Bridge ready - will authenticate devices dynamically using OAuth")

    client.loop_forever()

if __name__ == "__main__":
    main()