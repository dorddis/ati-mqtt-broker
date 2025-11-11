#!/usr/bin/env python3
"""
TVS Exhaustive Topic Testing
Systematically test every possible topic to find what we can access
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
from datetime import datetime
import sys

# Configuration
HOST = "tvs-dev.ifactory.ai"
PORT = 8883
USERNAME = "amr-001"
PASSWORD = "TVSamr001@2025"

# Track results
successful_subscriptions = []
failed_subscriptions = []
messages_received = {}
connected = False

def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"✅ Connected successfully at {datetime.now().strftime('%H:%M:%S')}")
    else:
        connected = False
        print(f"❌ Connection failed: {rc}")

def on_message(client, userdata, msg):
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    topic = msg.topic

    if topic not in messages_received:
        messages_received[topic] = []

    print(f"\n🎉 MESSAGE RECEIVED!")
    print(f"   Topic: {topic}")
    print(f"   Time: {timestamp}")
    print(f"   QoS: {msg.qos}, Retain: {msg.retain}")

    try:
        payload = msg.payload.decode('utf-8')
        try:
            data = json.loads(payload)
            print(f"   Data: {json.dumps(data, indent=4)[:500]}")
            messages_received[topic].append(data)
        except:
            print(f"   Raw: {payload[:200]}")
            messages_received[topic].append(payload)
    except:
        print(f"   Binary: {msg.payload.hex()[:100]}")
        messages_received[topic].append(msg.payload.hex())

    print("-" * 60)

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    if granted_qos and len(granted_qos) > 0:
        if granted_qos[0].is_failure:
            print(f"   ❌ Subscription MID={mid} FAILED: {granted_qos[0]}")
        else:
            print(f"   ✅ Subscription MID={mid} granted QoS: {granted_qos}")

def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
    global connected
    connected = False
    print(f"\n🔌 Disconnected: rc={rc}, reason={reasonCode}")

def test_topic_subscription(client, topic, description):
    """Test subscription to a specific topic"""
    print(f"\n🔬 Testing: {description}")
    print(f"   Topic: '{topic}'")

    try:
        result, mid = client.subscribe(topic, qos=1)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"   📡 Subscribe request sent (MID={mid})")
            time.sleep(2)  # Wait for response

            # Check if still connected
            if connected:
                successful_subscriptions.append((topic, description))
                print(f"   ✅ Still connected - subscription might be allowed")
                return True
            else:
                failed_subscriptions.append((topic, description))
                print(f"   ❌ Disconnected - subscription not allowed")
                # Reconnect for next test
                client.reconnect()
                time.sleep(1)
                return False
        else:
            failed_subscriptions.append((topic, description))
            print(f"   ❌ Subscribe failed: {result}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        failed_subscriptions.append((topic, description))
        return False

def main():
    print("="*80)
    print("🔍 TVS EXHAUSTIVE TOPIC TESTING")
    print("="*80)
    print(f"Broker: {HOST}:{PORT}")
    print(f"Username: {USERNAME}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Create client
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="topic-tester",
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

    try:
        print("\n🔗 Initial connection...")
        client.connect(HOST, PORT, 60)
        client.loop_start()
        time.sleep(2)  # Wait for connection

        if not connected:
            print("❌ Failed to establish initial connection")
            return

        # COMPREHENSIVE TOPIC LIST TO TEST
        topics_to_test = [
            # Primary target topic
            ("ati_fm/sherpa/status", "Primary ATI topic"),

            # Variations of ATI/sherpa
            ("ati/sherpa/status", "ATI without fm"),
            ("ati_fm/sherpa/#", "ATI sherpa wildcard"),
            ("ati_fm/#", "ATI fm wildcard"),
            ("ati/#", "ATI wildcard"),

            # Robotspace variations
            ("robotspace/sherpa/status", "Robotspace sherpa"),
            ("robotspace/#", "Robotspace wildcard"),
            ("robotspace/+/status", "Robotspace any status"),

            # AMR specific with MAC addresses
            ("amr/f4:7b:09:0e:04:1b/status", "Tug 133 MAC status"),
            ("amr/10:3d:1c:66:67:55/status", "Tug 39 MAC status"),
            ("amr/f4:4e:e3:f6:c7:91/status", "Tug 55 MAC status"),
            ("amr/ec:2e:98:4a:7c:f7/status", "Tug 78 MAC status"),

            # AMR with device names
            ("amr/tug133/status", "Tug 133 name status"),
            ("amr/tug39/status", "Tug 39 name status"),
            ("amr/tug55/status", "Tug 55 name status"),
            ("amr/tug78/status", "Tug 78 name status"),

            # Tug variations
            ("tug/133/status", "Tug 133 status"),
            ("tug/39/status", "Tug 39 status"),
            ("tug/55/status", "Tug 55 status"),
            ("tug/78/status", "Tug 78 status"),

            # Client ID based topics
            ("amr-001/status", "Client ID status"),
            ("amr-001/#", "Client ID wildcard"),
            ("clients/amr-001/#", "Clients path"),

            # Fleet topics
            ("fleet/tuggers/status", "Fleet tuggers"),
            ("fleet/amr/status", "Fleet AMR"),
            ("fleet/status", "Fleet status"),

            # TVS specific
            ("tvs/amr/status", "TVS AMR status"),
            ("tvs/tuggers/status", "TVS tuggers"),
            ("tvs/fleet/status", "TVS fleet"),

            # Position/location topics
            ("amr/+/position", "AMR position"),
            ("amr/+/location", "AMR location"),
            ("tug/+/position", "Tug position"),
            ("tug/+/location", "Tug location"),

            # Data/telemetry topics
            ("amr/+/data", "AMR data"),
            ("amr/+/telemetry", "AMR telemetry"),
            ("tug/+/data", "Tug data"),
            ("tug/+/telemetry", "Tug telemetry"),

            # Sherpa variations
            ("sherpa/status", "Sherpa status direct"),
            ("sherpa/#", "Sherpa wildcard"),
            ("+/sherpa/status", "Any sherpa status"),

            # System topics (less likely but worth trying)
            ("$SYS/broker/clients/connected", "System connected clients"),
            ("$SYS/broker/version", "System version"),

            # Minimal wildcards
            ("+/status", "Any status"),
            ("+/position", "Any position"),
            ("+/+", "Two level wildcard"),
            ("+", "Single level wildcard"),
        ]

        print(f"\n📋 Testing {len(topics_to_test)} topic variations...")
        print("="*80)

        for topic, description in topics_to_test:
            if not connected:
                print("\n🔄 Reconnecting...")
                client.reconnect()
                time.sleep(2)

            test_topic_subscription(client, topic, description)

            # Wait a bit between tests
            time.sleep(1)

        # If we found successful subscriptions, wait for messages
        if successful_subscriptions:
            print("\n✅ SUCCESSFUL SUBSCRIPTIONS:")
            for topic, desc in successful_subscriptions:
                print(f"   • {topic}: {desc}")

            print("\n⏱️  Waiting 30 seconds for messages...")
            time.sleep(30)

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")

    # FINAL REPORT
    print("\n" + "="*80)
    print("📊 FINAL REPORT")
    print("="*80)

    print(f"\n✅ SUCCESSFUL SUBSCRIPTIONS ({len(successful_subscriptions)}):")
    if successful_subscriptions:
        for topic, desc in successful_subscriptions:
            print(f"   • {topic}: {desc}")
    else:
        print("   None - all subscriptions were rejected")

    print(f"\n❌ FAILED SUBSCRIPTIONS ({len(failed_subscriptions)}):")
    if len(failed_subscriptions) <= 10:
        for topic, desc in failed_subscriptions:
            print(f"   • {topic}: {desc}")
    else:
        print(f"   {len(failed_subscriptions)} topics failed (too many to list)")

    print(f"\n📦 MESSAGES RECEIVED:")
    if messages_received:
        for topic, messages in messages_received.items():
            print(f"   • {topic}: {len(messages)} messages")
            if messages and len(str(messages[0])) < 200:
                print(f"     Sample: {messages[0]}")
    else:
        print("   No messages received on any topic")

    print("\n🎯 CONCLUSIONS:")
    if successful_subscriptions and messages_received:
        print("   ✅ SUCCESS! Found working topics with data")
    elif successful_subscriptions:
        print("   ⚠️  Can subscribe to some topics but no data received")
        print("   → AMRs may be offline or not publishing")
    else:
        print("   ❌ Cannot subscribe to any topics")
        print("   → Need different credentials or permission changes")

    print("="*80)

if __name__ == "__main__":
    main()