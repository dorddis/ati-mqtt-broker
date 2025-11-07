#!/usr/bin/env python3
"""
Production Bridge: ATI MQTTS Server → Twinzo Old Plant (Sector 2)

Subscribes to ATI's MQTTS broker (tvs-dev.ifactory.ai:8883) and streams AMR data
to Twinzo Old Plant tuggers.

ATI Data Format (topic: ati_fm/sherpa/status):
  - sherpa_name: Device identifier (e.g., "val-sherpa-01")
  - pose: [x, y, z, roll, pitch, yaw] array
  - battery_status: Battery percentage (0-100)
  - mode: "Fleet" (moving) or other states
  - Update frequency: 2 seconds

Device Mapping:
  - ATI sherpa names → tugger-05-old, tugger-06-old, tugger-07-old
"""
import os, json, time, ssl
import requests
from paho.mqtt import client as mqtt

# ATI MQTTS Configuration
ATI_HOST = os.getenv("ATI_MQTT_HOST", "tvs-dev.ifactory.ai")
ATI_PORT = int(os.getenv("ATI_MQTT_PORT", "8883"))
ATI_USERNAME = os.getenv("ATI_MQTT_USERNAME", "amr-001")
ATI_PASSWORD = os.getenv("ATI_MQTT_PASSWORD", "TVSamr001@2025")
ATI_TOPIC = os.getenv("ATI_MQTT_TOPIC", "ati_fm/sherpa/status")
ATI_CLIENT_ID = os.getenv("ATI_CLIENT_ID", "amr-001")

# Twinzo Configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOC_URL = "https://api.platform.twinzo.com/v3/localization"

# Old Plant Configuration
OLD_PLANT_SECTOR = 2
OLD_PLANT_BRANCH = "40557468-2d57-4a3d-9a5e-3eede177daf5"

# Device mapping: ATI sherpa_name → Twinzo tugger login
# Update these with actual sherpa names once AMRs start publishing (e.g., "val-sherpa-01")
DEVICE_MAP = {
    "val-sherpa-01": "tugger-05-old",
    "val-sherpa-02": "tugger-06-old",
    "val-sherpa-03": "tugger-07-old",
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
        print("OK Connected to ATI MQTTS broker")
        print(f"  Subscribing to: {ATI_TOPIC} with QoS 2")
        client.subscribe(ATI_TOPIC, qos=2)
    else:
        print(f"FAIL Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Process ATI AMR data and forward to Old Plant"""
    global counter
    try:
        # Log raw incoming message
        print(f"\n{'='*70}")
        print(f"RAW MESSAGE RECEIVED")
        print(f"{'='*70}")
        print(f"Topic: {msg.topic}")
        print(f"Payload (raw): {msg.payload[:500]}")
        print(f"{'='*70}\n")

        payload = json.loads(msg.payload.decode("utf-8"))

        # Log parsed JSON payload
        print(f"PARSED JSON:")
        print(json.dumps(payload, indent=2))
        print(f"{'='*70}\n")

        # Extract ATI sherpa name (device identifier)
        sherpa_name = payload.get("sherpa_name")
        if not sherpa_name:
            print(f"WARN No sherpa_name found in payload. Keys available: {list(payload.keys())}")
            return

        # Map to Twinzo tugger
        tugger_login = DEVICE_MAP.get(sherpa_name)
        if not tugger_login:
            print(f"WARN Unknown ATI sherpa: {sherpa_name} (add to DEVICE_MAP)")
            print(f"Available mappings: {DEVICE_MAP}")
            print(f"Add this line to DEVICE_MAP: \"{sherpa_name}\": \"tugger-XX-old\"")
            return

        print(f"Mapped {sherpa_name} -> {tugger_login}")

        # Get Twinzo credentials
        creds = get_device_credentials(tugger_login)
        if not creds:
            return

        # Extract position from pose array [x, y, z, roll, pitch, yaw]
        pose = payload.get("pose", [0, 0, 0, 0, 0, 0])
        if not isinstance(pose, list) or len(pose) < 3:
            print(f"WARN Invalid pose format: {pose}")
            return

        x = float(pose[0])
        y = float(pose[1])
        z = float(pose[2])
        X, Y = transform_xy(x, y)

        # Extract battery status
        battery = int(payload.get("battery_status", 85))

        # Extract mode to determine if moving
        mode = payload.get("mode", "Unknown")
        is_moving = mode == "Fleet"  # Moving when in Fleet mode

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

        print(f"Posting to Twinzo: {json.dumps(twinzo_payload[0], indent=2)}")

        r = session.post(TWINZO_LOC_URL, headers=headers, json=twinzo_payload, timeout=5)

        if r.status_code == 200:
            print(f"OK {tugger_login} (Sherpa:{sherpa_name}) -> Old Plant: ({X:.0f}, {Y:.0f}) Battery:{battery}% Moving:{is_moving}")
            print(f"Twinzo response: {r.status_code} {r.text[:200]}")
        else:
            print(f"FAIL POST failed for {tugger_login}: {r.status_code}")
            print(f"Response: {r.text}")

        counter += 1
        print(f"Messages processed: {counter}\n")

    except Exception as e:
        print(f"FAIL Error processing message: {e}")
        import traceback
        traceback.print_exc()

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

    # Create MQTT client with configured client ID
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=ATI_CLIENT_ID,
        protocol=mqtt.MQTTv5
    )
    client.username_pw_set(ATI_USERNAME, ATI_PASSWORD)
    # TLS configuration - using latest TLS version
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"\nConnecting to ATI broker with client ID: {ATI_CLIENT_ID}")
    print(f"Protocol: MQTT v5, QoS: 2")

    try:
        client.connect(ATI_HOST, ATI_PORT, keepalive=60)
        print("OK Bridge ready - waiting for AMR data\n")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nShutting down bridge...")
        client.disconnect()
        print("OK Bridge stopped")
    except Exception as e:
        print(f"FAIL Bridge error: {e}")

if __name__ == "__main__":
    main()
