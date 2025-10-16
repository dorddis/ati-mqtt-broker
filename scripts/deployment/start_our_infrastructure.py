#!/usr/bin/env python3
"""
Start our complete infrastructure for ATI integration
This simulates what YOU run on your side
"""
import subprocess
import time
import threading
import paho.mqtt.client as mqtt
import json
from pathlib import Path

def create_broker_config():
    """Create MQTT broker config for ATI integration"""
    config = """# MQTT Broker for ATI Integration
listener 1883 0.0.0.0
protocol mqtt
allow_anonymous true
log_dest stdout
log_type all
log_timestamp true
connection_messages true
persistence true
persistence_location ./ati_mqtt_data/
"""

    config_path = Path("ati_broker.conf")
    config_path.write_text(config)

    # Create data directory
    Path("ati_mqtt_data").mkdir(exist_ok=True)

    return config_path

def start_mqtt_broker():
    """Start our MQTT broker"""
    config_path = create_broker_config()
    mosquitto_exe = r"C:\Program Files\Mosquitto\mosquitto.exe"

    print("🚀 [OUR SIDE] Starting MQTT broker for ATI...")

    try:
        process = subprocess.Popen([
            mosquitto_exe, "-c", str(config_path), "-v"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        time.sleep(3)

        if process.poll() is None:
            print("✅ [OUR SIDE] MQTT broker started on localhost:1883")
            return process
        else:
            print("❌ [OUR SIDE] MQTT broker failed to start")
            return None

    except Exception as e:
        print(f"❌ [OUR SIDE] Error starting broker: {e}")
        return None

def start_bridge_subscriber():
    """Start our bridge service (subscribes to local broker)"""
    print("🌉 [OUR SIDE] Starting bridge subscriber...")

    messages_received = []

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ [OUR BRIDGE] Connected to local MQTT broker")
            client.subscribe("ati/amr/+/status")
            print("📡 [OUR BRIDGE] Subscribed to ati/amr/+/status")
        else:
            print(f"❌ [OUR BRIDGE] Connection failed: {rc}")

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            messages_received.append({
                'topic': msg.topic,
                'data': data,
                'timestamp': time.time()
            })

            sherpa_name = data.get('sherpa_name', 'unknown')
            battery = data.get('battery_status', 'N/A')

            print(f"📨 [OUR BRIDGE] Received {sherpa_name} data - Battery: {battery}%")

            # Here we would normally forward to Twinzo
            print(f"🔄 [OUR BRIDGE] → Would forward to Twinzo API")

        except Exception as e:
            print(f"❌ [OUR BRIDGE] Error processing message: {e}")

    bridge_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="our_bridge")
    bridge_client.on_connect = on_connect
    bridge_client.on_message = on_message

    try:
        bridge_client.connect("localhost", 1883, 60)
        bridge_client.loop_start()
        return bridge_client, messages_received

    except Exception as e:
        print(f"❌ [OUR BRIDGE] Error: {e}")
        return None, None

def simulate_ngrok_tunnel():
    """Simulate ngrok tunnel (we'd actually run: ngrok tcp 1883)"""
    print("🌐 [OUR SIDE] Simulating ngrok tunnel...")
    print("    In real setup, you'd run: ngrok tcp 1883")
    print("    ngrok would give you something like: tcp://0.tcp.ngrok.io:12345")

    # For testing, we'll pretend ngrok gives us these details
    return {
        'host': 'localhost',  # In real scenario: "0.tcp.ngrok.io"
        'port': 1883,         # In real scenario: 12345 (ngrok port)
        'public_url': 'tcp://localhost:1883'  # In real scenario: "tcp://0.tcp.ngrok.io:12345"
    }

def main():
    print("🏗️  Starting OUR Infrastructure for ATI Integration")
    print("=" * 55)

    # Step 1: Start MQTT broker
    broker = start_mqtt_broker()
    if not broker:
        return

    # Step 2: Start bridge subscriber
    bridge_client, messages_received = start_bridge_subscriber()
    if not bridge_client:
        broker.terminate()
        return

    # Step 3: Simulate ngrok tunnel
    tunnel_info = simulate_ngrok_tunnel()

    print(f"\n🎯 [OUR SIDE] Infrastructure Ready!")
    print("=" * 35)
    print(f"📡 MQTT Broker: Running on localhost:1883")
    print(f"🌉 Bridge Service: Subscribed and listening")
    print(f"🌐 ngrok Tunnel: {tunnel_info['public_url']}")
    print(f"\n📋 Connection Details to Give ATI:")
    print(f"   Host: {tunnel_info['host']}")
    print(f"   Port: {tunnel_info['port']}")

    # Keep running and show activity
    try:
        print(f"\n🎧 [OUR SIDE] Listening for ATI data...")
        print("    (Press Ctrl+C to stop)")

        last_count = 0
        while True:
            time.sleep(5)

            # Show new messages
            if len(messages_received) > last_count:
                new_messages = len(messages_received) - last_count
                print(f"📊 [OUR SIDE] Received {new_messages} new messages (total: {len(messages_received)})")
                last_count = len(messages_received)

    except KeyboardInterrupt:
        print(f"\n🛑 [OUR SIDE] Stopping infrastructure...")

    finally:
        if bridge_client:
            bridge_client.loop_stop()
            bridge_client.disconnect()
            print("✅ [OUR SIDE] Bridge stopped")

        if broker:
            broker.terminate()
            print("✅ [OUR SIDE] MQTT broker stopped")

        print(f"📊 [OUR SIDE] Final Stats: {len(messages_received)} messages processed")

    return tunnel_info, len(messages_received)

if __name__ == "__main__":
    main()