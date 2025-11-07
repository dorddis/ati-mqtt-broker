#!/usr/bin/env python3
"""
Systematic Grid Coordinate Test
Tests a grid of coordinates to map the factory floor bounds precisely
"""
import requests
import json
import time

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

ROBOTS = [
    {"device_id": "tugger-01", "oauth_login": "tugger-01", "battery": 79},
    {"device_id": "tugger-02", "oauth_login": "tugger-02", "battery": 77},
    {"device_id": "tugger-03", "oauth_login": "tugger-03", "battery": 75},
]

# Test grid: 9 points covering the suspected factory floor area
# Based on previous tests: 100k is on floor, 0 and 300k are off
# Testing: 75k, 125k, 175k, 225k to narrow down bounds
GRID_TESTS = [
    # Top row (Y = 75k)
    {"x": 75000, "y": 75000, "label": "Top-Left", "robot": 0},
    {"x": 150000, "y": 75000, "label": "Top-Center", "robot": 1},
    {"x": 225000, "y": 75000, "label": "Top-Right", "robot": 2},

    # Middle row (Y = 150k)
    {"x": 75000, "y": 150000, "label": "Mid-Left", "robot": 0},
    {"x": 150000, "y": 150000, "label": "Center", "robot": 1},
    {"x": 225000, "y": 150000, "label": "Mid-Right", "robot": 2},

    # Bottom row (Y = 225k)
    {"x": 75000, "y": 225000, "label": "Bottom-Left", "robot": 0},
    {"x": 150000, "y": 225000, "label": "Bottom-Center", "robot": 1},
    {"x": 225000, "y": 225000, "label": "Bottom-Right", "robot": 2},
]

oauth_cache = {}

def authenticate_device(device_login):
    auth_payload = {
        "client": TWINZO_CLIENT,
        "login": device_login,
        "password": TWINZO_PASSWORD
    }
    response = requests.post(TWINZO_AUTH_URL, json=auth_payload, timeout=10)
    if response.status_code == 200:
        auth_data = response.json()
        oauth_cache[device_login] = {
            "token": auth_data["Token"],
            "client": auth_data["Client"],
            "branch": auth_data["Branch"],
            "expires": auth_data["Expiration"]
        }
        return oauth_cache[device_login]
    return None

def send_position(robot, x, y, description):
    credentials = oauth_cache.get(robot["oauth_login"])
    if not credentials:
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
            print(f"  OK {robot['device_id']}: ({x}, {y}) - {description}")
            return True
        else:
            print(f"  FAIL {robot['device_id']}: ({x}, {y}) - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ERROR {robot['device_id']}: ({x}, {y}) - {e}")
        return False

def main():
    print("=" * 80)
    print("SYSTEMATIC GRID COORDINATE TEST")
    print("=" * 80)
    print()
    print("Testing 9 grid points to map factory floor bounds")
    print("Grid: 75k, 150k, 225k on both X and Y axes")
    print()

    # Authenticate all robots
    print("Authenticating robots...")
    for robot in ROBOTS:
        if authenticate_device(robot["oauth_login"]):
            print(f"  {robot['device_id']}: OK")

    print()
    print("=" * 80)
    print("GRID TEST SEQUENCE")
    print("=" * 80)
    print()
    print("After each placement, check Twinzo and note:")
    print("  - Is the tugger visible on the factory floor?")
    print("  - If yes, where exactly is it located?")
    print("  - If no, it's outside the visible area")
    print()

    # Test each grid point with 3 second delay between tests
    for i, test in enumerate(GRID_TESTS, 1):
        print(f"Test {i}/9: {test['label']}")
        robot = ROBOTS[test["robot"]]
        send_position(robot, test["x"], test["y"], test["label"])
        print()

        if i < len(GRID_TESTS):
            print("Waiting 5 seconds before next test...")
            print()
            time.sleep(5)

    print("=" * 80)
    print("GRID TEST COMPLETE")
    print("=" * 80)
    print()
    print("Review Results:")
    print()
    print("Grid Points Tested:")
    print("  75k      150k     225k")
    print("  -------------------------")
    print("  TL       TC       TR      75k")
    print("  ML       C        MR      150k")
    print("  BL       BC       BR      225k")
    print()
    print("For each point, note if tugger was:")
    print("  - ON FLOOR: visible on factory layout")
    print("  - OFF MAP: not visible (outside bounds)")
    print()
    print("This will help determine the actual coordinate bounds!")

if __name__ == "__main__":
    main()
