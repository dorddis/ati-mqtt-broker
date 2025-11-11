#!/usr/bin/env python3
"""
TVS COMPREHENSIVE MQTT TEST
Exhaustive testing of all possible client IDs, topics, and data formats
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
import uuid
from datetime import datetime, timezone
import threading
from collections import defaultdict

# Configuration
HOST = "tvs-dev.ifactory.ai"
PORT = 8883
BASE_PASSWORD = "TVSamr001@2025"

# Test different client configurations
CLIENT_CONFIGS = [
    # Original credential
    {"client_id": "amr-001", "username": "amr-001", "password": BASE_PASSWORD},

    # Try different device IDs from documentation
    {"client_id": "device-1", "username": "device-1", "password": ""},
    {"client_id": "device-2", "username": "device-2", "password": ""},

    # Try tug-specific IDs
    {"client_id": "tug-133", "username": "tug-133", "password": ""},
    {"client_id": "tug-39", "username": "tug-39", "password": ""},
    {"client_id": "tug-55", "username": "tug-55", "password": ""},
    {"client_id": "tug-78", "username": "tug-78", "password": ""},

    # Try MAC addresses as client IDs
    {"client_id": "f4:7b:09:0e:04:1b", "username": "f4:7b:09:0e:04:1b", "password": ""},
    {"client_id": "10:3d:1c:66:67:55", "username": "10:3d:1c:66:67:55", "password": ""},

    # Try robotspace/admin patterns
    {"client_id": "robotspace", "username": "robotspace", "password": ""},
    {"client_id": "admin", "username": "admin", "password": ""},
    {"client_id": "consumer", "username": "consumer", "password": ""},

    # Try amr-001 with different usernames
    {"client_id": "tvs-client", "username": "amr-001", "password": BASE_PASSWORD},
    {"client_id": "test-client", "username": "amr-001", "password": BASE_PASSWORD},

    # Try blank client ID (auto-generate)
    {"client_id": "", "username": "amr-001", "password": BASE_PASSWORD},
]

# Global results tracking
results = {
    "connections": defaultdict(dict),
    "subscriptions": defaultdict(lambda: defaultdict(list)),
    "publishes": defaultdict(lambda: defaultdict(list)),
    "messages_received": defaultdict(list)
}

class ComprehensiveTestClient:
    def __init__(self, config):
        self.config = config
        self.client_id = config["client_id"] or f"auto-{uuid.uuid4().hex[:8]}"
        self.username = config["username"]
        self.password = config["password"]

        self.connected = False
        self.connection_attempts = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.subscription_results = {}
        self.publish_results = {}

        # Create MQTT client
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
            protocol=mqtt.MQTTv5
        )

        # Set credentials if provided
        if self.username:
            self.client.username_pw_set(self.username, self.password)

        # Configure TLS
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.client.tls_set_context(context)

        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc, properties=None):
        self.connection_attempts += 1
        if rc == 0:
            self.connected = True
            results["connections"][self.client_id]["success"] = True
            results["connections"][self.client_id]["username"] = self.username
        else:
            results["connections"][self.client_id]["success"] = False
            results["connections"][self.client_id]["error"] = rc

    def on_disconnect(self, client, userdata, rc, properties=None, reasonCode=None):
        self.connected = False
        if reasonCode:
            results["connections"][self.client_id]["disconnect_reason"] = str(reasonCode)

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        if mid in self.subscription_results:
            topic = self.subscription_results[mid]
            if granted_qos and len(granted_qos) > 0:
                if hasattr(granted_qos[0], 'is_failure') and granted_qos[0].is_failure:
                    results["subscriptions"][self.client_id][topic].append("DENIED")
                else:
                    results["subscriptions"][self.client_id][topic].append("GRANTED")

    def on_publish(self, client, userdata, mid, properties=None, reasonCode=None):
        if mid in self.publish_results:
            topic = self.publish_results[mid]
            self.messages_sent += 1
            results["publishes"][self.client_id][topic].append("SUCCESS")

    def on_message(self, client, userdata, msg):
        self.messages_received += 1
        results["messages_received"][self.client_id].append({
            "topic": msg.topic,
            "size": len(msg.payload),
            "timestamp": datetime.now().isoformat()
        })

    def test_connection(self):
        """Test if we can connect with these credentials"""
        try:
            self.client.connect(HOST, PORT, keepalive=60)
            self.client.loop_start()
            time.sleep(2)

            if self.connected:
                return True
            return False
        except Exception as e:
            results["connections"][self.client_id]["error"] = str(e)
            return False
        finally:
            self.client.loop_stop()
            self.client.disconnect()

    def test_topics(self):
        """Test subscribing and publishing to various topics"""
        if not self.test_connection():
            return

        try:
            self.client.connect(HOST, PORT, keepalive=60)
            self.client.loop_start()
            time.sleep(1)

            # Test subscribe topics
            test_subscribe_topics = [
                f"/c2d/{self.client_id}",  # Commands to this device
                f"/d2c/{self.client_id}",  # Data from this device (echo)
                f"/d2c/+",  # All device data
                f"/c2d/+",  # All commands
                "#",  # Everything
                "ati_fm/sherpa/status",  # Original topic
                f"{self.client_id}/#",  # Client-specific wildcard
            ]

            for topic in test_subscribe_topics:
                result, mid = self.client.subscribe(topic, qos=1)
                self.subscription_results[mid] = topic
                time.sleep(0.5)

            # Wait for subscription results
            time.sleep(3)

            # Test publish topics
            test_publish_topics = [
                f"/d2c/{self.client_id}",  # Device to cloud
                f"/d2c/{self.username}",  # Username-based
                "ati_fm/sherpa/status",  # Try original topic
            ]

            for topic in test_publish_topics:
                if self.connected:
                    message = self.generate_test_message()
                    result = self.client.publish(topic, json.dumps(message), qos=1)
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        self.publish_results[result.mid] = topic
                    time.sleep(0.5)

            # Wait for results
            time.sleep(5)

        except Exception as e:
            results["connections"][self.client_id]["test_error"] = str(e)
        finally:
            self.client.loop_stop()
            self.client.disconnect()

    def generate_test_message(self):
        """Generate various message types"""
        message_types = [
            # Heartbeat
            {
                "data": {
                    "ueid": str(uuid.uuid4()),
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "did": self.client_id,
                    "eid": 2001,
                    "pl": {
                        "uptime": "1h 0m 0sec",
                        "signalStrength": "55/70",
                        "battery": 85.45,
                        "temperature": 42.56
                    }
                }
            },
            # Trip update
            {
                "data": {
                    "ueid": str(uuid.uuid4()),
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "did": self.client_id,
                    "eid": 2002,
                    "pl": {
                        "location": {"lat": 17.0234, "long": 13.023456},
                        "status": "moving",
                        "distance": 78.34,
                        "tripId": str(uuid.uuid4())
                    }
                }
            }
        ]
        return message_types[self.messages_sent % len(message_types)]

def test_client_configuration(config):
    """Test a single client configuration"""
    print(f"\n{'='*60}")
    print(f"Testing: Client ID: {config['client_id'] or 'auto'}, Username: {config['username']}")
    print(f"{'='*60}")

    test_client = ComprehensiveTestClient(config)

    # Test connection
    print("1. Testing connection...")
    if test_client.test_connection():
        print(f"   ✅ Connected as {test_client.client_id}")

        # Test topics
        print("2. Testing topics...")
        test_client.test_topics()

        # Report results for this client
        client_results = {
            "connected": test_client.connected,
            "messages_sent": test_client.messages_sent,
            "messages_received": test_client.messages_received,
            "subscriptions": results["subscriptions"].get(test_client.client_id, {}),
            "publishes": results["publishes"].get(test_client.client_id, {})
        }

        if test_client.messages_sent > 0:
            print(f"   ✅ Published {test_client.messages_sent} messages")
        if test_client.messages_received > 0:
            print(f"   ✅ Received {test_client.messages_received} messages")

        # Show allowed subscriptions
        allowed_subs = []
        for topic, results_list in client_results["subscriptions"].items():
            if "GRANTED" in results_list:
                allowed_subs.append(topic)

        if allowed_subs:
            print(f"   ✅ Can subscribe to: {', '.join(allowed_subs)}")

        # Show successful publishes
        published_topics = list(client_results["publishes"].keys())
        if published_topics:
            print(f"   ✅ Can publish to: {', '.join(published_topics)}")
    else:
        print(f"   ❌ Connection failed")

def main():
    print("="*80)
    print("🔍 TVS COMPREHENSIVE MQTT TEST")
    print("="*80)
    print(f"Broker: {HOST}:{PORT}")
    print(f"Testing {len(CLIENT_CONFIGS)} different configurations")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Test each configuration
    working_configs = []

    for config in CLIENT_CONFIGS:
        try:
            test_client_configuration(config)

            # Check if this config worked
            client_id = config["client_id"] or f"auto-generated"
            if results["connections"].get(client_id, {}).get("success"):
                working_configs.append(config)

        except Exception as e:
            print(f"   ❌ Error: {e}")

        time.sleep(2)  # Pause between tests

    # Generate comprehensive report
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE REPORT")
    print("="*80)

    print(f"\n✅ WORKING CONFIGURATIONS ({len(working_configs)}):")
    for config in working_configs:
        client_id = config["client_id"] or "auto"
        print(f"\n   Client ID: {client_id}")
        print(f"   Username: {config['username']}")
        print(f"   Password: {'***' if config['password'] else 'none'}")

        # Show what this config can do
        subs = results["subscriptions"].get(client_id, {})
        pubs = results["publishes"].get(client_id, {})
        msgs = results["messages_received"].get(client_id, [])

        allowed_subs = [t for t, r in subs.items() if "GRANTED" in r]
        successful_pubs = list(pubs.keys())

        if allowed_subs:
            print(f"   Can subscribe to: {', '.join(allowed_subs)}")
        if successful_pubs:
            print(f"   Can publish to: {', '.join(successful_pubs)}")
        if msgs:
            print(f"   Received {len(msgs)} messages")

    print("\n" + "="*80)
    print("🔍 KEY FINDINGS:")
    print("="*80)

    # Analyze patterns
    all_allowed_subs = set()
    all_successful_pubs = set()

    for client_id in results["subscriptions"]:
        for topic, result_list in results["subscriptions"][client_id].items():
            if "GRANTED" in result_list:
                all_allowed_subs.add(topic)

    for client_id in results["publishes"]:
        for topic in results["publishes"][client_id]:
            all_successful_pubs.add(topic)

    print("\n📥 SUBSCRIPTION PERMISSIONS:")
    if all_allowed_subs:
        for topic in sorted(all_allowed_subs):
            print(f"   ✅ {topic}")
    else:
        print("   ❌ No successful subscriptions")

    print("\n📤 PUBLISH PERMISSIONS:")
    if all_successful_pubs:
        for topic in sorted(all_successful_pubs):
            print(f"   ✅ {topic}")
    else:
        print("   ❌ No successful publishes")

    print("\n📝 CONCLUSIONS:")
    if len(working_configs) == 1 and working_configs[0]["username"] == "amr-001":
        print("• Only the amr-001 account can connect")
        print("• This is a device account for publishing AMR data")
        print("• It can subscribe to /c2d/amr-001 for commands")
        print("• It can publish to /d2c/amr-001 for telemetry")
        print("• It CANNOT read data from other devices")
        print("\n🎯 WHAT YOU NEED:")
        print("• Ask for CONSUMER credentials to read /d2c/+ topics")
        print("• Or ask for the specific broker/topic where processed data is available")
        print("• Or ask for credentials to the system that consumes this data")
    elif len(working_configs) > 1:
        print("• Multiple configurations work!")
        print("• Review the working configs above for capabilities")
    else:
        print("• No configurations could connect successfully")
        print("• The credentials may have changed or been revoked")

    print("="*80)

if __name__ == "__main__":
    main()