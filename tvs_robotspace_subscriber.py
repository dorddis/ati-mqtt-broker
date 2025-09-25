#!/usr/bin/env python3
"""
TVS Robotspace MQTT Subscriber
Based on the official documentation - subscribes to the correct topic patterns
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
from datetime import datetime

# Configuration from documentation
HOST = "tvs-dev.ifactory.ai"
PORT = 8883
USERNAME = "amr-001"
PASSWORD = "TVSamr001@2025"
CLIENT_ID = "amr-001"

# Track data
messages_received = []
connected = False
subscription_status = {}

def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"✅ Connected successfully at {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Client ID: {CLIENT_ID}")

        # Subscribe to topics based on documentation patterns
        topics = [
            # Device-to-cloud patterns (where AMRs publish)
            ("/d2c/+", "All device-to-cloud messages"),
            ("/d2c/amr-001", "Our device's messages"),
            (f"/d2c/{CLIENT_ID}", "Client ID based d2c"),

            # Cloud-to-device patterns (commands to devices)
            ("/c2d/+", "All cloud-to-device messages"),
            (f"/c2d/{CLIENT_ID}", "Commands to our device"),

            # Wildcards to discover any topics
            ("#", "All topics"),
            ("+", "Single level wildcard"),

            # Original patterns from documentation
            ("ati_fm/sherpa/status", "Primary ATI topic"),

            # Patterns that might be used by devices
            ("/d2c/device-1", "Device 1 messages"),
            ("/d2c/device-2", "Device 2 messages"),
            ("/d2c/tug-133", "Tug 133 messages"),
            ("/d2c/tug-39", "Tug 39 messages"),

            # Alternative patterns
            ("d2c/+", "D2C without leading slash"),
            ("c2d/+", "C2D without leading slash"),
        ]

        print("\n📡 Subscribing to topics based on documentation:")
        for topic, description in topics:
            result, mid = client.subscribe(topic, qos=1)
            print(f"   • {topic}: {description} (mid={mid})")
            subscription_status[mid] = (topic, description)

    else:
        connected = False
        print(f"❌ Connection failed: {rc}")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    if mid in subscription_status:
        topic, desc = subscription_status[mid]
        if granted_qos and len(granted_qos) > 0:
            if hasattr(granted_qos[0], 'is_failure') and granted_qos[0].is_failure:
                print(f"   ❌ {topic}: Not authorized")
            else:
                print(f"   ✅ {topic}: Subscription granted (QoS: {granted_qos})")

def on_message(client, userdata, msg):
    global messages_received

    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"\n🎉 MESSAGE RECEIVED at {timestamp}!")
    print(f"   Topic: {msg.topic}")
    print(f"   QoS: {msg.qos}, Retain: {msg.retain}")

    try:
        payload = msg.payload.decode('utf-8')
        print(f"   Size: {len(payload)} bytes")

        try:
            # Try to parse as JSON (expected format)
            data = json.loads(payload)
            print(f"   JSON Data:")

            # Check if it matches expected format from docs
            if "data" in data:
                print(f"      Event ID: {data['data'].get('eid', 'N/A')}")
                print(f"      Device ID: {data['data'].get('did', 'N/A')}")
                print(f"      Timestamp: {data['data'].get('ts', 'N/A')}")
                print(f"      Unique Event ID: {data['data'].get('ueid', 'N/A')}")
                if "pl" in data["data"]:
                    print(f"      Payload: {json.dumps(data['data']['pl'], indent=8)[:500]}")
            else:
                print(json.dumps(data, indent=4)[:500])

            messages_received.append({
                "timestamp": timestamp,
                "topic": msg.topic,
                "data": data
            })

        except json.JSONDecodeError:
            # Not JSON, show raw
            print(f"   Raw Data: {payload[:200]}")
            messages_received.append({
                "timestamp": timestamp,
                "topic": msg.topic,
                "raw": payload
            })

    except UnicodeDecodeError:
        print(f"   Binary Data: {msg.payload.hex()[:100]}...")
        messages_received.append({
            "timestamp": timestamp,
            "topic": msg.topic,
            "binary": msg.payload.hex()
        })

    print("-" * 70)

def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
    global connected
    connected = False
    print(f"\n🔌 Disconnected at {datetime.now().strftime('%H:%M:%S')}")
    if reasonCode:
        print(f"   Reason: {reasonCode}")

def main():
    print("="*80)
    print("🔍 TVS ROBOTSPACE MQTT SUBSCRIBER")
    print("   Based on Official Documentation")
    print("="*80)
    print(f"Broker: {HOST}:{PORT}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Username: {USERNAME}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Create client with MQTTv5 as per documentation
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID,
        protocol=mqtt.MQTTv5
    )

    # Set credentials
    client.username_pw_set(USERNAME, PASSWORD)

    # Configure TLS
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    client.tls_set_context(context)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect

    # Enable logging for debugging
    client.enable_logger()

    try:
        print("\n🔗 Connecting to broker...")
        client.connect(HOST, PORT, keepalive=60)

        # Start loop
        client.loop_start()

        # Monitor for messages
        print("\n⏱️ Monitoring for 3 minutes...")
        start_time = time.time()
        last_report = time.time()

        while time.time() - start_time < 180:  # 3 minutes
            time.sleep(1)

            # Report every 20 seconds
            if time.time() - last_report >= 20:
                elapsed = int(time.time() - start_time)
                if connected:
                    if messages_received:
                        print(f"📊 [{elapsed}s] Connected - {len(messages_received)} messages received")
                    else:
                        print(f"⏳ [{elapsed}s] Connected - No messages yet...")
                else:
                    print(f"❌ [{elapsed}s] Not connected - reconnecting...")
                    try:
                        client.reconnect()
                    except:
                        pass
                last_report = time.time()

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")

    # Final report
    print("\n" + "="*80)
    print("📊 FINAL REPORT")
    print("="*80)

    if messages_received:
        print(f"\n✅ SUCCESS! Received {len(messages_received)} messages")

        # Group by topic
        topics_seen = {}
        for msg in messages_received:
            topic = msg["topic"]
            if topic not in topics_seen:
                topics_seen[topic] = []
            topics_seen[topic].append(msg)

        print(f"\n📋 Topics with data:")
        for topic, msgs in topics_seen.items():
            print(f"   • {topic}: {len(msgs)} messages")

            # Show sample of first message
            first_msg = msgs[0]
            if "data" in first_msg:
                print(f"     Sample: {json.dumps(first_msg['data'], indent=6)[:200]}")
            elif "raw" in first_msg:
                print(f"     Sample: {first_msg['raw'][:100]}")

    else:
        print("\n❌ No messages received")
        print("\nPossible reasons:")
        print("• AMR devices are not publishing data")
        print("• ACL permissions still blocking subscriptions")
        print("• Data is published to different topics than documented")
        print("• Need different credentials with proper permissions")

    print("="*80)

if __name__ == "__main__":
    main()