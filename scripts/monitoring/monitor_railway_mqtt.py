#!/usr/bin/env python3
"""
Monitor Railway MQTT Broker
Watch ATI data and system health in real-time
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
from datetime import datetime
import argparse

class RailwayMQTTMonitor:
    def __init__(self, broker_url, username, password):
        self.broker_url = broker_url
        self.username = username
        self.password = password
        self.message_count = 0
        self.connected = False

        # Extract host from URL
        self.host = broker_url.replace('wss://', '').replace('ws://', '')
        self.port = 443 if 'wss://' in broker_url else 80

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print(f"✅ Connected to Railway MQTT at {datetime.now().strftime('%H:%M:%S')}")
            print(f"🌐 Broker: {self.broker_url}")

            # Subscribe to all ATI topics
            topics = [
                ("ati/+/status", 1),
                ("ati/+/position", 1),
                ("amr/+/status", 1),
                ("amr/+/telemetry", 1),
                ("#", 0)  # Catch-all for debugging
            ]

            for topic, qos in topics:
                client.subscribe(topic, qos)
                print(f"📡 Subscribed to: {topic}")

        else:
            print(f"❌ Connection failed: {rc}")

    def on_message(self, client, userdata, msg):
        self.message_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        print(f"\n🎉 ATI MESSAGE #{self.message_count} at {timestamp}")
        print(f"   📍 Topic: {msg.topic}")
        print(f"   📦 Size: {len(msg.payload)} bytes")

        try:
            data = json.loads(msg.payload.decode('utf-8'))

            # Pretty print JSON
            print("   📄 Data:")
            print(json.dumps(data, indent=6))

            # Extract key information
            if isinstance(data, dict):
                if "data" in data:
                    inner_data = data["data"]
                    if "eid" in inner_data:
                        event_types = {
                            2001: "❤️ Heartbeat/Trip Start",
                            2002: "🚶 Trip Update",
                            2003: "🏁 Trip End/Error"
                        }
                        eid = inner_data["eid"]
                        print(f"   🏷️  Event: {event_types.get(eid, f'Unknown ({eid})')}")

                    if "pl" in inner_data:
                        payload = inner_data["pl"]
                        if "battery" in payload:
                            battery = payload["battery"]
                            if battery < 20:
                                print(f"   🔋 Battery: {battery}% ⚠️ LOW")
                            else:
                                print(f"   🔋 Battery: {battery}%")

                        if "location" in payload:
                            loc = payload["location"]
                            print(f"   🗺️  Location: {loc.get('lat', '?')}, {loc.get('long', '?')}")

        except json.JSONDecodeError:
            # Not JSON, show raw
            payload_str = msg.payload.decode('utf-8', errors='ignore')
            print(f"   📝 Raw: {payload_str[:200]}")
        except Exception as e:
            print(f"   ❌ Parse error: {e}")

        print("-" * 80)

    def on_disconnect(self, client, userdata, rc, properties=None, reasonCode=None):
        self.connected = False
        print(f"\n🔌 Disconnected from Railway broker")
        if reasonCode:
            print(f"   Reason: {reasonCode}")

    def monitor(self):
        print("="*80)
        print("🔍 RAILWAY MQTT MONITOR - ATI Data Stream")
        print("="*80)
        print(f"🌐 Broker: {self.broker_url}")
        print(f"👤 User: {self.username}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Create client for WebSocket connection
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"railway-monitor-{int(time.time())}",
            transport="websockets"
        )

        # Set credentials
        client.username_pw_set(self.username, self.password)

        # Configure TLS for wss://
        if 'wss://' in self.broker_url:
            client.tls_set()

        # Set callbacks
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        try:
            print(f"🔗 Connecting to {self.host}:{self.port}...")
            client.connect(self.host, self.port, 60)
            client.loop_forever()

        except KeyboardInterrupt:
            print("\n⚠️ Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            client.disconnect()
            print(f"\n📊 Session Summary:")
            print(f"   Total messages received: {self.message_count}")

def main():
    parser = argparse.ArgumentParser(description="Monitor Railway MQTT Broker")
    parser.add_argument("--url", default="wss://your-app.railway.app",
                       help="Railway MQTT WebSocket URL")
    parser.add_argument("--username", default="ati_user",
                       help="MQTT username")
    parser.add_argument("--password", default="ati_password_123",
                       help="MQTT password")

    args = parser.parse_args()

    monitor = RailwayMQTTMonitor(args.url, args.username, args.password)
    monitor.monitor()

if __name__ == "__main__":
    main()
