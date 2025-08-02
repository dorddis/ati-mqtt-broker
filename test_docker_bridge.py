#!/usr/bin/env python3
"""
Test script to verify the Docker bridge configuration works
"""
import sys
import os
sys.path.append('./bridge')

# Import the bridge module to test the OAuth functionality
import json
import time
import requests

# Test the OAuth authentication directly
def test_oauth_auth():
    """Test OAuth authentication with the same config as Docker bridge"""
    
    TWINZO_CLIENT = "TVSMotor"
    TWINZO_PASSWORD = "Tvs@Hosur$2025"
    TWINZO_API_KEY = "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S"
    TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
    TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"
    
    print("🧪 Testing Docker Bridge OAuth Configuration")
    print("=" * 50)
    
    # Test authentication for all tugger devices
    devices = ["tugger-01", "tugger-02", "tugger-03"]
    
    for device in devices:
        print(f"\n🔐 Testing OAuth for {device}...")
        
        auth_payload = {
            "client": TWINZO_CLIENT,
            "login": device,
            "password": TWINZO_PASSWORD
        }
        
        auth_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            # Authenticate
            response = requests.post(TWINZO_AUTH_URL, headers=auth_headers, json=auth_payload, timeout=10)
            
            if response.status_code == 200:
                auth_data = response.json()
                print(f"✅ OAuth successful for {device}")
                
                # Test localization post
                credentials = {
                    "token": auth_data["Token"],
                    "client": auth_data["Client"],
                    "branch": auth_data["Branch"]
                }
                
                # Create test localization payload
                twinzo_payload = [
                    {
                        "Timestamp": int(time.time()),
                        "SectorId": 1,
                        "X": 15.0 + (hash(device) % 10),
                        "Y": 25.0 + (hash(device) % 10),
                        "Z": 0.0,
                        "Interval": 5000,
                        "Battery": 85,
                        "IsMoving": True,
                        "LocalizationAreas": [1, 2],
                        "NoGoAreas": [3]
                    }
                ]
                
                # Create headers
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Client": credentials["client"],
                    "Branch": credentials["branch"],
                    "Token": credentials["token"],
                    "Api-Key": TWINZO_API_KEY
                }
                
                # Test localization post
                loc_response = requests.post(TWINZO_LOCALIZATION_URL, headers=headers, json=twinzo_payload, timeout=5)
                
                if loc_response.status_code in [200, 201]:
                    print(f"✅ Localization post successful for {device}")
                    print(f"   Response: {loc_response.text}")
                else:
                    print(f"❌ Localization post failed for {device}: {loc_response.status_code}")
                    print(f"   Response: {loc_response.text}")
                    
            else:
                print(f"❌ OAuth failed for {device}: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {device}: {e}")
    
    print(f"\n🏁 Docker bridge configuration test completed!")
    print(f"If all tests passed, your Docker setup should work correctly.")

if __name__ == "__main__":
    test_oauth_auth()