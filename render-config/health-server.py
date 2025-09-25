#!/usr/bin/env python3
# Simple health endpoint for Render

from flask import Flask
import subprocess
import threading
import time

app = Flask(__name__)

@app.route('/health')
def health():
    try:
        # Check if mosquitto is running
        result = subprocess.run(['pgrep', 'mosquitto'], capture_output=True)
        if result.returncode == 0:
            return {'status': 'healthy', 'service': 'mqtt'}, 200
        else:
            return {'status': 'unhealthy', 'error': 'mosquitto not running'}, 503
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503

@app.route('/')
def root():
    return {'message': 'ATI MQTT Broker', 'status': 'running', 'websocket': 'ws://localhost:9001'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
