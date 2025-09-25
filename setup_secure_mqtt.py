#!/usr/bin/env python3
"""
Setup secure MQTT authentication for Twinzo access
"""
import subprocess
import os
import time

def create_mqtt_credentials():
    """Create secure MQTT credentials for Twinzo"""
    
    # Strong credentials for Twinzo
    username = "mock_tvs"
    password = "Twinzo2025!@#"
    
    print("🔐 Setting up secure MQTT authentication...")
    
    # Ensure mosquitto directory exists
    os.makedirs("mosquitto", exist_ok=True)
    
    # Create password file using Docker mosquitto_passwd
    try:
        print("📝 Creating password file...")
        result = subprocess.run([
            "docker", "run", "--rm", "-v", f"{os.getcwd()}/mosquitto:/mosquitto/config",
            "eclipse-mosquitto:2", "mosquitto_passwd", "-c", "-b", 
            "/mosquitto/config/passwd", username, password
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created password file successfully")
            print(f"✅ Username: {username}")
            print(f"✅ Password: {password}")
            return username, password
        else:
            print(f"❌ Failed to create password file: {result.stderr}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error creating credentials: {e}")
        return None, None

def update_mosquitto_config():
    """Update Mosquitto configuration for secure access"""
    
    config_content = """# MQTT TCP listener (internal use - no auth)
listener 1883 0.0.0.0
allow_anonymous true

# WebSockets listener for external access (with auth)
listener 9001 0.0.0.0
protocol websockets
allow_anonymous false
password_file /mosquitto/config/passwd

persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
"""
    
    with open("mosquitto/mosquitto.conf", "w") as f:
        f.write(config_content)
    
    print("✅ Updated Mosquitto configuration for secure access")

def update_docker_compose():
    """Update docker-compose to mount password file"""
    
    print("📝 Updating docker-compose.yml...")
    
    # Read current docker-compose
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # Add password file volume if not already present
    if "passwd" not in content:
        content = content.replace(
            "- ./mosquitto/log:/mosquitto/log",
            "- ./mosquitto/log:/mosquitto/log\n      - ./mosquitto/passwd:/mosquitto/config/passwd"
        )
        
        with open("docker-compose.yml", "w") as f:
            f.write(content)
        
        print("✅ Updated docker-compose.yml with password file mount")
    else:
        print("✅ docker-compose.yml already configured")

def restart_broker():
    """Restart MQTT broker to apply changes"""
    
    print("🔄 Restarting MQTT broker...")
    
    try:
        # Stop and start broker to apply config changes
        subprocess.run(["docker-compose", "stop", "broker"], check=True)
        time.sleep(2)
        subprocess.run(["docker-compose", "start", "broker"], check=True)
        time.sleep(3)
        
        print("✅ MQTT broker restarted successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to restart broker: {e}")
        return False

def test_authentication(username, password):
    """Test MQTT authentication"""
    
    print("🧪 Testing MQTT authentication...")
    
    try:
        # Test authenticated connection
        result = subprocess.run([
            "docker", "run", "--rm", "--network", "twinzo-mock_default",
            "eclipse-mosquitto:2", "mosquitto_pub", 
            "-h", "broker", "-p", "9001", "-u", username, "-P", password,
            "-t", "test/auth", "-m", "Authentication test"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Authentication test successful!")
            return True
        else:
            print(f"❌ Authentication test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SECURE MQTT SETUP FOR TWINZO")
    print("=" * 50)
    
    # Step 1: Create credentials
    username, password = create_mqtt_credentials()
    
    if not username:
        print("❌ Failed to create credentials")
        exit(1)
    
    # Step 2: Update configuration
    update_mosquitto_config()
    update_docker_compose()
    
    # Step 3: Restart broker
    if not restart_broker():
        print("❌ Failed to restart broker")
        exit(1)
    
    # Step 4: Test authentication
    if test_authentication(username, password):
        print("\n" + "=" * 50)
        print("🎉 SECURE MQTT CREDENTIALS FOR TWINZO")
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Topic: ati_fm/sherpa/status")
        print(f"Protocol: WebSocket (ws://)")
        print("=" * 50)
        print("\n✅ Setup complete! Now run: python expose_mqtt.py")
    else:
        print("❌ Authentication test failed - please check configuration")