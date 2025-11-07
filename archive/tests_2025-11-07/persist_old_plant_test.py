#!/usr/bin/env python3
"""Keep tugger-01 visible at each test position for Old Plant"""
import os, requests, time

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
LOC_URL = "https://api.platform.twinzo.com/v3/localization"

print("="*70)
print("PERSISTENT OLD PLANT COORDINATE TEST")
print("="*70)
print("\nThis will keep tugger-01 visible at each position for 30 seconds.")
print("Open Old Plant UI NOW:")
print("https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5")
print("\nTell me which position you see tugger-01 at!")
print("="*70)

# Auth
r = requests.post(AUTH_URL, json={"client": TWINZO_CLIENT, "login": "tugger-01", "password": TWINZO_PASSWORD}, timeout=10)
auth = r.json()

headers = {
    "Content-Type": "application/json",
    "Client": auth["Client"],
    "Branch": auth["Branch"],
    "Token": auth["Token"],
    "Api-Key": TWINZO_API_KEY
}

# Test positions
positions = [
    ("ORIGIN (0, 0)", 0, 0),
    ("SMALL (10m, 10m)", 10000, 10000),
    ("MEDIUM (50m, 50m)", 50000, 50000),
    ("CENTER (125m, 125m)", 125000, 125000),
    ("HIGH (200m, 200m)", 200000, 200000),
    ("MAX (240m, 240m)", 240000, 240000),
]

for name, x, y in positions:
    print(f"\n{'='*70}")
    print(f"NOW TESTING: {name} -> X={x/1000:.0f}m, Y={y/1000:.0f}m")
    print(f"{'='*70}")
    print("Posting every second for 30 seconds...")

    for i in range(30):
        payload = [{
            "Timestamp": int(time.time() * 1000),
            "SectorId": 2,  # Old Plant
            "X": x,
            "Y": y,
            "Z": 0,
            "Interval": 100,
            "Battery": 85,
            "IsMoving": True,
            "LocalizationAreas": [],
            "NoGoAreas": []
        }]

        try:
            r = requests.post(LOC_URL, headers=headers, json=payload, timeout=10)
            if i % 5 == 0:
                print(f"  [{i+1}/30] Status: {r.status_code}")
        except Exception as e:
            print(f"  Error: {e}")

        time.sleep(1)

    print(f"\nDid you see tugger-01 at {name}? (check Old Plant UI)")
    input("Press ENTER to test next position...")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nWhich position(s) did you see tugger-01 at?")
