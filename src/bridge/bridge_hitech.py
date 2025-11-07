#!/usr/bin/env python3
"""
Production Bridge: HiveMQ Cloud → Twinzo HiTech Plant (Sector 1)

Subscribes to HiveMQ Cloud MQTT broker and streams AMR data to HiTech tuggers.
Device mapping:
  - HiveMQ AMR data → tugger-03, tugger-04 (and more as needed)
"""
import os, json, time, ssl
import requests
from paho.mqtt import client as mqtt

# HiveMQ Cloud Configuration
HIVEMQ_CONFIG_PATH = os.getenv("HIVEMQ_CONFIG", "config/hivemq_config.json")
with open(HIVEMQ_CONFIG_PATH, "r") as f:
    hivemq_config = json.load(f)

HIVEMQ_HOST = os.getenv("HIVEMQ_HOST", hivemq_config["host"])
HIVEMQ_PORT = int(os.getenv("HIVEMQ_PORT", str(hivemq_config["port"])))
HIVEMQ_USERNAME = os.getenv("HIVEMQ_USERNAME", hivemq_config["username"])
HIVEMQ_PASSWORD = os.getenv("HIVEMQ_PASSWORD", hivemq_config["password"])
HIVEMQ_TOPIC = os.getenv("HIVEMQ_TOPIC", "hitech/amr/#")

# Twinzo Configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOC_URL = "https://api.platform.twinzo.com/v3/localization"

# HiTech Plant Configuration
HITECH_PLANT_SECTOR = 1
HITECH_PLANT_BRANCH = "dcac4881-05ab-4f29-b0df-79c40df9c9c2"

# Device mapping: HiveMQ device ID → Twinzo tugger login
DEVICE_MAP = {
    "hitech_amr_001": "tugger-03",
    "hitech_amr_002": "tugger-04",
    # Add more mappings as HiTech provides more AMRs
}

# OAuth token cache
oauth_cache = {"tokens": {}, "last_cleanup": time.time()}

# Coordinate transform (if needed for HiTech Plant)
AFFINE_A = float(os.getenv("AFFINE_A", "1.0"))
AFFINE_B = float(os.getenv("AFFINE_B", "0.0"))
AFFINE_C = float(os.getenv("AFFINE_C", "0.0"))
AFFINE_D = float(os.getenv("AFFINE_D", "1.0"))
AFFINE_TX = float(os.getenv("AFFINE_TX", "0.0"))
AFFINE_TY = float(os.getenv("AFFINE_TY", "0.0"))

LOG_EVERY_N = int(os.getenv("LOG_EVERY_N", "50"))

def transform_xy(x, y):
    return AFFINE_A*x + AFFINE_B*y + AFFINE_TX, AFFINE_C*x + AFFINE_D*y + AFFINE_TY

def authenticate_device(device_login):
    """Authenticate Twinzo device"""
    try:
        r = requests.post(TWINZO_AUTH_URL, json={
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

    # Return valid cached or authenticate
    if device_login in oauth_cache["tokens"]:
        creds = oauth_cache["tokens"][device_login]
        if creds["expires"] > now * 1000:
            return creds
        del oauth_cache["tokens"][device_login]

    return authenticate_device(device_login)

counter = 0
session = requests.Session()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("OK Connected to HiveMQ Cloud")
        print(f"  Subscribing to: {HIVEMQ_TOPIC}")
        client.subscribe(HIVEMQ_TOPIC, qos=1)
    else:
        print(f"FAIL Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Process HiveMQ AMR data and forward to HiTech Plant"""
    global counter
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        # Extract HiveMQ device ID (adjust based on actual HiveMQ message format)
        hivemq_device_id = payload.get("device_id") or payload.get("amr_id") or payload.get("id")
        if not hivemq_device_id:
            return

        # Map to Twinzo tugger
        tugger_login = DEVICE_MAP.get(hivemq_device_id)
        if not tugger_login:
            if counter % LOG_EVERY_N == 0:
                print(f"WARN Unknown HiveMQ device: {hivemq_device_id} (add to DEVICE_MAP)")
            return

        # Get Twinzo credentials
        creds = get_device_credentials(tugger_login)
        if not creds:
            return

        # Extract position (adjust field names based on HiveMQ format)
        x = float(payload.get("x", 0))
        y = float(payload.get("y", 0))
        z = float(payload.get("z", 0))
        X, Y = transform_xy(x, y)

        # Extract other fields
        battery = int(payload.get("battery", 85))
        is_moving = payload.get("is_moving", True)

        # Movement detection
        device_key = f"{tugger_login}_last_pos"
        if device_key not in oauth_cache:
            oauth_cache[device_key] = {"x": X, "y": Y, "time": time.time()}
            is_moving = True
        else:
            last_pos = oauth_cache[device_key]
            distance = ((X - last_pos["x"])**2 + (Y - last_pos["y"])**2)**0.5
            is_moving = distance > 10
            if distance > 100 or time.time() - last_pos["time"] > 1.0:
                oauth_cache[device_key] = {"x": X, "y": Y, "time": time.time()}

        # Post to Twinzo HiTech Plant
        headers = {
            "Content-Type": "application/json",
            "Client": creds["client"],
            "Branch": creds["branch"],
            "Token": creds["token"],
            "Api-Key": TWINZO_API_KEY
        }

        twinzo_payload = [{
            "Timestamp": int(time.time() * 1000),
            "SectorId": HITECH_PLANT_SECTOR,
            "X": X,
            "Y": Y,
            "Z": z,
            "Interval": 100,
            "Battery": battery,
            "IsMoving": is_moving,
            "LocalizationAreas": [],
            "NoGoAreas": []
        }]

        r = session.post(TWINZO_LOC_URL, headers=headers, json=twinzo_payload, timeout=5)

        if counter % LOG_EVERY_N == 0:
            if r.status_code == 200:
                print(f"OK {tugger_login} (HiveMQ:{hivemq_device_id}) -> HiTech Plant: ({X:.0f}, {Y:.0f})")
            else:
                print(f"FAIL POST failed for {tugger_login}: {r.status_code}")

        counter += 1

    except Exception as e:
        if counter % LOG_EVERY_N == 0:
            print(f"FAIL Error: {e}")

def main():
    print("="*70)
    print("HiveMQ Cloud -> HiTech Plant Bridge (Sector 1)")
    print("="*70)
    print(f"HiveMQ Broker: {HIVEMQ_HOST}:{HIVEMQ_PORT}")
    print(f"Twinzo HiTech Plant: {HITECH_PLANT_BRANCH}")
    print(f"Device Mappings: {len(DEVICE_MAP)}")
    for hivemq_id, tugger in DEVICE_MAP.items():
        print(f"  {hivemq_id} -> {tugger}")
    print("="*70)

    # Create MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "hivemq_hitech_bridge")
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

    client.on_connect = on_connect
    client.on_message = on_message

    print("\nConnecting to HiveMQ Cloud...")
    client.connect(HIVEMQ_HOST, HIVEMQ_PORT, keepalive=60)
    print("OK Bridge ready\n")

    client.loop_forever()

if __name__ == "__main__":
    main()
