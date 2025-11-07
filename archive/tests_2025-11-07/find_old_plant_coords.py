#!/usr/bin/env python3
"""Find visible coordinates for Old Plant by testing different positions"""
import os, requests, time

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
LOC_URL = "https://api.platform.twinzo.com/v3/localization"

print("Finding Old Plant visible coordinates...")
print("Watch the Old Plant UI and tell me which position you see!")
print("Old Plant: https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5")
print()

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

# Test different coordinate ranges
# Old plant sector is 250m x 250m according to the info
test_positions = [
    ("Center (125m, 125m)", 125000, 125000),
    ("Origin (0, 0)", 0, 0),
    ("Small (10m, 10m)", 10000, 10000),
    ("Bottom Right (240m, 240m)", 240000, 240000),
    ("Top Left (10m, 10m)", 10000, 10000),
    ("Mid-high (125m, 200m)", 125000, 200000),
    ("Publisher range (200m, 200m)", 200000, 200000),
]

for i, (name, x, y) in enumerate(test_positions):
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

    print(f"\n{i+1}. Testing {name} -> ({x/1000:.0f}m, {y/1000:.0f}m)")
    r = requests.post(LOC_URL, headers=headers, json=payload, timeout=15)
    print(f"   Status: {r.status_code}")

    print("   Waiting 5 seconds... Check if you see tugger-01 move in Old Plant UI!")
    time.sleep(5)

print("\n\nDone! Which position(s) did you see tugger-01 appear at?")
