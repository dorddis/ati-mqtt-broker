import requests
import json
import time

def authenticate_device(login, password="Tvs@Hosur$2025", client="TVSMotor"):
    """Authenticate device and return credentials"""
    auth_url = "https://api.platform.twinzo.com/v3/authorization/authenticate"
    
    oauth_payload = {
        "client": client,
        "login": login, 
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"🔐 Authenticating {login}...")
    
    try:
        response = requests.post(auth_url, headers=headers, json=oauth_payload, timeout=10)
        
        if response.status_code == 200:
            auth_data = response.json()
            print(f"✅ Authentication successful for {login}")
            return {
                'token': auth_data['Token'],
                'client': auth_data['Client'],
                'branch': auth_data['Branch'],
                'expiration': auth_data['Expiration']
            }
        else:
            print(f"❌ Authentication failed for {login}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error for {login}: {e}")
        return None

def post_localization_data(credentials, device_login):
    """Post localization data using authenticated credentials"""
    # Using the EU endpoint for localization
    url = "https://api.twinzo.eu/v3/localization"
    
    headers = {
        "Authorization": f"Bearer {credentials['token']}",
        "Client": credentials['client'],
        "Branch": credentials['branch'],
        "Content-Type": "application/json"
    }
    
    # Sample localization data
    test_payload = {
        "deviceId": device_login,
        "timestamp": "2025-08-02T10:15:00.000000+00:00",
        "position": {"x": 15.2, "y": 28.7, "z": 0.0},
        "heading": 2.1
    }
    
    print(f"📍 Posting localization data for {device_login}...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=test_payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code in [200, 201]:
            print(f"✅ SUCCESS! Localization data posted for {device_login}")
            return True
        else:
            print(f"❌ Failed to post data for {device_login}")
            return False
            
    except Exception as e:
        print(f"❌ Error posting data for {device_login}: {e}")
        return False

def post_batch_data(credentials):
    """Post batch localization data"""
    url = "https://api.twinzo.eu/v3/localization/batch"
    
    headers = {
        "Authorization": f"Bearer {credentials['token']}",
        "Client": credentials['client'],
        "Branch": credentials['branch'],
        "Content-Type": "application/json"
    }
    
    # Batch payload with multiple devices
    batch_payload = {
        "Login": "tugger-batch",
        "Locations": [
            {
                "Timestamp": int(time.time()),
                "SectorId": 1,
                "X": 10.5,
                "Y": 22.4,
                "Z": 0.0,
                "Interval": 5000,
                "Battery": 85,
                "IsMoving": True,
                "LocalizationAreas": [1, 2],
                "NoGoAreas": [3]
            },
            {
                "Timestamp": int(time.time()) + 5,
                "SectorId": 1,
                "X": 11.2,
                "Y": 23.1,
                "Z": 0.0,
                "Interval": 5000,
                "Battery": 84,
                "IsMoving": True,
                "LocalizationAreas": [1, 2],
                "NoGoAreas": [3]
            }
        ]
    }
    
    print("📦 Posting batch localization data...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=batch_payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS! Batch data posted")
            return True
        else:
            print("❌ Failed to post batch data")
            return False
            
    except Exception as e:
        print(f"❌ Error posting batch data: {e}")
        return False

# Main execution
if __name__ == "__main__":
    devices = ["tugger-01", "tugger-02", "tugger-03"]
    
    print("=" * 60)
    print("TWINZO OAUTH + LOCALIZATION DATA TEST")
    print("=" * 60)
    
    # Test each device
    for device in devices:
        print(f"\n{'='*20} Testing {device} {'='*20}")
        
        # Authenticate
        credentials = authenticate_device(device)
        
        if credentials:
            # Post individual localization data
            post_localization_data(credentials, device)
            
            # For the first device, also test batch endpoint
            if device == "tugger-01":
                print(f"\n--- Testing batch endpoint with {device} credentials ---")
                post_batch_data(credentials)
        
        print("-" * 60)
    
    print("\n🏁 Test completed!")