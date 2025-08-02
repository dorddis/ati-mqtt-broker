import requests
import json

def authenticate_and_debug():
    """Authenticate and test different endpoint combinations"""
    
    # Authenticate first
    auth_url = "https://api.platform.twinzo.com/v3/authorization/authenticate"
    oauth_payload = {
        "client": "TVSMotor",
        "login": "tugger-01", 
        "password": "Tvs@Hosur$2025"
    }
    
    auth_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🔐 Getting fresh authentication...")
    auth_response = requests.post(auth_url, headers=auth_headers, json=oauth_payload, timeout=10)
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        return
    
    auth_data = auth_response.json()
    print(f"✅ Auth successful!")
    print(f"Token: {auth_data['Token'][:20]}...")
    print(f"Client: {auth_data['Client']}")
    print(f"Branch: {auth_data['Branch']}")
    
    # Test different endpoint combinations
    endpoints_to_test = [
        "https://api.twinzo.eu/v3/localization",
        "https://api.platform.twinzo.com/v3/localization", 
        "https://api.twinzo.com/v3/localization"
    ]
    
    test_payload = {
        "deviceId": "tugger-01",
        "timestamp": "2025-08-02T10:15:00.000000+00:00",
        "position": {"x": 15.2, "y": 28.7, "z": 0.0},
        "heading": 2.1
    }
    
    for endpoint in endpoints_to_test:
        print(f"\n{'='*50}")
        print(f"Testing endpoint: {endpoint}")
        print(f"{'='*50}")
        
        # Try different header combinations
        header_combinations = [
            {
                "Authorization": f"Bearer {auth_data['Token']}",
                "Client": auth_data['Client'],
                "Branch": auth_data['Branch'],
                "Content-Type": "application/json"
            },
            {
                "Authorization": f"Bearer {auth_data['Token']}",
                "X-Client-Guid": auth_data['Client'],
                "X-Branch-Guid": auth_data['Branch'],
                "Content-Type": "application/json"
            },
            {
                "Client": auth_data['Client'],
                "Branch": auth_data['Branch'],
                "Content-Type": "application/json"
            }
        ]
        
        for i, headers in enumerate(header_combinations, 1):
            print(f"\n--- Header combination {i} ---")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            
            try:
                response = requests.post(endpoint, headers=headers, json=test_payload, timeout=10)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
                if response.status_code in [200, 201]:
                    print("🎉 SUCCESS! This combination works!")
                    return endpoint, headers
                    
            except Exception as e:
                print(f"Error: {e}")
    
    print("\n❌ No working combination found")
    return None, None

if __name__ == "__main__":
    print("🔍 DEBUGGING OAUTH + ENDPOINT COMBINATIONS")
    print("=" * 60)
    
    working_endpoint, working_headers = authenticate_and_debug()
    
    if working_endpoint:
        print(f"\n🎯 WORKING SOLUTION FOUND:")
        print(f"Endpoint: {working_endpoint}")
        print(f"Headers: {json.dumps(working_headers, indent=2)}")
    else:
        print(f"\n🤔 No working combination found. Possible issues:")
        print("- API endpoints might be different")
        print("- Token format might be wrong")
        print("- Additional headers might be required")
        print("- Different authentication flow needed")