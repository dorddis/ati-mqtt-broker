#!/usr/bin/env python3
"""
Map Factory Floor - Place tuggers at visible factory corners
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

# Based on screenshot - factory floor appears to be between 50k-250k
TEST_POSITIONS = {
    "tugger-01": {
        "x": 50000,
        "y": 50000,
        "description": "Top-Left Factory Corner"
    },
    "tugger-02": {
        "x": 150000,
        "y": 150000,
        "description": "Center of Factory Floor"
    },
    "tugger-03": {
        "x": 250000,
        "y": 250000,
        "description": "Bottom-Right Factory Corner"
    }
}

oauth_cache = {}

def authenticate_device(device_login):
    auth_payload = {"client": TWINZO_CLIENT, "login": device_login, "password": TWINZO_PASSWORD}
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

    response = requests.post(TWINZO_LOCALIZATION_URL, headers=headers, json=payload, timeout=5)
    if response.status_code == 200:
        print(f"✓ {robot['device_id']}: X={x}, Y={y} - {description}")
        return True
    else:
        print(f"✗ {robot['device_id']}: Failed")
        return False

def main():
    print("=" * 80)
    print("MAPPING FACTORY FLOOR CORNERS")
    print("=" * 80)
    print()

    for robot in ROBOTS:
        authenticate_device(robot["oauth_login"])

    print()
    for robot in ROBOTS:
        position = TEST_POSITIONS[robot["device_id"]]
        send_position(robot, position["x"], position["y"], position["description"])

    print()
    print("=" * 80)
    print("tugger-01: (50000, 50000) - Top-Left")
    print("tugger-02: (150000, 150000) - Center")
    print("tugger-03: (250000, 250000) - Bottom-Right")
    print("=" * 80)
    print()
    print("Refresh Twinzo and tell me WHERE each tugger appears!")
    print("For example: 'tugger-01 is at the loading dock area'")

if __name__ == "__main__":
    main()
