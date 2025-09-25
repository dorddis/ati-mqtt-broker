#!/bin/bash
# Start script for Render - runs both mosquitto and health server

# Start mosquitto in background
echo "Starting MQTT broker..."
mosquitto -c /mosquitto/config/mosquitto.conf &
MQTT_PID=$!

# Wait a moment for MQTT to start
sleep 2

# Start health server in background
echo "Starting health server..."
python3 /usr/local/bin/health-server.py &
HEALTH_PID=$!

# Keep both running
echo "Services started. MQTT PID: $MQTT_PID, Health PID: $HEALTH_PID"

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $MQTT_PID $HEALTH_PID 2>/dev/null
    exit 0
}

trap cleanup SIGTERM SIGINT

# Wait for either process to exit
wait
