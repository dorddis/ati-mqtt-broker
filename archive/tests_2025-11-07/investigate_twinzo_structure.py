#!/usr/bin/env python3
"""
Investigate Twinzo API structure to understand branches, sectors, and GUIDs
"""
import os
import json
import requests
from datetime import datetime

# Twinzo OAuth configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

# API URLs
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_BASE_URL = "https://api.platform.twinzo.com/v3"

# Known plant/branch IDs
OLD_PLANT_GUID = "40557468-2d57-4a3d-9a5e-3eede177daf5"  # Original spaghetti diagrams
NEW_PLANT_GUID = "dcac4881-05ab-4f29-b0df-79c40df9c9c2"  # New HiTech plant
NEW_SECTOR_GUID = "8010257b-d416-43e2-b1a3-cc98604bb117"  # Sector in new plant

def authenticate(device_login="tugger-01"):
    """Authenticate and return credentials"""
    try:
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
            print(f"\n=== Authentication Successful for {device_login} ===")
            print(f"Token: {auth_data['Token'][:50]}...")
            print(f"Client: {auth_data['Client']}")
            print(f"Branch: {auth_data['Branch']}")
            print(f"Expiration: {datetime.fromtimestamp(auth_data['Expiration']/1000)}")
            return {
                "token": auth_data["Token"],
                "client": auth_data["Client"],
                "branch": auth_data["Branch"]
            }
        else:
            print(f"\nAuthentication failed: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\nAuthentication error: {e}")
        return None

def make_api_call(endpoint, credentials, method="GET", data=None):
    """Make an API call with credentials"""
    url = f"{TWINZO_BASE_URL}/{endpoint}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials["client"],
        "Branch": credentials["branch"],
        "Token": credentials["token"],
        "Api-Key": TWINZO_API_KEY
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)

        print(f"\n=== {method} {endpoint} ===")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"API call error: {e}")
        return None

def investigate_branches(credentials):
    """Investigate branch structure"""
    print("\n" + "="*80)
    print("INVESTIGATING BRANCHES")
    print("="*80)

    # Try to get branch list
    branches = make_api_call("branches", credentials)
    if branches:
        print(f"\nFound {len(branches)} branches:")
        for i, branch in enumerate(branches):
            print(f"\n--- Branch {i+1} ---")
            print(json.dumps(branch, indent=2))

    # Try to get current branch info
    current_branch = make_api_call(f"branches/{credentials['branch']}", credentials)
    if current_branch:
        print(f"\nCurrent Branch Details:")
        print(json.dumps(current_branch, indent=2))

def investigate_sectors(credentials):
    """Investigate sector structure"""
    print("\n" + "="*80)
    print("INVESTIGATING SECTORS")
    print("="*80)

    # Try to get sector list
    sectors = make_api_call("sectors", credentials)
    if sectors:
        print(f"\nFound {len(sectors)} sectors:")
        for i, sector in enumerate(sectors):
            print(f"\n--- Sector {i+1} ---")
            print(json.dumps(sector, indent=2))

def investigate_plants(credentials):
    """Investigate plant/facility structure"""
    print("\n" + "="*80)
    print("INVESTIGATING PLANTS/FACILITIES")
    print("="*80)

    # Try various potential endpoints
    endpoints = [
        "plants",
        "facilities",
        "locations",
        "sites",
        f"branches/{OLD_PLANT_GUID}",
        f"branches/{NEW_PLANT_GUID}",
        f"sectors/{NEW_SECTOR_GUID}"
    ]

    for endpoint in endpoints:
        result = make_api_call(endpoint, credentials)
        if result:
            print(f"\nSuccess! {endpoint} returned:")
            print(json.dumps(result, indent=2))

def investigate_localization_with_guid(credentials):
    """Test posting localization data with different GUIDs"""
    print("\n" + "="*80)
    print("TESTING LOCALIZATION WITH DIFFERENT IDS")
    print("="*80)

    test_cases = [
        ("SectorId (integer)", 1),
        ("Old Plant GUID", OLD_PLANT_GUID),
        ("New Plant GUID", NEW_PLANT_GUID),
        ("New Sector GUID", NEW_SECTOR_GUID),
    ]

    for name, sector_id in test_cases:
        print(f"\n--- Testing with {name}: {sector_id} ---")

        payload = [
            {
                "Timestamp": int(datetime.now().timestamp() * 1000),
                "SectorId": sector_id,
                "X": 1000.0,
                "Y": 2000.0,
                "Z": 0.0,
                "Interval": 100,
                "Battery": 85,
                "IsMoving": False,
                "LocalizationAreas": [],
                "NoGoAreas": []
            }
        ]

        result = make_api_call("localization", credentials, method="POST", data=payload)

def investigate_device_management(credentials):
    """Investigate device/asset management"""
    print("\n" + "="*80)
    print("INVESTIGATING DEVICES/ASSETS")
    print("="*80)

    endpoints = [
        "devices",
        "assets",
        "robots",
        "amrs",
        "vehicles"
    ]

    for endpoint in endpoints:
        result = make_api_call(endpoint, credentials)

def main():
    print("="*80)
    print("TWINZO API STRUCTURE INVESTIGATION")
    print("="*80)
    print(f"\nOld Plant GUID (spaghetti): {OLD_PLANT_GUID}")
    print(f"New Plant GUID (HiTech): {NEW_PLANT_GUID}")
    print(f"New Sector GUID: {NEW_SECTOR_GUID}")

    # Authenticate
    credentials = authenticate()
    if not credentials:
        print("\nFailed to authenticate. Exiting.")
        return

    # Run investigations
    investigate_branches(credentials)
    investigate_sectors(credentials)
    investigate_plants(credentials)
    investigate_device_management(credentials)
    investigate_localization_with_guid(credentials)

    print("\n" + "="*80)
    print("INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
