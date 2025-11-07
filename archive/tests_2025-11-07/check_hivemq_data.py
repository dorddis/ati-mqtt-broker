#!/usr/bin/env python3
"""
Check if HiveMQ server is receiving any AMR data
"""
import json
import ssl
import paho.mqtt.client as mqtt
import time

# Load HiveMQ config
with open("config/hivemq_config.json", "r") as f:
    config = json.load(f)

HOST = config["connection"]["host"]
PORT = config["connection"]["port"]
USERNAME = config["credentials"]["username"]
PASSWORD = config["credentials"]["password"]

print("="*70)
print("CHECKING HIVEMQ SERVER FOR INCOMING DATA")
print("="*70)
print(f"Host: {HOST}")
print(f"Port: {PORT}")
print(f"Topics: {config['topics']['amr_positions']}, {config['topics']['amr_status']}")
print("="*70)

messages_received = []

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("\n✓ Connected to HiveMQ Cloud!")
        print("  Subscribing to all AMR topics...")
        client.subscribe("hitech/amr/#", qos=1)
        client.subscribe("test/#", qos=1)
        print("  Listening for messages (30 seconds)...\n")
    else:
        print(f"\n✗ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    messages_received.append(msg)
    print(f"\n→ Message received!")
    print(f"  Topic: {msg.topic}")
    print(f"  Payload: {msg.payload.decode('utf-8', errors='replace')[:200]}")

# Create client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "hivemq_checker")
client.username_pw_set(USERNAME, PASSWORD)

# Enable TLS
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

# Set callbacks
client.on_connect = on_connect
client.on_message = on_message

try:
    print("\nConnecting...")
    client.connect(HOST, PORT, keepalive=60)
    client.loop_start()

    # Wait for messages
    time.sleep(30)

    client.loop_stop()
    client.disconnect()

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    if len(messages_received) == 0:
        print("\n✗ NO MESSAGES RECEIVED")
        print("\nPossible reasons:")
        print("  1. No AMRs are publishing to this HiveMQ broker yet")
        print("  2. AMRs are publishing to different topics")
        print("  3. HiveMQ credentials may have changed")
        print("\nAction: Wait for HiTech team to configure their AMRs")
    else:
        print(f"\n✓ Received {len(messages_received)} message(s)!")
        print("\nTopics with data:")
        topics = set([msg.topic for msg in messages_received])
        for topic in topics:
            count = len([m for m in messages_received if m.topic == topic])
            print(f"  - {topic}: {count} messages")

except Exception as e:
    print(f"\n✗ Error: {e}")
