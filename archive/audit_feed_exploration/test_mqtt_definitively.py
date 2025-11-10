#!/usr/bin/env python3
"""
DEFINITIVE MQTT CONNECTION TEST

This will prove:
1. Connection credentials work
2. Subscription is successful
3. But no data is being published

We'll use TWO clients:
- Client 1: Publisher (sends test messages)
- Client 2: Subscriber (receives messages)

If Client 2 receives messages from Client 1, but not from ATI AMRs,
then we KNOW the connection works and AMRs simply aren't publishing.
"""
import ssl
import time
import json
import threading
from paho.mqtt import client as mqtt

# ATI MQTT Configuration
ATI_HOST = "tvs-dev.ifactory.ai"
ATI_PORT = 8883
ATI_USERNAME = "amr-001"
ATI_PASSWORD = "TVSamr001@2025"

messages_received = []
test_message_received = False

def subscriber_thread():
    """Subscriber client - listens for ALL messages"""
    global messages_received, test_message_received

    def on_connect_sub(client, userdata, flags, rc, properties=None):
        print(f"\n[SUBSCRIBER] Connected with result code: {rc}")
        if rc == 0:
            print("[SUBSCRIBER] OK - Connection successful!")
            # Subscribe to ALL topics
            client.subscribe("#", qos=2)
            print("[SUBSCRIBER] Subscribed to ALL topics (#)")
        else:
            print(f"[SUBSCRIBER] FAIL - Connection failed: {rc}")

    def on_message_sub(client, userdata, msg):
        global messages_received, test_message_received
        timestamp = time.strftime('%H:%M:%S')

        # Check if it's our test message
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            if payload.get("test_id") == "DEFINITIVE_TEST":
                test_message_received = True
                print(f"\n[SUBSCRIBER] {timestamp} - ✅ RECEIVED OUR TEST MESSAGE!")
                print(f"             Topic: {msg.topic}")
                print(f"             Payload: {payload}")
                return
        except:
            pass

        # Not our test message - must be real AMR data!
        messages_received.append({
            "time": timestamp,
            "topic": msg.topic,
            "payload": str(msg.payload[:200])
        })
        print(f"\n[SUBSCRIBER] {timestamp} - 📨 MESSAGE RECEIVED FROM AMR!")
        print(f"             Topic: {msg.topic}")
        print(f"             Payload (first 200 bytes): {msg.payload[:200]}")

    def on_disconnect_sub(client, userdata, flags, rc, properties=None):
        print(f"\n[SUBSCRIBER] Disconnected (code: {rc})")

    # Create subscriber client
    sub_client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="test-subscriber",
        protocol=mqtt.MQTTv5
    )
    sub_client.username_pw_set(ATI_USERNAME, ATI_PASSWORD)
    sub_client.tls_set(cert_reqs=ssl.CERT_NONE)
    sub_client.tls_insecure_set(True)

    sub_client.on_connect = on_connect_sub
    sub_client.on_message = on_message_sub
    sub_client.on_disconnect = on_disconnect_sub

    print("[SUBSCRIBER] Connecting...")
    sub_client.connect(ATI_HOST, ATI_PORT, keepalive=60)
    sub_client.loop_forever()

def publisher_thread():
    """Publisher client - sends test messages"""
    time.sleep(3)  # Wait for subscriber to connect

    def on_connect_pub(client, userdata, flags, rc, properties=None):
        print(f"\n[PUBLISHER] Connected with result code: {rc}")
        if rc == 0:
            print("[PUBLISHER] OK - Connection successful!")
        else:
            print(f"[PUBLISHER] FAIL - Connection failed: {rc}")

    # Create publisher client
    pub_client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="test-publisher",
        protocol=mqtt.MQTTv5
    )
    pub_client.username_pw_set(ATI_USERNAME, ATI_PASSWORD)
    pub_client.tls_set(cert_reqs=ssl.CERT_NONE)
    pub_client.tls_insecure_set(True)

    pub_client.on_connect = on_connect_pub

    print("[PUBLISHER] Connecting...")
    pub_client.connect(ATI_HOST, ATI_PORT, keepalive=60)
    pub_client.loop_start()

    time.sleep(2)  # Wait for connection

    # Publish test message
    test_payload = {
        "test_id": "DEFINITIVE_TEST",
        "timestamp": time.time(),
        "message": "This is a test message to verify MQTT is working"
    }

    print("\n[PUBLISHER] Publishing test message to topic: test/connection")
    result = pub_client.publish("test/connection", json.dumps(test_payload), qos=2)
    print(f"[PUBLISHER] Publish result: {result.rc}")

    time.sleep(2)
    pub_client.loop_stop()
    pub_client.disconnect()

def main():
    print("="*70)
    print("DEFINITIVE MQTT CONNECTION TEST")
    print("="*70)
    print(f"Broker: {ATI_HOST}:{ATI_PORT}")
    print(f"Username: {ATI_USERNAME}")
    print("="*70)
    print("\nTHIS TEST WILL PROVE:")
    print("1. Connection credentials work ✓")
    print("2. We can publish messages ✓")
    print("3. We can receive messages ✓")
    print("4. BUT if no AMR data received = AMRs not publishing ✓")
    print("="*70)

    # Start subscriber in background thread
    sub_thread = threading.Thread(target=subscriber_thread, daemon=True)
    sub_thread.start()

    # Start publisher in background thread
    pub_thread = threading.Thread(target=publisher_thread, daemon=True)
    pub_thread.start()

    # Monitor for 30 seconds
    print("\n⏱️  Monitoring for 30 seconds...")
    print("="*70)

    start_time = time.time()
    while time.time() - start_time < 30:
        time.sleep(1)

    # Results
    print("\n")
    print("="*70)
    print("TEST RESULTS")
    print("="*70)

    if test_message_received:
        print("✅ MQTT CONNECTION VERIFIED")
        print("   - Credentials work")
        print("   - Can publish messages")
        print("   - Can receive messages")
        print("   - Subscriptions work")
    else:
        print("❌ TEST MESSAGE NOT RECEIVED")
        print("   - This indicates a connection problem")

    print()

    if len(messages_received) > 0:
        print(f"✅ AMR DATA FOUND: {len(messages_received)} messages received!")
        print("\nSample messages:")
        for i, msg in enumerate(messages_received[:5]):
            print(f"\n   Message {i+1}:")
            print(f"   Time: {msg['time']}")
            print(f"   Topic: {msg['topic']}")
            print(f"   Payload: {msg['payload']}")
    else:
        print("❌ NO AMR DATA RECEIVED")
        print("   - AMRs are NOT publishing to this broker")
        print("   - OR AMRs are offline")
        print("   - OR publishing to different topics")

    print("="*70)

    # Final verdict
    if test_message_received and len(messages_received) == 0:
        print("\n🎯 DEFINITIVE CONCLUSION:")
        print("   Connection works perfectly!")
        print("   BUT: ATI AMRs are not publishing data.")
        print("\n📋 ACTION REQUIRED:")
        print("   Contact ATI team to:")
        print("   1. Verify AMRs are online and running")
        print("   2. Confirm they're publishing to tvs-dev.ifactory.ai:8883")
        print("   3. Provide the exact MQTT topics they're using")

    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
