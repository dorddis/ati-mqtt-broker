#!/usr/bin/env python3
"""
Twinzo Device Management Utility

Manage Twinzo devices via API: list, create, delete

Usage:
  python -X utf8 manage_twinzo_devices.py list [plant]
  python -X utf8 manage_twinzo_devices.py create <login> <plant> [--title TITLE] [--note NOTE] [--sector SECTOR]
  python -X utf8 manage_twinzo_devices.py delete <device_id> <plant>

Examples:
  # List devices in both plants
  python -X utf8 manage_twinzo_devices.py list

  # List devices in specific plant
  python -X utf8 manage_twinzo_devices.py list hitech
  python -X utf8 manage_twinzo_devices.py list old

  # Create a new device in HiTech plant
  python -X utf8 manage_twinzo_devices.py create tugger-10 hitech --title "Tugger 10" --note "New AMR"

  # Create a new device in Old Plant
  python -X utf8 manage_twinzo_devices.py create tugger-07-old old --title "Tugger 07 Old" --sector 2

  # Delete a device
  python -X utf8 manage_twinzo_devices.py delete 13 hitech
"""
import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, List

# Twinzo API configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
DEVICES_URL = "https://api.platform.twinzo.com/v3/devices"

# Plant configurations
PLANTS = {
    "hitech": {
        "name": "HiTech Plant",
        "branch_guid": "dcac4881-05ab-4f29-b0df-79c40df9c9c2",
        "branch_id": 1,
        "sector_id": 1,
        "reference_device": "tugger-03"
    },
    "old": {
        "name": "Old Plant",
        "branch_guid": "40557468-2d57-4a3d-9a5e-3eede177daf5",
        "branch_id": 2,
        "sector_id": 2,
        "reference_device": "tugger-05-old"
    }
}

def authenticate(device_login: str) -> Optional[Dict]:
    """Authenticate with Twinzo API"""
    try:
        r = requests.post(AUTH_URL, json={
            "client": TWINZO_CLIENT,
            "login": device_login,
            "password": TWINZO_PASSWORD
        }, timeout=10)

        if r.status_code == 200:
            return r.json()
        else:
            print(f"FAIL Authentication failed: {r.status_code}")
            print(r.text)
            return None
    except Exception as e:
        print(f"FAIL Authentication error: {e}")
        return None

def get_headers(creds: Dict) -> Dict:
    """Create API headers from credentials"""
    return {
        "Content-Type": "application/json",
        "Client": creds["Client"],
        "Branch": creds["Branch"],
        "Token": creds["Token"],
        "Api-Key": TWINZO_API_KEY
    }

def list_devices(plant: Optional[str] = None) -> None:
    """List devices in plant(s)"""
    plants_to_check = [plant] if plant else list(PLANTS.keys())

    for plant_key in plants_to_check:
        if plant_key not in PLANTS:
            print(f"FAIL Unknown plant: {plant_key}")
            continue

        plant_info = PLANTS[plant_key]
        print()
        print("=" * 70)
        print(f"{plant_info['name']} (Branch {plant_info['branch_id']})")
        print("=" * 70)

        # Authenticate with reference device
        creds = authenticate(plant_info["reference_device"])
        if not creds:
            continue

        headers = get_headers(creds)

        # Get devices
        try:
            r = requests.get(DEVICES_URL, headers=headers, timeout=10)
            if r.status_code == 200:
                devices = r.json()
                print(f"Found {len(devices)} devices:")
                print()

                for d in devices:
                    sector = d.get('SectorId', 'None')
                    print(f"  ID: {d.get('Id'):3}  Login: {d.get('Login'):20}  Title: {d.get('Title'):20}  Sector: {sector}")
            else:
                print(f"FAIL GET /devices failed: {r.status_code}")
                print(r.text)
        except Exception as e:
            print(f"FAIL Error: {e}")

def create_device(login: str, plant: str, title: Optional[str] = None,
                 note: Optional[str] = None, sector: Optional[int] = None) -> None:
    """Create a new device"""
    if plant not in PLANTS:
        print(f"FAIL Unknown plant: {plant}")
        return

    plant_info = PLANTS[plant]

    print()
    print(f"Creating device in {plant_info['name']}...")
    print(f"  Login: {login}")

    # Authenticate with reference device
    creds = authenticate(plant_info["reference_device"])
    if not creds:
        return

    headers = get_headers(creds)

    # Generate MAC address (random)
    import random
    mac = ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])

    # Prepare device data
    device_data = {
        "Login": login,
        "Title": title or login,
        "Mac": mac,
        "BranchId": plant_info["branch_id"],
        "SectorId": sector or plant_info["sector_id"],
        "DeviceTypeId": 2,  # Tugger type
        "Note": note or f"Created via API for {plant_info['name']}"
    }

    print()
    print("Device data:")
    print(json.dumps(device_data, indent=2))
    print()

    # Create device
    try:
        r = requests.post(DEVICES_URL, headers=headers, json=device_data, timeout=10)
        if r.status_code == 201:
            created = r.json()
            print("SUCCESS Device created:")
            print(json.dumps(created, indent=2))
        else:
            print(f"FAIL POST /devices failed: {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"FAIL Error: {e}")

def delete_device(device_id: int, plant: str) -> None:
    """Delete a device"""
    if plant not in PLANTS:
        print(f"FAIL Unknown plant: {plant}")
        return

    plant_info = PLANTS[plant]

    print()
    print(f"Deleting device {device_id} from {plant_info['name']}...")

    # Authenticate with reference device
    creds = authenticate(plant_info["reference_device"])
    if not creds:
        return

    headers = get_headers(creds)

    # Delete device
    try:
        delete_url = f"{DEVICES_URL}/{device_id}"
        r = requests.delete(delete_url, headers=headers, timeout=10)
        if r.status_code == 204:
            print(f"SUCCESS Device {device_id} deleted")
        else:
            print(f"FAIL DELETE /devices/{device_id} failed: {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"FAIL Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Manage Twinzo devices via API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List devices")
    list_parser.add_argument("plant", nargs="?", choices=["hitech", "old"],
                           help="Plant to list (default: both)")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a device")
    create_parser.add_argument("login", help="Device login name")
    create_parser.add_argument("plant", choices=["hitech", "old"], help="Target plant")
    create_parser.add_argument("--title", help="Device title (default: same as login)")
    create_parser.add_argument("--note", help="Device note")
    create_parser.add_argument("--sector", type=int, help="Sector ID (default: plant default)")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a device")
    delete_parser.add_argument("device_id", type=int, help="Device ID to delete")
    delete_parser.add_argument("plant", choices=["hitech", "old"], help="Plant containing device")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "list":
        list_devices(args.plant)
    elif args.command == "create":
        create_device(args.login, args.plant, args.title, args.note, args.sector)
    elif args.command == "delete":
        delete_device(args.device_id, args.plant)

if __name__ == "__main__":
    main()
