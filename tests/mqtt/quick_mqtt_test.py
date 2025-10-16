#!/usr/bin/env python3
"""Quick MQTT test to verify broker is working"""
import paho.mqtt.client as mqtt
import time
import json

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected: {rc}")
    if rc == 0:
        client.subscribe("test/topic")

def on_message(client, userdata, msg):
    print(f"Received: {msg.topic} -> {msg.payload.decode()}")

# Test publisher
def test_publish():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="test_pub")
    client.connect("localhost", 1883, 60)
    client.loop_start()
    time.sleep(1)

    result = client.publish("test/topic", "Hello MQTT")
    print(f"Publish result: {result.rc}")

    time.sleep(2)
    client.disconnect()

# Test subscriber
def test_subscribe():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="test_sub")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)
    client.loop_start()

    time.sleep(5)
    client.disconnect()

if __name__ == "__main__":
    print("Testing MQTT publish...")
    test_publish()

    print("\nTesting MQTT subscribe...")
    test_subscribe()