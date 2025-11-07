#!/usr/bin/env python3
"""
Find Left Edge of Factory Floor
Place all tuggers at different X coordinates to find left boundary
"""
import requests
import json
import time

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

# All available tuggers
ROBOTS = [
    {"device_id": "tugger-01", "oauth_login": "tugger-01", "battery": 79},
    {"device_id": "tugger-02", "oauth_login": "tugger-02", "battery": 77},
    {"device_id": "tugger-03", "oauth_login": "tugger-03", "battery": 75},
]

# Testing LEFT edge - spread X values from 50k to 100k
# Keep Y constant at 150k (known to be in middle of factory)
LEFT_EDGE_TESTS = [
    {"robot_idx": 0, "x": 50000, "y": 150000, "label": "X=50k"},
    {"robot_idx": 1, "x": 75000, "y": 150000, "label": "X=75k"},
    {"robot_idx": 2, "x": 100000, "y": 150000, "label": "X=100k"},
]

oauth_cache = {}

def authenticate_device(device_login):
    auth_payload = {
        "client": TWINZO_CLIENT,
        "login": device_login,
        "password": TWINZO_PASSWORD
    }
    try:
        response = requests.post(TWINZO_AUTH_URL, json=auth_payload, timeout=15)
        if response.status_code == 200:
            auth_data = response.json()
            oauth_cache[device_login] = {
                "token": auth_data["Token"],
                "client": auth_data["Client"],
                "branch": auth_data["Branch"],
                "expires": auth_data["Expiration"]
            }
            return True
    except Exception as e:
        print(f"  Auth error for {device_login}: {e}")
    return False

def send_position(robot, x, y, label):
    credentials = oauth_cache.get(robot["oauth_login"])
    if not credentials:
        print(f"  SKIP {robot['device_id']}: No credentials")
        return False

    payload = [{
        "Timestamp": int(time.time() * 1000),
        "SectorId": 1,
        "X": x,
        "Y": y,
        "Z": 0.0,
        "Interval": 1000,
        "Battery": robot["battery"],
        "IsMoving": False,
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
        response = requests.post(TWINZO_LOCALIZATION_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            print(f"  OK {robot['device_id']}: {label} at ({x}, {y})")
            return True
        else:
            print(f"  FAIL {robot['device_id']}: {label} - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ERROR {robot['device_id']}: {label} - {e}")
        return False

def main():
    print("=" * 80)
    print("FIND LEFT EDGE - Factory Floor Boundary Test")
    print("=" * 80)
    print()
    print("Placing all tuggers at different X coordinates to find LEFT edge")
    print("Y is constant at 150k (middle of factory)")
    print()

    # Authenticate all robots
    print("Authenticating tuggers...")
    for robot in ROBOTS:
        if authenticate_device(robot["oauth_login"]):
            print(f"  {robot['device_id']}: OK")
        else:
            print(f"  {robot['device_id']}: FAILED")

    print()
    print("=" * 80)
    print("PLACING TUGGERS AT LEFT EDGE TEST POSITIONS")
    print("=" * 80)
    print()

    # Place all tuggers simultaneously
    for test in LEFT_EDGE_TESTS:
        robot = ROBOTS[test["robot_idx"]]
        send_position(robot, test["x"], test["y"], test["label"])

    print()
    print("=" * 80)
    print("LEFT EDGE TEST COMPLETE")
    print("=" * 80)
    print()
    print("Current positions:")
    print("  tugger-01: X=50,000  Y=150,000")
    print("  tugger-02: X=75,000  Y=150,000")
    print("  tugger-03: X=100,000 Y=150,000")
    print()
    print("All tuggers should be at the SAME Y coordinate (150k)")
    print("They are spread across X from 50k to 100k")
    print()
    print("CHECK TWINZO NOW:")
    print("  - Which tugger is CLOSEST to the LEFT edge of factory floor?")
    print("  - Which tuggers are ON the floor vs OFF the floor?")
    print("  - Take a screenshot!")

if __name__ == "__main__":
    main()
