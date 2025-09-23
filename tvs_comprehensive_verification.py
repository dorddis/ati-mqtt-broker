#!/usr/bin/env python3
"""
Comprehensive TVS MQTT Verification Tool
Try multiple approaches to ensure we're not missing any data
"""
import json
import time
import ssl
import socket
from datetime import datetime
import paho.mqtt.client as mqtt
import threading
import subprocess
from collections import defaultdict

# TVS MQTT Configuration
MQTT_HOST = "tvs-dev.ifactory.ai"
MQTT_PORT = 8883
MQTT_CLIENT_ID = "amr-001"
MQTT_USERNAME = "amr-001"
MQTT_PASSWORD = "TVSamr001@2025"

# Results tracking
results = {
    "connection_tests": [],
    "messages_received": [],
    "broker_info": {},
    "protocol_tests": {}
}

def test_network_connectivity():
    """Test basic network connectivity to the broker"""
    print("🔍 TESTING NETWORK CONNECTIVITY")
    print("="*50)

    try:
        # Test DNS resolution
        ip = socket.gethostbyname(MQTT_HOST)
        print(f"✅ DNS Resolution: {MQTT_HOST} -> {ip}")
        results["broker_info"]["ip"] = ip

        # Test TCP connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((MQTT_HOST, MQTT_PORT))
        sock.close()

        if result == 0:
            print(f"✅ TCP Connection: {MQTT_HOST}:{MQTT_PORT} reachable")
            results["broker_info"]["tcp_reachable"] = True
        else:
            print(f"❌ TCP Connection: {MQTT_HOST}:{MQTT_PORT} not reachable (error: {result})")
            results["broker_info"]["tcp_reachable"] = False

    except Exception as e:
        print(f"❌ Network test failed: {e}")
        results["broker_info"]["error"] = str(e)

def test_tls_connection():
    """Test TLS/SSL connection to the broker"""
    print("\n🔐 TESTING TLS CONNECTION")
    print("="*50)

    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.create_connection((MQTT_HOST, MQTT_PORT), timeout=10)
        tls_sock = context.wrap_socket(sock, server_hostname=MQTT_HOST)

        print(f"✅ TLS Connection successful")
        print(f"   Protocol: {tls_sock.version()}")
        print(f"   Cipher: {tls_sock.cipher()}")

        results["broker_info"]["tls_working"] = True
        results["broker_info"]["tls_version"] = tls_sock.version()

        tls_sock.close()

    except Exception as e:
        print(f"❌ TLS Connection failed: {e}")
        results["broker_info"]["tls_working"] = False
        results["broker_info"]["tls_error"] = str(e)

def create_mqtt_client_with_logging(client_id, protocol_version, clean_start=True):
    """Create MQTT client with detailed logging"""

    if protocol_version == mqtt.MQTTv5:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=protocol_version
        )
    else:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=protocol_version,
            clean_session=clean_start
        )

    # Enable logging
    client.enable_logger()

    # Detailed callbacks
    def on_connect(client, userdata, flags, rc, properties=None):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        protocol_name = {
            mqtt.MQTTv31: "MQTTv3.1",
            mqtt.MQTTv311: "MQTTv3.1.1",
            mqtt.MQTTv5: "MQTTv5"
        }.get(protocol_version, f"Unknown({protocol_version})")

        if rc == 0:
            print(f"✅ [{timestamp}] Connected with {protocol_name}")
            print(f"   Client ID: {client_id}")
            print(f"   Clean Start: {clean_start}")
            if properties:
                print(f"   Properties: {properties}")

            # Subscribe to everything with different QoS levels
            subscriptions = [
                ("#", 0),  # Everything, QoS 0
                ("#", 1),  # Everything, QoS 1
                ("$SYS/#", 0),  # System topics
            ]

            for topic, qos in subscriptions:
                try:
                    result = client.subscribe(topic, qos)
                    print(f"   📡 Subscribed to '{topic}' QoS {qos}: {result}")
                except Exception as e:
                    print(f"   ❌ Failed to subscribe to '{topic}': {e}")

        else:
            print(f"❌ [{timestamp}] Connection failed with {protocol_name}")
            print(f"   Return code: {rc}")
            if rc == 1:
                print("   Error: Incorrect protocol version")
            elif rc == 2:
                print("   Error: Invalid client identifier")
            elif rc == 3:
                print("   Error: Server unavailable")
            elif rc == 4:
                print("   Error: Bad username or password")
            elif rc == 5:
                print("   Error: Not authorized")

    def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"🔌 [{timestamp}] Disconnected: {rc}")
        if reasonCode:
            print(f"   Reason: {reasonCode}")

    def on_message(client, userdata, msg):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"📦 [{timestamp}] RECEIVED MESSAGE!")
        print(f"   Topic: {msg.topic}")
        print(f"   QoS: {msg.qos}")
        print(f"   Retain: {msg.retain}")
        print(f"   Payload Length: {len(msg.payload)} bytes")

        # Try to decode payload
        try:
            decoded = msg.payload.decode('utf-8')
            print(f"   Payload (text): {decoded[:200]}...")

            # Try JSON
            try:
                json_data = json.loads(decoded)
                print(f"   Payload (JSON): {json.dumps(json_data, indent=4)}")
            except:
                pass

        except:
            print(f"   Payload (hex): {msg.payload.hex()}")

        results["messages_received"].append({
            "timestamp": timestamp,
            "topic": msg.topic,
            "qos": msg.qos,
            "retain": msg.retain,
            "payload_length": len(msg.payload),
            "payload": msg.payload.decode('utf-8', errors='ignore')
        })

        print("-" * 60)

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        print(f"   ✅ Subscription confirmed: MID {mid}, QoS {granted_qos}")

    def on_log(client, userdata, level, buf):
        print(f"   LOG[{level}]: {buf}")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log = on_log

    return client

def test_mqtt_protocols():
    """Test different MQTT protocol versions"""
    print("\n📡 TESTING MQTT PROTOCOLS")
    print("="*50)

    protocols = [
        (mqtt.MQTTv5, "MQTTv5"),
        (mqtt.MQTTv311, "MQTTv3.1.1"),
        (mqtt.MQTTv31, "MQTTv3.1")
    ]

    for protocol, name in protocols:
        print(f"\n🔬 Testing {name}")
        print("-" * 30)

        client_id = f"{MQTT_CLIENT_ID}-{name.replace('.', '')}"
        client = create_mqtt_client_with_logging(client_id, protocol)

        # Set credentials
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        # Configure TLS
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        client.tls_set_context(context)

        try:
            print(f"🔗 Connecting with {name}...")
            client.connect(MQTT_HOST, MQTT_PORT, 60)

            # Run for 30 seconds
            client.loop_start()
            time.sleep(30)
            client.loop_stop()
            client.disconnect()

            results["protocol_tests"][name] = "success"

        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results["protocol_tests"][name] = f"failed: {e}"

def test_different_client_ids():
    """Test with different client IDs"""
    print("\n🆔 TESTING DIFFERENT CLIENT IDS")
    print("="*50)

    client_ids = [
        "amr-001",
        "tvs-client",
        "twinzo-bridge",
        "test-client-001",
        "",  # Empty client ID
        "f4:7b:09:0e:04:1b",  # MAC address format
        "Tug133",
        "AMR_CLIENT_001"
    ]

    for client_id in client_ids:
        print(f"\n🔬 Testing Client ID: '{client_id}'")
        print("-" * 40)

        client = create_mqtt_client_with_logging(client_id or "auto-generated", mqtt.MQTTv5)
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        client.tls_set_context(context)

        try:
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            client.loop_start()
            time.sleep(15)  # Shorter test per client ID
            client.loop_stop()
            client.disconnect()

        except Exception as e:
            print(f"❌ Client ID '{client_id}' failed: {e}")

def test_with_mosquitto_tools():
    """Test using mosquitto command line tools if available"""
    print("\n🛠️  TESTING WITH MOSQUITTO TOOLS")
    print("="*50)

    try:
        # Test mosquitto_sub
        cmd = [
            "mosquitto_sub",
            "-h", MQTT_HOST,
            "-p", str(MQTT_PORT),
            "-u", MQTT_USERNAME,
            "-P", MQTT_PASSWORD,
            "-t", "#",
            "--cafile", "",  # Skip certificate verification
            "-v",  # Verbose
            "-d",  # Debug
            "-W", "30"  # Wait 30 seconds
        ]

        print("🔗 Running mosquitto_sub...")
        print(f"Command: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)

        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        results["mosquitto_tools"] = {
            "available": True,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except FileNotFoundError:
        print("❌ mosquitto_sub not available (not installed)")
        results["mosquitto_tools"] = {"available": False, "reason": "not_installed"}
    except subprocess.TimeoutExpired:
        print("⏰ mosquitto_sub timed out (30 seconds)")
        results["mosquitto_tools"] = {"available": True, "result": "timeout"}
    except Exception as e:
        print(f"❌ mosquitto_sub failed: {e}")
        results["mosquitto_tools"] = {"available": True, "error": str(e)}

def check_for_retained_messages():
    """Check specifically for retained messages"""
    print("\n💾 CHECKING FOR RETAINED MESSAGES")
    print("="*50)

    client = create_mqtt_client_with_logging("retained-checker", mqtt.MQTTv5, clean_start=True)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    client.tls_set_context(context)

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()

        # Subscribe and immediately check for retained messages
        print("🔍 Subscribing to check for retained messages...")
        time.sleep(10)  # Brief check

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"❌ Retained message check failed: {e}")

def generate_summary_report():
    """Generate comprehensive summary"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE VERIFICATION SUMMARY")
    print("="*80)

    print("\n🌐 NETWORK CONNECTIVITY:")
    if results["broker_info"].get("tcp_reachable"):
        print("✅ TCP connection successful")
    else:
        print("❌ TCP connection failed")

    if results["broker_info"].get("tls_working"):
        print(f"✅ TLS connection successful ({results['broker_info'].get('tls_version', 'unknown')})")
    else:
        print("❌ TLS connection failed")

    print(f"\n📡 PROTOCOL TESTS:")
    for protocol, result in results["protocol_tests"].items():
        status = "✅" if result == "success" else "❌"
        print(f"{status} {protocol}: {result}")

    print(f"\n📦 MESSAGES RECEIVED: {len(results['messages_received'])}")
    if results["messages_received"]:
        print("   Topics with messages:")
        topics = defaultdict(int)
        for msg in results["messages_received"]:
            topics[msg["topic"]] += 1
        for topic, count in topics.items():
            print(f"   • {topic}: {count} messages")
    else:
        print("   ❌ NO MESSAGES RECEIVED")

    print(f"\n🛠️  MOSQUITTO TOOLS:")
    if results.get("mosquitto_tools", {}).get("available"):
        print("✅ Available")
    else:
        print("❌ Not available")

    print(f"\n🎯 CONCLUSION:")
    if results["messages_received"]:
        print("✅ SUCCESS: Data is being received from TVS broker")
    elif results["broker_info"].get("tcp_reachable") and results["broker_info"].get("tls_working"):
        print("⚠️  PARTIAL: Connection works but no data detected")
        print("   Possible reasons:")
        print("   • AMRs are offline/not operational")
        print("   • Different topic structure than expected")
        print("   • Data published at very low frequency")
        print("   • Client ID conflicts or access restrictions")
    else:
        print("❌ FAILURE: Cannot establish proper connection")

    # Save detailed results
    with open(f"tvs_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Detailed report saved to: tvs_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

def main():
    """Run comprehensive verification"""
    print("🔍 TVS MQTT COMPREHENSIVE VERIFICATION")
    print("="*80)
    print(f"Target: {MQTT_HOST}:{MQTT_PORT}")
    print(f"Username: {MQTT_USERNAME}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Run all tests
    test_network_connectivity()
    test_tls_connection()
    test_mqtt_protocols()
    test_different_client_ids()
    test_with_mosquitto_tools()
    check_for_retained_messages()

    # Generate final report
    generate_summary_report()

if __name__ == "__main__":
    main()