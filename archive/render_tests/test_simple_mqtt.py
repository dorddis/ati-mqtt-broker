#!/usr/bin/env python3
"""
Simple MQTT test - tries multiple connection methods
"""
import paho.mqtt.client as mqtt
import time

def test_websocket():
    print("🔗 Testing WebSocket connection...")
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
        client.username_pw_set("ati_user", "ati_password_123")
        client.tls_set()

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print("✅ WebSocket connection successful!")
                client.publish("test/websocket", "Hello via WebSocket")
            else:
                print(f"❌ WebSocket connection failed: {rc}")

        client.on_connect = on_connect
        client.connect("ati-mqtt-broker.onrender.com", 443, 10)
        client.loop(timeout=5)
        return True
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

def test_websocket_path():
    print("🔗 Testing WebSocket with /mqtt path...")
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
        client.username_pw_set("ati_user", "ati_password_123")
        client.tls_set()
        client.ws_set_options(path="/mqtt")

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print("✅ WebSocket /mqtt path successful!")
                client.publish("test/path", "Hello via /mqtt path")
            else:
                print(f"❌ WebSocket /mqtt path failed: {rc}")

        client.on_connect = on_connect
        client.connect("ati-mqtt-broker.onrender.com", 443, 10)
        client.loop(timeout=5)
        return True
    except Exception as e:
        print(f"❌ WebSocket /mqtt error: {e}")
        return False

def main():
    print("Testing MQTT Broker Connection Methods")
    print("======================================")

    success = False
    success |= test_websocket()
    success |= test_websocket_path()

    if success:
        print("\n✅ At least one connection method worked!")
    else:
        print("\n❌ All connection methods failed")
        print("\nThis suggests the WebSocket listener might not be properly configured.")
        print("The broker is running (health check works), but WebSocket access needs debugging.")

if __name__ == "__main__":
    main()