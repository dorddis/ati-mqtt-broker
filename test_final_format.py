#!/usr/bin/env python3
"""
Test the final corrected payload format
"""
import requests
import json
import time

def test_corrected_format():
    """Test with the corrected payload format"""
    
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
    
    print("🔐 Authenticating tugger-01...")
    auth_response = requests.post(auth_url, headers=auth_headers, json=oauth_payload, timeout=10)
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        return
    
    auth_data = auth_response.json()
    print(f"✅ Auth successful!")
    
    # Test localization with corrected format
    localization_url = "https://api.platform.twinzo.com/v3/localization"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Client": auth_data["Client"],
        "Branch": auth_data["Branch"],
        "Token": auth_data["Token"],
        "Api-Key": "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
    }
    
    # CORRECTED PAYLOAD: Direct array format
    localization_payload = [
        {
            "Timestamp": int(time.time() * 1000),  # Milliseconds
            "SectorId": 1,  # Integer sector ID
            "X": 200000.0,  # Within coordinate bounds
            "Y": 200000.0,
            "Z": 0.0,
            "Interval": 100,  # 100ms = 10Hz
            "Battery": 79,  # tugger-01 battery
            "IsMoving": True,
            "LocalizationAreas": [],  # Empty for now
            "NoGoAreas": []  # Empty for now
        }
    ]
    
    print(f"📍 Testing corrected localization format...")
    print(f"Payload: {json.dumps(localization_payload, indent=2)}")
    
    try:
        response = requests.post(localization_url, headers=headers, json=localization_payload, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("🎉 SUCCESS! Corrected format works!")
            return True
        else:
            print("❌ Still failing, need further investigation")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING FINAL CORRECTED FORMAT")
    print("=" * 50)
    test_corrected_format()