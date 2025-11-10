#!/usr/bin/env python3
"""
Test HiveMQ Cloud Connection
Verifies MQTT connection to HiveMQ Cloud Serverless broker
"""
import paho.mqtt.client as mqtt
import json
import time
import ssl

# Load HiveMQ config
with open('config/hivemq_config.json', 'r') as f:
    config = json.load(f)

BROKER = config['connection']['host']
PORT = config['connection']['port']
USERNAME = config['credentials']['username']
PASSWORD = config['credentials']['password']
TEST_TOPIC = config['topics']['test_topic']

# Track connection state
connected = False
message_received = False

def on_connect(client, userdata, flags, rc):
    """Callback when connected to broker"""
    global connected
    if rc == 0:
        print("=" * 80)
        print("SUCCESS: Connected to HiveMQ Cloud!")
        print("=" * 80)
        print(f"Broker: {BROKER}")
        print(f"Port: {PORT}")
        print(f"Username: {USERNAME}")
        print()
        connected = True

        # Subscribe to test topic
        client.subscribe(TEST_TOPIC)
        print(f"Subscribed to topic: {TEST_TOPIC}")
        print()
    else:
        print(f"FAILED: Connection error, return code {rc}")
        print("Return codes:")
        print("  0: Success")
        print("  1: Incorrect protocol version")
        print("  2: Invalid client identifier")
        print("  3: Server unavailable")
        print("  4: Bad username or password")
        print("  5: Not authorized")

def on_message(client, userdata, msg):
    """Callback when message received"""
    global message_received
    print("=" * 80)
    print("MESSAGE RECEIVED!")
    print("=" * 80)
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode()}")
    print(f"QoS: {msg.qos}")
    print()
    message_received = True

def on_disconnect(client, userdata, rc):
    """Callback when disconnected"""
    global connected
    connected = False
    if rc != 0:
        print(f"Unexpected disconnect, return code: {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscription confirmed"""
    print(f"Subscription confirmed, QoS: {granted_qos[0]}")
    print()

def on_publish(client, userdata, mid):
    """Callback when message published"""
    print(f"Message published (mid: {mid})")
    print()

def main():
    print("=" * 80)
    print("TESTING HIVEMQ CLOUD CONNECTION")
    print("=" * 80)
    print()

    # Create MQTT client
    client = mqtt.Client(client_id="twinzo-test-client")

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish

    # Set credentials
    client.username_pw_set(USERNAME, PASSWORD)

    # Enable TLS/SSL
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

    try:
        # Connect to broker
        print(f"Connecting to {BROKER}:{PORT}...")
        print()
        client.connect(BROKER, PORT, keepalive=60)

        # Start network loop in background
        client.loop_start()

        # Wait for connection
        timeout = 10
        start = time.time()
        while not connected and (time.time() - start) < timeout:
            time.sleep(0.5)

        if not connected:
            print("ERROR: Connection timeout!")
            return

        # Publish test message
        print("=" * 80)
        print("PUBLISHING TEST MESSAGE")
        print("=" * 80)
        test_message = {
            "source": "twinzo-test-client",
            "timestamp": int(time.time() * 1000),
            "message": "Hello from Twinzo Mock System!"
        }

        result = client.publish(TEST_TOPIC, json.dumps(test_message), qos=1)
        print(f"Publishing to: {TEST_TOPIC}")
        print(f"Payload: {json.dumps(test_message, indent=2)}")
        print()

        # Wait for message to be received
        print("Waiting for message to be received...")
        print("(Should receive the message we just published)")
        print()

        timeout = 5
        start = time.time()
        while not message_received and (time.time() - start) < timeout:
            time.sleep(0.5)

        if message_received:
            print("=" * 80)
            print("SUCCESS: MQTT PUBLISH/SUBSCRIBE TEST PASSED!")
            print("=" * 80)
            print()
            print("Your HiveMQ Cloud broker is working correctly!")
            print()
            print("Next steps:")
            print("1. Test from phone/external network")
            print("2. Set up AMR data simulator")
            print("3. Create bridge to Twinzo API")
        else:
            print("WARNING: Message not received within timeout")
            print("Connection works, but publish/subscribe may have issues")

        # Keep connection alive for a bit
        time.sleep(2)

        # Disconnect
        client.loop_stop()
        client.disconnect()
        print()
        print("Disconnected from broker")

    except Exception as e:
        print(f"ERROR: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check internet connection")
        print("2. Verify credentials in config/hivemq_config.json")
        print("3. Check HiveMQ Cloud console for cluster status")

if __name__ == "__main__":
    main()
