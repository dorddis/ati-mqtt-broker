#!/usr/bin/env python3
"""
Start local MQTT broker and ngrok tunnel for ATI integration
Simplified version with full Windows paths
"""
import subprocess
import time
import json
import requests
from pathlib import Path

def create_local_config():
    """Create simple local MQTT config"""
    config = """# Local MQTT for ATI via ngrok
listener 1883 0.0.0.0
protocol mqtt
allow_anonymous true
log_dest stdout
log_type all
log_timestamp true
persistence true
persistence_location ./mqtt_data/
connection_messages true
"""

    config_path = Path("local_mqtt.conf")
    config_path.write_text(config)

    # Create data directory
    Path("mqtt_data").mkdir(exist_ok=True)

    return config_path

def start_mqtt_broker():
    """Start local MQTT broker"""
    config_path = create_local_config()
    mosquitto_exe = r"C:\Program Files\Mosquitto\mosquitto.exe"

    print(f"🚀 Starting MQTT broker with config: {config_path}")

    try:
        process = subprocess.Popen([
            mosquitto_exe, "-c", str(config_path), "-v"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

        # Give it time to start
        time.sleep(3)

        if process.poll() is None:
            print("✅ MQTT broker started successfully")
            return process
        else:
            print("❌ MQTT broker failed to start")
            return None

    except Exception as e:
        print(f"❌ Error starting MQTT broker: {e}")
        return None

def start_ngrok_tunnel():
    """Start ngrok tunnel for MQTT"""
    print("🌐 Starting ngrok tunnel...")

    try:
        # Start ngrok tunnel
        ngrok_process = subprocess.Popen([
            'ngrok', 'tcp', '1883'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for tunnel to establish
        time.sleep(8)

        # Get tunnel info
        try:
            response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=10)
            if response.status_code == 200:
                tunnels = response.json()

                for tunnel in tunnels['tunnels']:
                    if tunnel['proto'] == 'tcp':
                        url = tunnel['public_url']
                        host = url.replace('tcp://', '').split(':')[0]
                        port = int(url.replace('tcp://', '').split(':')[1])

                        print(f"✅ ngrok tunnel active!")
                        print(f"🔗 Public URL: {url}")
                        print(f"📡 Host: {host}")
                        print(f"📡 Port: {port}")

                        return {
                            'process': ngrok_process,
                            'url': url,
                            'host': host,
                            'port': port
                        }
        except Exception as e:
            print(f"⚠️  Could not get tunnel info: {e}")
            print("Check ngrok dashboard at: http://127.0.0.1:4040")

        return {'process': ngrok_process}

    except Exception as e:
        print(f"❌ ngrok error: {e}")
        return None

def create_ati_example(tunnel_info):
    """Create ATI integration example"""
    if not tunnel_info or 'host' not in tunnel_info:
        return

    example = f'''#!/usr/bin/env python3
"""
ATI MQTT Integration Example
Connect to local MQTT broker via ngrok tunnel
"""
import paho.mqtt.client as mqtt
import json
import time

# ngrok tunnel connection details
MQTT_HOST = "{tunnel_info['host']}"
MQTT_PORT = {tunnel_info['port']}

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ ATI connected to MQTT broker!")
    else:
        print(f"❌ Connection failed: {{rc}}")

def publish_amr_data(client):
    """Publish sample AMR data"""
    amr_data = {{
        "sherpa_name": "tugger-01",
        "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
        "battery_status": 79.5,
        "mode": "Fleet",
        "timestamp": int(time.time() * 1000)
    }}

    topic = f"ati/amr/{{amr_data['sherpa_name']}}/status"
    result = client.publish(topic, json.dumps(amr_data), qos=1)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"✅ Published {{amr_data['sherpa_name']}} data")
    else:
        print(f"❌ Publish failed: {{result.rc}}")

def main():
    print(f"🔗 Connecting to MQTT broker at {{MQTT_HOST}}:{{MQTT_PORT}}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()

        time.sleep(2)  # Wait for connection

        # Publish test data every 5 seconds
        for i in range(10):
            publish_amr_data(client)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\\n🛑 Stopping...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
'''

    with open("ati_mqtt_example.py", "w") as f:
        f.write(example)

    print(f"✅ Created ATI example: ati_mqtt_example.py")

def test_connection(tunnel_info):
    """Test the MQTT connection"""
    if not tunnel_info or 'host' not in tunnel_info:
        return False

    print(f"🧪 Testing connection to {tunnel_info['host']}:{tunnel_info['port']}...")

    try:
        import paho.mqtt.client as mqtt

        connected = False

        def on_connect(client, userdata, flags, rc, properties=None):
            nonlocal connected
            if rc == 0:
                print("✅ Test connection successful!")
                connected = True

                # Test publish
                test_data = {
                    "sherpa_name": "test-connection",
                    "timestamp": int(time.time() * 1000)
                }

                result = client.publish("test/connection", json.dumps(test_data), qos=1)
                print(f"✅ Test publish: Message ID {result.mid}")

                client.disconnect()
            else:
                print(f"❌ Test connection failed: {rc}")

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect

        client.connect(tunnel_info['host'], tunnel_info['port'], 10)
        client.loop(timeout=10)

        return connected

    except ImportError:
        print("⚠️  paho-mqtt not available for testing")
        return True  # Assume it would work
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("🚀 Local MQTT Broker + ngrok Tunnel for ATI")
    print("=" * 48)

    # Start MQTT broker
    broker = start_mqtt_broker()
    if not broker:
        return

    try:
        # Start ngrok tunnel
        tunnel = start_ngrok_tunnel()
        if not tunnel:
            return

        # Create ATI example
        create_ati_example(tunnel)

        # Test connection
        test_connection(tunnel)

        print("\n🎉 Setup Complete!")
        print("=" * 20)

        if 'host' in tunnel:
            print(f"📡 ATI Connection Details:")
            print(f"   Host: {tunnel['host']}")
            print(f"   Port: {tunnel['port']}")
            print(f"   URL: {tunnel['url']}")

        print(f"📋 ATI Example: ati_mqtt_example.py")
        print(f"🌐 ngrok Dashboard: http://127.0.0.1:4040")
        print(f"📊 MQTT Data Directory: mqtt_data/")

        print("\\n⚠️  Keep this running for tunnel to stay active")
        print("🛑 Press Ctrl+C to stop")

        # Keep running and show MQTT logs
        try:
            while True:
                # Read MQTT broker output
                if broker.poll() is None:
                    line = broker.stdout.readline()
                    if line:
                        print(f"🔍 MQTT: {line.strip()}")
                else:
                    print("⚠️  MQTT broker stopped")
                    break

        except KeyboardInterrupt:
            print("\\n🛑 Shutting down...")

    finally:
        if broker:
            broker.terminate()
            print("✅ MQTT broker stopped")

        if tunnel and 'process' in tunnel:
            tunnel['process'].terminate()
            print("✅ ngrok tunnel stopped")

if __name__ == "__main__":
    main()