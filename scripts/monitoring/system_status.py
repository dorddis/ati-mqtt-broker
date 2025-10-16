#!/usr/bin/env python3
"""Check system status and test MQTT functionality"""
import paho.mqtt.client as mqtt
import time
import json

def test_mqtt_connectivity():
    """Test basic MQTT connectivity"""
    print("=== MQTT Connectivity Test ===")

    messages = []

    def on_connect_sub(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ Subscriber connected successfully")
            client.subscribe("test/#")
        else:
            print(f"❌ Subscriber failed: {rc}")

    def on_message(client, userdata, msg):
        messages.append((msg.topic, msg.payload.decode()))
        print(f"📨 Received: {msg.topic} -> {msg.payload.decode()}")

    def on_connect_pub(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ Publisher connected successfully")
        else:
            print(f"❌ Publisher failed: {rc}")

    # Create subscriber
    sub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="status_sub")
    sub.on_connect = on_connect_sub
    sub.on_message = on_message

    # Create publisher
    pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="status_pub")
    pub.on_connect = on_connect_pub

    try:
        # Connect subscriber
        sub.connect("localhost", 1883, 60)
        sub.loop_start()
        time.sleep(2)

        # Connect publisher
        pub.connect("localhost", 1883, 60)
        pub.loop_start()
        time.sleep(1)

        # Test publishing
        print("\n📤 Publishing test messages...")
        for i in range(3):
            test_data = {
                "sherpa_name": f"test-robot-{i}",
                "battery_status": 85.0 - i,
                "pose": [1000.0 + i, 2000.0, 0.0, 0.0, 0.0, 0.0],
                "timestamp": int(time.time() * 1000)
            }

            topic = f"ati/amr/test-robot-{i}/status"
            result = pub.publish(topic, json.dumps(test_data), qos=1)

            if result.rc == 0:
                print(f"✅ Published test-robot-{i}")
            else:
                print(f"❌ Failed to publish test-robot-{i}: {result.rc}")

            time.sleep(0.5)

        # Wait for messages
        time.sleep(3)

        print(f"\n📊 Results: {len(messages)} messages received")

        if len(messages) > 0:
            print("✅ MQTT system is working correctly!")
            return True
        else:
            print("❌ MQTT system has issues")
            return False

    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

    finally:
        pub.loop_stop()
        pub.disconnect()
        sub.loop_stop()
        sub.disconnect()

if __name__ == "__main__":
    print("🔍 System Status Check")
    print("=" * 25)

    success = test_mqtt_connectivity()

    if success:
        print("\n🎉 System Status: ALL GOOD")
        print("✅ MQTT broker is operational")
        print("✅ Publishing works")
        print("✅ Subscribing works")
        print("✅ Ready for ATI integration")
    else:
        print("\n❌ System Status: ISSUES DETECTED")
        print("🔧 MQTT system needs attention")