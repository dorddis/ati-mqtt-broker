# Deployments

Deployment configurations for different hosting platforms.

## Available Platforms

### docker/
Local Docker deployment using docker-compose:
- Development and testing environment
- Full control over configuration
- See root docker-compose.yml

### railway/
Railway.app deployment:
- Free tier MQTT hosting
- Automated deployments
- railway.json - Railway configuration
- mosquitto.conf - Railway-specific MQTT config
- See docs/deployment/PERSISTENT_MQTT_HOSTING.md

### render/
Render.com deployment:
- Free tier with WebSocket support
- render.yaml - Render service configuration
- Dockerfile.render - Custom Dockerfile for Render
- mosquitto.conf - Render-specific MQTT config
- acl.conf - Access control list
- health-server.py - Health check endpoint
- See docs/deployment/RENDER_DEPLOYMENT.md

### ngrok/
Ngrok tunnel for local MQTT:
- Expose local MQTT broker to internet
- Useful for testing with external clients
- mosquitto.conf - Ngrok-compatible config
- See docs/guides/NGROK_MQTT_SETUP_GUIDE.md

## Deployment Guide

### Local (Docker)
```bash
docker-compose up -d
```

### Railway
```bash
python -X utf8 scripts/deployment/deploy_to_railway.py
```

### Render
Deploy via Render dashboard or:
```bash
python -X utf8 scripts/setup/setup_render_deployment.py
```

### Ngrok
```bash
python -X utf8 scripts/deployment/start_ngrok_mqtt.py
```

## Choosing a Platform

- **Docker**: Best for local development and testing
- **Railway**: Easy setup, good for persistent free MQTT broker
- **Render**: Better WebSocket support, more configuration options
- **Ngrok**: Quick temporary exposure of local broker

See docs/deployment/ for detailed comparison and guides.
