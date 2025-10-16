#!/usr/bin/env python3
"""
Simple test subscriber to verify ATI data is flowing
"""
import paho.mqtt.client as mqtt
import json
import time

messages_received = []

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to MQTT broker!")
        client.subscribe("ati/amr/+/status")
        client.subscribe("#")  # Subscribe to all topics for debugging
        print("📡 Subscribed to ati/amr/+/status and all topics")
    else:
        print(f"❌ Connection failed: {rc}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        messages_received.append((topic, payload))

        print(f"📨 Received on {topic}:")

        # Try to parse as JSON for better formatting
        try:
            data = json.loads(payload)
            if isinstance(data, dict) and 'sherpa_name' in data:
                sherpa = data.get('sherpa_name', 'unknown')
                battery = data.get('battery_status', 'N/A')
                pose = data.get('pose', [0,0,0,0,0,0])
                print(f"    🤖 Robot: {sherpa}")
                print(f"    🔋 Battery: {battery}%")
                print(f"    📍 Position: [{pose[0]:.1f}, {pose[1]:.1f}]")
            else:
                print(f"    Data: {json.dumps(data, indent=2)[:200]}...")
        except:
            print(f"    Raw: {payload[:100]}...")

    except Exception as e:
        print(f"❌ Error processing message: {e}")

def main():
    print("🎧 Test Subscriber for ATI Integration")
    print("=" * 40)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="test_subscriber")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect("localhost", 1883, 60)
        client.loop_start()

        print("⏳ Listening for messages for 30 seconds...")
        start_time = time.time()

        while time.time() - start_time < 30:
            time.sleep(1)
            if len(messages_received) > 0:
                print(f"📊 Total messages received: {len(messages_received)}")

        print(f"\n📊 Final Results:")
        print(f"Messages Received: {len(messages_received)}")

        if len(messages_received) > 0:
            print("✅ Data is flowing correctly!")
            unique_topics = set(msg[0] for msg in messages_received)
            print(f"Topics seen: {', '.join(unique_topics)}")
        else:
            print("❌ No messages received - check if ATI simulator is running")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()