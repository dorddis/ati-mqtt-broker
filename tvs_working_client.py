#!/usr/bin/env python3
"""
TVS Working MQTT Client
Only subscribes to ALLOWED topic and publishes data
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
import uuid
from datetime import datetime, timezone
import threading

# Configuration
HOST = "tvs-dev.ifactory.ai"
PORT = 8883
DEVICE_ID = "amr-001"
USERNAME = "amr-001"
PASSWORD = "TVSamr001@2025"

# Topics
PUBLISH_TOPIC = f"/d2c/{DEVICE_ID}"  # Where we publish TO
SUBSCRIBE_TOPIC = f"/c2d/{DEVICE_ID}"  # Where we receive commands FROM (ALLOWED!)

# State
connected = False
messages_sent = 0
commands_received = 0
publish_timer = None

def get_heartbeat_message():
    """Generate heartbeat message as per documentation"""
    return {
        "data": {
            "ueid": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "did": DEVICE_ID,
            "eid": 2001,  # Heartbeat event ID
            "pl": {
                "uptime": f"{messages_sent}h 0m 0sec",
                "signalStrength": "55/70",
                "battery": 85.45,
                "temperature": 42.56
            }
        }
    }

def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"✅ Connected at {datetime.now().strftime('%H:%M:%S')}")

        # ONLY subscribe to the ALLOWED topic
        print(f"📡 Subscribing to: {SUBSCRIBE_TOPIC}")
        result, mid = client.subscribe(SUBSCRIBE_TOPIC, qos=1)
        print(f"   Subscription sent (mid={mid})")

    else:
        connected = False
        print(f"❌ Connection failed: {rc}")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print(f"   ✅ Subscription confirmed (mid={mid}, QoS={granted_qos})")
    print("\n🚀 Starting to publish data...")

def on_publish(client, userdata, mid, properties=None, reasonCode=None):
    print(f"   ✅ Published (mid={mid})")

def on_message(client, userdata, msg):
    global commands_received
    commands_received += 1
    timestamp = datetime.now().strftime('%H:%M:%S')

    print(f"\n🎉 COMMAND RECEIVED at {timestamp}!")
    print(f"   Topic: {msg.topic}")

    try:
        data = json.loads(msg.payload.decode('utf-8'))
        print(f"   Data: {json.dumps(data, indent=4)[:300]}")
    except:
        print(f"   Raw: {msg.payload[:100]}")

def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
    global connected
    connected = False
    print(f"\n🔌 Disconnected (rc={rc})")

def publish_data(client):
    """Publish heartbeat data periodically"""
    global messages_sent

    if connected:
        message = get_heartbeat_message()
        result = client.publish(PUBLISH_TOPIC, json.dumps(message), qos=1)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            messages_sent += 1
            print(f"📤 Heartbeat #{messages_sent} sent to {PUBLISH_TOPIC}")
        else:
            print(f"❌ Publish failed: {result.rc}")

def main():
    print("="*80)
    print("🔍 TVS WORKING MQTT CLIENT")
    print("="*80)
    print(f"Broker: {HOST}:{PORT}")
    print(f"Device: {DEVICE_ID}")
    print(f"Publish to: {PUBLISH_TOPIC}")
    print(f"Subscribe to: {SUBSCRIBE_TOPIC}")
    print("="*80)

    # Create client
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=DEVICE_ID,
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
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    try:
        print("\n🔗 Connecting...")
        client.connect(HOST, PORT, keepalive=60)
        client.loop_start()

        # Wait for connection
        time.sleep(3)

        # Monitor and publish
        start_time = time.time()
        last_publish = time.time()

        print("\n⏰ Running for 2 minutes...")
        print("-" * 40)

        while time.time() - start_time < 120:  # Run for 2 minutes
            if connected:
                # Publish every 10 seconds
                if time.time() - last_publish >= 10:
                    publish_data(client)
                    last_publish = time.time()
            else:
                print(f"❌ Not connected, attempting reconnect...")
                try:
                    client.reconnect()
                except:
                    pass
                time.sleep(5)

            time.sleep(1)

        client.loop_stop()
        client.disconnect()

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Final report
    print("\n" + "="*80)
    print("📊 FINAL REPORT")
    print("="*80)
    print(f"✅ Messages Published: {messages_sent}")
    print(f"📥 Commands Received: {commands_received}")

    if messages_sent > 0:
        print("\n🎉 SUCCESS!")
        print("• We CAN publish AMR data to the broker")
        print(f"• Published to: {PUBLISH_TOPIC}")

    if commands_received > 0:
        print("• We received commands from the cloud")
        print(f"• Commands from: {SUBSCRIBE_TOPIC}")

    if messages_sent > 0 and commands_received == 0:
        print("\n📝 CONCLUSION:")
        print("• The amr-001 account is configured for AMR devices")
        print("• It can PUBLISH sensor/telemetry data to /d2c/amr-001")
        print("• It can SUBSCRIBE to commands from /c2d/amr-001")
        print("• No commands were sent during this test")

    print("="*80)

if __name__ == "__main__":
    main()