#!/usr/bin/env python3
"""
Quick test to verify Render MQTT broker connection
Replace YOUR_APP_URL with your actual Render URL
"""
import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to Render MQTT broker!")
        client.publish("test/connection", "Hello from test client!")
    else:
        print(f"❌ Connection failed: {rc}")

def on_message(client, userdata, msg):
    print(f"📨 Received: {msg.topic} -> {msg.payload.decode()}")

def main():
    # Your actual Render URL
    RENDER_URL = "ati-mqtt-broker.onrender.com"

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
    client.username_pw_set("ati_user", "ati_password_123")
    client.tls_set()  # Enable TLS for wss://

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"🔗 Connecting to wss://{RENDER_URL}...")
    client.connect(RENDER_URL, 443, 60)
    client.subscribe("test/#")

    client.loop_forever()

if __name__ == "__main__":
    main()