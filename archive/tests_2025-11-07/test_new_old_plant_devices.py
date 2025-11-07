#!/usr/bin/env python3
"""
Test new Old Plant devices: tugger-05-old and tugger-06-old
"""
import os, requests, time, math

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
LOC_URL = "https://api.platform.twinzo.com/v3/localization"

print("="*70)
print("TESTING NEW OLD PLANT DEVICES")
print("="*70)
print("\nDevices: tugger-05-old, tugger-06-old")
print("\nOpen Old Plant UI:")
print("https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5")
print("="*70)

# Test the new devices
test_devices = ["tugger-05-old", "tugger-06-old"]

tuggers = {}
for device_name in test_devices:
    print(f"\nAuthenticating {device_name}...")
    r = requests.post(AUTH_URL, json={"client": TWINZO_CLIENT, "login": device_name, "password": TWINZO_PASSWORD}, timeout=10)

    if r.status_code == 200:
        d = r.json()
        tuggers[device_name] = {
            "token": d["Token"],
            "client": d["Client"],
            "branch": d["Branch"]
        }
        print(f"  ✓ Authenticated successfully")
        print(f"    Client: {d['Client']}")
        print(f"    Branch: {d['Branch']}")
        print(f"    Token: {d['Token'][:50]}...")

        # Check which branch
        if d["Branch"] == "40557468-2d57-4a3d-9a5e-3eede177daf5":
            print(f"    → Confirmed in OLD PLANT branch!")
        elif d["Branch"] == "dcac4881-05ab-4f29-b0df-79c40df9c9c2":
            print(f"    → WARNING: In HiTech branch, not Old Plant!")
        else:
            print(f"    → Unknown branch")
    else:
        print(f"  ✗ Authentication FAILED - Status {r.status_code}")
        print(f"    Response: {r.text}")

if len(tuggers) == 0:
    print("\n❌ No devices authenticated successfully. Exiting.")
    exit(1)

print(f"\n✓ {len(tuggers)} device(s) authenticated!")
print("\nStarting circular motion on Old Plant...\n")
print("Press Ctrl+C to stop\n")

t = 0
try:
    while True:
        t += 1

        for i, (name, creds) in enumerate(tuggers.items()):
            # Old Plant sector is 250m x 250m, center at 125m
            center_x = 125000  # 125m in mm
            center_y = 125000  # 125m in mm
            radius = 40000     # 40m radius

            # Different phase for each tugger
            phase = i * math.pi  # 180 degrees apart
            angle = (t * 0.05) + phase

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Post to Sector 2 (Old Plant)
            headers = {
                "Content-Type": "application/json",
                "Client": creds["client"],
                "Branch": creds["branch"],
                "Token": creds["token"],
                "Api-Key": TWINZO_API_KEY
            }

            payload = [{
                "Timestamp": int(time.time() * 1000),
                "SectorId": 2,  # Old Plant sector
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
                if t % 5 == 0:  # Log every 5th iteration
                    if r.status_code == 200:
                        print(f"✓ {name} -> Old Plant Sector 2: ({x/1000:.1f}m, {y/1000:.1f}m) - Status {r.status_code}")
                    else:
                        print(f"✗ {name} -> FAILED {r.status_code}: {r.text[:100]}")
            except Exception as e:
                if t % 5 == 0:
                    print(f"✗ {name} -> ERROR: {str(e)[:70]}")

        time.sleep(1.0)  # 1Hz update rate

except KeyboardInterrupt:
    print("\n\n" + "="*70)
    print("STOPPED")
    print("="*70)
    print("\nCheck Old Plant UI - you should see the tuggers moving in circles!")
    print("https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5")
