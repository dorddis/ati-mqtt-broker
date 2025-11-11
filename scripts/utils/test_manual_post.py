"""
Manually test posting a single coordinate to Twinzo API to verify it's working.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TWINZO_CLIENT = os.getenv('TWINZO_CLIENT')
TWINZO_PASSWORD = os.getenv('TWINZO_PASSWORD')
TWINZO_API_KEY = os.getenv('TWINZO_API_KEY')

AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
LOC_URL = "https://api.platform.twinzo.com/v3/localization"

OLD_PLANT_BRANCH = "40557468-2d57-4a3d-9a5e-3eede177daf5"
OLD_PLANT_SECTOR = 2

def authenticate(device_login):
    """Authenticate device with Twinzo."""
    payload = {
        "Client": TWINZO_CLIENT,
        "Login": device_login,
        "Password": TWINZO_PASSWORD
    }

    print(f"Authenticating {device_login}...")
    response = requests.post(AUTH_URL, json=payload, timeout=10)

    if response.status_code == 200:
        data = response.json()
        print(f"  OK: Token obtained")
        return data['Token'], data['Branch']
    else:
        print(f"  FAIL: {response.status_code} - {response.text}")
        return None, None

def post_location(device_login, token, branch, x, y, battery=85):
    """Post a single location to Twinzo."""
    headers = {
        'Content-Type': 'application/json',
        'Client': TWINZO_CLIENT,
        'Branch': branch,
        'Token': token,
        'Api-Key': TWINZO_API_KEY
    }

    payload = [{
        "deviceLogin": device_login,
        "sectorId": OLD_PLANT_SECTOR,
        "x": x,
        "y": y,
        "battery": battery
    }]

    print(f"\nPosting location for {device_login}:")
    print(f"  Sector: {OLD_PLANT_SECTOR}")
    print(f"  X: {x:.2f}, Y: {y:.2f}")
    print(f"  Battery: {battery}%")

    response = requests.post(LOC_URL, json=payload, headers=headers, timeout=10)

    print(f"  Response: {response.status_code}")
    if response.status_code in [200, 204]:
        print(f"  OK: Location posted successfully")
        return True
    else:
        print(f"  FAIL: {response.text[:200]}")
        return False

def main():
    print("=" * 80)
    print("MANUAL TWINZO API TEST")
    print("=" * 80)
    print()

    # Test with tug-55's current position
    device_login = "tug-55-hosur-09"
    x = 227374
    y = 105559
    battery = 85

    # Authenticate
    token, branch = authenticate(device_login)
    if not token:
        print("\nAuthentication failed. Cannot proceed.")
        return

    print(f"  Branch: {branch}")
    print()

    # Post location
    success = post_location(device_login, token, branch, x, y, battery)

    print()
    print("=" * 80)
    if success:
        print("SUCCESS: Manual API post completed")
        print()
        print("If you still don't see the tugger on Twinzo:")
        print("1. Check if you're viewing the correct plant (Old Plant / Sector 2)")
        print("2. Check if the map viewport includes X=227374, Y=105559")
        print("3. Try refreshing the Twinzo web interface")
        print("4. Check with Twinzo team if device needs activation")
    else:
        print("FAILED: API post returned an error")
        print("Check the error message above for details")
    print("=" * 80)

if __name__ == "__main__":
    main()
