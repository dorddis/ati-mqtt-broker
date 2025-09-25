#!/usr/bin/env python3
"""
Test MQTT client to verify credentials work
"""
import json
import time
from paho.mqtt import client as mqtt

def test_mqtt_connection():
    """Test MQTT connection with credentials"""
    
    # MQTT settings
    broker_host = "localhost"
    broker_port = 9001  # WebSocket port
    username = "mock_tvs"
    password = "Twinzo2025!@#"
    topic = "ati_fm/sherpa/status"
    
    messages_received = 0
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker successfully!")
            print(f"📡 Subscribing to topic: {topic}")
            client.subscribe(topic)
        else:
            print(f"❌ Failed to connect: {rc}")
    
    def on_message(client, userdata, msg):
        nonlocal messages_received
        messages_received += 1
        
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            device_id = payload.get("sherpa_name", "unknown")
            battery = payload.get("battery_status", "N/A")
            pose = payload.get("pose", [])
            
            if len(pose) >= 2:
                x, y = pose[0], pose[1]
                print(f"📦 Message {messages_received}: {device_id} at ({x:.1f}, {y:.1f}) - Battery: {battery}%")
            else:
                print(f"📦 Message {messages_received}: {device_id} - Battery: {battery}%")
            
            if messages_received >= 10:  # Stop after 10 messages
                print("✅ Test complete - credentials working!")
                client.disconnect()
                
        except Exception as e:
            print(f"❌ Error parsing message: {e}")
    
    def on_disconnect(client, userdata, rc):
        print("🔌 Disconnected from MQTT broker")
    
    # Create MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        print("🔗 Connecting to MQTT broker...")
        print(f"   Host: {broker_host}")
        print(f"   Port: {broker_port}")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
        client.connect(broker_host, broker_port, 60)
        client.loop_forever()
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure the broker is running and credentials are set up")

if __name__ == "__main__":
    print("🧪 TESTING MQTT CREDENTIALS")
    print("=" * 40)
    test_mqtt_connection()