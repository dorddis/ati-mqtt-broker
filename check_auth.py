import requests
import json

# Test different authentication approaches for the endpoint that returned 401
url = "https://api.twinzo.eu/v3/localization"

# Test data
test_data = {
    "deviceId": "test-device",
    "timestamp": "2025-08-02T07:30:00Z",
    "position": {"x": 50, "y": 30, "z": 0},
    "heading": 1.5
}

print("Testing different authentication methods for:", url)
print()

# Test 1: Current approach
headers1 = {
    "Authorization": "Bearer sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "X-Client-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "Content-Type": "application/json"
}

# Test 2: With Branch GUID
headers2 = {
    "Authorization": "Bearer sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "X-Client-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "X-Branch-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "Content-Type": "application/json"
}

# Test 3: Different token format (without Bearer)
headers3 = {
    "Authorization": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "X-Client-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "Content-Type": "application/json"
}

# Test 4: API Key in header instead
headers4 = {
    "X-API-Key": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "X-Client-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "Content-Type": "application/json"
}

# Test 5: Try GET request first to see if endpoint accepts it
print("=== Testing GET request (no auth needed?) ===")
try:
    response = requests.get(url, timeout=10)
    print(f"GET Status: {response.status_code}")
    print(f"GET Response: {response.text[:200]}")
except Exception as e:
    print(f"GET Error: {e}")
print()

test_cases = [
    (headers1, "Bearer token + Client GUID"),
    (headers2, "Bearer token + Client GUID + Branch GUID"),
    (headers3, "Token without Bearer + Client GUID"),
    (headers4, "API Key header + Client GUID")
]

for headers, description in test_cases:
    print(f"=== Testing: {description} ===")
    try:
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS! This authentication method works!")
            break
        elif response.status_code == 401:
            print("❌ Still 401 - Authentication failed")
        elif response.status_code == 403:
            print("❌ 403 - Forbidden (might need different permissions)")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    print()