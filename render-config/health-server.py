#!/usr/bin/env python3
"""
HTTP service for Render (port 8080) + MQTT WebSocket proxy
This satisfies Render's HTTP requirement while providing MQTT access
"""
from flask import Flask, jsonify, request
import json
import paho.mqtt.client as mqtt
import threading
import time

app = Flask(__name__)

# Global MQTT client
mqtt_client = None

def setup_mqtt():
    """Setup connection to local mosquitto broker"""
    global mqtt_client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"Connected to MQTT broker: {rc}")

    mqtt_client.on_connect = on_connect

    # Connect to local mosquitto
    try:
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()
        print("MQTT client started successfully")
    except Exception as e:
        print(f"MQTT connection failed: {e}")

@app.route('/')
def root():
    return jsonify({
        'service': 'ATI MQTT Broker',
        'status': 'running',
        'mqtt_websocket': 'wss://ati-mqtt-broker.onrender.com',
        'websocket_port': 9001,
        'http_publish': '/publish',
        'instructions': 'Use WebSocket MQTT client or POST to /publish endpoint'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/publish', methods=['POST'])
def publish():
    """HTTP endpoint to publish MQTT messages"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'ati/default')
        message = data.get('message', {})

        if mqtt_client:
            result = mqtt_client.publish(topic, json.dumps(message))
            return jsonify({
                'status': 'published',
                'topic': topic,
                'message_id': result.mid
            })
        else:
            return jsonify({'error': 'MQTT not connected'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Service status endpoint"""
    return jsonify({
        'http_service': 'running',
        'mqtt_connected': mqtt_client is not None and mqtt_client.is_connected(),
        'endpoints': {
            'health': '/health',
            'publish': '/publish (POST)',
            'status': '/status'
        }
    })

if __name__ == '__main__':
    # Start MQTT client
    setup_mqtt()

    # Run HTTP server (this satisfies Render's HTTP requirement)
    print("Starting HTTP service on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)
