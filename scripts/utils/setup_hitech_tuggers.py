"""
Setup tug-78 and tug-140 in HiTech Plant if they don't exist.
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from integrations.twinzo.twinzo_api import TwinzoAPI

load_dotenv()

# HiTech Plant configuration
HITECH_PLANT = {
    'branch_id': 1,
    'branch_uuid': 'dcac4881-05ab-4f29-b0df-79c40df9c9c2',
    'sector_id': 1
}

# Devices to setup
DEVICES = [
    {'login': 'tug-78', 'title': 'Tugger 78'},
    {'login': 'tug-140', 'title': 'Tugger 140'}
]


def main():
    api = TwinzoAPI()

    print("=" * 80)
    print("SETUP TUG-78 AND TUG-140 IN HITECH PLANT")
    print("=" * 80)
    print()

    # List existing devices
    print(f"Checking existing devices in HiTech Plant (Branch {HITECH_PLANT['branch_id']})...")
    devices = api.list_devices(HITECH_PLANT['branch_id'])

    if devices is None:
        print("FAIL Could not list devices. Check API connection.")
        return

    existing_logins = [d['Login'] for d in devices]
    print(f"Found {len(devices)} existing devices")
    print()

    # Check and create each device
    for device in DEVICES:
        login = device['login']
        title = device['title']

        if login in existing_logins:
            print(f"OK {login} already exists in HiTech Plant")
        else:
            print(f"Creating {login} ({title})...")
            result = api.create_device(
                branch_id=HITECH_PLANT['branch_id'],
                login=login,
                title=title
            )

            if result:
                print(f"OK {login} created successfully (ID: {result.get('Id', 'N/A')})")
            else:
                print(f"FAIL Could not create {login}")
        print()

    # List final state
    print("=" * 80)
    print("FINAL DEVICE LIST - HITECH PLANT")
    print("=" * 80)
    devices = api.list_devices(HITECH_PLANT['branch_id'])
    if devices:
        for d in devices:
            print(f"  ID {d['Id']:3d}: {d['Login']:20s} - {d['Title']}")
    print()


if __name__ == "__main__":
    main()
