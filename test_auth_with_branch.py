import requests
import json

# Test authentication with the branch GUID
url = "https://api.twinzo.eu/v3/localization"
headers = {
    "Authorization": "Bearer sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "Client": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "Branch": "dcac4881-05ab-4f29-b0df-79c40df9c9c2",
    "Content-Type": "application/json"
}

test_payload = {
    "deviceId": "test-device",
    "timestamp": "2025-08-02T09:35:00.000000+00:00",
    "position": {"x": 10.5, "y": 22.4, "z": 0.0},
    "heading": 1.57
}

print("Testing Twinzo API with branch GUID...")
print(f"URL: {url}")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print()

try:
    response = requests.post(url, headers=headers, json=test_payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCCESS! Authentication and API call worked")
    elif response.status_code == 401:
        print("❌ 401 Unauthorized - Check token, client GUID, or branch GUID")
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Check permissions")
    elif response.status_code == 404:
        print("❌ 404 Not Found - Check endpoint URL")
    else:
        print(f"⚠️ Unexpected status: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")