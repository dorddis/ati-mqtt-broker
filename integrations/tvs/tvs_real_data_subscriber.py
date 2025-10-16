#!/usr/bin/env python3
"""
TVS Real Data Subscriber
Connects to actual TVS MQTT broker to capture and analyze real AMR data
"""
import json
import time
import ssl
from datetime import datetime
import paho.mqtt.client as mqtt
from collections import defaultdict
import statistics

# TVS MQTT Broker Configuration from email
MQTT_HOST = "tvs-dev.ifactory.ai"
MQTT_PORT = 8883  # TLS port
MQTT_CLIENT_ID = "amr-001"
MQTT_USERNAME = "amr-001"
MQTT_PASSWORD = "TVSamr001@2025"

# AMR MAC Addresses from email
AMR_MACS = {
    "f4:7b:09:0e:04:1b": "Tug 133",
    "10:3d:1c:66:67:55": "Tug 39",
    "f4:4e:e3:f6:c7:91": "Tug 55",
    "ec:2e:98:4a:7c:f7": "Tug 78"
}

# Data collection
message_count = 0
device_data = defaultdict(list)
raw_messages = []
unique_topics = set()
field_analysis = defaultdict(set)

def analyze_message_structure(data, prefix=""):
    """Recursively analyze message structure and collect field types"""
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            field_analysis[full_key].add(type(value).__name__)
            if isinstance(value, (dict, list)):
                analyze_message_structure(value, full_key)
    elif isinstance(data, list) and data:
        for i, item in enumerate(data[:3]):  # Analyze first 3 items
            analyze_message_structure(item, f"{prefix}[{i}]")

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for MQTT connection"""
    if rc == 0:
        print("✅ Connected to TVS MQTT broker successfully!")
        print(f"🔗 Host: {MQTT_HOST}:{MQTT_PORT}")
        print(f"👤 Client ID: {MQTT_CLIENT_ID}")
        print(f"🔐 Username: {MQTT_USERNAME}")
        print("-" * 70)

        # Subscribe to all topics to discover what's available
        # Common AMR topics
        topics_to_try = [
            "amr/+/status",
            "amr/+/position",
            "amr/+/location",
            "amr/+/telemetry",
            "robot/+/status",
            "robot/+/position",
            "tug/+/status",
            "tug/+/position",
            "fleet/+/status",
            "tvs/+/status",
            "+/amr/+",
            "+/robot/+",
            "+/tug/+",
            "+/fleet/+",
            "#"  # Subscribe to everything as fallback
        ]

        print("🔍 Subscribing to potential AMR topics...")
        for topic in topics_to_try:
            try:
                result = client.subscribe(topic, qos=1)
                print(f"   📡 Subscribed to: {topic} (result: {result})")
            except Exception as e:
                print(f"   ❌ Failed to subscribe to {topic}: {e}")

        print("-" * 70)
        print("🎯 Listening for messages... (Ctrl+C to stop and analyze)")
        print("-" * 70)

    else:
        print(f"❌ Connection failed with code: {rc}")
        error_codes = {
            1: "Incorrect protocol version",
            2: "Invalid client identifier",
            3: "Server unavailable",
            4: "Bad username or password",
            5: "Not authorized"
        }
        print(f"   Error: {error_codes.get(rc, 'Unknown error')}")

def on_message(client, userdata, msg):
    """Callback for received MQTT messages"""
    global message_count
    message_count += 1

    try:
        topic = msg.topic
        unique_topics.add(topic)

        # Try to decode as JSON
        try:
            data = json.loads(msg.payload.decode('utf-8'))
            is_json = True
        except:
            # If not JSON, treat as raw string
            data = msg.payload.decode('utf-8', errors='ignore')
            is_json = False

        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        # Store raw message for analysis
        raw_messages.append({
            'timestamp': timestamp,
            'topic': topic,
            'data': data,
            'is_json': is_json,
            'qos': msg.qos,
            'retain': msg.retain
        })

        # Real-time display
        print(f"📦 [{timestamp}] Topic: {topic}")

        if is_json:
            # Analyze structure
            analyze_message_structure(data)

            # Extract device info if possible
            device_id = None
            for key in ['device_id', 'robot_id', 'amr_id', 'tug_id', 'id', 'name', 'sherpa_name']:
                if key in data:
                    device_id = data[key]
                    break

            if device_id:
                device_data[device_id].append({
                    'timestamp': timestamp,
                    'topic': topic,
                    'data': data
                })

            # Pretty print JSON with relevant fields highlighted
            print("   📊 Data:")
            if isinstance(data, dict):
                # Show key fields first
                key_fields = ['id', 'name', 'device_id', 'robot_id', 'amr_id', 'tug_id', 'sherpa_name',
                             'x', 'y', 'z', 'position', 'pose', 'location', 'coordinates',
                             'battery', 'battery_status', 'charge', 'status', 'state', 'mode',
                             'speed', 'velocity', 'heading', 'orientation', 'angle']

                shown_fields = set()
                for field in key_fields:
                    if field in data:
                        print(f"      🔹 {field}: {data[field]}")
                        shown_fields.add(field)

                # Show remaining fields
                for key, value in data.items():
                    if key not in shown_fields:
                        if len(str(value)) > 100:
                            print(f"      • {key}: {str(value)[:100]}...")
                        else:
                            print(f"      • {key}: {value}")
            else:
                print(f"      {json.dumps(data, indent=6)}")
        else:
            print(f"   📝 Raw data: {data}")

        print("-" * 70)

        # Keep only last 1000 messages to avoid memory issues
        if len(raw_messages) > 1000:
            raw_messages.pop(0)

    except Exception as e:
        print(f"❌ Error processing message: {e}")
        print(f"   Topic: {msg.topic}")
        print(f"   Raw payload: {msg.payload}")
        print("-" * 70)

def on_disconnect(client, userdata, rc, properties=None, reasonCode=None):
    """Callback for MQTT disconnection"""
    print(f"\n🔌 Disconnected from MQTT broker (code: {rc})")

def print_analysis_summary():
    """Print comprehensive analysis of collected data"""
    print("\n" + "="*80)
    print("📊 TVS MQTT DATA ANALYSIS SUMMARY")
    print("="*80)

    print(f"\n📈 MESSAGE STATISTICS:")
    print(f"   Total messages received: {message_count}")
    print(f"   Unique topics discovered: {len(unique_topics)}")
    print(f"   Devices identified: {len(device_data)}")

    print(f"\n📡 TOPICS DISCOVERED:")
    for topic in sorted(unique_topics):
        topic_count = sum(1 for msg in raw_messages if msg['topic'] == topic)
        print(f"   • {topic} ({topic_count} messages)")

    print(f"\n🤖 DEVICES IDENTIFIED:")
    for device_id, messages in device_data.items():
        print(f"   • {device_id}: {len(messages)} messages")

        # Check if this matches any known MAC
        for mac, name in AMR_MACS.items():
            if mac in device_id or device_id in name.lower():
                print(f"     🎯 Matches known AMR: {name} ({mac})")

    print(f"\n📋 FIELD ANALYSIS:")
    for field, types in sorted(field_analysis.items()):
        print(f"   • {field}: {', '.join(types)}")

    if raw_messages:
        print(f"\n📝 SAMPLE MESSAGES:")
        # Show first few messages of each type
        shown_topics = set()
        for msg in raw_messages[:20]:
            if msg['topic'] not in shown_topics:
                shown_topics.add(msg['topic'])
                print(f"\n   Topic: {msg['topic']}")
                if msg['is_json']:
                    print(f"   Data: {json.dumps(msg['data'], indent=8)}")
                else:
                    print(f"   Data: {msg['data']}")

                if len(shown_topics) >= 5:  # Limit sample output
                    break

    # Save detailed analysis to file
    analysis_file = f"tvs_data_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_file, 'w') as f:
        json.dump({
            'summary': {
                'total_messages': message_count,
                'unique_topics': list(unique_topics),
                'devices': list(device_data.keys()),
                'field_analysis': {k: list(v) for k, v in field_analysis.items()}
            },
            'raw_messages': raw_messages[-100:],  # Last 100 messages
            'device_data': {k: v[-10:] for k, v in device_data.items()}  # Last 10 per device
        }, f, indent=2, default=str)

    print(f"\n💾 Detailed analysis saved to: {analysis_file}")
    print("="*80)

def main():
    """Main function to run the TVS data subscriber"""

    print("🔍 TVS REAL DATA SUBSCRIBER")
    print("="*50)
    print(f"Host: {MQTT_HOST}:{MQTT_PORT}")
    print(f"Client ID: {MQTT_CLIENT_ID}")
    print(f"Username: {MQTT_USERNAME}")
    print(f"Known AMRs: {len(AMR_MACS)} devices")
    for mac, name in AMR_MACS.items():
        print(f"   • {name}: {mac}")
    print("="*50)

    # Create MQTT client with MQTT5 protocol
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv5)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Configure TLS/SSL
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    client.tls_set_context(context)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        # Connect to broker
        print("🔗 Connecting to TVS MQTT broker...")
        client.connect(MQTT_HOST, MQTT_PORT, 60)

        # Start the loop
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n🛑 Stopping TVS data subscriber...")
        client.disconnect()
        print_analysis_summary()

    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if the TVS broker is accessible")
        print("   2. Verify credentials are correct")
        print("   3. Confirm firewall allows outbound connections on port 8883")
        print("   4. Try connecting from TVS network if behind firewall")

if __name__ == "__main__":
    main()