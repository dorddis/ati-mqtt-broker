import os, json, time, math, random, threading
from paho.mqtt import client as mqtt

HOST = os.getenv("MQTT_HOST", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
USER = os.getenv("MQTT_USERNAME", "") or None
PASS = os.getenv("MQTT_PASSWORD", "") or None
TOPIC = os.getenv("MQTT_TOPIC", "ati_fm/sherpa/status")
NUM_ROBOTS = int(os.getenv("NUM_ROBOTS", "3"))
ROBOT_PREFIX = os.getenv("ROBOT_PREFIX", "tugger")
HZ = float(os.getenv("HZ", "10"))
DT = 1.0 / HZ if HZ > 0 else 1.0
PATH_SHAPE = os.getenv("PATH_SHAPE", "loop")

# Real-world coordinates for Twinzo visualization
RMINX = float(os.getenv("REGION_MIN_X", "195630.16"))  # Top left X
RMINY = float(os.getenv("REGION_MIN_Y", "188397.78"))  # Top left Y
RMAXX = float(os.getenv("REGION_MAX_X", "223641.36"))  # Bottom right X
RMAXY = float(os.getenv("REGION_MAX_Y", "213782.93"))  # Bottom right Y

INCLUDE_TRIPS = os.getenv("INCLUDE_TRIPS", "true").lower() == "true"

def yaw_from_y_clockwise(dx, dy):
    """
    theta measured from +Y axis, clockwise, in [0, 2pi).
    Using atan2(dx, dy) (note the swapped order).
    """
    theta = math.atan2(dx, dy)
    if theta < 0:
        theta += 2*math.pi
    return theta

def make_path(shape, idx):
    if shape == "line":
        y = RMINY + (RMAXY - RMINY) * (0.2 + 0.15 * (idx % 3))
        return {"type":"line", "y":y}
    elif shape == "rectangle":
        margin = 2 + 2*(idx%2)
        return {"type":"rectangle", "xmin":RMINX+margin, "xmax":RMAXX-margin, "ymin":RMINY+margin, "ymax":RMAXY-margin}
    else:
        return {"type":"loop", "phase": (idx * 0.6)}

def step_position(state):
    t = time.time()
    path = state["path"]
    speed = state["speed"]
    x, y = state["x"], state["y"]
    if path["type"] == "loop":
        w = 2*math.pi/60.0  # ~60s per loop
        ph = path["phase"]
        ax = (RMAXX - RMINX)/2.5
        ay = (RMAXY - RMINY)/3.0
        cx = (RMAXX + RMINX)/2.0
        cy = (RMAXY + RMINY)/2.0
        newx = cx + ax * math.sin(w*t + ph)
        newy = cy + ay * math.cos(0.8*w*t + 0.5*ph)
        dx = newx - x; dy = newy - y
        x, y = newx, newy
    elif path["type"] == "rectangle":
        if "target" not in state:
            state["target"] = (path["xmin"], path["ymin"])
        tx, ty = state["target"]
        dx, dy = tx - x, ty - y
        dist = math.hypot(dx, dy)
        if dist < 0.2:
            corners = [
                (path["xmin"], path["ymin"]),
                (path["xmax"], path["ymin"]),
                (path["xmax"], path["ymax"]),
                (path["xmin"], path["ymax"]),
            ]
            if "corner_idx" not in state: state["corner_idx"] = 0
            state["corner_idx"] = (state["corner_idx"] + 1) % 4
            state["target"] = corners[state["corner_idx"]]
            dx = dy = 0.0
        else:
            step = min(speed*DT, dist)
            if dist > 0:
                x += dx/dist * step
                y += dy/dist * step
    else:  # line
        if "dir" not in state:
            state["dir"] = +1
            state["x"] = RMINX + 2.0
            state["y"] = path["y"]
        x += state["dir"] * speed * DT
        if x > RMAXX - 2.0:
            x = RMAXX - 2.0; state["dir"] = -1
        if x < RMINX + 2.0:
            x = RMINX + 2.0; state["dir"] = +1
        dx = state["dir"] * speed * DT; dy = 0.0

    theta = yaw_from_y_clockwise(dx, dy)
    state["x"], state["y"], state["theta"] = x, y, theta
    return x, y, theta

def run_robot(idx, client, name):
    random.seed(idx*1337 + 42)
    state = {
        "x": random.uniform(RMINX+5, RMAXX-5),
        "y": random.uniform(RMINY+5, RMAXY-5),
        "theta": 0.0,
        "speed": 800 + 200*(idx%3),  # units/sec (faster for visible movement)
        "path": make_path(PATH_SHAPE, idx),
        "battery": [79.0, 77.0, 75.0][idx],  # Specific battery levels
        "trip_id": 1000 + idx,
        "trip_leg_id": 5000 + idx,
        "mode": "Fleet",
        "error": ""
    }
    last_pub = 0.0
    while True:
        now = time.time()
        if now - last_pub >= DT:
            last_pub = now
            x, y, theta = step_position(state)
            # Keep battery levels constant for demo
            # state["battery"] = max(0.0, state["battery"] - 0.0005)
            payload = {
                "sherpa_name": name,
                "mode": state["mode"],
                "error": state["error"],
                "disabled": False,
                "disabled_reason": "",
                "pose": [x, y, 0.0, 0.0, 0.0, theta],
                "battery_status": round(state["battery"], 2),
                "trip_id": state["trip_id"],
                "trip_leg_id": state["trip_leg_id"]
            }
            client.publish(TOPIC, json.dumps(payload), qos=1, retain=False)
        time.sleep(0.002)

def main():
    client = mqtt.Client()
    if USER:
        client.username_pw_set(USER, PASS or "")
    client.connect(HOST, PORT, keepalive=30)
    client.loop_start()

    names = [f"{ROBOT_PREFIX}-{i:02d}" for i in range(1, NUM_ROBOTS+1)]
    threads = []
    for idx, name in enumerate(names):
        th = threading.Thread(target=run_robot, args=(idx, client, name), daemon=True)
        th.start(); threads.append(th)

    print(f"Publishing {NUM_ROBOTS} robots to mqtt://{HOST}:{PORT} topic '{TOPIC}' at ~{HZ} Hz each. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()

if __name__ == "__main__":
    main()
