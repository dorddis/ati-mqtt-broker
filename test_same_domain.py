import requests
import json
import time

def test_same_domain_approach():
    """Test using the same domain for auth and data posting"""
    
    # Authenticate on platform domain
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
    
    print("🔐 Authenticating on platform domain...")
    auth_response = requests.post(auth_url, headers=auth_headers, json=oauth_payload, timeout=10)
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        return
    
    auth_data = auth_response.json()
    print(f"✅ Auth successful!")
    
    # Try localization on SAME domain (platform)
    localization_urls = [
        "https://api.platform.twinzo.com/v3/localization",
        "https://api.twinzo.eu/v3/localization",
        "https://api.twinzo.com/v3/localization"
    ]
    
    # Test payload
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
    
    for url in localization_urls:
        print(f"\n{'='*50}")
        print(f"Testing: {url}")
        print(f"{'='*50}")
        
        # Try different header combinations
        header_sets = [
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Client": auth_data['Client'],
                "Branch": auth_data['Branch'],
                "Token": auth_data['Token'],
                "Api-Key": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
            },
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Client": auth_data['Client'],
                "Branch": auth_data['Branch'],
                "Token": auth_data['Token']
            },
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {auth_data['Token']}",
                "Client": auth_data['Client'],
                "Branch": auth_data['Branch'],
                "Api-Key": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
            }
        ]
        
        for i, headers in enumerate(header_sets, 1):
            print(f"\n--- Header set {i} ---")
            
            try:
                response = requests.post(url, headers=headers, json=localization_payload, timeout=10)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
                if response.status_code in [200, 201]:
                    print(f"🎉 SUCCESS! Working combination found!")
                    print(f"URL: {url}")
                    print(f"Headers: {json.dumps(headers, indent=2)}")
                    return
                elif response.status_code == 404:
                    print("❌ 404 - Endpoint not found")
                    break  # No point trying other headers for this URL
                elif response.status_code == 401:
                    print("❌ 401 - Unauthorized")
                else:
                    print(f"⚠️ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print(f"\n❌ No working combination found across all domains")

if __name__ == "__main__":
    print("🔍 TESTING SAME DOMAIN APPROACH")
    print("=" * 60)
    test_same_domain_approach()