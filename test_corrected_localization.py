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

def post_localization_data_corrected(credentials, device_login):
    """Post localization data with corrected format"""
    url = "https://api.twinzo.eu/v3/localization"
    
    # Corrected headers based on curl example
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials['client'],
        "Branch": credentials['branch'],
        "Token": credentials['token'],
        "Api-Key": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
    }
    
    # Corrected payload - should be an array directly
    localization_payload = [
        {
            "Timestamp": int(time.time()),
            "SectorId": 1,
            "X": 15.2,
            "Y": 28.7,
            "Z": 0.0,
            "Interval": 5000,
            "Battery": 85,
            "IsMoving": True,
            "LocalizationAreas": [1, 2],
            "NoGoAreas": [3]
        }
    ]
    
    print(f"📍 Posting corrected localization data for {device_login}...")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(localization_payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=localization_payload, timeout=10)
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

def post_batch_data_corrected(credentials):
    """Post batch localization data with corrected format"""
    url = "https://api.twinzo.eu/v3/localization/batch"
    
    # Corrected headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": credentials['client'],
        "Branch": credentials['branch'],
        "Token": credentials['token'],
        "Api-Key": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
    }
    
    # Corrected batch payload - should be an array with Login and Locations
    batch_payload = [
        {
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
    ]
    
    print("📦 Posting corrected batch localization data...")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(batch_payload, indent=2)}")
    
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
    print("=" * 60)
    print("CORRECTED TWINZO LOCALIZATION TEST")
    print("=" * 60)
    
    # Test with tugger-01
    device = "tugger-01"
    print(f"\n{'='*20} Testing {device} {'='*20}")
    
    # Authenticate
    credentials = authenticate_device(device)
    
    if credentials:
        # Test individual localization
        success = post_localization_data_corrected(credentials, device)
        
        if success:
            print(f"\n--- Testing batch endpoint ---")
            post_batch_data_corrected(credentials)
        else:
            print(f"\n⚠️ Individual post failed, might need Api-Key headers")
    
    print("\n🏁 Test completed!")