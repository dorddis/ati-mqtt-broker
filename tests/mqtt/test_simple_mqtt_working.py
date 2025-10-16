#!/usr/bin/env python3
"""
Simple MQTT test based on diagnostic results
Uses the exact same configuration that worked in the diagnostic
"""
import paho.mqtt.client as mqtt
import json
import time

def test_working_mqtt_connection():
    """Test MQTT using the exact working configuration from diagnostic"""
    print("🧪 Testing MQTT with Proven Working Configuration")
    print("=" * 52)

    connection_success = False
    publish_success = False

    def on_connect(client, userdata, flags, rc, properties=None):
        nonlocal connection_success
        if rc == 0:
            print("✅ Connected successfully!")
            connection_success = True

            # Publish test AMR data
            amr_data = {
                "sherpa_name": "test-amr-001",
                "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
                "battery_status": 79.5,
                "mode": "Fleet",
                "timestamp": int(time.time() * 1000)
            }

            topic = "ati/test/amr-001/status"
            result = client.publish(topic, json.dumps(amr_data), qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"✅ Published AMR data to {topic}")
                print(f"📊 Message ID: {result.mid}")
                nonlocal publish_success
                publish_success = True
            else:
                print(f"❌ Publish failed: {result.rc}")

            # Disconnect after publish
            client.disconnect()

        else:
            print(f"❌ Connection failed: {mqtt.error_string(rc)}")

    def on_publish(client, userdata, mid):
        print(f"📤 Message {mid} published successfully!")

    def on_disconnect(client, userdata, rc):
        print(f"🔌 Disconnected: {rc}")

    try:
        # Use exact same configuration as diagnostic tool
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            transport="websockets",
            client_id=f"simple-test-{int(time.time())}"
        )

        client.tls_set()
        client.ws_set_options(path="/")  # Root path worked in diagnostic

        client.on_connect = on_connect
        client.on_publish = on_publish
        client.on_disconnect = on_disconnect

        print("🔗 Connecting to wss://ati-mqtt-broker.onrender.com...")
        client.connect("ati-mqtt-broker.onrender.com", 443, 10)
        client.loop(timeout=10)

        return connection_success, publish_success

    except Exception as e:
        print(f"❌ Error: {e}")
        return False, False

def test_multiple_amr_publishing():
    """Test publishing for multiple AMRs in sequence"""
    print("\n🧪 Testing Multiple AMR Publishing")
    print("=" * 38)

    amr_list = [
        {"name": "tugger-01", "x": 195630.16, "y": 188397.78, "battery": 79.5},
        {"name": "tugger-02", "x": 195635.22, "y": 188402.33, "battery": 82.1},
        {"name": "sherpa-01", "x": 195628.91, "y": 188395.44, "battery": 74.8}
    ]

    successful_publishes = 0

    for amr in amr_list:
        print(f"\n📡 Publishing data for {amr['name']}...")

        connection_success = False
        publish_success = False

        def on_connect(client, userdata, flags, rc, properties=None):
            nonlocal connection_success, publish_success
            if rc == 0:
                connection_success = True

                amr_data = {
                    "sherpa_name": amr['name'],
                    "pose": [amr['x'], amr['y'], 0.0, 0.0, 0.0, 1.57],
                    "battery_status": amr['battery'],
                    "mode": "Fleet",
                    "timestamp": int(time.time() * 1000)
                }

                result = client.publish(f"ati/amr/{amr['name']}/status", json.dumps(amr_data), qos=1)

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"✅ {amr['name']}: Published successfully")
                    publish_success = True
                    nonlocal successful_publishes
                    successful_publishes += 1
                else:
                    print(f"❌ {amr['name']}: Publish failed")

                client.disconnect()

        try:
            client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                transport="websockets",
                client_id=f"{amr['name']}-{int(time.time())}"
            )

            client.tls_set()
            client.ws_set_options(path="/")
            client.on_connect = on_connect

            client.connect("ati-mqtt-broker.onrender.com", 443, 10)
            client.loop(timeout=8)

        except Exception as e:
            print(f"❌ {amr['name']}: Connection error - {e}")

        time.sleep(1)  # Brief pause between AMRs

    return successful_publishes, len(amr_list)

def main():
    print("🚀 Simple MQTT WebSocket Verification Test")
    print("=" * 45)

    # Test 1: Single connection and publish
    connected, published = test_working_mqtt_connection()

    # Test 2: Multiple AMRs
    multi_success, multi_total = test_multiple_amr_publishing()

    # Results
    print(f"\n📊 Test Results Summary")
    print("=" * 25)
    print(f"Single Connection: {'✅ SUCCESS' if connected else '❌ FAILED'}")
    print(f"Single Publish: {'✅ SUCCESS' if published else '❌ FAILED'}")
    print(f"Multi-AMR Publishing: {multi_success}/{multi_total} successful")

    overall_success = connected and published and (multi_success == multi_total)

    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '⚠️  SOME TESTS FAILED'}")

    if overall_success:
        print("\n🎉 MQTT WebSocket is FULLY OPERATIONAL!")
        print("\n📋 ATI Integration Instructions:")
        print("  • URL: wss://ati-mqtt-broker.onrender.com")
        print("  • Port: 443")
        print("  • Protocol: MQTT over WebSocket")
        print("  • Path: / (root path)")
        print("  • TLS: Required")
        print("  • Authentication: Anonymous (no credentials needed)")
        print("  • Topic Pattern: ati/amr/{robot_name}/status")
    else:
        print("\n⚠️  Some connection issues detected. Check network/firewall settings.")

    return overall_success

if __name__ == "__main__":
    main()