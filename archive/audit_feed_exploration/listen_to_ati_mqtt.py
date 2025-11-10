#!/usr/bin/env python3
"""
Simple MQTT listener to see what's actually being published on ATI broker
"""
import ssl
import json
import time
from paho.mqtt import client as mqtt

# ATI MQTT Configuration
ATI_HOST = "tvs-dev.ifactory.ai"
ATI_PORT = 8883
ATI_USERNAME = "amr-001"
ATI_PASSWORD = "TVSamr001@2025"
ATI_CLIENT_ID = "ati-listener"

message_count = 0

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n{'='*70}")
    print(f"CONNECTED TO ATI MQTT BROKER")
    print(f"{'='*70}")
    print(f"Result code: {rc}")
    if rc == 0:
        print("OK Connection successful!")
        # Subscribe to ALL topics
        client.subscribe("#", qos=2)
        print("Subscribed to ALL topics (#) with QoS 2")
        print("Waiting for messages...")
    else:
        print(f"FAIL Connection failed with code {rc}")
    print(f"{'='*70}\n")

def on_message(client, userdata, msg):
    global message_count
    message_count += 1

    print(f"\n{'='*70}")
    print(f"MESSAGE #{message_count}")
    print(f"{'='*70}")
    print(f"Topic: {msg.topic}")
    print(f"QoS: {msg.qos}")
    print(f"Retain: {msg.retain}")
    print(f"Payload length: {len(msg.payload)} bytes")
    print(f"\nRaw payload (first 1000 chars):")
    print(msg.payload[:1000])

    # Try to parse as JSON
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"\nParsed JSON:")
        print(json.dumps(payload, indent=2))
    except:
        print(f"\nNot JSON or decode failed")
        print(f"Attempting UTF-8 decode:")
        try:
            print(msg.payload.decode("utf-8")[:1000])
        except:
            print("Cannot decode as UTF-8")

    print(f"{'='*70}\n")

    # Save to file
    with open("ati_messages.log", "a", encoding="utf-8") as f:
        f.write(f"\n{'='*70}\n")
        f.write(f"MESSAGE #{message_count} - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*70}\n")
        f.write(f"Topic: {msg.topic}\n")
        f.write(f"Payload: {msg.payload}\n")
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            f.write(f"JSON:\n{json.dumps(payload, indent=2)}\n")
        except:
            pass
        f.write(f"{'='*70}\n\n")

def on_disconnect(client, userdata, flags, rc, properties=None):
    print(f"\nDISCONNECTED (code: {rc})")

def main():
    print(f"\n{'='*70}")
    print(f"ATI MQTT LISTENER")
    print(f"{'='*70}")
    print(f"Broker: {ATI_HOST}:{ATI_PORT}")
    print(f"Client ID: {ATI_CLIENT_ID}")
    print(f"Username: {ATI_USERNAME}")
    print(f"Subscribing to: ALL topics (#)")
    print(f"Log file: ati_messages.log")
    print(f"{'='*70}\n")

    # Clear log file
    with open("ati_messages.log", "w", encoding="utf-8") as f:
        f.write(f"ATI MQTT Messages Log - Started {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Create MQTT client
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=ATI_CLIENT_ID,
        protocol=mqtt.MQTTv5
    )
    client.username_pw_set(ATI_USERNAME, ATI_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print("Connecting...")
    try:
        client.connect(ATI_HOST, ATI_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        client.disconnect()
        print(f"Total messages received: {message_count}")
        print("OK Listener stopped")

if __name__ == "__main__":
    main()
