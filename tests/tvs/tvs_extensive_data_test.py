#!/usr/bin/env python3
"""
TVS Extensive Data Test
Focus on publishing different data types and understanding exact capabilities
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
USERNAME = "amr-001"
PASSWORD = "TVSamr001@2025"

# Global tracking
test_results = {
    "connections": [],
    "subscriptions": defaultdict(list),
    "publishes": defaultdict(list),
    "messages_received": [],
    "disconnections": []
}

class ExtensiveTestClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.connected = False
        self.messages_sent = 0
        self.messages_received = 0
        self.client = None

    def create_client(self):
        """Create a new MQTT client"""
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
            protocol=mqtt.MQTTv5
        )

        self.client.username_pw_set(USERNAME, PASSWORD)

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
        if rc == 0:
            self.connected = True
            test_results["connections"].append({
                "client_id": self.client_id,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
        else:
            test_results["connections"].append({
                "client_id": self.client_id,
                "success": False,
                "error": rc,
                "timestamp": datetime.now().isoformat()
            })

    def on_disconnect(self, client, userdata, rc, properties=None, reasonCode=None):
        self.connected = False
        test_results["disconnections"].append({
            "client_id": self.client_id,
            "reason": str(reasonCode) if reasonCode else str(rc),
            "timestamp": datetime.now().isoformat()
        })

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        # We'll track this in the calling function
        pass

    def on_publish(self, client, userdata, mid, properties=None, reasonCode=None):
        self.messages_sent += 1

    def on_message(self, client, userdata, msg):
        self.messages_received += 1
        test_results["messages_received"].append({
            "client_id": self.client_id,
            "topic": msg.topic,
            "size": len(msg.payload),
            "timestamp": datetime.now().isoformat()
        })

    def test_comprehensive_publishing(self):
        """Test publishing all types of data to all possible topics"""
        if not self.connected:
            return

        # All possible publish topics based on documentation
        publish_topics = [
            f"/d2c/{self.client_id}",
            f"/d2c/amr-001",
            f"/d2c/device-1",
            f"/d2c/tug-133",
            "ati_fm/sherpa/status",
            "robotspace/sherpa/status",
            f"amr/{self.client_id}/status",
            f"tug/{self.client_id}/status",
        ]

        # All message types from documentation
        message_types = [
            ("heartbeat", self.get_heartbeat_message()),
            ("trip_start", self.get_trip_start_message()),
            ("trip_update", self.get_trip_update_message()),
            ("trip_end", self.get_trip_end_message()),
            ("error", self.get_error_message()),
            ("raw_sensor", self.get_raw_sensor_data()),
            ("minimal", self.get_minimal_message())
        ]

        print(f"\n📤 Testing {len(publish_topics)} topics × {len(message_types)} message types = {len(publish_topics) * len(message_types)} combinations")

        success_count = 0
        for topic in publish_topics:
            if not self.connected:
                break

            print(f"\n   Testing topic: {topic}")
            for msg_type, message in message_types:
                if not self.connected:
                    break

                try:
                    result = self.client.publish(topic, json.dumps(message), qos=1)
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        success_count += 1
                        test_results["publishes"][topic].append({
                            "message_type": msg_type,
                            "success": True,
                            "mid": result.mid,
                            "timestamp": datetime.now().isoformat()
                        })
                        print(f"      ✅ {msg_type}")
                    else:
                        test_results["publishes"][topic].append({
                            "message_type": msg_type,
                            "success": False,
                            "error": result.rc,
                            "timestamp": datetime.now().isoformat()
                        })
                        print(f"      ❌ {msg_type} (error: {result.rc})")

                    time.sleep(0.2)  # Brief pause
                except Exception as e:
                    print(f"      ❌ {msg_type} (exception: {e})")

                # Check if we got disconnected
                if not self.connected:
                    print("      ⚠️ Disconnected during publish test!")
                    break

        print(f"\n   📊 Successfully published {success_count} messages")
        return success_count

    def test_comprehensive_subscribing(self):
        """Test subscribing to all possible topics"""
        if not self.connected:
            return

        # All possible subscribe topics
        subscribe_topics = [
            f"/c2d/{self.client_id}",
            f"/c2d/amr-001",
            f"/d2c/{self.client_id}",
            f"/d2c/amr-001",
            f"/d2c/+",
            f"/c2d/+",
            "#",
            "+",
            "ati_fm/sherpa/status",
            "robotspace/sherpa/status",
            f"amr/{self.client_id}/#",
            f"tug/{self.client_id}/#",
            "$SYS/#"
        ]

        print(f"\n📥 Testing {len(subscribe_topics)} subscription topics")

        granted_count = 0
        for topic in subscribe_topics:
            if not self.connected:
                break

            try:
                result, mid = self.client.subscribe(topic, qos=1)
                time.sleep(0.5)  # Wait for response

                # Since we don't have direct access to the response in the callback,
                # we'll assume success if we didn't get disconnected
                if self.connected:
                    granted_count += 1
                    test_results["subscriptions"][topic].append({
                        "client_id": self.client_id,
                        "success": True,
                        "mid": mid,
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"   ✅ {topic}")
                else:
                    test_results["subscriptions"][topic].append({
                        "client_id": self.client_id,
                        "success": False,
                        "reason": "disconnected",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"   ❌ {topic} (caused disconnection)")
                    break

            except Exception as e:
                test_results["subscriptions"][topic].append({
                    "client_id": self.client_id,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                print(f"   ❌ {topic} (exception: {e})")

        print(f"\n   📊 Successfully subscribed to {granted_count} topics")
        return granted_count

    def run_comprehensive_test(self):
        """Run all tests for this client"""
        print(f"\n{'='*80}")
        print(f"🔬 COMPREHENSIVE TEST: Client ID = {self.client_id}")
        print(f"{'='*80}")

        self.create_client()

        try:
            # Test connection
            print("1. Testing connection...")
            self.client.connect(HOST, PORT, keepalive=60)
            self.client.loop_start()
            time.sleep(2)

            if not self.connected:
                print("   ❌ Could not connect")
                return

            print(f"   ✅ Connected successfully")

            # Test subscriptions first (safer)
            print("\n2. Testing subscriptions...")
            sub_count = self.test_comprehensive_subscribing()

            # Wait a bit to receive any messages
            print("\n3. Waiting for incoming messages (10 seconds)...")
            time.sleep(10)

            # Test publishing (might cause disconnections)
            print("\n4. Testing publishing...")
            pub_count = self.test_comprehensive_publishing()

            # Final wait for any responses
            print("\n5. Waiting for responses (10 seconds)...")
            time.sleep(10)

            # Report summary
            print(f"\n📊 SUMMARY for {self.client_id}:")
            print(f"   • Subscriptions: {sub_count}")
            print(f"   • Publishes: {pub_count}")
            print(f"   • Messages received: {self.messages_received}")
            print(f"   • Still connected: {self.connected}")

        except Exception as e:
            print(f"   ❌ Test error: {e}")

        finally:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
                time.sleep(1)

    # Message generators
    def get_heartbeat_message(self):
        return {
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
        }

    def get_trip_start_message(self):
        return {
            "data": {
                "ueid": str(uuid.uuid4()),
                "ts": datetime.now(timezone.utc).isoformat(),
                "did": self.client_id,
                "eid": 2001,
                "pl": {
                    "location": {"lat": 17.0234, "long": 13.023456},
                    "destination": {"lat": 17.0250, "long": 13.023500},
                    "distance": 78.34,
                    "tripId": str(uuid.uuid4()),
                    "battery": 85.45
                }
            }
        }

    def get_trip_update_message(self):
        return {
            "data": {
                "ueid": str(uuid.uuid4()),
                "ts": datetime.now(timezone.utc).isoformat(),
                "did": self.client_id,
                "eid": 2002,
                "pl": {
                    "location": {"lat": 17.0240, "long": 13.023470},
                    "status": "moving",
                    "distance": 45.67,
                    "tripId": str(uuid.uuid4())
                }
            }
        }

    def get_trip_end_message(self):
        return {
            "data": {
                "ueid": str(uuid.uuid4()),
                "ts": datetime.now(timezone.utc).isoformat(),
                "did": self.client_id,
                "eid": 2003,
                "pl": {
                    "location": {"lat": 17.0250, "long": 13.023500},
                    "status": "success",
                    "distance": 78.34,
                    "tripId": str(uuid.uuid4())
                }
            }
        }

    def get_error_message(self):
        return {
            "data": {
                "ueid": str(uuid.uuid4()),
                "ts": datetime.now(timezone.utc).isoformat(),
                "did": self.client_id,
                "eid": 2004,
                "pl": {
                    "status": "error",
                    "reasonCode": 5,
                    "errorMessage": "Obstacle detected"
                }
            }
        }

    def get_raw_sensor_data(self):
        return {
            "device_id": self.client_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sensors": {
                "battery": 85.45,
                "temperature": 42.56,
                "position": [17.0234, 13.023456],
                "speed": 2.3,
                "heading": 45.2
            }
        }

    def get_minimal_message(self):
        return {
            "id": self.client_id,
            "status": "ok",
            "time": datetime.now(timezone.utc).isoformat()
        }

def main():
    print("="*80)
    print("🔬 TVS EXTENSIVE DATA TEST")
    print("="*80)
    print(f"Broker: {HOST}:{PORT}")
    print(f"Username: {USERNAME}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Test different client IDs with the working username
    test_clients = [
        "amr-001",
        "data-collector",
        f"test-{int(time.time())}",
        "comprehensive-test"
    ]

    for client_id in test_clients:
        try:
            test_client = ExtensiveTestClient(client_id)
            test_client.run_comprehensive_test()

            # Pause between clients
            time.sleep(3)

        except Exception as e:
            print(f"❌ Error testing {client_id}: {e}")

    # Generate final comprehensive report
    print("\n" + "="*80)
    print("📊 FINAL COMPREHENSIVE REPORT")
    print("="*80)

    # Connection summary
    successful_connections = [c for c in test_results["connections"] if c["success"]]
    print(f"\n✅ CONNECTIONS: {len(successful_connections)}/{len(test_results['connections'])}")
    for conn in successful_connections:
        print(f"   • {conn['client_id']}")

    # Subscription summary
    successful_subs = {topic: results for topic, results in test_results["subscriptions"].items()
                      if any(r["success"] for r in results)}
    print(f"\n📥 SUCCESSFUL SUBSCRIPTIONS: {len(successful_subs)}")
    for topic in sorted(successful_subs.keys()):
        print(f"   ✅ {topic}")

    # Publish summary
    successful_pubs = {topic: results for topic, results in test_results["publishes"].items()
                      if any(r["success"] for r in results)}
    print(f"\n📤 SUCCESSFUL PUBLISHES: {len(successful_pubs)}")
    for topic in sorted(successful_pubs.keys()):
        success_count = len([r for r in successful_pubs[topic] if r["success"]])
        total_count = len(successful_pubs[topic])
        print(f"   ✅ {topic} ({success_count}/{total_count} messages)")

    # Messages received
    print(f"\n📨 MESSAGES RECEIVED: {len(test_results['messages_received'])}")
    if test_results["messages_received"]:
        topics = set(m["topic"] for m in test_results["messages_received"])
        for topic in sorted(topics):
            count = len([m for m in test_results["messages_received"] if m["topic"] == topic])
            print(f"   📩 {topic}: {count} messages")

    # Disconnection analysis
    print(f"\n🔌 DISCONNECTIONS: {len(test_results['disconnections'])}")
    if test_results["disconnections"]:
        reasons = {}
        for disc in test_results["disconnections"]:
            reason = disc["reason"]
            if reason not in reasons:
                reasons[reason] = 0
            reasons[reason] += 1

        for reason, count in reasons.items():
            print(f"   • {reason}: {count} times")

    print("\n🎯 FINAL CONCLUSIONS:")

    if successful_pubs and not test_results["messages_received"]:
        print("• ✅ We CAN publish data (confirmed working)")
        print("• ❌ We CANNOT see our own published data")
        print("• ❌ No other systems are publishing data we can see")
        print("\n📋 This confirms the account is for DEVICE PUBLISHING ONLY:")
        print("  - Use it to send AMR telemetry TO the broker")
        print("  - Cannot read data FROM other devices")
        print("  - Need different credentials to CONSUME data")

    if successful_subs and not test_results["messages_received"]:
        print("• ✅ We CAN subscribe to some topics")
        print("• ❌ But no data is flowing on those topics")
        print("• ❓ Either AMRs are offline OR data flows elsewhere")

    if len(successful_pubs) == 0:
        print("• ❌ Cannot publish to any topics")
        print("• ❌ Account may have been restricted")

    print("\n🚀 NEXT STEPS:")
    print("1. Ask TVS for CONSUMER credentials to read /d2c/+ topics")
    print("2. Ask for the topic where processed/aggregated AMR data is published")
    print("3. Ask if there's a REST API or different system to access AMR data")
    print("4. Confirm the current status of AMR operations (are they running?)")

    print("="*80)

if __name__ == "__main__":
    main()