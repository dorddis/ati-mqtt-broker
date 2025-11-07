#!/usr/bin/env python3
"""
Find Actual Factory Floor Coordinate Bounds
Test extreme coordinates to see where tuggers disappear/appear
"""
import requests
import json
import time

# Twinzo Configuration
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

# Test much wider spread - try extreme values
TEST_POSITIONS = {
    "tugger-01": {
        "x": 0,
        "y": 0,
        "description": "Origin (0, 0)"
    },
    "tugger-02": {
        "x": 100000,
        "y": 100000,
        "description": "Mid range (100k, 100k)"
    },
    "tugger-03": {
        "x": 300000,
        "y": 300000,
        "description": "High range (300k, 300k)"
    }
}

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

    response = requests.post(TWINZO_LOCALIZATION_URL, headers=headers, json=payload, timeout=5)
    if response.status_code == 200:
        print(f"✓ {robot['device_id']}: X={x}, Y={y} - {description}")
        return True
    else:
        print(f"✗ {robot['device_id']}: Failed")
        return False

def main():
    print("=" * 80)
    print("FINDING FACTORY FLOOR BOUNDS - Testing Extreme Coordinates")
    print("=" * 80)
    print()

    for robot in ROBOTS:
        authenticate_device(robot["oauth_login"])

    print()
    print("Testing wide spread coordinates...")
    print()

    for robot in ROBOTS:
        position = TEST_POSITIONS[robot["device_id"]]
        send_position(robot, position["x"], position["y"], position["description"])

    print()
    print("=" * 80)
    print("Check Twinzo - where did they go?")
    print("=" * 80)
    print()
    print("tugger-01: (0, 0) - Origin")
    print("tugger-02: (100000, 100000) - Mid")
    print("tugger-03: (300000, 300000) - High")
    print()
    print("Take a screenshot and tell me:")
    print("- Which tuggers are visible?")
    print("- Where on the factory floor are they?")

if __name__ == "__main__":
    main()
