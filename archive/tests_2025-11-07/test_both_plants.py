#!/usr/bin/env python3
"""
Test both plants after moving devices:
- tugger-01, tugger-02 -> Old Plant (Branch 2)
- tugger-03, tugger-04 -> HiTech (Branch 1)
"""
import os, requests, time, math

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
LOC_URL = "https://api.platform.twinzo.com/v3/localization"

print("="*70)
print("TESTING BOTH PLANTS WITH SPLIT DEVICES")
print("="*70)
print("\nExpected setup:")
print("  Old Plant: tugger-01, tugger-02")
print("  HiTech: tugger-03, tugger-04")
print("\nOpen BOTH UIs:")
print("  HiTech: https://platform.twinzo.com/branch/dcac4881-05ab-4f29-b0df-79c40df9c9c2")
print("  Old Plant: https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5")
print("="*70)

# Device to sector mapping
# This will be auto-detected from authentication response
device_config = {
    "tugger-01": {"sector": None, "branch": None, "plant": "Old Plant"},
    "tugger-02": {"sector": None, "branch": None, "plant": "Old Plant"},
    "tugger-03": {"sector": None, "branch": None, "plant": "HiTech"},
    "tugger-04": {"sector": None, "branch": None, "plant": "HiTech"},
}

# Authenticate all devices
tuggers = {}
for device_name in device_config.keys():
    print(f"\nAuthenticating {device_name}...")
    r = requests.post(AUTH_URL, json={"client": TWINZO_CLIENT, "login": device_name, "password": TWINZO_PASSWORD}, timeout=10)
    if r.status_code == 200:
        d = r.json()
        tuggers[device_name] = {
            "token": d["Token"],
            "client": d["Client"],
            "branch": d["Branch"]
        }
        # Store branch info
        device_config[device_name]["branch"] = d["Branch"]

        # Determine which sector based on branch
        if d["Branch"] == "dcac4881-05ab-4f29-b0df-79c40df9c9c2":  # HiTech
            device_config[device_name]["sector"] = 1
            print(f"  OK - HiTech (Sector 1)")
        elif d["Branch"] == "40557468-2d57-4a3d-9a5e-3eede177daf5":  # Old Plant
            device_config[device_name]["sector"] = 2
            print(f"  OK - Old Plant (Sector 2)")
        else:
            print(f"  OK - Unknown branch: {d['Branch']}")
    else:
        print(f"  FAILED - Status {r.status_code}")

if len(tuggers) < 2:
    print(f"\nOnly {len(tuggers)} tuggers authenticated. Need at least 2. Exiting.")
    exit(1)

print(f"\n{len(tuggers)} tuggers ready!")
print("\nDevice configuration:")
for device, config in device_config.items():
    if device in tuggers:
        print(f"  {device}: Sector {config['sector']} ({config['plant']})")

print("\nStarting circular motion...\n")
print("Press Ctrl+C to stop\n")

t = 0
try:
    while True:
        t += 1

        for i, (name, creds) in enumerate(tuggers.items()):
            config = device_config[name]
            sector_id = config["sector"]

            if sector_id is None:
                continue  # Skip if sector not determined

            # Different centers for different sectors
            if sector_id == 1:  # HiTech - 265m x 265m
                center_x = 132000  # 132m
                center_y = 132000
                radius = 50000     # 50m
            else:  # Old Plant - 250m x 250m
                center_x = 125000  # 125m
                center_y = 125000
                radius = 40000     # 40m

            # Different phase for each tugger
            phase = i * (2 * math.pi / 4)  # 4 tuggers
            angle = (t * 0.05) + phase

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Post to appropriate sector
            headers = {
                "Content-Type": "application/json",
                "Client": creds["client"],
                "Branch": creds["branch"],
                "Token": creds["token"],
                "Api-Key": TWINZO_API_KEY
            }

            payload = [{
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
            }]

            try:
                r = requests.post(LOC_URL, headers=headers, json=payload, timeout=10)
                if t % 10 == 0:  # Log every 10th iteration
                    plant_name = config["plant"]
                    status = "OK" if r.status_code == 200 else f"FAIL {r.status_code}"
                    print(f"{name} -> Sector {sector_id} ({plant_name}): ({x/1000:.1f}m, {y/1000:.1f}m) - {status}")
            except Exception as e:
                if t % 10 == 0:
                    print(f"{name} -> ERROR: {str(e)[:50]}")

        time.sleep(1.0)  # 1Hz update rate

except KeyboardInterrupt:
    print("\n\nStopped.")
    print("\nCheck both plants:")
    print("  - HiTech should show tugger-03 and tugger-04")
    print("  - Old Plant should show tugger-01 and tugger-02")
