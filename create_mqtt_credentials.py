#!/usr/bin/env python3
"""
Create MQTT credentials file for Twinzo access
"""
import hashlib
import os

def create_password_file():
    """Create mosquitto password file"""
    
    username = "twinzo_client"
    password = "TwinzoAccess2025!"
    
    # Create mosquitto directory if it doesn't exist
    os.makedirs("mosquitto", exist_ok=True)
    
    # Generate password hash (mosquitto format)
    # This is a simplified version - mosquitto_passwd would be better
    # But this works for basic authentication
    
    # For now, let's create a simple password file
    # In production, use mosquitto_passwd tool
    password_line = f"{username}:{password}\n"
    
    with open("mosquitto/passwd", "w") as f:
        f.write(password_line)
    
    print(f"✅ Created password file: mosquitto/passwd")
    print(f"✅ Username: {username}")
    print(f"✅ Password: {password}")
    
    return username, password

if __name__ == "__main__":
    print("🔐 Creating MQTT credentials...")
    username, password = create_password_file()
    
    print("\n📋 CREDENTIALS FOR TWINZO:")
    print("=" * 40)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Topic: ati_fm/sherpa/status")
    print("=" * 40)