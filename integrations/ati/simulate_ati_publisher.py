#!/usr/bin/env python3
"""
Simulate ATI publishing data to our MQTT broker
This is what ATI would run on their side
"""
import paho.mqtt.client as mqtt
import json
import time
import random

# Connection to OUR broker (would be ngrok in real scenario)
MQTT_HOST = "localhost"  # In real scenario: "0.tcp.ngrok.io"
MQTT_PORT = 1883         # In real scenario: 12345 (ngrok port)

class ATIDataSimulator:
    def __init__(self):
        self.client = None
        self.connected = False
        self.robots = [
            {
                "sherpa_name": "tugger-001",
                "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
                "battery_status": 85.2
            },
            {
                "sherpa_name": "lifter-002",
                "pose": [195700.45, 188420.12, 0.0, 0.0, 0.0, 0.78],
                "battery_status": 73.8
            },
            {
                "sherpa_name": "carrier-003",
                "pose": [195580.90, 188350.34, 0.0, 0.0, 0.0, 2.34],
                "battery_status": 91.5
            }
        ]

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ [ATI] Connected to MQTT broker!")
            self.connected = True
        else:
            print(f"❌ [ATI] Connection failed: {rc}")
            self.connected = False

    def on_publish(self, client, userdata, mid, reasonCode=None, properties=None):
        print(f"📤 [ATI] Message {mid} published successfully")

    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        print(f"🔌 [ATI] Disconnected from broker: {rc}")
        self.connected = False

    def connect_to_broker(self):
        """Connect to our MQTT broker"""
        print(f"🔗 [ATI] Connecting to broker at {MQTT_HOST}:{MQTT_PORT}")

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ati_publisher")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect

        try:
            self.client.connect(MQTT_HOST, MQTT_PORT, 60)
            self.client.loop_start()

            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5

            if self.connected:
                print("✅ [ATI] Successfully connected and ready to publish!")
                return True
            else:
                print("❌ [ATI] Connection timeout")
                return False

        except Exception as e:
            print(f"❌ [ATI] Connection error: {e}")
            return False

    def simulate_movement(self, robot):
        """Simulate realistic robot movement"""
        # Small random movement
        robot["pose"][0] += random.uniform(-5.0, 5.0)
        robot["pose"][1] += random.uniform(-3.0, 3.0)
        robot["pose"][5] += random.uniform(-0.1, 0.1)  # Rotation

        # Battery slowly drains
        robot["battery_status"] -= random.uniform(0.01, 0.05)
        robot["battery_status"] = max(20.0, robot["battery_status"])

    def publish_amr_data(self):
        """Publish AMR data for all robots"""
        if not self.connected:
            print("❌ [ATI] Not connected to broker")
            return False

        success_count = 0

        for robot in self.robots:
            # Simulate movement
            self.simulate_movement(robot)

            # Create ATI-standard message
            amr_data = {
                "sherpa_name": robot["sherpa_name"],
                "mode": "Fleet",
                "error": "",
                "disabled": False,
                "disabled_reason": "",
                "pose": robot["pose"].copy(),
                "battery_status": round(robot["battery_status"], 1),
                "trip_id": None,
                "trip_leg_id": None,
                "timestamp": int(time.time() * 1000)
            }

            topic = f"ati/amr/{robot['sherpa_name']}/status"

            try:
                result = self.client.publish(topic, json.dumps(amr_data), qos=1)

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    battery = amr_data["battery_status"]
                    print(f"📡 [ATI] Published {robot['sherpa_name']} data - Battery: {battery}%")
                    success_count += 1
                else:
                    print(f"❌ [ATI] Failed to publish {robot['sherpa_name']}: {result.rc}")

            except Exception as e:
                print(f"❌ [ATI] Error publishing {robot['sherpa_name']}: {e}")

        return success_count == len(self.robots)

    def start_publishing_loop(self, duration_seconds=60):
        """Start publishing AMR data every few seconds"""
        if not self.connect_to_broker():
            return False

        print(f"🚀 [ATI] Starting data publishing for {duration_seconds} seconds...")
        print("    Publishing every 5 seconds (real ATI might be faster)")

        start_time = time.time()
        publish_count = 0

        try:
            while time.time() - start_time < duration_seconds:
                success = self.publish_amr_data()
                publish_count += 1

                if success:
                    print(f"✅ [ATI] Batch {publish_count} - All {len(self.robots)} robots published successfully")
                else:
                    print(f"⚠️  [ATI] Batch {publish_count} - Some publishes failed")

                # Wait before next batch
                time.sleep(5)

        except KeyboardInterrupt:
            print("\n🛑 [ATI] Publishing stopped by user")

        finally:
            self.client.loop_stop()
            self.client.disconnect()
            print(f"📊 [ATI] Final stats: {publish_count} batches published")

def main():
    print("🏭 ATI AMR Data Publisher Simulation")
    print("=" * 40)
    print("This simulates what ATI would run to publish AMR data")
    print("to our MQTT broker via ngrok tunnel")
    print()

    simulator = ATIDataSimulator()

    # Test connection first
    print("🧪 Testing connection to broker...")
    if not simulator.connect_to_broker():
        print("❌ Cannot connect to MQTT broker")
        print("   Make sure start_our_infrastructure.py is running")
        return

    # Disconnect test connection
    simulator.client.loop_stop()
    simulator.client.disconnect()
    time.sleep(1)

    print("✅ Connection test successful!")
    print()

    # Start real publishing
    simulator.start_publishing_loop(duration_seconds=60)

if __name__ == "__main__":
    main()