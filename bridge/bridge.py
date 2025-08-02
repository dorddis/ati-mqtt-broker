import os, json, time, math
import requests
from paho.mqtt import client as mqtt
from datetime import datetime, timezone

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USERNAME") or None
MQTT_PASS = os.getenv("MQTT_PASSWORD") or None
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "ati_fm/sherpa/status")

TWINZO_URL = os.getenv("TWINZO_URL")  # must be set
HEADERS_JSON = os.getenv("TWINZO_HEADERS_JSON", "{}")
HEADERS = json.loads(HEADERS_JSON)

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
    # Supports both {"pose":{x,y,z,theta}} and {"pose_array":[x,y,0,0,0,theta]}
    x = y = z = theta = 0.0
    if "pose" in payload and isinstance(payload["pose"], dict):
        x = float(payload["pose"].get("x", 0))
        y = float(payload["pose"].get("y", 0))
        z = float(payload["pose"].get("z", 0))
        theta = float(payload["pose"].get("theta", 0))
    elif "pose_array" in payload and isinstance(payload["pose_array"], (list,tuple)) and len(payload["pose_array"]) >= 6:
        x = float(payload["pose_array"][0]); y = float(payload["pose_array"][1])
        z = float(payload["pose_array"][2]); theta = float(payload["pose_array"][5])
    return x, y, z, theta

counter = 0
session = requests.Session()

def on_message(client, userdata, msg):
    global counter
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        device_id = payload.get("sherpa_name")
        if not device_id:
            return

        x, y, z, theta = extract_pose(payload)
        # apply affine if configured
        X, Y = transform_xy(x, y)

        # timestamp: prefer incoming, else now
        ts = payload.get("timestamp")
        if not ts:
            ts = datetime.now(timezone.utc).isoformat()

        twinzo_loc = {
            "deviceId": device_id,
            "timestamp": ts,
            "position": { "x": X, "y": Y, "z": z },
            "heading": theta
        }

        if DRY_RUN:
            if counter % LOG_EVERY_N == 0:
                print("[DRY] would POST:", twinzo_loc)
        else:
            r = session.post(TWINZO_URL, headers=HEADERS, json=twinzo_loc, timeout=5)
            if r.status_code >= 300:
                print("POST failed", r.status_code, r.text)
            elif counter % LOG_EVERY_N == 0:
                print("POST ok", r.status_code)

        counter += 1
    except Exception as e:
        print("bad msg:", e)

def main():
    if not TWINZO_URL:
        raise SystemExit("Set TWINZO_URL and TWINZO_HEADERS_JSON in environment variables.")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS or "")
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    client.subscribe(MQTT_TOPIC, qos=1)
    print(f"Bridge subscribed to mqtt://{MQTT_HOST}:{MQTT_PORT} topic '{MQTT_TOPIC}', forwarding to {TWINZO_URL}")
    client.loop_forever()

if __name__ == "__main__":
    main()