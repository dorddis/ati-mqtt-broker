#!/usr/bin/env python3
"""
Production Bridge: ATI MQTTS Server → Twinzo Old Plant (Sector 2)

Subscribes to ATI's MQTTS broker and streams AMR data to Old Plant tuggers.
Device mapping:
  - ATI AMR data → tugger-05-old, tugger-06-old (and more as needed)
"""
import os, json, time, ssl
import requests
from paho.mqtt import client as mqtt

# ATI MQTTS Configuration (credentials to be provided)
ATI_HOST = os.getenv("ATI_MQTT_HOST", "tvs-dev.ifactory.ai")
ATI_PORT = int(os.getenv("ATI_MQTT_PORT", "8883"))
ATI_USERNAME = os.getenv("ATI_MQTT_USERNAME", "")  # Pending from ATI
ATI_PASSWORD = os.getenv("ATI_MQTT_PASSWORD", "")  # Pending from ATI
ATI_TOPIC = os.getenv("ATI_MQTT_TOPIC", "ati/amr/#")

# Twinzo Configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOC_URL = "https://api.platform.twinzo.com/v3/localization"

# Old Plant Configuration
OLD_PLANT_SECTOR = 2
OLD_PLANT_BRANCH = "40557468-2d57-4a3d-9a5e-3eede177daf5"

# Device mapping: ATI device ID → Twinzo tugger login
DEVICE_MAP = {
    "ati_amr_001": "tugger-05-old",
    "ati_amr_002": "tugger-06-old",
    # Add more mappings as ATI provides more AMRs
}

# OAuth token cache
oauth_cache = {"tokens": {}, "last_cleanup": time.time()}

# Coordinate transform (if needed for Old Plant)
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
            print(f"✓ OAuth successful for {device_login}")
            return oauth_cache["tokens"][device_login]
        else:
            print(f"✗ OAuth failed for {device_login}: {r.status_code}")
            return None
    except Exception as e:
        print(f"✗ OAuth error for {device_login}: {e}")
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
        print("✓ Connected to ATI MQTTS broker")
        print(f"  Subscribing to: {ATI_TOPIC}")
        client.subscribe(ATI_TOPIC, qos=1)
    else:
        print(f"✗ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Process ATI AMR data and forward to Old Plant"""
    global counter
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        # Extract ATI device ID (adjust based on actual ATI message format)
        ati_device_id = payload.get("device_id") or payload.get("amr_id") or payload.get("id")
        if not ati_device_id:
            return

        # Map to Twinzo tugger
        tugger_login = DEVICE_MAP.get(ati_device_id)
        if not tugger_login:
            if counter % LOG_EVERY_N == 0:
                print(f"⚠ Unknown ATI device: {ati_device_id} (add to DEVICE_MAP)")
            return

        # Get Twinzo credentials
        creds = get_device_credentials(tugger_login)
        if not creds:
            return

        # Extract position (adjust field names based on ATI format)
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

        # Post to Twinzo Old Plant
        headers = {
            "Content-Type": "application/json",
            "Client": creds["client"],
            "Branch": creds["branch"],
            "Token": creds["token"],
            "Api-Key": TWINZO_API_KEY
        }

        twinzo_payload = [{
            "Timestamp": int(time.time() * 1000),
            "SectorId": OLD_PLANT_SECTOR,
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
                print(f"✓ {tugger_login} (ATI:{ati_device_id}) → Old Plant: ({X:.0f}, {Y:.0f})")
            else:
                print(f"✗ POST failed for {tugger_login}: {r.status_code}")

        counter += 1

    except Exception as e:
        if counter % LOG_EVERY_N == 0:
            print(f"✗ Error: {e}")

def main():
    print("="*70)
    print("ATI MQTTS → Old Plant Bridge (Sector 2)")
    print("="*70)
    print(f"ATI Broker: {ATI_HOST}:{ATI_PORT}")
    print(f"Twinzo Old Plant: {OLD_PLANT_BRANCH}")
    print(f"Device Mappings: {len(DEVICE_MAP)}")
    for ati_id, tugger in DEVICE_MAP.items():
        print(f"  {ati_id} → {tugger}")
    print("="*70)

    if not ATI_USERNAME or not ATI_PASSWORD:
        print("\n⚠ WARNING: ATI credentials not configured!")
        print("Set ATI_MQTT_USERNAME and ATI_MQTT_PASSWORD environment variables")
        print("Bridge will wait for credentials...\n")

    # Create MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "ati_old_plant_bridge")
    client.username_pw_set(ATI_USERNAME, ATI_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

    client.on_connect = on_connect
    client.on_message = on_message

    print("\nConnecting to ATI broker...")
    client.connect(ATI_HOST, ATI_PORT, keepalive=60)
    print("✓ Bridge ready\n")

    client.loop_forever()

if __name__ == "__main__":
    main()
