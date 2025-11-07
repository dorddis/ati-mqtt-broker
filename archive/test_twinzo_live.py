#!/usr/bin/env python3
"""
Test Twinzo Live Integration
Simulates robots on Plant 4 layout and sends data to Twinzo API
"""
import requests
import json
import time
import math
from datetime import datetime

# Twinzo Configuration
TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

# Robot Configuration (from Twinzo screenshot)
ROBOTS = [
    {"device_id": "tugger-01", "oauth_login": "tugger-01", "battery": 79, "color": "🔵"},
    {"device_id": "tugger-02", "oauth_login": "tugger-02", "battery": 77, "color": "🟢"},
    {"device_id": "tugger-03", "oauth_login": "tugger-03", "battery": 75, "color": "🟡"},
]

# Coordinate bounds (from existing config)
REGION_MIN_X = 195630.16
REGION_MIN_Y = 188397.78
REGION_MAX_X = 223641.36
REGION_MAX_Y = 213782.93

# Calculate center and size
CENTER_X = (REGION_MIN_X + REGION_MAX_X) / 2
CENTER_Y = (REGION_MIN_Y + REGION_MAX_Y) / 2
RADIUS_X = (REGION_MAX_X - REGION_MIN_X) / 4
RADIUS_Y = (REGION_MAX_Y - REGION_MIN_Y) / 4

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

        print(f"   Authenticating {device_login}...")
        response = requests.post(TWINZO_AUTH_URL, json=auth_payload, timeout=10)

        if response.status_code == 200:
            auth_data = response.json()
            oauth_cache[device_login] = {
                "token": auth_data["Token"],
                "client": auth_data["Client"],
                "branch": auth_data["Branch"],
                "expires": auth_data["Expiration"]
            }
            print(f"   SUCCESS: {device_login}")
            return oauth_cache[device_login]
        else:
            print(f"   FAILED: {device_login} - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"   ERROR: {device_login} - {e}")
        return None

def calculate_position(robot_index, time_offset):
    """Calculate robot position in a circular/loop pattern"""
    speed = 0.5 + (robot_index * 0.2)
    angle_offset = (robot_index * 2 * math.pi / len(ROBOTS))
    angle = (time_offset * speed) + angle_offset
    x = CENTER_X + RADIUS_X * math.cos(angle)
    y = CENTER_Y + RADIUS_Y * math.sin(angle)
    return x, y

def send_position_to_twinzo(robot, x, y):
    """Send position data to Twinzo localization API"""
    credentials = oauth_cache.get(robot["oauth_login"])
    if not credentials:
        print(f"   {robot['color']} {robot['device_id']}: No credentials")
        return False

    payload = [{
        "Timestamp": int(time.time() * 1000),
        "SectorId": 1,
        "X": x,
        "Y": y,
        "Z": 0.0,
        "Interval": 60000,
        "Battery": robot["battery"],
        "IsMoving": True,
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
            print(f"   {robot['color']} {robot['device_id']}: X={x:.1f}, Y={y:.1f}, Battery={robot['battery']}% - OK")
            return True
        else:
            print(f"   {robot['color']} {robot['device_id']}: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"   {robot['color']} {robot['device_id']}: ERROR - {e}")
        return False

def main():
    print("=" * 80)
    print("TWINZO LIVE INTEGRATION TEST - Plant 4 AMR Simulation")
    print("=" * 80)
    print()
    print(f"Coordinate Bounds:")
    print(f"  X: {REGION_MIN_X:.2f} to {REGION_MAX_X:.2f}")
    print(f"  Y: {REGION_MIN_Y:.2f} to {REGION_MAX_Y:.2f}")
    print(f"  Center: ({CENTER_X:.2f}, {CENTER_Y:.2f})")
    print()
    print("Step 1: Authenticating robots with Twinzo OAuth...")
    print("-" * 80)

    authenticated = []
    for robot in ROBOTS:
        credentials = authenticate_device(robot["oauth_login"])
        if credentials:
            authenticated.append(robot)

    print()
    if not authenticated:
        print("ERROR: No robots authenticated successfully!")
        print("Check your Twinzo credentials and internet connection.")
        return

    print(f"SUCCESS: {len(authenticated)}/{len(ROBOTS)} robots authenticated")
    print()
    print("=" * 80)
    print("Step 2: Sending position updates to Twinzo...")
    print("-" * 80)
    print()

    update_count = 0
    start_time = time.time()

    try:
        while True:
            time_offset = time.time() - start_time

            print(f"Update #{update_count + 1} at {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 80)

            for i, robot in enumerate(authenticated):
                x, y = calculate_position(i, time_offset)
                send_position_to_twinzo(robot, x, y)

            update_count += 1
            print()
            print(f"Waiting 60 seconds before next update...")
            print(f"CHECK TWINZO PLATFORM NOW to see robot positions!")
            print()

            time.sleep(60)

    except KeyboardInterrupt:
        print()
        print("=" * 80)
        print(f"STOPPED - Total updates sent: {update_count}")
        print("=" * 80)

if __name__ == "__main__":
    main()
