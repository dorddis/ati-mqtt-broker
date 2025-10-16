#!/usr/bin/env python3
"""
ATI WebSocket MQTT Publisher for Twinzo Integration
Uses WebSocket MQTT over ngrok HTTP tunnel
"""
import paho.mqtt.client as mqtt
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ATIWebSocketPublisher:
    def __init__(self, websocket_host, websocket_port=443):
        """
        Initialize WebSocket MQTT publisher

        Args:
            websocket_host: ngrok WebSocket host (e.g., "abc123.ngrok-free.app")
            websocket_port: WebSocket port (443 for HTTPS ngrok tunnels)
        """
        self.host = websocket_host
        self.port = websocket_port

        # Create WebSocket MQTT client
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"ati-websocket-{int(time.time())}",
            transport="websockets"
        )

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish

        # WebSocket specific settings
        self.client.ws_set_options(path="/", headers=None)
        self.client.tls_set()  # Enable TLS for HTTPS ngrok tunnel

        self.connected = False
        self.published_count = 0

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            logger.info(f"SUCCESS WebSocket MQTT connection to {self.host}")
        else:
            self.connected = False
            logger.error(f"FAILED WebSocket MQTT connection: {rc} - {mqtt.error_string(rc)}")

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected WebSocket disconnection: {rc}")
        else:
            logger.info("Disconnected from WebSocket MQTT broker")

    def _on_publish(self, client, userdata, mid, reasonCode=None, properties=None):
        self.published_count += 1
        logger.debug(f"WebSocket message {mid} published (total: {self.published_count})")

    def connect(self, timeout=15):
        """Connect to WebSocket MQTT broker"""
        try:
            logger.info(f"Connecting to WebSocket MQTT at wss://{self.host}:{self.port}")

            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()

            # Wait for connection
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            if self.connected:
                logger.info("WebSocket MQTT connection established")
                return True
            else:
                logger.error("WebSocket MQTT connection timeout")
                return False

        except Exception as e:
            logger.error(f"WebSocket MQTT connection error: {e}")
            return False

    def publish_sherpa(self, sherpa_data):
        """Publish Sherpa (AMR) status data via WebSocket MQTT"""
        if not self.connected:
            logger.error("Not connected to WebSocket MQTT broker")
            return False

        try:
            # Validate required fields
            required_fields = ["sherpa_name", "pose", "battery_status"]
            for field in required_fields:
                if field not in sherpa_data:
                    logger.error(f"Missing required field: {field}")
                    return False

            # Add timestamp if not present
            if "timestamp" not in sherpa_data:
                sherpa_data["timestamp"] = int(time.time() * 1000)

            # Create topic and message
            topic = f"ati/amr/{sherpa_data['sherpa_name']}/status"
            message = json.dumps(sherpa_data, separators=(',', ':'))

            # Publish via WebSocket
            result = self.client.publish(topic, message, qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published {sherpa_data['sherpa_name']} via WebSocket")
                return True
            else:
                logger.error(f"WebSocket publish failed: {mqtt.error_string(result.rc)}")
                return False

        except Exception as e:
            logger.error(f"Error publishing via WebSocket: {e}")
            return False

    def disconnect(self):
        """Disconnect from WebSocket MQTT broker"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("WebSocket MQTT disconnected")

    def get_status(self):
        """Get publisher status"""
        return {
            "connected": self.connected,
            "host": self.host,
            "port": self.port,
            "transport": "websockets",
            "published_count": self.published_count
        }


def test_websocket_integration():
    """Test WebSocket MQTT integration"""
    # ngrok WebSocket connection details
    WEBSOCKET_HOST = "dbf62e689562.ngrok-free.app"  # Real ngrok URL
    WEBSOCKET_PORT = 443  # HTTPS port for ngrok

    logger.info("=== WebSocket MQTT Integration Test ===")

    publisher = ATIWebSocketPublisher(WEBSOCKET_HOST, WEBSOCKET_PORT)

    if not publisher.connect():
        logger.error("Failed to connect to WebSocket MQTT broker")
        return False

    try:
        # Test with sample Sherpa data
        test_robots = [
            {
                "sherpa_name": "ws-tugger-001",
                "mode": "Fleet",
                "pose": [195630.16, 188397.78, 0.0, 0.0, 0.0, 1.57],
                "battery_status": 85.2,
                "trip_id": 1001
            },
            {
                "sherpa_name": "ws-lifter-002",
                "mode": "Fleet",
                "pose": [195700.45, 188420.12, 0.0, 0.0, 0.0, 0.78],
                "battery_status": 73.8,
                "trip_id": 1002
            },
            {
                "sherpa_name": "ws-carrier-003",
                "mode": "Fleet",
                "pose": [195580.90, 188350.34, 0.0, 0.0, 0.0, 2.34],
                "battery_status": 91.5,
                "trip_id": 1003
            }
        ]

        logger.info("Publishing test data via WebSocket MQTT...")
        success_count = 0

        for robot in test_robots:
            success = publisher.publish_sherpa(robot)
            if success:
                success_count += 1
                logger.info(f"SUCCESS: {robot['sherpa_name']} published via WebSocket")
            else:
                logger.error(f"FAILED: {robot['sherpa_name']} WebSocket publish failed")

            time.sleep(1)  # Space out publishes

        # Test rapid publishing
        logger.info("Testing rapid WebSocket publishing...")
        for i in range(5):
            rapid_data = {
                "sherpa_name": f"ws-speed-test-{i}",
                "mode": "Fleet",
                "pose": [195630.0 + i * 5, 188400.0, 0.0, 0.0, 0.0, 0.0],
                "battery_status": 80.0 - i,
            }

            success = publisher.publish_sherpa(rapid_data)
            result = "SUCCESS" if success else "FAILED"
            logger.info(f"Rapid test {i+1}: {result}")
            time.sleep(0.5)

        status = publisher.get_status()
        logger.info(f"Final status: {status['published_count']} messages published")

        if success_count == len(test_robots):
            logger.info("✅ WebSocket MQTT integration test: SUCCESS")
            return True
        else:
            logger.error("❌ WebSocket MQTT integration test: FAILED")
            return False

    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

    finally:
        publisher.disconnect()


if __name__ == "__main__":
    success = test_websocket_integration()

    if success:
        print("\n🎉 WebSocket MQTT Integration: WORKING")
        print("✅ ATI can use WebSocket MQTT over ngrok HTTP tunnel")
        print("✅ Connection established successfully")
        print("✅ Message publishing works")
        print("✅ Ready for production deployment")
    else:
        print("\n❌ WebSocket MQTT Integration: ISSUES")
        print("🔧 Check WebSocket broker and ngrok tunnel")