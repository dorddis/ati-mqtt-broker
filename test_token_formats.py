import requests
import json

# Use the token from your successful OAuth response
TOKEN = "1JeIaYI/Y7fzeYXJh2gA8N8M4UQL8SC8Sjttz2HKihs="
CLIENT = "a3960903-00c2-4f39-9727-c5fa745eabb7"
BRANCH = "dcac4881-05ab-4f29-b0df-79c40df9c9c2"

def test_different_token_formats():
    """Test different ways to use the OAuth token"""
    
    url = "https://api.twinzo.eu/v3/localization"
    
    test_payload = {
        "deviceId": "tugger-01",
        "timestamp": "2025-08-02T10:15:00.000000+00:00",
        "position": {"x": 15.2, "y": 28.7, "z": 0.0},
        "heading": 2.1
    }
    
    # Different token format attempts
    token_formats = [
        f"Bearer {TOKEN}",
        TOKEN,
        f"Token {TOKEN}",
        f"OAuth {TOKEN}"
    ]
    
    for i, token_format in enumerate(token_formats, 1):
        print(f"\n{'='*40}")
        print(f"Test {i}: Token format = '{token_format[:30]}...'")
        print(f"{'='*40}")
        
        headers = {
            "Authorization": token_format,
            "Client": CLIENT,
            "Branch": BRANCH,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=test_payload, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print(f"✅ SUCCESS with token format: {token_format}")
                return
            elif response.status_code == 401:
                print("❌ 401 - Still unauthorized")
            else:
                print(f"⚠️ Other status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_without_auth_header():
    """Test if the token should be used differently"""
    
    url = "https://api.twinzo.eu/v3/localization"
    
    test_payload = {
        "deviceId": "tugger-01",
        "timestamp": "2025-08-02T10:15:00.000000+00:00",
        "position": {"x": 15.2, "y": 28.7, "z": 0.0},
        "heading": 2.1
    }
    
    # Maybe token goes in a different header?
    alternative_headers = [
        {
            "Token": TOKEN,
            "Client": CLIENT,
            "Branch": BRANCH,
            "Content-Type": "application/json"
        },
        {
            "X-Token": TOKEN,
            "Client": CLIENT,
            "Branch": BRANCH,
            "Content-Type": "application/json"
        },
        {
            "Access-Token": TOKEN,
            "Client": CLIENT,
            "Branch": BRANCH,
            "Content-Type": "application/json"
        }
    ]
    
    print(f"\n{'='*50}")
    print("TESTING ALTERNATIVE HEADER NAMES")
    print(f"{'='*50}")
    
    for i, headers in enumerate(alternative_headers, 1):
        print(f"\n--- Alternative {i} ---")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=test_payload, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print(f"✅ SUCCESS with alternative headers!")
                return
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 TESTING DIFFERENT TOKEN FORMATS")
    print("=" * 60)
    
    test_different_token_formats()
    test_without_auth_header()
    
    print(f"\n💡 If none work, the issue might be:")
    print("- Wrong API endpoint domain")
    print("- Token needs to be refreshed")
    print("- Different payload structure required")
    print("- API version mismatch")