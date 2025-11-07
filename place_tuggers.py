#!/usr/bin/env python3
"""
Place Tuggers at Specific Coordinates - Command Line Tool

Usage:
  python -X utf8 place_tuggers.py <tugger_id> <x> <y>
  python -X utf8 place_tuggers.py all <x1,y1> <x2,y2> <x3,y3>

Examples:
  python -X utf8 place_tuggers.py 1 0 150000
  python -X utf8 place_tuggers.py all "0,150000" "75000,150000" "100000,150000"
"""
import requests
import sys
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
    {"device_id": "tugger-04", "oauth_login": "tugger-04", "battery": 73},
    {"device_id": "dzdB2rvp3k", "oauth_login": "dzdB2rvp3k", "battery": 71},
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
        print(f"Auth error for {device_login}: {e}")
    return False

def send_position(robot, x, y):
    credentials = oauth_cache.get(robot["oauth_login"])
    if not credentials:
        print(f"ERROR: {robot['device_id']} not authenticated")
        return False

    payload = [{
        "Timestamp": int(time.time() * 1000),
        "SectorId": 1,
        "X": float(x),
        "Y": float(y),
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
            print(f"OK: {robot['device_id']} at ({x}, {y})")
            return True
        else:
            print(f"FAIL: {robot['device_id']} - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {robot['device_id']} - {e}")
        return False

def show_usage():
    print(__doc__)
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        show_usage()

    # Authenticate all robots first
    print("Authenticating tuggers...")
    for robot in ROBOTS:
        authenticate_device(robot["oauth_login"])
    print()

    tugger_arg = sys.argv[1]

    if tugger_arg == "all":
        # Place all tuggers
        num_coords = len(sys.argv) - 2
        if num_coords < 1 or num_coords > 5:
            print("ERROR: 'all' requires 1-5 coordinate pairs")
            print("Example: python place_tuggers.py all \"0,0\" \"450000,0\" \"0,400000\" \"450000,400000\" \"225000,200000\"")
            sys.exit(1)

        for i in range(num_coords):
            coords = sys.argv[i + 2].split(',')
            if len(coords) != 2:
                print(f"ERROR: Invalid coordinate format: {sys.argv[i + 2]}")
                sys.exit(1)
            x, y = float(coords[0]), float(coords[1])
            send_position(ROBOTS[i], x, y)

    else:
        # Place single tugger
        if len(sys.argv) != 4:
            print("ERROR: Single tugger requires tugger_id, x, y")
            print("Example: python place_tuggers.py 1 0 150000")
            sys.exit(1)

        tugger_id = int(tugger_arg)
        if tugger_id < 1 or tugger_id > 5:
            print("ERROR: tugger_id must be 1-5")
            sys.exit(1)

        x = float(sys.argv[2])
        y = float(sys.argv[3])
        send_position(ROBOTS[tugger_id - 1], x, y)

if __name__ == "__main__":
    main()
