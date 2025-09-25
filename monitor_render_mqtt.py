#!/usr/bin/env python3
"""
Monitor Render MQTT Broker
Watch ATI data and handle sleep/wake cycle
"""
import paho.mqtt.client as mqtt
import json
import ssl
import time
import requests
import threading
from datetime import datetime

class RenderMQTTMonitor:
    def __init__(self, render_url, username="ati_user", password="ati_password_123"):
        self.render_url = render_url
        self.username = username
        self.password = password
        self.message_count = 0
        self.connected = False

        # Extract WebSocket URL
        self.ws_url = render_url.replace('https://', 'wss://').rstrip('/')
        self.host = render_url.replace('https://', '').replace('http://', '').rstrip('/')

    def keep_alive(self):
        """Send HTTP requests to keep Render service awake"""
        while True:
            try:
                response = requests.get(f"https://{self.host}/health", timeout=10)
                if response.status_code == 200:
                    print(f"⏰ Keep-alive ping successful at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    print(f"⚠️ Keep-alive returned {response.status_code}")
            except Exception as e:
                print(f"⚠️ Keep-alive failed: {e}")

            time.sleep(300)  # Ping every 5 minutes (well under 15min sleep)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print(f"✅ Connected to Render MQTT at {datetime.now().strftime('%H:%M:%S')}")
            print(f"🌐 Broker: {self.ws_url}")

            # Subscribe to all ATI topics
            topics = [
                ("ati/+/status", 1),
                ("ati/+/position", 1),
                ("amr/+/status", 1),
                ("amr/+/telemetry", 1),
                ("keepalive", 0),
                ("#", 0)  # Catch all
            ]

            for topic, qos in topics:
                client.subscribe(topic, qos)
                print(f"📡 Subscribed to: {topic}")

        else:
            print(f"❌ Connection failed: {rc}")
            if rc == 1:
                print("   Error: Incorrect protocol version")
            elif rc == 2:
                print("   Error: Invalid client ID")
            elif rc == 3:
                print("   Error: Server unavailable (service may be sleeping)")
                print("   💡 Trying to wake up service...")
                requests.get(f"https://{self.host}/health")
            elif rc == 4:
                print("   Error: Bad username/password")
            elif rc == 5:
                print("   Error: Not authorized")

    def on_message(self, client, userdata, msg):
        self.message_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        # Skip keepalive messages in detailed output
        if msg.topic == "keepalive":
            print(f"💓 Keepalive at {timestamp}")
            return

        print(f"\n🎉 ATI MESSAGE #{self.message_count} at {timestamp}")
        print(f"   📍 Topic: {msg.topic}")
        print(f"   📦 Size: {len(msg.payload)} bytes")

        try:
            data = json.loads(msg.payload.decode('utf-8'))
            print("   📄 Data:")
            print(json.dumps(data, indent=6)[:500])

            # Extract key info
            if isinstance(data, dict) and "data" in data:
                inner_data = data["data"]
                if "eid" in inner_data:
                    event_types = {
                        2001: "❤️ Heartbeat/Trip Start",
                        2002: "🚶 Trip Update",
                        2003: "🏁 Trip End/Error"
                    }
                    eid = inner_data["eid"]
                    print(f"   🏷️ Event: {event_types.get(eid, f'Unknown ({eid})')}")

        except json.JSONDecodeError:
            payload_str = msg.payload.decode('utf-8', errors='ignore')
            print(f"   📝 Raw: {payload_str[:200]}")
        except Exception as e:
            print(f"   ❌ Parse error: {e}")

        print("-" * 60)

    def on_disconnect(self, client, userdata, rc, properties=None, reasonCode=None):
        self.connected = False
        print(f"\n🔌 Disconnected from Render broker")
        if reasonCode:
            print(f"   Reason: {reasonCode}")

    def monitor(self):
        print("="*80)
        print("🔍 RENDER MQTT MONITOR - ATI Data Stream")
        print("="*80)
        print(f"🌐 Render URL: {self.render_url}")
        print(f"🔌 WebSocket: {self.ws_url}")
        print(f"👤 Username: {self.username}")
        print(f"⏰ Keep-alive: Every 5 minutes")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Start keep-alive thread
        keepalive_thread = threading.Thread(target=self.keep_alive, daemon=True)
        keepalive_thread.start()

        # Create MQTT client for WebSocket
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"render-monitor-{int(time.time())}",
            transport="websockets"
        )

        # Set credentials
        client.username_pw_set(self.username, self.password)

        # Configure TLS for WSS
        client.tls_set()

        # Set callbacks
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        try:
            print(f"🔗 Connecting to {self.host}...")
            client.connect(self.host, 443, 60)
            client.loop_forever()

        except KeyboardInterrupt:
            print("\n⚠️ Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            client.disconnect()
            print(f"\n📊 Session Summary:")
            print(f"   Messages received: {self.message_count}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Monitor Render MQTT Broker")
    parser.add_argument("--url", default="https://your-app.onrender.com",
                       help="Render app URL")
    parser.add_argument("--username", default="ati_user",
                       help="MQTT username")
    parser.add_argument("--password", default="ati_password_123",
                       help="MQTT password")

    args = parser.parse_args()

    monitor = RenderMQTTMonitor(args.url, args.username, args.password)
    monitor.monitor()

if __name__ == "__main__":
    main()
