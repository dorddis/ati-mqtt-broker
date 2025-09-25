#!/usr/bin/env python3
"""
Setup Render Deployment for ATI MQTT Broker
Free alternative to Railway with 750 hours/month
"""
import os
import json
import yaml
from pathlib import Path

def create_render_yaml():
    """Create render.yaml for Render deployment"""

    render_config = {
        "services": [
            {
                "type": "web",
                "name": "ati-mqtt-broker",
                "env": "docker",
                "dockerfilePath": "./Dockerfile.render",
                "envVars": [
                    {
                        "key": "MQTT_USERNAME",
                        "value": "ati_user"
                    },
                    {
                        "key": "MQTT_PASSWORD",
                        "value": "ati_password_123"
                    },
                    {
                        "key": "ADMIN_USERNAME",
                        "value": "admin"
                    },
                    {
                        "key": "ADMIN_PASSWORD",
                        "value": "admin_password_456"
                    }
                ],
                "disk": {
                    "name": "mqtt-data",
                    "mountPath": "/mosquitto/data",
                    "sizeGB": 1
                },
                "healthCheckPath": "/health"
            }
        ]
    }

    with open("render.yaml", "w") as f:
        yaml.dump(render_config, f, default_flow_style=False, sort_keys=False)

    print("✅ Created render.yaml")

def create_render_dockerfile():
    """Create Render-optimized Dockerfile"""

    dockerfile_content = """# Render MQTT Broker Dockerfile
# Optimized for Render free tier deployment

FROM eclipse-mosquitto:2.0.18

# Install curl for health checks
USER root
RUN apk add --no-cache curl

# Create necessary directories
RUN mkdir -p /mosquitto/data /mosquitto/log /mosquitto/config

# Copy configuration files
COPY render-config/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY render-config/passwd /mosquitto/config/passwd
COPY render-config/acl.conf /mosquitto/config/acl.conf

# Copy health check script
COPY render-config/health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

# Set proper permissions
RUN chown -R mosquitto:mosquitto /mosquitto/data /mosquitto/log /mosquitto/config
RUN chmod 600 /mosquitto/config/passwd /mosquitto/config/acl.conf

# Create health endpoint handler
COPY render-config/health-server.py /usr/local/bin/health-server.py
RUN apk add --no-cache python3 py3-pip
RUN pip3 install flask

# Expose ports (Render will map to 443/80)
EXPOSE 1883 9001 8080

# Use mosquitto user
USER mosquitto

# Start script that runs both mosquitto and health server
COPY render-config/start.sh /usr/local/bin/start.sh
USER root
RUN chmod +x /usr/local/bin/start.sh
USER mosquitto

CMD ["/usr/local/bin/start.sh"]
"""

    with open("Dockerfile.render", "w") as f:
        f.write(dockerfile_content)

    print("✅ Created Dockerfile.render")

def create_render_config_files():
    """Create all Render configuration files"""

    # Create config directory
    os.makedirs("render-config", exist_ok=True)

    # Mosquitto config for Render
    mosquitto_config = """# Render MQTT Configuration
# Optimized for Render free tier with sleep/wake cycle

# Primary MQTT port
port 1883
protocol mqtt

# WebSocket support
listener 9001
protocol websockets
socket_domain ipv4

# Render-friendly logging (to stdout)
log_dest stdout
log_type error
log_type warning
log_type notice
log_type information
log_timestamp true

# Data persistence (Render provides disk)
persistence true
persistence_location /mosquitto/data/
autosave_interval 60

# Authentication
allow_anonymous false
password_file /mosquitto/config/passwd
acl_file /mosquitto/config/acl.conf

# Performance settings for free tier
max_connections 100
max_inflight_messages 50
message_size_limit 1048576

# Keep alive settings
keepalive_interval 60

# Connection logging
connection_messages true
"""

    with open("render-config/mosquitto.conf", "w") as f:
        f.write(mosquitto_config)

    # Credentials
    with open("render-config/passwd", "w") as f:
        f.write("ati_user:ati_password_123\nadmin:admin_password_456\n")

    # ACL config
    acl_config = """# Render MQTT Access Control

# Admin can do everything
user admin
topic readwrite #

# ATI user for publishing AMR data
user ati_user
topic write ati/+/status
topic write ati/+/position
topic write ati/+/battery
topic write ati/+/telemetry
topic write amr/+/status
topic write amr/+/position
topic write keepalive
topic read ati/commands/+
"""

    with open("render-config/acl.conf", "w") as f:
        f.write(acl_config)

    # Health check script
    health_script = """#!/bin/bash
# Health check for Render

# Check if mosquitto is running
if pgrep mosquitto > /dev/null; then
    # Try to publish a test message
    mosquitto_pub -h localhost -p 1883 -u admin -P admin_password_456 -t health/check -m "ok" -q 1
    if [ $? -eq 0 ]; then
        echo "MQTT broker is healthy"
        exit 0
    fi
fi

echo "MQTT broker is not healthy"
exit 1
"""

    with open("render-config/health-check.sh", "w") as f:
        f.write(health_script)

    # Simple health server for Render
    health_server = """#!/usr/bin/env python3
# Simple health endpoint for Render

from flask import Flask
import subprocess
import threading
import time

app = Flask(__name__)

@app.route('/health')
def health():
    try:
        # Check if mosquitto is running
        result = subprocess.run(['pgrep', 'mosquitto'], capture_output=True)
        if result.returncode == 0:
            return {'status': 'healthy', 'service': 'mqtt'}, 200
        else:
            return {'status': 'unhealthy', 'error': 'mosquitto not running'}, 503
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503

@app.route('/')
def root():
    return {'message': 'ATI MQTT Broker', 'status': 'running', 'websocket': 'ws://localhost:9001'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
"""

    with open("render-config/health-server.py", "w") as f:
        f.write(health_server)

    # Start script that runs both services
    start_script = """#!/bin/bash
# Start script for Render - runs both mosquitto and health server

# Start mosquitto in background
echo "Starting MQTT broker..."
mosquitto -c /mosquitto/config/mosquitto.conf &
MQTT_PID=$!

# Wait a moment for MQTT to start
sleep 2

# Start health server in background
echo "Starting health server..."
python3 /usr/local/bin/health-server.py &
HEALTH_PID=$!

# Keep both running
echo "Services started. MQTT PID: $MQTT_PID, Health PID: $HEALTH_PID"

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $MQTT_PID $HEALTH_PID 2>/dev/null
    exit 0
}

trap cleanup SIGTERM SIGINT

# Wait for either process to exit
wait
"""

    with open("render-config/start.sh", "w") as f:
        f.write(start_script)

    print("✅ Created render-config/ files")

def create_render_monitor():
    """Create monitoring script for Render deployment"""

    monitor_script = """#!/usr/bin/env python3
\"\"\"
Monitor Render MQTT Broker
Watch ATI data and handle sleep/wake cycle
\"\"\"
import paho.mqtt.client as mqtt
import json
import ssl
import time
import requests
import threading
from datetime import datetime

class RenderMQTTMonitor:
    def __init__(self, render_url, username="ati_user", password="ati_password_123"):
        self.render_url = render_url
        self.username = username
        self.password = password
        self.message_count = 0
        self.connected = False

        # Extract WebSocket URL
        self.ws_url = render_url.replace('https://', 'wss://').rstrip('/')
        self.host = render_url.replace('https://', '').replace('http://', '').rstrip('/')

    def keep_alive(self):
        \"\"\"Send HTTP requests to keep Render service awake\"\"\"
        while True:
            try:
                response = requests.get(f"https://{self.host}/health", timeout=10)
                if response.status_code == 200:
                    print(f"⏰ Keep-alive ping successful at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    print(f"⚠️ Keep-alive returned {response.status_code}")
            except Exception as e:
                print(f"⚠️ Keep-alive failed: {e}")

            time.sleep(300)  # Ping every 5 minutes (well under 15min sleep)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print(f"✅ Connected to Render MQTT at {datetime.now().strftime('%H:%M:%S')}")
            print(f"🌐 Broker: {self.ws_url}")

            # Subscribe to all ATI topics
            topics = [
                ("ati/+/status", 1),
                ("ati/+/position", 1),
                ("amr/+/status", 1),
                ("amr/+/telemetry", 1),
                ("keepalive", 0),
                ("#", 0)  # Catch all
            ]

            for topic, qos in topics:
                client.subscribe(topic, qos)
                print(f"📡 Subscribed to: {topic}")

        else:
            print(f"❌ Connection failed: {rc}")
            if rc == 1:
                print("   Error: Incorrect protocol version")
            elif rc == 2:
                print("   Error: Invalid client ID")
            elif rc == 3:
                print("   Error: Server unavailable (service may be sleeping)")
                print("   💡 Trying to wake up service...")
                requests.get(f"https://{self.host}/health")
            elif rc == 4:
                print("   Error: Bad username/password")
            elif rc == 5:
                print("   Error: Not authorized")

    def on_message(self, client, userdata, msg):
        self.message_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        # Skip keepalive messages in detailed output
        if msg.topic == "keepalive":
            print(f"💓 Keepalive at {timestamp}")
            return

        print(f"\\n🎉 ATI MESSAGE #{self.message_count} at {timestamp}")
        print(f"   📍 Topic: {msg.topic}")
        print(f"   📦 Size: {len(msg.payload)} bytes")

        try:
            data = json.loads(msg.payload.decode('utf-8'))
            print("   📄 Data:")
            print(json.dumps(data, indent=6)[:500])

            # Extract key info
            if isinstance(data, dict) and "data" in data:
                inner_data = data["data"]
                if "eid" in inner_data:
                    event_types = {
                        2001: "❤️ Heartbeat/Trip Start",
                        2002: "🚶 Trip Update",
                        2003: "🏁 Trip End/Error"
                    }
                    eid = inner_data["eid"]
                    print(f"   🏷️ Event: {event_types.get(eid, f'Unknown ({eid})')}")

        except json.JSONDecodeError:
            payload_str = msg.payload.decode('utf-8', errors='ignore')
            print(f"   📝 Raw: {payload_str[:200]}")
        except Exception as e:
            print(f"   ❌ Parse error: {e}")

        print("-" * 60)

    def on_disconnect(self, client, userdata, rc, properties=None, reasonCode=None):
        self.connected = False
        print(f"\\n🔌 Disconnected from Render broker")
        if reasonCode:
            print(f"   Reason: {reasonCode}")

    def monitor(self):
        print("="*80)
        print("🔍 RENDER MQTT MONITOR - ATI Data Stream")
        print("="*80)
        print(f"🌐 Render URL: {self.render_url}")
        print(f"🔌 WebSocket: {self.ws_url}")
        print(f"👤 Username: {self.username}")
        print(f"⏰ Keep-alive: Every 5 minutes")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Start keep-alive thread
        keepalive_thread = threading.Thread(target=self.keep_alive, daemon=True)
        keepalive_thread.start()

        # Create MQTT client for WebSocket
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"render-monitor-{int(time.time())}",
            transport="websockets"
        )

        # Set credentials
        client.username_pw_set(self.username, self.password)

        # Configure TLS for WSS
        client.tls_set()

        # Set callbacks
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        try:
            print(f"🔗 Connecting to {self.host}...")
            client.connect(self.host, 443, 60)
            client.loop_forever()

        except KeyboardInterrupt:
            print("\\n⚠️ Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            client.disconnect()
            print(f"\\n📊 Session Summary:")
            print(f"   Messages received: {self.message_count}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Monitor Render MQTT Broker")
    parser.add_argument("--url", default="https://your-app.onrender.com",
                       help="Render app URL")
    parser.add_argument("--username", default="ati_user",
                       help="MQTT username")
    parser.add_argument("--password", default="ati_password_123",
                       help="MQTT password")

    args = parser.parse_args()

    monitor = RenderMQTTMonitor(args.url, args.username, args.password)
    monitor.monitor()

if __name__ == "__main__":
    main()
"""

    with open("monitor_render_mqtt.py", "w") as f:
        f.write(monitor_script)

    # Make executable
    os.chmod("monitor_render_mqtt.py", 0o755)

    print("✅ Created monitor_render_mqtt.py")

def create_render_instructions():
    """Create step-by-step Render deployment instructions"""

    instructions = """# Render Deployment Instructions

## Quick Setup (5 minutes)

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub (free)
- No credit card required

### 2. Deploy from GitHub
- Connect your GitHub repo
- Select "Web Service"
- Choose this repository
- Render auto-detects render.yaml

### 3. Get Your URL
After deployment completes:
- Your app will be at: https://your-app-name.onrender.com
- WebSocket URL: wss://your-app-name.onrender.com

### 4. Test Connection
```bash
# Monitor your broker
python monitor_render_mqtt.py --url https://your-app-name.onrender.com
```

### 5. Share with ATI
Give ATI these details:
```
MQTT WebSocket URL: wss://your-app-name.onrender.com
Username: ati_user
Password: ati_password_123
Topics: ati/amr/status, amr/position, etc.
```

## Important Notes

**Sleep Behavior:**
- Service sleeps after 15 minutes of no HTTP requests
- WebSocket connections don't prevent sleep
- Monitor script includes keep-alive HTTP pings
- ATI can add keep-alive pings too

**Free Tier Limits:**
- 750 hours/month (31+ days)
- No bandwidth limits
- 1GB disk storage
- Automatic SSL/HTTPS

**Keep Awake Options:**
1. Monitor script (recommended)
2. ATI adds keep-alive HTTP requests
3. External uptime monitor (UptimeRobot, etc.)

## Troubleshooting

**Service won't start:**
- Check build logs in Render dashboard
- Ensure Dockerfile.render is correct

**Connection refused:**
- Service may be sleeping
- Try HTTP request to https://your-app.onrender.com/health
- Wait 30 seconds for wake-up

**Can't connect via WebSocket:**
- URL should start with wss:// not ws://
- Port should be 443 (default for wss)
- Render handles SSL termination
"""

    with open("RENDER_DEPLOYMENT.md", "w") as f:
        f.write(instructions)

    print("✅ Created RENDER_DEPLOYMENT.md")

def main():
    print("🚀 Setting up Render Deployment for ATI MQTT Broker")
    print("="*60)

    try:
        create_render_yaml()
        create_render_dockerfile()
        create_render_config_files()
        create_render_monitor()
        create_render_instructions()
    except ImportError as e:
        if "yaml" in str(e):
            print("⚠️ PyYAML not installed")
            print("Install with: pip install pyyaml")
        else:
            raise

    print("\\n" + "="*60)
    print("✅ RENDER DEPLOYMENT SETUP COMPLETE!")
    print("="*60)

    print("\\n📋 NEXT STEPS:")
    print("1. Create Render account (free):")
    print("   https://render.com")
    print()
    print("2. Connect GitHub repo and deploy")
    print("   (Render will use render.yaml automatically)")
    print()
    print("3. Get your permanent URL:")
    print("   https://your-app-name.onrender.com")
    print()
    print("4. Monitor ATI data:")
    print("   python monitor_render_mqtt.py --url https://your-app.onrender.com")
    print()
    print("5. Share with ATI:")
    print("   WebSocket: wss://your-app-name.onrender.com")
    print("   Username: ati_user")
    print("   Password: ati_password_123")
    print()
    print("💡 FREE TIER BENEFITS:")
    print("   ✅ 750 hours/month (enough for 24/7)")
    print("   ✅ Permanent URL (never expires)")
    print("   ✅ Auto SSL/HTTPS")
    print("   ✅ No credit card required")
    print("   ⚠️ Sleeps after 15min (keep-alive included)")
    print("="*60)

if __name__ == "__main__":
    main()