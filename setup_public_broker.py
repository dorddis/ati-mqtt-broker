#!/usr/bin/env python3
"""
Setup Public MQTT Broker Integration
Immediate solution using free public brokers while setting up hosting
"""
import json
from datetime import datetime

def create_public_broker_configs():
    """Create configs for popular public MQTT brokers"""

    public_brokers = {
        "emqx": {
            "name": "EMQX Public Broker",
            "host": "broker.emqx.io",
            "port": 1883,
            "websocket_port": 8083,
            "websocket_path": "/mqtt",
            "ssl_port": 8883,
            "websocket_ssl_port": 8084,
            "auth": None,
            "reliability": "High",
            "websocket_url": "ws://broker.emqx.io:8083/mqtt"
        },
        "hivemq": {
            "name": "HiveMQ Public Broker",
            "host": "broker.hivemq.com",
            "port": 1883,
            "websocket_port": 8000,
            "websocket_path": "/mqtt",
            "ssl_port": None,
            "websocket_ssl_port": None,
            "auth": None,
            "reliability": "High",
            "websocket_url": "ws://broker.hivemq.com:8000/mqtt"
        },
        "mosquitto": {
            "name": "Eclipse Mosquitto Test Server",
            "host": "test.mosquitto.org",
            "port": 1883,
            "websocket_port": 8080,
            "websocket_path": "/",
            "ssl_port": 8883,
            "websocket_ssl_port": 8081,
            "auth": None,
            "reliability": "Medium",
            "websocket_url": "ws://test.mosquitto.org:8080/"
        }
    }

    with open("public_brokers.json", "w") as f:
        json.dump(public_brokers, f, indent=2)

    print("✅ Created public_brokers.json")

def create_ati_public_instructions():
    """Create instructions for ATI to use public brokers"""

    instructions = """# ATI Public MQTT Broker Setup (Immediate Solution)

## Quick Start - 5 Minutes to Working Integration

While we set up permanent hosting, ATI can immediately start publishing to a public MQTT broker.

### Option 1: EMQX Public Broker (Recommended)

**For ATI Team:**
```javascript
// Change your MQTT connection to:
const broker = 'ws://broker.emqx.io:8083/mqtt'

// Everything else stays the same!
// Your existing topics: ati/amr/status, ati/position, etc.
```

**Connection Details:**
- **WebSocket URL:** `ws://broker.emqx.io:8083/mqtt`
- **Host:** `broker.emqx.io`
- **Port:** 8083 (WebSocket) or 1883 (direct MQTT)
- **Auth:** No username/password needed
- **Topics:** Use any topics (recommend: `ati/amr/status`, `ati/position`, etc.)

### Option 2: HiveMQ Public Broker

**For ATI Team:**
```javascript
const broker = 'ws://broker.hivemq.com:8000/mqtt'
```

## Data Privacy Note

⚠️ **Important:** Public brokers are visible to anyone.
- Don't publish sensitive data
- Perfect for testing and development
- Consider using random prefixes: `test-123/ati/amr/status`

## Our Integration Setup

**We monitor the same broker:**
```python
# Our bridge connects to same public broker
MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
TOPICS = ["ati/+/status", "ati/+/position", "#"]
```

**Result:** Working integration in 5 minutes! ✅

## Upgrade Path

1. **Phase 1:** Use public broker (immediate)
2. **Phase 2:** Deploy to Render (permanent, private)
3. **Phase 3:** ATI switches to private broker URL

## Testing Commands

**For ATI to test:**
```bash
# Install mosquitto client
# Windows: Download from mosquitto.org
# Mac: brew install mosquitto
# Linux: apt install mosquitto-clients

# Test publish
mosquitto_pub -h broker.emqx.io -t ati/test -m "hello world"

# Test subscribe (we'll see this!)
mosquitto_sub -h broker.emqx.io -t "ati/#"
```

**For us to test:**
```bash
# Monitor ATI data
python monitor_public_mqtt.py --broker emqx
```
"""

    with open("ATI_PUBLIC_BROKER_SETUP.md", "w") as f:
        f.write(instructions)

    print("✅ Created ATI_PUBLIC_BROKER_SETUP.md")

def create_public_monitor():
    """Create monitor script for public brokers"""

    monitor_script = '''#!/usr/bin/env python3
"""
Monitor Public MQTT Brokers for ATI Data
Immediate solution while setting up permanent hosting
"""
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import argparse

# Public broker configurations
PUBLIC_BROKERS = {
    "emqx": {
        "host": "broker.emqx.io",
        "port": 1883,
        "name": "EMQX Public Broker",
        "websocket_url": "ws://broker.emqx.io:8083/mqtt"
    },
    "hivemq": {
        "host": "broker.hivemq.com",
        "port": 1883,
        "name": "HiveMQ Public Broker",
        "websocket_url": "ws://broker.hivemq.com:8000/mqtt"
    },
    "mosquitto": {
        "host": "test.mosquitto.org",
        "port": 1883,
        "name": "Eclipse Mosquitto Test",
        "websocket_url": "ws://test.mosquitto.org:8080/"
    }
}

class PublicMQTTMonitor:
    def __init__(self, broker_name):
        if broker_name not in PUBLIC_BROKERS:
            raise ValueError(f"Unknown broker: {broker_name}")

        self.broker_config = PUBLIC_BROKERS[broker_name]
        self.broker_name = broker_name
        self.message_count = 0
        self.connected = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print(f"✅ Connected to {self.broker_config['name']}")
            print(f"🌐 Host: {self.broker_config['host']}")
            print(f"📡 WebSocket: {self.broker_config['websocket_url']}")

            # Subscribe to ATI topics
            topics = [
                "ati/+/status",
                "ati/+/position",
                "ati/+/battery",
                "ati/+/telemetry",
                "amr/+/status",
                "amr/+/position",
                "test-123/ati/+/+",  # For testing with prefix
                "#"  # Catch everything for debugging
            ]

            for topic in topics:
                client.subscribe(topic, qos=1)
                print(f"📡 Subscribed to: {topic}")

        else:
            print(f"❌ Connection failed: {rc}")

    def on_message(self, client, userdata, msg):
        self.message_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        print(f"\\n🎉 MESSAGE #{self.message_count} at {timestamp}")
        print(f"   📍 Topic: {msg.topic}")
        print(f"   📦 Size: {len(msg.payload)} bytes")

        try:
            # Try to decode as JSON
            data = json.loads(msg.payload.decode('utf-8'))

            print("   📄 JSON Data:")
            print(json.dumps(data, indent=6)[:400])

            # Extract ATI-specific info
            if isinstance(data, dict):
                if "data" in data and isinstance(data["data"], dict):
                    inner_data = data["data"]

                    # Event type
                    if "eid" in inner_data:
                        event_types = {
                            2001: "❤️ Heartbeat/Trip Start",
                            2002: "🚶 Trip Update",
                            2003: "🏁 Trip End/Error"
                        }
                        eid = inner_data["eid"]
                        print(f"   🏷️ Event: {event_types.get(eid, f'Unknown ({eid})')}")

                    # Device ID
                    if "did" in inner_data:
                        print(f"   🤖 Device: {inner_data['did']}")

                    # Payload details
                    if "pl" in inner_data:
                        payload = inner_data["pl"]
                        if "battery" in payload:
                            battery = payload["battery"]
                            emoji = "🔋" if battery >= 20 else "🪫"
                            print(f"   {emoji} Battery: {battery}%")

                        if "location" in payload:
                            loc = payload["location"]
                            print(f"   🗺️ Location: {loc.get('lat', '?')}, {loc.get('long', '?')}")

                        if "status" in payload:
                            status_emoji = {
                                "moving": "🚶",
                                "idle": "⏸️",
                                "charging": "🔌",
                                "error": "❌"
                            }
                            status = payload["status"]
                            emoji = status_emoji.get(status, "❓")
                            print(f"   {emoji} Status: {status}")

        except json.JSONDecodeError:
            # Not JSON, show raw
            payload_str = msg.payload.decode('utf-8', errors='ignore')
            print(f"   📝 Raw: {payload_str[:200]}")
        except Exception as e:
            print(f"   ❌ Parse error: {e}")

        print("-" * 70)

    def on_disconnect(self, client, userdata, rc, properties=None, reasonCode=None):
        self.connected = False
        print(f"\\n🔌 Disconnected from {self.broker_config['name']}")

    def monitor(self):
        print("="*80)
        print(f"🔍 PUBLIC MQTT MONITOR - {self.broker_config['name']}")
        print("="*80)
        print(f"🌐 Host: {self.broker_config['host']}:{self.broker_config['port']}")
        print(f"📡 WebSocket: {self.broker_config['websocket_url']}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("⚠️ Public broker - visible to all users")
        print("="*80)

        # Create MQTT client
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"public-monitor-{int(time.time())}"
        )

        # Set callbacks
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        try:
            print(f"🔗 Connecting to {self.broker_config['host']}...")
            client.connect(self.broker_config['host'], self.broker_config['port'], 60)
            client.loop_forever()

        except KeyboardInterrupt:
            print("\\n⚠️ Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            client.disconnect()
            print(f"\\n📊 Session Summary: {self.message_count} messages received")

def main():
    parser = argparse.ArgumentParser(description="Monitor Public MQTT Brokers")
    parser.add_argument("--broker", choices=list(PUBLIC_BROKERS.keys()),
                       default="emqx", help="Public broker to monitor")

    args = parser.parse_args()

    print(f"🚀 Starting monitor for {args.broker} broker...")
    print("💡 Tell ATI to publish to:")
    config = PUBLIC_BROKERS[args.broker]
    print(f"   WebSocket: {config['websocket_url']}")
    print(f"   Direct MQTT: {config['host']}:{config['port']}")
    print("\\nPress Ctrl+C to stop\\n")

    monitor = PublicMQTTMonitor(args.broker)
    monitor.monitor()

if __name__ == "__main__":
    main()
'''

    with open("monitor_public_mqtt.py", "w") as f:
        f.write(monitor_script)

    # Make executable
    os.chmod("monitor_public_mqtt.py", 0o755)

    print("✅ Created monitor_public_mqtt.py")

def create_ati_test_script():
    """Create test script for ATI to verify connection"""

    test_script = '''#!/usr/bin/env python3
"""
ATI Test Script - Verify MQTT Connection
Quick test to confirm ATI can publish to public broker
"""
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime, timezone
import uuid

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to public MQTT broker!")
        print("🚀 Starting to publish test data...")
    else:
        print(f"❌ Connection failed: {rc}")

def publish_test_data(client):
    """Publish test AMR data"""

    # Test message in ATI format
    test_message = {
        "data": {
            "ueid": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "did": "ati-test-device",
            "eid": 2001,  # Heartbeat
            "pl": {
                "location": {
                    "lat": 17.0234,
                    "long": 13.023456
                },
                "battery": 85.5,
                "status": "moving",
                "temperature": 42.3,
                "uptime": "2h 15m 30s"
            }
        }
    }

    topic = "test-123/ati/amr/status"
    payload = json.dumps(test_message)

    result = client.publish(topic, payload, qos=1)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"✅ Published test message to: {topic}")
        print(f"📦 Message ID: {test_message['data']['ueid'][:8]}...")
        return True
    else:
        print(f"❌ Publish failed: {result.rc}")
        return False

def main():
    print("="*60)
    print("🧪 ATI MQTT CONNECTION TEST")
    print("="*60)
    print("Testing connection to EMQX public broker...")
    print("If this works, ATI integration is ready!")
    print("="*60)

    # Connect to EMQX public broker
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"ati-test-{int(time.time())}"
    )

    client.on_connect = on_connect

    try:
        print("🔗 Connecting to broker.emqx.io...")
        client.connect("broker.emqx.io", 1883, 60)
        client.loop_start()

        time.sleep(2)  # Wait for connection

        # Publish test messages
        success_count = 0
        for i in range(3):
            if publish_test_data(client):
                success_count += 1
            time.sleep(1)

        print(f"\\n📊 Published {success_count}/3 test messages")

        if success_count == 3:
            print("\\n🎉 SUCCESS! ATI can publish to public broker")
            print("\\n📋 Next steps for ATI:")
            print("1. Change broker URL to: ws://broker.emqx.io:8083/mqtt")
            print("2. Keep same topics: ati/amr/status, etc.")
            print("3. We'll see your data immediately!")
        else:
            print("\\n⚠️ Some publishes failed - check connection")

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''

    with open("ati_connection_test.py", "w") as f:
        f.write(test_script)

    # Make executable
    os.chmod("ati_connection_test.py", 0o755)

    print("✅ Created ati_connection_test.py")

def main():
    print("🚀 Setting up Public MQTT Broker Integration")
    print("="*60)
    print("Immediate solution while permanent hosting is being set up")
    print("="*60)

    create_public_broker_configs()
    create_ati_public_instructions()
    create_public_monitor()
    create_ati_test_script()

    print("\\n" + "="*60)
    print("✅ PUBLIC BROKER SETUP COMPLETE!")
    print("="*60)

    print("\\n🚀 IMMEDIATE SOLUTION (5 minutes):")
    print("1. Tell ATI to use public broker:")
    print("   WebSocket: ws://broker.emqx.io:8083/mqtt")
    print("   Topics: ati/amr/status, ati/position, etc.")
    print()
    print("2. Start monitoring:")
    print("   python monitor_public_mqtt.py --broker emqx")
    print()
    print("3. Test connection:")
    print("   python ati_connection_test.py")
    print()
    print("💡 BENEFITS:")
    print("   ✅ Works immediately (no setup)")
    print("   ✅ No coordination needed")
    print("   ✅ Both teams connect to same broker")
    print("   ✅ Permanent URL (broker.emqx.io)")
    print()
    print("⚠️ CONSIDERATIONS:")
    print("   • Public broker (visible to others)")
    print("   • Good for testing/development")
    print("   • Upgrade to private hosting later")
    print("="*60)

if __name__ == "__main__":
    main()