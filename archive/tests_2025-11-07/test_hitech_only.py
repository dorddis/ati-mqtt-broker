#!/usr/bin/env python3
"""
Stream 3 tuggers to HiTech (Sector 1) ONLY - No dashboard changes needed!
"""
import os, requests, time, math

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
LOC_URL = "https://api.platform.twinzo.com/v3/localization"

print("="*70)
print("STREAMING 3 TUGGERS TO HITECH (SECTOR 1) ONLY")
print("="*70)
print("\nOpen HiTech UI:")
print("https://platform.twinzo.com/branch/dcac4881-05ab-4f29-b0df-79c40df9c9c2")
print("\nYou should see 3 tuggers moving in circles!")
print("="*70)

# Authenticate all 3 tuggers
tuggers = {}
for i in [1, 2, 3]:
    name = f"tugger-0{i}"
    print(f"\nAuthenticating {name}...")
    r = requests.post(AUTH_URL, json={"client": TWINZO_CLIENT, "login": name, "password": TWINZO_PASSWORD}, timeout=10)
    if r.status_code == 200:
        d = r.json()
        tuggers[name] = {"token": d["Token"], "client": d["Client"], "branch": d["Branch"]}
        print(f"  OK - Branch: {d['Branch']}")
    else:
        print(f"  FAILED")

if len(tuggers) != 3:
    print(f"\nOnly {len(tuggers)} tuggers authenticated. Exiting.")
    exit(1)

print(f"\n{len(tuggers)} tuggers ready. Starting circular motion on HiTech...\n")
print("Press Ctrl+C to stop\n")

t = 0
try:
    while True:
        t += 1

        for i, (name, creds) in enumerate(tuggers.items()):
            # Circular motion around center of HiTech sector
            # HiTech is 265m x 265m, so center is ~132m
            center_x = 132000  # 132m in mm
            center_y = 132000  # 132m in mm
            radius = 50000     # 50m radius

            # Different phase for each tugger
            phase = i * (2 * math.pi / 3)
            angle = (t * 0.05) + phase  # Slower rotation

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # POST TO SECTOR 1 ONLY (HiTech)
            headers = {
                "Content-Type": "application/json",
                "Client": creds["client"],
                "Branch": creds["branch"],
                "Token": creds["token"],
                "Api-Key": TWINZO_API_KEY
            }

            payload = [{
                "Timestamp": int(time.time() * 1000),
                "SectorId": 1,  # HITECH ONLY!
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
                    status = "OK" if r.status_code == 200 else f"FAIL {r.status_code}"
                    print(f"{name} -> Sector 1 (HiTech): ({x/1000:.1f}m, {y/1000:.1f}m) - {status}")
            except Exception as e:
                if t % 10 == 0:
                    print(f"{name} -> ERROR: {str(e)[:50]}")

        time.sleep(1.0)  # 1Hz update rate

except KeyboardInterrupt:
    print("\n\nStopped. All 3 tuggers should have been visible on HiTech map!")
