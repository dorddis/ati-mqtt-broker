#!/usr/bin/env python3
"""
COMPREHENSIVE DIAGNOSTIC - NO ASSUMPTIONS
Just fetch everything from Twinzo API and log it all
"""
import os, requests, json, time
from datetime import datetime

TWINZO_CLIENT = "TVSMotor"
TWINZO_PASSWORD = "Tvs@Hosur$2025"
TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
BASE_URL = "https://api.platform.twinzo.com/v3"

LOG_FILE = "twinzo_diagnostic_log.txt"

def log(msg):
    """Log to both console and file"""
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def api_call(url, method="GET", headers=None, data=None, description=""):
    """Make API call and log everything"""
    log(f"\n{'='*100}")
    log(f"API CALL: {description}")
    log(f"{'='*100}")
    log(f"Method: {method}")
    log(f"URL: {url}")
    log(f"Headers: {json.dumps(headers, indent=2)}")
    if data:
        log(f"Request Body: {json.dumps(data, indent=2)}")

    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=15)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=15)

        log(f"\nResponse Status: {r.status_code}")
        log(f"Response Headers: {json.dumps(dict(r.headers), indent=2)}")

        try:
            response_json = r.json()
            log(f"Response Body (JSON):")
            log(json.dumps(response_json, indent=2))
            return response_json
        except:
            log(f"Response Body (Raw Text): {r.text}")
            return r.text

    except Exception as e:
        log(f"\nEXCEPTION: {type(e).__name__}: {str(e)}")
        return None

# Clear log file
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"TWINZO COMPREHENSIVE DIAGNOSTIC\n")
    f.write(f"Started: {datetime.now().isoformat()}\n")
    f.write(f"="*100 + "\n\n")

log("STARTING COMPREHENSIVE DIAGNOSTIC")
log(f"Log file: {LOG_FILE}")

# Test devices to authenticate
test_devices = ["tugger-01", "tugger-02", "tugger-03"]

# Store all auth credentials
auth_creds = {}

log("\n" + "="*100)
log("PART 1: AUTHENTICATE ALL TEST DEVICES")
log("="*100)

for device in test_devices:
    result = api_call(
        AUTH_URL,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        data={
            "client": TWINZO_CLIENT,
            "login": device,
            "password": TWINZO_PASSWORD
        },
        description=f"Authenticate {device}"
    )

    if result and isinstance(result, dict) and "Token" in result:
        auth_creds[device] = {
            "token": result["Token"],
            "client": result["Client"],
            "branch": result["Branch"]
        }
        log(f"\n✓ {device} authenticated successfully")
        log(f"  Client: {result['Client']}")
        log(f"  Branch: {result['Branch']}")
        log(f"  Token: {result['Token'][:50]}...")
    else:
        log(f"\n✗ {device} authentication FAILED")

# Use tugger-01 for all subsequent calls
if "tugger-01" not in auth_creds:
    log("\nFATAL: Could not authenticate tugger-01. Exiting.")
    exit(1)

creds = auth_creds["tugger-01"]
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Client": creds["client"],
    "Branch": creds["branch"],
    "Token": creds["token"],
    "Api-Key": TWINZO_API_KEY
}

log("\n" + "="*100)
log("PART 2: FETCH ALL BRANCHES")
log("="*100)

branches = api_call(
    f"{BASE_URL}/branches",
    headers=headers,
    description="Get all branches"
)

log("\n" + "="*100)
log("PART 3: FETCH ALL SECTORS")
log("="*100)

sectors = api_call(
    f"{BASE_URL}/sectors",
    headers=headers,
    description="Get all sectors"
)

log("\n" + "="*100)
log("PART 4: FETCH ALL DEVICES")
log("="*100)

devices = api_call(
    f"{BASE_URL}/devices",
    headers=headers,
    description="Get all devices"
)

log("\n" + "="*100)
log("PART 5: TRY FETCHING BRANCH-SPECIFIC DATA")
log("="*100)

# Try to get sectors for each branch
if branches and isinstance(branches, list):
    for branch in branches:
        branch_id = branch.get("Id")
        branch_guid = branch.get("Guid")
        branch_title = branch.get("Title")

        log(f"\n--- Trying to access Branch {branch_id}: {branch_title} ---")

        # Try various endpoints
        api_call(
            f"{BASE_URL}/branches/{branch_id}",
            headers=headers,
            description=f"Get Branch {branch_id} by ID"
        )

        api_call(
            f"{BASE_URL}/branches/{branch_guid}",
            headers=headers,
            description=f"Get Branch {branch_id} by GUID"
        )

        api_call(
            f"{BASE_URL}/sectors?branchId={branch_id}",
            headers=headers,
            description=f"Get sectors for Branch {branch_id}"
        )

log("\n" + "="*100)
log("PART 6: TEST POSTING LOCALIZATION DATA")
log("="*100)

# Test posting to different sector IDs
test_coords = [
    (1, 100000, 100000),  # Sector 1 at 100m, 100m
    (2, 100000, 100000),  # Sector 2 at 100m, 100m
    (2, 0, 0),            # Sector 2 at origin
    (2, 125000, 125000),  # Sector 2 at center
]

for sector_id, x, y in test_coords:
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

    api_call(
        f"{BASE_URL}/localization",
        method="POST",
        headers=headers,
        data=payload,
        description=f"Post to Sector {sector_id} at ({x/1000:.0f}m, {y/1000:.0f}m)"
    )

    time.sleep(1)

log("\n" + "="*100)
log("PART 7: TRY ALTERNATE AUTHENTICATION")
log("="*100)

# Try authenticating with branch 2 GUID explicitly
log("\n--- Attempting to authenticate directly to Branch 2 ---")

# We can't change the branch in auth, but let's try setting it in headers
alt_headers = headers.copy()
alt_headers["Branch"] = "40557468-2d57-4a3d-9a5e-3eede177daf5"  # Old Plant GUID

log(f"\nUsing alternate headers with Branch 2 GUID:")
log(json.dumps(alt_headers, indent=2))

sectors_branch2 = api_call(
    f"{BASE_URL}/sectors",
    headers=alt_headers,
    description="Get sectors with Branch 2 in headers"
)

devices_branch2 = api_call(
    f"{BASE_URL}/devices",
    headers=alt_headers,
    description="Get devices with Branch 2 in headers"
)

# Try posting with branch 2 headers
payload = [{
    "Timestamp": int(time.time() * 1000),
    "SectorId": 2,
    "X": 100000,
    "Y": 100000,
    "Z": 0,
    "Interval": 100,
    "Battery": 85,
    "IsMoving": True,
    "LocalizationAreas": [],
    "NoGoAreas": []
}]

api_call(
    f"{BASE_URL}/localization",
    method="POST",
    headers=alt_headers,
    data=payload,
    description="Post to Sector 2 with Branch 2 headers"
)

log("\n" + "="*100)
log("PART 8: EXPLORE OTHER ENDPOINTS")
log("="*100)

# Try other potential endpoints
other_endpoints = [
    "/plants",
    "/facilities",
    "/sites",
    "/locations",
    "/assets",
    "/robots",
    "/amrs",
    "/vehicles",
    "/users",
    "/clients",
    f"/sectors/2",
    f"/sectors/8010257b-d416-43e2-b1a3-cc98604bb117",  # HiTech sector GUID
    f"/sectors/07dd750f-6ad8-4122-9030-35bbc696a38b",  # Old Plant sector GUID
]

for endpoint in other_endpoints:
    api_call(
        f"{BASE_URL}{endpoint}",
        headers=headers,
        description=f"Try endpoint: {endpoint}"
    )

log("\n" + "="*100)
log("DIAGNOSTIC COMPLETE")
log("="*100)
log(f"\nAll data logged to: {LOG_FILE}")
log(f"Finished: {datetime.now().isoformat()}")
log(f"\nPlease review {LOG_FILE} for full details.")
