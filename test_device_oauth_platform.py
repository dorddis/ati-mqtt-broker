import requests
import json

# Test device OAuth authentication - Platform API
# Using Platform API endpoint
auth_url = "https://api.platform.twinzo.com/v3/authorization/authenticate"

# Device OAuth credentials
oauth_payload = {
    "client": "TVSMotor",
    "login": "tugger-01", 
    "password": "Tvs@Hosur$2025"
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print("Testing Twinzo Device OAuth Authentication (Platform API)...")
print(f"URL: {auth_url}")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Payload: {json.dumps(oauth_payload, indent=2)}")
print()

try:
    response = requests.post(auth_url, headers=headers, json=oauth_payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        try:
            auth_data = response.json()
            print("\n✅ SUCCESS! OAuth authentication worked")
            
            # Extract token and other info if available
            if 'token' in auth_data:
                print(f"🔑 Access Token: {auth_data['token']}")
            if 'expires' in auth_data:
                print(f"⏰ Expires: {auth_data['expires']}")
            if 'clientGuid' in auth_data:
                print(f"🆔 Client GUID: {auth_data['clientGuid']}")
            if 'branchGuid' in auth_data:
                print(f"🏢 Branch GUID: {auth_data['branchGuid']}")
                
        except json.JSONDecodeError:
            print("✅ SUCCESS! But response is not JSON")
            
    elif response.status_code == 401:
        print("❌ 401 Unauthorized - Check login credentials")
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Check client permissions")
    elif response.status_code == 404:
        print("❌ 404 Not Found - Check endpoint URL")
    elif response.status_code == 400:
        print("❌ 400 Bad Request - Check payload format")
    else:
        print(f"⚠️ Unexpected status: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50)
print("If successful, use the returned token in your API calls!")