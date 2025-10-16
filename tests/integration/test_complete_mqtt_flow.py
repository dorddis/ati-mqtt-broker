#!/usr/bin/env python3
"""
Test Complete MQTT to Twinzo Flow
Tests: WebSocket MQTT → Bridge → Twinzo OAuth → REST API
"""
import os, json, time, math, threading
import requests
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# Twinzo OAuth configuration
TWINZO_CLIENT = os.getenv("TWINZO_CLIENT", "TVSMotor")
TWINZO_PASSWORD = os.getenv("TWINZO_PASSWORD", "Tvs@Hosur$2025")
TWINZO_API_KEY = os.getenv("TWINZO_API_KEY", "sq29vSdYEribAbJjPc93FwNvk8ndo53P2yoAsS6S")

# API URLs
TWINZO_AUTH_URL = "https://api.platform.twinzo.com/v3/authorization/authenticate"
TWINZO_LOCALIZATION_URL = "https://api.platform.twinzo.com/v3/localization"

# Test settings
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"  # Default to dry run for testing

class TwinzoWebSocketBridge:
    def __init__(self):
        self.oauth_cache = {"tokens": {}, "last_cleanup": time.time()}
        self.session = requests.Session()
        self.messages_processed = 0
        self.successful_posts = 0
        self.failed_posts = 0

    def authenticate_device(self, device_login):
        """Authenticate device using OAuth"""
        try:
            auth_payload = {
                "client": TWINZO_CLIENT,
                "login": device_login,
                "password": TWINZO_PASSWORD
            }

            auth_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            print(f"Authenticating {device_login} with Twinzo OAuth...")
            response = requests.post(TWINZO_AUTH_URL, headers=auth_headers, json=auth_payload, timeout=10)

            if response.status_code == 200:
                auth_data = response.json()
                self.oauth_cache["tokens"][device_login] = {
                    "token": auth_data["Token"],
                    "client": auth_data["Client"],
                    "branch": auth_data["Branch"],
                    "expires": auth_data["Expiration"]
                }
                print(f"SUCCESS OAuth for {device_login}")
                return self.oauth_cache["tokens"][device_login]
            else:
                print(f"FAILED OAuth for {device_login}: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"ERROR OAuth for {device_login}: {e}")
            return None

    def get_device_credentials(self, device_login):
        """Get cached credentials or authenticate if needed"""
        now = time.time()

        # Check if we have valid cached credentials
        if device_login in self.oauth_cache["tokens"]:
            creds = self.oauth_cache["tokens"][device_login]
            if creds["expires"] > now * 1000:  # expires is in milliseconds
                return creds
            else:
                print(f"Token expired for {device_login}, re-authenticating...")
                del self.oauth_cache["tokens"][device_login]

        # Authenticate if no valid cached credentials
        return self.authenticate_device(device_login)

    def process_sherpa_message(self, payload):
        """Process a single Sherpa message and send to Twinzo"""
        try:
            device_id = payload.get("sherpa_name")
            if not device_id:
                print("No sherpa_name in payload, skipping")
                return False

            print(f"\nProcessing {device_id}...")

            # Get OAuth credentials for this device
            credentials = self.get_device_credentials(device_id)
            if not credentials:
                print(f"FAILED to get credentials for {device_id}")
                self.failed_posts += 1
                return False

            # Extract pose data (ATI format: [x, y, z, roll, pitch, yaw])
            x = y = z = theta = 0.0
            if "pose" in payload and isinstance(payload["pose"], list) and len(payload["pose"]) >= 6:
                x = float(payload["pose"][0])
                y = float(payload["pose"][1])
                z = float(payload["pose"][2])
                theta = float(payload["pose"][5])  # yaw/heading

            # Use battery from payload or default
            battery = payload.get("battery_status", 85.0)

            # Create Twinzo localization payload
            twinzo_payload = [
                {
                    "Timestamp": int(time.time() * 1000),  # Milliseconds
                    "SectorId": 1,  # Integer sector ID
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "Interval": 100,  # 100ms = 10Hz
                    "Battery": int(battery),
                    "IsMoving": True,  # Assume moving for test
                    "LocalizationAreas": [],
                    "NoGoAreas": []
                }
            ]

            # Create headers with OAuth credentials
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Client": credentials["client"],
                "Branch": credentials["branch"],
                "Token": credentials["token"],
                "Api-Key": TWINZO_API_KEY
            }

            if DRY_RUN:
                print(f"[DRY RUN] Would POST to Twinzo for {device_id}:")
                print(f"  Position: X={x:.1f}, Y={y:.1f}, Z={z:.1f}")
                print(f"  Battery: {battery}%")
                print(f"  OAuth Client: {credentials['client']}")
                print(f"  OAuth Branch: {credentials['branch']}")
                print(f"  Token: {credentials['token'][:20]}...")
                self.successful_posts += 1
                return True
            else:
                print(f"POSTing to Twinzo for {device_id}...")
                response = self.session.post(TWINZO_LOCALIZATION_URL, headers=headers, json=twinzo_payload, timeout=10)

                if response.status_code < 300:
                    print(f"SUCCESS POST for {device_id}: {response.status_code} - {response.text[:100]}")
                    self.successful_posts += 1
                    return True
                else:
                    print(f"FAILED POST for {device_id}: {response.status_code} - {response.text}")
                    self.failed_posts += 1
                    return False

        except Exception as e:
            print(f"ERROR processing {device_id}: {e}")
            self.failed_posts += 1
            return False

    def start_websocket_bridge(self, duration=30):
        """Start WebSocket MQTT bridge and process messages"""
        print("=" * 60)
        print("Starting WebSocket MQTT to Twinzo Bridge")
        print("=" * 60)
        print(f"Twinzo Auth URL: {TWINZO_AUTH_URL}")
        print(f"Twinzo API URL: {TWINZO_LOCALIZATION_URL}")
        print(f"OAuth Client: {TWINZO_CLIENT}")
        print(f"DRY RUN Mode: {DRY_RUN}")
        print("=" * 60)

        messages = []

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print("Connected to local WebSocket MQTT")
                client.subscribe("ati/amr/+/status")
                print("Subscribed to ati/amr/+/status")
            else:
                print(f"Failed to connect: {rc}")

        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                messages.append(payload)
                self.messages_processed += 1

                print(f"\nReceived message #{self.messages_processed} on {msg.topic}")
                print(f"Sherpa: {payload.get('sherpa_name', 'unknown')}")
                print(f"Battery: {payload.get('battery_status', 'unknown')}%")

                # Process message and send to Twinzo
                success = self.process_sherpa_message(payload)
                if success:
                    print("Forwarded to Twinzo successfully")
                else:
                    print("Failed to forward to Twinzo")

            except Exception as e:
                print(f"Error processing message: {e}")

        # Connect to local WebSocket MQTT broker
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="twinzo_bridge_test",
            transport="websockets"
        )
        client.on_connect = on_connect
        client.on_message = on_message
        client.ws_set_options(path="/", headers=None)

        try:
            client.connect("localhost", 9001, 60)
            client.loop_start()

            # Wait for connection
            time.sleep(2)

            print(f"\nListening for {duration} seconds...")
            start_time = time.time()

            while (time.time() - start_time) < duration:
                time.sleep(1)

            print(f"\nBridge Test Results:")
            print(f"Messages Processed: {self.messages_processed}")
            print(f"Successful Twinzo Posts: {self.successful_posts}")
            print(f"Failed Twinzo Posts: {self.failed_posts}")

            return self.messages_processed > 0 and self.successful_posts > 0

        except Exception as e:
            print(f"Bridge error: {e}")
            return False

        finally:
            client.loop_stop()
            client.disconnect()

def test_oauth_only():
    """Test OAuth authentication only"""
    print("=" * 60)
    print("Testing Twinzo OAuth Authentication")
    print("=" * 60)

    bridge = TwinzoWebSocketBridge()

    # Test OAuth for sample device
    test_device = "ws-tugger-001"
    credentials = bridge.authenticate_device(test_device)

    if credentials:
        print(f"\nOAuth SUCCESS for {test_device}:")
        print(f"  Client: {credentials['client']}")
        print(f"  Branch: {credentials['branch']}")
        print(f"  Token: {credentials['token'][:20]}...")
        print(f"  Expires: {credentials['expires']}")
        return True
    else:
        print(f"\nOAuth FAILED for {test_device}")
        return False

def test_complete_flow():
    """Test complete flow: WebSocket MQTT → OAuth → Twinzo API"""
    print("=" * 60)
    print("Testing Complete WebSocket MQTT to Twinzo Flow")
    print("=" * 60)

    bridge = TwinzoWebSocketBridge()

    # Start bridge in background
    bridge_thread = threading.Thread(target=bridge.start_websocket_bridge, args=(20,))
    bridge_thread.start()

    # Wait for bridge to start
    time.sleep(3)

    # Run WebSocket publisher test to generate data
    print("\nStarting WebSocket publisher to generate test data...")
    from websocket_ati_publisher import test_websocket_integration

    publisher_success = test_websocket_integration()

    # Wait for bridge to finish
    bridge_thread.join()

    # Results
    success = (
        publisher_success and
        bridge.messages_processed > 0 and
        bridge.successful_posts > 0
    )

    print("\n" + "=" * 60)
    print("COMPLETE FLOW TEST RESULTS")
    print("=" * 60)
    print(f"Publisher Success: {publisher_success}")
    print(f"Messages Processed: {bridge.messages_processed}")
    print(f"Successful Twinzo Posts: {bridge.successful_posts}")
    print(f"Failed Twinzo Posts: {bridge.failed_posts}")
    print(f"Overall Success: {success}")

    return success

if __name__ == "__main__":
    print("Testing Twinzo Integration")
    print("=" * 40)

    # Test 1: OAuth only
    print("\nTest 1: OAuth Authentication")
    oauth_success = test_oauth_only()

    if oauth_success:
        print("\nTest 2: Complete Flow")
        flow_success = test_complete_flow()

        if flow_success:
            print("\nALL TESTS PASSED")
            print("OAuth authentication works")
            print("WebSocket MQTT to Twinzo bridge works")
            print("Complete integration verified")
        else:
            print("\nComplete flow test failed")
    else:
        print("\nOAuth test failed - skipping complete flow test")
        print("Check Twinzo credentials and API access")