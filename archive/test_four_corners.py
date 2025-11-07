#!/usr/bin/env python3
"""
Four Corner Coordinate Test
Tests the four corners of suspected factory floor area
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

# Test the four corners - tugger-01 gets all positions
# Based on previous tests: 100k is on floor, 0 and 300k are off
# Testing corners at 100k and 200k to stay within bounds
CORNER_POSITIONS = [
    {"x": 100000, "y": 100000, "label": "Top-Left Corner (100k, 100k)"},
    {"x": 200000, "y": 100000, "label": "Top-Right Corner (200k, 100k)"},
    {"x": 100000, "y": 200000, "label": "Bottom-Left Corner (100k, 200k)"},
    {"x": 200000, "y": 200000, "label": "Bottom-Right Corner (200k, 200k)"},
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
            return oauth_cache[device_login]
    except Exception as e:
        print(f"  Auth error: {e}")
    return None

def send_position(robot, x, y, description):
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
            print(f"  OK: {description}")
            return True
        else:
            print(f"  FAIL: {description} - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ERROR: {description} - {e}")
        return False

def main():
    print("=" * 80)
    print("FOUR CORNER TEST - Mapping Factory Floor Bounds")
    print("=" * 80)
    print()
    print("This will place tugger-01 at each corner position sequentially.")
    print("Testing coordinates: 100k to 200k range (known to be on floor)")
    print()

    # Authenticate tugger-01
    print("Authenticating tugger-01...")
    if authenticate_device(ROBOTS[0]["oauth_login"]):
        print("  SUCCESS")
    else:
        print("  FAILED - cannot continue")
        return

    print()
    print("=" * 80)
    print("CORNER TESTS")
    print("=" * 80)
    print()
    print("After each placement:")
    print("  1. Refresh Twinzo platform")
    print("  2. Note where tugger-01 appears on the factory floor")
    print("  3. Wait for next placement")
    print()

    # Test each corner
    for i, pos in enumerate(CORNER_POSITIONS, 1):
        print(f"Test {i}/4: {pos['label']}")
        send_position(ROBOTS[0], pos["x"], pos["y"], pos["label"])

        if i < len(CORNER_POSITIONS):
            print()
            print("Check Twinzo now! Waiting 8 seconds before next test...")
            print()
            time.sleep(8)

    print()
    print("=" * 80)
    print("FOUR CORNER TEST COMPLETE")
    print("=" * 80)
    print()
    print("Coordinates tested:")
    print("  (100k, 100k) - Top-Left")
    print("  (200k, 100k) - Top-Right")
    print("  (100k, 200k) - Bottom-Left")
    print("  (200k, 200k) - Bottom-Right")
    print()
    print("Based on where tugger-01 appeared at each position,")
    print("we can determine the coordinate system orientation.")

if __name__ == "__main__":
    main()
