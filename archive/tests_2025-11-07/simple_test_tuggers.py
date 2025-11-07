#!/usr/bin/env python3
"""
Simple test: 3 tuggers moving in circles on both plants
"""
import os, requests, time, math

TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
LOC_URL = "https://api.platform.twinzo.com/v3/localization"

# Authenticate
def auth(device):
    r = requests.post(AUTH_URL, json={"client": TWINZO_CLIENT, "login": device, "password": TWINZO_PASSWORD}, timeout=10)
    if r.status_code == 200:
        d = r.json()
        return {"token": d["Token"], "client": d["Client"], "branch": d["Branch"]}
    return None

# Post location
def post(creds, sector, x, y, device):
    headers = {
        "Content-Type": "application/json",
        "Client": creds["client"],
        "Branch": creds["branch"],
        "Token": creds["token"],
        "Api-Key": TWINZO_API_KEY
    }
    payload = [{
        "Timestamp": int(time.time() * 1000),
        "SectorId": sector,
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
        return r.status_code
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

print("Simple Tugger Movement Test")
print("="*60)

# Authenticate 3 tuggers
tuggers = {}
for i in [1, 2, 3]:
    name = f"tugger-0{i}"
    print(f"Authenticating {name}...")
    creds = auth(name)
    if creds:
        tuggers[name] = creds
        print(f"  OK")
    else:
        print(f"  FAILED")

if not tuggers:
    print("No tuggers authenticated!")
    exit(1)

print(f"\n{len(tuggers)} tuggers ready. Starting movement...\n")
print("Check Twinzo UI:")
print("  HiTech: https://platform.twinzo.com/branch/dcac4881-05ab-4f29-b0df-79c40df9c9c2")
print("  Old Plant: https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5")
print("\nPress Ctrl+C to stop\n")

# Move tuggers in circles
t = 0
try:
    while True:
        t += 1

        for i, (name, creds) in enumerate(tuggers.items()):
            # Simple circular motion - different circles for each tugger
            # Center at 100m, 100m with 40m radius
            center_x = 100000  # 100m in mm
            center_y = 100000  # 100m in mm
            radius = 40000     # 40m in mm

            # Different phase for each tugger
            phase = i * (2 * math.pi / 3)
            angle = (t * 0.1) + phase

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Post to BOTH sectors
            for sector in [1, 2]:
                status = post(creds, sector, x, y, name)
                if t % 10 == 0:  # Log every 10th iteration
                    sector_name = "HiTech" if sector == 1 else "Old Plant"
                    print(f"{name} -> Sector {sector} ({sector_name}): ({x:.0f}, {y:.0f}) - Status {status}")

        time.sleep(1.0)  # 1Hz update rate to avoid overloading API

except KeyboardInterrupt:
    print("\n\nStopped.")
