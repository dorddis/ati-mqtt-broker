#!/usr/bin/env python3
"""
Test Specific Coordinates on Twinzo Platform
Place tuggers at exact positions to map the factory floor
"""
import requests
import json
import time
from datetime import datetime

# Twinzo Configuration
TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

# Robot Configuration
ROBOTS = [
    {"device_id": "tugger-01", "oauth_login": "tugger-01", "battery": 79},
    {"device_id": "tugger-02", "oauth_login": "tugger-02", "battery": 77},
    {"device_id": "tugger-03", "oauth_login": "tugger-03", "battery": 75},
]

# Test positions - we'll place each tugger at a specific coordinate
# Current known bounds from config:
# X: 195630.16 to 223641.36
# Y: 188397.78 to 213782.93

TEST_POSITIONS = {
    "tugger-01": {
        "x": 195630.16,  # Min X (left edge)
        "y": 188397.78,  # Min Y (top edge)
        "description": "Top-Left Corner"
    },
    "tugger-02": {
        "x": 209635.76,  # Center X
        "y": 201090.35,  # Center Y
        "description": "Center of Factory"
    },
    "tugger-03": {
        "x": 223641.36,  # Max X (right edge)
        "y": 213782.93,  # Max Y (bottom edge)
        "description": "Bottom-Right Corner"
    }
}

# OAuth token cache
oauth_cache = {}

def authenticate_device(device_login):
    """Authenticate device with Twinzo OAuth"""
    try:
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
        else:
            print(f"Auth failed for {device_login}: {response.status_code}")
            return None

    except Exception as e:
        print(f"Auth error for {device_login}: {e}")
        return None

def send_position(robot, x, y, description):
    """Send specific position to Twinzo"""
    credentials = oauth_cache.get(robot["oauth_login"])
    if not credentials:
        print(f"No credentials for {robot['device_id']}")
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
        response = requests.post(TWINZO_LOCALIZATION_URL, headers=headers, json=payload, timeout=5)

        if response.status_code == 200:
            print(f"✓ {robot['device_id']}: X={x:.1f}, Y={y:.1f} - {description}")
            return True
        else:
            print(f"✗ {robot['device_id']}: Failed - {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ {robot['device_id']}: Error - {e}")
        return False

def main():
    print("=" * 80)
    print("COORDINATE MAPPING TEST - Place Tuggers at Specific Positions")
    print("=" * 80)
    print()
    print("This will place each tugger at a known coordinate.")
    print("Take a screenshot after each placement to see where they appear!")
    print()

    # Authenticate all robots
    print("Authenticating robots...")
    for robot in ROBOTS:
        authenticate_device(robot["oauth_login"])

    print()
    print("=" * 80)
    print("Placing tuggers at test positions...")
    print("=" * 80)
    print()

    for robot in ROBOTS:
        position = TEST_POSITIONS[robot["device_id"]]
        send_position(
            robot,
            position["x"],
            position["y"],
            position["description"]
        )

    print()
    print("=" * 80)
    print("POSITIONS SET!")
    print("=" * 80)
    print()
    print("Check Twinzo platform now. You should see:")
    print(f"  tugger-01: {TEST_POSITIONS['tugger-01']['description']}")
    print(f"  tugger-02: {TEST_POSITIONS['tugger-02']['description']}")
    print(f"  tugger-03: {TEST_POSITIONS['tugger-03']['description']}")
    print()
    print("Take a screenshot and tell me where each tugger appears!")
    print()
    print("We can then adjust coordinates to map specific factory locations.")

if __name__ == "__main__":
    main()
