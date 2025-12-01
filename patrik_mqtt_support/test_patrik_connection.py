#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Minimal ATI MQTT Connection Test (Python version)

This script tests the exact connection settings needed for the ATI broker.
Share this with Patrik to help troubleshoot subscription issues.

Usage:
    python -X utf8 test_patrik_connection.py
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime

# ATI Audit Feed credentials
MQTT_HOST = 'tvs-dev.ifactory.ai'
MQTT_PORT = 8883
MQTT_USERNAME = 'tvs-audit-user'
MQTT_PASSWORD = 'TVSAudit@2025'
MQTT_CLIENT_ID = MQTT_USERNAME  # CRITICAL: Must match username!

# Topics to subscribe to
TOPICS = [
    ('ati_fm/#', 1),           # All ATI Fleet Manager topics, QoS 1
    ('fleet/trips/info', 1)    # Trip info, QoS 1
]

def on_connect(client, userdata, flags, reason_code, properties):
    """Callback when connected to broker"""
    print('\n' + '='*70)
    if reason_code == 0:
        print('✅ CONNECTED successfully!')
        print(f'Connection flags: {flags}')
        if properties:
            print(f'Properties: {properties}')
        print('='*70)

        # Subscribe to topics
        print('\nAttempting to subscribe to topics...')
        result = client.subscribe(TOPICS)
        print(f'Subscription result: {result}')
    else:
        print(f'❌ CONNECTION FAILED with code: {reason_code}')
        print('='*70)

def on_subscribe(client, userdata, mid, reason_codes, properties):
    """Callback when subscription is confirmed"""
    print('\n✅ SUBSCRIBED successfully!')
    print('Granted subscriptions:')
    for i, (topic, qos) in enumerate(TOPICS):
        granted_qos = reason_codes[i]
        if isinstance(granted_qos, int):
            print(f'  - Topic: {topic}, QoS: {granted_qos}')
        else:
            print(f'  - Topic: {topic}, Reason: {granted_qos}')
    print('\nListening for messages (press Ctrl+C to stop)...\n')

def on_message(client, userdata, message):
    """Callback when message is received"""
    print('\n' + '='*70)
    print('📨 MESSAGE RECEIVED')
    print(f'Topic: {message.topic}')
    print(f'Time: {datetime.now().isoformat()}')
    print(f'QoS: {message.qos}')

    try:
        payload = json.loads(message.payload.decode('utf-8'))
        print('Payload:')
        print(json.dumps(payload, indent=2))
    except:
        print(f'Raw payload: {message.payload.decode("utf-8")}')

    print('='*70)

def on_disconnect(client, userdata, flags, reason_code, properties):
    """Callback when disconnected from broker"""
    print(f'\n⚠️  DISCONNECTED with code: {reason_code}')
    if reason_code != 0:
        print('Unexpected disconnection. Will auto-reconnect...')

def on_log(client, userdata, level, buf):
    """Callback for logging"""
    print(f'[LOG] {buf}')

def main():
    print('='*70)
    print('ATI MQTT Connection Test (Python)')
    print('='*70)
    print(f'Host: {MQTT_HOST}:{MQTT_PORT}')
    print(f'Username: {MQTT_USERNAME}')
    print(f'Client ID: {MQTT_CLIENT_ID}')
    print('Protocol: MQTT v5')
    print('='*70)

    # Create MQTT client with v5 protocol
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=MQTT_CLIENT_ID,
        protocol=mqtt.MQTTv5
    )

    # Set callbacks
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    # Uncomment for debug logging:
    # client.on_log = on_log

    # Set username and password
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Enable TLS (import ssl first)
    import ssl
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)  # Skip certificate verification

    try:
        # Connect to broker
        print('\nConnecting to broker...')
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

        # Start network loop
        client.loop_forever()

    except KeyboardInterrupt:
        print('\n\nShutting down...')
        client.disconnect()
        print('✅ Disconnected cleanly')

    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
