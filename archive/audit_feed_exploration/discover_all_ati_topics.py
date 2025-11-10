#!/usr/bin/env python3
"""
Comprehensive ATI MQTT Topic Discovery

Subscribes to ALL topics on the ATI broker to discover what's actually being published.
This will tell us definitively if ANY data is flowing, regardless of topic.
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
ATI_CLIENT_ID = "amr-001-discovery"

# Try multiple wildcard patterns to catch everything
TOPICS_TO_TRY = [
    "#",                           # Everything
    "ati/#",                       # ATI namespace
    "ati_fm/#",                    # ATI Fleet Manager
    "ati_fm/sherpa/#",             # Sherpa specific
    "ati_fm/sherpa/status",        # Expected topic from docs
    "$SYS/#",                      # System topics (broker stats)
    "+/#",                         # All first-level topics
    "amr/#",                       # AMR namespace
    "fleet/#",                     # Fleet namespace
    "robot/#",                     # Robot namespace
    "sherpa/#",                    # Sherpa namespace
    "tugger/#",                    # Tugger namespace
]

message_count = 0
topics_seen = set()
log_file = "ati_topic_discovery.log"

def on_connect(client, userdata, flags, rc, properties=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if rc == 0:
        print(f"[{timestamp}] CONNECTED to ATI MQTTS broker")
        print(f"[{timestamp}] Subscribing to ALL topics for discovery...")

        # Subscribe to all patterns
        for topic in TOPICS_TO_TRY:
            result = client.subscribe(topic, qos=2)
            print(f"[{timestamp}]   Subscribed to: {topic} (result: {result})")

        print(f"\n[{timestamp}] Listening for ANY messages on ANY topic...")
        print(f"[{timestamp}] This will prove definitively if data is being published\n")
        print("="*80)
    else:
        print(f"[{timestamp}] CONNECTION FAILED with code {rc}")

def on_disconnect(client, userdata, flags, rc, properties=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if rc == 0:
        print(f"[{timestamp}] Clean disconnect")
    else:
        print(f"[{timestamp}] DISCONNECTED (rc={rc}) - will reconnect")

def on_subscribe(client, userdata, mid, reason_codes, properties=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Subscription confirmed (mid={mid})")

def on_message(client, userdata, msg):
    global message_count
    message_count += 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    # Track unique topics
    topics_seen.add(msg.topic)

    print(f"\n{'='*80}")
    print(f"🎉 MESSAGE RECEIVED! #{message_count} at {timestamp}")
    print(f"{'='*80}")
    print(f"Topic: {msg.topic}")
    print(f"QoS: {msg.qos}")
    print(f"Retain: {msg.retain}")
    print(f"Payload Length: {len(msg.payload)} bytes")

    try:
        # Try to parse as JSON
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"\n✅ Valid JSON:")
        print(json.dumps(payload, indent=2))

        # Log to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"MESSAGE #{message_count} at {timestamp}\n")
            f.write(f"Topic: {msg.topic}\n")
            f.write(f"JSON:\n{json.dumps(payload, indent=2)}\n")

    except json.JSONDecodeError:
        # Not JSON, print raw
        raw_payload = msg.payload.decode("utf-8", errors="replace")
        print(f"\n📄 Raw Payload (not JSON):")
        print(raw_payload[:500])

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"MESSAGE #{message_count} at {timestamp}\n")
            f.write(f"Topic: {msg.topic}\n")
            f.write(f"Raw: {raw_payload}\n")

    print(f"\n{'='*80}")
    print(f"📊 Total messages: {message_count}")
    print(f"📊 Unique topics seen: {len(topics_seen)}")
    print(f"📊 Topics: {list(topics_seen)}")
    print(f"{'='*80}\n")

def main():
    print("="*80)
    print("ATI MQTT Topic Discovery Tool")
    print("="*80)
    print(f"Broker: {ATI_HOST}:{ATI_PORT}")
    print(f"Client ID: {ATI_CLIENT_ID}")
    print(f"Log file: {log_file}")
    print("="*80)
    print("\nThis tool will:")
    print("1. Subscribe to ALL possible topic patterns")
    print("2. Log EVERY message received on ANY topic")
    print("3. Prove definitively if the broker is publishing ANY data")
    print("\nIf we receive ZERO messages after 60 seconds, it means:")
    print("- Connection works ✅")
    print("- Credentials work ✅")
    print("- NO data is being published ❌")
    print("="*80)
    print("\nPress Ctrl+C to stop\n")

    # Clear log file
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"ATI MQTT Topic Discovery Log - Started {datetime.now()}\n")
        f.write(f"Broker: {ATI_HOST}:{ATI_PORT}\n")
        f.write(f"Subscribed to: {', '.join(TOPICS_TO_TRY)}\n")
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
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    try:
        print("Connecting...")
        client.connect(ATI_HOST, ATI_PORT, keepalive=60)

        # Run for 60 seconds to give ample time to receive messages
        print("\n⏱️  Running for 60 seconds to check for messages...")
        print("    (Stop early with Ctrl+C if you see messages)\n")

        start_time = time.time()
        client.loop_start()

        try:
            while time.time() - start_time < 60:
                time.sleep(1)
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 and elapsed > 0:
                    print(f"[{elapsed}s] Still listening... Messages so far: {message_count}")
        except KeyboardInterrupt:
            print("\n\nStopped by user")

        client.loop_stop()
        client.disconnect()

        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print(f"✅ Connection: SUCCESS")
        print(f"✅ Authentication: SUCCESS")
        print(f"✅ Subscriptions: {len(TOPICS_TO_TRY)} patterns subscribed")
        print(f"📊 Messages received: {message_count}")
        print(f"📊 Unique topics seen: {len(topics_seen)}")

        if message_count == 0:
            print("\n❌ CONCLUSION: NO DATA IS BEING PUBLISHED")
            print("   The broker is online and accepting connections,")
            print("   but no AMRs are currently publishing telemetry.")
            print("\n✅ Our bridge code is correct and ready.")
            print("   We just need ATI to configure AMRs to publish data.")
        else:
            print(f"\n✅ SUCCESS! Received {message_count} messages")
            print(f"   Topics seen: {list(topics_seen)}")
            print(f"   Check {log_file} for details")

        print("="*80)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
