#!/usr/bin/env python3
"""
Test posting to specific coordinates to find what's visible in Twinzo
"""
import os
import requests
import time

TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

def authenticate(device_login="tugger-01"):
    auth_payload = {
        "client": TWINZO_CLIENT,
        "login": device_login,
        "password": TWINZO_PASSWORD
    }

    auth_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(TWINZO_AUTH_URL, headers=auth_headers, json=auth_payload, timeout=10)

    if response.status_code == 200:
        auth_data = response.json()
        return {
            "token": auth_data["Token"],
            "client": auth_data["Client"],
            "branch": auth_data["Branch"]
        }
    return None

def post_location(credentials, sector_id, x, y, device_name):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials["client"],
        "Branch": credentials["branch"],
        "Token": credentials["token"],
        "Api-Key": TWINZO_API_KEY
    }

    payload = [
        {
            "Timestamp": int(time.time() * 1000),
            "SectorId": sector_id,
            "X": x,
            "Y": y,
            "Z": 0,
            "Interval": 100,
            "Battery": 85,
            "IsMoving": True,
            "LocalizationAreas": [],
            "NoGoAreas": []
        }
    ]

    response = requests.post(TWINZO_LOCALIZATION_URL, headers=headers, json=payload, timeout=5)
    status = "OK" if response.status_code == 200 else f"FAIL {response.status_code}"
    print(f"  {device_name} at ({x:>8.0f}, {y:>8.0f}) -> Sector {sector_id}: {status}")

def main():
    print("="*80)
    print("TESTING VISIBLE COORDINATES IN TWINZO")
    print("="*80)
    print("\nThis will place test markers at different coordinates.")
    print("Check Twinzo UI to see which ones appear!\n")

    # Test coordinates covering different areas
    test_coords = [
        ("Origin", 0, 0),
        ("Small coords", 1000, 1000),
        ("10k", 10000, 10000),
        ("50k", 50000, 50000),
        ("100k", 100000, 100000),
        ("150k", 150000, 150000),
        ("200k Center", 200000, 200000),
        ("Publisher range", 210000, 200000),
        ("250k (Old Plant max)", 250000, 250000),
        ("265k (HiTech max)", 265000, 265000),
    ]

    creds = authenticate("tugger-01")
    if not creds:
        print("Authentication failed!")
        return

    print("\nPosting to BOTH sectors (will take ~20 seconds)...\n")

    for name, x, y in test_coords:
        print(f"{name}:")
        post_location(creds, 1, x, y, "HiTech")
        post_location(creds, 2, x, y, "Old Plant")
        time.sleep(2)  # Wait 2 seconds between each coordinate

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nNow check your Twinzo UI:")
    print("- HiTech: https://platform.twinzo.com/branch/dcac4881-05ab-4f29-b0df-79c40df9c9c2")
    print("- Old Plant: https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5")
    print("\nLook for tugger-01 appearing at different locations.")
    print("This will tell us what coordinate range is visible!")

if __name__ == "__main__":
    main()
