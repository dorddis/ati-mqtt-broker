#!/usr/bin/env python3
"""
TVS Connection Test with Unique Client ID
Testing if multiple connections are causing the issue
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
import random
from datetime import datetime

# Configuration
HOST = "tvs-dev.ifactory.ai"
PORT = 8883
USERNAME = "amr-001"
PASSWORD = "TVSamr001@2025"

# Generate unique client ID to avoid conflicts
UNIQUE_ID = f"tvs-test-{random.randint(1000, 9999)}-{int(time.time())}"

message_count = 0
connected = False

def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"✅ Connected successfully!")
        print(f"   Client ID: {UNIQUE_ID}")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

        # Try different subscription approaches
        topics = [
            ("#", 0),           # All topics, QoS 0
            ("#", 1),           # All topics, QoS 1
            ("$SYS/#", 0),      # System topics
            ("+/+/+", 1),       # Three-level wildcard
            ("amr/#", 1),       # AMR specific
            ("tug/#", 1),       # Tug specific
        ]

        for topic, qos in topics:
            result = client.subscribe(topic, qos)
            print(f"   📡 Subscribing to '{topic}' QoS {qos}: {result}")
    else:
        connected = False
        print(f"❌ Connection failed: {rc}")
        error_messages = {
            1: "Incorrect protocol version",
            2: "Invalid client identifier",
            3: "Server unavailable",
            4: "Bad username or password",
            5: "Not authorized"
        }
        print(f"   Error: {error_messages.get(rc, 'Unknown error')}")

def on_message(client, userdata, msg):
    global message_count
    message_count += 1

    print(f"\n🎉 MESSAGE RECEIVED! #{message_count}")
    print(f"Topic: {msg.topic}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    print(f"QoS: {msg.qos}, Retain: {msg.retain}")

    try:
        payload = msg.payload.decode('utf-8')
        print(f"Payload ({len(payload)} bytes):")

        try:
            data = json.loads(payload)
            print(json.dumps(data, indent=2))
        except:
            if len(payload) < 200:
                print(payload)
            else:
                print(payload[:200] + "...")
    except:
        print(f"Binary: {msg.payload.hex()[:100]}...")

    print("-" * 60)

def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
    global connected
    connected = False
    print(f"\n🔌 Disconnected at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    print(f"   Return code: {rc}")
    if reasonCode:
        print(f"   Reason: {reasonCode}")
    if properties:
        print(f"   Properties: {properties}")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print(f"   ✅ Subscription confirmed: MID={mid}, QoS={granted_qos}")

def main():
    global message_count, connected

    print("="*70)
    print("🔍 TVS CONNECTION TEST WITH UNIQUE CLIENT ID")
    print("="*70)
    print(f"Broker: {HOST}:{PORT}")
    print(f"Username: {USERNAME}")
    print(f"Client ID: {UNIQUE_ID}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Create client with unique ID
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=UNIQUE_ID,
        protocol=mqtt.MQTTv5
    )

    # Set username/password
    client.username_pw_set(USERNAME, PASSWORD)

    # Configure TLS
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    client.tls_set_context(context)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    # Enable detailed logging
    client.enable_logger()

    try:
        print("\n🔗 Attempting connection...")
        client.connect(HOST, PORT, keepalive=60)

        # Start the loop
        client.loop_start()

        # Monitor for 3 minutes
        start_time = time.time()
        last_status = time.time()

        while time.time() - start_time < 180:  # 3 minutes
            time.sleep(1)

            # Status update every 15 seconds
            if time.time() - last_status >= 15:
                elapsed = int(time.time() - start_time)
                if connected:
                    if message_count > 0:
                        print(f"✅ [{elapsed}s] Connected - {message_count} messages received")
                    else:
                        print(f"⏳ [{elapsed}s] Connected - Waiting for messages...")
                else:
                    print(f"❌ [{elapsed}s] Not connected")
                last_status = time.time()

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*70)
    print("📊 FINAL RESULTS")
    print("="*70)
    print(f"Total messages received: {message_count}")
    if message_count > 0:
        print("✅ SUCCESS - Data detected!")
    else:
        print("❌ NO DATA DETECTED")
        print("\nPossible reasons:")
        print("• AMRs not publishing data")
        print("• Wrong topics subscribed")
        print("• Access restrictions on this account")
        print("• Data published to different broker/port")
    print("="*70)

if __name__ == "__main__":
    main()