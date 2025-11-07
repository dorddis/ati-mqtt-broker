#!/usr/bin/env python3
"""
Test streaming AMR data to both plants (HiTech and Old Plant)
"""
import os
import json
import requests
import time
from datetime import datetime

# Twinzo OAuth configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

# API URLs
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_BASE_URL = "https://api.platform.twinzo.com/v3"

# Known sector information
SECTORS = {
    "hitech": {
        "name": "Sector 1",
        "guid": "8010257b-d416-43e2-b1a3-cc98604bb117",
        "branch_id": 1,
        "branch_guid": "dcac4881-05ab-4f29-b0df-79c40df9c9c2",
        "width": 265337.97,
        "height": 265337.97,
        "sector_id": 1  # We know this from earlier
    },
    "old_plant": {
        "name": "Main",
        "guid": "07dd750f-6ad8-4122-9030-35bbc696a38b",
        "branch_id": 2,
        "branch_guid": "40557468-2d57-4a3d-9a5e-3eede177daf5",
        "width": 250000,
        "height": 250000,
        "sector_id": None  # Need to find this
    }
}

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
            return {
                "token": auth_data["Token"],
                "client": auth_data["Client"],
                "branch": auth_data["Branch"],
                "branch_guid": auth_data["Branch"]
            }
        else:
            print(f"Authentication failed for {device_login}: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"Authentication error for {device_login}: {e}")
        return None

def get_sectors_for_branch(credentials):
    """Get sectors for the authenticated branch"""
    url = f"{TWINZO_BASE_URL}/sectors"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials["client"],
        "Branch": credentials["branch"],
        "Token": credentials["token"],
        "Api-Key": TWINZO_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get sectors: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"Error getting sectors: {e}")
        return None

def test_localization_post(credentials, sector_id, plant_name):
    """Test posting localization data to a specific sector"""
    url = f"{TWINZO_BASE_URL}/localization"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials["client"],
        "Branch": credentials["branch"],
        "Token": credentials["token"],
        "Api-Key": TWINZO_API_KEY
    }

    # Create test payload
    payload = [
        {
            "Timestamp": int(time.time() * 1000),
            "SectorId": sector_id,
            "X": 10000.0,
            "Y": 20000.0,
            "Z": 0.0,
            "Interval": 100,
            "Battery": 85,
            "IsMoving": True,
            "LocalizationAreas": [],
            "NoGoAreas": []
        }
    ]

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        print(f"\n--- Testing {plant_name} (SectorId: {sector_id}) ---")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print(f"SUCCESS! Posted to {plant_name}")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"FAILED! Error posting to {plant_name}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Error posting to {plant_name}: {e}")
        return False

def discover_old_plant_sector_id(credentials):
    """Try to discover the sector ID for the old plant"""
    print("\n=== Attempting to Discover Old Plant Sector ID ===")

    # Strategy 1: Try common sector IDs (2, 3, 4, etc.)
    print("\nStrategy 1: Trying common sector IDs...")
    for sector_id in [2, 3, 4, 5]:
        result = test_localization_post(credentials, sector_id, f"Old Plant (trying ID {sector_id})")
        if result:
            print(f"\nFOUND IT! Old plant sector ID is: {sector_id}")
            return sector_id

    print("\nCould not find old plant sector ID with common values")
    return None

def main():
    print("="*80)
    print("MULTI-PLANT AMR STREAMING TEST")
    print("="*80)

    print("\nKnown Sector Information:")
    print(f"  HiTech Plant: {SECTORS['hitech']['name']}")
    print(f"    - Branch ID: {SECTORS['hitech']['branch_id']}")
    print(f"    - Branch GUID: {SECTORS['hitech']['branch_guid']}")
    print(f"    - Sector GUID: {SECTORS['hitech']['guid']}")
    print(f"    - Sector ID: {SECTORS['hitech']['sector_id']}")
    print(f"    - Size: {SECTORS['hitech']['width']/1000:.2f}m x {SECTORS['hitech']['height']/1000:.2f}m")

    print(f"\n  Old Plant: {SECTORS['old_plant']['name']}")
    print(f"    - Branch ID: {SECTORS['old_plant']['branch_id']}")
    print(f"    - Branch GUID: {SECTORS['old_plant']['branch_guid']}")
    print(f"    - Sector GUID: {SECTORS['old_plant']['guid']}")
    print(f"    - Sector ID: UNKNOWN (to be discovered)")
    print(f"    - Size: {SECTORS['old_plant']['width']/1000:.2f}m x {SECTORS['old_plant']['height']/1000:.2f}m")

    # Step 1: Authenticate as tugger-01
    print("\n" + "="*80)
    print("STEP 1: Authenticate Device")
    print("="*80)

    credentials = authenticate("tugger-01")
    if not credentials:
        print("Authentication failed. Exiting.")
        return

    print(f"\nAuthenticated as tugger-01")
    print(f"  Branch: {credentials['branch']}")
    print(f"  Client: {credentials['client']}")

    # Step 2: Get sectors for current branch
    print("\n" + "="*80)
    print("STEP 2: Get Sectors for Authenticated Branch")
    print("="*80)

    sectors = get_sectors_for_branch(credentials)
    if sectors:
        print(f"\nFound {len(sectors)} sector(s):")
        for sector in sectors:
            print(f"\n  Sector: {sector.get('Title', 'N/A')}")
            print(f"    - ID: {sector.get('Id', 'N/A')}")
            print(f"    - GUID: {sector.get('Guid', 'N/A')}")
            print(f"    - Branch ID: {sector.get('BranchId', 'N/A')}")
            print(f"    - Size: {sector.get('SectorWidth', 0)/1000:.2f}m x {sector.get('SectorHeight', 0)/1000:.2f}m")

    # Step 3: Test posting to HiTech plant (SectorId: 1)
    print("\n" + "="*80)
    print("STEP 3: Test Posting to HiTech Plant")
    print("="*80)

    hitech_success = test_localization_post(
        credentials,
        SECTORS['hitech']['sector_id'],
        "HiTech Plant"
    )

    # Step 4: Try to find and post to old plant
    print("\n" + "="*80)
    print("STEP 4: Discover and Test Old Plant Sector")
    print("="*80)

    old_plant_sector_id = discover_old_plant_sector_id(credentials)

    if old_plant_sector_id:
        SECTORS['old_plant']['sector_id'] = old_plant_sector_id

    # Step 5: Summary and next steps
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    print(f"\nHiTech Plant (Sector 1): {'SUCCESS' if hitech_success else 'FAILED'}")

    if old_plant_sector_id:
        print(f"Old Plant (Sector {old_plant_sector_id}): SUCCESS")
        print(f"\nGREAT NEWS! Both plants are accessible!")
        print(f"\nTo stream to both plants simultaneously, use:")
        print(f"  - HiTech: SectorId = {SECTORS['hitech']['sector_id']}")
        print(f"  - Old Plant: SectorId = {old_plant_sector_id}")

        print(f"\nNext step: Update bridge code to post to both sectors")
    else:
        print(f"Old Plant: COULD NOT ACCESS")
        print(f"\nPossible reasons:")
        print(f"  1. Device 'tugger-01' is not authorized for Branch 2 (old plant)")
        print(f"  2. Old plant sector has a different ID that we haven't tried")
        print(f"  3. Need to authenticate with a device that's bound to old plant")

        print(f"\nTroubleshooting steps:")
        print(f"  1. Check Twinzo UI to see what sector ID the old plant has")
        print(f"  2. Create a device bound to Branch 2 (old plant)")
        print(f"  3. Try authenticating with different device credentials")

    # Additional info
    print("\n" + "="*80)
    print("DEVICE AUTHORIZATION INFO")
    print("="*80)
    print(f"\nCurrent authentication:")
    print(f"  Device: tugger-01")
    print(f"  Branch: {credentials['branch']}")
    print(f"  This is Branch ID 1 (HiTech) based on GUID")
    print(f"\nThe device might only be authorized for one branch.")
    print(f"To access both plants, you may need to:")
    print(f"  - Authorize tugger-01 for both branches, OR")
    print(f"  - Create separate devices for each plant")

if __name__ == "__main__":
    main()
