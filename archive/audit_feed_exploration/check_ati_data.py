#!/usr/bin/env python3
"""
Simple ATI MQTT Listener - Check what data is being published

Connects to ATI MQTTS broker and logs all incoming messages to console and file.
"""
import json
import ssl
import time
from datetime import datetime
from paho.mqtt import client as mqtt

# ATI Configuration
ATI_HOST = "tvs-dev.ifactory.ai"
ATI_PORT = 8883
ATI_USERNAME = "amr-001"
ATI_PASSWORD = "TVSamr001@2025"
ATI_CLIENT_ID = "amr-001-listener"
ATI_TOPIC = "ati_fm/sherpa/status"

message_count = 0
log_file = "ati_data_received.log"

def on_connect(client, userdata, flags, rc, properties=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if rc == 0:
        print(f"[{timestamp}] CONNECTED to ATI MQTTS broker")
        print(f"[{timestamp}] Subscribing to: {ATI_TOPIC}")
        client.subscribe(ATI_TOPIC, qos=2)
        print(f"[{timestamp}] Waiting for messages...\n")
        print("="*80)
    else:
        print(f"[{timestamp}] CONNECTION FAILED with code {rc}")

def on_disconnect(client, userdata, flags, rc, properties=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] DISCONNECTED (rc={rc})")

def on_message(client, userdata, msg):
    global message_count
    message_count += 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    print(f"\n{'='*80}")
    print(f"MESSAGE #{message_count} at {timestamp}")
    print(f"{'='*80}")
    print(f"Topic: {msg.topic}")

    try:
        # Try to parse as JSON
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"\nParsed JSON:")
        print(json.dumps(payload, indent=2))

        # Extract key fields
        print(f"\nKey Fields:")
        print(f"  sherpa_name: {payload.get('sherpa_name', 'NOT FOUND')}")
        print(f"  pose: {payload.get('pose', 'NOT FOUND')}")
        print(f"  battery_status: {payload.get('battery_status', 'NOT FOUND')}")
        print(f"  mode: {payload.get('mode', 'NOT FOUND')}")

        # Log to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"MESSAGE #{message_count} at {timestamp}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Topic: {msg.topic}\n")
            f.write(f"JSON:\n{json.dumps(payload, indent=2)}\n")

    except json.JSONDecodeError:
        # Not JSON, print raw
        print(f"\nRaw Payload (not JSON):")
        print(msg.payload.decode("utf-8", errors="replace"))

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"MESSAGE #{message_count} at {timestamp}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Topic: {msg.topic}\n")
            f.write(f"Raw: {msg.payload.decode('utf-8', errors='replace')}\n")

    print(f"{'='*80}\n")
    print(f"Total messages received: {message_count}")
    print(f"Logged to: {log_file}")
    print("="*80)

def main():
    print("="*80)
    print("ATI MQTT Data Checker")
    print("="*80)
    print(f"Broker: {ATI_HOST}:{ATI_PORT}")
    print(f"Topic: {ATI_TOPIC}")
    print(f"Client ID: {ATI_CLIENT_ID}")
    print(f"Log file: {log_file}")
    print("="*80)
    print("\nPress Ctrl+C to stop\n")

    # Clear log file
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"ATI MQTT Data Log - Started {datetime.now()}\n")
        f.write(f"Broker: {ATI_HOST}:{ATI_PORT}\n")
        f.write(f"Topic: {ATI_TOPIC}\n")
        f.write("="*80 + "\n")

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
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        print("Connecting...")
        client.connect(ATI_HOST, ATI_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\nStopping...")
        client.disconnect()
        print(f"\nTotal messages received: {message_count}")
        print(f"Log saved to: {log_file}")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
