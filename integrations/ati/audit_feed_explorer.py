"""
ATI Audit Feed Explorer

This script connects to ATI's audit MQTT feed and logs ALL messages published
by ATI. Use this to discover available topics and data structures beyond the
standard sherpa status messages.

Credentials: tvs-audit-user (audit/monitoring access)
Topics: ati_fm/# (all ATI Fleet Manager messages) + fleet/trips/info

Usage:
    python -X utf8 integrations/ati/audit_feed_explorer.py
"""

import os
import json
import logging
import ssl
from datetime import datetime
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
MQTT_HOST = os.getenv('AUDIT_MQTT_HOST', 'tvs-dev.ifactory.ai')
MQTT_PORT = int(os.getenv('AUDIT_MQTT_PORT', '8883'))
USERNAME = os.getenv('AUDIT_USERNAME', 'tvs-audit-user')
PASSWORD = os.getenv('AUDIT_PASSWORD', 'TVSAudit@2025')
CLIENT_ID = f"{USERNAME}-explorer"

# Subscribe to all ATI topics
SUBSCRIPTION_TOPICS = [
    ('ati_fm/#', 1),  # All ATI Fleet Manager messages, QoS 1
    ('fleet/trips/info', 1)  # Fleet trip information, QoS 1
]

# Track discovered topics
discovered_topics = set()
message_counts = {}


def on_connect(client, userdata, flags, reason_code, properties):
    """Callback when client connects to broker"""
    if reason_code == 0:
        logger.info("Connected to ATI audit feed successfully")
        logger.info(f"Host: {MQTT_HOST}:{MQTT_PORT}")
        logger.info(f"Username: {USERNAME}")
        logger.info(f"Client ID: {CLIENT_ID}")
        logger.info("=" * 80)

        # Subscribe to topics
        for topic, qos in SUBSCRIPTION_TOPICS:
            result = client.subscribe(topic, qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Subscribed to: {topic} (QoS {qos})")
            else:
                logger.error(f"Failed to subscribe to {topic}: {result}")

        logger.info("=" * 80)
        logger.info("Waiting for audit messages...")
        logger.info("Press Ctrl+C to stop and see summary")
        logger.info("=" * 80 + "\n")
    else:
        logger.error(f"Connection failed with reason code: {reason_code}")


def on_message(client, userdata, message):
    """Callback when message is received"""
    topic = message.topic

    # Track new topics
    if topic not in discovered_topics:
        discovered_topics.add(topic)
        logger.info(f"\n*** NEW TOPIC DISCOVERED: {topic} ***\n")

    # Update message count
    message_counts[topic] = message_counts.get(topic, 0) + 1

    try:
        # Try to parse as JSON
        payload = json.loads(message.payload.decode('utf-8'))

        logger.info("=" * 80)
        logger.info(f"MESSAGE #{message_counts[topic]} - {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        logger.info("=" * 80)
        logger.info(f"Topic: {topic}")
        logger.info(f"QoS: {message.qos}")
        logger.info(f"Retain: {message.retain}")
        logger.info("\nPayload (JSON):")
        logger.info(json.dumps(payload, indent=2))
        logger.info("=" * 80 + "\n")

    except json.JSONDecodeError:
        # Not JSON, log as string
        logger.info("=" * 80)
        logger.info(f"MESSAGE #{message_counts[topic]} - {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        logger.info("=" * 80)
        logger.info(f"Topic: {topic}")
        logger.info(f"QoS: {message.qos}")
        logger.info(f"Retain: {message.retain}")
        logger.info("\nPayload (raw):")
        logger.info(message.payload.decode('utf-8', errors='replace'))
        logger.info("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Error processing message from {topic}: {e}")
        logger.error(f"Raw payload: {message.payload}")


def on_disconnect(client, userdata, reason_code, properties):
    """Callback when client disconnects"""
    if reason_code != 0:
        logger.warning(f"Unexpected disconnection. Reason code: {reason_code}")
        logger.info("Attempting to reconnect...")
    else:
        logger.info("Disconnected from audit feed")


def on_subscribe(client, userdata, mid, reason_codes, properties):
    """Callback when subscription is confirmed"""
    logger.debug(f"Subscription confirmed with message ID: {mid}")


def print_summary():
    """Print summary of discovered topics and messages"""
    logger.info("\n" + "=" * 80)
    logger.info("AUDIT FEED EXPLORATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total topics discovered: {len(discovered_topics)}")
    logger.info(f"Total messages received: {sum(message_counts.values())}")
    logger.info("\nTopics and message counts:")
    for topic in sorted(discovered_topics):
        count = message_counts.get(topic, 0)
        logger.info(f"  {topic}: {count} messages")
    logger.info("=" * 80)


def main():
    """Main function to run the audit feed explorer"""
    logger.info("Starting ATI Audit Feed Explorer...")
    logger.info("This will show ALL messages published by ATI")
    logger.info("")

    # Create MQTT client (using MQTT v5)
    client = mqtt.Client(
        client_id=CLIENT_ID,
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        clean_session=None  # Use MQTT v5 clean_start property instead
    )

    # Set MQTT v5 connection properties
    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes

    properties = Properties(PacketTypes.CONNECT)
    properties.SessionExpiryInterval = 86400  # 24 hours, like in JS code

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    # Note: Not setting on_disconnect or on_subscribe to avoid callback API version issues

    # Set username and password
    client.username_pw_set(USERNAME, PASSWORD)

    # Configure TLS (disable cert verification for internal servers)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

    # Connect to broker
    try:
        logger.info(f"Connecting to {MQTT_HOST}:{MQTT_PORT}...")
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60, properties=properties)

        # Start network loop
        client.loop_forever()

    except KeyboardInterrupt:
        logger.info("\n\nShutting down...")
        print_summary()
        client.disconnect()
        logger.info("Disconnected. Goodbye!")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
