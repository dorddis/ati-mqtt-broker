#!/usr/bin/env python3
"""
Quick TVS Data Check - Simple and direct
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
from datetime import datetime

# Configuration
HOST = "tvs-dev.ifactory.ai"
PORT = 8883
USERNAME = "amr-001"
PASSWORD = "TVSamr001@2025"

message_count = 0

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Connected at {datetime.now().strftime('%H:%M:%S')}")
        # Subscribe to EVERYTHING
        client.subscribe("#", qos=1)
        print("📡 Subscribed to # (all topics)")
    else:
        print(f"❌ Connection failed: {rc}")

def on_message(client, userdata, msg):
    global message_count
    message_count += 1

    print(f"\n🎉 MESSAGE #{message_count} RECEIVED!")
    print(f"Topic: {msg.topic}")
    print(f"QoS: {msg.qos}, Retain: {msg.retain}")
    print(f"Timestamp: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

    # Try to decode payload
    try:
        payload = msg.payload.decode('utf-8')
        print(f"Payload length: {len(payload)} bytes")

        # Try to parse as JSON
        try:
            data = json.loads(payload)
            print("JSON Data:")
            print(json.dumps(data, indent=2))
        except:
            # Not JSON, show raw
            if len(payload) < 500:
                print(f"Raw data: {payload}")
            else:
                print(f"Raw data (truncated): {payload[:500]}...")
    except:
        print(f"Binary payload: {msg.payload.hex()[:100]}...")

    print("-" * 60)

def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
    print(f"\n🔌 Disconnected at {datetime.now().strftime('%H:%M:%S')}")
    if reasonCode:
        print(f"Reason: {reasonCode}")

def main():
    print("="*60)
    print("🚀 TVS QUICK DATA CHECK")
    print("="*60)
    print(f"Broker: {HOST}:{PORT}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Create client
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="quick-check",
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
    client.on_disconnect = on_disconnect

    try:
        print("🔗 Connecting...")
        client.connect(HOST, PORT, 60)

        # Run for 2 minutes
        print("⏱️  Listening for 2 minutes...")
        print("="*60)

        client.loop_start()

        # Check every 10 seconds
        for i in range(12):
            time.sleep(10)
            if message_count == 0:
                print(f"⏳ {(i+1)*10} seconds elapsed... No messages yet")
            else:
                print(f"📦 {(i+1)*10} seconds elapsed... {message_count} messages received!")

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*60)
    print(f"📊 FINAL RESULT: {message_count} messages received")
    if message_count > 0:
        print("✅ SUCCESS - Data is flowing!")
    else:
        print("❌ NO DATA - AMRs may still be offline")
    print("="*60)

if __name__ == "__main__":
    main()