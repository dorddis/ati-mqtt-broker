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
                'branch': auth_data['Branch']
            }
        else:
            print(f"❌ Authentication failed for {login}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error for {login}: {e}")
        return None

def post_localization_data(credentials, device_login):
    """Post localization data using working configuration"""
    # WORKING CONFIGURATION: Use platform domain
    url = "https://api.platform.twinzo.com/v3/localization"
    
    # WORKING HEADERS: Token, Client, Branch, Api-Key
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials['client'],
        "Branch": credentials['branch'],
        "Token": credentials['token'],
        "Api-Key": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
    }
    
    # WORKING PAYLOAD: Array format
    localization_payload = [
        {
            "Timestamp": int(time.time()),
            "SectorId": 1,
            "X": 15.2 + (hash(device_login) % 10),  # Vary position by device
            "Y": 28.7 + (hash(device_login) % 10),
            "Z": 0.0,
            "Interval": 5000,
            "Battery": 85,
            "IsMoving": True,
            "LocalizationAreas": [1, 2],
            "NoGoAreas": [3]
        }
    ]
    
    print(f"📍 Posting localization data for {device_login}...")
    print(f"Payload: {json.dumps(localization_payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=localization_payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
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
    # WORKING CONFIGURATION: Use platform domain
    url = "https://api.platform.twinzo.com/v3/localization/batch"
    
    # WORKING HEADERS
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials['client'],
        "Branch": credentials['branch'],
        "Token": credentials['token'],
        "Api-Key": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
    }
    
    # WORKING BATCH PAYLOAD: Array with Login and Locations
    batch_payload = [
        {
            "Login": "tugger-batch-test",
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
    ]
    
    print("📦 Posting batch localization data...")
    print(f"Payload: {json.dumps(batch_payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=batch_payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
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
    print("🎯 WORKING TWINZO LOCALIZATION TEST")
    print("=" * 60)
    print("✅ Using WORKING configuration:")
    print("   - Domain: api.platform.twinzo.com")
    print("   - Headers: Token, Client, Branch, Api-Key")
    print("   - Payload: Array format")
    print("=" * 60)
    
    # Test each device
    for device in devices:
        print(f"\n{'='*20} Testing {device} {'='*20}")
        
        # Authenticate
        credentials = authenticate_device(device)
        
        if credentials:
            # Post individual localization data
            success = post_localization_data(credentials, device)
            
            # For the first device, also test batch endpoint
            if device == "tugger-01" and success:
                print(f"\n--- Testing batch endpoint with {device} credentials ---")
                post_batch_data(credentials)
        
        print("-" * 60)
    
    print("\n🏁 All tests completed successfully!")