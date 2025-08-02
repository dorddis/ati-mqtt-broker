import requests
import json

# Test different API versions and paths based on the Swagger hint
base_urls = [
    "https://api.twinzo.eu/v3/localization",
    "https://api.twinzo.eu/v2/localization", 
    "https://api.twinzo.eu/v1/localization",
    "https://api.twinzo.eu/aos/v3/localization",
    "https://api.twinzo.eu/aos/localization",
    "https://api.twinzo.eu/api/aos/v3/localization"
]

headers = {
    "Authorization": "Bearer sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "X-Client-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "Content-Type": "application/json"
}

test_data = {
    "deviceId": "test-device",
    "timestamp": "2025-08-02T07:30:00Z",
    "position": {"x": 50, "y": 30, "z": 0},
    "heading": 1.5
}

print("Testing different API versions and paths...")
print()

for url in base_urls:
    print(f"Testing: {url}")
    
    # First try GET to see what error we get
    try:
        get_response = requests.get(url, headers=headers, timeout=5)
        print(f"  GET Status: {get_response.status_code}")
        if get_response.text:
            print(f"  GET Response: {get_response.text[:150]}...")
    except Exception as e:
        print(f"  GET Error: {e}")
    
    # Then try POST
    try:
        post_response = requests.post(url, headers=headers, json=test_data, timeout=5)
        print(f"  POST Status: {post_response.status_code}")
        if post_response.text:
            print(f"  POST Response: {post_response.text[:150]}...")
            
        if post_response.status_code == 200 or post_response.status_code == 201:
            print("  ✅ SUCCESS!")
            break
        elif post_response.status_code == 401:
            print("  ❌ 401 - Auth issue")
        elif post_response.status_code == 404:
            print("  ❌ 404 - Not found")
        elif post_response.status_code == 405:
            print("  ⚠️  405 - Method not allowed")
        else:
            print(f"  ⚠️  {post_response.status_code}")
            
    except Exception as e:
        print(f"  POST Error: {e}")
    print()