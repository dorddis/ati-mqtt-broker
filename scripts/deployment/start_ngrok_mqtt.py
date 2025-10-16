#!/usr/bin/env python3
"""
Super Simple MQTT + ngrok Server Starter
Just run this and everything starts automatically
"""
import subprocess
import time
import requests
import json
import os

def start_mqtt_broker():
    """Start WebSocket MQTT broker"""
    print("Starting WebSocket MQTT broker on port 9001...")

    mosquitto_exe = r"C:\Program Files\Mosquitto\mosquitto.exe"
    config_file = "websocket_only.conf"

    try:
        process = subprocess.Popen([mosquitto_exe, "-c", config_file, "-v"])
        time.sleep(2)  # Wait for broker to start
        print("WebSocket MQTT broker started")
        return process
    except Exception as e:
        print(f"Failed to start MQTT broker: {e}")
        return None

def start_ngrok_tunnel():
    """Start ngrok HTTP tunnel"""
    print("Starting ngrok tunnel...")

    try:
        process = subprocess.Popen(["ngrok", "http", "9001"])
        time.sleep(5)  # Wait for ngrok to start
        print("ngrok tunnel started")
        return process
    except Exception as e:
        print(f"Failed to start ngrok: {e}")
        return None

def get_ngrok_url():
    """Get the current ngrok URL"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()["tunnels"]

        if tunnels:
            url = tunnels[0]["public_url"]
            print(f"ngrok URL: {url}")
            return url
        else:
            print("No active tunnels found")
            return None
    except Exception as e:
        print(f"Could not get ngrok URL: {e}")
        return None

def main():
    print("=" * 50)
    print("Starting MQTT + ngrok Server")
    print("=" * 50)

    # Start MQTT broker
    mqtt_process = start_mqtt_broker()
    if not mqtt_process:
        print("Cannot start without MQTT broker")
        return

    # Start ngrok tunnel
    ngrok_process = start_ngrok_tunnel()
    if not ngrok_process:
        print("Cannot start without ngrok tunnel")
        mqtt_process.terminate()
        return

    # Get and display ngrok URL
    ngrok_url = get_ngrok_url()

    print("\n" + "=" * 50)
    print("SERVER READY!")
    print("=" * 50)
    print(f"MQTT Broker: Running on localhost:9001")
    print(f"ngrok Tunnel: {ngrok_url}")
    print(f"ATI Connection: {ngrok_url.replace('https://', '')}:443")
    print("=" * 50)
    print("\nGive these details to ATI:")
    print(f"   Host: {ngrok_url.replace('https://', '')}")
    print(f"   Port: 443")
    print(f"   Protocol: WebSocket MQTT over HTTPS")
    print(f"   Authentication: None")
    print("\nPress Ctrl+C to stop server")

    try:
        # Keep running until interrupted
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping server...")
        ngrok_process.terminate()
        mqtt_process.terminate()
        print("Server stopped")

if __name__ == "__main__":
    main()