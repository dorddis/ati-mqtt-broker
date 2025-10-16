#!/usr/bin/env python3
"""
Setup ngrok tunnel for local MQTT broker
Provides stable MQTT access for ATI integration
"""
import subprocess
import time
import json
import os
import requests
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ngrok installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ ngrok not found")
            return False
    except FileNotFoundError:
        print("❌ ngrok not installed")
        return False

def install_ngrok_instructions():
    """Provide ngrok installation instructions"""
    print("\n📋 ngrok Installation Instructions:")
    print("=" * 40)
    print("1. Download ngrok from: https://ngrok.com/download")
    print("2. Extract to a directory in your PATH")
    print("3. Sign up for free account at: https://ngrok.com/signup")
    print("4. Get auth token from: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("5. Run: ngrok config add-authtoken YOUR_TOKEN")
    print("\nThen run this script again.")

def create_local_mqtt_config():
    """Create local MQTT broker configuration"""
    config_content = """# Local MQTT Broker for ngrok tunnel
# Simple configuration for ATI integration

# Standard MQTT port
listener 1883 0.0.0.0
protocol mqtt

# Allow anonymous connections (for testing)
allow_anonymous true

# Logging
log_dest stdout
log_type error
log_type warning
log_type notice
log_type information
log_timestamp true

# Persistence
persistence true
persistence_location ./mqtt_data/
autosave_interval 60

# Performance settings
max_connections 100
max_inflight_messages 50
message_size_limit 1048576

# Connection logging
connection_messages true
"""

    # Create config file
    config_path = Path("mosquitto_local.conf")
    config_path.write_text(config_content)
    print(f"✅ Created local MQTT config: {config_path}")

    # Create data directory
    data_dir = Path("mqtt_data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Created data directory: {data_dir}")

    return config_path

def start_local_mqtt_broker(config_path):
    """Start local MQTT broker"""
    print("\n🚀 Starting local MQTT broker...")

    # Check if mosquitto is installed
    try:
        subprocess.run(['mosquitto', '-h'], capture_output=True)
        print("✅ mosquitto found")
    except FileNotFoundError:
        print("❌ mosquitto not installed")
        print("Install mosquitto:")
        print("  Windows: https://mosquitto.org/download/")
        print("  Linux: sudo apt-get install mosquitto")
        print("  macOS: brew install mosquitto")
        return None

    # Start mosquitto broker
    try:
        print(f"Starting mosquitto with config: {config_path}")
        broker_process = subprocess.Popen([
            'mosquitto', '-c', str(config_path), '-v'
        ])

        # Give it a moment to start
        time.sleep(2)

        if broker_process.poll() is None:
            print("✅ Local MQTT broker started successfully")
            return broker_process
        else:
            print("❌ MQTT broker failed to start")
            return None

    except Exception as e:
        print(f"❌ Error starting MQTT broker: {e}")
        return None

def setup_ngrok_tunnel():
    """Setup ngrok tunnel for MQTT"""
    print("\n🌐 Setting up ngrok tunnel...")

    try:
        # Start ngrok tunnel for MQTT port 1883
        ngrok_process = subprocess.Popen([
            'ngrok', 'tcp', '1883', '--log', 'stdout'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Give ngrok time to establish tunnel
        time.sleep(5)

        # Get tunnel info from ngrok API
        try:
            response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()

                for tunnel in tunnels['tunnels']:
                    if tunnel['proto'] == 'tcp':
                        public_url = tunnel['public_url']
                        print(f"✅ ngrok tunnel established!")
                        print(f"🔗 Public MQTT URL: {public_url}")

                        # Extract host and port
                        url_parts = public_url.replace('tcp://', '').split(':')
                        host = url_parts[0]
                        port = int(url_parts[1])

                        return {
                            'process': ngrok_process,
                            'public_url': public_url,
                            'host': host,
                            'port': port
                        }

        except requests.exceptions.RequestException:
            print("⚠️  Couldn't get tunnel info from ngrok API")
            print("Check ngrok dashboard at: http://127.0.0.1:4040")

        return {'process': ngrok_process, 'public_url': 'check_dashboard'}

    except Exception as e:
        print(f"❌ Error setting up ngrok tunnel: {e}")
        return None

def create_ati_integration_example(tunnel_info):
    """Create example code for ATI"""
    if not tunnel_info or 'host' not in tunnel_info:
        print("⚠️  Tunnel info incomplete - check ngrok dashboard for details")
        return

    example_code = f'''#!/usr/bin/env python3
"""
ATI MQTT Integration via ngrok tunnel
Connects to local MQTT broker through ngrok
"""
import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to MQTT broker via ngrok!")
        # ATI can start publishing AMR data here
    else:
        print(f"❌ Connection failed: {{rc}}")

def publish_amr_data(client, amr_data):
    """Publish AMR data to MQTT broker"""
    topic = f"ati/amr/{{amr_data['sherpa_name']}}/status"
    result = client.publish(topic, json.dumps(amr_data), qos=1)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"✅ Published {{amr_data['sherpa_name']}} data")
        return True
    else:
        print(f"❌ Publish failed: {{result.rc}}")
        return False

def main():
    # ngrok tunnel details
    MQTT_HOST = "{tunnel_info['host']}"
    MQTT_PORT = {tunnel_info['port']}

    print(f"🔗 Connecting to MQTT broker at {{MQTT_HOST}}:{{MQTT_PORT}}")

    # Setup MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect

    # Connect to broker
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    # Example AMR data publishing
    time.sleep(2)  # Wait for connection

    # Sample AMR data
    sample_data = {{
        "sherpa_name": "tugger-01",
        "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
        "battery_status": 79.5,
        "mode": "Fleet",
        "timestamp": int(time.time() * 1000)
    }}

    # Publish sample data
    publish_amr_data(client, sample_data)

    # Keep publishing (ATI would do this in their main loop)
    try:
        while True:
            # Update AMR data with real values
            sample_data["timestamp"] = int(time.time() * 1000)
            sample_data["battery_status"] -= 0.1  # Simulate battery drain

            publish_amr_data(client, sample_data)
            time.sleep(10)  # Publish every 10 seconds

    except KeyboardInterrupt:
        print("\\n🛑 Stopping...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
'''

    # Write example to file
    example_path = Path("ati_ngrok_integration_example.py")
    example_path.write_text(example_code)
    print(f"✅ Created ATI integration example: {example_path}")

def create_test_client(tunnel_info):
    """Create test client to verify tunnel"""
    print("\n🧪 Testing ngrok MQTT tunnel...")

    if not tunnel_info or 'host' not in tunnel_info:
        print("⚠️  Can't test - tunnel info incomplete")
        return False

    try:
        import paho.mqtt.client as mqtt

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print("✅ Test client connected successfully!")

                # Publish test message
                test_data = {
                    "sherpa_name": "test-amr",
                    "pose": [195630.0, 188400.0, 0.0, 0.0, 0.0, 1.57],
                    "battery_status": 85.0,
                    "timestamp": int(time.time() * 1000)
                }

                result = client.publish("ati/test/connection", json.dumps(test_data), qos=1)

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print("✅ Test message published successfully!")
                    return True
                else:
                    print(f"❌ Test publish failed: {result.rc}")
                    return False
            else:
                print(f"❌ Test connection failed: {rc}")
                return False

        # Create test client
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect

        print(f"🔗 Testing connection to {tunnel_info['host']}:{tunnel_info['port']}...")
        client.connect(tunnel_info['host'], tunnel_info['port'], 10)
        client.loop(timeout=10)

        return True

    except ImportError:
        print("⚠️  paho-mqtt not installed - can't test connection")
        print("Install with: pip install paho-mqtt")
        return False
    except Exception as e:
        print(f"❌ Test connection error: {e}")
        return False

def main():
    print("🚀 ngrok MQTT Tunnel Setup for ATI Integration")
    print("=" * 52)

    # Step 1: Check ngrok installation
    if not check_ngrok_installed():
        install_ngrok_instructions()
        return

    # Step 2: Create local MQTT configuration
    config_path = create_local_mqtt_config()

    # Step 3: Start local MQTT broker
    broker_process = start_local_mqtt_broker(config_path)
    if not broker_process:
        return

    try:
        # Step 4: Setup ngrok tunnel
        tunnel_info = setup_ngrok_tunnel()
        if not tunnel_info:
            return

        # Step 5: Create ATI integration example
        create_ati_integration_example(tunnel_info)

        # Step 6: Test the connection
        create_test_client(tunnel_info)

        print("\n🎉 ngrok MQTT Setup Complete!")
        print("=" * 35)

        if 'public_url' in tunnel_info and tunnel_info['public_url'] != 'check_dashboard':
            print(f"📡 ATI MQTT Connection Details:")
            print(f"   Host: {tunnel_info.get('host', 'check_dashboard')}")
            print(f"   Port: {tunnel_info.get('port', 'check_dashboard')}")
            print(f"   URL: {tunnel_info['public_url']}")
        else:
            print("📡 Check ngrok dashboard for connection details:")
            print("   http://127.0.0.1:4040")

        print(f"📋 Integration file created: ati_ngrok_integration_example.py")
        print(f"🔧 MQTT config: {config_path}")

        print("\n⚠️  Important Notes:")
        print("   • Keep this script running to maintain tunnel")
        print("   • ngrok tunnel URL changes when restarted")
        print("   • Free ngrok has connection limits")
        print("   • Use ngrok pro for production stability")

        print("\n🛑 Press Ctrl+C to stop tunnel and broker")

        # Keep running
        try:
            while True:
                time.sleep(30)
                # Check if broker is still running
                if broker_process.poll() is not None:
                    print("⚠️  MQTT broker stopped unexpectedly")
                    break
        except KeyboardInterrupt:
            print("\n🛑 Stopping ngrok tunnel and MQTT broker...")

    finally:
        # Cleanup
        if 'broker_process' in locals() and broker_process:
            broker_process.terminate()
            print("✅ MQTT broker stopped")

        if tunnel_info and 'process' in tunnel_info:
            tunnel_info['process'].terminate()
            print("✅ ngrok tunnel stopped")

if __name__ == "__main__":
    main()