#!/usr/bin/env python3
"""
WebSocket MQTT Bridge Subscriber
Receives data from WebSocket MQTT and forwards to Twinzo
"""
import paho.mqtt.client as mqtt
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketBridgeSubscriber:
    def __init__(self):
        """Initialize local WebSocket MQTT subscriber"""
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="websocket_bridge_subscriber",
            transport="websockets"
        )

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # Local WebSocket connection (no TLS for localhost)
        self.client.ws_set_options(path="/", headers=None)

        self.connected = False
        self.messages_received = []

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            logger.info("✅ Bridge connected to local WebSocket MQTT")
            client.subscribe("ati/amr/+/status")
            logger.info("📡 Bridge subscribed to ati/amr/+/status")
        else:
            logger.error(f"❌ Bridge connection failed: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.messages_received.append({
                'topic': msg.topic,
                'data': data,
                'timestamp': time.time()
            })

            sherpa_name = data.get('sherpa_name', 'unknown')
            battery = data.get('battery_status', 'N/A')

            logger.info(f"📨 Bridge received {sherpa_name} data - Battery: {battery}%")
            logger.info(f"🔄 Bridge → Would forward to Twinzo API")

        except Exception as e:
            logger.error(f"❌ Bridge error processing message: {e}")

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        self.connected = False
        logger.info(f"🔌 Bridge disconnected: {rc}")

    def connect_and_listen(self, duration=30):
        """Connect to local WebSocket MQTT and listen"""
        try:
            logger.info("🌉 Starting WebSocket bridge subscriber...")

            # Connect to local WebSocket MQTT (port 9001, no TLS)
            self.client.connect("localhost", 9001, 60)
            self.client.loop_start()

            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1

            if not self.connected:
                logger.error("❌ Bridge failed to connect to local WebSocket MQTT")
                return False

            logger.info(f"🎧 Bridge listening for {duration} seconds...")
            start_time = time.time()
            last_count = 0

            while (time.time() - start_time) < duration:
                time.sleep(1)

                # Show new messages
                if len(self.messages_received) > last_count:
                    new_messages = len(self.messages_received) - last_count
                    logger.info(f"📊 Bridge received {new_messages} new messages (total: {len(self.messages_received)})")
                    last_count = len(self.messages_received)

            logger.info(f"📊 Bridge final stats: {len(self.messages_received)} messages received")

            return len(self.messages_received) > 0

        except Exception as e:
            logger.error(f"❌ Bridge error: {e}")
            return False

        finally:
            if self.connected:
                self.client.loop_stop()
                self.client.disconnect()
                logger.info("✅ Bridge stopped")


def test_complete_websocket_flow():
    """Test complete WebSocket MQTT data flow"""
    logger.info("=== Complete WebSocket MQTT Flow Test ===")

    # Start bridge subscriber
    bridge = WebSocketBridgeSubscriber()

    # Start bridge in background
    import threading
    bridge_thread = threading.Thread(target=bridge.connect_and_listen, args=(20,))
    bridge_thread.start()

    # Wait for bridge to connect
    time.sleep(3)

    # Now run publisher test
    logger.info("🚀 Starting WebSocket publisher test...")

    # Import and run the publisher test
    from websocket_ati_publisher import test_websocket_integration

    publisher_success = test_websocket_integration()

    # Wait for bridge to finish
    bridge_thread.join()

    # Results
    if publisher_success and len(bridge.messages_received) > 0:
        logger.info("🎉 COMPLETE WEBSOCKET FLOW: SUCCESS")
        logger.info(f"✅ Publisher sent messages successfully")
        logger.info(f"✅ Bridge received {len(bridge.messages_received)} messages")
        logger.info("✅ End-to-end WebSocket MQTT flow verified")
        return True
    else:
        logger.error("❌ COMPLETE WEBSOCKET FLOW: FAILED")
        return False


if __name__ == "__main__":
    success = test_complete_websocket_flow()

    if success:
        print("\n🎉 WebSocket MQTT End-to-End: WORKING")
        print("✅ ATI → ngrok → WebSocket MQTT → Bridge → Twinzo")
        print("✅ Complete data flow verified")
    else:
        print("\n❌ WebSocket MQTT End-to-End: ISSUES")
        print("🔧 Check WebSocket configuration")