#!/usr/bin/env python3
"""
Comprehensive WebSocket MQTT diagnosis tool
Tests multiple connection methods and provides detailed debugging
"""
import requests
import socket
import ssl
import time
import json
from urllib.parse import urlparse
import paho.mqtt.client as mqtt

def test_basic_connectivity():
    """Test basic HTTP connectivity to the service"""
    print("🔍 Testing Basic Connectivity")
    print("-" * 40)

    try:
        response = requests.get("https://ati-mqtt-broker.onrender.com", timeout=10)
        print(f"✅ HTTP Status: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON Response: {data}")
            except:
                print(f"✅ Text Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ HTTP Connection Error: {e}")

def test_websocket_handshake():
    """Manually test WebSocket handshake"""
    print("\n🔍 Testing WebSocket Handshake Manually")
    print("-" * 45)

    try:
        # Create SSL context
        context = ssl.create_default_context()

        # Connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        # Wrap with SSL
        ssock = context.wrap_socket(sock, server_hostname="ati-mqtt-broker.onrender.com")
        ssock.connect(("ati-mqtt-broker.onrender.com", 443))

        # Send WebSocket upgrade request
        websocket_key = "dGhlIHNhbXBsZSBub25jZQ=="
        request = (
            "GET / HTTP/1.1\r\n"
            "Host: ati-mqtt-broker.onrender.com\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: {}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "Sec-WebSocket-Protocol: mqtt\r\n"
            "\r\n"
        ).format(websocket_key)

        print(f"📤 Sending WebSocket handshake request:")
        print(request)

        ssock.send(request.encode())

        # Read response
        response = ssock.recv(4096).decode()
        print(f"📥 WebSocket handshake response:")
        print(response)

        if "101 Switching Protocols" in response:
            print("✅ WebSocket handshake successful!")
        else:
            print("❌ WebSocket handshake failed - no protocol switch")

        ssock.close()

    except Exception as e:
        print(f"❌ WebSocket handshake error: {e}")

def test_port_connectivity():
    """Test if specific ports are accessible"""
    print("\n🔍 Testing Port Connectivity")
    print("-" * 35)

    ports_to_test = [
        ("HTTPS", "ati-mqtt-broker.onrender.com", 443),
        ("HTTP", "ati-mqtt-broker.onrender.com", 80),
        ("Direct 8080", "ati-mqtt-broker.onrender.com", 8080),
    ]

    for name, host, port in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                print(f"✅ {name} (port {port}): Open")
            else:
                print(f"❌ {name} (port {port}): Closed/Filtered")
        except Exception as e:
            print(f"❌ {name} (port {port}): Error - {e}")

def test_mqtt_websocket_detailed():
    """Test MQTT WebSocket with detailed logging"""
    print("\n🔍 Testing MQTT WebSocket with Detailed Logging")
    print("-" * 52)

    # Enable detailed MQTT logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    mqtt_logger = logging.getLogger("paho.mqtt.client")

    paths_to_test = ["/", "/mqtt", "/ws", "/websocket"]

    for path in paths_to_test:
        print(f"\n📍 Testing path: '{path}'")

        try:
            client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                transport="websockets",
                client_id=f"diagnostic-{int(time.time())}"
            )

            # Enable logging
            client.enable_logger(mqtt_logger)

            # Set WebSocket options
            client.tls_set()
            client.ws_set_options(path=path)

            def on_connect(client, userdata, flags, rc, properties=None):
                print(f"📡 Connection result for path '{path}': {rc}")
                if rc == 0:
                    print(f"✅ Connected successfully with path '{path}'!")
                    client.disconnect()
                else:
                    print(f"❌ Connection failed with path '{path}': {mqtt.error_string(rc)}")

            def on_log(client, userdata, level, buf):
                print(f"🔍 MQTT Log [{path}]: {buf}")

            client.on_connect = on_connect
            client.on_log = on_log

            print(f"🔗 Connecting to wss://ati-mqtt-broker.onrender.com{path}...")
            client.connect_async("ati-mqtt-broker.onrender.com", 443, 10)
            client.loop_start()

            # Wait for connection
            time.sleep(8)
            client.loop_stop()
            client.disconnect()

        except Exception as e:
            print(f"❌ Error testing path '{path}': {e}")

        time.sleep(2)  # Pause between tests

def test_alternative_mqtt_clients():
    """Test alternative MQTT connection methods"""
    print("\n🔍 Testing Alternative Connection Methods")
    print("-" * 45)

    # Test 1: Without TLS (direct HTTP)
    print("📍 Testing without TLS (ws://):")
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
        client.ws_set_options(path="/")

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print("✅ Non-TLS WebSocket connection successful!")
            else:
                print(f"❌ Non-TLS WebSocket failed: {rc}")
            client.disconnect()

        client.on_connect = on_connect
        print("🔗 Connecting to ws://ati-mqtt-broker.onrender.com:80...")
        client.connect("ati-mqtt-broker.onrender.com", 80, 10)
        client.loop(timeout=5)

    except Exception as e:
        print(f"❌ Non-TLS WebSocket error: {e}")

def analyze_render_logs():
    """Analyze what Render's load balancer might be doing"""
    print("\n🔍 Analyzing Render Platform Behavior")
    print("-" * 42)

    print("🔍 Render.com WebSocket Requirements:")
    print("  - Single port binding (✅ We're using 8080)")
    print("  - WebSocket upgrade support (❓ Testing)")
    print("  - Proper WebSocket headers (❓ Testing)")
    print("  - CloudFlare proxy compatibility (❓ Unknown)")

    print("\n🔍 Possible Issues:")
    print("  1. CloudFlare blocking WebSocket MQTT protocol")
    print("  2. Render load balancer not forwarding WebSocket upgrades")
    print("  3. Mosquitto not binding to correct interface")
    print("  4. Missing WebSocket subprotocol headers")

def suggest_alternatives():
    """Suggest alternative approaches"""
    print("\n💡 Alternative Solutions")
    print("-" * 28)

    print("1. 🔄 HTTP-to-MQTT Bridge (Current working solution)")
    print("   - ATI sends HTTP POST → Our service converts to MQTT")
    print("   - Pros: Working, simple, reliable")
    print("   - Cons: Not native MQTT protocol")

    print("\n2. 🌐 Use Public MQTT Broker")
    print("   - Switch to broker.emqx.io or test.mosquitto.org")
    print("   - Pros: Known WebSocket support")
    print("   - Cons: Not private, may have rate limits")

    print("\n3. 🐳 Deploy to Different Platform")
    print("   - Try Fly.io, Railway, or DigitalOcean")
    print("   - Pros: May have better WebSocket support")
    print("   - Cons: Migration effort")

    print("\n4. 🔌 TCP MQTT (Non-WebSocket)")
    print("   - Use standard MQTT on port 1883")
    print("   - Pros: Native MQTT protocol")
    print("   - Cons: May require firewall/network changes")

    print("\n5. 🚇 MQTT over SSH Tunnel")
    print("   - Create SSH tunnel to expose internal MQTT port")
    print("   - Pros: Full MQTT access")
    print("   - Cons: Complex setup, authentication needed")

def main():
    print("🚀 Comprehensive WebSocket MQTT Diagnostic Tool")
    print("=" * 55)

    # Run all diagnostic tests
    test_basic_connectivity()
    test_port_connectivity()
    test_websocket_handshake()
    test_mqtt_websocket_detailed()
    test_alternative_mqtt_clients()
    analyze_render_logs()
    suggest_alternatives()

    print("\n" + "=" * 55)
    print("🎯 Diagnostic Complete!")
    print("Check the logs above for specific error patterns.")
    print("If all WebSocket tests fail, consider the alternatives listed.")

if __name__ == "__main__":
    main()