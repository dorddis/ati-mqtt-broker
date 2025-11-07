#!/usr/bin/env python3
"""
Check what devices are configured in Twinzo and their branch associations
"""
import os
import json
import requests

# Twinzo OAuth configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

# API URLs
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_BASE_URL = "https://api.platform.twinzo.com/v3"

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
                "branch": auth_data["Branch"]
            }
        else:
            print(f"Authentication failed for {device_login}: {response.status_code}")
            return None

    except Exception as e:
        print(f"Authentication error for {device_login}: {e}")
        return None

def get_devices(credentials):
    """Get all devices"""
    url = f"{TWINZO_BASE_URL}/devices"

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
            print(f"Failed to get devices: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"Error getting devices: {e}")
        return None

def main():
    print("="*80)
    print("CHECKING TWINZO DEVICES CONFIGURATION")
    print("="*80)

    # Test devices to check
    test_devices = ["tugger-01", "tugger-02", "tugger-03"]

    print("\n=== Testing Device Authentication ===\n")
    device_auth_results = {}

    for device in test_devices:
        print(f"Authenticating {device}...")
        creds = authenticate(device)
        if creds:
            device_auth_results[device] = creds
            print(f"  Success! Branch: {creds['branch']}")
        else:
            print(f"  FAILED")
        print()

    # Get devices list using first successful auth
    if device_auth_results:
        first_device = list(device_auth_results.keys())[0]
        creds = device_auth_results[first_device]

        print("\n=== Getting Devices List ===\n")
        devices = get_devices(creds)

        if devices:
            print(f"Found {len(devices)} devices:\n")
            for i, device in enumerate(devices):
                print(f"--- Device {i+1} ---")
                print(json.dumps(device, indent=2))
                print()
        else:
            print("No devices found or empty response")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    print("\nDevice Authentication Results:")
    for device, creds in device_auth_results.items():
        print(f"  {device}: Branch {creds['branch']}")

    print("\nKey Findings:")
    print("  - All authenticated devices are bound to Branch:",
          creds['branch'] if creds else "N/A")
    print("  - To stream to old plant, need to:")
    print("    1. Create sector in old plant")
    print("    2. Authorize devices for old plant branch")
    print("    3. Update code to handle multi-branch streaming")

if __name__ == "__main__":
    main()
