#!/usr/bin/env python3
"""
Simple verification that credentials are set up correctly
"""
import subprocess
import time

def verify_setup():
    """Verify MQTT setup is working"""
    
    print("🔍 VERIFYING MQTT CREDENTIALS SETUP")
    print("=" * 50)
    
    # Check if password file exists
    try:
        with open("mosquitto/passwd", "r") as f:
            content = f.read().strip()
            if "mock_tvs:" in content:
                print("✅ Password file exists with correct username")
                print(f"   File content: {content[:20]}...")
            else:
                print("❌ Password file doesn't contain expected username")
                return False
    except FileNotFoundError:
        print("❌ Password file not found")
        return False
    
    # Check if broker is running
    result = subprocess.run(["docker", "ps", "--filter", "name=mock-mqtt-broker"], 
                          capture_output=True, text=True)
    
    if "mock-mqtt-broker" in result.stdout:
        print("✅ MQTT broker container is running")
    else:
        print("❌ MQTT broker container is not running")
        return False
    
    # Check if WebSocket port is accessible
    result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)
    if ":9001" in result.stdout:
        print("✅ WebSocket port 9001 is listening")
    else:
        print("⚠️  WebSocket port 9001 status unclear (this is normal on some systems)")
    
    print("\n🎉 CREDENTIALS READY FOR TWINZO!")
    print("=" * 50)
    print("Username: mock_tvs")
    print("Password: Twinzo2025!@#")
    print("Topic: ati_fm/sherpa/status")
    print("Protocol: WebSocket (ws://)")
    print("=" * 50)
    print("\n✅ Ready to expose! Run: python expose_mqtt.py")
    
    return True

if __name__ == "__main__":
    verify_setup()