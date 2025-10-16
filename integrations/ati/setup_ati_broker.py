#!/usr/bin/env python3
"""
Setup MQTT Broker for ATI Direct Integration
Creates ATI-friendly broker configuration
"""
import os
import json
from pathlib import Path

def create_ati_mosquitto_config():
    """Create mosquitto config optimized for ATI integration"""
    config = """# ATI Direct Integration MQTT Broker Configuration
# Optimized for receiving ATI AMR data

# Basic settings
port 1883
protocol mqtt

# WebSocket support for easier ATI integration
listener 9001
protocol websockets

# Logging for debugging ATI data
log_dest file /mosquitto/log/mosquitto.log
log_type all

# Data persistence
persistence true
persistence_location /mosquitto/data/
autosave_interval 60

# ATI-friendly settings
allow_anonymous true
max_connections -1
max_inflight_messages 100

# Message size limits (ATI may send large payloads)
message_size_limit 1048576

# Keep alive settings
keepalive_interval 60

# ACL file for future credential management
# acl_file /mosquitto/config/acl.conf

# Connection logging for ATI troubleshooting
connection_messages true
log_timestamp true

# Topic patterns ATI might use
# (No restrictions - accept all topics)
"""

    # Ensure mosquitto directory exists
    os.makedirs("mosquitto", exist_ok=True)

    # Write config
    with open("mosquitto/mosquitto_ati.conf", "w") as f:
        f.write(config)

    print("✅ Created mosquitto/mosquitto_ati.conf for ATI integration")

def create_ati_credentials():
    """Create simple credentials for ATI"""

    # Create password file for ATI
    ati_creds = {
        "ati_user": "ati_password_123",
        "admin": "admin_password_456"
    }

    # Mosquitto password file format
    with open("mosquitto/passwd_ati", "w") as f:
        for user, password in ati_creds.items():
            # Note: In production, use mosquitto_passwd tool to hash these
            f.write(f"{user}:{password}\n")

    print("✅ Created mosquitto/passwd_ati with ATI credentials")
    print("   ATI can use: username=ati_user, password=ati_password_123")

def create_ati_docker_compose():
    """Create docker-compose override for ATI broker"""

    compose_override = {
        "version": "3.8",
        "services": {
            "ati-mqtt-broker": {
                "image": "eclipse-mosquitto:latest",
                "container_name": "ati-mqtt-broker",
                "ports": [
                    "1883:1883",  # MQTT
                    "9001:9001"   # WebSockets
                ],
                "volumes": [
                    "./mosquitto/mosquitto_ati.conf:/mosquitto/config/mosquitto.conf",
                    "./mosquitto/data:/mosquitto/data",
                    "./mosquitto/log:/mosquitto/log",
                    "./mosquitto/passwd_ati:/mosquitto/config/passwd"
                ],
                "restart": "unless-stopped",
                "healthcheck": {
                    "test": ["CMD-SHELL", "mosquitto_pub -h localhost -t test -m 'health'"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            }
        }
    }

    with open("docker-compose.ati.yml", "w") as f:
        import yaml
        yaml.dump(compose_override, f, default_flow_style=False)

    print("✅ Created docker-compose.ati.yml for ATI broker")

def create_ati_monitor_script():
    """Create script to monitor ATI data in real-time"""

    monitor_script = '''#!/usr/bin/env python3
"""
ATI Data Monitor - Watch incoming ATI data in real-time
"""
import paho.mqtt.client as mqtt
import json
from datetime import datetime

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Connected to ATI broker at {datetime.now().strftime('%H:%M:%S')}")
        print("📡 Subscribing to all ATI topics...")
        client.subscribe("#", qos=1)  # Subscribe to everything
    else:
        print(f"❌ Connection failed: {rc}")

def on_message(client, userdata, msg):
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

    print(f"\\n🎉 ATI DATA RECEIVED at {timestamp}")
    print(f"   Topic: {msg.topic}")
    print(f"   Size: {len(msg.payload)} bytes")

    try:
        # Try to parse as JSON
        data = json.loads(msg.payload.decode('utf-8'))
        print("   JSON Data:")
        print(json.dumps(data, indent=4))

        # Analyze data structure
        if isinstance(data, dict):
            if "data" in data and "eid" in data.get("data", {}):
                eid = data["data"]["eid"]
                event_types = {
                    2001: "Heartbeat/Trip Start",
                    2002: "Trip Update",
                    2003: "Trip End/Error"
                }
                print(f"   📋 Event Type: {event_types.get(eid, f'Unknown ({eid})')}")

            if "pl" in data.get("data", {}):
                payload = data["data"]["pl"]
                if "battery" in payload:
                    print(f"   🔋 Battery: {payload['battery']}%")
                if "location" in payload:
                    loc = payload["location"]
                    print(f"   📍 Location: {loc.get('lat', '?')}, {loc.get('long', '?')}")

    except json.JSONDecodeError:
        # Not JSON, show raw
        payload_str = msg.payload.decode('utf-8', errors='ignore')
        print(f"   Raw Data: {payload_str[:200]}")
    except Exception as e:
        print(f"   Error parsing: {e}")

    print("-" * 60)

def main():
    print("="*80)
    print("🔍 ATI DATA MONITOR")
    print("="*80)
    print("Monitoring localhost:1883 for incoming ATI data...")
    print("Press Ctrl+C to stop")
    print("="*80)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ati-monitor")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect("localhost", 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\\n⚠️ Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
'''

    with open("ati_data_monitor.py", "w") as f:
        f.write(monitor_script)

    # Make executable
    os.chmod("ati_data_monitor.py", 0o755)

    print("✅ Created ati_data_monitor.py for watching ATI data")

def main():
    print("🚀 Setting up MQTT Broker for ATI Direct Integration")
    print("="*60)

    create_ati_mosquitto_config()
    create_ati_credentials()

    try:
        create_ati_docker_compose()
    except ImportError:
        print("⚠️ PyYAML not installed - skipping docker-compose.ati.yml")
        print("   Install with: pip install pyyaml")

    create_ati_monitor_script()

    print("\n" + "="*60)
    print("✅ ATI MQTT BROKER SETUP COMPLETE!")
    print("="*60)

    print("\n📋 NEXT STEPS:")
    print("1. Start the ATI broker:")
    print("   docker-compose -f docker-compose.ati.yml up -d")
    print()
    print("2. Expose it publicly for ATI:")
    print("   python expose_mqtt.py")
    print()
    print("3. Monitor ATI data:")
    print("   python ati_data_monitor.py")
    print()
    print("4. Give ATI the public URL from step 2")
    print()
    print("💡 ATI Credentials:")
    print("   Username: ati_user")
    print("   Password: ati_password_123")
    print("="*60)

if __name__ == "__main__":
    main()