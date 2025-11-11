#!/usr/bin/env python3
"""
Focused TVS MQTT Verification - Multiple approaches to ensure we're not missing data
"""
import json
import time
import ssl
import socket
from datetime import datetime
import paho.mqtt.client as mqtt
import threading

# TVS Configuration
MQTT_HOST = "tvs-dev.ifactory.ai"
MQTT_PORT = 8883
MQTT_USERNAME = "amr-001"
MQTT_PASSWORD = "TVSamr001@2025"

message_count = 0
unique_topics = set()
all_messages = []

def test_basic_connectivity():
    """Test that we can reach the broker"""
    print("🔍 BASIC CONNECTIVITY TEST")
    print("="*50)

    try:
        # DNS resolution
        ip = socket.gethostbyname(MQTT_HOST)
        print(f"✅ DNS: {MQTT_HOST} -> {ip}")

        # TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((MQTT_HOST, MQTT_PORT))
        sock.close()

        if result == 0:
            print(f"✅ TCP: Port {MQTT_PORT} is reachable")
        else:
            print(f"❌ TCP: Port {MQTT_PORT} not reachable")
            return False

        # TLS handshake
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.create_connection((MQTT_HOST, MQTT_PORT), timeout=10)
        tls_sock = context.wrap_socket(sock, server_hostname=MQTT_HOST)
        print(f"✅ TLS: {tls_sock.version()} connection successful")
        tls_sock.close()

        return True

    except Exception as e:
        print(f"❌ Connectivity failed: {e}")
        return False

def test_mqtt_with_different_settings():
    """Test MQTT with various settings systematically"""
    print("\n📡 SYSTEMATIC MQTT TESTING")
    print("="*60)

    global message_count, unique_topics, all_messages

    # Test configurations
    configs = [
        {"protocol": mqtt.MQTTv5, "client_id": "amr-001", "clean_start": True},
        {"protocol": mqtt.MQTTv311, "client_id": "amr-001", "clean_session": True},
        {"protocol": mqtt.MQTTv5, "client_id": "tvs-monitor", "clean_start": True},
        {"protocol": mqtt.MQTTv5, "client_id": "", "clean_start": True},  # Auto client ID
        {"protocol": mqtt.MQTTv5, "client_id": "f4:7b:09:0e:04:1b", "clean_start": True},  # MAC format
    ]

    for i, config in enumerate(configs, 1):
        print(f"\n🔬 Test {i}: {config}")
        print("-" * 40)

        # Reset counters for this test
        message_count = 0
        test_messages = []

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print(f"   ✅ Connected successfully")
                # Subscribe to comprehensive topic patterns
                topics = [
                    "#",                    # Everything
                    "$SYS/#",              # System topics
                    "amr/+/+",             # AMR specific
                    "tug/+/+",             # Tug specific
                    "robot/+/+",           # Robot specific
                    "tvs/+/+",             # TVS specific
                    "+/+/status",          # Any status
                    "+/+/position",        # Any position
                    "f4:7b:09:0e:04:1b/+", # Specific MAC
                    "10:3d:1c:66:67:55/+", # Specific MAC
                    "f4:4e:e3:f6:c7:91/+", # Specific MAC
                    "ec:2e:98:4a:7c:f7/+", # Specific MAC
                ]

                for topic in topics:
                    client.subscribe(topic, qos=1)
                    print(f"   📡 Subscribed: {topic}")

            else:
                print(f"   ❌ Connection failed: {rc}")

        def on_message(client, userdata, msg):
            global message_count
            message_count += 1
            unique_topics.add(msg.topic)

            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            print(f"   📦 [{timestamp}] Message #{message_count}")
            print(f"      Topic: {msg.topic}")
            print(f"      QoS: {msg.qos}, Retain: {msg.retain}")
            print(f"      Payload: {len(msg.payload)} bytes")

            # Try to decode and display payload
            try:
                decoded = msg.payload.decode('utf-8')
                if len(decoded) < 200:
                    print(f"      Content: {decoded}")
                else:
                    print(f"      Content: {decoded[:200]}...")

                # Try JSON parsing
                try:
                    json_data = json.loads(decoded)
                    print(f"      JSON Keys: {list(json_data.keys())}")
                except:
                    pass

            except:
                print(f"      Content: <binary data>")

            all_messages.append({
                "test": i,
                "timestamp": timestamp,
                "topic": msg.topic,
                "qos": msg.qos,
                "retain": msg.retain,
                "payload": msg.payload.decode('utf-8', errors='ignore')
            })

            print("   " + "-" * 50)

        def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
            print(f"   🔌 Disconnected: {rc}")

        try:
            # Create client based on protocol
            if config["protocol"] == mqtt.MQTTv5:
                client = mqtt.Client(
                    mqtt.CallbackAPIVersion.VERSION2,
                    client_id=config["client_id"],
                    protocol=config["protocol"]
                )
            else:
                client = mqtt.Client(
                    mqtt.CallbackAPIVersion.VERSION2,
                    client_id=config["client_id"],
                    protocol=config["protocol"],
                    clean_session=config.get("clean_session", True)
                )

            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

            # TLS setup
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            client.tls_set_context(context)

            # Set callbacks
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_disconnect = on_disconnect

            # Connect and wait
            print(f"   🔗 Connecting...")
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            client.loop_start()

            # Wait for messages for 45 seconds
            print(f"   ⏱️  Waiting 45 seconds for messages...")
            time.sleep(45)

            client.loop_stop()
            client.disconnect()

            print(f"   📊 Result: {message_count} messages received")

            if message_count > 0:
                print(f"   🎯 SUCCESS! Found data with this configuration")
                break

        except Exception as e:
            print(f"   ❌ Test failed: {e}")

        print()

def test_alternative_authentication():
    """Test different authentication approaches"""
    print("\n🔐 AUTHENTICATION VARIATIONS")
    print("="*50)

    auth_configs = [
        {"username": "amr-001", "password": "TVSamr001@2025"},
        {"username": "AMR-001", "password": "TVSamr001@2025"},  # Uppercase
        {"username": "amr-001", "password": ""},  # Empty password
        {"username": "", "password": ""},  # No auth
        {"username": "tug133", "password": "TVSamr001@2025"},  # Device name
        {"username": "f4:7b:09:0e:04:1b", "password": "TVSamr001@2025"},  # MAC as username
    ]

    for i, auth in enumerate(auth_configs, 1):
        print(f"\n🔬 Auth Test {i}: user='{auth['username']}', pass='{auth['password']}'")

        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"auth-test-{i}", protocol=mqtt.MQTTv5)

            if auth["username"] or auth["password"]:
                client.username_pw_set(auth["username"], auth["password"])

            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            client.tls_set_context(context)

            connected = False

            def on_connect(client, userdata, flags, rc, properties=None):
                nonlocal connected
                if rc == 0:
                    print(f"   ✅ Authentication successful")
                    connected = True
                    client.subscribe("#", qos=1)
                else:
                    print(f"   ❌ Authentication failed: {rc}")

            client.on_connect = on_connect
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            client.loop_start()
            time.sleep(10)
            client.loop_stop()
            client.disconnect()

            if connected:
                print(f"   🎯 This authentication works!")

        except Exception as e:
            print(f"   ❌ Auth test failed: {e}")

def generate_final_report():
    """Generate final comprehensive report"""
    print("\n" + "="*80)
    print("📊 FINAL VERIFICATION REPORT")
    print("="*80)

    print(f"🎯 SUMMARY:")
    print(f"   Total messages received: {len(all_messages)}")
    print(f"   Unique topics discovered: {len(unique_topics)}")

    if all_messages:
        print(f"   ✅ SUCCESS: TVS broker IS publishing data!")

        print(f"\n📡 TOPICS WITH DATA:")
        topic_counts = {}
        for msg in all_messages:
            topic_counts[msg["topic"]] = topic_counts.get(msg["topic"], 0) + 1

        for topic, count in sorted(topic_counts.items()):
            print(f"   • {topic}: {count} messages")

        print(f"\n📝 SAMPLE MESSAGES:")
        for i, msg in enumerate(all_messages[:5]):
            print(f"   Message {i+1}:")
            print(f"      Topic: {msg['topic']}")
            print(f"      Time: {msg['timestamp']}")
            print(f"      Content: {msg['payload'][:100]}...")

    else:
        print(f"   ❌ NO DATA DETECTED")
        print(f"   Possible explanations:")
        print(f"   • AMRs are currently offline/not operational")
        print(f"   • Different authentication required")
        print(f"   • Data published to unexpected topics")
        print(f"   • Very low frequency publishing")
        print(f"   • Access restrictions for this client ID")

    # Save detailed results
    report_file = f"tvs_focused_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "summary": {
                "total_messages": len(all_messages),
                "unique_topics": list(unique_topics),
                "success": len(all_messages) > 0
            },
            "messages": all_messages
        }, f, indent=2)

    print(f"\n💾 Detailed report saved: {report_file}")

def main():
    """Run focused verification"""
    print("🔍 TVS MQTT FOCUSED VERIFICATION")
    print("="*80)
    print(f"Target: {MQTT_HOST}:{MQTT_PORT}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Step 1: Basic connectivity
    if not test_basic_connectivity():
        print("❌ Cannot proceed - basic connectivity failed")
        return

    # Step 2: Systematic MQTT testing
    test_mqtt_with_different_settings()

    # Step 3: Authentication variations
    test_alternative_authentication()

    # Step 4: Final report
    generate_final_report()

if __name__ == "__main__":
    main()