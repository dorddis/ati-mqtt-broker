# Scripts

Utility scripts for setup, monitoring, deployment, and verification.

## Directory Structure

### setup/
Setup and configuration scripts:
- setup_secure_mqtt.py - Configure secure MQTT broker
- setup_railway_deployment.py - Setup Railway.app deployment
- setup_render_deployment.py - Setup Render.com deployment
- setup_public_broker.py - Setup public MQTT broker
- setup_ngrok_mqtt.py - Setup ngrok MQTT tunnel
- create_mqtt_credentials.py - Generate MQTT credentials
- create_password_hash.py - Create password hashes

### monitoring/
Monitoring and status tools:
- monitor_twinzo.py - Monitor Twinzo integration
- monitor_railway_mqtt.py - Monitor Railway deployment
- monitor_render_mqtt.py - Monitor Render deployment
- system_status.py - Overall system status

### deployment/
Deployment helper scripts:
- deploy_to_railway.py - Deploy to Railway.app
- start_local_mqtt_ngrok.py - Start local MQTT with ngrok
- start_ngrok_mqtt.py - Start ngrok tunnel
- start_our_infrastructure.py - Start complete infrastructure

### verification/
Verification and validation tools:
- verify_system.py - Verify system setup
- verify_credentials.py - Verify MQTT credentials

### utils/
General utility scripts:
- expose_mqtt.py - Expose MQTT broker via ngrok

## Usage

Always use `python -X utf8` on Windows:

```bash
# Monitor Twinzo integration
python -X utf8 scripts/monitoring/monitor_twinzo.py status

# Verify system
python -X utf8 scripts/verification/verify_system.py

# Setup ngrok tunnel
python -X utf8 scripts/setup/setup_ngrok_mqtt.py
```
