#!/usr/bin/env python3
"""
Test local MQTT broker functionality
Simple test to verify MQTT broker works before ngrok
"""
import subprocess
import time
import paho.mqtt.client as mqtt
import json
from pathlib import Path
import threading

def create_mqtt_config():
    """Create simple MQTT config"""
    config = """# Simple MQTT config for testing
listener 1883 0.0.0.0
protocol mqtt
allow_anonymous true
log_dest stdout
log_type all
log_timestamp true
connection_messages true
"""

    config_file = Path("test_mqtt.conf")
    config_file.write_text(config)
    return config_file

def start_mqtt_broker():
    """Start MQTT broker for testing"""
    config_file = create_mqtt_config()
    mosquitto_exe = r"C:\Program Files\Mosquitto\mosquitto.exe"

    print("🚀 Starting local MQTT broker for testing...")

    try:
        process = subprocess.Popen([
            mosquitto_exe, "-c", str(config_file), "-v"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        time.sleep(3)  # Let it start

        if process.poll() is None:
            print("✅ MQTT broker started successfully!")
            return process
        else:
            print("❌ MQTT broker failed to start")
            # Read any error output
            output, _ = process.communicate()
            print(f"Error: {output}")
            return None

    except Exception as e:
        print(f"❌ Error starting MQTT broker: {e}")
        return None

def test_mqtt_connection():
    """Test MQTT publish/subscribe locally"""
    print("🧪 Testing MQTT connection...")

    messages_received = []
    connection_success = threading.Event()

    def on_connect_sub(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ Subscriber connected!")
            client.subscribe("test/+")
            client.subscribe("ati/amr/+/status")
            connection_success.set()
        else:
            print(f"❌ Subscriber connection failed: {rc}")

    def on_message(client, userdata, msg):
        message = msg.payload.decode()
        print(f"📨 Received: {msg.topic} -> {message}")
        messages_received.append((msg.topic, message))

    def on_connect_pub(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ Publisher connected!")
        else:
            print(f"❌ Publisher connection failed: {rc}")

    try:
        # Create subscriber
        sub_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="test_subscriber")
        sub_client.on_connect = on_connect_sub
        sub_client.on_message = on_message

        # Create publisher
        pub_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="test_publisher")
        pub_client.on_connect = on_connect_pub

        print("🔗 Connecting subscriber...")
        sub_client.connect("localhost", 1883, 60)
        sub_client.loop_start()

        # Wait for subscriber to connect
        if not connection_success.wait(timeout=10):
            print("❌ Subscriber connection timeout")
            return False

        print("🔗 Connecting publisher...")
        pub_client.connect("localhost", 1883, 60)
        pub_client.loop_start()

        time.sleep(2)  # Let connections settle

        # Test 1: Simple message
        print("📤 Publishing test message...")
        result = pub_client.publish("test/simple", "Hello MQTT!", qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ Simple message published")
        else:
            print(f"❌ Simple message failed: {result.rc}")

        # Test 2: AMR-style message
        print("📤 Publishing AMR-style message...")
        amr_data = {
            "sherpa_name": "test-amr-001",
            "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
            "battery_status": 79.5,
            "mode": "Fleet",
            "timestamp": int(time.time() * 1000)
        }

        result = pub_client.publish("ati/amr/test-amr-001/status", json.dumps(amr_data), qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ AMR message published")
        else:
            print(f"❌ AMR message failed: {result.rc}")

        # Wait for messages to be received
        time.sleep(3)

        # Test 3: High frequency messages
        print("📤 Publishing high frequency messages...")
        for i in range(5):
            high_freq_data = {
                "sherpa_name": f"speed-test-{i}",
                "pose": [195630.0 + i, 188400.0, 0.0, 0.0, 0.0, 0.0],
                "battery_status": 85.0 - i,
                "timestamp": int(time.time() * 1000)
            }
            result = pub_client.publish(f"test/speed/{i}", json.dumps(high_freq_data), qos=1)
            print(f"  Message {i+1}: {'✅' if result.rc == 0 else '❌'}")
            time.sleep(0.2)  # 5 Hz

        # Final wait
        time.sleep(2)

        # Cleanup
        pub_client.loop_stop()
        sub_client.loop_stop()
        pub_client.disconnect()
        sub_client.disconnect()

        # Results
        print(f"\n📊 Test Results:")
        print(f"Messages Received: {len(messages_received)}")

        if len(messages_received) > 0:
            print("✅ MQTT broker is working correctly!")
            print("📨 Received messages:")
            for topic, message in messages_received:
                print(f"  - {topic}: {message[:50]}{'...' if len(message) > 50 else ''}")
            return True
        else:
            print("❌ No messages received - check broker logs")
            return False

    except Exception as e:
        print(f"❌ MQTT test error: {e}")
        return False

def main():
    print("🧪 Local MQTT Broker Test")
    print("=" * 28)

    # Start broker
    broker = start_mqtt_broker()
    if not broker:
        print("❌ Cannot start MQTT broker - check Mosquitto installation")
        return

    try:
        # Test MQTT functionality
        success = test_mqtt_connection()

        if success:
            print("\n🎉 Local MQTT Broker Test: SUCCESS!")
            print("✅ Ready for ngrok tunnel setup")
            print("✅ ATI can connect via ngrok once tunnel is established")
        else:
            print("\n❌ Local MQTT Broker Test: FAILED")
            print("🔧 Check broker logs and configuration")

    finally:
        print("\n🛑 Stopping MQTT broker...")
        broker.terminate()

        # Wait a moment and force kill if needed
        try:
            broker.wait(timeout=3)
            print("✅ MQTT broker stopped cleanly")
        except subprocess.TimeoutExpired:
            broker.kill()
            print("⚠️  MQTT broker force killed")

if __name__ == "__main__":
    main()