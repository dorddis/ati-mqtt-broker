import requests
import json

# Test the Twinzo API directly - trying different endpoint patterns
urls_to_test = [
    "https://api.twinzo.eu/v3/localization",
    "https://api.twinzo.eu/v3/localizations", 
    "https://api.twinzo.eu/v3/rtls/localization",
    "https://api.twinzo.eu/v3/rtls/localizations",
    "https://api.twinzo.eu/v3/aos/localization",
    "https://api.twinzo.eu/v3/aos/localizations",
    "https://api.twinzo.eu/api/v3/localization",
    "https://api.twinzo.eu/api/v3/localizations"
]
headers = {
    "Authorization": "Bearer sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "X-Client-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "Content-Type": "application/json"
}

# Also test with additional headers that might be required
headers_with_branch = {
    "Authorization": "Bearer sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "X-Client-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "X-Branch-Guid": "a3960903-00c2-4f39-9727-c5fa745eabb7",  # Sometimes needed
    "Content-Type": "application/json"
}

test_data = {
    "deviceId": "test-device",
    "timestamp": "2025-08-02T07:30:00Z",
    "position": {"x": 50, "y": 30, "z": 0},
    "heading": 1.5
}

print("Testing multiple Twinzo API endpoints...")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Data: {json.dumps(test_data, indent=2)}")
print()

# First, let's try a simple GET to see if we can connect at all
print("=== Testing basic connectivity ===")
base_urls = [
    "https://api.twinzo.eu/v3/",
    "https://api.twinzo.eu/api/v3/",
    "https://api.twinzo.eu/"
]

for base_url in base_urls:
    print(f"Testing base URL: {base_url}")
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code != 404:
            print(f"  Response: {response.text[:200]}...")
    except Exception as e:
        print(f"  Error: {e}")
print()

print("=== Testing POST endpoints ===")

for url in urls_to_test:
    print(f"Testing: {url}")
    
    # Try with standard headers first
    for header_set, header_name in [(headers, "standard"), (headers_with_branch, "with branch GUID")]:
        print(f"  Using {header_name} headers...")
        try:
            response = requests.post(url, headers=header_set, json=test_data, timeout=10)
            print(f"    Status Code: {response.status_code}")
            print(f"    Response Headers: {dict(response.headers)}")
            print(f"    Response Body: {response.text}")
            
            if response.status_code == 401:
                print("    ❌ 401 Unauthorized - Check token/auth")
            elif response.status_code == 403:
                print("    ❌ 403 Forbidden - Check permissions/Branch GUID")
            elif response.status_code == 404:
                print("    ❌ 404 Not Found - Wrong endpoint")
            elif response.status_code == 200 or response.status_code == 201:
                print("    ✅ Success! This endpoint works")
                print(f"    Working URL: {url}")
                print(f"    Working headers: {header_name}")
                exit(0)
            else:
                print(f"    ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
        print()
    print()