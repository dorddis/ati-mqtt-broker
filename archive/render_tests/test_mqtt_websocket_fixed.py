#!/usr/bin/env python3
"""
Fixed MQTT WebSocket test using correct path configuration
"""
import paho.mqtt.client as mqtt
import json
import time
import threading

def test_mqtt_websocket_with_paths():
    """Test different WebSocket path configurations"""
    paths_to_try = ["/", "/mqtt", "/ws"]

    for path in paths_to_try:
        print(f"\n🧪 Testing WebSocket MQTT with path: '{path}'")

        success = threading.Event()

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print(f"✅ Connected successfully with path '{path}'!")
                success.set()

                # Test publish
                test_data = {
                    "sherpa_name": "test-amr",
                    "pose": [195630.0, 188400.0, 0.0, 0.0, 0.0, 1.57],
                    "battery_status": 85.0,
                    "timestamp": int(time.time() * 1000)
                }

                result = client.publish("ati/test/websocket", json.dumps(test_data), qos=1)
                print(f"Published test message: {result.mid}")

                client.disconnect()
            else:
                print(f"❌ Connection failed with path '{path}': {rc}")

        def on_disconnect(client, userdata, rc):
            print(f"Disconnected from path '{path}': {rc}")

        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
            client.tls_set()
            client.ws_set_options(path=path)  # This is the key fix!

            client.on_connect = on_connect
            client.on_disconnect = on_disconnect

            print(f"Connecting to wss://ati-mqtt-broker.onrender.com with path '{path}'...")
            client.connect("ati-mqtt-broker.onrender.com", 443, 10)
            client.loop_start()

            # Wait for connection result
            if success.wait(timeout=8):
                print(f"✅ SUCCESS with path '{path}'!")
                client.loop_stop()
                return path  # Return successful path
            else:
                print(f"❌ Timeout with path '{path}'")

            client.loop_stop()
            time.sleep(1)  # Brief pause between attempts

        except Exception as e:
            print(f"❌ Error with path '{path}': {e}")

    print("\n❌ All WebSocket paths failed")
    return None

def test_direct_port_connection():
    """Test connecting directly to port 8080 (bypassing CDN)"""
    print(f"\n🧪 Testing direct connection to port 8080...")

    success = threading.Event()

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ Direct port 8080 connection successful!")
            success.set()
            client.disconnect()
        else:
            print(f"❌ Direct port 8080 failed: {rc}")

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
        # No TLS for direct port test
        client.ws_set_options(path="/")

        client.on_connect = on_connect

        print("Connecting to ws://ati-mqtt-broker.onrender.com:8080...")
        client.connect("ati-mqtt-broker.onrender.com", 8080, 10)
        client.loop_start()

        if success.wait(timeout=8):
            print("✅ Direct port connection worked!")
            client.loop_stop()
            return True
        else:
            print("❌ Direct port connection timeout")

        client.loop_stop()

    except Exception as e:
        print(f"❌ Direct port connection error: {e}")

    return False

def main():
    print("🚀 Fixed MQTT WebSocket Connection Test")
    print("=" * 45)

    # First, wait for service to be ready
    print("⏳ Waiting for service deployment to complete...")
    time.sleep(5)

    # Test 1: Try different WebSocket paths
    successful_path = test_mqtt_websocket_with_paths()

    # Test 2: Try direct port connection
    direct_success = test_direct_port_connection()

    print("\n📊 Test Results Summary:")
    print("=" * 30)

    if successful_path:
        print(f"✅ WebSocket MQTT working with path: '{successful_path}'")
        print(f"✅ ATI should use: wss://ati-mqtt-broker.onrender.com with ws_set_options(path='{successful_path}')")
    elif direct_success:
        print("✅ Direct port connection working")
        print("✅ ATI should use: ws://ati-mqtt-broker.onrender.com:8080")
    else:
        print("❌ All connection methods failed")
        print("💡 May need to debug Render port mapping or Mosquitto configuration")

    return successful_path is not None or direct_success

if __name__ == "__main__":
    main()