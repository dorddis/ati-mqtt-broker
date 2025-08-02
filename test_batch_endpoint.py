import requests
import json

# Test the /localization/batch endpoint
url = "https://api.twinzo.eu/v3/localization/batch"
headers = {
    "Authorization": "Bearer sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S",
    "Client": "a3960903-00c2-4f39-9727-c5fa745eabb7",
    "Branch": "dcac4881-05ab-4f29-b0df-79c40df9c9c2",
    "Content-Type": "application/json"
}

# Batch payload based on the provided structure
batch_payload = {
    "Login": "test-device",
    "Locations": [
        {
            "Timestamp": 1722594900,  # Unix timestamp
            "SectorId": 1,
            "X": 10.5,
            "Y": 22.4,
            "Z": 0.0,
            "Interval": 5000,  # 5 seconds
            "Battery": 85,
            "IsMoving": True,
            "LocalizationAreas": [1, 2],
            "NoGoAreas": [3]
        },
        {
            "Timestamp": 1722594905,
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

print("Testing Twinzo API /localization/batch endpoint...")
print(f"URL: {url}")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Payload: {json.dumps(batch_payload, indent=2)}")
print()

try:
    response = requests.post(url, headers=headers, json=batch_payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCCESS! Batch localization data submitted")
    elif response.status_code == 401:
        print("❌ 401 Unauthorized - Check token, client GUID, or branch GUID")
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Check permissions")
    elif response.status_code == 404:
        print("❌ 404 Not Found - Check endpoint URL")
    elif response.status_code == 400:
        print("❌ 400 Bad Request - Check payload structure")
    else:
        print(f"⚠️ Unexpected status: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")