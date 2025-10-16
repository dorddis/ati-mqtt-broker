#!/usr/bin/env python3
"""
Test client for Twinzo team to verify MQTT integration
Run this to test connection and see live data transformation
"""
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# Configuration - UPDATE THE URL WHEN PROVIDED
MQTT_BROKER = "localhost"  # Replace with ngrok URL (without wss://)
MQTT_PORT = 9001
MQTT_USERNAME = "mock_tvs"
MQTT_PASSWORD = "Twinzo2025!@#"
MQTT_TOPIC = "ati_fm/sherpa/status"

# Device tracking for movement calculation
device_tracking = {}

def transform_to_twinzo_format(mqtt_data):
    """Transform MQTT data to Twinzo platform format"""
    
    device_id = mqtt_data['sherpa_name']
    current_pos = [mqtt_data['pose'][0], mqtt_data['pose'][1]]
    current_time = time.time()
    
    # Calculate movement and speed
    is_moving = False
    speed = 0.0
    
    if device_id in device_tracking:
        last_data = device_tracking[device_id]
        
        # Calculate distance moved
        dx = current_pos[0] - last_data['pos'][0]
        dy = current_pos[1] - last_data['pos'][1]
        distance = (dx**2 + dy**2)**0.5
        
        # Calculate time difference
        time_diff = current_time - last_data['time']
        
        # Movement detection (threshold: 0.5 meters)
        is_moving = distance > 0.5
        
        # Speed calculation (meters per second)
        if time_diff > 0:
            speed = distance / time_diff
    
    # Update tracking
    device_tracking[device_id] = {
        'pos': current_pos,
        'time': current_time
    }
    
    # Transform to Twinzo format
    twinzo_data = {
        "device_id": device_id,
        "timestamp": int(current_time * 1000),  # milliseconds
        "x": mqtt_data['pose'][0],
        "y": mqtt_data['pose'][1],
        "z": mqtt_data['pose'][2],
        "heading": mqtt_data['pose'][5],  # radians
        "battery": mqtt_data['battery_status'],
        "status": mqtt_data['mode'],
        "is_active": not mqtt_data['disabled'],
        "error_message": mqtt_data['error'],
        "trip_id": mqtt_data['trip_id'],
        "leg_id": mqtt_data['trip_leg_id'],
        "is_moving": is_moving,
        "speed": round(speed, 2)
    }
    
    return twinzo_data

def on_connect(client, userdata, flags, rc):
    """Callback for MQTT connection"""
    if rc == 0:
        print("✅ Connected to TVS MQTT broker successfully!")
        print(f"📡 Subscribing to topic: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC, qos=1)
        print("🎯 Waiting for messages... (Ctrl+C to stop)")
        print("-" * 80)
    else:
        print(f"❌ Connection failed with code: {rc}")
        print("   Check your broker URL and credentials")

def on_message(client, userdata, msg):
    """Callback for received MQTT messages"""
    try:
        # Parse MQTT message
        mqtt_data = json.loads(msg.payload.decode())
        
        # Transform to Twinzo format
        twinzo_data = transform_to_twinzo_format(mqtt_data)
        
        # Display the transformation
        device_id = twinzo_data['device_id']
        timestamp = datetime.fromtimestamp(twinzo_data['timestamp']/1000).strftime('%H:%M:%S.%f')[:-3]
        
        print(f"🚛 {device_id} @ {timestamp}")
        print(f"   Position: ({twinzo_data['x']:.1f}, {twinzo_data['y']:.1f}, {twinzo_data['z']:.1f})")
        print(f"   Heading: {twinzo_data['heading']:.2f} rad")
        print(f"   Battery: {twinzo_data['battery']}%")
        print(f"   Status: {twinzo_data['status']} | Active: {twinzo_data['is_active']}")
        print(f"   Moving: {twinzo_data['is_moving']} | Speed: {twinzo_data['speed']} m/s")
        print(f"   Trip: {twinzo_data['trip_id']} | Leg: {twinzo_data['leg_id']}")
        
        if twinzo_data['error_message']:
            print(f"   ⚠️  Error: {twinzo_data['error_message']}")
        
        print("-" * 80)
        
        # Here you would send twinzo_data to your platform
        # send_to_twinzo_platform(twinzo_data)
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        print(f"   Raw message: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    """Callback for MQTT disconnection"""
    print(f"🔌 Disconnected from MQTT broker (code: {rc})")

def main():
    """Main function to run the test client"""
    
    print("🧪 TWINZO MQTT INTEGRATION TEST CLIENT")
    print("=" * 50)
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Username: {MQTT_USERNAME}")
    print(f"Topic: {MQTT_TOPIC}")
    print("=" * 50)
    
    # Create MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        # Connect to broker
        print("🔗 Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Start the loop
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping test client...")
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure the ngrok tunnel is running")
        print("   2. Update MQTT_BROKER with the correct ngrok URL")
        print("   3. Verify credentials are correct")
        print("   4. Check if the TVS system is running")

if __name__ == "__main__":
    main()