#!/bin/bash
# Health check for Render

# Check if mosquitto is running
if pgrep mosquitto > /dev/null; then
    # Try to publish a test message
    mosquitto_pub -h localhost -p 1883 -u admin -P admin_password_456 -t health/check -m "ok" -q 1
    if [ $? -eq 0 ]; then
        echo "MQTT broker is healthy"
        exit 0
    fi
fi

echo "MQTT broker is not healthy"
exit 1
