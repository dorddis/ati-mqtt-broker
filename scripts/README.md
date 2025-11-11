# Scripts

Utility scripts for setup, monitoring, deployment, verification, and coordinate transformation.

## Directory Structure

### setup/
Setup and configuration scripts:
- `setup_secure_mqtt.py` - Configure secure MQTT broker
- `setup_railway_deployment.py` - Setup Railway.app deployment
- `setup_render_deployment.py` - Setup Render.com deployment
- `setup_public_broker.py` - Setup public MQTT broker
- `setup_ngrok_mqtt.py` - Setup ngrok MQTT tunnel
- `create_mqtt_credentials.py` - Generate MQTT credentials
- `create_password_hash.py` - Create password hashes

### monitoring/
Monitoring and status tools:
- `monitor_twinzo.py` - Monitor Twinzo integration
- `monitor_railway_mqtt.py` - Monitor Railway deployment
- `monitor_render_mqtt.py` - Monitor Render deployment
- `system_status.py` - Overall system status

### deployment/
Deployment helper scripts:
- `deploy_to_railway.py` - Deploy to Railway.app
- `start_local_mqtt_ngrok.py` - Start local MQTT with ngrok
- `start_ngrok_mqtt.py` - Start ngrok tunnel
- `start_our_infrastructure.py` - Start complete infrastructure

### transformation/ (NEW)
Coordinate transformation and analysis scripts:
- `calculate_affine_transform.py` - Calculate transformation from reference points
- `recalculate_transform_precise.py` - Recalculate with precise coordinates
- `calculate_offset_correction.py` - Calculate offset adjustments
- `test_coordinate_transform.py` - Test transformation accuracy
- `validate_transformation_live.py` - Validate with live data
- `analyze_log_data.py` - Analyze historical movement data
- `analyze_movement_coordinates.py` - Analyze coordinate patterns
- `overlay_paths_on_map.py` - Overlay tugger paths on Twinzo map
- `visualize_transform_errors.py` - Visualize transformation errors

### verification/
Verification and validation tools:
- `verify_system.py` - Verify system setup
- `verify_credentials.py` - Verify MQTT credentials

### utils/
General utility scripts:
- `expose_mqtt.py` - Expose MQTT broker via ngrok
- `manage_twinzo_devices.py` - Manage Twinzo devices via API
- `setup_hitech_tuggers.py` - Setup HiTech plant tuggers
- `test_manual_post.py` - Manually test Twinzo API posting

### Root Scripts
- `start_bridges.py` - Start production bridges (multi-plant)
- `start_multi_plant_streaming.bat` - Windows batch starter

## Usage

Always use `python -X utf8` on Windows:

### Production Operations
```bash
# Start bridges for both plants
python -X utf8 scripts/start_bridges.py

# Start only Old Plant bridge
python -X utf8 scripts/start_bridges.py old

# Monitor Twinzo integration
python -X utf8 scripts/monitoring/monitor_twinzo.py
```

### Coordinate Transformation
```bash
# Recalculate transformation with precise coordinates
python -X utf8 scripts/transformation/recalculate_transform_precise.py

# Analyze log data for movement patterns
python -X utf8 scripts/transformation/analyze_log_data.py

# Overlay paths on Twinzo map for visual validation
python -X utf8 scripts/transformation/overlay_paths_on_map.py

# Calculate offset corrections
python -X utf8 scripts/transformation/calculate_offset_correction.py
```

### Device Management
```bash
# List all devices
python -X utf8 scripts/utils/manage_twinzo_devices.py list

# Create new device
python -X utf8 scripts/utils/manage_twinzo_devices.py create tugger-10 hitech --title "Tugger 10"

# Test manual API post
python -X utf8 scripts/utils/test_manual_post.py
```

### System Verification
```bash
# Verify system setup
python -X utf8 scripts/verification/verify_system.py

# Verify MQTT credentials
python -X utf8 scripts/verification/verify_credentials.py
```
