import os, json, time, math
import requests
from paho.mqtt import client as mqtt
from datetime import datetime, timezone

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USERNAME") or None
MQTT_PASS = os.getenv("MQTT_PASSWORD") or None
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "ati_fm/sherpa/status")

# Twinzo OAuth configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

# API URLs - using working platform domain
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

# OAuth token cache
oauth_cache = {
    "tokens": {},  # device_login -> {token, client, branch, expires}
    "last_cleanup": time.time()
}

# Affine transform (sector alignment). Identity by default.
A = float(os.getenv("AFFINE_A", "1.0"))
B = float(os.getenv("AFFINE_B", "0.0"))
C = float(os.getenv("AFFINE_C", "0.0"))
D = float(os.getenv("AFFINE_D", "1.0"))
TX = float(os.getenv("AFFINE_TX", "0.0"))
TY = float(os.getenv("AFFINE_TY", "0.0"))

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
LOG_EVERY_N = int(os.getenv("LOG_EVERY_N", "50"))

def transform_xy(x, y):
    # X' = a*x + b*y + tx ;  Y' = c*x + d*y + ty
    xp = A*x + B*y + TX
    yp = C*x + D*y + TY
    return xp, yp

def extract_pose(payload):
    # Supports {"pose":[x,y,z,roll,pitch,yaw]} format
    x = y = z = theta = 0.0
    if "pose" in payload and isinstance(payload["pose"], (list, tuple)) and len(payload["pose"]) >= 6:
        x = float(payload["pose"][0])
        y = float(payload["pose"][1])
        z = float(payload["pose"][2])
        theta = float(payload["pose"][5])  # yaw/heading is the 6th element
    elif "pose" in payload and isinstance(payload["pose"], dict):
        # Legacy support for old dict format
        x = float(payload["pose"].get("x", 0))
        y = float(payload["pose"].get("y", 0))
        z = float(payload["pose"].get("z", 0))
        theta = float(payload["pose"].get("theta", 0))
    return x, y, z, theta

def authenticate_device(device_login):
    """Authenticate device using OAuth and cache the token"""
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
            # Cache the credentials
            oauth_cache["tokens"][device_login] = {
                "token": auth_data["Token"],
                "client": auth_data["Client"],
                "branch": auth_data["Branch"],
                "expires": auth_data["Expiration"]
            }
            print(f"✅ OAuth successful for {device_login}")
            return oauth_cache["tokens"][device_login]
        else:
            print(f"❌ OAuth failed for {device_login}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ OAuth error for {device_login}: {e}")
        return None

def get_device_credentials(device_login):
    """Get cached credentials or authenticate if needed"""
    now = time.time()
    
    # Clean up expired tokens every 10 minutes
    if now - oauth_cache["last_cleanup"] > 600:
        expired_devices = []
        for device, creds in oauth_cache["tokens"].items():
            if creds["expires"] < now * 1000:  # expires is in milliseconds
                expired_devices.append(device)
        
        for device in expired_devices:
            del oauth_cache["tokens"][device]
            print(f"🗑️ Cleaned up expired token for {device}")
        
        oauth_cache["last_cleanup"] = now
    
    # Check if we have valid cached credentials
    if device_login in oauth_cache["tokens"]:
        creds = oauth_cache["tokens"][device_login]
        if creds["expires"] > now * 1000:  # expires is in milliseconds
            return creds
        else:
            print(f"🔄 Token expired for {device_login}, re-authenticating...")
            del oauth_cache["tokens"][device_login]
    
    # Authenticate if no valid cached credentials
    return authenticate_device(device_login)

counter = 0
session = requests.Session()

def on_message(client, userdata, msg):
    global counter
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        device_id = payload.get("sherpa_name")
        if not device_id:
            return

        # Get OAuth credentials for this device
        credentials = get_device_credentials(device_id)
        if not credentials:
            if counter % LOG_EVERY_N == 0:
                print(f"❌ No valid credentials for {device_id}")
            return

        x, y, z, theta = extract_pose(payload)
        # Apply affine transform if configured
        X, Y = transform_xy(x, y)

        # Get device-specific battery levels
        device_batteries = {
            "tugger-01": 79,
            "tugger-02": 77, 
            "tugger-03": 75
        }
        
        # Calculate movement based on coordinate changes
        device_key = f"{device_id}_last_pos"
        if device_key not in oauth_cache:
            oauth_cache[device_key] = {"x": X, "y": Y, "time": time.time()}
            is_moving = True
        else:
            last_pos = oauth_cache[device_key]
            distance = ((X - last_pos["x"])**2 + (Y - last_pos["y"])**2)**0.5
            time_diff = time.time() - last_pos["time"]
            
            # Movement threshold: 250 units (0.25m if in mm)
            # Only update position if significant movement or 1 second passed
            if distance > 250 or time_diff > 1.0:
                is_moving = distance > 250
                oauth_cache[device_key] = {"x": X, "y": Y, "time": time.time()}
            else:
                is_moving = distance > 250

        # Create Twinzo localization payload (direct array format)
        twinzo_payload = [
            {
                "Timestamp": int(time.time() * 1000),  # Milliseconds
                "SectorId": 1,  # Integer sector ID (using 1 for now)
                "X": X,
                "Y": Y,
                "Z": z,
                "Interval": 100,  # 100ms = 10Hz
                "Battery": device_batteries.get(device_id, 85),
                "IsMoving": is_moving,
                "LocalizationAreas": [],  # Empty for now
                "NoGoAreas": []  # Empty for now
            }
        ]

        # Create headers with OAuth credentials
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Client": credentials["client"],
            "Branch": credentials["branch"],
            "Token": credentials["token"],
            "Api-Key": TWINZO_API_KEY
        }

        if DRY_RUN:
            if counter % LOG_EVERY_N == 0:
                print(f"[DRY] would POST for {device_id}:", twinzo_payload)
        else:
            r = session.post(TWINZO_LOCALIZATION_URL, headers=headers, json=twinzo_payload, timeout=5)
            if r.status_code >= 300:
                if counter % LOG_EVERY_N == 0:
                    print(f"POST failed {r.status_code} for {device_id}: {r.text}")
                    print(f"Headers sent: {headers}")
                    print(f"Payload: {twinzo_payload}")
            elif counter % LOG_EVERY_N == 0:
                print(f"POST ok {r.status_code} for {device_id} (X:{X:.1f}, Y:{Y:.1f}, Battery:{device_batteries.get(device_id, 85)}%, Moving:{is_moving}): {r.text}")

        counter += 1
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    print("🚀 Starting Twinzo OAuth Bridge...")
    print(f"Auth URL: {TWINZO_AUTH_URL}")
    print(f"Localization URL: {TWINZO_LOCALIZATION_URL}")
    print(f"Client: {TWINZO_CLIENT}")
    print(f"DRY_RUN: {DRY_RUN}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS or "")
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    client.subscribe(MQTT_TOPIC, qos=1)
    print(f"Bridge subscribed to mqtt://{MQTT_HOST}:{MQTT_PORT} topic '{MQTT_TOPIC}'")
    print("✅ Bridge ready - will authenticate devices dynamically using OAuth")
    client.loop_forever()

if __name__ == "__main__":
    main()