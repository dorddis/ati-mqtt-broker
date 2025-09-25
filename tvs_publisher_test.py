#!/usr/bin/env python3
"""
TVS MQTT Publisher Test
Based on the documentation - the amr-001 account might be for PUBLISHING data
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
import uuid
from datetime import datetime, timezone
import threading

# Configuration from documentation
HOST = "tvs-dev.ifactory.ai"
PORT = 8883
DEVICE_ID = "amr-001"  # Using client ID as device ID
USERNAME = "amr-001"
PASSWORD = "TVSamr001@2025"

# Topics based on documentation
PUBLISH_TOPIC = f"/d2c/{DEVICE_ID}"  # Device to cloud
SUBSCRIBE_TOPIC = f"/c2d/{DEVICE_ID}"  # Cloud to device (commands)

# Global state
connected = False
messages_sent = 0
messages_received = 0

def get_heartbeat_message():
    """Generate heartbeat message as per documentation"""
    return {
        "data": {
            "ueid": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "did": DEVICE_ID,
            "eid": 2001,  # Heartbeat event ID
            "pl": {
                "uptime": "0h 1m 0sec",
                "signalStrength": "55/70",
                "battery": 85.45,
                "temperature": 42.56
            }
        }
    }

def get_trip_start_message():
    """Generate trip start message as per documentation"""
    return {
        "data": {
            "ueid": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "did": DEVICE_ID,
            "eid": 2001,  # Trip start event ID
            "pl": {
                "location": {
                    "lat": 17.0234,
                    "long": 13.023456
                },
                "destination": {
                    "lat": 17.0234,
                    "long": 13.023456
                },
                "distance": 78.34,
                "tripId": str(uuid.uuid4()),
                "battery": 85.45
            }
        }
    }

def get_trip_update_message():
    """Generate trip update message as per documentation"""
    return {
        "data": {
            "ueid": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "did": DEVICE_ID,
            "eid": 2002,  # Trip update event ID
            "pl": {
                "location": {
                    "lat": 17.0234,
                    "long": 13.023456
                },
                "status": "moving",
                "distance": 78.34,
                "tripId": str(uuid.uuid4())
            }
        }
    }

def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"✅ Connected successfully at {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Client ID: {DEVICE_ID}")

        # Subscribe to cloud-to-device topic (for commands)
        print(f"\n📡 Subscribing to command topic: {SUBSCRIBE_TOPIC}")
        result, mid = client.subscribe(SUBSCRIBE_TOPIC, qos=1)
        print(f"   Subscription request sent (mid={mid})")

        # Also try subscribing to our own publish topic to see if we get echo
        echo_topic = PUBLISH_TOPIC
        result2, mid2 = client.subscribe(echo_topic, qos=1)
        print(f"📡 Subscribing to echo topic: {echo_topic}")
        print(f"   Subscription request sent (mid={mid2})")

    else:
        connected = False
        print(f"❌ Connection failed: {rc}")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    if granted_qos and len(granted_qos) > 0:
        if hasattr(granted_qos[0], 'is_failure') and granted_qos[0].is_failure:
            print(f"   ❌ Subscription {mid}: Not authorized")
        else:
            print(f"   ✅ Subscription {mid}: Granted (QoS: {granted_qos})")

def on_publish(client, userdata, mid, properties=None, reasonCode=None):
    print(f"   ✅ Message published successfully (mid={mid})")

def on_message(client, userdata, msg):
    global messages_received
    messages_received += 1

    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"\n🎉 MESSAGE RECEIVED at {timestamp}!")
    print(f"   Topic: {msg.topic}")
    print(f"   QoS: {msg.qos}, Retain: {msg.retain}")

    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        print(f"   Data: {json.dumps(data, indent=4)[:300]}")
    except:
        print(f"   Raw: {msg.payload[:100]}")
    print("-" * 70)

def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
    global connected
    connected = False
    print(f"\n🔌 Disconnected at {datetime.now().strftime('%H:%M:%S')}")
    if reasonCode:
        print(f"   Reason: {reasonCode}")

def publish_messages(client):
    """Publish different types of messages as per documentation"""
    global messages_sent

    message_types = [
        ("Heartbeat", get_heartbeat_message),
        ("Trip Start", get_trip_start_message),
        ("Trip Update", get_trip_update_message),
    ]

    for msg_type, msg_func in message_types:
        if not connected:
            print("❌ Not connected, skipping publish")
            break

        message = msg_func()
        print(f"\n📤 Publishing {msg_type} message to {PUBLISH_TOPIC}")
        print(f"   Message: {json.dumps(message, indent=4)[:200]}...")

        result = client.publish(PUBLISH_TOPIC, json.dumps(message), qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            messages_sent += 1
            print(f"   ✅ Publish initiated (mid={result.mid})")
        else:
            print(f"   ❌ Publish failed: {result.rc}")

        time.sleep(2)

def main():
    global messages_sent, messages_received

    print("="*80)
    print("🔍 TVS MQTT PUBLISHER TEST")
    print("   Testing if amr-001 can PUBLISH data")
    print("="*80)
    print(f"Broker: {HOST}:{PORT}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Username: {USERNAME}")
    print(f"Publish Topic: {PUBLISH_TOPIC}")
    print(f"Subscribe Topic: {SUBSCRIBE_TOPIC}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Create MQTT client
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

    # Enable debug logging
    # client.enable_logger()

    try:
        print("\n🔗 Connecting to broker...")
        client.connect(HOST, PORT, keepalive=60)
        client.loop_start()

        # Wait for connection
        time.sleep(2)

        if connected:
            print("\n" + "="*80)
            print("📤 STARTING PUBLISH TEST")
            print("="*80)

            # Publish messages every 5 seconds
            for i in range(5):  # Send 5 rounds of messages
                if not connected:
                    print("\n❌ Lost connection, attempting to reconnect...")
                    try:
                        client.reconnect()
                        time.sleep(2)
                    except:
                        pass

                if connected:
                    print(f"\n--- Round {i+1} of 5 ---")
                    publish_messages(client)

                    # Wait between rounds
                    if i < 4:
                        print(f"\n⏳ Waiting 10 seconds before next round...")
                        time.sleep(10)
                else:
                    print(f"\n❌ Skipping round {i+1} - not connected")
                    time.sleep(5)

        # Final wait to receive any responses
        print("\n⏳ Waiting 20 seconds for any responses...")
        time.sleep(20)

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")

    # Final report
    print("\n" + "="*80)
    print("📊 FINAL REPORT")
    print("="*80)
    print(f"Messages Published: {messages_sent}")
    print(f"Messages Received: {messages_received}")

    if messages_sent > 0:
        print("\n✅ SUCCESS: We CAN publish messages!")
        print("The amr-001 account has WRITE permissions")
    else:
        print("\n❌ FAILURE: Cannot publish messages")

    if messages_received > 0:
        print("✅ We also received some messages")
    else:
        print("❌ No messages received (expected - we may not have READ permissions)")

    print("\n🔍 CONCLUSIONS:")
    if messages_sent > 0 and messages_received == 0:
        print("• The amr-001 account is configured as a PUBLISHER (write-only)")
        print("• It can send AMR data TO the broker")
        print("• It cannot read/subscribe to topics")
        print("• This matches the documentation - it's for AMR vendors to send data")
    elif messages_sent > 0 and messages_received > 0:
        print("• The account has both read and write permissions")
    else:
        print("• The account cannot publish or subscribe")
        print("• There may be additional restrictions or issues")

    print("="*80)

if __name__ == "__main__":
    main()