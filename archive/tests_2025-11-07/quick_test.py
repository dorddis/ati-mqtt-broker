#!/usr/bin/env python3
"""Quick test - post one location and exit"""
import os, requests, time

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
LOC_URL = "https://api.platform.twinzo.com/v3/localization"

print("Quick test - posting tugger-01 to both sectors...")

# Auth
print("Authenticating...")
r = requests.post(AUTH_URL, json={"client": TWINZO_CLIENT, "login": "tugger-01", "password": TWINZO_PASSWORD}, timeout=10)
auth = r.json()
print(f"  Status: {r.status_code}")

headers = {
    "Content-Type": "application/json",
    "Client": auth["Client"],
    "Branch": auth["Branch"],
    "Token": auth["Token"],
    "Api-Key": TWINZO_API_KEY
}

# Post to Sector 1 at (100000, 100000)
payload = [{
    "Timestamp": int(time.time() * 1000),
    "SectorId": 1,
    "X": 100000,
    "Y": 100000,
    "Z": 0,
    "Interval": 100,
    "Battery": 85,
    "IsMoving": True,
    "LocalizationAreas": [],
    "NoGoAreas": []
}]

print(f"\nPosting to Sector 1 (HiTech) at (100000, 100000)...")
r = requests.post(LOC_URL, headers=headers, json=payload, timeout=15)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.text}")

# Post to Sector 2
payload[0]["SectorId"] = 2
print(f"\nPosting to Sector 2 (Old Plant) at (100000, 100000)...")
r = requests.post(LOC_URL, headers=headers, json=payload, timeout=15)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.text}")

print("\nDone! Check Twinzo UI to see if tugger-01 appears at (100m, 100m)")
print("  HiTech: https://platform.twinzo.com/branch/dcac4881-05ab-4f29-b0df-79c40df9c9c2")
print("  Old Plant: https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5")
