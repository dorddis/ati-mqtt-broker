#!/usr/bin/env python3
"""
Complete integration test for ATI MQTT broker
Tests both HTTP and WebSocket MQTT publishing/subscribing
"""
import requests
import json
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime

def test_http_publishing():
    """Test HTTP REST API publishing"""
    print("🧪 Testing HTTP REST API Publishing...")

    # Test data matching ATI's expected format
    test_data = {
        "topic": "ati/test/amr-001",
        "message": {
            "sherpa_name": "amr-001",
            "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
            "battery_status": 78.5,
            "mode": "Fleet",
            "error": "",
            "disabled": False,
            "trip_id": 1001,
            "trip_leg_id": 5001,
            "timestamp": int(time.time() * 1000)
        }
    }

    try:
        response = requests.post(
            "https://ati-mqtt-broker.onrender.com/publish",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ HTTP Publish Success: {result}")
            return True
        else:
            print(f"❌ HTTP Publish Failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ HTTP Publish Error: {e}")
        return False

def test_websocket_mqtt():
    """Test MQTT over WebSocket publishing and subscribing"""
    print("🧪 Testing MQTT over WebSocket...")

    messages_received = []
    connection_successful = threading.Event()
    publish_successful = threading.Event()

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ WebSocket MQTT Connected!")
            connection_successful.set()

            # Subscribe to test topic
            client.subscribe("ati/test/#")
            print("📡 Subscribed to ati/test/#")

            # Publish test message
            test_message = {
                "sherpa_name": "websocket-test-amr",
                "pose": [195631.0, 188398.0, 0.0, 0.0, 0.0, 2.14],
                "battery_status": 82.3,
                "mode": "Manual",
                "timestamp": int(time.time() * 1000)
            }

            result = client.publish("ati/test/websocket", json.dumps(test_message), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print("✅ WebSocket Message Published!")
                publish_successful.set()
            else:
                print(f"❌ WebSocket Publish Failed: {result.rc}")
        else:
            print(f"❌ WebSocket Connection Failed: {rc}")

    def on_message(client, userdata, msg):
        try:
            message_data = json.loads(msg.payload.decode())
            print(f"📨 Received on {msg.topic}: {message_data}")
            messages_received.append({
                'topic': msg.topic,
                'message': message_data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"❌ Error processing message: {e}")

    def on_disconnect(client, userdata, rc):
        print(f"🔌 WebSocket Disconnected: {rc}")

    # Setup MQTT client
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
        client.tls_set()  # Enable TLS for wss://

        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect

        print("🔗 Connecting to wss://ati-mqtt-broker.onrender.com...")
        client.connect("ati-mqtt-broker.onrender.com", 443, 60)

        # Start the loop in background
        client.loop_start()

        # Wait for connection
        if connection_successful.wait(timeout=10):
            print("✅ WebSocket connection established")

            # Wait a bit for message processing
            time.sleep(3)

            # Stop the client
            client.loop_stop()
            client.disconnect()

            return len(messages_received) > 0, messages_received
        else:
            print("❌ WebSocket connection timeout")
            client.loop_stop()
            return False, []

    except Exception as e:
        print(f"❌ WebSocket MQTT Error: {e}")
        return False, []

def test_service_health():
    """Test service health endpoints"""
    print("🧪 Testing Service Health...")

    endpoints = [
        ("Health Check", "https://ati-mqtt-broker.onrender.com/health"),
        ("Service Status", "https://ati-mqtt-broker.onrender.com/status"),
        ("Root Info", "https://ati-mqtt-broker.onrender.com/")
    ]

    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {response.json()}")
            else:
                print(f"❌ {name} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} error: {e}")

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive ATI MQTT Broker Test")
    print("=" * 60)

    results = {
        'http_publish': False,
        'websocket_mqtt': False,
        'messages_received': [],
        'service_health': True
    }

    # Test 1: Service Health
    test_service_health()
    print()

    # Test 2: HTTP Publishing
    results['http_publish'] = test_http_publishing()
    print()

    # Test 3: WebSocket MQTT
    websocket_success, messages = test_websocket_mqtt()
    results['websocket_mqtt'] = websocket_success
    results['messages_received'] = messages
    print()

    # Summary
    print("📊 Test Results Summary:")
    print("=" * 30)
    print(f"HTTP Publishing: {'✅ PASS' if results['http_publish'] else '❌ FAIL'}")
    print(f"WebSocket MQTT: {'✅ PASS' if results['websocket_mqtt'] else '❌ FAIL'}")
    print(f"Messages Received: {len(results['messages_received'])}")

    if results['messages_received']:
        print("\n📨 Messages Received:")
        for msg in results['messages_received']:
            print(f"  - {msg['topic']}: {msg['message']['sherpa_name']} @ {msg['timestamp']}")

    # Overall Status
    all_passed = results['http_publish'] and results['websocket_mqtt']
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '⚠️  SOME TESTS FAILED'}")

    if all_passed:
        print("\n🎉 ATI MQTT Broker is ready for production use!")
        print("ATI can proceed with integration using either:")
        print("  1. HTTP REST API: https://ati-mqtt-broker.onrender.com/publish")
        print("  2. MQTT WebSocket: wss://ati-mqtt-broker.onrender.com")
    else:
        print("\n⚠️  Please review failing tests before ATI integration")

    return results

if __name__ == "__main__":
    run_comprehensive_test()