#!/usr/bin/env python3
"""
Setup Railway Deployment for ATI MQTT Broker
Creates Railway-optimized configuration for permanent hosting
"""
import os
import json
import yaml
from pathlib import Path

def create_railway_mosquitto_config():
    """Create Railway-optimized mosquitto configuration"""
    config = """# Railway MQTT Broker Configuration
# Optimized for cloud deployment with ATI integration

# Primary MQTT port
port 1883
protocol mqtt

# WebSocket support (Railway handles HTTPS automatically)
listener 9001
protocol websockets
socket_domain ipv4

# Railway-friendly logging
log_dest stdout
log_type error
log_type warning
log_type notice
log_type information
log_type debug
log_timestamp true

# Data persistence (Railway provides persistent volumes)
persistence true
persistence_location /mosquitto/data/
autosave_interval 300

# Connection settings optimized for cloud
allow_anonymous false
password_file /mosquitto/config/passwd

# Performance settings for Railway
max_connections 1000
max_inflight_messages 100
message_size_limit 2097152

# Keep alive settings
keepalive_interval 60

# Security settings
require_certificate false

# Topic access control
acl_file /mosquitto/config/acl.conf

# Connection logging for debugging
connection_messages true
log_timestamp true

# WebSocket settings for Railway
websockets_log_level 255
"""

    # Ensure directories exist
    os.makedirs("railway-deployment/mosquitto", exist_ok=True)

    # Write Railway-optimized config
    with open("railway-deployment/mosquitto/mosquitto.conf", "w") as f:
        f.write(config)

    print("✅ Created railway-deployment/mosquitto/mosquitto.conf")

def create_railway_credentials():
    """Create credentials for ATI and admin access"""

    # Password file (Railway format)
    passwd_content = """# ATI MQTT Broker Credentials
# Use mosquitto_passwd to generate these in production

# ATI user for publishing AMR data
ati_user:$7$101$abc123$hash_placeholder_for_ati_password

# Admin user for monitoring
admin:$7$101$def456$hash_placeholder_for_admin_password
"""

    # ACL file for topic permissions
    acl_content = """# ATI MQTT Broker Access Control
# Define who can publish/subscribe to what topics

# Admin can do everything
user admin
topic readwrite #

# ATI user can publish AMR data and read commands
user ati_user
topic write ati/+/status
topic write ati/+/position
topic write ati/+/battery
topic write ati/+/telemetry
topic write amr/+/status
topic write amr/+/position
topic read ati/commands/+
"""

    with open("railway-deployment/mosquitto/passwd", "w") as f:
        f.write("ati_user:ati_password_123\nadmin:admin_password_456\n")

    with open("railway-deployment/mosquitto/acl.conf", "w") as f:
        f.write(acl_content)

    print("✅ Created Railway credentials and ACL")
    print("   ATI user: ati_user / ati_password_123")
    print("   Admin user: admin / admin_password_456")

def create_railway_dockerfile():
    """Create optimized Dockerfile for Railway"""

    dockerfile_content = """# Railway MQTT Broker Dockerfile
# Optimized for ATI integration hosting

FROM eclipse-mosquitto:2.0.18

# Set Railway-friendly user
USER root

# Create necessary directories
RUN mkdir -p /mosquitto/data /mosquitto/log /mosquitto/config

# Copy configuration files
COPY mosquitto/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY mosquitto/passwd /mosquitto/config/passwd
COPY mosquitto/acl.conf /mosquitto/config/acl.conf

# Set proper permissions
RUN chown -R mosquitto:mosquitto /mosquitto/data /mosquitto/log /mosquitto/config
RUN chmod 600 /mosquitto/config/passwd /mosquitto/config/acl.conf

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD mosquitto_pub -h localhost -p 1883 -t health/check -m "ok" || exit 1

# Expose ports
EXPOSE 1883 9001

# Use mosquitto user
USER mosquitto

# Start mosquitto with custom config
CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
"""

    with open("railway-deployment/Dockerfile", "w") as f:
        f.write(dockerfile_content)

    print("✅ Created railway-deployment/Dockerfile")

def create_railway_compose():
    """Create docker-compose for Railway"""

    compose_config = {
        "version": "3.8",
        "services": {
            "ati-mqtt-broker": {
                "build": {
                    "context": ".",
                    "dockerfile": "Dockerfile"
                },
                "container_name": "ati-mqtt-railway",
                "ports": [
                    "${PORT:-1883}:1883",  # Railway assigns PORT
                    "9001:9001"
                ],
                "environment": [
                    "MQTT_USERNAME=${MQTT_USERNAME:-ati_user}",
                    "MQTT_PASSWORD=${MQTT_PASSWORD:-ati_password_123}"
                ],
                "volumes": [
                    "./data:/mosquitto/data"
                ],
                "restart": "unless-stopped",
                "healthcheck": {
                    "test": ["CMD-SHELL", "mosquitto_pub -h localhost -p 1883 -t health -m ok"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "10s"
                }
            }
        }
    }

    with open("railway-deployment/docker-compose.yml", "w") as f:
        yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)

    print("✅ Created railway-deployment/docker-compose.yml")

def create_railway_config():
    """Create railway.json configuration"""

    railway_config = {
        "build": {
            "builder": "dockerfile",
            "dockerfilePath": "Dockerfile"
        },
        "deploy": {
            "startCommand": "mosquitto -c /mosquitto/config/mosquitto.conf",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 10
        }
    }

    with open("railway-deployment/railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)

    print("✅ Created railway-deployment/railway.json")

def create_railway_env():
    """Create .env template for Railway"""

    env_content = """# Railway Environment Variables for ATI MQTT Broker
# Set these in Railway dashboard

# MQTT Credentials
MQTT_USERNAME=ati_user
MQTT_PASSWORD=ati_password_123

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin_password_456

# Port (Railway will set this automatically)
PORT=1883

# Optional: Custom domain
# RAILWAY_STATIC_URL=your-custom-domain.com
"""

    with open("railway-deployment/.env.example", "w") as f:
        f.write(env_content)

    print("✅ Created railway-deployment/.env.example")

def create_deployment_script():
    """Create Railway deployment script"""

    deploy_script = """#!/usr/bin/env python3
\"\"\"
Deploy ATI MQTT Broker to Railway
Automated deployment script
\"\"\"
import subprocess
import sys
import os

def run_command(cmd, description):
    \"\"\"Run command with error handling\"\"\"
    print(f"🚀 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def main():
    print("="*60)
    print("🚀 DEPLOYING ATI MQTT BROKER TO RAILWAY")
    print("="*60)

    # Check if Railway CLI is installed
    try:
        subprocess.run(["railway", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Railway CLI not found!")
        print("Install with: npm install -g @railway/cli")
        print("Or: brew install railway")
        sys.exit(1)

    # Check if logged in
    try:
        subprocess.run(["railway", "whoami"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ Not logged in to Railway")
        run_command("railway login", "Logging in to Railway")

    # Initialize project if needed
    if not os.path.exists(".railway"):
        run_command("railway init", "Initializing Railway project")

    # Deploy
    run_command("railway up", "Deploying to Railway")

    # Get the URL
    try:
        url = subprocess.run(["railway", "domain"], capture_output=True, text=True, check=True)
        print("\\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("="*60)
        print(f"🌐 Your ATI MQTT Broker URL: {url.stdout.strip()}")
        print()
        print("📋 For ATI Team:")
        print(f"   MQTT WebSocket: wss://{url.stdout.strip()}")
        print("   Username: ati_user")
        print("   Password: ati_password_123")
        print()
        print("📋 For Twinzo Integration:")
        print(f"   Subscribe to: wss://{url.stdout.strip()}")
        print("   Topics: ati/+/status, amr/+/position")
        print("="*60)
    except subprocess.CalledProcessError:
        print("⚠️ Could not get Railway URL automatically")
        print("Run 'railway domain' to get your deployment URL")

if __name__ == "__main__":
    main()
"""

    with open("deploy_to_railway.py", "w") as f:
        f.write(deploy_script)

    # Make executable
    os.chmod("deploy_to_railway.py", 0o755)

    print("✅ Created deploy_to_railway.py")

def create_monitoring_script():
    """Create script to monitor Railway-hosted broker"""

    monitor_script = """#!/usr/bin/env python3
\"\"\"
Monitor Railway MQTT Broker
Watch ATI data and system health in real-time
\"\"\"
import paho.mqtt.client as mqtt
import json
import ssl
import time
from datetime import datetime
import argparse

class RailwayMQTTMonitor:
    def __init__(self, broker_url, username, password):
        self.broker_url = broker_url
        self.username = username
        self.password = password
        self.message_count = 0
        self.connected = False

        # Extract host from URL
        self.host = broker_url.replace('wss://', '').replace('ws://', '')
        self.port = 443 if 'wss://' in broker_url else 80

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print(f"✅ Connected to Railway MQTT at {datetime.now().strftime('%H:%M:%S')}")
            print(f"🌐 Broker: {self.broker_url}")

            # Subscribe to all ATI topics
            topics = [
                ("ati/+/status", 1),
                ("ati/+/position", 1),
                ("amr/+/status", 1),
                ("amr/+/telemetry", 1),
                ("#", 0)  # Catch-all for debugging
            ]

            for topic, qos in topics:
                client.subscribe(topic, qos)
                print(f"📡 Subscribed to: {topic}")

        else:
            print(f"❌ Connection failed: {rc}")

    def on_message(self, client, userdata, msg):
        self.message_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        print(f"\\n🎉 ATI MESSAGE #{self.message_count} at {timestamp}")
        print(f"   📍 Topic: {msg.topic}")
        print(f"   📦 Size: {len(msg.payload)} bytes")

        try:
            data = json.loads(msg.payload.decode('utf-8'))

            # Pretty print JSON
            print("   📄 Data:")
            print(json.dumps(data, indent=6))

            # Extract key information
            if isinstance(data, dict):
                if "data" in data:
                    inner_data = data["data"]
                    if "eid" in inner_data:
                        event_types = {
                            2001: "❤️ Heartbeat/Trip Start",
                            2002: "🚶 Trip Update",
                            2003: "🏁 Trip End/Error"
                        }
                        eid = inner_data["eid"]
                        print(f"   🏷️  Event: {event_types.get(eid, f'Unknown ({eid})')}")

                    if "pl" in inner_data:
                        payload = inner_data["pl"]
                        if "battery" in payload:
                            battery = payload["battery"]
                            if battery < 20:
                                print(f"   🔋 Battery: {battery}% ⚠️ LOW")
                            else:
                                print(f"   🔋 Battery: {battery}%")

                        if "location" in payload:
                            loc = payload["location"]
                            print(f"   🗺️  Location: {loc.get('lat', '?')}, {loc.get('long', '?')}")

        except json.JSONDecodeError:
            # Not JSON, show raw
            payload_str = msg.payload.decode('utf-8', errors='ignore')
            print(f"   📝 Raw: {payload_str[:200]}")
        except Exception as e:
            print(f"   ❌ Parse error: {e}")

        print("-" * 80)

    def on_disconnect(self, client, userdata, rc, properties=None, reasonCode=None):
        self.connected = False
        print(f"\\n🔌 Disconnected from Railway broker")
        if reasonCode:
            print(f"   Reason: {reasonCode}")

    def monitor(self):
        print("="*80)
        print("🔍 RAILWAY MQTT MONITOR - ATI Data Stream")
        print("="*80)
        print(f"🌐 Broker: {self.broker_url}")
        print(f"👤 User: {self.username}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Create client for WebSocket connection
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"railway-monitor-{int(time.time())}",
            transport="websockets"
        )

        # Set credentials
        client.username_pw_set(self.username, self.password)

        # Configure TLS for wss://
        if 'wss://' in self.broker_url:
            client.tls_set()

        # Set callbacks
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        try:
            print(f"🔗 Connecting to {self.host}:{self.port}...")
            client.connect(self.host, self.port, 60)
            client.loop_forever()

        except KeyboardInterrupt:
            print("\\n⚠️ Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            client.disconnect()
            print(f"\\n📊 Session Summary:")
            print(f"   Total messages received: {self.message_count}")

def main():
    parser = argparse.ArgumentParser(description="Monitor Railway MQTT Broker")
    parser.add_argument("--url", default="wss://your-app.railway.app",
                       help="Railway MQTT WebSocket URL")
    parser.add_argument("--username", default="ati_user",
                       help="MQTT username")
    parser.add_argument("--password", default="ati_password_123",
                       help="MQTT password")

    args = parser.parse_args()

    monitor = RailwayMQTTMonitor(args.url, args.username, args.password)
    monitor.monitor()

if __name__ == "__main__":
    main()
"""

    with open("monitor_railway_mqtt.py", "w") as f:
        f.write(monitor_script)

    # Make executable
    os.chmod("monitor_railway_mqtt.py", 0o755)

    print("✅ Created monitor_railway_mqtt.py")

def main():
    print("🚀 Setting up Railway Deployment for ATI MQTT Broker")
    print("="*60)

    # Create all necessary files
    create_railway_mosquitto_config()
    create_railway_credentials()
    create_railway_dockerfile()

    try:
        create_railway_compose()
    except ImportError:
        print("⚠️ PyYAML not installed - install with: pip install pyyaml")

    create_railway_config()
    create_railway_env()
    create_deployment_script()
    create_monitoring_script()

    # Create data directory
    os.makedirs("railway-deployment/data", exist_ok=True)

    print("\\n" + "="*60)
    print("✅ RAILWAY DEPLOYMENT SETUP COMPLETE!")
    print("="*60)

    print("\\n📋 NEXT STEPS:")
    print("1. Install Railway CLI:")
    print("   npm install -g @railway/cli")
    print()
    print("2. Deploy to Railway:")
    print("   python deploy_to_railway.py")
    print()
    print("3. Monitor ATI data:")
    print("   python monitor_railway_mqtt.py --url wss://your-app.railway.app")
    print()
    print("4. Share URL with ATI:")
    print("   URL: wss://your-app.railway.app")
    print("   Username: ati_user")
    print("   Password: ati_password_123")
    print()
    print("💡 PERMANENT URL BENEFITS:")
    print("   ✅ Never expires")
    print("   ✅ Automatic HTTPS/WSS")
    print("   ✅ No coordination needed")
    print("   ✅ Same URL for ATI and Twinzo")
    print("="*60)

if __name__ == "__main__":
    main()