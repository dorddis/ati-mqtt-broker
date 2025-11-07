#!/usr/bin/env python3
"""Compare sector configurations between HiTech and Old Plant"""
import os, requests, json

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
BASE_URL = "https://api.platform.twinzo.com/v3"

print("="*80)
print("CHECKING SECTOR CONFIGURATIONS")
print("="*80)

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

# Get all sectors
print("\nFetching sectors...")
r = requests.get(f"{BASE_URL}/sectors", headers=headers, timeout=10)
sectors = r.json()

print(f"\nFound {len(sectors)} sector(s)")

for sector in sectors:
    print("\n" + "="*80)
    print(f"SECTOR: {sector.get('Title', 'N/A')}")
    print("="*80)
    print(f"ID: {sector.get('Id')}")
    print(f"GUID: {sector.get('Guid')}")
    print(f"Branch ID: {sector.get('BranchId')}")
    print(f"Floor: {sector.get('Floor', 0)} ({sector.get('FloorName', 'N/A')})")
    print(f"Size: {sector.get('SectorWidth', 0)/1000:.2f}m x {sector.get('SectorHeight', 0)/1000:.2f}m")
    print(f"Modified: {sector.get('Modified')}")

    # Check for localization features
    print(f"\nLocalization Features:")
    print(f"  GPS Items: {len(sector.get('GpsItems', []))}")
    print(f"  Areas: {len(sector.get('Areas', []))}")
    print(f"  Barriers: {len(sector.get('Barriers', []))}")
    print(f"  Beacons: {len(sector.get('Beacons', []))}")
    print(f"  Sensors: {len(sector.get('Sensors', []))}")
    print(f"  Paths: {len(sector.get('Paths', []))}")

    # Show full JSON for debugging
    print(f"\nFull Configuration:")
    print(json.dumps(sector, indent=2))

# Get branches too
print("\n" + "="*80)
print("CHECKING BRANCHES")
print("="*80)

r = requests.get(f"{BASE_URL}/branches", headers=headers, timeout=10)
branches = r.json()

for branch in branches:
    print(f"\nBranch: {branch.get('Title')}")
    print(f"  ID: {branch.get('Id')}")
    print(f"  GUID: {branch.get('Guid')}")
    print(f"  Sectors in response: {branch.get('Sectors', [])}")

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)
print("\nIf Old Plant sector is missing GPS Items, Beacons, or has different")
print("configuration, that could explain why devices don't appear.")
print("\nThe sector might need to be configured in Twinzo admin UI with:")
print("  - Localization settings enabled")
print("  - GPS/coordinate system set up")
print("  - Floor plan uploaded")
